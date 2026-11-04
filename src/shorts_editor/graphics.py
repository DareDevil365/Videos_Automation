"""Original graphics and timed overlays shared by preview and video rendering."""
from pathlib import Path
import os
import re

from PIL import Image, ImageDraw, ImageFont


def font(size, bold=False):
    candidates = [os.environ.get("SHORTS_EDITOR_FONT", ""),
                  str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / ("arialbd.ttf" if bold else "arial.ttf")),
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file(): return ImageFont.truetype(candidate, size=max(1,int(size)))
    return ImageFont.load_default(size=max(1,int(size)))


def wrapped(draw, text, fnt, width):
    lines = []
    for paragraph in text.splitlines() or [""]:
        line = ""
        for word in paragraph.split():
            if draw.textlength(word, font=fnt) > width:
                if line: lines.append(line); line = ""
                fragment = ""
                for char in word:
                    if fragment and draw.textlength(fragment+char,font=fnt)>width:
                        lines.append(fragment); fragment=""
                    fragment += char
                line = fragment
            elif line and draw.textlength(line+" "+word,font=fnt)>width:
                lines.append(line); line=word
            else: line = (line+" "+word).strip()
        if line: lines.append(line)
    return lines


def text_box(draw, value, rect, color="#f7f8f5", size=40, bold=False, align="left", minimum=12):
    x,y,w,h = rect
    for point in range(max(minimum,int(size)),minimum-1,-1):
        fnt=font(point,bold); lines=wrapped(draw,value,fnt,w); step=point*1.24
        if len(lines)*step <= h: break
    if len(lines)*step > h:
        raise ValueError("There is too much text to fit this card. Shorten it or split it into scenes.")
    for line in lines:
        tx = x + (w-draw.textlength(line,font=fnt))/2 if align=="center" else x
        draw.text((tx,y),line,font=fnt,fill=color,stroke_width=0)
        y += step
    return len(lines)*step


def panel_rects(project, scene, size):
    w,h=size; kind=project["format"]
    if kind=="chat": return []
    if kind=="split":
        cut=int(h*project["split_ratio"])//2*2
        refs=[("media", "media_start"), ("secondary_media", "secondary_start")]
        if project["swap_panels"]: refs.reverse()
        return [(refs[0][0],refs[0][1],(0,0,w,cut-4)),(refs[1][0],refs[1][1],(0,cut+4,w,h-cut-4))]
    if kind=="list": return [("media","media_start",(int(w*.065),int(h*.17),int(w*.87)//2*2,int(h*.56)//2*2))]
    if kind=="explainer": return [("media","media_start",(int(w*.065),int(h*.32),int(w*.87)//2*2,int(h*.37)//2*2))]
    return [("media","media_start",(0,0,w,h))]


def cue_ranges(project,scene):
    d=scene["duration"]
    if project["format"]=="chat":
        count=max(1,len(scene["messages"]))
        return [(i*d/count,(i+1)*d/count,i) for i in range(count)]
    if project["format"]=="punchline": return [(0,d*.55,0),(d*.55,d,1)]
    if project["format"] in ("list","explainer"): return [(0,d,0)]
    chunks=[s.strip() for s in scene["text"].splitlines() if s.strip()] or [""]
    return [(i*d/len(chunks),(i+1)*d/len(chunks),i) for i in range(len(chunks))]


def paint_overlay(project,scene,index,total,size,cue=0):
    w,h=size; scale=w/720; fs=project["font_scale"]; accent=project["accent"]
    image=Image.new("RGBA",size,(0,0,0,0)); draw=ImageDraw.Draw(image)
    m=int(w*.065); kind=project["format"]
    def box(rect,fill,radius=18): draw.rounded_rectangle(rect,radius=int(radius*scale),fill=fill)
    def txt(value,rect,sz=38,bold=False,color="#f7f8f5",align="left"):
        return text_box(draw,value,rect,color,sz*scale*fs,bold,align,minimum=max(4,int(12*scale)))
    if kind=="chat":
        draw.rectangle((0,0,w,h),fill=project["background"])
        box((m,int(h*.07),w-m,int(h*.19)),"#1b2527")
        txt(scene["title"],(m+20*scale,h*.087,w-2*m-40*scale,h*.065),36,True)
        y=h*.225
        for msg in scene["messages"][:cue+1]:
            max_width=w*.75; bubble_width=max_width
            lines=wrapped(draw,msg["text"],font(27*scale*fs),bubble_width-36*scale)
            bh=38*scale+len(lines)*34*scale*fs
            if y+bh>h*.87: raise ValueError("Messages exceed the safe frame. Use fewer or shorter messages in this scene.")
            x=m if msg["side"]=="left" else w-m-bubble_width
            right=msg["side"]=="right"
            box((x,y,x+bubble_width,y+bh),accent if right else "#263134")
            txt(msg["name"],(x+18*scale,y+9*scale,bubble_width-36*scale,24*scale),15,True,"#182310" if right else accent)
            txt(msg["text"],(x+18*scale,y+35*scale,bubble_width-36*scale,bh-38*scale),27,color="#182310" if right else "#f7f8f5")
            y+=bh+19*scale
        txt(f"{index+1:02d} / {total:02d}",(m,h*.91,w-2*m,h*.025),17,color="#94a5a6")
        return image
    if kind in ("story","split","punchline"):
        box((m,h*.075,w-m,h*.23),(12,17,18,224))
        draw.rounded_rectangle((m,h*.075,m+6*scale,h*.23),radius=3*scale,fill=accent)
        txt(scene["title"],(m+24*scale,h*.092,w-2*m-45*scale,h*.12),43,True)
        chunks=[s.strip() for s in scene["text"].splitlines() if s.strip()] or [""]
        caption=scene["text"] if kind=="punchline" else chunks[min(cue,len(chunks)-1)]
        show=kind!="punchline" or cue>0
        if show and caption:
            top=h*.46 if kind=="split" else h*.65
            box((m,top,w-m,top+h*.17),(12,17,18,235))
            txt(caption,(m+24*scale,top+24*scale,w-2*m-48*scale,h*.125),37,True,align="center")
        txt(f"{index+1:02d}  /  {total:02d}",(m,h*.9,w-2*m,h*.03),17,color=accent)
    elif kind=="list":
        txt(scene["title"],(m,h*.075,w-2*m,h*.075),34,True,color=accent)
        box((m-3,h*.75,w-m+3,h*.89),"#1c2729")
        txt(scene["text"],(m+22*scale,h*.77,w-2*m-44*scale,h*.1),37,True)
        txt(f"{index+1:02d}  /  {total:02d}",(m,h*.92,w-2*m,h*.025),17,color="#94a5a6")
    else:
        txt("ONE USEFUL IDEA",(m,h*.065,w-2*m,h*.025),18,True,color=accent)
        txt(scene["title"],(m,h*.12,w-2*m,h*.15),53,True)
        draw.rectangle((m,h*.29,m+w*.13,h*.294),fill=accent)
        txt(scene["text"],(m,h*.735,w-2*m,h*.14),36)
        txt(f"{index+1:02d}  /  {total:02d}",(m,h*.92,w-2*m,h*.025),17,color="#94a5a6")
    return image
