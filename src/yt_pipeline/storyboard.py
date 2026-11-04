"""Bounded beat-to-shot mapping and original procedural mystery illustrations.

The model chooses scene tags and literal details, never executable drawing code.
These are visibly illustrated fiction, not claimed photographic evidence.
"""
from pathlib import Path
import math
import re
import subprocess

from PIL import Image,ImageDraw
from shorts_editor.graphics import text_box
from .core import Held


SCENES=('elevator','phone','hallway','door','stairwell','security')


def prop_data(scene,detail,caption,spoken=''):
    """Resolve visible content from the story, never print visual instructions.

    visual_query describes the drawing. Spoken/onscreen text supplies message
    content. A generic notification must not prematurely reveal a later twist.
    """
    content=' '.join((spoken,caption,detail)).lower()
    words={'zero':'0','one':'1','two':'2','three':'3','four':'4','five':'5','six':'6','seven':'7','eight':'8','nine':'9','ten':'10','thirteen':'13'}
    floor=''
    negative=re.search(r'\b(?:minus|negative)\s+(\d{1,2}|'+ '|'.join(words)+r')\b',content)
    basement=re.search(r'\bbasement(?:\s+level)?\s+(\d{1,2}|'+ '|'.join(words)+r')\b',content)
    number=re.search(r'(?<!\w)-?\d{1,3}(?!\w)',content)
    if negative:floor='-'+words.get(negative[1],negative[1])
    elif basement:floor='B'+words.get(basement[1],basement[1])
    elif number:floor=number[0]
    message='New message'
    actual=re.search(r'\b(?:message|text)\s+(?:said|read|reads|says)\s*[:\-]?\s*(.+)',spoken,re.I)
    if actual:message=actual[1].strip(' .\"\'')
    elif scene=='phone' and not re.search(r'\b(buzz|notification|incoming|received|arrived)\b',spoken+' '+caption,re.I):message=caption
    return {'floor':floor,'phone_message':message,'open_elevator':scene=='door' and bool(re.search(r'\b(elevator|metal)\b',detail,re.I)) and bool(re.search(r'\b(open|opening|opened)\b',detail+' '+spoken,re.I))}


def story_specs(script,request):
    value=request.get('story_visuals')
    if not value:return None
    ids=[u['id'] for u in script['units']]
    if value=='from_script':
        value={}
        for unit in script['units']:
            match=re.fullmatch(r'\s*('+ '|'.join(SCENES)+r')\s*:\s*(.{1,180})\s*',unit.get('visual_query',''),re.I)
            if not match:raise Held('storyboard_scene','Every story unit needs a supported scene tag and literal detail in visual_query')
            value[unit['id']]={'scene':match[1].lower(),'detail':match[2].strip()}
    if not isinstance(value,dict) or set(value)!=set(ids):
        raise Held('storyboard_units','The story storyboard must cover exactly the script unit IDs')
    result={}
    for uid in ids:
        row=value[uid]
        if not isinstance(row,dict) or row.get('scene') not in SCENES or not isinstance(row.get('detail'),str) or not 1<=len(row['detail'])<=180:
            raise Held('storyboard_scene','Storyboards use a supported scene and a bounded literal detail')
        result[uid]={'scene':row['scene'],'detail':row['detail']}
    return result


