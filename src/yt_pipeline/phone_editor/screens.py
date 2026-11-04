"""Composable phone events: navigation, alerts, lock-screen and silent gaps."""
import math
from PIL import Image, ImageDraw, ImageFilter
from shorts_editor.graphics import text_box

from .chrome import _app_chrome, _avatar
from .themes import wallpaper


def event_screen(kind, progress, base, *, contact, time, text, theme, avatar=None, elapsed_label='Later'):
    picture = base.copy(); d = ImageDraw.Draw(picture)
    if kind == 'blackout':
        return Image.new('RGB', picture.size, '#000000')
    if kind == 'switch':
        # Slide the new conversation into view over a neutral phone background.
        offset = round(720*(1-progress)**3)
        background = wallpaper('light'); _app_chrome(background, 'Messages', None, time=time)
        background.paste(picture, (offset, 0)); return background
    if kind == 'glitch':
        # Bounded local displacement, no repetitive full-screen flashing.
        for i in range(6):
            y = 230+i*134+round(12*math.sin(progress*15+i))
            strip = picture.crop((0,y,720,y+8)); picture.paste(strip,(round(12*math.sin(i+progress*19)),y))
        return picture
    if kind in ('time_jump', 'notification'):
        picture = wallpaper('dark').filter(ImageFilter.GaussianBlur(5)); d = ImageDraw.Draw(picture)
        text_box(d, time, (80,165,560,150), '#f3f5fa', 105, False, 'center', minimum=105)
        text_box(d, elapsed_label, (100,318,520,48), '#b8c0cf', 28, False, 'center', minimum=28)
        d.rounded_rectangle((265,1250,455,1258),radius=4,fill='#f3f5fa')
        if kind == 'notification':
            y = round(450-32*(1-progress)**3)
            d.rounded_rectangle((24,y,696,y+180),radius=30,fill='#e9edf3')
            _avatar(picture,avatar,(45,y+24,48),contact); d=ImageDraw.Draw(picture)
            text_box(d,'Messages',(108,y+15,390,35),'#65707d',22,minimum=22)
            text_box(d,contact,(108,y+53,540,38),'#151c29',29,True,minimum=29)
            text_box(d,text,(108,y+99,530,65),'#263244',29,minimum=29)
        return picture
    if kind == 'low_battery':
        picture = Image.blend(picture,Image.new('RGB',picture.size,'black'),.32);d=ImageDraw.Draw(picture)
        d.rounded_rectangle((100,490,620,735),radius=30,fill='#f5f5f8')
        text_box(d,'Low Battery',(130,525,460,45),'#19191c',34,True,'center',minimum=34)
        text_box(d,'5% battery remaining',(125,583,470,48),'#4c4c55',28,False,'center',minimum=28)
        d.line((100,664,620,664),fill='#c8c8ce',width=1)
        text_box(d,'Low Power Mode',(120,682,480,38),'#007aff',28,False,'center',minimum=28)
    return picture
