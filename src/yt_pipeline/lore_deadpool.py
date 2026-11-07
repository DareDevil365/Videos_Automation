"""Original geometric staging for Deadpool's 2012 metafiction horror story."""
import math
from PIL import ImageDraw
from shorts_editor.graphics import text_box
from .lore_screen_cast import actor,shield,EDGE

DEADPOOL_KINDS=tuple('dp_'+k for k in ('targets','clinic','voice','panels','hunt','avengers','hulk','regrow','banner','boundary','swamp','gate','studio','reader'))


def title(d,text,box,color=EDGE,size=28):text_box(d,text,box,color,size,True,'center',minimum=18)


def page(d,box,fill='#c8b18a',ink='#625444'):
    d.rectangle(box,fill=fill,outline=ink,width=4)
    x,y,r,b=box
    for xx,yy in ((x+18,y+18),(x+(r-x)/2+5,y+18),(x+18,y+(b-y)/2+5),(x+(r-x)/2+5,y+(b-y)/2+5)):
        d.rectangle((xx,yy,xx+(r-x)/2-35,yy+(b-y)/2-35),outline=ink,width=3)


def deadpool_art(layer,scene,second,p,glow):
    d=ImageDraw.Draw(layer);k=scene['kind'];e=max(0,min(1,p*1.4));sway=math.sin(second*2)*4
    if k=='dp_targets':
        actor(layer,'deadpool',365,536,1.5,hand=(510,470+sway))
        shield(d,145,404,58);actor(layer,'iron',565,620,.65)
        for x,y in ((145,404),(565,620)):
            r=62+6*math.sin(second*3);d.ellipse((x-r,y-r,x+r,y+r),outline='#c6735a',width=3)
            d.line((x-r-15,y,x+r+15,y),fill='#c6735a',width=2)
        d.line((105,843,615,843),fill=EDGE,width=3)
    elif k=='dp_clinic':
        d.rectangle((81,256,637,888),outline=EDGE,width=3)
        for y in range(286,870,47):d.line((94,y,625,y),fill='#827c70',width=1)
        d.polygon([(139,595),(338,595),(362,832),(113,832)],fill='#706a5b',outline=EDGE,width=4)
        actor(layer,'deadpool',236,507,1.03)
        actor(layer,'doctor',515,486,.98,hand=(405,571))
        d.rectangle((365,546,449,653),fill='#3b3b37',outline=EDGE,width=3)
        for n in range(3):d.ellipse((379,564+n*25,391,576+n*25),fill='#c87051' if (second+n)%1>.5 else '#d4ba73')
        d.line((365,592,338,592,310,478),fill='#9ca57f',width=4)
    elif k=='dp_voice':
        actor(layer,'deadpool',362,601,1.2)
        for x,y,color,sign in ((192,365,'#e7d9b7',-1),(479,352,'#d3b967',1)):
            dx=sign*100*e;d.rounded_rectangle((x-68+dx,y-37,x+68+dx,y+37),radius=17,fill=color,outline=EDGE,width=3)
            for n in range(3):d.line((x-40+dx,y-14+n*13,x+40+dx,y-14+n*13),fill='#76614a',width=2)
        d.rounded_rectangle((282,362,439,446),radius=18,fill='#9b3d41',outline=EDGE,width=3)
        d.polygon([(343,443),(364,469),(378,443)],fill='#9b3d41')
        title(d,'FICTION',(292,385,138,34),size=24)
    elif k=='dp_panels':
        page(d,(93,248,627,870))
        actor(layer,'deadpool',363,499,1.10,hand=(502,474+sway))
        for x in (328,395):d.line((x,260,x,475),fill='#7c6150',width=3)
        d.polygon([(501,456),(517,466),(501,481)],fill='#a85c49')
        title(d,'A WORLD INSIDE PANELS',(126,789,464,47),'#58422e',25)
    elif k=='dp_hunt':
        for n,(x,y) in enumerate(((103,294),(402,294),(103,575),(402,575))):
            d.rectangle((x,y,x+215,y+234),fill='#514b43' if n%2 else '#6b514a',outline=EDGE,width=3)
            who=('iron','cap','spider','zemo')[n];actor(layer,who,x+107,y+85,.48)
            q=min(1,max(0,(p-n*.14)*2))
            d.line((x+27,y+207,x+27+159*q,y+207-161*q),fill='#bf6951',width=6)
        actor(layer,'deadpool',365,588,.75,hand=(435,579+sway))
    elif k=='dp_avengers':
        for who,x in (('iron',177),('cap',367),('war',559)):
            actor(layer,who,x,436,.64)
        d.polygon([(93,592),(612,592),(654,727),(58,727)],fill='#796451',outline=EDGE,width=4)
        d.rectangle((321,586,372,636),fill='#dfcda8',outline=EDGE,width=3)
        d.arc((357,590,393,624),270,90,fill=EDGE,width=4)
        r=max(3,29*(1-e));d.ellipse((240-r,682-r,240+r,682+r),fill='#3b3333',outline='#c98855',width=2)
        d.line((270,676,311,619),fill='#ba9764',width=3)
        if p>.58:
            q=(p-.58)/.42
            for n in range(10):
                a=n*math.tau/10+second*.2;radius=35+q*150
                d.line((352+math.cos(a)*35,583+math.sin(a)*35,352+math.cos(a)*radius,583+math.sin(a)*radius),fill='#e4ae6e',width=5)
        title(d,'STOLEN SHRINKING TECHNOLOGY',(105,787,510,65),'#55432e',26)
    elif k=='dp_hulk':
        actor(layer,'hulk',481,464,1.47,hand=(330,517))
        actor(layer,'deadpool',209-35*e,613,.91,hand=(305-40*e,553))
        d.line((359,710,386+60*e,755),fill='#b29168',width=5)
        d.polygon([(340,683),(315,710),(337,737),(304,754)],outline='#d6c29d',width=4)
    elif k=='dp_regrow':
        d.polygon([(83,803),(634,803),(668,866),(57,866)],fill='#625247',outline=EDGE,width=3)
        actor(layer,'deadpool',356,699-125*e,.60+.40*e)
        for n in range(5):
            a=n*math.tau/5+second*.8;r=120-40*e
            x=356+math.cos(a)*r;y=626+math.sin(a)*r
            d.line((x-5,y,x+5,y),fill='#c7ad79',width=3)
        title(d,'HE REGENERATES',(145,335,430,54),size=28)
    elif k=='dp_banner':
        actor(layer,'banner',482,651,.74)
        actor(layer,'deadpool',213+30*e,570,1.05,hand=(337,624))
        d.polygon([(425,656),(546,656),(563,839),(409,839)],fill='#6f4863',outline=EDGE,width=3)
        for x in (469,494):d.arc((x-7,609,x+7,621),0,180,fill='#3c302a',width=2)
        # Empty green outline indicates the lost Hulk form; no graphic injury.
        d.arc((373,377,602,733),190,350,fill='#9aab79',width=4)
    elif k=='dp_boundary':
        page(d,(93,247,548,866),fill='#c4af8c')
        actor(layer,'deadpool',330+55*e,565,1.13,hand=(537,499+sway))
        d.line((549,247,549,867),fill='#e2ceb2',width=10)
        for n in range(6):
            y=365+n*55;d.line((560,y,610+12*math.sin(second+n),y),fill='#af6654',width=4)
        title(d,'THE STORY STILL HOLDS HIM',(130,810,378,42),'#534332',23)
    elif k=='dp_swamp':
        d.polygon([(42,752),(199,713),(393,764),(680,723),(680,925),(40,925)],fill='#444d39',outline=EDGE,width=2)
        for x in (93,576):
            d.line((x,293,x-9,811),fill='#8b8568',width=12)
            d.line((x-9,445,x+43,371),fill='#8b8568',width=7)
        actor(layer,'deadpool',225,558,1.0,hand=(319,548+sway))
        actor(layer,'manthing',488,537,1.3)
        title(d,'NEXUS OF ALL REALITIES',(102,285,518,51),size=27)
    elif k=='dp_gate':
        center=(411,557);glow(layer,center,155,(226,198,142),95);d=ImageDraw.Draw(layer)
        for n in range(4):
            r=121+n*20+7*math.sin(second*2+n)
            d.ellipse((center[0]-r*.72,center[1]-r,center[0]+r*.72,center[1]+r),outline='#e2cb9e',width=3)
        for n in range(6):
            x=112+n*85;y=330+math.sin(second+n)*32
            d.polygon([(x,y),(x+44,y-14),(x+52,y+53),(x+6,y+67)],outline='#ad9270',width=2)
        actor(layer,'deadpool',208+185*e,591-47*e,1.10-.27*e,hand=(392+55*e,501))
    elif k=='dp_studio':
        for x in (180,491):
            actor(layer,'writer' if x==180 else 'artist',x,447,.83,hand=(x+42,631+sway))
        d.polygon([(96,625),(611,625),(653,755),(62,755)],fill='#8e7156',outline='#e4cfaa',width=4)
        d.line((111,754,97,882),fill=EDGE,width=9);d.line((594,754,611,882),fill=EDGE,width=9)
        page(d,(267,596,451,709),fill='#eadbbd',ink='#75604b')
        d.polygon([(400,590),(421,539),(428,541),(410,596)],fill='#5b4b42',outline=EDGE,width=2)
        actor(layer,'deadpool',616-35*e,543,.91,hand=(515,606))
        title(d,'THE PEOPLE WRITING HIS ENDING',(104,280,516,75),'#4a382e',27)
    elif k=='dp_reader':
        page(d,(93,255,628,867),fill='#b99975',ink='#72543e')
        actor(layer,'deadpool',361,516,1.41,hand=(483+40*e,728+35*e))
        d.rounded_rectangle((456+40*e,690+35*e,522+40*e,775+35*e),radius=10,fill='#a63f3b',outline=EDGE,width=4)
        title(d,'NEXT: THE READER',(122,304,470,55),'#4b3029',32)
