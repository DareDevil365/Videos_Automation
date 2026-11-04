import json
from pathlib import Path
import threading
import time
import uuid
import shutil

from shorts_editor.render import render_project
from shorts_editor.store import Store, write_json
from .core import Held, STAGES, digest, file_hash, redact
from .research import research_job
from .writer import Gemini, write_script
from .voice import synthesize
from .visuals import build_visuals
from .director import direct
from .quality import inspect_render, package
from .clips import clip_timing
from .transcripts import burn_captions
from .entertainment import aura_timing


def referenced_files(value):
    found=set()
    if isinstance(value,dict):
        for key,item in value.items():
            if key in ("file","audio","video","project","compose_job","cover","captions") and isinstance(item,str):
                path=Path(item)
                if path.is_absolute() and path.is_file():found.add(path)
            found.update(referenced_files(item))
    elif isinstance(value,list):
        for item in value:found.update(referenced_files(item))
    return found


class Pipeline:
    def __init__(self, workspace, provider=None, voice_fn=None):
        self.workspace=workspace;self.provider=provider or Gemini(workspace);self.voice_fn=voice_fn or synthesize

    def run(self, job_id):
        ws=self.workspace;owner=uuid.uuid4().hex
        ws.worker_lock(owner)
        try:
            claimed=ws.claim(job_id,owner)
        except BaseException:
            ws.worker_lock(owner,release=True);raise
        if not claimed:ws.worker_lock(owner,release=True);return ws.get(job_id)
        stopped=threading.Event()
        def heartbeat():
            while not stopped.wait(15):
                try:
                    if not ws.heartbeat(job_id,owner):stopped.set();return
                    ws.worker_lock(owner)
                except Exception:stopped.set();return
        thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
        try:
            job=ws.get(job_id);folder=ws.job_dir(job_id);results={}
            from .playbooks import prepare_request
            job={**job,'request':prepare_request(job['request'])}
            from .visual_review import review_mode,review_assets,review_render
            review_mode(ws,job['request'])
            for stage in STAGES:
                current=ws.get(job_id)
                if current["status"]=="cancelled":raise Held("cancelled","Job cancelled.")
                if stopped.is_set():raise Held("lease_lost","Worker lease was lost; this worker stopped before advancing.")
                if shutil.disk_usage(ws.root).free<1024**3:raise Held('disk_low','Less than 1 GiB disk space remains. Free space before continuing.')
                if ws.config()["channels"][job["channel"]].get("paused"):raise Held("channel_paused","This channel is paused.")
                checkpoint=current["artifacts"].get(stage)
                if checkpoint:
                    path=Path(checkpoint["path"])
                    if not path.is_file() or file_hash(path)!=checkpoint["sha256"]:
                        raise Held("artifact_changed",f"Saved {stage} result changed. Reset this stage deliberately.")
                    for file,sha in checkpoint.get("files",{}).items():
                        if not Path(file).is_file() or file_hash(file)!=sha:raise Held("artifact_changed",f"An input/output of {stage} changed. Reset that stage.")
                    results[stage]=json.loads(path.read_text(encoding="utf-8"));continue
                ws.update(job_id,stage=stage,message=f"Running {stage}",error_code=None,retry_at=None)
                ws.event(job_id,"stage_started",{"stage":stage})
                if stage=="research":result=research_job(ws,job,self.provider)
                elif stage=="script":result=write_script(ws,job,results["research"],self.provider)
                elif stage=="voice":
                    fmt=results['script']['script']['format']
                    if fmt=='clip':result=clip_timing(ws,job,results['script']['script'])
                    elif fmt=='aura':result=aura_timing(ws,job,results['script']['script'],creative_plan=(results['script'].get('creative_plan') or {}).get('plan'))
                    elif job['request'].get('playbook') and self.voice_fn is synthesize:
                        from .playbooks import get_playbook
                        record=results['script'].get('creative_plan')
                        if not record:raise Held('creative_plan_missing','This playbook needs its validated second-pass edit plan')
                        rules=get_playbook(job['request']['playbook'])
                        result=synthesize(ws,results['script']['script'],folder/'voice',creative_plan=record['plan'],delivery=rules['voice'])
                        minimum,maximum=rules['seconds']
                        if result['duration']<minimum and result['duration']>=minimum*.92:
                            # A small pace correction changes actual speech, not empty
                            # padding or the story. Only one bounded retry is allowed.
                            delivery={**rules['voice'],'length_scale':min(1.8,rules['voice']['length_scale']*(minimum+.3)/result['duration'])}
                            previous=result['duration']
                            result=synthesize(ws,results['script']['script'],folder/'voice',creative_plan=record['plan'],delivery=delivery)
                            result['pace_adjustment']={'previous_duration':previous,'method':'one bounded local resynthesis','original_length_scale':rules['voice']['length_scale']}
                        if not minimum<=result['duration']<=maximum:
                            raise Held('playbook_duration',f'Measured voice is {result["duration"]:.1f}s; this format requires {minimum}-{maximum}s. Revise the script rather than pad it with empty silence.')
                    else:result=self.voice_fn(ws,results['script']['script'],folder/'voice')
                    if job['request'].get('playbook') in ('cutout_ensemble','documentary_chapter','illustrated_story') or job['request'].get('motion_graphics') is True:
                        from .dialogue_captions import align_dialogue
                        result=align_dialogue(ws,result)
                elif stage=="visuals":
                    record=results['script'].get('creative_plan')
                    if record and results['script']['script']['format']!='aura':
                        from .planned_visuals import build_planned_visuals
                        result=build_planned_visuals(ws,job,results['script']['script'],results['voice'],folder/'visuals',record,provider=self.provider)
                    else:result=build_visuals(ws,results["script"]["script"],results["voice"],folder/"visuals",job=job)
                    result['asset_review']=review_assets(ws,job,result,self.provider,folder/'visual-review')
                elif stage=="direct":result=direct(ws,job,results["script"]["script"],results["voice"],results["visuals"])
                elif stage=="render":
                    project=json.loads(Path(results["direct"]["project"]).read_text(encoding="utf-8"))
                    output_dir=folder/"renders"/results["direct"]["version"][:16];output_dir.mkdir(parents=True,exist_ok=True)
                    output=output_dir/"video.mp4"
                    if output.exists():
                        manifest_path=output.with_suffix(".manifest.json")
                        if not manifest_path.exists():raise Held("partial_render","An existing render lacks its complete manifest; preserve it and choose a fresh render attempt.")
                        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
                        if digest(manifest["project"])!=digest(project):raise Held("render_mismatch","Existing output belongs to a different project version.")
                    else:
                        manifest=render_project(project,Store(ws.root/"media"),output,
                            progress=lambda value,message:ws.update(job_id,message=f"{message} ({value*100:.0f}%)"),cancel=stopped)
                    # The visual builder has the actual measured narration captions.
                    captions=Path(results["visuals"]["captions"])
                    output.with_suffix(".srt").write_text(captions.read_text(encoding="utf-8"),encoding="utf-8")
                    if results['voice'].get('caption_cues'):
                        caption_options={'canvas':(1280,720) if project['resolution']=='720p' else (1920,1080)} if project.get('profile')=='documentary' else {}
                        burn_captions(output,results['voice']['caption_cues'],split=project['format']=='stack',caption_bar=results['voice'].get('caption_style')=='dialogue_bar',
                            bar_height=round(1280*job['request'].get('top_fraction',.65)/2)*2 if job['request'].get('bottom_asset_id') else 1280,**caption_options)
                    result={"video":str(output),"cover":str(output.with_suffix(".png")),"captions":str(output.with_suffix(".srt")),
                            "manifest":str(output.with_suffix(".manifest.json")),"duration":manifest["duration"]}
                    result['visual_review']=review_render(ws,job,results['script'],results['voice'],result,self.provider,folder/'visual-review'/'finished')
                    result['asset_review']=results['visuals'].get('asset_review',{'status':'not_requested'})
                elif stage=="quality":result=inspect_render(ws,job,results["research"],results["script"],results["voice"],results["direct"],results["render"])
                else:result=package(ws,job,results["research"],results["script"],results["voice"],results["direct"],results["render"],results["quality"])
                if ws.get(job_id)["status"]=="cancelled":raise Held("cancelled","Job cancelled before stage completion was committed.")
                path=folder/(stage+".json");write_json(path,result)
                artifacts=ws.get(job_id)["artifacts"]
                artifacts[stage]={"path":str(path),"sha256":file_hash(path),"files":{str(f):file_hash(f) for f in referenced_files(result)}}
                ws.update(job_id,artifacts=artifacts)
                ws.event(job_id,"stage_completed",{"stage":stage});results[stage]=result
            ws.update(job_id,status="ready",stage="ready",message="Local video, captions, packaging and checks are ready. Publishing remains separate.")
            ws.event(job_id,"ready",{"publication_ready":results["quality"]["publication_ready"]})
        except Held as exc:
            cancelled=ws.get(job_id)["status"]=="cancelled" or exc.code=="cancelled"
            ws.update(job_id,status="cancelled" if cancelled else "retry_wait" if exc.retry_after else "held",
                      error_code=exc.code,message=redact(exc),retry_at=time.time()+exc.retry_after if exc.retry_after else None,approval_hash=None)
            ws.event(job_id,"held",{"code":exc.code,"message":redact(exc)})
            if not cancelled:ws.alert(job_id+":"+exc.code,job_id,str(exc))
        except Exception as exc:
            ws.update(job_id,status="failed",error_code=type(exc).__name__,message=redact(exc),approval_hash=None)
            ws.event(job_id,"failed",{"type":type(exc).__name__,"message":redact(exc)})
            ws.alert(job_id+":"+type(exc).__name__,job_id,str(exc))
        finally:
            stopped.set();thread.join(timeout=2)
            ws.update(job_id,lease_owner=None,lease_until=None)
            ws.worker_lock(owner,release=True)
        return ws.get(job_id)

    def work_once(self):
        eligible=[]
        for job in reversed(self.workspace.jobs()):
            if job["status"]=="queued" or (job["status"]=="retry_wait" and (job["retry_at"] or 0)<=time.time()) or (job["status"]=="running" and (job["lease_until"] or 0)<time.time()):
                eligible.append(job)
        return self.run(eligible[0]["id"]) if eligible else None
