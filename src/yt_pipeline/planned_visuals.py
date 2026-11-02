"""Execute the validated director plan with actual assets and small local blocks."""
from pathlib import Path
import math
import subprocess

from PIL import Image,ImageDraw,ImageOps
from shorts_editor.graphics import text_box
from shorts_editor.store import write_json
from .assets import asset_record,register_asset
from .core import Held,digest
from .media_agent import acquire_visual
from .transcripts import write_srt
from .cast_body import draw_human_body,shirt_color


def resolve_asset(ws,ref,query,cache,kind='image'):
    if ref:return asset_record(ws,ref)
    key=(query,kind)
    if key not in cache:cache[key]=acquire_visual(ws,query,kind)
    return cache[key]


def _cast_frame(background,cast,avatars,scene,caption,path,height=1280):
    """Photo heads on reusable human silhouettes; no rig/lip sync."""
    aa=3
    def box(values):return tuple(round(v*aa) for v in values)
    with Image.open(background['path']) as raw:picture=ImageOps.fit(raw.convert('RGB'),(720*aa,height*aa))
    picture=Image.blend(picture,Image.new('RGB',picture.size,'#101018'),.20)
    visible=scene['visible_cast']
    if scene['framing']=='closeup':visible=[scene['focus_id']]
    for i,actor_id in enumerate(visible):
        actor=cast[actor_id];avatar=avatars.get(actor_id)
        if not avatar:continue
        close=scene['framing']=='closeup';medium=scene['framing']=='medium'
        size=min(510,int(height*.40)) if close else min(250 if medium else 180,600//max(1,len(visible)),int((height-310)/4) if not medium else 250)
        x=(720-size)//2 if close else int(40+(i+.5)*640/len(visible)-size/2)
        y=int(height*.16) if close else int(height*.25) if medium else round(height-205-size*4)
        d=ImageDraw.Draw(picture)
        draw_human_body(picture,x*aa,y*aa,size*aa,shirt_color(actor))
        with Image.open(avatar['path']) as raw:head=ImageOps.fit(raw.convert('RGB'),(size*aa,size*aa),centering=(.5,.35))
        mask=Image.new('L',(size*aa,size*aa));ImageDraw.Draw(mask).ellipse((0,0,size*aa-1,size*aa-1),fill=255)
        picture.paste(head,(x*aa,y*aa),mask)
        text_box(d,actor['speaker'],box((max(15,x-10),y-52,min(690,size+20),42)),'white',27*aa,True,'center',minimum=20*aa)
    d=ImageDraw.Draw(picture)
    d.rounded_rectangle(box((25,height-180,695,height-30)),radius=14*aa,fill='#080c12')
    text_box(d,caption,box((48,height-155,624,98)),'white',35*aa,True,'center',minimum=23*aa)
    text_box(d,'ORIGINAL FICTION',box((32,30,656,30)),'#dddddd',18*aa,True)
    picture.resize((720,height),Image.Resampling.LANCZOS).save(path)


def _stock_frame(asset,caption,path,rank=None,height=1280):
    with Image.open(asset['path']) as raw:picture=ImageOps.fit(raw.convert('RGB'),(720,height))
    d=ImageDraw.Draw(picture)
    d.rounded_rectangle((26,height-190,694,height-30),radius=14,fill='#0b0c12')
    text_box(d,caption,(48,height-163,624,105),'white',38,True,'center',minimum=25)
    if rank is not None:
        d.rounded_rectangle((28,35,145,135),radius=15,fill='#0b0c12')
        text_box(d,str(rank),(37,48,100,73),'white',50,True,'center')
    picture.save(path)


def _camera_filter(duration,motion,height,repeat):
    frames=math.ceil(duration*30)
    zoom="1" if motion=='hold' else "1+0.05*max(0,1-abs((on/30-0.20)/0.18))" if motion=='punch' else 'min(1+on*0.00035,1.07)'
    x='iw/2-iw/zoom/2'
    if motion=='pan_left':zoom='1.06';x=f'(iw-iw/zoom)*(1-on/{max(1,frames-1)})'
    if motion=='pan_right':zoom='1.06';x=f'(iw-iw/zoom)*on/{max(1,frames-1)}'
    return f"scale=1440:{height*2},zoompan=z='{zoom}':x='{x}':y='ih/2-ih/zoom/2':d={frames if repeat else 1}:s=720x{height}:fps=30"


def _motion(poster,duration,path,motion,height=1280):
    vf=_camera_filter(duration,motion,height,True)
    result=subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-i',str(poster),'-vf',vf,'-t',str(duration),'-an','-c:v','libx264',
       '-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p',str(path)],capture_output=True,timeout=120)
    if result.returncode:raise Held('planned_visual_render','A directed scene failed; its source assets and poster were preserved')


