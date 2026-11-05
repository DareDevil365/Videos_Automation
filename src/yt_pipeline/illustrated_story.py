"""Measured portrait/landscape illustration shots; source motion and overlays are explicit."""
import math
from pathlib import Path
import random
import subprocess

from PIL import Image,ImageDraw,ImageOps
from shorts_editor.store import write_json
from .assets import asset_record,register_asset
from .core import Held,digest
from .scene_direction import callout_animation_state,draw_callout
from .transcripts import write_srt


def normalized_box(value,name):
    if not isinstance(value,list) or len(value)!=4 or any(type(v) not in (float,int) or not math.isfinite(v) for v in value):
        raise Held('story_effect',name+' needs four finite normalized coordinates.')
    x1,y1,x2,y2=value
    if not 0<=x1<x2<=1 or not 0<=y1<y2<=1 or x2-x1<.005 or y2-y1<.005:
        raise Held('story_effect',name+' is outside the source image or too small.')
    return value


def story_frame(source,scene,second,duration,effects=None,canvas=(1280,720)):
    effects=effects or {};progress=max(0,min(1,second/duration));sw,sh=source.size
    first=normalized_box(effects.get('crop_start',[0,0,1,1]),'crop_start')
    last=normalized_box(effects.get('crop_end',[.035,.035,.965,.965]),'crop_end')
    crop=[a+(b-a)*progress for a,b in zip(first,last)]
    raw=source.copy()
    if effects.get('flash_box'):
        box=normalized_box(effects['flash_box'],'flash_box');layer=Image.new('RGBA',raw.size);ld=ImageDraw.Draw(layer)
        phase=second%2.1
        # Irregular visible pulses are fictional lamp motion, not an SOS claim.
        on=any(a<=phase<b for a,b in ((0,.16),(.32,.48),(.64,.82),(1.25,1.45)))
        ld.rectangle(tuple(round(v*(sw if i%2==0 else sh)) for i,v in enumerate(box)),fill=(6,18,30,0 if on else 230))
        raw=Image.alpha_composite(raw.convert('RGBA'),layer).convert('RGB')
    pixels=(round(crop[0]*sw),round(crop[1]*sh),round(crop[2]*sw),round(crop[3]*sh))
    picture=ImageOps.fit(raw.crop(pixels),canvas,method=Image.Resampling.LANCZOS)
    if effects.get('callout_box'):
        box=normalized_box(effects['callout_box'],'callout_box')
        draw_callout(picture,source.size,{'box':box,'kind':'circle_arrow','target':effects.get('target','visible story clue'),'label':''},
            crop={'box':crop},**callout_animation_state(second,duration))
    overlay=Image.new('RGBA',picture.size);d=ImageDraw.Draw(overlay)
    if effects.get('rain',False):
        rng=random.Random(521)
        for _ in range(46):
            x=(rng.randrange(1450)-80-second*75)%1450-80
            y=(rng.randrange(850)+second*420)%850-100
            d.line((x,y,x-12,y+38),fill=(163,207,219,62),width=1)
    # Bottom caption contrast; it does not obscure faces/props higher in frame.
    w,h=canvas
    for y in range(round(h*.80),h):d.line((0,y,w,y),fill=(3,10,18,round(185*(y-h*.80)/(h*.20))))
    return Image.alpha_composite(picture.convert('RGBA'),overlay).convert('RGB')