def story_poster(scene,detail,caption,path,index=0,spoken=''):
    """Draw an original noir-style illustration for one model-selected story beat."""
    if scene not in SCENES:raise Held('storyboard_scene','Unknown mystery scene')
    im=Image.new('RGB',(720,1280));d=ImageDraw.Draw(im)
    # Literal prop descriptions remain archived in full, but overly long labels
    # should not consume the whole illustration or crash the text box.
    props=prop_data(scene,detail,caption,spoken)
    for y in range(1280):
        shade=int(10+12*(1-y/1280));d.line((0,y,720,y),fill=(shade,shade+4,shade+9))
    amber='#d7ad73';muted='#6d7c88';red='#ee685e';edge='#405263';black='#090d12'
    if scene=='elevator':
        d.rectangle((73,190,647,1100),fill='#18232e',outline=edge,width=5)
        d.rectangle((105,245,355,1060),fill='#293642');d.rectangle((365,245,615,1060),fill='#202d38')
        d.line((360,245,360,1060),fill=black,width=8)
        d.rectangle((250,115,470,200),fill=black,outline=muted,width=2)
        text_box(d,props['floor'] or '•',(265,122,190,64),red,52,True,'center')
        for y in (550,590,630):d.ellipse((625,y,639,y+14),fill=amber)
        if 'button' in detail.lower() and props['floor']:
            d.ellipse((515,740,585,810),fill=amber,outline='#fff1cf',width=4)
            text_box(d,props['floor'],(525,758,50,40),black,25,True,'center')
    elif scene=='phone':
        d.polygon([(0,500),(360,330),(720,500),(720,1080),(0,1080)],fill='#17212b')
        d.rounded_rectangle((163,205,557,1080),radius=45,fill='#020407',outline='#52606c',width=5)
        d.rounded_rectangle((181,238,539,1040),radius=23,fill='#18242d')
        d.rounded_rectangle((292,249,428,270),radius=10,fill='#05080c')
        text_box(d,'INCOMING MESSAGE',(210,340,300,65),muted,23,True,'center')
        d.rounded_rectangle((206,455,514,825),radius=18,fill='#273848',outline='#506375',width=2)
        text_box(d,props['phone_message'],(229,487,260,305),'#f1eee7',35,True,'center',minimum=23)
        d.ellipse((325,920,395,990),outline=red,width=4)
    elif scene=='hallway':
        d.polygon([(0,1080),(285,550),(435,550),(720,1080)],fill='#26313b')
        d.polygon([(0,180),(285,550),(285,1280),(0,1280)],fill='#17232d')
        d.polygon([(720,180),(435,550),(435,1280),(720,1280)],fill='#131e27')
        for i in range(3):
            x=35+75*i;top=260+100*i;bottom=1100-100*i
            d.polygon([(x,top),(x+60,top+60),(x+60,bottom-60),(x,bottom)],fill=black,outline=edge,width=3)
            d.polygon([(720-x,top),(660-x,top+60),(660-x,bottom-60),(720-x,bottom)],fill=black,outline=edge,width=3)
        d.rectangle((300,440,420,705),fill='#071016',outline=amber,width=3)
        d.line((285,1100,435,1100),fill=amber,width=2)
    elif scene=='door':
        d.rectangle((73,150,647,1110),fill='#18232e',outline=edge,width=7)
        if props['open_elevator']:
            d.rectangle((112,185,608,1080),fill='#03070c')
            d.polygon([(210,1080),(330,580),(390,580),(510,1080)],fill='#14202a')
            d.rectangle((112,185,205,1080),fill='#35444e',outline='#71818d',width=3)
            d.rectangle((515,185,608,1080),fill='#293943',outline='#71818d',width=3)
            d.line((205,185,205,1080),fill=amber,width=3);d.line((515,185,515,1080),fill=amber,width=3)
        else:
            d.rectangle((138,185,582,1080),fill='#24313a',outline='#364853',width=3)
            d.ellipse((348,390,372,414),fill=black,outline=amber,width=3)
            d.rounded_rectangle((483,650,510,810),radius=8,fill='#9b8567');d.line((498,695,555,695),fill=amber,width=11)
            d.line((138,1080,582,1080),fill=red,width=5)
    elif scene=='stairwell':
        d.polygon([(0,200),(720,60),(720,1150),(0,1250)],fill='#1a2732')
        points=[]
        for i in range(10):
            y=1000-i*53;x=140+i*35
            d.polygon([(x,y),(x+260,y-26),(x+260,y+14),(x,y+40)],fill='#344451',outline=edge,width=3)
            points.append((x-25,y-100))
        d.line(points,fill=muted,width=10)
        d.line((100,280,600,280),fill=amber,width=2)
    else:
        d.rounded_rectangle((45,230,675,920),radius=20,fill='#020609',outline=edge,width=5)
        for j in range(4):
            x=65+(j%2)*302;y=255+(j//2)*320
            d.rectangle((x,y,x+285,y+300),fill='#142a30',outline='#3a575c',width=2)
            d.polygon([(x+10,y+280),(x+115,y+80),(x+170,y+80),(x+275,y+280)],outline='#769b98',fill='#17383a')
            d.line((x+142,y+100,x+142,y+270),fill='#436a6c',width=3)
            text_box(d,f'CAM {j+1:02d}',(x+12,y+12,230,28),'#a6c4bb',19,True)
        text_box(d,'LIVE',(85,970,550,40),red,25,True,'center')
    if re.search(r'\b(figure|person|man|woman|shadow|someone|silhouette|reflection)\b',detail,re.I):
        # An original simple silhouette, only when the selected beat calls for one.
        x,y,size=(510,735,60) if scene=='security' else (360,655,95)
        d.ellipse((x-size*.23,y-size,x+size*.23,y-size*.52),fill='#05080b',outline='#536272',width=2)
        d.polygon([(x-size*.22,y-size*.48),(x-size*.43,y+size*.45),(x+size*.43,y+size*.45),(x+size*.22,y-size*.48)],fill='#05080b',outline='#536272')
    # A compact bottom caption is separate from prop detail, leaving the image dominant.
    d.rounded_rectangle((30,1115,690,1250),radius=16,fill='#070b10',outline='#28343f',width=2)
    text_box(d,caption,(53,1137,614,92),'#ffffff',34,True,'center',minimum=23)
    # Original graphic grain, deterministic and subtle; never replace a required real asset.
    for x in range(index%7,720,47):
        for y in range(85,1100,71):d.point((x,y),fill='#39414a')
    im.save(path)
    return {'scene':scene,'detail':detail,'props':props,'caption':caption,'width':720,'height':1280,'illustrated_fiction':True}


def mystery_scene(script,index,duration,folder,spec):
    folder=Path(folder);uid=script['units'][index]['id'];poster=folder/(uid+'-story.png')
    story_poster(spec['scene'],spec['detail'],script['units'][index]['onscreen'],poster,index,script['units'][index]['text'])
    output=folder/(uid+'-story.mp4');frames=math.ceil(duration*30)
    # Slow optical push, not extra visual clutter; the scene changes when the story beat does.
    vf=f"scale=1440:2560,zoompan=z='min(1.0+on*0.00045,1.065)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s=720x1280:fps=30"
    result=subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-i',str(poster),'-vf',vf,'-t',str(duration),'-an',
        '-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p',str(output)],capture_output=True,timeout=120)
    if result.returncode:raise Held('story_scene_render','Mystery scene render failed; source illustration was preserved')
    return output
