from array import array
import json
import math
from pathlib import Path
import wave
import subprocess
import os

from shorts_editor.store import write_json
from .core import Held, digest, file_hash, now
from .net import fetch


VOICE_BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ljspeech/high/"
VOICE_NAME="en_US-ljspeech-high.onnx"
LICENSE_URLS=["https://huggingface.co/rhasspy/piper-voices/raw/main/en/en_US/ljspeech/high/MODEL_CARD",
              "https://brycebeattie.com/files/tts/", "https://keithito.com/LJ-Speech-Dataset/"]


def install_kokoro_voice(workspace,voice_id='am_adam'):
    folder=workspace.root/'voices'/'kokoro';folder.mkdir(exist_ok=True)
    base='https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/'
    for name,limit in [('kokoro-v1.0.onnx',400_000_000),('voices-v1.0.bin',50_000_000)]:
        path=folder/name
        if not path.is_file():
            body,_,_=fetch(base+name,maximum=limit);temporary=path.with_suffix('.partial');temporary.write_bytes(body);temporary.replace(path)
    record={'model_license':'Apache-2.0','runtime_license':'MIT','checked_at':now(),
            'evidence':['https://huggingface.co/hexgrad/Kokoro-82M','https://github.com/thewh1teagle/kokoro-onnx'],
            'model_sha256':file_hash(folder/'kokoro-v1.0.onnx'),'voices_sha256':file_hash(folder/'voices-v1.0.bin')}
    write_json(folder/'license.json',record)
    try:from kokoro_onnx import Kokoro
    except ImportError:raise Held('voice_runtime_missing','Install the optional voices dependencies.')
    voices=Kokoro(str(folder/'kokoro-v1.0.onnx'),str(folder/'voices-v1.0.bin')).get_voices()
    if voice_id not in voices:raise Held('voice_id','The selected voice is not in this voice pack.')
    config=workspace.config();config['voice'].update(engine='kokoro',normalize_loudness=True)
    config['voice']['kokoro']={'model':'voices/kokoro/kokoro-v1.0.onnx','voices':'voices/kokoro/voices-v1.0.bin',
        'commercial_use_checked':True,'license_evidence':record['evidence'],'model_sha256':record['model_sha256'],
        'config_sha256':record['voices_sha256'],'voice_id':voice_id}
    workspace.save_config(config);return {'engine':'kokoro','selected_voice':voice_id,'voices':voices,'license_record':str(folder/'license.json')}


def install_default_voice(workspace):
    folder=workspace.root/"voices"
    paths=[]
    for name in (VOICE_NAME,VOICE_NAME+".json"):
        path=folder/name
        if not path.exists():
            body,_,_=fetch(VOICE_BASE+name,maximum=140_000_000)
            temporary=path.with_suffix(path.suffix+".partial")
            temporary.write_bytes(body);temporary.replace(path)
        paths.append(path)
    card,_,_=fetch(LICENSE_URLS[0])
    (folder/"MODEL_CARD.md").write_bytes(card)
    author,_,_=fetch(LICENSE_URLS[1])
    (folder/"voice-author-license.html").write_bytes(author)
    record={"name":VOICE_NAME,"checked_at":now(),"license":"public domain (author and model dataset statements)",
            "evidence_urls":LICENSE_URLS,"model_sha256":file_hash(paths[0]),"config_sha256":file_hash(paths[1]),
            "source":VOICE_BASE,"note":"Model provenance is recorded; final pronunciation/naturalness still needs sample review."}
    write_json(folder/"license.json",record)
    config=workspace.config();config["voice"].update(model="voices/"+VOICE_NAME,commercial_use_checked=True,
        license_evidence=LICENSE_URLS,model_sha256=record["model_sha256"],config_sha256=record["config_sha256"])
    workspace.save_config(config)
    return record


def wav_metrics(path):
    with wave.open(str(path),"rb") as wav:
        if wav.getsampwidth()!=2:raise Held("unsupported_audio","Expected 16-bit PCM speech.")
        samples=array("h");samples.frombytes(wav.readframes(wav.getnframes()))
        duration=wav.getnframes()/wav.getframerate()
        rate,channels=wav.getframerate(),wav.getnchannels()
    peak=max((abs(x) for x in samples),default=0)/32768
    rms=math.sqrt(sum(x*x for x in samples)/max(1,len(samples)))/32768
    return {"duration":duration,"sample_rate":rate,"channels":channels,"peak":peak,"rms":rms,
            "clipped_fraction":sum(abs(x)>=32760 for x in samples)/max(1,len(samples))}


