from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
import uuid
import threading
from urllib.parse import urlencode, urlparse

from shorts_editor.store import write_json
from .assets import asset_record
from .core import Held, digest, file_hash, now
from .research import source_freshness


SCOPES=["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/yt-analytics.readonly"]


def authorize(workspace, channel, client_file):
    """Explicit owner-invoked OAuth flow. Never called by a render/research worker."""
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow=InstalledAppFlow.from_client_secrets_file(str(client_file),SCOPES)
    credentials=flow.run_local_server(port=0,open_browser=True,access_type="offline",prompt="consent")
    path=workspace.root/"credentials"/(channel+".json")
    path.write_text(credentials.to_json(),encoding="utf-8")
    client=YouTube(workspace,channel)
    identity=client.identity()
    config=workspace.config();config["channels"][channel]["youtube_channel_id"]=identity["id"];workspace.save_config(config)
    return {"channel_profile":channel,"channel_id":identity["id"],"title":identity.get("title"),"credentials_saved":True,
            "publication_mode":config["channels"][channel]["publication_mode"]}


class YouTube:
    def __init__(self,workspace,channel,transport=None):self.workspace,self.channel,self.transport=workspace,channel,transport

    def call(self,method,url,body=None,headers=None):
        if self.transport:return self.transport(method,url,body,headers or {})
        path=self.workspace.root/"credentials"/(self.channel+".json")
        if not path.exists():raise Held("youtube_auth_missing","Connect this channel through the explicit authorize command first.")
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        import requests
        try:
            credentials=Credentials.from_authorized_user_file(str(path),SCOPES)
            if not credentials.valid:
                if not credentials.refresh_token:raise Held("youtube_reconnect","YouTube authorization needs reconnecting.")
                credentials.refresh(Request());path.write_text(credentials.to_json(),encoding="utf-8")
            response=requests.request(method,url,data=body,headers={"Authorization":"Bearer "+credentials.token,**(headers or {})},timeout=45,allow_redirects=False)
        except Held:raise
        except Exception:raise Held("youtube_network","YouTube request failed or authorization expired. Existing upload sessions were preserved.",retry_after=600)
        if response.status_code in (401,403):raise Held("youtube_access","YouTube access/quota was rejected. Check this channel/project; no alternate account is used.",retry_after=3600)
        return response.status_code,dict(response.headers),response.content

    def get(self,path,params):
        code,_,body=self.call("GET","https://www.googleapis.com/youtube/v3/"+path+"?"+urlencode(params))
        if code!=200:raise Held("youtube_response",f"YouTube returned HTTP {code}.",retry_after=600 if code>=500 else None)
        return json.loads(body)

    def identity(self):
        rows=self.get("channels",{"part":"snippet","mine":"true"}).get("items",[])
        if len(rows)!=1:raise Held("channel_ambiguous","Authorization did not identify exactly one channel.")
        return {"id":rows[0]["id"],"title":rows[0].get("snippet",{}).get("title","")}

    def video(self,video_id):
        rows=self.get("videos",{"part":"snippet,status,processingDetails","id":video_id}).get("items",[])
        if not rows:raise Held("video_unknown","Uploaded video could not be reconciled; no replacement upload was started.")
        return rows[0]


def metadata_for(workspace,job_id):
    job=workspace.get(job_id)
    for stage,checkpoint in job['artifacts'].items():
        saved=Path(checkpoint['path'])
        if not saved.is_file() or file_hash(saved)!=checkpoint['sha256']:
            raise Held('artifact_changed',f'Saved {stage} evidence changed after production. Rebuild/review it before publication.')
        for name,sha in checkpoint.get('files',{}).items():
            if not Path(name).is_file() or file_hash(name)!=sha:
                raise Held('artifact_changed',f'A file used by {stage} changed after production.')
    item=job["artifacts"].get("package")
    if not item:raise Held("not_ready","Complete local production before publishing.")
    path=Path(item["path"])
    if file_hash(path)!=item["sha256"]:raise Held("package_changed","Packaging changed after checks; regenerate/review it.")
    metadata=json.loads(path.read_text(encoding="utf-8"))
    return job,metadata


