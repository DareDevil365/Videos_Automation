"""Original full-screen fictional server chat, with timed message/scroll motion."""
from hashlib import sha256
import math
from pathlib import Path
import subprocess

from PIL import Image,ImageDraw
from shorts_editor.graphics import font,wrapped,text_box
from .core import Held


def speaker_color(name,used=()):
    colors=['#a7baff','#77dfb7','#ffb981','#efa7ee','#ffe08d']
    initial=int(sha256(name.encode()).hexdigest()[:8],16)%len(colors)
    return next((colors[(initial+i)%len(colors)] for i in range(len(colors)) if colors[(initial+i)%len(colors)] not in used),colors[initial])


def message_layout(script,height=1280):
    draw=ImageDraw.Draw(Image.new('RGB',(720,height)));rows=[];y=0
    for unit in script['units']:
        text=unit['text']
        lines=wrapped(draw,text,font(34),530)
        if len(lines)>4:raise Held('chat_message_length','A server-chat message needs at most four readable lines; shorten it rather than shrinking its text.')
        row_height=55+max(1,len(lines))*44+26
        rows.append({'id':unit['id'],'speaker':unit['speaker'],'text':text,'y':y,'height':row_height})
        y+=row_height
    return rows


def server_chat_frame(script,index,progress=1,height=1280):
    rows=message_layout(script,height);current=rows[index]
    top=185;bottom=height-125;viewport=bottom-top
    previous_bottom=current['y'];current_bottom=current['y']+current['height']
    old_offset=max(0,previous_bottom-viewport);new_offset=max(0,current_bottom-viewport)
    progress=max(0,min(1,progress));ease=1-(1-progress)**3
    offset=old_offset+(new_offset-old_offset)*ease
    picture=Image.new('RGB',(720,height),'#252830');draw=ImageDraw.Draw(picture)
    palette={}
    for unit in script['units']:
        if unit['speaker'] not in palette:palette[unit['speaker']]=speaker_color(unit['speaker'],palette.values())
    # A generic fictional server interface, not a screenshot of a real service.
    draw.rectangle((0,0,720,78),fill='#1b1e25')
    text_box(draw,'Messages',(26,22,668,32),'#c6cad7',22,True,minimum=22)
    text_box(draw,' & '.join(dict.fromkeys(u['speaker'] for u in script['units'])),(30,100,660,50),'white',34,True,minimum=34)
    draw.line((26,162,694,162),fill='#3d4250',width=2)
    for i,row in enumerate(rows[:index+1]):
        y=top+row['y']-offset+(24*(1-ease) if i==index else 0)
        if y+row['height']<top or y>bottom:continue
        layer=Image.new('RGBA',(720,row['height']));ld=ImageDraw.Draw(layer);color=palette[row['speaker']]
        ld.ellipse((25,13,83,71),fill=color)
        initials=''.join(word[0] for word in row['speaker'].split()[:2]).upper()
        text_box(ld,initials,(27,28,54,30),'#1b1e25',23,True,'center',minimum=23)
        text_box(ld,row['speaker'],(104,7,550,40),color,27,True,minimum=27)
        text_box(ld,row['text'],(104,51,530,row['height']-59),'#f3f4f7',34,minimum=34)
        if i==index:layer.putalpha(layer.getchannel('A').point(lambda value:round(value*ease)))
        picture.paste(layer,(0,round(y)),layer)
    # Fixed chrome covers scrolled-off rows cleanly.
    draw=ImageDraw.Draw(picture)
    draw.rectangle((0,0,720,top-12),fill='#252830')
    draw.rectangle((0,0,720,78),fill='#1b1e25')
    text_box(draw,'Messages',(26,22,668,32),'#c6cad7',22,True,minimum=22)
    text_box(draw,' & '.join(dict.fromkeys(u['speaker'] for u in script['units'])),(30,100,660,50),'white',34,True,minimum=34)
    draw.rectangle((0,bottom,720,height),fill='#252830')
    draw.rounded_rectangle((24,height-92,696,height-27),radius=12,fill='#343945')
    text_box(draw,'Message',(44,height-73,620,34),'#969eaf',24,minimum=24)
    visible=[row['id'] for row in rows[:index+1] if top+row['y']-offset+row['height']>top and top+row['y']-offset<bottom]
    return picture,{'visible_unit_ids':visible,'active_unit_id':current['id'],'scroll_offset':offset,'speaker_colors':palette,
        'presentation':'original fictional full-screen server chat','entry_seconds':.18}


def render_server_message(script,index,duration,path,height=1280):
    if not math.isfinite(duration) or duration<=0:raise Held('chat_timing','Message duration must be positive and finite.')
    path=Path(path)
    poster,details=server_chat_frame(script,index,1,height);poster.save(path.with_suffix('.png'))
    process=subprocess.Popen(['ffmpeg','-v','error','-nostdin','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'720x{height}',
        '-framerate','30','-i','pipe:0','-t',str(duration),'-an','-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p',str(path)],
        stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    try:
        final=poster.tobytes()
        for frame in range(math.ceil(duration*30)):
            second=frame/30
            data=server_chat_frame(script,index,min(1,(second+.035)/min(.18,duration*.2)),height)[0].tobytes() if second<.18 else final
            process.stdin.write(data)
        process.stdin.close();process.stdin=None;process.communicate(timeout=120)
        if process.returncode:raise Held('chat_render','The server-chat message failed to render.')
    except BaseException:
        if process.poll() is None:process.kill();process.communicate()
        raise
    return details
