"""Standalone resumable production plans using Gemini and local production tools.

No OpenAI service or ChatGPT session is used. A plan is data, not executable code.
The batch creates stable pipeline jobs and copies reviewable output into Resources.
"""
from array import array
from contextlib import contextmanager
from datetime import datetime,timezone,timedelta
import json
import math
from pathlib import Path
import random
import re
import shutil
import threading
import time
import uuid
import wave

from shorts_editor.store import write_json
from .assets import asset_record,register_asset
from .browser_agent import create_generation,import_generation,production_from_generation
from .core import Held,now,digest,file_hash,redact
from .pipeline import Pipeline
from .playbooks import PLAYBOOKS,get_playbook


PROJECT_ROOT=Path(__file__).resolve().parents[2]
PORTRAIT='8be2ec05e46e467b90a5fea879f817aa'
GAMEPLAY='023fa5cb353d4fc1bdd38a6e65600a5c'


def _date():
    return datetime.now(timezone(timedelta(hours=5,minutes=30))).date().isoformat()


def default_plan(resources_root=None):
    resources=Path(resources_root or PROJECT_ROOT/'Resources').resolve()
    # This exact download was supplied by the owner as generated ASMR. Never
    # infer permission or subject matter from the newest arbitrary MP4.
    source=resources/'Generated Video November 02, 2026 - 12_46AM.mp4'
    chat={'bottom_kind':'asmr','require_music':True,'test_only':True}
    if source.is_file():chat.update(bottom_source_file=str(source),bottom_source_type='owner_generated',
        bottom_source_evidence={'owner_supplied':True,'description':'Owner-supplied generated clay ASMR download; model not independently verified'})
    return {'version':1,'id':'playbooks-'+_date(),'created_at':now(),'output_root':str(resources/'Productions'),
            'note':'Local playbook previews using Gemini and local voice/FFmpeg. Add explicit permitted format-matched music; aura also needs four distinct permitted visuals. Missing prerequisites hold before generation. Publishing stays disabled.',
            'items':[{'id':'mystery-last-floor','kind':'playbook','playbook':'horror_stock','channel':'entertainment',
                      'topic':'Original elevator mystery with planted clues and a concrete phone-message reveal',
                      'request':{'fiction':True,'media_mode':'stock','bottom_kind':'none','require_music':True,'test_only':True}},
                     {'id':'tea-wrong-texter','kind':'playbook','playbook':'tea_chat','channel':'entertainment',
                      'topic':'Original fictional chat: a friend sitting beside you receives a message apparently sent by you; reveal the actual sender',
                      'request':chat},
                     {'id':'aura-progression','kind':'playbook','playbook':'aura_progression','channel':'entertainment',
                      'topic':'A supported before/after contrast using the supplied visual evidence, ending on its strongest actual moment',
                      'request':{'bottom_kind':'none','visual_asset_ids':[],'require_music':True,'test_only':True}}]}