def fingerprint(job,metadata,mode=None):
    return digest([file_hash(metadata["video"]),metadata["title"],metadata["description"],job["channel"],
                   metadata["contains_synthetic_media"],metadata.get('made_for_kids'),metadata.get('category_id'),
                   job["request"].get("publish_at"),mode or job['request'].get('publish_visibility')])


def approve(workspace,job_id):
    job,metadata=metadata_for(workspace,job_id)
    if job['status']!='ready':raise Held('not_ready','Only a completed ready job can receive a new publication approval.')
    if not metadata["qa"]["publication_ready"]:raise Held("test_media","Test-only or held source media cannot be approved for upload.")
    if file_hash(metadata['video'])!=metadata['qa']['video_sha256']:raise Held('video_changed','The video changed after technical review. Rebuild and check it before approving.')
    value=fingerprint(job,metadata,workspace.config()['channels'][job['channel']]['publication_mode'])
    workspace.update(job_id,approval_hash=value)
    workspace.event(job_id,"publication_approved",{"fingerprint":value})
    return {"job_id":job_id,"approved_version":value}


def save_upload(workspace,job_id,state):
    with workspace.connect() as db:
        db.execute("INSERT INTO uploads(job_id,data) VALUES(?,?) ON CONFLICT(job_id) DO UPDATE SET data=excluded.data",(job_id,json.dumps(state)))


def load_upload(workspace,job_id):
    with workspace.connect() as db:row=db.execute("SELECT data FROM uploads WHERE job_id=?",(job_id,)).fetchone()
    return json.loads(row[0]) if row else None


def safe_session(url):
    parsed=urlparse(url)
    if parsed.scheme!="https" or parsed.hostname not in ("www.googleapis.com","youtube.googleapis.com") or not parsed.path.startswith("/upload/"):
        raise Held("upload_session_invalid","YouTube returned an unsupported upload session URL.")
    return url


def publish(workspace,job_id,apply=False,client=None):
    if not apply:return _publish(workspace,job_id,False,client)
    owner=uuid.uuid4().hex;name="upload:"+workspace.get(job_id)["channel"]
    workspace.worker_lock(owner,name=name)
    stopped=threading.Event()
    def heartbeat():
        while not stopped.wait(30):workspace.worker_lock(owner,name=name)
    thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
    try:return _publish(workspace,job_id,True,client)
    finally:
        stopped.set();thread.join(timeout=2);workspace.worker_lock(owner,release=True,name=name)


