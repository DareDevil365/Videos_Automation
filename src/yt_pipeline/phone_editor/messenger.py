"""Measured scrolling bubbles and bounded camera animation."""
import math
from PIL import Image,ImageDraw
from shorts_editor.graphics import font,wrapped,text_box
from ..core import Held
from .chrome import _app_chrome
from .themes import PALETTES,wallpaper

def _ease(value):
    return 1-(1-max(0,min(1,value)))**3


def bubble_layout(script,outgoing=None):
    """Measure the real conversation once; history uses one continuous scroll."""
    draw=ImageDraw.Draw(Image.new('RGB',(720,1280)));rows=[];y=260
    outgoing=outgoing or script['units'][0]['speaker'];speakers=list(dict.fromkeys(u['speaker'] for u in script['units']))
    for index,unit in enumerate(script['units']):
        lines=wrapped(draw,unit['text'],font(38),490)
        if len(lines)>4:raise Held('chat_message_length','Keep each message within four readable lines.')
        width=min(550,max(100,math.ceil(max(draw.textlength(line,font=font(38)) for line in lines))+44))
        height=round(len(lines)*47.2)+34+(24 if unit.get('_story_time') else 0)
        named=len(speakers)>2 and unit['speaker']!=outgoing
        if named:y+=30
        if index and unit['speaker']!=script['units'][index-1]['speaker']:y+=14
        x=692-width if unit['speaker']==outgoing else 28
        rows.append({'id':unit['id'],'speaker':unit['speaker'],'text':unit['text'],'x':x,'y':y,'width':width,'height':height,'outgoing':unit['speaker']==outgoing,'named':named,'time':unit.get('_story_time')})
        y+=height+12
    return rows


