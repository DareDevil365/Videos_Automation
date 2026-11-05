"""Execute the validated director plan with actual assets and small local blocks."""
from pathlib import Path
import math
import subprocess

from PIL import Image,ImageDraw,ImageOps
from shorts_editor.graphics import text_box
from shorts_editor.store import write_json
from .assets import asset_record,register_asset
from .core import Held,digest,file_hash
from .media_agent import acquire_visual
from .transcripts import write_srt
from .cast_body import draw_human_body,shirt_color,resolve_wardrobes
from .scene_direction import narrator,compose_scene,validate_direction,check_stock_reuse,locate_callout,draw_callout,callout_animation_state


def resolve_asset(ws,ref,query,cache,kind='image',*,context=None):
    if ref:return asset_record(ws,ref)
    key=(query,kind,digest(context) if context else None)
    if key not in cache:cache[key]=acquire_visual(ws,query,kind,context=context) if context else acquire_visual(ws,query,kind)
    return cache[key]


def crop_character_head(ws,asset,actor,folder,provider=None):
    from .writer import Gemini
    provider=provider or Gemini(ws)
    schema={'type':'object','properties':{'visible':{'type':'boolean'},'box_yxyx':{'type':'array','minItems':4,'maxItems':4,
        'items':{'type':'number','minimum':0,'maximum':1000}}},'required':['visible','box_yxyx'],'additionalProperties':False}
    prompt={'avatar_kind':actor['avatar_kind'],'coordinate_order':'[y_min,x_min,y_max,x_max], normalized 0..1000 on the FIRST original image',
        'task':'Locate ONE complete, preferably upright/front-facing head of the requested kind. Include hair/ears and chin, with visible eyes/nose/mouth; exclude all other people/faces and large body/background areas. The crop will become a single character head, not a group collage. Return visible=false if no suitable complete head is visible.'}
    verdict_schema={'type':'object','properties':{'passes':{'type':'boolean'},'reason':{'type':'string','minLength':1,'maxLength':500}},'required':['passes','reason'],'additionalProperties':False}
    output=Path(folder)/('avatar-'+digest([actor['id'],asset['sha256']])[:16]+'.png')
    images=[Path(asset['path'])]
    for attempt in range(2):
        region=provider.generate('avatar-head-box-v1' if attempt==0 else 'avatar-head-box-repair-v1',prompt,schema,images=images)
        values=region.get('box_yxyx') if isinstance(region,dict) else None
        if (not isinstance(region,dict) or region.get('visible') is not True or not isinstance(values,list) or len(values)!=4
            or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1000 for v in values)
            or values[2]<=values[0] or values[3]<=values[1]):
            raise Held('cast_face_crop','A complete individual head could not be located in the source.')
        normalized=[values[1]/1000,values[0]/1000,values[3]/1000,values[2]/1000]
        with Image.open(asset['path']) as raw:
            source=ImageOps.exif_transpose(raw).convert('RGB')
            box=tuple(round(v*(source.width if i%2==0 else source.height)) for i,v in enumerate(normalized))
            if min(box[2]-box[0],box[3]-box[1])<40:raise Held('cast_face_crop','The selected head is too small; select a clearer individual portrait.')
            source.crop(box).save(output)
        review=provider.generate('avatar-head-pixels-v1',{'avatar_kind':actor['avatar_kind'],
            'task':'Inspect this actual CROPPED image. Pass only if it contains ONE usable complete head of the requested kind, with face/eyes/nose/mouth visible and enough hair/ears/chin. Reject hair-only, cut-off/incomplete faces, multiple people, or a large scene/body crop. This is a character head, not a whole-scene illustration.'},verdict_schema,images=[output])
        if not isinstance(review,dict) or type(review.get('passes')) is not bool or not isinstance(review.get('reason'),str) or not 1<=len(review['reason'])<=500:
            raise Held('cast_face_crop','The actual cropped-head review was malformed.')
        if review['passes']:
            return {'path':str(output)}, {'file':str(output),'source_asset_id':asset['id'],'source_sha256':asset['sha256'],
                'box':normalized,'sha256':file_hash(output),'review':review,'repairs':attempt}
        prompt={**prompt,'failed_crop_box_yxyx':values,'critique':review['reason'],
            'repair':'Image 1 is the ORIGINAL. Image 2 is the rejected crop. Correct the coordinates on Image 1; choose a different complete upright face if necessary. Do not reuse the rejected crop.'}
        images=[Path(asset['path']),output]
    raise Held('cast_face_crop','The character-head crop still failed after one correction; choose a suitable individual portrait.')


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
        wardrobe=actor.get('_wardrobe')
        if wardrobe:
            draw_human_body(picture,x*aa,y*aa,size*aa,wardrobe['shirt'],style=wardrobe['style'],
                pose=scene.get('pose','neutral') if actor_id==scene['speaker_id'] else 'neutral',pants_color=wardrobe['pants'])
        else:draw_human_body(picture,x*aa,y*aa,size*aa,shirt_color(actor))
        with Image.open(avatar['path']) as raw:head=ImageOps.fit(raw.convert('RGB'),(size*aa,size*aa),centering=(.5,.35))
        mask=Image.new('L',(size*aa,size*aa));ImageDraw.Draw(mask).ellipse((0,0,size*aa-1,size*aa-1),fill=255)
        picture.paste(head,(x*aa,y*aa),mask)
        text_box(d,actor['speaker'],box((max(15,x-10),y-52,min(690,size+20),42)),'white',27*aa,True,'center',minimum=20*aa)
    d=ImageDraw.Draw(picture)
    d.rounded_rectangle(box((25,height-180,695,height-30)),radius=14*aa,fill='#080c12')
    text_box(d,caption,box((48,height-155,624,98)),'white',35*aa,True,'center',minimum=23*aa)
    picture.resize((720,height),Image.Resampling.LANCZOS).save(path)


