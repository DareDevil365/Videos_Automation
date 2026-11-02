"""Create original local fixtures. Nothing is downloaded from a creator or game."""
import math
from pathlib import Path
import struct
import subprocess
import wave

from PIL import Image, ImageDraw

from .graphics import font, text_box
from .models import FORMATS, template_project
from .store import write_json


def create_demo(store):
    source=store.root/"demo-source"; source.mkdir(exist_ok=True)
    art=[]
    names=["MIDNIGHT\nORBIT", "THE LAST\nMESSAGE", "SIDE\nQUEST", "OPEN\nHORIZON", "SMALL\nWONDERS"]
    colors=[("#172a36","#98e8c1"),("#342944","#f3a9c6"),("#30351b","#d3ed7b"),("#1b3146","#8bc7f5"),("#43301c","#ffd78e")]
    for i,(name,(background,accent)) in enumerate(zip(names,colors)):
        asset_id=f"demo_art_{i}"
        try: store.asset(asset_id); art.append(asset_id); continue
        except ValueError: pass
        img=Image.new("RGB",(600,900),background); d=ImageDraw.Draw(img)
        for ring in range(7,0,-1):
            r=ring*45; d.ellipse((300-r,420-r,300+r,420+r),outline=accent,width=2)
        d.ellipse((210+i*17,300,345+i*17,435),fill=accent)
        d.polygon([(0,680),(190,470),(360,690),(470,540),(600,680),(600,900),(0,900)],fill="#111c23")
        text_box(d,"ORIGINAL DEMO ART",(45,50,510,30),accent,19,True)
        text_box(d,name,(45,690,510,145),"#f7f8f5",65,True)
        path=source/f"art-{i}.png"; img.save(path)
        store.register(path,f"Demo art — {name.replace(chr(10),' ')}",asset_id,demo=True); art.append(asset_id)
    motion="demo_motion"
    try: store.asset(motion)
    except ValueError:
        path=source/"original-obstacle-animation.mp4"
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pixel_format","rgb24","-video_size","360x640","-framerate","24","-i","pipe:0",
             "-an","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-movflags","+faststart",str(path)]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            for frame in range(72):
                t=frame/24; image=Image.new("RGB",(360,640),"#111e25"); d=ImageDraw.Draw(image)
                d.polygon([(125,210),(235,210),(360,640),(0,640)],fill="#223d44")
                for j in range(8):
                    z=((j/8+t*.22)%1)**2
                    y=210+z*430; half=55+z*125
                    d.line((180-half,y,180+half,y),fill="#83c8bc",width=2)
                for j in range(5):
                    x=25+j*80; d.line((180+(x-180)*.3,210,x,640),fill="#365e61",width=1)
                bx=180+math.sin(t*2.1)*60; by=490-abs(math.sin(t*3))*80
                d.ellipse((bx-24,by-24,bx+24,by+24),fill="#c3f576")
                d.ellipse((bx-9,by-12,bx+1,by-2),fill="#ecffcb")
                text_box(d,"ORIGINAL MOTION STUDY",(20,85,320,30),"#a5c5c6",13,True,"center")
                proc.stdin.write(image.tobytes())
            proc.stdin.close(); errors=proc.stderr.read(); code=proc.wait(timeout=30)
            if code: raise RuntimeError(errors.decode(errors="replace"))
        except BaseException:
            proc.kill(); proc.wait(); raise
        store.register(path,"Demo obstacle animation (not a game recording)",motion,demo=True)
    music="demo_music"
    try: store.asset(music)
    except ValueError:
        path=source/"original-soft-pulse.wav"; sample_rate=48000
        samples=bytearray()
        for i in range(sample_rate*8):
            t=i/sample_rate; beat=t%1
            amp=math.sin(math.pi*min(1,beat/.8))**2 if beat<.8 else 0
            frequency=[220,261.63,329.63,293.66][int(t)%4]
            value=int(3500*amp*(math.sin(2*math.pi*frequency*t)+.25*math.sin(4*math.pi*frequency*t)))
            samples.extend(struct.pack("<h",value))
        with wave.open(str(path),"wb") as audio:
            audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(sample_rate); audio.writeframes(samples)
        store.register(path,"Demo soft pulse (original synthesized audio)",music,demo=True)
    result={"art":art,"motion":motion,"music":music}
    write_json(store.root/"demo.json",result)
    examples=store.root/"demo-projects"; examples.mkdir(exist_ok=True)
    for item in FORMATS:
        write_json(examples/(item["id"]+".json"),template_project(item["id"],result))
    return result