def chat_frame(script,index,second,duration,typing,avatars=None,settings=None):
    units=script['units'];avatars=avatars or {};settings=settings or {}
    outgoing=settings.get('pov',units[0]['speaker']);theme_name=settings.get('theme','light');theme=PALETTES[theme_name]
    rows=bubble_layout(script,outgoing)
    current=rows[index];arrived=second>=typing;elapsed=max(0,second-typing)
    last=index if arrived else index-1
    contact=next((u['speaker'] for u in units if u['speaker']!=units[0]['speaker']),'Messages')
    speakers=list(dict.fromkeys(u['speaker'] for u in units))
    if len(speakers)>2:contact=' & '.join(speakers[1:])
    contact=settings.get('contact',contact)
    old_bottom=rows[index-1]['y']+rows[index-1]['height'] if index else 260
    new_bottom=current['y']+current['height']
    old_offset=max(0,old_bottom-1015);new_offset=max(0,new_bottom-1015)
    scroll=old_offset+(new_offset-old_offset)*_ease(elapsed/.30) if arrived else old_offset
    focus=settings.get('focus',index==len(units)-1 or (len(current['text'].split())<=4 and '?' in current['text']) or index==0)
    image=wallpaper(theme_name,settings.get('wallpaper'));layer=Image.new('RGBA',(720,1280));visible=[]
    if scroll<70:
        text_box(ImageDraw.Draw(layer),'Today' if units[0].get('_story_time') else 'Today '+settings.get('time','09:41'),(130,225-scroll,460,30),theme.muted,21,False,'center',minimum=21)
    active_box=None
    for i,row in enumerate(rows[:last+1]):
        y=round(row['y']-scroll);x=row['x'];w=row['width'];h=row['height'];active=i==index
        if y+h<218 or y>1115:continue
        visible.append(row['id']);bubble=Image.new('RGBA',(w+18,h+22));bd=ImageDraw.Draw(bubble)
        fill=theme.outgoing if row['outgoing'] else theme.incoming
        bd.rounded_rectangle((8,0,w+8,h),radius=29,fill=fill)
        if row['outgoing']:bd.polygon([(w-13,h-17),(w+16,h+1),(w-31,h-1)],fill=fill)
        else:bd.polygon([(25,h-17),(0,h+1),(42,h-1)],fill=fill)
        text_box(bd,row['text'],(30,15,w-44,h-20-(24 if row['time'] else 0)),'white' if row['outgoing'] else theme.incoming_ink,38,minimum=38)
        if row['time']:bd.text((w-10-bd.textlength(row['time'],font=font(17)),h-26),row['time'],font=font(17),fill='#dbe9ff' if row['outgoing'] else theme.muted)
        if active:
            entry=_ease(elapsed/.22);scale=.94+.06*entry
            bubble=bubble.resize((round(bubble.width*scale),round(bubble.height*scale)),Image.Resampling.LANCZOS)
            bubble.putalpha(bubble.getchannel('A').point(lambda a:round(a*entry)))
            y+=round(16*(1-entry));active_box=[x,y,x+w,y+h]
            if focus and .30<elapsed<1.0:
                pulse=math.sin(math.pi*(elapsed-.3)/.7)
                glow=Image.new('RGBA',(720,1280));gd=ImageDraw.Draw(glow)
                gd.rounded_rectangle((x-5,y-5,x+w+5,y+h+5),radius=35,outline=(0,122,255,round(65*pulse)),width=5)
                layer=Image.alpha_composite(layer,glow)
        if row['named']:text_box(ImageDraw.Draw(layer),row['speaker'],(x+10,y-29,w,28),'#86868d',22,minimum=22)
        layer.alpha_composite(bubble,(x-8,y))
    if not arrived:
        y=min(1060,round(old_bottom-scroll+30));x=560 if current['outgoing'] else 28
        d=ImageDraw.Draw(layer);d.rounded_rectangle((x,y,x+130,y+62),radius=30,fill=theme.incoming)
        for i in range(3):
            lift=round(4*math.sin(second*18-i*.8));d.ellipse((x+30+i*25,y+26+lift,x+42+i*25,y+38+lift),fill='#93939b')
    # Only conversation content moves; the app navigation/composer remain fixed.
    layer.paste((0,0,0,0),(0,0,720,218));layer.paste((0,0,0,0),(0,1124,720,1280))
    image=Image.alpha_composite(image.convert('RGBA'),layer).convert('RGB')
    # A clear camera move, then a gentle pull-back to the app view. The crop
    # always includes the complete active bubble, never sacrificing words.
    zoom=1.0
    if arrived and focus and active_box:
        attack=_ease(elapsed/.45);release=_ease((duration-second)/.38)
        zoom=1+.105*min(attack,release)
        shown=[r for r in rows[:last+1] if r['y']-scroll+r['height']>=218 and r['y']-scroll<=1115]
        if shown:
            left_edge=min(r['x'] for r in shown);right_edge=max(r['x']+r['width'] for r in shown)
            zoom=min(zoom,720/(right_edge-left_edge+40))
        cw=720/zoom;ch=906/zoom;bx1,by1,bx2,by2=active_box
        cx=max(cw/2,min(720-cw/2,(bx1+bx2)/2));cy=max(218+ch/2,min(1124-ch/2,(by1+by2)/2))
        left=max(0,min(720-cw,cx-cw/2));top=max(218,min(1124-ch,cy-ch/2))
        if shown:left=max(right_edge-cw+16,min(left,left_edge-16))
        left=max(0,min(720-cw,left))
        viewport=image.crop((round(left),round(top),round(left+cw),round(top+ch))).resize((720,906),Image.Resampling.LANCZOS)
        image.paste(viewport,(0,218))
    _app_chrome(image,contact,avatars.get(contact),theme_name,settings.get('time','09:41'),settings.get('battery',82))
    return image,{'visible_unit_ids':visible,'active_unit_id':current['id'],'message_arrived':arrived,
        'emphasis':focus,'typing_seconds':typing,'canvas':[720,1280],'ui':'clean_mobile_messenger',
        'camera_zoom':round(zoom,4),'scroll_offset':round(scroll,3),'active_bubble_box':active_box,
        'outgoing_speaker':outgoing,'contact':contact,'theme':theme_name,'story_time':settings.get('time','09:41'),'decorative_labels':False}