def stock_closeup(ws,asset,scene,unit,provider=None):
    if scene.get('framing')!='closeup':return None
    from .writer import Gemini
    schema={'type':'object','properties':{'box':{'type':'array','minItems':4,'maxItems':4,
        'items':{'type':'number','minimum':0,'maximum':1}},'subject':{'type':'string','minLength':1,'maxLength':180}},
        'required':['box','subject'],'additionalProperties':False}
    result=(provider or Gemini(ws)).generate('stock-closeup-v1',{'query':scene['visual_query'],'narration':unit['text'],
        'task':'Choose a tight closeup crop on an ACTUALLY VISIBLE relevant subject in this source image. Return normalized [left,top,right,bottom] coordinates and the visible subject. Use the full image only if it is already a tight closeup. For a room containing monitors, focus the relevant visible monitor area rather than retaining the wide room. For a portrait, keep the relevant painted face intact. The narration is original fiction: do not invent extra screen content or pretend the image proves an imagined event. No new objects, fabricated pixels or source changes; this only selects an actual crop. Keep at least 8% of each original dimension.'},schema,images=[Path(asset['path'])])
    box=result.get('box') if isinstance(result,dict) else None
    if (not isinstance(box,list) or len(box)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in box)
        or box[2]-box[0]<.08 or box[3]-box[1]<.08 or not isinstance(result.get('subject'),str) or not 1<=len(result['subject'].strip())<=180):
        raise Held('stock_framing','Stock closeup needs a valid visible-subject crop within the source bounds.')
    return result


