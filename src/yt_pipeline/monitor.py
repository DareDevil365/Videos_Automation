"""Owned-channel observations and local, evidence-limited growth suggestions."""
from datetime import datetime, timezone, timedelta
import json
import shutil
import time
from urllib.parse import urlencode

from shorts_editor.store import write_json
from .assets import asset_record
from .core import Held, now
from .publishing import YouTube, reconcile


WINDOWS={"24h":24,"72h":72,"7d":168}


def incident(workspace, channel, message, source_id=None):
    config=workspace.config()
    if channel not in config["channels"]:raise ValueError("Unknown channel")
    config["channels"][channel]["paused"]=True
    workspace.save_config(config)
    workspace.alert("incident:"+channel+":"+(source_id or message[:80]),None,message)
    workspace.event(None,"incident",{"channel":channel,"source_id":source_id,"message":message})
    return {"channel":channel,"paused":True,"note":"No video was deleted and no dispute/counter-notice was submitted."}


def alerts(workspace, acknowledge=None):
    with workspace.connect() as db:
        if acknowledge:db.execute("UPDATE alerts SET acknowledged=1 WHERE key=?",(acknowledge,))
        return [dict(row) for row in db.execute("SELECT * FROM alerts ORDER BY at DESC LIMIT 100")]


def supervise(workspace, remote=False):
    free=shutil.disk_usage(workspace.root).free
    findings=[]
    if free<2*1024**3:
        findings.append("Less than 2 GiB disk space remains.");workspace.alert("disk_low",None,findings[-1])
    for job in workspace.jobs(1000):
        if job["status"]=="running" and (job["lease_until"] or 0)<time.time():
            workspace.alert(job["id"]+":stale_worker",job["id"],"Worker lease expired; the next worker can resume the saved stages.")
        if remote and job.get("video_id"):
            try:reconcile(workspace,job["id"])
            except Held as exc:
                findings.append(str(exc));workspace.alert(job["id"]+":"+exc.code,job["id"],str(exc))
    with workspace.connect() as db:ids=[row[0] for row in db.execute("SELECT id FROM assets")]
    for asset_id in ids:
        try:asset_record(workspace,asset_id)
        except Held as exc:
            findings.append(str(exc));workspace.alert(asset_id+":"+exc.code,None,str(exc))
    result={"checked_at":now(),"disk_free_bytes":free,"findings":findings,"alerts":alerts(workspace),
            "remote_checked":remote,"limits":["YouTube Data API is not a complete copyright-claim/strike feed. Review Studio notices and record incidents.",
                 "Alerts stay in this local dashboard/database. External notifications are not connected."]}
    write_json(workspace.root/"reports"/"supervisor.json",result)
    return result


def observe(workspace, job_id, window="24h", client=None):
    if window not in WINDOWS:raise ValueError("Use 24h, 72h or 7d")
    job=workspace.get(job_id)
    if not job.get("video_id"):raise Held("not_published","This job has no uploaded video ID.")
    client=client or YouTube(workspace,job["channel"])
    row=client.video(job["video_id"])
    expected=workspace.config()["channels"][job["channel"]]["youtube_channel_id"]
    if not expected or row.get("snippet",{}).get("channelId")!=expected:raise Held("wrong_channel","Analytics identity does not match the owned profile.")
    if row.get("status",{}).get("privacyStatus")!="public":raise Held("not_public","Comparable performance windows start after public publication.")
    try:published=datetime.fromisoformat(row["snippet"]["publishedAt"].replace("Z","+00:00"))
    except (KeyError,ValueError):raise Held("publication_time_unknown","The API did not return a publication timestamp.")
    age=(datetime.now(timezone.utc)-published).total_seconds()/3600
    if age<WINDOWS[window]:raise Held("observation_early",f"The {window} window is not due yet.",retry_after=max(60,int((WINDOWS[window]-age)*3600)))
    end=published+timedelta(hours=WINDOWS[window])
    params={"ids":"channel==MINE","startDate":published.date().isoformat(),"endDate":end.date().isoformat(),
            "metrics":"views,estimatedMinutesWatched,averageViewDuration,subscribersGained","filters":"video=="+job["video_id"]}
    code,_,body=client.call("GET","https://youtubeanalytics.googleapis.com/v2/reports?"+urlencode(params))
    if code!=200:raise Held("analytics_unavailable",f"Owned Analytics returned HTTP {code}; missing metrics were not replaced with zero.",retry_after=3600)
    response=json.loads(body);rows=response.get("rows",[])
    metrics=dict(zip([c["name"] for c in response.get("columnHeaders",[])],rows[0])) if rows else None
    data={"job_id":job_id,"video_id":job["video_id"],"channel":job["channel"],"window":window,"checked_at":now(),
          "published_at":published.isoformat(),"age_hours_at_check":age,"metrics":metrics,"available":bool(rows),
          "data_may_be_delayed":age<WINDOWS[window]+72,
          "date_range":{"start":params["startDate"],"end":params["endDate"]},
          "limitations":["Analytics reports use calendar dates, not exact rolling-hour boundaries; the window label is a collection checkpoint.",
                         "Recent Analytics data may be delayed or incomplete; missing is not zero. No competitor retention/revenue is inferred."]}
    with workspace.connect() as db:
        db.execute("INSERT INTO observations(job_id,window,at,data) VALUES(?,?,?,?) ON CONFLICT(job_id,window) DO UPDATE SET at=excluded.at,data=excluded.data",(job_id,window,now(),json.dumps(data)))
    return data


def growth_report(workspace, channel):
    if channel not in workspace.config()['channels']:raise ValueError('Unknown channel profile')
    with workspace.connect() as db:
        records=[json.loads(r[0]) for r in db.execute("SELECT data FROM observations")]
    records=[r for r in records if r["channel"]==channel]
    comparable={w:[r for r in records if r["window"]==w and r.get("metrics")] for w in WINDOWS}
    experiments=[];rankings={}
    for window,rows in comparable.items():
        rankings[window]=sorted(rows,key=lambda x:x["metrics"].get("views",0),reverse=True)
        if len(rows)>=3:
            best=rankings[window][0]
            experiments.append({"hypothesis":"Test another distinct topic using the leading video's hook structure, while changing only one presentation variable.",
                                "evidence_job":best["job_id"],"window":window,"sample_size":len(rows),"status":"hypothesis, not a causal finding"})
    result={"channel":channel,"created_at":now(),"observations":len(records),"rankings":rankings,"experiments":experiments,
            "next_action":"Collect at least three owned, comparable observations before proposing a winner." if not experiments else "Run one new original episode per hypothesis and compare the same collection checkpoint.",
            "limits":["No income forecast, sponsor offer or competitor private metric is fabricated.","Private channel analytics are processed locally, not sent to free-tier Gemini."]}
    write_json(workspace.root/"reports"/(channel+"-growth.json"),result)
    return result
