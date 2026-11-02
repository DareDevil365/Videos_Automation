"""Trusted local motion graphics. Model JSON supplies text, never executable code."""
import math
from pathlib import Path
import subprocess

from PIL import Image,ImageDraw
from shorts_editor.graphics import text_box
from .core import Held

KINDS=('none','comparison','process','callout')
UI_TITLES=('Before and After','Situation','Task','Action','Result','Example','Interview Tip','Try this','Your turn')
BLOCK_SCHEMA={'type':'object','properties':{
    'kind':{'type':'string','enum':list(KINDS)},
    'title':{'type':'string'},'labels':{'type':'array','items':{'type':'string'}},
},'required':['kind','title','labels'],'additionalProperties':False}


def validate_block(block,unit,script=None):
    if not isinstance(block,dict) or set(block)!={'kind','title','labels'} or block.get('kind') not in KINDS:
        raise Held('scene_block','Unsupported motion block; use the declared JSON vocabulary.')
    title=block['title'];labels=block['labels'];kind=block['kind']
    if not isinstance(title,str) or len(title)>70 or not isinstance(labels,list):
        raise Held('scene_block','Motion block title or labels are invalid.')
    if kind=='none':
        if title or labels:raise Held('scene_block','An unused block must have empty title and labels.')
        return block
    lower,upper={'comparison':(2,2),'process':(2,4),'callout':(1,1)}[kind]
    if not lower<=len(labels)<=upper or any(not isinstance(s,str) or not s.strip() or len(s)>110 for s in labels):
        raise Held('scene_block','Motion block has too many, missing or overlong labels.')
    # Visual planner cannot introduce new facts, numbers, endorsements or claims.
    texts=[' '.join((u['text']+' '+u.get('onscreen','')).split()).casefold() for u in (script['units'] if script else [unit])]
    if any(not any(' '.join(s.split()).casefold() in text for text in texts) for s in labels):
        raise Held('scene_block_rewrite','Every graphic label must be an exact phrase from this script or its on-screen text.')
    if title and title not in UI_TITLES and not any(' '.join(title.split()).casefold() in text for text in texts):
        raise Held('scene_block_rewrite','Graphic title must quote the script or use a fixed UI heading.')
    return block


def block_frame(block,path,*,height=1280,progress=1):
    """High resolution masks/text, then downsample; no generated Python/TSX."""
    if type(height) is not int or not 720<=height<=1280:
        raise Held('scene_block_layout','Motion graphics need a main panel at least 720 pixels tall; use full-frame or increase top_fraction.')
    aa=2;w=720;h=height
    canvas=Image.new('RGB',(w*aa,h*aa),'#f3eee5');d=ImageDraw.Draw(canvas)
    def rect(box,fill,outline=None):
        d.rounded_rectangle(tuple(round(n*aa) for n in box),radius=20*aa,fill=fill,outline=outline,width=2*aa)
    def text(value,box,size=36,color='#20242c'):
        try:text_box(d,value,tuple(round(n*aa) for n in box),color,size*aa,True,'left',minimum=22*aa)
        except ValueError as exc:raise Held('scene_block_layout','The graphic label does not fit. Shorten it or choose a larger panel.') from exc
    d.rectangle((0,0,720*aa,12*aa),fill='#e15c37')
    text(block['title'],(48,50,624,140),44)
    labels=block['labels'];kind=block['kind'];top=max(210,round(h*.25));bottom=h-245
    visible=max(1,min(len(labels),math.ceil(progress*len(labels))))
    for i,label in enumerate(labels[:visible]):
        if kind=='comparison':
            gap=18;cell=(bottom-top-gap)//2;y=top+i*(cell+gap)
            rect((40,y,680,y+cell),'#fffdf8', '#d3cabc')
            text('BEFORE' if i==0 else 'AFTER',(64,y+20,580,35),24,'#a34c32' if i==0 else '#287765')
            text(label,(64,y+75,580,max(75,cell-95)),40)
        elif kind=='process':
            cell=(bottom-top)//len(labels);y=top+i*cell
            rect((40,y+4,680,y+cell-8),'#fffdf8')
            text(str(i+1).zfill(2),(62,y+25,80,55),30,'#a34c32')
            text(label,(156,y+20,490,max(58,cell-30)),36)
            if i: d.line((82*aa,(y-16)*aa,82*aa,(y+4)*aa),fill='#a34c32',width=3*aa)
        else:
            rect((40,top,680,bottom),'#20242c')
            text(label,(72,top+45,576,max(100,bottom-top-90)),48,'#fffdf8')
    # Narration lives in a dedicated, quiet caption area.
    rect((24,h-185,696,h-28),'#171b22')
    canvas.resize((w,h),Image.Resampling.LANCZOS).save(path)


def render_block(block,duration,path,*,height=1280):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    # Four timed reveals at most, streamed as still plates to FFmpeg.
    count=len(block['labels']);plates=[]
    for i in range(count):
        plate=path.with_name(path.stem+f'-step-{i+1}.png')
        block_frame(block,plate,height=height,progress=(i+1)/count);plates.append(plate)
    args=['ffmpeg','-v','error','-nostdin','-y']
    # First reveal immediately; following labels appear within the first 65%.
    lengths=[duration*.65/count]*(count-1)+[duration-duration*.65/count*(count-1)]
    for plate,length in zip(plates,lengths):args+=['-loop','1','-framerate','30','-t',str(length),'-i',str(plate)]
    filters=';'.join(f'[{i}:v]fps=30,setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v{i}]' for i in range(count))
    filters+=';'+''.join(f'[v{i}]' for i in range(count))+f'concat=n={count}:v=1:a=0[out]'
    args+=['-filter_complex_threads','1','-filter_complex',filters,'-map','[out]','-t',str(duration),'-an',
           '-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p',str(path)]
    result=subprocess.run(args,capture_output=True,timeout=120)
    if result.returncode:raise Held('scene_block_render','The local motion scene failed; input plates were retained.')
    return {'kind':block['kind'],'plates':[str(p) for p in plates]}
