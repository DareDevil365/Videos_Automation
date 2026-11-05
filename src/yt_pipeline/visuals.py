from pathlib import Path

from PIL import Image, ImageDraw

from shorts_editor.graphics import font, wrapped, text_box
from shorts_editor.render import export_captions, srt_time
from shorts_editor.store import write_json
from .media_agent import select_visuals
from .transcripts import write_srt
from .montage import build_cuts
from .entertainment import aura_scene,cutout_scene
from .storyboard import story_specs,mystery_scene


def chat_frame(script, index, path):
    width=720;pad=24;header=108
    history=max(1,min(3,int(script.get('chat_history',3))))
    rows=script["units"][max(0,index-history+1):index+1]
    labels=bool(script.get('show_speakers'))
    names=[]
    for unit in script["units"]:
        if unit["speaker"] not in names:names.append(unit["speaker"])
    sizing=ImageDraw.Draw(Image.new("RGB",(width,1200)))
    bubbles=[];height=header+22
    for row in rows:
        lines=wrapped(sizing,row["onscreen"],font(30),560)
        bubble_height=max(68,26+len(lines)*38)+(24 if labels else 0)
        bubble_width=min(610,max(140,max((sizing.textlength(line,font=font(30)) for line in lines),default=100)+40))
        bubbles.append((row,bubble_width,bubble_height))
        height+=bubble_height+14
    height=min(1100,max(260,height+18))
    image=Image.new("RGB",(width,height),"#000000");draw=ImageDraw.Draw(image)
    draw.rectangle((0,0,width,header),fill="#22252b")
    draw.text((22,31),"‹",font=font(46),fill="#168aff")
    draw.ellipse((width/2-22,12,width/2+22,56),fill="#676b75")
    contacts=[n for n in names if n!='Narrator']
    contact=script.get('chat_title') or (contacts[1] if len(contacts)>1 else contacts[0] if contacts else 'Chat')
    text_box(draw,contact,(100,64,width-200,30),"#ffffff",24,False,"center")
    draw.rectangle((width-70,35,width-35,57),outline="#168aff",width=3)
    y=header+18
    for row,bw,bh in bubbles:
        right=names.index(row["speaker"])%2==0
        x=width-pad-bw if right else pad
        color="#0784fc" if right else "#303033"
        draw.rounded_rectangle((x,y,x+bw,y+bh),radius=23,fill=color)
        draw.polygon([(x+bw-26,y+bh-10),(x+bw+9,y+bh),(x+bw-6,y+bh-28)] if right else
                     [(x+26,y+bh-10),(x-9,y+bh),(x+6,y+bh-28)],fill=color)
        if labels:text_box(draw,row['speaker'],(x+20,y+8,bw-40,22),'#dddddd',18,True)
        text_box(draw,row["onscreen"],(x+20,y+12+(24 if labels else 0),bw-40,bh-20-(24 if labels else 0)),"white",30,minimum=22)
        y+=bh+14
    image.save(path)
    return {"width":width,"height":height,"visible_unit_ids":[r["id"] for r in rows]}


def lesson_frame(script, index, path):
    w,h=720,1280
    image=Image.new("RGB",(w,h),"#faf9f6");draw=ImageDraw.Draw(image)
    unit=script["units"][index]
    draw.rectangle((0,0,w,10),fill="#1760df")
    text_box(draw,"ONE USEFUL THING",(52,72,616,40),"#1760df",23,True)
    text_box(draw,script["title"],(52,145,605,225),"#131c2b",51,True,minimum=28)
    draw.rounded_rectangle((52,425,668,875),radius=20,fill="#142132")
    draw.ellipse((86,464,156,534),fill="#2b68e7")
    text_box(draw,str(index+1),(86,478,70,38),"white",28,True,"center")
    text_box(draw,unit["onscreen"],(90,570,540,250),"white",39,True,minimum=24)
    text_box(draw,unit["text"],(52,940,616,165),"#354152",29,minimum=20)
    draw.rectangle((52,1160,668,1164),fill="#d7dae0")
    draw.rectangle((52,1160,52+616*(index+1)/len(script["units"]),1164),fill="#1760df")
    text_box(draw,f"{index+1:02d} / {len(script['units']):02d}",(52,1190,616,35),"#647084",18)
    image.save(path)
    return {"width":w,"height":h,"kind":"original_explanation_graphic"}


