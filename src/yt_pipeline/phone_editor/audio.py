"""Measured character speech for the trusted phone/chat timeline."""
from array import array
from pathlib import Path
import math
import subprocess
import wave

from ..core import Held, digest
from ..voice import synthesize
from ..assets import asset_record


DEFAULT_VOICES=('af_heart','am_adam','am_onyx','af_bella','bm_george','bf_emma')


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
    cast=[{'id':f'p{i}','speaker':speaker,'voice_id':voice} for i,(speaker,voice) in enumerate(voices.items())]
    ids={c['speaker']:c['id'] for c in cast}
    plan={'cast':cast,'scenes':[{'unit_id':u['id'],'speaker_id':ids[u['speaker']],'pause_after':0} for u in script['units']]}
    return synthesize(ws,script,folder,creative_plan=plan,delivery={'length_scale':1.0,'pause':0})


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
    return {'cast_voices':timing['cast_voices'],'engine':timing['engine'],
        'speech_model_sha256':timing['model_sha256'],'license_evidence':timing['license_evidence'],
        'speech_signature':digest([(u['id'],u['voice_id'],u['text'],u['metrics']['duration']) for u in timing['units']])}


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
