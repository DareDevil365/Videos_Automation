"""Reading-led portrait chat: model supplies dialogue; code supplies every edit."""
from array import array
from copy import deepcopy
import math
from pathlib import Path
import subprocess
import wave

from PIL import Image,ImageDraw,ImageOps
from shorts_editor.graphics import font,wrapped,text_box
from shorts_editor.store import write_json
from .assets import asset_record,register_asset
from .core import Held,digest
from .server_chat import speaker_color
from .transcripts import write_srt


def compile_chat_plan(script,request):
    from .playbooks import validate_playbook_script
    validate_playbook_script(script,'server_chat',request)
    speakers=list(dict.fromkeys(u['speaker'] for u in script['units']))
    scenes=[]
    for index,unit in enumerate(script['units']):
        scenes.append({'unit_id':unit['id'],'text':unit['text'],'speaker_id':f'p{speakers.index(unit["speaker"])+1}',
            'stage':'hook' if index==0 else 'payoff' if unit['id']==script['edit']['payoff_unit_id'] else 'reply',
            'visible_cast':[],'framing':'message_focus','motion':'reaction_punch' if index in (0,len(script['units'])-1) or (len(unit['text'].split())<=3 and '?' in unit['text']) else 'message_entry',
            'pause_after':0,'avatar_slot':speakers.index(unit['speaker'])})
    plan={'version':2,'template':'server_chat_v2','cast':[{'id':f'p{i+1}','speaker':s,'avatar_kind':'chat_avatar','voice_id':''} for i,s in enumerate(speakers)],
        'scenes':scenes,'comment_question':'','script_sha256':digest(script),
        'editing_policy':'Fixed readable portrait cards, measured reading holds, context, typing/entry and reaction emphasis. No model timing/camera/sound decisions.'}
    return {'plan':plan,'script_sha256':digest(script),'origin':'compiled_chat_rules_v2','repairs':0,
        'review_note':'Structural code checks only. This is not a model or owner opinion about humor.'}


