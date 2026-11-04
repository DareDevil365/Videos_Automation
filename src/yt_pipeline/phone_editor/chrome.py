"""Fixed phone status, contact actions and composer chrome."""
from PIL import Image,ImageDraw,ImageOps
from shorts_editor.graphics import text_box
from .themes import PALETTES

def _avatar(image,avatar,rect,name):
    x,y,size=rect;mask=Image.new('L',(size,size));ImageDraw.Draw(mask).ellipse((0,0,size-1,size-1),fill=255)
    if avatar is None:
        tile=Image.new('RGB',(size,size),'#afb8c8');d=ImageDraw.Draw(tile)
        text_box(d,name[:1].upper(),(0,size*.18,size,size*.65),'white',size*.55,True,'center',minimum=12)
    else:tile=ImageOps.fit(avatar,(size,size),method=Image.Resampling.LANCZOS)
    image.paste(tile,(x,y),mask)


def _app_chrome(image,contact,avatar,theme_name="light",time="09:41",battery=82):
    theme=PALETTES[theme_name]
    d=ImageDraw.Draw(image)
    d.rectangle((0,0,720,210),fill=theme.chrome)
    text_box(d,time,(37,22,130,40),theme.ink,27,True,minimum=27)
    for i in range(4):d.rounded_rectangle((577+i*9,47-i*5,582+i*9,52),radius=2,fill=theme.ink)
    d.arc((620,27,652,57),205,335,fill=theme.ink,width=3)
    d.arc((627,34,645,55),210,330,fill=theme.ink,width=3)
    d.ellipse((634,47,638,51),fill=theme.ink)
    d.rounded_rectangle((664,31,699,49),radius=5,outline='#85858b',width=2)
    d.rectangle((668,35,668+max(1,round(24*battery/100)),45),fill='#ef4444' if battery<=10 else theme.ink);d.rounded_rectangle((701,36,704,44),radius=1,fill='#85858b')
    d.line((42,109,26,125,42,141),fill=theme.accent,width=5)
    _avatar(image,avatar,(331,74,58),contact)
    d=ImageDraw.Draw(image)
    text_box(d,contact,(105,148,510,38),theme.ink,28,False,'center',minimum=25)
    d.rounded_rectangle((631,112,664,136),radius=6,outline=theme.accent,width=3)
    d.line((665,119,679,112,679,137,665,130),fill=theme.accent,width=3)
    # Voice call and menu are phone-app controls, never decorative headings.
    d.line([(550,108),(546,112),(546,120),(551,128),(558,134),(566,136),(570,131)],fill=theme.accent,width=5,joint='curve')
    d.line((550,108,555,116),fill=theme.accent,width=7);d.line((564,128,570,131),fill=theme.accent,width=7)
    for yy in (114,125,136):d.ellipse((701,yy,705,yy+4),fill=theme.accent)
    d.line((0,209,720,209),fill='#dedee3',width=1)
    d.rectangle((0,1124,720,1280),fill=theme.chrome)
    d.line((0,1124,720,1124),fill='#ededf1',width=1)
    d.ellipse((24,1154,70,1200),fill='#ededf1')
    d.line((35,1177,59,1177),fill='#74747b',width=3);d.line((47,1165,47,1189),fill='#74747b',width=3)
    d.rounded_rectangle((88,1149,692,1208),radius=29,outline='#c8c8ce',width=2)
    text_box(d,'Message',(110,1162,450,38),'#9b9ba3',27,minimum=27)
    d.line((665,1164,665,1185),fill='#8c8c94',width=4)
    d.arc((655,1171,675,1195),0,180,fill='#8c8c94',width=3);d.line((665,1194,665,1200),fill='#8c8c94',width=2)
    d.rounded_rectangle((265,1250,455,1258),radius=4,fill=theme.ink)