def _video_scene(asset,caption,duration,path,height,offset=0,rank=None,motion='hold'):
    plate=Image.new('RGBA',(720,height));draw=ImageDraw.Draw(plate)
    draw.rounded_rectangle((26,height-190,694,height-30),radius=14,fill='#0b0c12ee')
    text_box(draw,caption,(48,height-163,624,105),'white',38,True,'center',minimum=25)
    if rank:
        draw.rounded_rectangle((28,35,145,135),radius=15,fill='#0b0c12')
        text_box(draw,str(rank),(37,48,100,73),'white',50,True,'center')
    overlay=path.with_suffix('.caption.png');plate.save(overlay)
    camera=_camera_filter(duration,motion,height,False)
    filters=f'[0:v]scale=720:{height}:force_original_aspect_ratio=increase,crop=720:{height},setsar=1,fps=30,setpts=PTS-STARTPTS,{camera}[v];[v][1:v]overlay=0:0:shortest=1[out]'
    result=subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-stream_loop','-1','-ss',str(offset%asset['duration']),'-i',asset['path'],
        '-loop','1','-framerate','30','-i',str(overlay),'-filter_complex_threads','1','-filter_complex',filters,'-map','[out]','-t',str(duration),
        '-an','-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p',str(path)],capture_output=True,timeout=120)
    if result.returncode:raise Held('planned_visual_render','Directed source clip/caption preparation failed')


