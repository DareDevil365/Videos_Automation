"""Reading-led portrait chat: model supplies dialogue; code supplies every edit."""
from array import array
import math
from pathlib import Path
import subprocess
import wave

from PIL import Image,ImageOps
from shorts_editor.store import write_json
from .assets import asset_record,register_asset
from .core import Held,digest
from .transcripts import write_srt
from .phone_editor.contract import compile_beats
from .phone_editor.story import story_frame
from .phone_editor.messenger import bubble_layout,chat_frame


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
        'editing_policy':'Clean mobile messenger crop, readable bubbles, real scrolling, local camera emphasis and soft cue audio. No model timing/camera/sound decisions.'}
    if script.get('phone_story'):plan['phone_timeline']=compile_beats(script)
    return {'plan':plan,'script_sha256':digest(script),'origin':'compiled_chat_rules_v2','repairs':0,
        'review_note':'Structural code checks only. This is not a model or owner opinion about humor.'}


def reading_timing(ws,job,script,folder):
    """Frame-clock reading durations and locally synthesized original sound effects."""
    from .playbooks import get_playbook
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);rows=[];cursor=0
    beats=compile_beats(script) if script.get('phone_story') else None
    for index,unit in enumerate(script['units']):
        typing=0 if index==0 else .38 if index==len(script['units'])-1 else .16
        hold=max(1.05,len(unit['text'].split())/3.8+.25,len(unit['text'])/24+.25)
        if unit['id'] in job['request'].get('chat_attachment_ids',{}):hold=max(hold,3.0)
        if index==len(script['units'])-1:hold+=.65
        prefix=beats[index]['prefix_seconds'] if beats else 0
        seconds=math.ceil((prefix+typing+hold)*30)/30
        rows.append({'id':unit['id'],'speaker':unit['speaker'],'text':unit['text'],'start':cursor,
            'speech_end':cursor+seconds,'end':cursor+seconds,'duration':seconds,'typing_seconds':typing,
            'arrival':cursor+prefix+typing,'hold_seconds':seconds-prefix-typing,
            'prefix_seconds':prefix,'screen_events':beats[index]['events'] if beats else []})
        cursor+=seconds
    minimum,maximum=get_playbook('server_chat',job['request'])['seconds']
    if not minimum<=cursor<=maximum:
        raise Held('chat_reading_duration',f'Complete reading time is {cursor:.1f}s; need {minimum}-{maximum}s. Revise messages, never truncate their holds.')
    rate=24000;samples=array('h',[0])*round(cursor*rate)
    def soft_pop(start,outgoing=False,payoff=False):
        first=round(start*rate)
        seconds=.13 if not payoff else .19
        base=520 if outgoing else 415
        for n in range(round(seconds*rate)):
            if first+n>=len(samples):break
            t=n/rate;envelope=math.sin(math.pi*t/seconds)**2*math.exp(-t*21)
            phase=2*math.pi*(base*t+45*(1-math.exp(-t*35))/35)
            value=round((.095 if payoff else .065)*envelope*(math.sin(phase)+.12*math.sin(phase*2))*26000)
            samples[first+n]=max(-30000,min(30000,samples[first+n]+value))
    outgoing=script.get('phone_story',{}).get('pov',script['units'][0]['speaker'])
    for index,row in enumerate(rows):
        notification=next((e for e in row['screen_events'] if e['type']=='notification'),None)
        soft_pop(row['start']+notification['start'] if notification else row['arrival'],row['speaker']==outgoing,index==len(rows)-1)
    output=folder/'chat-sound.wav';temporary=folder/'chat-sound.partial.wav'
    with wave.open(str(temporary),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(samples.tobytes())
    temporary.replace(output)
    result={'version':2,'voice':'none; reading-led conversation','source':'original_local_chat_sfx',
        'audio':str(output),'duration':len(samples)/rate,'units':rows,'model_sha256':digest('chat-soft-message-pop-v3'),
        'sound_design':'One quiet rounded message pop per arrival, distinct incoming/outgoing pitch; no repeated typing chirps or sharp notification stack.',
        'caption_alignment':'Exact complete message text with code-measured reading holds; no invented speech alignment.',
        'editing_origin':'compiled_chat_rules_v2','narration':False,
        'limits':['Reading time is a bounded heuristic, not measured audience comprehension.','No voiceover, copied creator audio or model editing calls.']}
    write_json(folder/'timing.json',result);return result


def render_chat_message(script,index,spoken,path,avatars=None,wallpapers=None,attachments=None,group_name=None):
    path=Path(path);duration=spoken['duration'];typing=spoken['typing_seconds']
    render=(lambda second: story_frame(script,index,second,duration,typing,avatars,wallpapers,attachments)) if script.get('phone_story') else (lambda second: chat_frame(script,index,second,duration,typing,avatars,{'attachments':attachments or {},**({'contact':group_name} if group_name else {})}))
    hold_time=min(duration-.51,spoken.get('prefix_seconds',0)+typing+1.12)
    poster,meta=render(hold_time);poster.save(path.with_suffix('.png'))
    partial=path.with_suffix('.partial.mp4');log=path.with_suffix('.ffmpeg.log')
    with log.open('wb') as errors:
        process=subprocess.Popen(['ffmpeg','-v','error','-nostdin','-y','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280',
            '-framerate','30','-i','pipe:0','-t',str(duration),'-an','-c:v','libx264','-preset','veryfast','-crf','20',
            '-threads','2','-pix_fmt','yuv420p',str(partial)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=errors)
        try:
            final=poster.tobytes()
            for frame in range(math.ceil(duration*30)):
                second=frame/30
                value=render(second)[0].tobytes() if attachments or second<spoken.get('prefix_seconds',0)+typing+1.1 or second>duration-.5 else final
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
    if not isinstance(ids,list) or len(ids)>6:raise Held('chat_avatar','Supply at most six registered avatar IDs.')
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
    wallpapers={}
    for thread_id,ref in job['request'].get('phone_wallpaper_ids',{}).items():
        if thread_id not in {t['id'] for t in script.get('phone_story',{}).get('threads',[])}:raise Held('phone_wallpaper','Wallpaper references an unknown conversation.')
        asset=asset_record(ws,ref)
        if asset['kind']!='image':raise Held('phone_wallpaper','Wallpapers need registered images.')
        provenance.append(asset)
        with Image.open(asset['path']) as raw:wallpapers[thread_id]=ImageOps.exif_transpose(raw).convert('RGB')
    attachments={}
    from .phone_editor.attachments import Attachment
    for uid,ref in job['request'].get('chat_attachment_ids',{}).items():
        if uid not in {u['id'] for u in script['units']}:raise Held('chat_attachment','Attachment must reference an existing message.')
        asset=asset_record(ws,ref)
        if Path(asset['path']).suffix.lower() not in ('.gif','.png','.jpg','.jpeg','.webp'):raise Held('chat_attachment','Use registered GIF or still-image attachments.')
        attachments[uid]=Attachment(asset['path']);provenance.append(asset)
    rows=[]
    for index,spoken in enumerate(timing['units']):
        output=folder/(spoken['id']+'-chat.mp4');details=render_chat_message(script,index,spoken,output,avatars,wallpapers,attachments,job['request'].get('chat_group_name'))
        made=register_asset(ws,output,'original_graphic',{'generator':'compiled-chat-editor-v2','unit_id':spoken['id'],
            'avatar_source_ids':ids,'wallpaper_source_ids':list(job['request'].get('phone_wallpaper_ids',{}).values()),'message_state':details},test_only=job['request'].get('test_only',False))
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
