from pathlib import Path

from PIL import Image

from shorts_editor.jobspec import materialize_job
from shorts_editor.models import validate_project
from shorts_editor.store import Store, write_json
from .assets import asset_record, choose_background, register_asset
from .core import Held, digest
from .music_agent import choose_music


def direct(workspace, job, script, timing, visuals):
    profile=workspace.config()["channels"][job["channel"]]
    request=job["request"];folder=workspace.job_dir(job["id"])
    provenance=[]
    if visuals.get('planned_template'):
        from .playbooks import get_playbook
        rules=get_playbook(request['playbook'],request)
        bottom_id=request.get('bottom_asset_id')
        bottom_kind=request.get('bottom_kind','none')
        if bottom_kind not in rules['bottom']:raise Held('playbook_background','This lower-panel type is not allowed by the selected format')
        if bottom_id and bottom_kind=='none':raise Held('creative_layout','A lower-panel asset requires an explicit allowed lower-panel kind')
        if bottom_kind!='none' and not bottom_id:raise Held('background_missing','Select a registered lower-panel asset for this template')
        bottom=asset_record(workspace,bottom_id) if bottom_id else None
        if bottom and bottom['kind']!='video':raise Held('background_missing','A lower-panel recording must be a real video file')
        provenance.extend(asset_record(workspace,a['id']) for a in visuals['planned_provenance'])
        if bottom:provenance.append(bottom)
        rows=[]
        for unit,frame in zip(timing['units'],visuals['frames']):
            if unit['id']!=frame['unit_id']:raise Held('creative_units','Resolved visual and narration units differ')
            asset=asset_record(workspace,frame['media_id']);provenance.append(asset)
            rows.append({'duration':unit['duration'],'media_start':unit['start']%bottom['duration'] if bottom else 0,'secondary_start':0,
                'source_audio':False,'effect_at':max(.1,unit['duration']-.35) if unit['id']==script['edit']['payoff_unit_id'] else 180,
                'inputs':{'background':bottom['path'] if bottom else asset['path'],**({'foreground':asset['path']} if bottom else {})}})
        inputs={'narration':timing['audio']}
        music_id=request.get('music_id')
        if rules['music']['volume'] and not music_id and request.get('require_music',True):
            raise Held('playbook_music_missing','Select a permitted music asset matching this format; the rejected generic instrumental is not an automatic fallback')
        if music_id:
            music=asset_record(workspace,music_id)
            if not music['has_audio']:raise Held('music_missing_audio','Selected soundtrack has no audio')
            inputs['music']=music['path'];provenance.append(music)
        spec={'template':'stack' if bottom else 'focus','name':script['title'],'resolution':request.get('resolution','720p'),'fps':30,
            'inputs':inputs,'shots':rows,'music_volume':rules['music']['volume'],
            'composition':{'height':round(1280*request.get('top_fraction',.65)/2)*2/1280 if bottom else 1,'x':0,'y':0,'width':1,'foreground_fit':'cover','audio_source':'none',
                           'effect':script['edit']['effect'],'cta':False,'border_width':0,'glow':0}}
        if request.get('playbook') in ('documentary_chapter','illustrated_story'):
            spec.update(profile='documentary')
            spec['composition']['effect']='none'
        if request.get('playbook')=='server_chat' and request.get('chat_editing_version')==2:
            spec['composition']['effect']='none'  # The compiled chat editor owns emphasis, not model edit hints.
        project=materialize_job(spec,Store(workspace.root/'media'),folder)
        write_json(folder/'compose-job.json',spec);write_json(folder/'render-project.json',project)
        return {'compose_job':str(folder/'compose-job.json'),'project':str(folder/'render-project.json'),'duration':timing['duration'],
            'version':digest([project,timing['model_sha256']]),'provenance':provenance,'fiction':script['fiction'],
            'audio_routing':'Measured directed cast speech; lower panel muted; explicit format-matched permitted music.'}
    stock=bool(visuals.get('selected_media'))
    for asset in visuals.get('montage_sources',[]):provenance.append(asset_record(workspace,asset['id']))
    if script["format"]=="clip":
        source=timing["clip"];provenance.append(source)
        provenance.extend(a for a in timing.get('source_assets',[]) if a['id']!=source['id'])
        split=bool(request.get("background_ids") or profile.get("footage_ids"))
        background=choose_background(workspace,job["channel"],request) if split else source
        if split:provenance.append(background)
        spec={"template":"stack" if split else "focus","name":script["title"],"resolution":request.get("resolution","720p"),"fps":30,
              "composition":{"audio_source":"foreground" if split else "background","effect":script["edit"]["effect"],"cta":script["edit"]["cta"]},
              "shots":[{"duration":timing["duration"],"media_start":0 if split else timing["clip_start"],"secondary_start":timing["clip_start"],
                        "source_audio":True,"inputs":{"background":background["path"],**({"foreground":source["path"]} if split else {})}}]}
        clip_music=request.get('music_id') or profile.get('music_id')
        if not clip_music and request.get('music_category'):clip_music=choose_music(workspace,request['music_category'],request.get('auto_download_music',False),request.get('music_query'))['id']
        if clip_music:
            music=asset_record(workspace,clip_music)
            if not music['has_audio']:raise Held('music_missing_audio','Selected music has no audio.')
            provenance.append(music);spec['inputs']={'music':music['path']};spec['music_volume']=.1
        project=materialize_job(spec,Store(workspace.root/"media"),folder)
        write_json(folder/"compose-job.json",spec);write_json(folder/"render-project.json",project)
        return {"compose_job":str(folder/"compose-job.json"),"project":str(folder/"render-project.json"),"duration":timing["duration"],
                "version":digest(project),"provenance":provenance,"fiction":script["fiction"],"audio_routing":"Original permitted source speech; other footage muted."}
    if script['format'] in ('aura','cutout'):
        split=script['format']=='aura' or bool(request.get('background_ids') or profile.get('footage_ids'))
        if request.get('playbook')=='aura_progression':split=request.get('bottom_kind','none')=='gameplay'
        if script['format']=='cutout' and request.get('story_visuals') and request.get('story_full_frame',True):split=False
        gameplay=choose_background(workspace,job['channel'],request) if split else None
        if gameplay:provenance.append(gameplay)
        provenance.extend(asset_record(workspace,a['id']) for a in visuals.get('aura_provenance',[]))
        rows=[]
        for unit,frame in zip(timing['units'],visuals['frames']):
            made=register_asset(workspace,frame['file'],'licensed_stock' if script['format']=='aura' else 'original_graphic',
                {'generator':script['format']+'-scene-v1','source_asset_ids':[a['id'] for a in visuals.get('aura_provenance',[])]})
            provenance.append(asset_record(workspace,made['id']))
            rows.append({'duration':unit['duration'],'media_start':unit['start']%gameplay['duration'] if gameplay else 0,'secondary_start':0,
                'source_audio':False,'effect_at':max(.1,unit['duration']-.35) if unit['id']==script['edit']['payoff_unit_id'] else 180,
                'inputs':{'background':gameplay['path'] if gameplay else frame['file'],**({'foreground':frame['file']} if split else {})}})
        inputs={}
        if timing.get('audio'):inputs['narration']=timing['audio']
        music_id=timing.get('music_id') or request.get('music_id') or profile.get('music_id')
        if not music_id and request.get('music_category'):music_id=choose_music(workspace,request['music_category'],request.get('auto_download_music',False),request.get('music_query'))['id']
        if music_id:
            music=asset_record(workspace,music_id);inputs['music']=music['path'];provenance.append(music)
        spec={'template':'stack' if split else 'focus','name':script['title'],'resolution':request.get('resolution','720p'),'fps':30,
            'inputs':inputs,'shots':rows,'music_volume':.55 if request.get('playbook')=='aura_progression' else .65 if script['format']=='aura' else .1,
            'composition':{'height':.65,'audio_source':'none','effect':script['edit']['effect'],'cta':script['edit']['cta'],'border_width':2,'glow':8}}
        if request.get('story_visuals') and not split:
            spec['composition'].update(x=0,y=0,width=1,height=1,foreground_fit='contain',border_width=0,glow=0)
        if request.get('playbook')=='aura_progression' and not split:
            spec['composition'].update(x=0,y=.05,width=1,height=.9,foreground_fit='contain',border_width=0,glow=0)
        project=materialize_job(spec,Store(workspace.root/'media'),folder)
        write_json(folder/'compose-job.json',spec);write_json(folder/'render-project.json',project)
        return {'compose_job':str(folder/'compose-job.json'),'project':str(folder/'render-project.json'),'duration':timing['duration'],
            'version':digest([project,timing['model_sha256']]),'provenance':provenance,'fiction':script['fiction'],
            'audio_routing':'No imitated creator speech. Original narration when applicable; licensed music and muted background footage.'}
    if script["format"]=="chat":
        background=choose_background(workspace,job["channel"],request)
        provenance.append(background)
    else:
        path=folder/"visuals"/"background.png"
        Image.new("RGB",(720,1280),"#faf9f6").save(path)
        background=register_asset(workspace,path,"original_graphic",{"generator":"lesson background v1"})
        background=asset_record(workspace,background["id"]);provenance.append(background)
    shots=[]
    base_offset=int(job['id'][:8],16)%max(1,int(background['duration']-timing['duration'])) if background['kind']=='video' else 0
    timeline=[({'id':cut['unit_id'],'duration':cut['duration'],'start':cut['start']},cut) for cut in visuals['cuts']] if visuals.get('cuts') else list(zip(timing['units'],visuals['frames']))
    for index,(unit,frame) in enumerate(timeline):
        if stock:
            background=asset_record(workspace,frame['media_id'])
            if background['id'] not in {a['id'] for a in provenance}:provenance.append(background)
            base_offset=0
        if frame["unit_id"]!=unit["id"]:raise Held("timing_mismatch","Speech and visual unit IDs do not match.")
        shot={"duration":unit["duration"],"media_start":((base_offset+unit["start"])%background["duration"]) if background["kind"]=="video" else 0,
              "source_audio":False,"effect_at":min(unit["duration"]-.05,max(.1,unit["duration"]-.35)) if unit["id"]==script["edit"]["payoff_unit_id"] and frame.get('payoff_end',True) else 180,
              "inputs":{"background":background["path"],"foreground":frame["file"]}}
        shots.append(shot)
    composition={"audio_source":"none","effect":script["edit"]["effect"],"cta":script["edit"]["cta"],
                 "cta_at":max(0,timing["duration"]-2.5),"cta_duration":2}
    if stock:composition.update(height=.2,foreground_fit='contain')
    elif script["format"]=="lesson":composition.update(x=0,y=0,width=1,height=1,foreground_fit="contain")
    inputs={"narration":timing["audio"]}
    music_id=request.get("music_id") or profile.get("music_id")
    if not music_id and request.get('music_category'):
        music_id=choose_music(workspace,request['music_category'],request.get('auto_download_music',False),request.get('music_query'))['id']
    if music_id:
        music=asset_record(workspace,music_id)
        if not music["has_audio"]:raise Held("music_missing_audio","The selected music file contains no audio.")
        inputs["music"]=music["path"];provenance.append(music)
    spec={"template":"stack" if stock else "overlay","name":script["title"],"resolution":request.get("resolution","720p"),"fps":30,
          "inputs":inputs,"shots":shots,"composition":composition,"music_volume":.10}
    project=materialize_job(spec,Store(workspace.root/"media"),folder)
    # A payoff effect belongs to the resolved payoff unit, not every shot.
    payoff_id=script["edit"]["payoff_unit_id"]
    for index,(unit,frame) in enumerate(timeline):
        if unit['id']!=payoff_id or not frame.get('payoff_end',True):project['scenes'][index]['effect_at']=180
    write_json(folder/"compose-job.json",spec)
    write_json(folder/"render-project.json",project)
    result={"compose_job":str(folder/"compose-job.json"),"project":str(folder/"render-project.json"),
            "duration":timing["duration"],"version":digest([project,timing["model_sha256"]]),
            "provenance":provenance,"fiction":script["fiction"],"audio_routing":"Single synthesized narration track; footage and chat-frame audio muted."}
    write_json(folder/"director.json",result)
    return result