def _publish(workspace,job_id,apply=False,client=None):
    job,metadata=metadata_for(workspace,job_id)
    profile=workspace.config()["channels"][job["channel"]]
    status={"privacyStatus":"private","selfDeclaredMadeForKids":metadata["made_for_kids"],"containsSyntheticMedia":metadata["contains_synthetic_media"]}
    mode=profile['publication_mode']
    intended=job['request'].get('publish_visibility')
    if intended and intended!=mode:raise Held('publication_policy_changed','This job requests '+intended+' visibility; the channel policy differs. Restore its intended policy or create a new job.')
    if mode=='public':status['privacyStatus']='public'
    if profile["publication_mode"]=="scheduled":
        stamp=job["request"].get("publish_at")
        if not stamp:raise Held("schedule_missing","A scheduled job needs publish_at in ISO format with a timezone.")
        try:target=datetime.fromisoformat(stamp.replace("Z","+00:00"))
        except ValueError:raise Held("schedule_invalid","Invalid publication timestamp.")
        if target.tzinfo is None or target<=datetime.now(timezone.utc):raise Held("schedule_invalid","Publication time must be in the future with an explicit timezone.")
        status["publishAt"]=target.astimezone(timezone.utc).isoformat()
    payload={"snippet":{"title":metadata["title"],"description":metadata["description"],"categoryId":metadata["category_id"]},"status":status}
    if not apply:
        return {"dry_run":True,"job_id":job_id,"channel_profile":job["channel"],"channel_id":profile["youtube_channel_id"],
                "payload":payload,"publication_ready":metadata["qa"]["publication_ready"],"approved":job["approval_hash"]==fingerprint(job,metadata,mode),
                "note":"No network request, credential lookup or upload occurred."}
    if profile.get("paused"):raise Held("channel_paused","Channel publishing is paused.")
    if job['status'] not in ('ready','processing','uploaded_private','scheduled','published'):raise Held('not_ready','This job is not eligible for publication or reconciliation.')
    if mode not in ("private","public","scheduled"):raise Held("publishing_disabled","Publishing is disabled. Configure an authorized private/public/scheduled policy explicitly.")
    if not metadata["qa"]["publication_ready"]:raise Held("test_media","A test-only result cannot be uploaded.")
    if file_hash(metadata['video'])!=metadata['qa']['video_sha256']:raise Held('video_changed','The video changed after its quality checks.')
    if job["approval_hash"]!=fingerprint(job,metadata,mode):raise Held("approval_missing","This exact video, metadata and visibility version needs publication approval.")
    directed=json.loads(Path(job["artifacts"]["direct"]["path"]).read_text(encoding="utf-8"))
    for asset in directed["provenance"]:asset_record(workspace,asset["id"])
    brief=json.loads(Path(job["artifacts"]["research"]["path"]).read_text(encoding="utf-8"))
    if source_freshness(brief,int(job["request"].get("max_source_age_days",30))):raise Held("stale_sources","Refresh the source evidence before publishing.")
    expected=profile["youtube_channel_id"]
    if not expected:raise Held("channel_not_configured","No verified YouTube channel ID is configured for this profile.")
    client=client or YouTube(workspace,job["channel"])
    if client.identity()["id"]!=expected:raise Held("wrong_channel","OAuth channel identity does not match this production profile.")
    state=load_upload(workspace,job_id)
    video=Path(metadata["video"]);size=video.stat().st_size
    version=fingerprint(job,metadata,mode)
    if state and state["version"]!=version:raise Held("upload_version_changed","An upload session exists for another content version. Reconcile it instead of replacing it.")
    if state and state.get("video_id"):
        return reconcile(workspace,job_id,client)
    if state and not state.get("session"):
        raise Held("upload_session_unknown","Upload initialization was interrupted before the session URL was saved. Reconcile before starting anything new.")
    if state:
        session=safe_session(state["session"])
        code,headers,body=client.call("PUT",session,b"",{"Content-Length":"0","Content-Range":f"bytes */{size}"})
        completed=_upload_response(workspace,job_id,state,code,headers,body,size)
        if completed:return reconcile(workspace,job_id,client)
    else:
        workspace.reserve_call("youtube_upload_"+job["channel"],int(profile.get("daily_cap",4)))
        state={"version":version,"created_at":now(),"offset":0,"size":size,"phase":"starting","requested_status":status}
        save_upload(workspace,job_id,state) # Persist intent before the first side effect.
        code,headers,body=client.call("POST","https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
            json.dumps(payload).encode(),{"Content-Type":"application/json; charset=UTF-8","X-Upload-Content-Type":"video/mp4","X-Upload-Content-Length":str(size)})
        location=next((v for k,v in headers.items() if k.lower()=="location"),None)
        if code not in (200,201) or not location:raise Held("upload_initialization","Upload initialization is unresolved; no video bytes were sent.")
        state.update(session=safe_session(location),phase="uploading");save_upload(workspace,job_id,state)
    with video.open("rb") as stream:
        while state["offset"]<size:
            stream.seek(state["offset"]);chunk=stream.read(8*1024*1024)
            start=state["offset"];end=start+len(chunk)-1
            code,headers,body=client.call("PUT",state["session"],chunk,{"Content-Type":"video/mp4","Content-Length":str(len(chunk)),"Content-Range":f"bytes {start}-{end}/{size}"})
            previous=state["offset"]
            if _upload_response(workspace,job_id,state,code,headers,body,size):break
            if state["offset"]<=previous:raise Held("upload_no_progress","Upload did not advance. Its session was preserved for a later reconciliation.",retry_after=600)
    if not state.get("video_id"):raise Held("upload_ambiguous","All bytes were sent but completion is unresolved. Resume the saved session; do not start another upload.",retry_after=600)
    return reconcile(workspace,job_id,client)