def _validate_playbook_item(item,channels=None):
    if not isinstance(item.get('playbook'),str) or item['playbook'] not in PLAYBOOKS:raise ValueError('Choose a supported playbook name')
    if not isinstance(item.get('topic'),str) or not item['topic'].strip() or len(item['topic'])>180:
        raise ValueError('A playbook item needs a nonempty topic of at most 180 characters')
    channel=item.get('channel')
    if not isinstance(channel,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',channel):raise ValueError('A playbook item needs a safe channel profile name')
    if channels is not None and channel not in channels:raise ValueError('Unknown channel profile in playbook batch item')
    request=item.get('request')
    if not isinstance(request,dict):raise ValueError('A playbook item request must be an object')
    for key,value in [('playbook',item['playbook']),('topic',item['topic']),('format',PLAYBOOKS[item['playbook']]['format'])]:
        if key in request and request[key]!=value:raise ValueError('Batch request conflicts with item '+key)
    if 'batch_item_token' in request:raise ValueError('Batch recovery tokens are managed by the runner')
    if 'require_music' in request and type(request['require_music']) is not bool:raise ValueError('require_music must be a boolean')


def _paths(plan_path=None):
    path=Path(plan_path or PROJECT_ROOT/'Resources/Plans/playbook-starter.json').resolve()
    if not path.exists():
        if plan_path is not None:raise ValueError('The selected production plan does not exist')
        path.parent.mkdir(parents=True,exist_ok=True)
        try:
            with path.open('x',encoding='utf-8') as stream:json.dump(default_plan(),stream,ensure_ascii=False,indent=2)
        except FileExistsError:pass
    try:plan=json.loads(path.read_text(encoding='utf-8-sig'))
    except (ValueError,UnicodeError):raise ValueError('The production plan is not valid UTF-8 JSON')
    if not isinstance(plan,dict) or plan.get('version')!=1:raise ValueError('Use production plan version 1')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',str(plan.get('id',''))):raise ValueError('Plan ID must be a safe stable name')
    items=plan.get('items')
    if not isinstance(items,list) or not 1<=len(items)<=20:raise ValueError('A batch needs 1-20 items')
    ids=set()
    for item in items:
        if not isinstance(item,dict) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',str(item.get('id',''))) or item['id'] in ids:
            raise ValueError('Batch item IDs must be safe and unique')
        if item.get('kind') not in ('asmr','mystery','aura','playbook'):raise ValueError('Unknown batch video format')
        if item['kind']=='playbook':_validate_playbook_item(item)
        if item['kind']=='asmr' and (not isinstance(item.get('source_file'),str) or not item['source_file'].strip()):
            raise ValueError('An ASMR item needs a source_file path')
        ids.add(item['id'])
    output_root=plan.get('output_root',str(PROJECT_ROOT/'Resources/Productions'))
    if not isinstance(output_root,str) or not output_root.strip():raise ValueError('output_root must be a nonempty folder path')
    output=Path(output_root).resolve()/plan['id']
    output.mkdir(parents=True,exist_ok=True)
    return path,plan,output,output/'batch.json'


@contextmanager
def _batch_lease(ws,key):
    owner=uuid.uuid4().hex;name='batch:'+digest(str(key));ws.worker_lock(owner,name=name)
    stopped=threading.Event();lost=threading.Event()
    def renew():
        while not stopped.wait(30):
            try:ws.worker_lock(owner,name=name)
            except Exception:lost.set();return
    thread=threading.Thread(target=renew,daemon=True);thread.start()
    try:yield lost
    finally:
        stopped.set();thread.join(timeout=2);ws.worker_lock(owner,release=True,name=name)


def _prepare_unlocked(ws,plan_path=None):
    path,plan,output,manifest_path=_paths(plan_path)
    for item in plan['items']:
        if item['kind']=='playbook':_validate_playbook_item(item,ws.config()['channels'])
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('plan_sha256')!=file_hash(path):raise Held('batch_plan_changed','This plan changed after initialization. Use a new plan ID for changed content.')
        if manifest.get('workspace')!=str(ws.root):raise Held('batch_workspace','This batch belongs to a different pipeline workspace')
        return manifest
    manifest={'version':1,'id':plan['id'],'plan_path':str(path),'plan_sha256':file_hash(path),'workspace':str(ws.root),
              'output_root':str(output),'created_at':now(),'updated_at':now(),'status':'queued',
              'runtime':{'text_provider':'Gemini free-tier API','speech':'local configured Kokoro/Piper','editor':'local FFmpeg','openai_calls':0},
              'items':[{'id':i['id'],'kind':i['kind'],'status':'queued','job_id':None,'output_folder':str(output/i['id'])} for i in plan['items']]}
    write_json(manifest_path,manifest)
    return manifest


def prepare_batch(ws,plan_path=None):
    _,_,_,manifest_path=_paths(plan_path)
    # Existing manifests are atomically replaced, so readers need not block a running batch.
    if manifest_path.exists():return _prepare_unlocked(ws,plan_path)
    with _batch_lease(ws,manifest_path):return _prepare_unlocked(ws,plan_path)


def _aggregate(items,fallback='waiting'):
    states=[i['status'] for i in items]
    if states and all(s=='ready' for s in states):return 'ready'
    if 'running' in states:return 'running'
    if fallback=='paused':return 'paused'
    return 'queued' if all(s=='queued' for s in states) else 'waiting'


def _export_valid(item,job):
    hashes=item.get('output_hashes',{})
    if job['status']!='ready' or not hashes:return False
    return _artifacts_valid(job) and all(Path(path).is_file() and file_hash(path)==sha for path,sha in hashes.items())


def _artifacts_valid(job):
    for stage,record in job.get('artifacts',{}).items():
        if record.get('sha256'):
            path=Path(record['path'])
            if not path.is_file() or file_hash(path)!=record['sha256']:return False
        for value,sha in record.get('files',{}).items():
            path=Path(value)
            if not path.is_file() or file_hash(path)!=sha:return False
    return True


def batch_status(ws,plan_path=None):
    manifest=prepare_batch(ws,plan_path)
    for item in manifest['items']:
        if item.get('job_id'):
            job=ws.get(item['job_id']);item.update(status=job['status'],stage=job['stage'],message=job['message'],error_code=job.get('error_code'))
            if job['status']=='ready' and not _export_valid(item,job):
                item.update(status='export_pending',message='Pipeline job is ready; Resources copies need export or integrity repair')
    manifest['status']=_aggregate(manifest['items'],manifest.get('status'))
    return manifest


def _music(ws,resources):
    """An original simple instrumental, no downloaded or imitated recording."""
    path=Path(resources)/'Music/Original/impact-bed-v1.wav';path.parent.mkdir(parents=True,exist_ok=True)
    evidence_path=path.with_suffix('.asset.json')
    if evidence_path.exists():
        saved=json.loads(evidence_path.read_text());return asset_record(ws,saved['asset_id'])
    rate=44100;seconds=24;beat=60/128;rng=random.Random(81173);samples=[]
    notes=[73.416,73.416,87.307,82.407]
    for n in range(rate*seconds):
        t=n/rate;b=t/beat;phase=b%1;bar=int(b//4);bass=notes[bar%4]
        kick=math.sin(2*math.pi*(48*t+7*(1-math.exp(-phase*28))))*math.exp(-phase*14)
        snare=rng.uniform(-1,1)*math.exp(-phase*32) if int(b)%4 in (1,3) else 0
        hat=rng.uniform(-1,1)*math.exp(-((b*2)%1)*38)
        tone=math.tanh(2.4*math.sin(2*math.pi*bass*t))*(.35+.65*(1-math.exp(-phase*12)))
        swell=min(1,t/.3,(seconds-t)/.5)
        samples.append((.36*kick+.13*snare+.045*hat+.16*tone)*max(0,swell))
    peak=max(abs(v) for v in samples) or 1
    pcm=array('h',(round(v/peak*25000) for v in samples))
    with wave.open(str(path),'wb') as audio:audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(rate);audio.writeframes(pcm.tobytes())
    asset=register_asset(ws,path,'original_graphic',{'generator':'batches-original-impact-bed-v1','composition':'Original deterministic synthesized percussion and bass; no samples or artist imitation','commercial':True})
    write_json(evidence_path,{'asset_id':asset['id'],'sha256':asset['sha256'],'note':'Original program-generated instrumental. Not a claim about a downloaded song.'})
    return asset_record(ws,asset['id'])


def _playbook_request(ws,item,folder):
    """Check explicit local prerequisites before creating a model-driven job.

    Registered assets retain their eligibility checks. A bare local path is not
    permission; only an explicitly owner-generated lower panel may be imported.
    """
    _validate_playbook_item(item,ws.config()['channels'])
    rules=get_playbook(item['playbook'])
    request=json.loads(json.dumps(item['request']))
    request.update(playbook=item['playbook'],topic=item['topic'],format=rules['format'])
    request.setdefault('fiction',item['playbook'] in ('horror_stock','tea_chat','cutout_ensemble'))
    request.setdefault('resolution','720p')
    # Newly initialized playbook jobs inspect actual media. Existing jobs/exports
    # remain hash-bound to their original immutable requests.
    request.setdefault('visual_review','required')
    bottom_kind=request.get('bottom_kind','none')
    if bottom_kind not in rules['bottom']:raise Held('playbook_background','The selected playbook does not allow this lower-panel type')
    request['bottom_kind']=bottom_kind
    music_id=request.get('music_id')
    if (item['playbook']=='aura_progression' or request.get('require_music',True)) and not music_id:
        raise Held('playbook_music_missing','Select an explicit permitted format-matched music_id; no generic instrumental will be substituted')
    checked={}
    def eligible(ref):
        if not isinstance(ref,str) or not ref.strip():raise Held('batch_asset_request','Asset references must be registered nonempty IDs')
        if ref.startswith('generation:'):raise Held('generated_media_pending','Import the generated asset and supply its registered ID before starting the batch')
        if ref not in checked:checked[ref]=asset_record(ws,ref)
        return checked[ref]
    if music_id and not eligible(music_id).get('has_audio'):
        raise Held('music_missing_audio','Selected soundtrack has no audio')
    for key in ('visual_asset_ids','background_ids'):
        values=request.get(key,[])
        if not isinstance(values,list):raise Held('batch_asset_request',key+' must be an array of registered asset IDs')
        for ref in values:eligible(ref)
    for key in ('media_assets','cast_assets'):
        values=request.get(key,{})
        if not isinstance(values,dict):raise Held('batch_asset_request',key+' must map unit/cast names to registered asset IDs')
        for ref in values.values():eligible(ref)
    if item['playbook']=='aura_progression':
        visuals=request.get('visual_asset_ids',[])
        if len(set(visuals))<4:raise Held('aura_progression_assets','Supply at least four distinct permitted before/after visual_asset_ids before generation')
        assets=[eligible(ref) for ref in visuals]
        if any(a.get('kind') not in ('image','video') for a in assets):raise Held('aura_progression_assets','Aura progression assets must be images or video clips')
        if len({a['sha256'] for a in assets})<4:raise Held('aura_progression_assets','Copies of one file are not four distinct aura visuals')
    bottom_id=request.get('bottom_asset_id');source_file=request.get('bottom_source_file')
    if source_file and bottom_id:raise Held('batch_bottom_source','Choose a registered bottom_asset_id or an explicitly owner-generated source file, not both')
    if bottom_kind=='none' and (source_file or bottom_id):raise Held('playbook_background','A lower-panel asset requires its explicit asmr or gameplay bottom_kind')
    if source_file:
        if request.get('bottom_source_type')!='owner_generated':
            raise Held('batch_bottom_permission','Only an explicitly owner_generated local source can be imported; use registered eligible IDs for other footage')
        evidence=request.get('bottom_source_evidence')
        if not isinstance(evidence,dict) or not evidence:raise Held('asset_evidence_missing','Owner-generated lower-panel imports need explicit provenance evidence')
        if not isinstance(source_file,str) or not source_file.strip():raise Held('batch_source_missing','Supply the owner-generated lower-panel file path')
        source=Path(source_file).resolve()
        if not source.is_file():raise Held('batch_source_missing','The explicitly supplied owner-generated lower-panel file is missing')
        folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);checkpoint=folder/'bottom-source.json'
        sha=file_hash(source)
        if checkpoint.exists():
            saved=json.loads(checkpoint.read_text(encoding='utf-8'))
            if saved.get('file_sha256')!=sha or saved.get('original_file')!=str(source):
                raise Held('batch_source_changed','The lower-panel source changed after initialization; create a new plan ID')
            bottom_id=saved['asset_id']
        else:
            asset=register_asset(ws,source,'original_graphic',{'source_type':'owner_generated','owner_evidence':evidence,
                'description':'Owner-supplied generated lower-panel footage; model and generation independently unverified'},test_only=request.get('test_only',False))
            bottom_id=asset['id']
            write_json(checkpoint,{'asset_id':bottom_id,'file_sha256':sha,'original_file':str(source)})
        request['bottom_asset_id']=bottom_id
        for key in ('bottom_source_file','bottom_source_type','bottom_source_evidence'):request.pop(key,None)
    if bottom_kind!='none':
        if not bottom_id:raise Held('background_missing','Supply an eligible bottom_asset_id or explicitly owner-generated lower-panel source before generation')
        if eligible(bottom_id).get('kind')!='video':raise Held('background_missing','The lower panel requires an actual registered video')
    return request


def _create_job(ws,item,folder,resources,token=None):
    marker={'batch_item_token':token} if token else {}
    if item['kind']=='playbook':
        request=_playbook_request(ws,item,folder)
        return ws.create(item['channel'],{**request,**marker})
    if item['kind']=='asmr':
        source=Path(item['source_file']).resolve()
        if not source.is_file():raise Held('batch_source_missing','Save the generated ASMR clip in Resources before this batch can render it')
        checkpoint=folder/'generation-source.json'
        if checkpoint.exists():
            saved=json.loads(checkpoint.read_text())
            if saved['file_sha256']!=file_hash(source):raise Held('batch_source_changed','The source clip changed after this batch was initialized; create a new plan ID')
            generated={'id':saved['generation_job']}
        else:
            generated=create_generation(ws,'Original turquoise-clay flower-stamp ASMR scene supplied by the owner after browser generation. Preserve the original source sound; do not claim a seamless loop.',kind='video',model='Owner-supplied Google generated result; model not independently verified')
            write_json(checkpoint,{'generation_job':generated['id'],'file_sha256':file_hash(source),'original_file':str(source),
                'notes':['Owner supplied generated clip; preserve aspect/subject with blurred fill.','Not a seamless loop: final kneaded lump differs from starting dome.','Do not mass-repost the same ASMR as new content.']})
        import_generation(ws,generated['id'],source)
        job=production_from_generation(ws,generated['id'],'The flower stamp payoff | Original AI ASMR',loop_count=1)
        return job
    if item['kind']=='mystery':
        return ws.create('entertainment',{**marker,'format':'cutout','fiction':True,'story_visuals':'from_script',
            'topic':'Original elevator mystery with a phone-message reveal and a complete unsettling twist',
            'creative_brief':'Write a NEW original 25-35 second fictional micro-mystery, roughly 65-85 words and 7-9 very short units. Hook immediately with one impossible detail in an elevator. The story must remain clear on first hearing, progress through visible events and end with a specific twist that resolves/reframes the opening. No generic advice, no gore, no celebrity or real allegations. One narrator; no long dialogue. Each visual_query MUST start with exactly one supported tag and colon: elevator:, phone:, hallway:, door:, stairwell:, security:. Choose the scene that actually shows the spoken beat. Follow the tag with a short literal visible prop/detail, maximum 60 characters. Captions/onscreen must be 3-8 words. A phone message must be readable and directly relevant. Use distinct relevant scenes, not a repeating character stage. Label the description original fictional story. No CTA; effect only at payoff.',
            'resolution':'720p','test_only':True})
    portrait=asset_record(ws,item.get('portrait_asset_id',PORTRAIT));gameplay=asset_record(ws,item.get('gameplay_asset_id',GAMEPLAY))
    music=_music(ws,resources)
    # The model generates short original edit captions, not quotes attributed to the photo subject.
    return ws.create('entertainment',{**marker,'format':'aura','fiction':True,'topic':'Composure over noise: an original cinematic editorial aura edit',
        'creative_brief':'Create a tight portrait/gameplay aura edit, NOT a factual biography. Exactly 6 short caption units, about 2-5 words each. Hook with a relatable contrast: loud reactions versus calm focus; build to a sharp payoff. These are original editorial captions, NOT quotes or claims about the photographed person. Do not invent achievements, wealth, dialogue, opinions, events, endorsements or advice attributed to anyone. Description must explicitly say this is a fan/editorial visual edit, captions are not the pictured person\'s words or endorsement. No spoken narration needed. Keep each text/onscreen very short, no CTA. Use punch only at final beat.',
        'media_assets':{},'portrait_asset_id':portrait['id'],'background_ids':[gameplay['id']],'music_id':music['id'],
        'resolution':'720p','test_only':True})


def _copy_outputs(ws,job,folder):
    folder.mkdir(parents=True,exist_ok=True)
    if not _artifacts_valid(job):raise Held('batch_artifact_changed','A pipeline checkpoint or referenced output changed; resolve it before exporting')
    hashes={}
    def copy(source,destination):
        source=Path(source);destination=Path(destination)
        before=file_hash(source);temporary=destination.with_name(destination.name+'.'+uuid.uuid4().hex+'.tmp')
        shutil.copy2(source,temporary)
        if file_hash(temporary)!=before or file_hash(source)!=before:
            raise Held('batch_export_changed','An output changed during export; retry the Resources copy')
        temporary.replace(destination);hashes[str(destination)]=before
    for name in ('request','research','script','voice','visuals','direct','quality','package','metadata'):
        source=ws.job_dir(job['id'])/(name+'.json')
        if source.is_file():copy(source,folder/source.name)
    render_record=job['artifacts'].get('render')
    if render_record:
        rendered=json.loads(Path(render_record['path']).read_text())
        for key,target in [('video','video.mp4'),('cover','cover.png'),('captions','captions.srt'),('manifest','render-manifest.json')]:
            if rendered.get(key) and Path(rendered[key]).is_file():copy(rendered[key],folder/target)
    voice=ws.job_dir(job['id'])/'voice.json'
    if voice.is_file():
        record=json.loads(voice.read_text());audio=record.get('audio')
        if audio and Path(audio).is_file():copy(audio,folder/'narration.wav')
    reviews=ws.job_dir(job['id'])/'visual-review'
    if reviews.is_dir():
        for source in reviews.rglob('*'):
            if source.is_file() and source.suffix in ('.json','.jpg'):
                destination=folder/'visual-review'/source.relative_to(reviews)
                destination.parent.mkdir(parents=True,exist_ok=True);copy(source,destination)
    if job['status']=='ready':
        required=['video.mp4','cover.png','captions.srt','render-manifest.json','script.json','quality.json']
        if any(str(folder/name) not in hashes for name in required):raise Held('batch_export_missing','A ready job is missing a required output; inspect its artifacts')
        qa=json.loads((folder/'quality.json').read_text())
        if qa['video_sha256']!=hashes[str(folder/'video.mp4')]:raise Held('batch_export_changed','Exported video no longer matches the quality report')
    return hashes


def run_batch(ws,plan_path=None,stop=None,progress=None,stop_file=None):
    _,_,_,manifest_path=_paths(plan_path)
    with _batch_lease(ws,manifest_path) as lost:
        return _run_batch(ws,plan_path,stop,progress,stop_file,lost)


def _run_batch(ws,plan_path,stop,progress,stop_file,lost):
    manifest=_prepare_unlocked(ws,plan_path);path,plan,output,manifest_path=_paths(plan_path)
    resources=PROJECT_ROOT/'Resources'
    def halted():
        if lost.is_set():raise Held('batch_lease_lost','Batch lease renewal failed; no next job was started')
        return bool((stop() if callable(stop) else stop.is_set() if stop is not None else False) or (stop_file and Path(stop_file).exists()))
    def save():
        manifest['updated_at']=now();write_json(manifest_path,manifest)
        if progress:progress(manifest)
    manifest['status']='running';save()
    for spec,item in zip(plan['items'],manifest['items']):
        if halted():manifest['status']='paused';save();return manifest
        folder=Path(item['output_folder']);folder.mkdir(parents=True,exist_ok=True)
        try:
            if not item.get('job_id'):
                token=digest([str(manifest_path),manifest['plan_sha256'],spec['id']])
                # The marker is inside the immutable job request, recovering a crash between
                # job creation and manifest save without another Gemini request/job.
                with ws.connect() as db:
                    found=db.execute("SELECT id FROM jobs WHERE json_extract(request,'$.batch_item_token')=? ORDER BY created_at LIMIT 1",(token,)).fetchone()
                job=ws.get(found['id']) if found else _create_job(ws,spec,folder,resources,token)
                item['job_id']=job['id'];save()
            job=ws.get(item['job_id'])
            if job['status'] in ('held','failed'):
                # Retry exactly its failed stage; upstream artifacts and generated script stay intact.
                ws.reset(job['id'],job['stage'] if job['stage'] in ('research','script','voice','visuals','direct','render','quality','package') else 'research')
            if job['status']=='retry_wait' and (job.get('retry_at') or 0)>time.time():
                item.update(status=job['status'],stage=job['stage'],message=job['message']);save();continue
            if halted():manifest['status']='paused';save();return manifest
            if job['status']!='ready':job=Pipeline(ws).run(job['id'])
            item.update(status=job['status'],stage=job['stage'],message=job['message'],error_code=job.get('error_code'))
            item['output_hashes']=_copy_outputs(ws,job,folder)
            if job['status']=='ready':
                item['video']=str(folder/'video.mp4');item['cover']=str(folder/'cover.png')
                scripted=json.loads((folder/'script.json').read_text())
                item['script_origin']=scripted.get('origin');item['duration']=json.loads((folder/'quality.json').read_text())['duration']
        except Exception as exc:
            item.update(status='held',message=redact(exc),error_code=getattr(exc,'code',type(exc).__name__))
        save()
    manifest['status']=_aggregate(manifest['items'])
    save();return manifest
