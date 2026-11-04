"""Timed subtitle import, local transcription and actual caption burn-in."""
import html
import json
import math
from pathlib import Path
import re
import subprocess
import os

from shorts_editor.render import srt_time
from shorts_editor.store import write_json
from .core import Held, digest, file_hash


def seconds(value):
    parts=value.replace(',','.').split(':')
    if len(parts)==2:return int(parts[0])*60+float(parts[1])
    if len(parts)==3:return int(parts[0])*3600+int(parts[1])*60+float(parts[2])
    raise ValueError('Invalid subtitle timestamp')


def parse_subtitles(path):
    text=Path(path).read_text(encoding='utf-8-sig',errors='replace');cues=[]
    pattern=r'(?m)^\s*((?:\d+:)?\d{2}:\d{2}[.,]\d{3})\s*-->\s*((?:\d+:)?\d{2}:\d{2}[.,]\d{3})[^\n]*\n(.*?)(?=\n\s*\n|\Z)'
    for match in re.finditer(pattern,text,re.S):
        start,end=seconds(match[1]),seconds(match[2]);body=html.unescape(re.sub(r'<[^>]*>','',match[3]))
        body=' '.join(line.strip() for line in body.splitlines() if line.strip())
        if not body or not math.isfinite(end) or not 0<=start<end:continue
        if cues and body==cues[-1]['text'] and start<=cues[-1]['end']+.15:
            cues[-1]['end']=max(end,cues[-1]['end']);continue
        cues.append({'start':start,'end':end,'text':body[:2000]})
    cues.sort(key=lambda row:row['start'])
    if not cues:raise Held('transcript_empty','No readable timed subtitles were found.')
    return cues


def transcribe(workspace, media, model='base.en'):
    if model not in ('tiny.en','base.en','small.en'):raise ValueError('Choose a supported local English ASR model')
    key=digest(['faster-whisper-1.2',file_hash(media),model])
    path=workspace.root/'cache'/('transcript-'+key+'.json')
    if path.exists():return json.loads(path.read_text(encoding='utf-8'))
    try:from faster_whisper import WhisperModel
    except ImportError:raise Held('transcriber_missing','Install the optional sources dependencies for local transcription.')
    runtime=WhisperModel(model,device='cpu',compute_type='int8',download_root=str(workspace.root/'voices'/'asr'))
    segments,info=runtime.transcribe(str(media),beam_size=5,vad_filter=False,word_timestamps=True)
    cues=[]
    for segment in segments:
        words=[{'start':w.start,'end':w.end,'text':w.word.strip()} for w in (segment.words or []) if w.word.strip()]
        cues.append({'start':segment.start,'end':segment.end,'text':segment.text.strip(),'words':words})
    if not cues:raise Held('transcript_empty','No speech was recognized. Supply corrected subtitles or choose a different source.')
    result={'origin':'local_whisper','model':model,'language':info.language,'cues':cues,
            'note':'Machine transcription can mishear names and words. Source speech remains authoritative.'}
    write_json(path,result);return result


def clip_cues(cues,start,end,max_words=7):
    rows=[]
    for cue in cues:
        left=max(start,float(cue['start']));right=min(end,float(cue['end']))
        if left>=right:continue
        words=cue.get('words') or []
        if words:
            kept=[w for w in words if float(w['end'])>start and float(w['start'])<end]
            for i in range(0,len(kept),max_words):
                group=kept[i:i+max_words]
                rows.append({'start':max(0,group[0]['start']-start),'end':min(end-start,group[-1]['end']-start),'text':' '.join(w['text'] for w in group)})
        else:rows.append({'start':left-start,'end':right-start,'text':cue['text']})
    return rows


def write_srt(cues,path):
    rows=[]
    for cue in cues:
        if not cue.get('text') or not 0<=float(cue['start'])<float(cue['end']):continue
        # Strip subtitle/control markup, including ASS override syntax.
        text=html.unescape(re.sub(r'<[^>]*>|\{[^}]*\}','',str(cue['text']))).replace('\\','/').strip()
        rows.append(f"{len(rows)+1}\n{srt_time(cue['start'])} --> {srt_time(cue['end'])}\n{text}\n")
    Path(path).write_text('\n'.join(rows),encoding='utf-8')


def burn_captions(video,cues,split=False,caption_bar=False,bar_height=1280,canvas=None):
    video=Path(video);signature=digest([cues,'dialogue_bar',bar_height]) if caption_bar else digest(cues);manifest_path=video.with_suffix('.manifest.json')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    if canvas:signature=digest([signature,canvas,'landscape-caption-v1'])
    captions=video.with_suffix('.srt');write_srt(cues,captions)
    if manifest.get('caption_burn',{}).get('cues_hash')==signature:return
    clean=video.with_name(video.stem+'.clean.mp4')
    if not clean.exists():
        import shutil
        shutil.copyfile(video,clean)
    temporary=video.with_name(video.stem+'.captioned.partial.mp4')
    style='Fontname=Arial,Fontsize=22,Bold=1,Outline=2,Shadow=1,MarginV='+('180' if split else '50')
    subtitle_filter=f"subtitles={captions.name}:force_style='{style}'"
    if caption_bar:
        ass=video.with_suffix('.ass')
        header='[Script Info]\nScriptType: v4.00+\nPlayResX: 720\nPlayResY: 1280\nWrapStyle: 0\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,35,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,2,48,48,'+str(1280-bar_height+56)+',1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
        if canvas:
            width,height=canvas
            header=header.replace('PlayResX: 720',f'PlayResX: {width}').replace('PlayResY: 1280',f'PlayResY: {height}')
            header=header.replace('Default,Arial,35,',f'Default,Arial,{round(height*30/720)},')
            header=header.replace('2,48,48,'+str(1280-bar_height+56)+',1',f'2,80,80,{round(height*28/720)},1')
        def stamp(t):return f'{int(t//3600)}:{int(t//60)%60:02d}:{t%60:05.2f}'
        events=[]
        for cue in cues:
            safe=re.sub(r'<[^>]*>|\{[^}]*\}','',cue['text']).replace('\\','/').replace('\n',' ')
            events.append(f"Dialogue: 0,{stamp(cue['start'])},{stamp(cue['end'])},Default,,0,0,0,,{safe}")
        ass.write_text(header+'\n'.join(events),encoding='utf-8');subtitle_filter=f'ass={ass.name}'
    result=subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-i',str(clean),'-vf',subtitle_filter,
                           '-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-c:a','copy','-movflags','+faststart',str(temporary)],
                          cwd=video.parent,capture_output=True,timeout=300)
    if result.returncode:raise Held('caption_render','Subtitle burn-in failed; the clean export was retained for retry.')
    os.replace(temporary,video)
    manifest['caption_burn']={'cues_hash':signature,'video_sha256':file_hash(video),'alignment':'Exact-script locally aligned progressive subtitles' if caption_bar else 'Timed supplied/recognized cues, not invented word times','style':'dialogue_bar' if caption_bar else 'default'}
    write_json(manifest_path,manifest)
