"""Deterministic FFmpeg engine. No network, AI calls, or publishing side effects."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time

from PIL import Image, ImageDraw

from .graphics import panel_rects, cue_ranges, paint_overlay, text_box
from .models import validate_project, dimensions, duration, ValidationError, COMPOSITION_IDS
from .store import probe, write_json


class RenderCancelled(Exception):
    pass


def capabilities():
    return {"ffmpeg": bool(shutil.which("ffmpeg")), "ffprobe": bool(shutil.which("ffprobe"))}


def run_ffmpeg(arguments, work, stage, seconds, progress=None, cancel=None):
    log=Path(work)/(stage+".log"); meter=Path(work)/(stage+".progress")
    command=["ffmpeg","-hide_banner","-nostdin","-y","-loglevel","error","-progress",str(meter),"-nostats",*arguments]
    with log.open("wb") as errors:
        process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=errors)
        try:
            while process.poll() is None:
                if cancel and cancel.is_set(): raise RenderCancelled("Render cancelled.")
                if meter.exists() and progress:
                    values={line.split("=",1)[0]:line.split("=",1)[1] for line in meter.read_text(errors="replace").splitlines() if "=" in line}
                    try:micros=float(values.get("out_time_us","0") or 0)
                    except ValueError:micros=0 # FFmpeg may report N/A while initializing a source decoder.
                    progress(min(.99,max(0,micros/1_000_000/max(.1,seconds))))
                time.sleep(.15)
        except BaseException:
            process.terminate()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
            raise
    if process.returncode:
        details=log.read_text(encoding="utf-8",errors="replace")[-2400:]
        raise RuntimeError(f"FFmpeg failed during {stage} (exit {process.returncode}): {details or 'No stderr; inspect the saved render work and input media.'}")
    if progress: progress(1)


def base_frame(project,scene,size,path):
    w,h=size; img=Image.new("RGB",size,project["background"]); draw=ImageDraw.Draw(img)
    for key,_,(x,y,pw,ph) in panel_rects(project,scene,size):
        if scene[key]: continue
        draw.rectangle((x,y,x+pw,y+ph),fill="#1b2528")
        for offset in range(-ph,pw,80):
            draw.line((x+max(0,offset),y+max(0,-offset),x+min(pw,offset+ph),y+min(ph,pw-offset)),fill="#253236",width=1)
        text_box(draw,"ADD YOUR MEDIA",(x+pw*.12,y+ph*.43,pw*.76,ph*.1),"#6b858a",max(14,int(w*.025)),True,"center")
    img.save(path)


def scene_inputs(project,scene,index,total,assets,work,size,preview_time=None):
    if project["format"] in COMPOSITION_IDS:
        from .composition import scene_inputs as compose
        return compose(project,scene,index,assets,work,size,preview_time)
    w,h=size; fps=project["fps"]; args=[]; filters=[]; input_index=0
    base=Path(work)/f"scene-{index}-base.png"; base_frame(project,scene,size,base)
    args += ["-loop","1","-framerate",str(fps),"-i",str(base)]
    current="0:v"; input_index=1; source_audio=None
    for panel_index,(key,offset_key,(x,y,pw,ph)) in enumerate(panel_rects(project,scene,size)):
        if not scene[key]: continue
        asset=assets[scene[key]]
        if asset["kind"]=="image":
            args += ["-loop","1","-framerate",str(fps),"-i",str(asset["path"])]
        else:
            seek=scene[offset_key]
            if preview_time is not None: seek=(seek+preview_time)%asset["duration"]
            args += ["-stream_loop","-1","-ss",str(round(seek,4)),"-i",str(asset["path"])]
        label=f"panel{panel_index}"
        if scene["fit"]=="contain":
            scaling=f"scale={pw}:{ph}:force_original_aspect_ratio=decrease:force_divisible_by=2,pad={pw}:{ph}:(ow-iw)/2:(oh-ih)/2:color={project['background'].replace('#','0x')}"
        else:
            scaling=f"scale={pw}:{ph}:force_original_aspect_ratio=increase:force_divisible_by=2,crop={pw}:{ph}:(iw-ow)*{scene['focus_x']}:(ih-oh)*{scene['focus_y']}"
        filters.append(f"[{input_index}:v]setpts=PTS-STARTPTS,{scaling},setsar=1,fps={fps}[{label}]")
        new=f"under{panel_index}"
        filters.append(f"[{current}][{label}]overlay={x}:{y}:eof_action=repeat:shortest=1[{new}]")
        current=new
        if key=="media" and scene["source_audio"] and asset["has_audio"]:
            source_audio=input_index
        input_index+=1
    ranges=cue_ranges(project,scene)
    if preview_time is not None:
        ranges=[next((r for r in ranges if r[0]<=preview_time<r[1]),ranges[-1])]
    for variant,(start,end,cue) in enumerate(ranges):
        overlay=Path(work)/f"scene-{index}-overlay-{variant}.png"
        paint_overlay(project,scene,index,total,size,cue).save(overlay)
        args += ["-loop","1","-framerate",str(fps),"-i",str(overlay)]
        new=f"over{variant}"
        enable="" if preview_time is not None else f":enable='gte(t,{start})*lt(t,{end})'"
        filters.append(f"[{current}][{input_index}:v]overlay=0:0:eof_action=repeat:shortest=1{enable}[{new}]")
        current=new; input_index+=1
    filters.append(f"[{current}]format=yuv420p,setsar=1[v]")
    return args,filters,source_audio


def preview(project,store,index=0,at=None):
    project=validate_project(project)
    if not 0<=index<len(project["scenes"]): raise ValidationError("Scene does not exist.")
    assets=store.resolve_project_assets(project); scene=project["scenes"][index]
    at=scene["duration"]*.7 if at is None else max(0,min(float(at),scene["duration"]-.001))
    # Small preview uses the exact same layout function and filters as export.
    size=(360,640)
    key=hashlib.sha256(json.dumps([project,index,round(at,2)],sort_keys=True).encode()).hexdigest()
    output=store.root/"previews"/(key+".png")
    if output.exists(): return output
    work=store.root/"previews"/key; work.mkdir(exist_ok=True)
    args,filters,_=scene_inputs(project,scene,index,len(project["scenes"]),assets,work,size,at)
    run_ffmpeg([*args,"-filter_complex_threads","1","-filter_complex",";".join(filters),
                "-map","[v]","-frames:v","1","-an","-update","1",str(output)],work,"preview",1)
    return output


def srt_time(seconds):
    millis=round(seconds*1000); hours,millis=divmod(millis,3_600_000); minutes,millis=divmod(millis,60_000); sec,millis=divmod(millis,1000)
    return f"{hours:02d}:{minutes:02d}:{sec:02d},{millis:03d}"


def export_captions(project,path):
    rows=[]; elapsed=0
    for scene in project["scenes"]:
        if project["format"] in COMPOSITION_IDS and not scene["text"]:
            elapsed+=scene["duration"]; continue
        chunks=[line.strip() for line in scene["text"].splitlines() if line.strip()] or [scene["title"]]
        for start,end,cue in cue_ranges(project,scene):
            if project["format"]=="chat":
                msg=scene["messages"][cue] if scene["messages"] else {"name":"", "text":scene["title"]}
                value=f"{msg['name']}: {msg['text']}".strip(": ")
            elif project["format"]=="punchline": value=scene["title"] if cue==0 else scene["text"]
            elif project["format"] in ("list","explainer"): value=scene["text"] or scene["title"]
            else: value=chunks[min(cue,len(chunks)-1)]
            rows.append(f"{len(rows)+1}\n{srt_time(elapsed+start)} --> {srt_time(elapsed+end)}\n{value}\n")
        elapsed+=scene["duration"]
    Path(path).write_text("\n".join(rows),encoding="utf-8")


def render_project(project,store,output,progress=None,cancel=None):
    """Public integration interface: a validated project, asset Store and new output path."""
    p=validate_project(project); output=Path(output).resolve()
    if output.exists(): raise ValidationError("Output already exists. Choose a new filename.")
    if not all(capabilities().values()): raise RuntimeError("Install FFmpeg and ffprobe and add both to PATH.")
    assets=store.resolve_project_assets(p); seconds=duration(p)
    from .composition import require_inputs
    require_inputs(p)
    if p["narration"] and assets[p["narration"]]["duration"]>seconds+.15:
        raise ValidationError("Narration is longer than the video. Extend scene durations before exporting.")
    output.parent.mkdir(parents=True,exist_ok=True)
    work=output.parent/(output.stem+"-work"); work.mkdir(exist_ok=True)
    w,h=dimensions(p); segments=[]
    def report(value,message):
        if progress: progress(round(value,4),message)
    for i,scene in enumerate(p["scenes"]):
        if cancel and cancel.is_set(): raise RenderCancelled()
        report(.85*i/len(p["scenes"]),f"Rendering scene {i+1} of {len(p['scenes'])}")
        args,filters,audio=scene_inputs(p,scene,i,len(p["scenes"]),assets,work,(w,h))
        if audio is not None:
            filters.append(f"[{audio}:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={p['source_volume']},apad,atrim=duration={scene['duration']}[a]")
        else: filters.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={scene['duration']}[a]")
        segment=work/f"segment-{i:03d}.mp4"; segments.append(segment)
        run_ffmpeg([*args,"-filter_complex_threads","1","-filter_complex",";".join(filters),"-map","[v]","-map","[a]",
                    "-t",str(scene["duration"]),"-c:v","libx264","-preset","veryfast","-crf","20","-threads","2",
                    "-r",str(p["fps"]),"-video_track_timescale","90000","-c:a","aac","-ar","48000","-ac","2",str(segment)],
                   work,f"scene-{i}",scene["duration"],lambda v,i=i: report(.85*(i+v)/len(p["scenes"]),f"Rendering scene {i+1} of {len(p['scenes'])}"),cancel)
    # The concat file contains only our own safe generated basenames.
    concat=work/"concat.txt"; concat.write_text("\n".join(f"file '{s.name}'" for s in segments),encoding="utf-8")
    joined=work/"joined.mp4"
    run_ffmpeg(["-f","concat","-safe","1","-i",str(concat),"-c","copy",str(joined)],work,"join",seconds,
               lambda v: report(.85+.03*v,"Assembling scenes"),cancel)
    partial=work/"final.partial.mp4"; args=["-i",str(joined)]; filters=[]; audio_labels=["[0:a]"]; idx=1
    if p["narration"]:
        args += ["-i",str(assets[p["narration"]]["path"])]
        filters.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration={seconds}[voice]")
        audio_labels.append("[voice]"); idx+=1
    if p["music"]:
        args += ["-stream_loop","-1","-i",str(assets[p["music"]]["path"])]
        fade=min(1,seconds/4)
        filters.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={p['music_volume']},afade=t=in:d={fade},afade=t=out:st={seconds-fade}:d={fade},atrim=duration={seconds}[music]")
        audio_labels.append("[music]")
    filters.append("".join(audio_labels)+f"amix=inputs={len(audio_labels)}:duration=first:normalize=0,alimiter=limit=0.95:latency=1[a]")
    run_ffmpeg([*args,"-filter_complex_threads","1","-filter_complex",";".join(filters),"-map","0:v","-map","[a]",
                "-c:v","copy","-c:a","aac","-ar","48000","-ac","2","-t",str(seconds),"-movflags","+faststart",str(partial)],
               work,"audio",seconds,lambda v: report(.88+.08*v,"Mixing audio"),cancel)
    info=probe(partial); video=next(s for s in info["streams"] if s["codec_type"]=="video")
    actual=float(info["format"]["duration"])
    if (video["width"],video["height"])!=(w,h) or abs(actual-seconds)>.25:
        raise RuntimeError("Export did not match the requested dimensions/duration. Inspect the render logs.")
    if cancel and cancel.is_set(): raise RenderCancelled()
    cover=output.with_suffix(".png")
    run_ffmpeg(["-ss",str(p["scenes"][0]["duration"]*.7),"-i",str(partial),"-frames:v","1","-update","1",str(cover)],work,"cover",1,cancel=cancel)
    captions=output.with_suffix(".srt"); export_captions(p,captions)
    write_json(output.with_suffix(".project.json"),p)
    manifest={"created_at":datetime.now(timezone.utc).isoformat(),"project":p,"duration":actual,"width":w,"height":h,
              "audio":any(s["codec_type"]=="audio" for s in info["streams"]),
              "assets":[{k:v for k,v in asset.items() if k!="path"} for asset in assets.values()],
              "notes":["Media rights and factual claims are not certified by the renderer.",
                       "No AI narration generated: narration is an optional imported file.",
                       "Timed captions follow scene cues, not forced word alignment."]}
    write_json(output.with_suffix(".manifest.json"),manifest)
    os.replace(partial,output)
    report(1,"Export ready")
    return manifest