def stock_caption_frame(script,index,path):
    image=Image.new('RGB',(720,256),'#101014');draw=ImageDraw.Draw(image)
    text_box(draw,script['units'][index]['onscreen'],(32,38,656,155),'#ffffff',48,True,'center',minimum=28)
    draw.rectangle((32,230,688,234),fill='#35353e')
    draw.rectangle((32,230,32+656*(index+1)/len(script['units']),234),fill='#ffd447')
    image.save(path)
    return {'width':720,'height':256,'kind':'short_caption_block'}


def build_visuals(workspace, script, timing, folder, job=None):
    folder=Path(folder);folder.mkdir(exist_ok=True)
    story=story_specs(script,job['request']) if job and script['format']=='cutout' else None
    media=[]
    if job and script['format']=='lesson' and job['request'].get('media_mode',workspace.config()['channels'][job['channel']].get('media_mode','graphic'))=='stock':
        media=select_visuals(workspace,job,script)
        write_json(folder/'asset-selection.json',media)
    rows=[]
    for i,unit in enumerate(script["units"]):
        if script["format"]=="clip":continue
        if script['format'] in ('aura','cutout'):
            duration=timing['units'][i]['duration']
            asset=timing['selected_media'][i]['asset'] if script['format']=='aura' else None
            path=mystery_scene(script,i,duration,folder,story[unit['id']]) if story else aura_scene(script,i,asset,duration,folder,
                progression=bool(job and job['request'].get('playbook')=='aura_progression'),
                motion=timing.get('creative_scenes',[{}]*len(script['units']))[i].get('motion','slow_push'),
                clean=bool(job and job['request'].get('aura_clean')),offset=job['request'].get('media_starts',{}).get(unit['id'],0) if job else 0) if asset else cutout_scene(script,i,duration,folder)
            rows.append({'unit_id':unit['id'],'file':str(path),'duration':duration,'kind':'illustrated_mystery' if story else script['format'],
                         **({'storyboard':story[unit['id']]} if story else {}),'provenance':'Original motion/layout; any source photo has its own recorded credit.'})
            continue
        path=folder/(unit["id"]+".png")
        details=chat_frame(script,i,path) if script["format"]=="chat" else stock_caption_frame(script,i,path) if media else lesson_frame(script,i,path)
        rows.append({"unit_id":unit["id"],"file":str(path),"duration":timing["units"][i]["duration"],
                     "provenance":"Original graphic generated from this job's script",**({'media_id':media[i]['asset']['id']} if media else {}),**details})
    captions=folder/"captions.srt"
    text=[]
    for i,row in enumerate(timing["units"]):
        if not row["text"]:continue
        text.append(f"{i+1}\n{srt_time(row['start'])} --> {srt_time(row['speech_end'])}\n{row['text']}\n")
    captions.write_text("\n".join(text),encoding="utf-8")
    if timing.get('caption_cues'):write_srt(timing['caption_cues'],captions)
    result={"version":1,"format":script["format"],"frames":rows,"captions":str(captions),'selected_media':media,
            "note":"Chat shows the most recent three messages as timed states. No real private conversation is claimed."}
    if script['format']=='aura':result['aura_provenance']=[row['asset'] for row in timing['selected_media']]
    chosen=media or (timing.get('selected_media',[]) if script['format']=='aura' else [])
    result['source_bindings']=[{'unit_id':row['unit_id'],'asset_id':row['asset']['id'],
        'query':next(u.get('visual_query') or u['onscreen'] for u in script['units'] if u['id']==row['unit_id']),
        'text':next(u['text'] for u in script['units'] if u['id']==row['unit_id']),
        'offset':0,'duration':next(u['duration'] for u in timing['units'] if u['id']==row['unit_id']) if row['asset']['kind']=='video' else 0}
        for row in chosen]
    if script['format']=='clip' and job:
        result['source_bindings']=[{'unit_id':script['units'][0]['id'],'asset_id':job['request']['clip_asset_id'],
            'query':script['units'][0].get('visual_query') or script['title'],'text':script['units'][0]['text'],
            'offset':job['request'].get('clip_start',0),'duration':timing['duration']}]
    if job and media and job['request'].get('layout')=='three_blocks':
        cuts,pool=build_cuts(workspace,job,script,timing,rows,media,folder)
        result.update(cuts=cuts,montage_sources=pool,layout='three_blocks')
        result['source_bindings']=[{'unit_id':cut['unit_id'],'asset_id':ref,'query':cut['purpose'],
            'text':next(u['text'] for u in script['units'] if u['id']==cut['unit_id']),
            'role':'decorative background' if j==1 and cut['bottom_role']=='decorative' else 'semantic visual',
            'offset':cut['source_offsets'][j],'duration':cut['duration']}
            for cut in cuts for j,ref in enumerate(cut['source_asset_ids'])]
    write_json(folder/"visuals.json",result)
    return result