def _stock_frame(asset,caption,path,rank=None,height=1280,crop=None,callout=None,animate_callout=False):
    with Image.open(asset['path']) as raw:
        source=ImageOps.exif_transpose(raw).convert('RGB');source_size=source.size
        if crop:
            left,top,right,bottom=crop['box']
            source=source.crop((round(left*source.width),round(top*source.height),round(right*source.width),round(bottom*source.height)))
        picture=ImageOps.fit(source,(720,height))
    annotation=draw_callout(picture.copy() if animate_callout else picture,source_size,callout,crop)
    if annotation and animate_callout:
        annotation['render_input']={'source_size':source_size,'callout':callout,'crop':crop}
    d=ImageDraw.Draw(picture)
    d.rounded_rectangle((26,height-190,694,height-30),radius=14,fill='#0b0c12')
    text_box(d,caption,(48,height-163,624,105),'white',38,True,'center',minimum=25)
    if rank is not None:
        d.rounded_rectangle((28,35,145,135),radius=15,fill='#0b0c12')
        text_box(d,str(rank),(37,48,100,73),'white',50,True,'center')
    picture.save(path)
    return annotation


def _camera_filter(duration,motion,height,repeat):
    frames=math.ceil(duration*30)
    zoom="1" if motion=='hold' else "1+0.05*max(0,1-abs((on/30-0.20)/0.18))" if motion=='punch' else 'min(1+on*0.00035,1.07)'
    x='iw/2-iw/zoom/2'
    if motion=='pan_left':zoom='1.06';x=f'(iw-iw/zoom)*(1-on/{max(1,frames-1)})'
    if motion=='pan_right':zoom='1.06';x=f'(iw-iw/zoom)*on/{max(1,frames-1)}'
    return f"scale=1440:{height*2},zoompan=z='{zoom}':x='{x}':y='ih/2-ih/zoom/2':d={frames if repeat else 1}:s=720x{height}:fps=30"


def _motion(poster,duration,path,motion,height=1280,*,callout=None):
    if callout:
        with Image.open(poster) as raw:base=raw.convert('RGB')
        frames=math.ceil(duration*30)
        vf=_camera_filter(duration,motion,height,False)
        process=subprocess.Popen(['ffmpeg','-v','error','-nostdin','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'720x{height}',
            '-framerate','30','-i','pipe:0','-vf',vf,'-t',str(duration),'-an','-c:v','libx264','-preset','veryfast','-crf','20',
            '-threads','2','-pix_fmt','yuv420p',str(path)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            for index in range(frames):
                picture=base.copy()
                draw_callout(picture,**callout,**callout_animation_state(index/30,duration))
                process.stdin.write(picture.tobytes())
            process.stdin.close();process.stdin=None
            _,error=process.communicate(timeout=120)
            if process.returncode:raise Held('planned_visual_render','Animated callout rendering failed; source assets and poster were preserved.')
        except BaseException:
            if process.poll() is None:process.kill();process.communicate()
            raise
        return
    vf=_camera_filter(duration,motion,height,True)
    result=subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-i',str(poster),'-vf',vf,'-t',str(duration),'-an','-c:v','libx264',
       '-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p',str(path)],capture_output=True,timeout=120)
    if result.returncode:raise Held('planned_visual_render','A directed scene failed; its source assets and poster were preserved')


def _video_scene(asset,caption,duration,path,height,offset=0,rank=None,motion='hold',minimal=False):
    plate=Image.new('RGBA',(720,height));draw=ImageDraw.Draw(plate)
    if minimal:
        for y in range(height-280,height):draw.line((0,y,720,y),fill=(0,0,0,round((y-height+280)*.5)))
    else:draw.rounded_rectangle((26,height-190,694,height-30),radius=14,fill='#0b0c12ee')
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