def _upload_response(workspace,job_id,state,code,headers,body,size):
    if code in (200,201):
        try:video_id=json.loads(body)["id"]
        except (ValueError,KeyError,TypeError):raise Held("upload_ambiguous","Upload completion did not include a video ID. Its saved session needs reconciliation.")
        state.update(video_id=video_id,phase="uploaded",offset=size);save_upload(workspace,job_id,state)
        workspace.update(job_id,video_id=video_id,status="processing",message="Video uploaded; checking processing and visibility.")
        return True
    if code==308:
        raw=next((v for k,v in headers.items() if k.lower()=="range"),"")
        match=re.fullmatch(r"bytes=0-(\d+)",raw)
        if raw and not match:raise Held("upload_offset","Server returned a malformed upload range.")
        offset=int(match[1])+1 if match else 0
        if not 0<=offset<=size:raise Held("upload_offset","Server returned an invalid upload offset.")
        state["offset"]=offset;save_upload(workspace,job_id,state);return False
    if code==404:raise Held("upload_session_expired","Upload session expired. Confirm the remote state before authorizing a fresh upload.")
    raise Held("upload_interrupted",f"Upload returned HTTP {code}; saved session retained.",retry_after=600)


def reconcile(workspace,job_id,client=None):
    job=workspace.get(job_id);state=load_upload(workspace,job_id)
    if not state or not state.get("video_id"):raise Held("video_unknown","No completed video ID is available yet; resume its saved upload session first.")
    client=client or YouTube(workspace,job["channel"])
    row=client.video(state["video_id"])
    expected=workspace.config()["channels"][job["channel"]]["youtube_channel_id"]
    if row.get("snippet",{}).get("channelId")!=expected:raise Held("wrong_channel","Uploaded video identity does not match the expected channel.")
    status=row.get("status",{});processing=row.get("processingDetails",{}).get("processingStatus")
    if status.get("uploadStatus") in ("failed","rejected","deleted") or processing in ("failed","terminated"):
        workspace.alert(job_id+":youtube_rejected",job_id,"YouTube processing/rejection requires review; publishing has been paused.")
        config=workspace.config();config["channels"][job["channel"]]["paused"]=True;workspace.save_config(config)
        raise Held("youtube_rejected","YouTube rejected or could not process the upload. Review the official status/Studio notice.")
    requested=state["requested_status"]
    if status.get("privacyStatus") not in ("private","public"):
        raise Held("visibility_mismatch","Uploaded visibility differs from the requested publication policy.")
    if "publishAt" not in requested and status.get("privacyStatus")!=requested['privacyStatus']:raise Held("visibility_mismatch","YouTube visibility differs from the requested upload policy; no replacement upload was started.")
    if 'publishAt' in requested and status.get('privacyStatus')=='public' and datetime.fromisoformat(requested['publishAt'])>datetime.now(timezone.utc):
        raise Held('visibility_mismatch','The video became public before its requested schedule. Review Studio immediately.')
    processed=processing=='succeeded' or status.get('uploadStatus')=='processed'
    target='processing' if not processed else 'published' if status.get('privacyStatus')=='public' else 'scheduled' if 'publishAt' in requested else 'uploaded_private'
    workspace.update(job_id,status=target,message=f"YouTube state: {target}")
    state.update(phase=target,checked_at=now(),processing_status=processing);save_upload(workspace,job_id,state)
    workspace.event(job_id,"upload_checked",{"video_id":state["video_id"],"state":target})
    return {"job_id":job_id,"video_id":state["video_id"],"status":target,"privacy":status.get("privacyStatus"),"processing":processing}