def render_story_shot(source,scene,duration,path,effects=None,canvas=(1280,720),inset=None):
    if not math.isfinite(duration) or not 1<=duration<=60:raise Held('story_timing','Story shots need measured 1-60 second durations.')
    path=Path(path);partial=path.with_suffix('.partial.mp4');log=path.with_suffix('.ffmpeg.log')
    with Image.open(source) as raw:image=ImageOps.exif_transpose(raw).convert('RGB')
    if inset:
        box=normalized_box((effects or {}).get('inset_box'),'inset_box');w,h=image.size
        x1,y1,x2,y2=[round(v*(w if i%2==0 else h)) for i,v in enumerate(box)]
        with Image.open(inset) as tile:image.paste(ImageOps.fit(tile.convert('RGB'),(x2-x1,y2-y1)),(x1,y1))
    story_frame(image,scene,duration*.7,duration,effects,canvas).save(path.with_suffix('.png'))
    with log.open('wb') as errors:
        process=subprocess.Popen(['ffmpeg','-v','error','-nostdin','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{canvas[0]}x{canvas[1]}',
            '-framerate','30','-i','pipe:0','-an','-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','20',
            '-threads','2','-pix_fmt','yuv420p',str(partial)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=errors)
        try:
            for frame in range(math.ceil(duration*30)):
                process.stdin.write(story_frame(image,scene,frame/30,duration,effects,canvas).tobytes())
            process.stdin.close();process.wait(timeout=120)
            if process.returncode:raise Held('story_render','Story-shot encoding failed; inspect its retained log.')
        except BaseException:
            if process.poll() is None:process.kill();process.wait()
            if not process.stdin.closed:process.stdin.close()
            raise
    partial.replace(path)


def build_story_visuals(ws,job,script,timing,folder,record):
    plan=record['plan'];folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    if record['script_sha256']!=digest(script):raise Held('creative_rewrite','Story direction does not match the frozen script.')
    if [s['unit_id'] for s in plan['scenes']]!=[u['id'] for u in timing['units']]:
        raise Held('story_timing','The shot sequence differs from measured narration.')
    rows=[];provenance={};seen={};effects=job['request'].get('illustration_effects',{})
    if not isinstance(effects,dict) or any(k not in {u['id'] for u in script['units']} for k in effects):
        raise Held('story_effect','Effects must refer to existing story units.')
    reasons=job['request'].get('illustration_reuse',{})
    for scene,spoken in zip(plan['scenes'],timing['units']):
        asset=asset_record(ws,scene['asset_id'])
        if asset['kind']!='image' or (asset['source_type']!='original_graphic' and not (job['request'].get('allow_licensed_illustrations') and asset['source_type']=='licensed_stock')):
            raise Held('story_asset','Supply registered original story illustrations for every shot.')
        if asset['sha256'] in seen and not isinstance(reasons.get(scene['unit_id']),str):
            raise Held('story_reuse','Repeated art needs an explicit continuity/detail/payoff reason.')
        if asset['sha256'] in seen and len(reasons[scene['unit_id']].strip())<20:
            raise Held('story_reuse','Explain why this specific story illustration returns.')
        seen[asset['sha256']]=True;provenance[asset['id']]=asset
        output=folder/(scene['unit_id']+'-story.mp4')
        effect=effects.get(scene['unit_id'],{});inset=None
        if effect.get('inset_asset_id'):
            inset=asset_record(ws,effect['inset_asset_id'])
            if inset['kind']!='image':raise Held('story_asset','Story insets need registered images.')
            provenance[inset['id']]=inset
        render_story_shot(asset['path'],scene,spoken['duration'],output,effect,(720,1280) if job['request'].get('story_canvas')=='portrait' else (1280,720),inset['path'] if inset else None)
        generated=register_asset(ws,output,'original_graphic',{'generator':'illustrated-story-v1','source_id':asset['id'],
            'unit_id':scene['unit_id'],'effects':effects.get(scene['unit_id'],{}),'reuse_reason':reasons.get(scene['unit_id'])},test_only=True)
        rows.append({'unit_id':scene['unit_id'],'file':str(output),'media_id':generated['id'],'duration':spoken['duration'],
            'kind':'illustrated_story','source_asset_id':asset['id'],'resolved_scene':scene})
    captions=folder/'captions.srt';write_srt([{'start':u['start'],'end':u['speech_end'],'text':u['text']} for u in timing['units']],captions)
    result={'version':1,'format':script['format'],'frames':rows,'captions':str(captions),'planned_template':'illustrated_story',
        'planned_provenance':list(provenance.values()),'selected_media':[],'source_bindings':[],
        'creative_plan_sha256':digest(plan),'limits':['Illustrations have camera, rain and light motion; character bodies are not rigged or lip-synced.']}
    write_json(folder/'visuals.json',result);return result
