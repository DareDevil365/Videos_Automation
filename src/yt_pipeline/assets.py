from datetime import datetime, timezone
import json
import os
from pathlib import Path
from urllib.parse import urlencode, urlparse
import uuid

from shorts_editor.store import Store
from .core import Held, file_hash, now
from .net import fetch


def register_asset(workspace, path, source_type, evidence, commercial=True, editing=True, expires_at=None, attribution="", test_only=False):
    if source_type not in ("owner_recording","original_graphic","licensed_stock","licensed_creator","test"):
        raise ValueError("Choose an explicit asset source type")
    if not evidence:raise Held("asset_evidence_missing","Asset provenance needs an owner/license evidence reference.")
    test_only=bool(test_only or source_type=="test")
    meta=Store(workspace.root/"media").register(path,demo=test_only)
    record={**meta,"sha256":file_hash(path),"source_type":source_type,"evidence":evidence,"commercial":commercial,
            "editing":editing,"expires_at":expires_at,"attribution":attribution,"test_only":test_only,"checked_at":now()}
    with workspace.connect() as db:db.execute("INSERT INTO assets(id,data) VALUES(?,?)",(meta["id"],json.dumps(record)))
    return record


def asset_record(workspace, asset_id):
    with workspace.connect() as db:row=db.execute("SELECT data FROM assets WHERE id=?",(asset_id,)).fetchone()
    if not row:raise Held("asset_missing","The configured asset is not registered with provenance.")
    record=json.loads(row[0]);meta=Store(workspace.root/"media").asset(asset_id)
    source_id=record.get('evidence',{}).get('source_profile')
    if source_id:
        if not isinstance(source_id,str) or not source_id.replace('_','').replace('-','').isalnum():raise Held('source_changed','Asset source profile ID is invalid.')
        profile=workspace.root/'sources'/(source_id+'.json')
        if not profile.is_file() or file_hash(profile)!=record['evidence'].get('profile_sha256'):raise Held('source_changed','The source permission/profile changed after asset registration.')
    if not record["commercial"] or not record["editing"]:raise Held("asset_not_eligible","The asset is not marked eligible for commercial edited use.")
    if record.get("expires_at"):
        expiry=datetime.fromisoformat(record["expires_at"].replace("Z","+00:00"))
        if expiry.tzinfo is None:expiry=expiry.replace(tzinfo=timezone.utc)
        if expiry<=datetime.now(timezone.utc):raise Held("asset_expired","An asset's recorded permission expired.")
    if file_hash(meta["path"])!=record["sha256"]:raise Held("asset_changed","An asset changed after its provenance was recorded.")
    return {**record,"path":str(meta["path"])}


def choose_background(workspace, channel, request):
    ids=request.get("background_ids") or workspace.config()["channels"][channel].get("footage_ids",[])
    if not ids:raise Held("background_missing","Register permitted footage and add its ID to this channel's footage_ids. No gameplay is generated as a substitute.")
    candidates=[asset_record(workspace,item) for item in ids]
    videos=[a for a in candidates if a["kind"]=="video"]
    if not videos:raise Held("background_missing","This format needs recorded video footage.")
    return sorted(videos,key=lambda a:a["duration"],reverse=True)[0]


def pexels_video(workspace, query):
    key=os.environ.get("PEXELS_API_KEY")
    if not key:raise Held("pexels_key_missing","Optional Pexels acquisition needs PEXELS_API_KEY.")
    workspace.reserve_call("pexels",30)
    raw,_,_=fetch("https://api.pexels.com/v1/videos/search?"+urlencode({"query":query,"orientation":"portrait","per_page":3}),headers={"Authorization":key})
    videos=json.loads(raw).get("videos",[])
    if not videos:raise Held("stock_not_found","No matching stock clip was found.")
    video=videos[0]
    choices=[v for v in video.get("video_files",[]) if v.get("file_type")=="video/mp4" and v.get("width",0)>=540]
    if not choices:raise Held("stock_not_found","No suitable downloadable MP4 was available.")
    chosen=min(choices,key=lambda v:abs(v.get("width",720)-720))
    link=chosen["link"]
    host=urlparse(link).hostname or ""
    if host!="pexels.com" and not host.endswith(".pexels.com"):
        raise Held("stock_host","Stock download did not point to a supported Pexels media host.")
    data,_,_=fetch(link,maximum=180_000_000)
    path=workspace.root/"assets"/("pexels-"+uuid.uuid4().hex+".mp4");path.write_bytes(data)
    owner=video.get("user",{}).get("name","Pexels contributor")
    return register_asset(workspace,path,"licensed_stock",{"url":video.get("url"),"license":"https://www.pexels.com/license/","checked_at":now()},
                          attribution=f"Video by {owner} on Pexels: {video.get('url','')}")
