"""Route permitted source speech through the compositor without synthesizing it."""
from .assets import asset_record
from .core import Held
import math
import subprocess
from pathlib import Path
from .assets import register_asset
from .core import digest


def clip_timing(workspace, job, script):
    request=job["request"]
    asset=asset_record(workspace,request.get("clip_asset_id",""))
    if asset["kind"]!="video" or not asset["has_audio"]:
        raise Held("clip_audio_missing","The source-clip route needs a registered video with its original audio.")
    start=float(request.get("clip_start",0));end=float(request.get("clip_end",min(asset["duration"],45)))
    if not 0<=start<end<=asset["duration"] or not 1<=end-start<=179:
        raise Held("clip_range","Choose an actual one-to-179-second range inside the source clip.")
    if len(script["units"])!=1:raise Held("clip_script","Source clips use one editorial unit. A supplied transcript is optional; no invented speech alignment is made.")
    unit=script["units"][0]
    loop_count=request.get('loop_count',1)
    if type(loop_count)!=int or not 1<=loop_count<=8 or (end-start)*loop_count>179:raise Held('clip_loop','Use 1–8 repeats within 179 seconds.')
    original=asset
    source_start,source_end=start,end
    if loop_count>1:
        path=workspace.job_dir(job['id'])/('loop-source-'+digest([asset['sha256'],start,end])[:16]+'.mp4')
        if not path.exists():
            process=subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-ss',str(start),'-i',asset['path'],'-t',str(end-start),
                '-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-c:a','aac',str(path)],capture_output=True,timeout=180)
            if process.returncode:raise Held('clip_loop_prepare','Could not prepare the bounded source range for looping.')
        made=register_asset(workspace,path,'licensed_stock',{'derived_from':asset['id'],'synthetic':asset.get('evidence',{}).get('synthetic',False)},test_only=asset.get('test_only',False))
        asset=asset_record(workspace,made['id']);start=0;end=asset['duration']*loop_count
    captions=request.get('caption_cues',[])
    if loop_count>1:captions=[{**cue,'start':cue['start']+repeat*asset['duration'],'end':cue['end']+repeat*asset['duration']} for repeat in range(loop_count) for cue in captions]
    if not isinstance(captions,list) or len(captions)>1000:raise Held('caption_contract','Invalid clip caption list.')
    for cue in captions:
        if not isinstance(cue,dict) or not isinstance(cue.get('text'),str):raise Held('caption_contract','Invalid caption cue.')
        left,right=float(cue.get('start',-1)),float(cue.get('end',-1))
        if not math.isfinite(left+right) or not 0<=left<right<=end-start+.1:raise Held('caption_contract','Caption times must be inside the selected clip.')
    return {"version":1,"source":"original_clip","voice":"Original source audio","model_sha256":asset["sha256"],
            "duration":end-start,"clip":asset,"clip_start":start,'caption_cues':captions,'source_assets':[original],'loop_count':loop_count,
            'source_range':{'start':source_start,'end':source_end},
            "units":[{"id":unit["id"],"start":0,"speech_end":end-start,"end":end-start,"duration":end-start,
                      "text":unit["text"] if request.get("transcript_verified") is True else ""}]}