def reading_timing(ws,job,script,folder):
    """Frame-clock reading durations and locally synthesized original sound effects."""
    from .playbooks import get_playbook
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);rows=[];cursor=0
    for index,unit in enumerate(script['units']):
        typing=0 if index==0 else .38 if index==len(script['units'])-1 else .16
        hold=max(1.05,len(unit['text'].split())/3.8+.25,len(unit['text'])/24+.25)
        if index==len(script['units'])-1:hold+=.65
        seconds=math.ceil((typing+hold)*30)/30
        rows.append({'id':unit['id'],'speaker':unit['speaker'],'text':unit['text'],'start':cursor,
            'speech_end':cursor+seconds,'end':cursor+seconds,'duration':seconds,'typing_seconds':typing,
            'arrival':cursor+typing,'hold_seconds':seconds-typing})
        cursor+=seconds
    minimum,maximum=get_playbook('server_chat',job['request'])['seconds']
    if not minimum<=cursor<=maximum:
        raise Held('chat_reading_duration',f'Complete reading time is {cursor:.1f}s; need {minimum}-{maximum}s. Revise messages, never truncate their holds.')
    rate=24000;samples=array('h',[0])*round(cursor*rate)
    def tone(start,frequency,seconds,volume):
        first=round(start*rate)
        for n in range(round(seconds*rate)):
            if first+n>=len(samples):break
            t=n/rate;envelope=min(1,t/.006)*math.exp(-t*30)
            value=round(volume*envelope*math.sin(2*math.pi*frequency*t)*26000)
            samples[first+n]=max(-30000,min(30000,samples[first+n]+value))
    for index,row in enumerate(rows):
        if row['typing_seconds']:
            for tick in (0,.055,.11):tone(row['start']+tick,650+index%3*75,.025,.09)
        tone(row['arrival'],970 if index%2 else 1220,.10,.16)
        tone(row['arrival']+.055,1450,.08,.07)
    tone(rows[-1]['arrival']+.2,210,.28,.28)
    output=folder/'chat-sound.wav';temporary=folder/'chat-sound.partial.wav'
    with wave.open(str(temporary),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(samples.tobytes())
    temporary.replace(output)
    result={'version':2,'voice':'none; reading-led conversation','source':'original_local_chat_sfx',
        'audio':str(output),'duration':len(samples)/rate,'units':rows,'model_sha256':digest('chat-reading-and-original-sfx-v2'),
        'caption_alignment':'Exact complete message text with code-measured reading holds; no invented speech alignment.',
        'editing_origin':'compiled_chat_rules_v2','narration':False,
        'limits':['Reading time is a bounded heuristic, not measured audience comprehension.','No voiceover, copied creator audio or model editing calls.']}
    write_json(folder/'timing.json',result);return result


def _card(unit,width,palette,avatar=None,emphasis=False):
    size=46 if emphasis else 42;draw=ImageDraw.Draw(Image.new('RGB',(width,800)))
    lines=wrapped(draw,unit['text'],font(size),width-152)
    if len(lines)>4:raise Held('chat_message_length','This message cannot fit four readable lines. Shorten it instead of shrinking text.')
    height=92+len(lines)*round(size*1.23)+22
    card=Image.new('RGBA',(width,height));d=ImageDraw.Draw(card)
    d.rounded_rectangle((0,0,width-1,height-1),radius=18,fill='#303238',outline='#44474f',width=2)
    color=palette[unit['speaker']];d.ellipse((19,23,91,95),fill=color)
    if avatar is not None:
        mask=Image.new('L',(72,72));ImageDraw.Draw(mask).ellipse((0,0,71,71),fill=255)
        card.paste(ImageOps.fit(avatar,(72,72)),(19,23),mask)
    else:text_box(d,unit['speaker'][0].upper(),(20,38,70,42),'#172127',30,True,'center',minimum=30)
    d=ImageDraw.Draw(card)
    text_box(d,unit['speaker'],(110,21,width-134,42),color,30,True,minimum=30)
    text_box(d,unit['text'],(110,75,width-134,height-83),'#f4f5f8',size,minimum=size)
    return card


def chat_frame(script,index,second,duration,typing,avatars=None):
    units=script['units'];avatars=avatars or {};palette={}
    for unit in units:
        if unit['speaker'] not in palette:palette[unit['speaker']]=speaker_color(unit['speaker'],palette.values())
    arrived=second>=typing;last=index if arrived else index-1
    focus=index==len(units)-1 or (len(units[index]['text'].split())<=3 and '?' in units[index]['text'])
    visible=units[max(0,last-(1 if focus else 2)):last+1] if last>=0 else []
    cards=[_card(u,656,palette,avatars.get(u['speaker']),focus and u['id']==units[index]['id']) for u in visible]
    while len(cards)>1 and sum(c.height+18 for c in cards)-18>850:
        cards.pop(0);visible=visible[1:]
    total=sum(c.height+18 for c in cards)-18
    image=Image.new('RGB',(720,1280),'#14151a');d=ImageDraw.Draw(image)
    d.rectangle((0,0,720,9),fill='#8eabff')
    text_box(d,'AFTER HOURS',(34,64,650,36),'#f4f5f8',28,True,minimum=28)
    text_box(d,'# common-room  /  fictional chat',(34,112,650,32),'#8f96a7',21,minimum=21)
    y=max(212,round(650-total/2))
    for unit,card in zip(visible,cards):
        active=unit['id']==units[index]['id']
        elapsed=max(0,second-typing);entry=min(1,elapsed/.16)
        if active:
            slide=round(22*(1-entry)**2)
            if entry<1:card.putalpha(card.getchannel('A').point(lambda a:round(a*entry)))
            if focus and entry>=1:
                scale=1+.035*min(1,elapsed/.7);card=card.resize((round(card.width*scale),round(card.height*scale)),Image.Resampling.LANCZOS)
            image.paste(card,((720-card.width)//2,y+slide),card)
        else:
            card.putalpha(card.getchannel('A').point(lambda a:round(a*.72)));image.paste(card,(32,y),card)
        y+=card.height+18
    d=ImageDraw.Draw(image)
    if not arrived:
        y=min(1060,max(340,y+15))
        text_box(d,units[index]['speaker']+' is typing',(40,y,600,32),'#a7afbf',25,minimum=25)
        for i in range(3):
            alpha=1 if int(second*12)%3==i else .4
            d.ellipse((42+i*22,y+44,52+i*22,y+54),fill=tuple(round(v*alpha) for v in (170,188,225)))
    text_box(d,'ORIGINAL FICTION',(34,1174,650,28),'#737c91',18,minimum=18)
    return image,{'visible_unit_ids':[u['id'] for u in visible],'active_unit_id':units[index]['id'],
        'message_arrived':arrived,'emphasis':focus,'typing_seconds':typing,'canvas':[720,1280]}


def render_chat_message(script,index,spoken,path,avatars=None):
    path=Path(path);duration=spoken['duration'];typing=spoken['typing_seconds']
    poster,meta=chat_frame(script,index,duration*.8,duration,typing,avatars);poster.save(path.with_suffix('.png'))
    partial=path.with_suffix('.partial.mp4');log=path.with_suffix('.ffmpeg.log')
    with log.open('wb') as errors:
        process=subprocess.Popen(['ffmpeg','-v','error','-nostdin','-y','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280',
            '-framerate','30','-i','pipe:0','-t',str(duration),'-an','-c:v','libx264','-preset','veryfast','-crf','20',
            '-threads','2','-pix_fmt','yuv420p',str(partial)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=errors)
        try:
            final=poster.tobytes()
            for frame in range(math.ceil(duration*30)):
                second=frame/30
                value=chat_frame(script,index,second,duration,typing,avatars)[0].tobytes() if second<typing+.9 else final
                process.stdin.write(value)
            process.stdin.close();process.wait(timeout=120)
            if process.returncode:raise Held('chat_render','Chat encoding failed; inspect the retained log.')
        except BaseException:
            if process.poll() is None:process.kill();process.wait()
            if not process.stdin.closed:process.stdin.close()
            raise
    partial.replace(path);return meta


def build_chat_visuals(ws,job,script,timing,folder,record):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);plan=record['plan']
    if record['script_sha256']!=digest(script):raise Held('creative_rewrite','Compiled chat plan differs from frozen dialogue.')
    if [u['id'] for u in timing['units']]!=[u['id'] for u in script['units']]:raise Held('chat_timing','Chat and timed message IDs differ.')
    avatars={};provenance=[];ids=job['request'].get('chat_avatar_ids',[]);crops=job['request'].get('chat_avatar_crops',[])
    if not isinstance(ids,list) or len(ids)>3:raise Held('chat_avatar','Supply at most three registered avatar IDs.')
    if not isinstance(crops,list) or len(crops)>len(ids):raise Held('chat_avatar','Avatar crops must be a list matching supplied avatar slots.')
    for index,ref in enumerate(ids):
        asset=asset_record(ws,ref)
        if asset['kind']!='image':raise Held('chat_avatar','Chat avatars must be actual registered images.')
        provenance.append(asset)
        if index>=len(plan['cast']):continue
        with Image.open(asset['path']) as raw:avatar=ImageOps.exif_transpose(raw).convert('RGB')
        if index<len(crops):
            from .illustrated_story import normalized_box
            box=normalized_box(crops[index],'avatar crop');w,h=avatar.size
            avatar=avatar.crop(tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(box)))
        avatars[plan['cast'][index]['speaker']]=avatar
    rows=[]
    for index,spoken in enumerate(timing['units']):
        output=folder/(spoken['id']+'-chat.mp4');details=render_chat_message(script,index,spoken,output,avatars)
        made=register_asset(ws,output,'original_graphic',{'generator':'compiled-chat-editor-v2','unit_id':spoken['id'],
            'avatar_source_ids':ids,'message_state':details},test_only=job['request'].get('test_only',False))
        rows.append({'unit_id':spoken['id'],'file':str(output),'media_id':made['id'],'duration':spoken['duration'],
            'kind':'chat_rules_v2','message_state':details})
    captions=folder/'captions.srt';write_srt([{'start':u['arrival'],'end':u['end'],'text':u['text']} for u in timing['units']],captions)
    result={'version':2,'format':'chat','frames':rows,'captions':str(captions),'planned_template':'server_chat_v2',
        'planned_provenance':provenance,'selected_media':[],'source_bindings':[],'editing_origin':record['origin'],
        'creative_plan_sha256':digest(plan)}
    result['chat_editing']={'status':'pass','origin':'compiled_chat_rules_v2','message_count':len(rows),
        'canvas':[720,1280],'timing':'frame-clock reading holds','narration':False,'editing_model_calls':0,
        'limits':'Structural rendering checks, not a humor, comprehension or audience-quality score.'}
    write_json(folder/'visuals.json',result);return result
