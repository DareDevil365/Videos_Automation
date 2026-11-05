"""Measured character speech for the trusted phone/chat timeline."""
from array import array
from pathlib import Path
import math
import subprocess
import wave

from shorts_editor.store import write_json
from ..core import Held, digest, file_hash
from ..voice import synthesize, wav_metrics
from ..assets import asset_record


DEFAULT_VOICES=('af_heart','am_adam','am_onyx','af_bella','bm_george','bf_emma')
VOICE_STYLES={'natural':{'pitch_semitones':0,'tempo':1},
              'light_youthful':{'pitch_semitones':1.25,'tempo':1.03}}


def voice_styles(request,speakers=None):
    styles=request.get('chat_voice_styles',{})
    if not isinstance(styles,dict) or len(styles)>6 or any(not isinstance(k,str) or not isinstance(v,str) or v not in VOICE_STYLES for k,v in styles.items()):
        raise Held('chat_voice_style','Map character names to natural or light_youthful voice styles.')
    if speakers is not None and set(styles)-set(speakers):raise Held('chat_voice_style','Voice styles must name actual message speakers.')
    return styles


def style_speech(ws,timing,styles,folder):
    """Small trusted character tuning; actual age/acting remains a listening judgment."""
    if not any(v!='natural' for v in styles.values()):return timing
    folder=Path(folder);cache=ws.root/'cache/voice';cache.mkdir(parents=True,exist_ok=True)
    rows=[];chunks=[];cursor=0;rate=None
    for original in timing['units']:
        row=dict(original);style=styles.get(row['speaker'],'natural');settings=VOICE_STYLES[style]
        source=Path(row['file'])
        if style!='natural':
            key=digest(['chat-voice-style-v1',file_hash(source),style,settings])
            path=cache/(key+'.wav')
            if not path.exists():
                partial=path.with_suffix('.partial.wav');factor=2**(settings['pitch_semitones']/12)
                result=subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-i',str(source),
                    '-af',f"rubberband=tempo={settings['tempo']}:pitch={factor}:formant=shifted:transients=smooth,alimiter=limit=0.95:level=false:latency=true",
                    '-ac','1','-ar',str(timing['metrics']['sample_rate']),'-c:a','pcm_s16le',str(partial)],capture_output=True,timeout=90)
                if result.returncode:raise Held('chat_voice_style','Local voice tuning failed; this style requires FFmpeg rubberband support.')
                metrics=wav_metrics(partial)
                if metrics['duration']<.15 or metrics['rms']<.001 or metrics['clipped_fraction']>.001:raise Held('chat_voice_style','Tuned character speech failed audio checks.')
                partial.replace(path)
            row.update(file=str(path),metrics=wav_metrics(path),source_speech_file=str(source))
        row['voice_style']={'name':style,**settings}
        with wave.open(row['file'],'rb') as wav:
            if wav.getnchannels()!=1 or wav.getsampwidth()!=2 or (rate is not None and rate!=wav.getframerate()):raise Held('chat_voice_style','Styled clips must retain matching mono PCM format.')
            rate=wav.getframerate();pcm=wav.readframes(wav.getnframes())
        seconds=max(1,math.ceil(row['metrics']['duration']*30)/30)
        row.update(start=cursor,speech_end=cursor+row['metrics']['duration'],end=cursor+seconds,duration=seconds)
        chunks.extend([pcm,b'\0\0'*max(0,round(seconds*rate)-len(pcm)//2)])
        rows.append(row);cursor+=seconds
    output=folder/'styled-characters.wav'
    with wave.open(str(output),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate)
        for chunk in chunks:wav.writeframes(chunk)
    result={**timing,'units':rows,'audio':str(output),'duration':wav_metrics(output)['duration'],'metrics':wav_metrics(output),
        'cast_voice_styles':styles,'style_note':'Modest local pitch/timbre/pace tuning; no cloned voice or guaranteed perceived age.'}
    write_json(folder/'timing.json',result);return result


def cast_voices(script,request):
    speakers=list(dict.fromkeys(u['speaker'] for u in script['units']))
    supplied=request.get('chat_voice_ids',{})
    if not isinstance(supplied,dict) or set(supplied)-set(speakers):
        raise Held('chat_voice','Voice assignments must name actual message speakers.')
    if any(not isinstance(v,str) or not v for v in supplied.values()):
        raise Held('chat_voice','Each character needs an installed voice ID.')
    if len(set(supplied.values()))!=len(supplied):
        raise Held('chat_voice','Use a distinct voice for each character.')
    available=[v for v in DEFAULT_VOICES if v not in supplied.values()]
    result=dict(supplied)
    for speaker in speakers:
        if speaker not in result:
            if not available:raise Held('chat_voice','Provide a distinct installed voice for every additional character.')
            result[speaker]=available.pop(0)
    return result


def character_speech(ws,job,script,folder):
    """Reuse licensed local TTS/cache; never speak names or invent narration."""
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    voices=cast_voices(script,job['request'])
    styles=voice_styles(job['request'],voices)
    cast=[{'id':f'p{i}','speaker':speaker,'voice_id':voice} for i,(speaker,voice) in enumerate(voices.items())]
    ids={c['speaker']:c['id'] for c in cast}
    plan={'cast':cast,'scenes':[{'unit_id':u['id'],'speaker_id':ids[u['speaker']],'pause_after':0} for u in script['units']]}
    timing=synthesize(ws,script,folder,creative_plan=plan,delivery={'length_scale':1.0,'pause':0})
    return style_speech(ws,timing,styles,folder)


def place_speech(timing,samples,rate,rows):
    """Place complete speech at bubble arrival; reject drift or truncation."""
    if len(timing['units'])!=len(rows):raise Held('chat_voice','Speech and message counts differ.')
    for speech,row in zip(timing['units'],rows):
        if (speech['id'],speech['speaker'],speech['text'])!=(row['id'],row['speaker'],row['text']):
            raise Held('chat_voice','Character speech must preserve exact ordered dialogue.')
        with wave.open(speech['file'],'rb') as wav:
            if (wav.getnchannels(),wav.getsampwidth(),wav.getframerate())!=(1,2,rate):
                raise Held('chat_voice','Character clips must use matching mono 16-bit PCM.')
            pcm=array('h');pcm.frombytes(wav.readframes(wav.getnframes()))
        first=round(row['speech_start']*rate)
        if first+len(pcm)>round(row['end']*rate):raise Held('chat_voice','Message hold would truncate character speech.')
        for index,value in enumerate(pcm):
            samples[first+index]=max(-32000,min(32000,samples[first+index]+round(value*.88)))
    return {'cast_voices':timing['cast_voices'],'cast_voice_styles':timing.get('cast_voice_styles',{}),'engine':timing['engine'],
        'speech_model_sha256':timing['model_sha256'],'license_evidence':timing['license_evidence'],
        'speech_signature':digest([(u['id'],u['voice_id'],u.get('voice_style'),u['text'],u['metrics']['duration']) for u in timing['units']])}


def mix_music(ws,job,samples,rate,rows):
    """Quiet licensed bed with smooth speech ducking and true blackout silence."""
    asset=asset_record(ws,job['request']['music_id'])
    if not asset.get('has_audio'):raise Held('music_missing_audio','Chat soundtrack needs registered audio.')
    volume=job['request'].get('chat_music_volume',.20)
    if type(volume) not in (int,float) or not math.isfinite(volume) or not 0<=volume<=.35:
        raise Held('chat_music','Keep chat background music between 0 and 0.35.')
    seconds=len(samples)/rate
    decoded=subprocess.run(['ffmpeg','-v','error','-nostdin','-stream_loop','-1','-i',asset['path'],
        '-t',str(seconds),'-vn','-af','loudnorm=I=-16:TP=-3:LRA=7','-ac','1','-ar',str(rate),'-f','s16le','-'],
        capture_output=True,timeout=90)
    if decoded.returncode:raise Held('chat_music','The registered soundtrack could not be decoded.')
    music=array('h');music.frombytes(decoded.stdout)
    if len(music)<len(samples):raise Held('chat_music','The soundtrack did not cover the complete chat timeline.')
    speech=[(r['speech_start'],r['speech_end']) for r in rows if 'speech_start' in r]
    silence=[(r['start']+e['start'],r['start']+e['end']) for r in rows for e in r['screen_events'] if e['type']=='blackout']
    for i in range(len(samples)):
        t=i/rate
        gain=min(1,t/.5,(seconds-t)/.7)
        for start,end in speech:
            if start-.12<=t<=end+.20:
                envelope=min(1,max(0,(t-start+.12)/.12),max(0,(end+.20-t)/.20))
                gain*=1-.60*envelope
        for start,end in silence:
            if start<=t<end:gain=0
            elif start-.08<t<start:gain*=max(0,(start-t)/.08)
            elif end<=t<end+.12:gain*=min(1,(t-end)/.12)
        samples[i]=max(-32000,min(32000,samples[i]+round(music[i]*volume*gain)))
    return {'mixed_music_id':asset['id'],'music_source':asset['path'],
        'music_mix':{'volume':volume,'speech_duck_multiplier':.40,'blackout_silence':True,'fade_in':.5,'fade_out':.7}}


def mix_chat_effects(ws,job,script,samples,rate,rows):
    """Map trusted phone events to quiet original sounds; never infer ambience."""
    from ..sound_library import install_sound_library,mix_sound_events
    install_sound_library(ws,include_ambience=False)
    pov=script.get('phone_story',{}).get('pov',script['units'][0]['speaker'])
    arrivals=[];extras=[];blackouts=[]
    mapping={'switch':'transition','low_battery':'low_battery','glitch':'glitch'}
    for row in rows:
        notification=next((e for e in row['screen_events'] if e['type']=='notification'),None)
        category='notification' if notification else 'message_outgoing' if row['speaker']==pov else 'message_incoming'
        start=row['start']+notification['start'] if notification else row['arrival']
        arrivals.append({'category':category,'start':start,'selection_key':row['id']})
        for event in row['screen_events']:
            interval=(row['start']+event['start'],row['start']+event['end'])
            if event['type']=='blackout':blackouts.append(interval)
            elif event['type'] in mapping:
                extras.append({'category':mapping[event['type']],'start':interval[0],'selection_key':row['id']})
    explicit=job['request'].get('chat_sound_events',[])
    if len(arrivals)+len(explicit)>48:raise Held('sound_events','Too many explicitly selected sounds for this episode.')
    events=[*arrivals,*explicit,*extras[:48-len(arrivals)-len(explicit)]]
    speech=[(r['speech_start'],r['speech_end']) for r in rows if 'speech_start' in r]
    return mix_sound_events(ws,samples,rate,events,blackouts,speech)