def build_planned_visuals(ws,job,script,timing,folder,record):
    plan=record['plan'];folder=Path(folder);folder.mkdir(exist_ok=True)
    if record['script_sha256']!=digest(script):raise Held('creative_rewrite','Edit plan belongs to a different script version')
    template=plan['template'];cache={};provenance={};cast={r['id']:r for r in plan['cast']};avatars={}
    if job['request'].get('bottom_asset_id') and job['request'].get('bottom_kind','none')=='none':
        raise Held('creative_layout','A lower-panel asset requires an explicit allowed lower-panel kind')
    fraction=job['request'].get('top_fraction',.65)
    if isinstance(fraction,bool) or not isinstance(fraction,(int,float)) or not math.isfinite(fraction) or not .35<=fraction<=.75:
        raise Held('creative_layout','Top panel fraction must be between .35 and .75')
    height=round(1280*fraction/2)*2 if job['request'].get('bottom_asset_id') else 1280
    if template=='cutout_cast':
        for actor in plan['cast']:
            if actor['avatar_kind']=='narrator':continue
            bindings=job['request'].get('cast_assets',{})
            ref=bindings.get(actor['id']) or bindings.get(actor['speaker'])
            avatar=resolve_asset(ws,ref,actor['avatar_query'],cache)
            if avatar['kind']!='image':raise Held('cast_asset','Cast heads require actual usable image files')
            avatars[actor['id']]=avatar;provenance[avatar['id']]=avatar
    rows=[];bindings=[];units={u['id']:u for u in script['units']}
    if [s['unit_id'] for s in plan['scenes']]!=[u['id'] for u in timing['units']]:raise Held('creative_units','Director and measured voice must cover the same ordered units')
    for i,(scene,spoken) in enumerate(zip(plan['scenes'],timing['units'])):
        if template=='cutout_cast':
            from .creative_plan import active_speaker_scene
            scene=active_speaker_scene(scene,plan['cast'])
        if scene['unit_id']!=spoken['id']:raise Held('creative_units','Edit scene and measured speech IDs differ')
        unit=units[spoken['id']]
        graphic=scene.get('graphic',{'kind':'none','title':'','labels':[]})
        if graphic['kind']!='none':
            from .scene_blocks import validate_block,render_block
            validate_block(graphic,unit,script)
            if template!='education_demo' or job['request'].get('motion_graphics') is not True:
                raise Held('scene_block_disabled','Motion graphics require an explicitly enabled education demonstration request.')
            output=folder/(unit['id']+'-graphic.mp4')
            detail=render_block(graphic,spoken['duration'],output,height=height)
            detail['label_sources']=[{'label':label,'unit_ids':[u['id'] for u in script['units'] if label.casefold() in (u['text']+' '+u['onscreen']).casefold()]} for label in graphic['labels']]
            generated=register_asset(ws,output,'original_graphic',{'operation':'Trusted local typography block','unit_id':unit['id'],'block':graphic},test_only=job['request'].get('test_only',False))
            rows.append({'unit_id':unit['id'],'file':str(output),'media_id':generated['id'],'duration':spoken['duration'],
                         'kind':'directed_graphic','resolved_scene':scene,'graphic':detail})
            continue
        if template=='chat_asmr':
            from .visuals import chat_frame
            chat_script={**script,'units':[{**u,'onscreen':u['text']} for u in script['units']],
                         'show_speakers':True,'chat_title':'Fictional group chat','chat_history':2}
            chat_path=folder/(unit['id']+'-chat.png');chat_frame(chat_script,i,chat_path)
            with Image.open(chat_path) as raw:card=ImageOps.contain(raw.convert('RGB'),(720,height-30))
            poster=folder/(unit['id']+'-planned.png');canvas=Image.new('RGB',(720,height),'#101014');canvas.paste(card,((720-card.width)//2,15));canvas.save(poster)
            output=folder/(unit['id']+'-planned.mp4');_motion(poster,spoken['duration'],output,'hold',height)
            generated=register_asset(ws,output,'original_graphic',{'generator':'timed fictional chat state','unit_id':unit['id']},test_only=job['request'].get('test_only',False))
            rows.append({'unit_id':unit['id'],'file':str(output),'media_id':generated['id'],'duration':spoken['duration'],'kind':'directed_chat'})
            continue
        supplied=job['request'].get('media_assets',{}).get(unit['id']) or scene['asset_id']
        if template=='cutout_cast' and not supplied:supplied=job['request'].get('default_background_id')
        query=job['request'].get('media_queries',{}).get(unit['id']) or (scene['background_query'] if template=='cutout_cast' else scene['visual_query'])
        if supplied and str(supplied).startswith('generation:'):
            from .browser_agent import read_generation
            made=read_generation(ws,supplied.partition(':')[2]);supplied=made.get('asset_id')
            if not supplied:raise Held('generated_media_pending','Waiting for the directed generated asset',retry_after=60)
        essential=template in ('education_demo','movie_cards')
        if essential and not supplied:raise Held('essential_visual_missing','Education demonstrations and named movie cards need matching registered inputs; generic first-result stock is not a substitute')
        approvals=job['request'].get('visual_approvals',{})
        if essential and not job['request'].get('test_only',False) and approvals.get(unit['id'])!=supplied:
            raise Held('essential_visual_unreviewed','This factual visual needs a recorded unit-to-asset match before non-test production')
        background=resolve_asset(ws,supplied,query,cache,'image' if template=='cutout_cast' else unit.get('visual_kind','image'));provenance[background['id']]=background
        bindings.append({'unit_id':unit['id'],'asset_id':background['id'],'query':query,
                         'text':unit['text'] if template!='cutout_cast' else '',
                         'role':'location backdrop for static fictional cast' if template=='cutout_cast' else 'literal illustration of narration',
                         'offset':job['request'].get('media_starts',{}).get(unit['id'],0),
                         'duration':spoken['duration'] if background['kind']=='video' else 0})
        if background['kind']!='image':
            if template=='cutout_cast':raise Held('cast_background','Current cast renderer requires a still background, not an unsupported video layer')
            output=folder/(unit['id']+'-planned.mp4')
            _video_scene(background,unit['onscreen'],spoken['duration'],output,height,job['request'].get('media_starts',{}).get(unit['id'],0),scene.get('rank') or None,scene['motion'])
            generated=register_asset(ws,output,'original_graphic',{'operation':'Directed source clip and caption','sources':[background['id']]},test_only=job['request'].get('test_only',False) or background.get('test_only',False))
            rows.append({'unit_id':unit['id'],'media_id':generated['id'],'duration':spoken['duration'],'file':str(output),'kind':'directed_stock_video'})
            continue
        poster=folder/(unit['id']+'-planned.png')
        if template=='cutout_cast':_cast_frame(background,cast,avatars,scene,'' if timing.get('caption_style')=='dialogue_bar' else unit['text'],poster,height)
        else:_stock_frame(background,unit['onscreen'],poster,scene.get('rank') or None,height)
        output=folder/(unit['id']+'-planned.mp4');_motion(poster,spoken['duration'],output,scene['motion'],height)
        generated=register_asset(ws,output,'original_graphic',{'operation':'Validated director-plan collage/stock crop; source licenses retained separately','sources':list(provenance),'scene':scene},test_only=job['request'].get('test_only',False))
        rows.append({'unit_id':unit['id'],'file':str(output),'media_id':generated['id'],'duration':spoken['duration'],'kind':'directed_'+template,'resolved_scene':scene})
    captions=folder/'captions.srt'
    write_srt([{'start':u['start'],'end':u['speech_end'],'text':u['text']} for u in timing['units']],captions)
    result={'version':1,'format':script['format'],'frames':rows,'captions':str(captions),'selected_media':[],
            'planned_template':template,'planned_provenance':list(provenance.values()),'creative_plan_sha256':digest(plan),'source_bindings':bindings}
    write_json(folder/'visuals.json',result);return result