def build_planned_visuals(ws,job,script,timing,folder,record,*,provider=None):
    if record.get('plan',{}).get('template')=='source_brief':
        from .brief_visuals import build_brief_visuals
        return build_brief_visuals(ws,job,script,timing,folder,record)
    if record.get('plan',{}).get('template')=='comic_lore':
        from .lore_visuals import build_lore_visuals
        return build_lore_visuals(ws,job,script,timing,folder,record)
    if record.get('plan',{}).get('template')=='server_chat_v2':
        from .chat_editing import build_chat_visuals
        return build_chat_visuals(ws,job,script,timing,folder,record)
    if record.get('plan',{}).get('template')=='illustrated_story':
        from .illustrated_story import build_story_visuals
        return build_story_visuals(ws,job,script,timing,folder,record)
    if record.get('plan',{}).get('template')=='documentary':
        from .documentary_graphics import build_chapter_visuals
        return build_chapter_visuals(ws,job,script,timing,folder,record)
    plan=record['plan'];folder=Path(folder);folder.mkdir(exist_ok=True)
    if record['script_sha256']!=digest(script):raise Held('creative_rewrite','Edit plan belongs to a different script version')
    template=plan['template'];cache={};provenance={};cast={r['id']:r for r in plan['cast']};avatars={}
    scene_mode=job['request'].get('scene_direction_version',1)==2
    if scene_mode:validate_direction(plan,script,job['request'])
    seen_stock={};reuse_log=[];wardrobes={};avatar_crops={}
    if job['request'].get('bottom_asset_id') and job['request'].get('bottom_kind','none')=='none':
        raise Held('creative_layout','A lower-panel asset requires an explicit allowed lower-panel kind')
    fraction=job['request'].get('top_fraction',.65)
    if isinstance(fraction,bool) or not isinstance(fraction,(int,float)) or not math.isfinite(fraction) or not .35<=fraction<=.75:
        raise Held('creative_layout','Top panel fraction must be between .35 and .75')
    height=round(1280*fraction/2)*2 if job['request'].get('bottom_asset_id') else 1280
    if template=='cutout_cast':
        for actor in plan['cast']:
            if actor['avatar_kind']=='narrator':continue
            if scene_mode and narrator(actor) and not job['request'].get('show_narrator',False):continue
            bindings=job['request'].get('cast_assets',{})
            ref=bindings.get(actor['id']) or bindings.get(actor['speaker'])
            avatar=resolve_asset(ws,ref,actor['avatar_query'],cache)
            if avatar['kind']!='image':raise Held('cast_asset','Cast heads require actual usable image files')
            provenance[avatar['id']]=avatar
            if scene_mode:avatars[actor['id']],avatar_crops[actor['id']]=crop_character_head(ws,avatar,actor,folder,provider)
            else:avatars[actor['id']]=avatar
        if scene_mode:
            wardrobes=resolve_wardrobes([a for a in plan['cast'] if a['id'] in avatars])
            cast={ref:{**actor,'_wardrobe':wardrobes.get(ref)} for ref,actor in cast.items()}
    rows=[];bindings=[];units={u['id']:u for u in script['units']}
    if [s['unit_id'] for s in plan['scenes']]!=[u['id'] for u in timing['units']]:raise Held('creative_units','Director and measured voice must cover the same ordered units')
    for i,(scene,spoken) in enumerate(zip(plan['scenes'],timing['units'])):
        if template=='cutout_cast':
            from .creative_plan import active_speaker_scene
            scene=compose_scene(scene,plan['cast'],job['request'].get('show_narrator',False)) if scene_mode else active_speaker_scene(scene,plan['cast'])
        if scene['unit_id']!=spoken['id']:raise Held('creative_units','Edit scene and measured speech IDs differ')
        unit=units[spoken['id']]
        graphic=scene.get('graphic',{'kind':'none','title':'','labels':[]})
        if template=='server_chat':
            from .server_chat import render_server_message
            if job['request'].get('bottom_asset_id'):raise Held('chat_layout','Server chat requires a full-frame layout.')
            if unit['onscreen']!=unit['text']:raise Held('creative_rewrite','Server-chat messages must display their full exact text.')
            output=folder/(unit['id']+'-server.mp4')
            detail=render_server_message(script,i,spoken['duration'],output,height)
            generated=register_asset(ws,output,'original_graphic',{'generator':'original server chat with actual message entry/scroll','unit_id':unit['id'],
                'visible_unit_ids':detail['visible_unit_ids']},test_only=job['request'].get('test_only',False))
            rows.append({'unit_id':unit['id'],'file':str(output),'media_id':generated['id'],'duration':spoken['duration'],
                'kind':'directed_server_chat','message_state':detail})
            continue
        if graphic['kind']!='none':
            from .scene_blocks import validate_block,render_block
            validate_block(graphic,unit,script)
            if template!='education_demo' or job['request'].get('motion_graphics') is not True:
                raise Held('scene_block_disabled','Motion graphics require an explicitly enabled education demonstration request.')
            output=folder/(unit['id']+'-graphic.mp4')
            detail=render_block(graphic,spoken['duration'],output,height=height,
                                speech_duration=spoken.get('metrics',{}).get('duration',spoken.get('speech_end',0)-spoken.get('start',0)),
                                thinking_seconds=spoken.get('thinking_seconds',0))
            detail['label_sources']=[{'label':label,'unit_ids':[u['id'] for u in script['units'] if label.casefold() in (u['text']+' '+u['onscreen']).casefold()]} for label in graphic['labels']]
            generated=register_asset(ws,output,'original_graphic',{'operation':'Trusted local typography block','unit_id':unit['id'],'block':graphic},test_only=job['request'].get('test_only',False))
            rows.append({'unit_id':unit['id'],'file':str(output),'media_id':generated['id'],'duration':spoken['duration'],
                         'kind':'directed_graphic','resolved_scene':scene,'graphic':detail})
            continue
        if template=='chat_asmr':
            from .visuals import chat_frame
            chat_script={**script,'units':[{**u,'onscreen':u['text']} for u in script['units']],
                         'show_speakers':True,'chat_title':'','chat_history':2}
            chat_path=folder/(unit['id']+'-chat.png');chat_frame(chat_script,i,chat_path)
            with Image.open(chat_path) as raw:card=ImageOps.contain(raw.convert('RGB'),(720,height-30))
            poster=folder/(unit['id']+'-planned.png');canvas=Image.new('RGB',(720,height),'#101014');canvas.paste(card,((720-card.width)//2,15));canvas.save(poster)
            output=folder/(unit['id']+'-planned.mp4');_motion(poster,spoken['duration'],output,'hold',height)
            generated=register_asset(ws,output,'original_graphic',{'generator':'timed fictional chat state','unit_id':unit['id']},test_only=job['request'].get('test_only',False))
            rows.append({'unit_id':unit['id'],'file':str(output),'media_id':generated['id'],'duration':spoken['duration'],'kind':'directed_chat'})
            continue
        insert=template=='cutout_cast' and scene.get('shot_type')=='insert'
        stock_scene=template!='cutout_cast' or insert
        supplied=job['request'].get('media_assets',{}).get(unit['id']) or scene['asset_id']
        if template=='cutout_cast' and not insert and not supplied:supplied=job['request'].get('default_background_id')
        query=job['request'].get('media_queries',{}).get(unit['id']) or (scene['visual_query'] if stock_scene else scene['background_query'])
        if supplied and str(supplied).startswith('generation:'):
            from .browser_agent import read_generation
            made=read_generation(ws,supplied.partition(':')[2]);supplied=made.get('asset_id')
            if not supplied:raise Held('generated_media_pending','Waiting for the directed generated asset',retry_after=60)
        essential=template in ('education_demo','movie_cards')
        if essential and not supplied:raise Held('essential_visual_missing','Education demonstrations and named movie cards need matching registered inputs; generic first-result stock is not a substitute')
        approvals=job['request'].get('visual_approvals',{})
        if essential and not job['request'].get('test_only',False) and approvals.get(unit['id'])!=supplied:
            raise Held('essential_visual_unreviewed','This factual visual needs a recorded unit-to-asset match before non-test production')
        context={'role':'location backdrop for static fictional cast'} if not stock_scene else {
            'title':script['title'],'narration':unit['text'],
            'previous_line':script['units'][max(0,i-1)]['text'],'next_line':script['units'][min(len(script['units'])-1,i+1)]['text']}
        background=resolve_asset(ws,supplied,query,cache,'image' if not stock_scene else unit.get('visual_kind','image'),context=context);provenance[background['id']]=background
        reuse=check_stock_reuse(seen_stock,background['sha256'],scene,i) if scene_mode and stock_scene else None
        if reuse:reuse_log.append({'unit_id':unit['id'],'source_sha256':background['sha256'],**reuse})
        bindings.append({'unit_id':unit['id'],'asset_id':background['id'],'query':query,
                         'text':unit['text'] if stock_scene else '',
                         'role':'literal animal/object/action illustration' if insert else 'location backdrop for static fictional cast' if not stock_scene else 'literal illustration of narration',
                         'reuse':reuse,
                         'offset':job['request'].get('media_starts',{}).get(unit['id'],0),
                         'duration':spoken['duration'] if background['kind']=='video' else 0})
        if background['kind']!='image':
            if not stock_scene:raise Held('cast_background','Current cast renderer requires a still background, not an unsupported video layer')
            if scene.get('callout',{}).get('kind','none')!='none':raise Held('creative_callout','A moving-video callout needs tracking; select a still image for this detail.')
            output=folder/(unit['id']+'-planned.mp4')
            _video_scene(background,unit['onscreen'],spoken['duration'],output,height,job['request'].get('media_starts',{}).get(unit['id'],0),scene.get('rank') or None,scene['motion'],minimal=bool(job['request'].get('aura_clean')))
            generated=register_asset(ws,output,'original_graphic',{'operation':'Directed source clip and caption','sources':[background['id']]},test_only=job['request'].get('test_only',False) or background.get('test_only',False))
            rows.append({'unit_id':unit['id'],'media_id':generated['id'],'duration':spoken['duration'],'file':str(output),'kind':'directed_stock_video'})
            continue
        poster=folder/(unit['id']+'-planned.png')
        crop=None;annotation=None
        if not stock_scene:_cast_frame(background,cast,avatars,scene,'' if timing.get('caption_style')=='dialogue_bar' else unit['text'],poster,height)
        else:
            crop=stock_closeup(ws,background,scene,unit,provider=provider)
            callout=locate_callout(ws,background,scene.get('callout',{'kind':'none'}),provider=provider)
            caption=('' if timing.get('caption_style')=='dialogue_bar' else unit['text']) if insert else unit['onscreen']
            annotation=_stock_frame(background,caption,poster,scene.get('rank') or None,height,crop=crop,callout=callout,animate_callout=True)
        output=folder/(unit['id']+'-planned.mp4');_motion(poster,spoken['duration'],output,scene['motion'],height,
            callout=annotation['render_input'] if annotation else None)
        generated=register_asset(ws,output,'original_graphic',{'operation':'Validated director-plan collage/stock crop; source licenses retained separately','sources':list(provenance),'scene':scene},test_only=job['request'].get('test_only',False))
        rows.append({'unit_id':unit['id'],'file':str(output),'media_id':generated['id'],'duration':spoken['duration'],'kind':'directed_'+template,'resolved_scene':scene})
        if crop:rows[-1]['source_crop']=crop
        if annotation:rows[-1]['source_callout']=annotation
    captions=folder/'captions.srt'
    write_srt([{'start':u['start'],'end':u['speech_end'],'text':u['text']} for u in timing['units']],captions)
    result={'version':1,'format':script['format'],'frames':rows,'captions':str(captions),'selected_media':[],
            'planned_template':template,'planned_provenance':list(provenance.values()),'creative_plan_sha256':digest(plan),'source_bindings':bindings,
            'wardrobes':wardrobes,'avatar_crops':avatar_crops,'stock_reuse':reuse_log,'scene_direction_version':2 if scene_mode else 1}
    write_json(folder/'visuals.json',result);return result