def synthesize(workspace, script, folder, pause=.16, fps=30,creative_plan=None,delivery=None):
    settings=workspace.config()["voice"]
    delivery=delivery or {}
    engine=settings.get('engine','piper')
    if engine=='kokoro':settings={**settings,**settings.get('kokoro',{})}
    elif engine!='piper':raise Held('voice_engine','Unsupported voice engine.')
    if delivery:settings={**settings,**{k:v for k,v in delivery.items() if k in ('voice_id','length_scale')}};pause=float(delivery.get('pause',pause))
    if not math.isfinite(float(settings.get('length_scale',1))) or not .6<=float(settings.get('length_scale',1))<=1.8:
        raise Held('voice_pace','Voice length scale must be between 0.6 and 1.8')
    if not math.isfinite(pause) or not 0<=pause<=1.5:raise Held('voice_pause','Pause must be between 0 and 1.5 seconds')
    scene_map={s['unit_id']:s for s in creative_plan['scenes']} if creative_plan else {}
    cast_map={c['id']:c for c in creative_plan['cast']} if creative_plan else {}
    if creative_plan and engine!='kokoro':raise Held('cast_voice_engine','Multi-character directed voice needs the configured Kokoro voice pack; do not pretend one Piper model is several voices')
    model=workspace.resolve(settings["model"])
    if not model.is_file():raise Held("voice_model_missing","Install the configured voice with the voice-setup command.")
    if not settings.get("commercial_use_checked") or not settings.get("license_evidence"):
        raise Held("voice_license_missing","Record the exact voice model's commercial-use evidence before production.")
    model_sha=file_hash(model)
    config_path=workspace.resolve(settings['voices']) if engine=='kokoro' else Path(str(model)+'.json')
    config_sha=file_hash(config_path)
    if settings.get("model_sha256") and model_sha!=settings["model_sha256"]:
        raise Held("voice_model_changed","The voice model changed; verify it before using cached production audio.")
    if settings.get('config_sha256') and config_sha!=settings['config_sha256']:
        raise Held('voice_model_changed','The voice configuration changed after its provenance was recorded.')
    if engine=='kokoro':
        try:
            from kokoro_onnx import Kokoro
            import numpy as np
        except ImportError:raise Held('voice_runtime_missing','Install the optional Kokoro voice dependencies.')
        voice=Kokoro(str(model),str(config_path))
        if settings.get('voice_id','am_onyx') not in voice.get_voices():raise Held('voice_id','Selected Kokoro voice is unavailable.')
    else:
        try:
            from piper import PiperVoice, SynthesisConfig
        except ImportError:raise Held("voice_runtime_missing","Install the production dependencies in the local environment.")
        voice=PiperVoice.load(model,use_cuda=False)
    cache=workspace.root/"cache"/"voice";cache.mkdir(exist_ok=True)
    from .speech_delivery import speech_segments,number

    def cached_segment(text,voice_id,speed):
        scale=float(settings.get('length_scale',1))/speed
        number(scale,.6,1.8,'voice_pace')
        key=digest(["measured-tts-v3",engine,voice_id,model_sha,config_sha,scale,text])
        path=cache/(key+'.wav')
        if not path.exists():
            temporary=path.with_suffix('.partial.wav')
            with wave.open(str(temporary),'wb') as wav:
                if engine=='kokoro':
                    samples,sample_rate=voice.create(text,voice=voice_id,speed=1/scale,lang='en-us')
                    peak=float(np.max(np.abs(samples))) if len(samples) else 0
                    if peak>.95:samples=samples*(.95/peak)
                    wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(sample_rate)
                    wav.writeframes((np.clip(samples,-1,1)*32767).astype('<i2').tobytes())
                else:voice.synthesize_wav(text,wav,syn_config=SynthesisConfig(length_scale=scale,normalize_audio=True))
            metrics=wav_metrics(temporary)
            if metrics['duration']<.15 or metrics['rms']<.001:raise Held('silent_voice','The voice produced empty or silent audio.')
            if metrics['clipped_fraction']>.001:raise Held('clipped_voice','The voice output contains excessive clipped samples.')
            temporary.replace(path)
        return path

    rows=[];pcm_parts=[];rate=None;elapsed=0
    folder=Path(folder);folder.mkdir(exist_ok=True)
    for unit in script["units"]:
        scene=scene_map.get(unit['id']);voice_id=cast_map[scene['speaker_id']]['voice_id'] if scene else settings.get('voice_id','am_onyx') if engine=='kokoro' else None
        unit_pause=float(scene.get('pause_after',pause)) if scene else pause
        if not 0<=unit_pause<=1.5:raise Held('voice_pause','Directed pause is outside the supported range')
        segments=speech_segments(unit['text'],scene)
        thinking=number((scene or {}).get('thinking_seconds',0),0,6,'voice_pause')
        if thinking and ((scene or {}).get('graphic',{}).get('kind')!='timer' or thinking<2):
            raise Held('voice_pause','Thinking silence needs a timer scene and 2-6 seconds.')
        if engine=='kokoro' and voice_id not in voice.get_voices():raise Held('voice_id','A cast voice is not installed')
        from .source_delivery import connected_text
        linked_phrases = (scene or {}).get('linked_phrases', [])
        spoken_texts = [connected_text(s['text'], linked_phrases) for s in segments]
        parts=[cached_segment(text,voice_id,s['speed']) for text,s in zip(spoken_texts,segments)]
        spans=[]
        if len(parts)==1 and segments[0]['pause_after']==0:
            path=parts[0]
        else:
            assembly_key = ['measured-tts-assembly-v1',engine,voice_id,model_sha,config_sha,
                            settings.get('length_scale',1),segments]
            if spoken_texts != [s['text'] for s in segments]:
                assembly_key.append(spoken_texts)
            path=cache/(digest(assembly_key)+'.wav')
            chunks=[];segment_rate=None;cursor=0
            for segment,part in zip(segments,parts):
                with wave.open(str(part),'rb') as wav:
                    if wav.getnchannels()!=1 or wav.getsampwidth()!=2:raise Held('voice_channels','Segments must be mono 16-bit PCM.')
                    if segment_rate is not None and segment_rate!=wav.getframerate():raise Held('voice_sample_rate','Speech segments have mismatched sample rates.')
                    segment_rate=wav.getframerate();pcm=wav.readframes(wav.getnframes())
                seconds=len(pcm)/2/segment_rate;silence=round(segment_rate*segment['pause_after'])
                spans.append({**segment,'start':cursor,'speech_end':cursor+seconds,'end':cursor+seconds+silence/segment_rate})
                chunks.extend([pcm,b'\0\0'*silence]);cursor+=seconds+silence/segment_rate
            if not path.exists():
                temporary=path.with_suffix('.partial.wav')
                with wave.open(str(temporary),'wb') as wav:
                    wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(segment_rate)
                    for pcm in chunks:wav.writeframes(pcm)
                temporary.replace(path)
        metrics=wav_metrics(path)
        with wave.open(str(path),"rb") as wav:
            if wav.getnchannels()!=1:raise Held("voice_channels","Voice output must be mono before assembly.")
            if rate is not None and rate!=wav.getframerate():raise Held("voice_sample_rate","Speech clips have mismatched sample rates.")
            rate=wav.getframerate();pcm=wav.readframes(wav.getnframes())
        duration=max(1,math.ceil((metrics["duration"]+thinking+unit_pause)*fps)/fps)
        padding=max(0,round(rate*duration)-len(pcm)//2)
        rows.append({"id":unit["id"],"speaker":unit["speaker"],"text":unit["text"],"file":str(path),
                     "start":elapsed,"speech_end":elapsed+metrics["duration"],"end":elapsed+duration,"duration":duration,"metrics":metrics,
                     'voice_id':voice_id,'pause_after':unit_pause,'delivery_length_scale':settings.get('length_scale',1),
                     **({'linked_phrases': linked_phrases, 'speech_engine_text': ' '.join(spoken_texts)} if linked_phrases else {}),
                     'speech_segments':segments,'segment_timings':spans,'thinking_seconds':thinking})
        pcm_parts.extend([pcm,b"\0\0"*padding])
        elapsed+=duration
    if not .5<elapsed<=179:raise Held("voice_too_long","Narration must fit the three-minute compositor limit; shorten this script.")
    output=folder/"narration.wav"
    with wave.open(str(output),"wb") as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate)
        for pcm in pcm_parts:wav.writeframes(pcm)
    if settings.get('normalize_loudness',True):
        normalized=folder/'normalized.partial.wav'
        result=subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-i',str(output),'-af','loudnorm=I=-14:TP=-1.5:LRA=7',
                               '-ar',str(rate),'-ac','1','-c:a','pcm_s16le',str(normalized)],capture_output=True,timeout=90)
        if result.returncode:raise Held('voice_normalization','Narration loudness normalization failed.')
        os.replace(normalized,output)
    timing={"version":1,"voice":settings.get('voice_id',model.name) if engine=='kokoro' else model.name,'engine':engine,"model_sha256":model_sha,"license_evidence":settings["license_evidence"],
            "audio":str(output),"duration":wav_metrics(output)["duration"],"units":rows,
            "caption_alignment":"Measured spoken-unit timing, not word alignment","metrics":wav_metrics(output)}
    if creative_plan:timing.update(cast_voices={c['speaker']:c['voice_id'] for c in creative_plan['cast']},delivery=delivery,
        emotion_note='Pauses, voice selection and pace are controlled; expressive fear/acting is not guaranteed by the local model.')
    write_json(folder/"timing.json",timing)
    return timing
