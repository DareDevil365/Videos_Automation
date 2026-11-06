"""Hybrid identity and physical-action scenes for two source-reviewed Shorts."""
import math

from PIL import ImageDraw
from shorts_editor.graphics import text_box
from .lore_style_assets import place_cutout


IDENTITY_KINDS=tuple('vision_'+n for n in ('question','bodies','magic','ship','two_ships','memory','unlock','answer','mapping','departure','aftermath'))+tuple('spider_'+n for n in ('question','theft','trapped','reach','resolve','lift','hospital','answer','transfusion','serum_return'))
CREAM='#e0d1af'
INK='#101923'


def _room(d,second,library=False):
    d.polygon([(45,910),(45,360),(360,278),(675,360),(675,910)],fill='#182c35',outline='#65838a',width=3)
    for x in (80,490):
        d.rectangle((x,360,x+149,745),fill='#15232e',outline='#5a727b',width=3)
        for y in range(400,730,72):
            d.line((x,y,x+149,y),fill='#9a8a75',width=3)
            if library:
                for i in range(6):
                    bx=x+8+i*23;d.polygon([(bx,y-47),(bx+14,y-45),(bx+14,y),(bx,y)],fill=('#594253','#77614d','#355766')[i%3])
    d.line((45,840,675,840),fill='#76918f',width=3)
    for i in range(7):
        x=80+i*93;y=330+(second*15+i*41)%460
        d.ellipse((x,y,x+2,y+2),fill='#a5bfb2')


def _vision(d,who,x,y,s=1,hand=None):
    white=who=='white_vision';body='#9daeb3' if white else '#557c79';face='#c4ced0' if white else '#a94763';edge='#e3e8de' if white else '#d2b982'
    q=lambda a,b:(x+a*s,y+b*s)
    d.polygon([q(-40,-3),q(-94,227),q(80,227),q(41,-4)],fill='#697a84' if white else '#a49363',outline=edge,width=3)
    d.polygon([q(-30,3),q(30,3),q(38,110),q(-37,110)],fill=body,outline=edge,width=3)
    for side in (-1,1):
        d.line([q(side*20,104),q(side*27,218)],fill=body,width=round(24*s))
        d.line([q(side*27,208),q(side*40,227)],fill=edge,width=round(14*s))
        target=hand if side==1 and hand else q(side*65,99)
        d.line([q(side*29,18),q(side*53,52),target],fill=edge,width=round(14*s))
        d.ellipse((target[0]-7*s,target[1]-7*s,target[0]+7*s,target[1]+7*s),fill=face)
    d.polygon([q(-29,-73),q(-14,-92),q(17,-92),q(32,-71),q(24,-29),q(0,-16),q(-26,-34)],fill=face,outline=edge,width=3)
    d.polygon([q(0,-86),q(-8,-76),q(0,-66),q(8,-76)],fill='#b8dfed' if white else '#f4d477')
    d.line([q(-21,-59),q(-7,-56)],fill='#edf2d9',width=3)
    d.line([q(8,-56),q(23,-59)],fill='#edf2d9',width=3)
    d.line([q(-10,-36),q(12,-36)],fill=INK,width=2)
    d.polygon([q(0,20),q(-12,41),q(0,66),q(12,41)],fill=edge)


def _actor(layer,scene,images,who,box,anchor):
    choice=scene.get('visual_style',{}).get('characters',{}).get(who,{'representation':'geometric'})
    if choice['representation']=='cutout':place_cutout(layer,images,who,box)
    else:_vision(ImageDraw.Draw(layer),who,*anchor)


def _ship(d,x,y,s,p,second=False):
    q=lambda a,b:(x+a*s,y+b*s)
    d.polygon([q(-126,0),q(119,0),q(76,65),q(-83,65)],fill='#4c494b',outline=CREAM,width=3)
    for i in range(6):
        xx=-106+i*36
        color='#81b9ae' if (i/6<p and not second) else '#ae8e61'
        dy=-47*math.sin(max(0,min(1,p*6-i))*math.pi) if not second else 0
        d.polygon([q(xx,12+dy),q(xx+30,12+dy),q(xx+25,48+dy),q(xx+6,48+dy)],fill=color,outline=INK,width=2)
    d.line([q(0,-128),q(0,0)],fill=CREAM,width=4)
    d.polygon([q(10,-124),q(10,-14),q(86,-14)],fill='#a7bcc0',outline=CREAM,width=3)


def _vial(d,x,y,s=1):
    d.rounded_rectangle((x-15*s,y-36*s,x+15*s,y+34*s),radius=6*s,fill='#426c76',outline='#c7eddd',width=3)
    d.rectangle((x-11*s,y-7*s,x+11*s,y+27*s),fill='#7bcbd1')
    d.rectangle((x-17*s,y-44*s,x+17*s,y-32*s),fill='#b3bdb1',outline=CREAM,width=2)


def _spider_mask(d,x,y,s=1):
    q=lambda a,b:(x+a*s,y+b*s)
    d.polygon([q(-33,-22),q(-19,-43),q(19,-43),q(35,-20),q(27,18),q(0,34),q(-27,18)],fill='#ba484b',outline='#e0b49b',width=max(2,round(3*s)))
    for side in (-1,1):
        d.polygon([q(side*26,-17),q(side*5,-6),q(side*10,8),q(side*27,1)],fill='#e5e4cf',outline=INK,width=max(2,round(3*s)))
    d.line([q(0,-40),q(0,30)],fill='#572d3b',width=max(2,round(2*s)))
    for yy in (-26,15):d.line([q(-25,yy),q(0,yy+8),q(25,yy)],fill='#572d3b',width=max(2,round(2*s)))


def _spider(d,x,y,beam=None,lift=0):
    red='#ba484b';blue='#31536c';edge='#e0b49b'
    for side in (-1,1):
        knee=(x+side*(90-50*lift),y+(875-y)*.65)
        foot=(x+side*110,875)
        d.line([(x+side*22,y+120),knee,foot],fill=INK,width=32,joint='curve')
        d.line([(x+side*22,y+120),knee,foot],fill=blue,width=25,joint='curve')
        d.line([foot,(foot[0]+side*28,875)],fill=red,width=16)
    d.polygon([(x-36,y+35),(x+36,y+35),(x+44,y+117),(x,y+143),(x-44,y+117)],fill=red,outline=edge,width=3)
    d.line((x,y+61,x,y+102),fill=INK,width=8)
    for i in range(3):
        for side in (-1,1):d.line((x,y+72+i*8,x+side*21,y+62+i*14),fill=INK,width=3)
    for side in (-1,1):
        target=(x+side*81,beam+31) if beam is not None else (x+side*83,y+130)
        elbow=(x+side*101,y+28 if beam is not None else y+96)
        d.line([(x+side*30,y+48),elbow,target],fill=INK,width=22,joint='curve')
        d.line([(x+side*30,y+48),elbow,target],fill=red,width=16,joint='curve')
        d.ellipse((target[0]-10,target[1]-7,target[0]+10,target[1]+7),fill=red,outline=edge,width=2)
    _spider_mask(d,x,y)


def _steel(d,y):
    d.polygon([(83,y-60),(600,y-82),(640,y+26),(78,y+36)],fill='#56616b',outline='#a4b2b5',width=4)
    d.line((94,y-28,608,y-49),fill='#263a49',width=16)
    for x in (113,220,327,434,541):d.ellipse((x,y+2,x+9,y+11),fill='#abb4b6')


def identity_art(layer,scene,second,p,glow,images):
    kind=scene['kind'];d=ImageDraw.Draw(layer)
    if kind.startswith('vision_'):
        if kind in ('vision_ship','vision_two_ships'):
            for x in range(75,680,60):d.line((x,245,x,900),fill='#29444e',width=1)
            for y in range(270,920,60):d.line((55,y,675,y),fill='#29444e',width=1)
        else:_room(d,second,True)
        if kind in ('vision_question','vision_bodies'):
            if kind=='vision_question':
                _actor(layer,scene,images,'vision',(76,275,423,878),(228,585,1.3))
                _actor(layer,scene,images,'white_vision',(423,342,655,883),(535,598,1.1))
            else:
                _actor(layer,scene,images,'vision',(60,330,359,882),(210,585,1.1))
                _actor(layer,scene,images,'white_vision',(394,330,660,882),(525,585,1.1))
            ImageDraw.Draw(layer).line((365,386,365,831),fill=CREAM,width=3)
        elif kind=='vision_magic':
            _vision(d,'vision',220,580,1.15);_vision(d,'white_vision',522,580,1.15)
            for i in range(17):
                a=i*.47+second*.7;r=98+14*math.sin(i+second)
                x=220+math.cos(a)*r;y=554+math.sin(a)*150;d.ellipse((x,y,x+4,y+4),fill='#ed7ca7')
            d.arc((426,383,615,635),second*29,second*29+250,fill='#b5d7da',width=4)
        elif kind in ('vision_ship','vision_two_ships'):
            if kind=='vision_ship':_ship(d,360,634,2.05,p)
            else:
                _ship(d,203,535,1.11,p);_ship(d,518,732,1.08,0,True)
                text_box(d,'REPLACED PARTS',(63,643,290,45),CREAM,23,True,minimum=21)
                text_box(d,'ORIGINAL PARTS',(370,820,290,45),CREAM,23,True,minimum=21)
                d.line((229,624,381,676),fill='#83b8ac',width=4)
        elif kind=='vision_memory':
            _actor(layer,scene,images,'white_vision',(383,292,661,899),(532,583,1.1))
            d=ImageDraw.Draw(layer)
            for i in range(7):
                a=i*math.tau/7+second*.12;x=223+112*math.cos(a);y=547+135*math.sin(a)
                d.line((223,547,x,y),fill='#d2b274',width=3);d.ellipse((x-14,y-14,x+14,y+14),fill='#b88085',outline=CREAM,width=3)
            d.rounded_rectangle((189,518,257,583),radius=9,fill='#4d6871',outline=CREAM,width=3)
            d.arc((202,495,244,540),180,360,fill=CREAM,width=5)
        elif kind=='vision_mapping':
            _actor(layer,scene,images,'vision',(47,311,325,762),(203,497,1.0))
            _actor(layer,scene,images,'white_vision',(403,311,671,762),(529,497,1.0))
            d=ImageDraw.Draw(layer)
            text_box(d,'NO ORIGINAL MATERIAL',(53,799,288,78),CREAM,24,True,'center',minimum=22)
            text_box(d,'BLOCKED MEMORIES',(391,799,287,78),CREAM,24,True,'center',minimum=22)
            d.line((355,365,355,866),fill=CREAM,width=3)
        elif kind=='vision_unlock':
            contact=min(1,max(0,p/.35));fly=0 if scene.get('unit_id')=='u7' else max(0,(p-.66)/.34)
            target=(280+220*contact,608-155*contact)
            _vision(d,'vision',220,580,1.1,hand=target)
            _vision(d,'white_vision',500,537-580*fly,1.1)
            if contact>=1:
                glow(layer,(500,453),83,(145,221,229),120)
                for i in range(7):
                    a=i*.9+second*.4;r=30+75*((p-.35)/.65)
                    x=500+r*math.cos(a);y=453+r*math.sin(a);ImageDraw.Draw(layer).ellipse((x-3,y-3,x+3,y+3),fill=CREAM)
        elif kind=='vision_departure':
            shift=round(1000*max(0,(p-.12)/.88)**1.5)
            cast={**images,'white_vision':images['white_vision_full']} if 'white_vision_full' in images else images
            _actor(layer,scene,cast,'white_vision',(220,306-shift,531,914-shift),(361,575-shift,1.25))
        elif kind=='vision_aftermath':
            # The empty library is the visible consequence of the attacker leaving.
            d.arc((195,386,518,710),second*32,second*32+205,fill='#617f8a',width=3)
        else:
            _actor(layer,scene,images,'white_vision',(200,270,537,900),(361,575,1.25))
    else:
        _room(d,second)
        if kind in ('spider_question','spider_answer'):
            choice=scene.get('visual_style',{}).get('characters',{}).get('spider_man',{})
            if 'spider_man' in images and choice.get('representation')!='geometric':place_cutout(layer,images,'spider_man',(75,303,647,888))
            else:_spider(d,360,550)
            if kind=='spider_question':_vial(ImageDraw.Draw(layer),561,315,1.15)
        elif kind=='spider_transfusion':
            d.polygon([(183,356),(137,435),(146,487),(181,512),(222,487),(233,435)],fill='#a45053',outline=CREAM,width=4)
            d.line((240,467,337,467,337,576,412,576),fill='#bd7570',width=6)
            d.polygon([(423,576),(402,563),(402,589)],fill=CREAM)
            d.rounded_rectangle((408,558,641,686),radius=13,fill='#71858a',outline=CREAM,width=3)
            d.ellipse((422,544,480,598),fill='#c0b197',outline=CREAM,width=3)
            d.arc((418,535,485,598),181,357,fill='#d5d1c0',width=10)
            d.polygon([(485,568),(623,573),(632,669),(480,669)],fill='#b7c5b6',outline=CREAM,width=3)
            for angle in (0,120,240):
                a=math.radians(angle)+second*.07
                points=[(184,650),(184+65*math.cos(a-.35),650+65*math.sin(a-.35)),(184+65*math.cos(a+.35),650+65*math.sin(a+.35))]
                d.polygon(points,fill='#d5a968')
            d.ellipse((174,640,194,660),fill=INK,outline=CREAM,width=2)
        elif kind=='spider_serum_return':
            d.polygon([(70,837),(650,837),(673,912),(44,912)],fill='#425963',outline=CREAM,width=3)
            _vial(d,360,728,3.2)
            glow(layer,(360,710),125,(109,196,185),70)
            # A recognizable geometric glove shares the scale and outline of the lift.
            x=83+110*min(1,p*1.8)
            d=ImageDraw.Draw(layer);d.polygon([(45,709),(x,709),(x+41,734),(x+111,734),(x+119,754),(x+27,768),(45,759)],fill='#ba484b',outline='#e0b49b',width=4)
            for y in (722,741):d.line((53,y,x,y+5),fill='#572d3b',width=3)
        elif kind=='spider_theft':
            # Four segmented mechanical arms identify the antagonist in an action shot.
            for side in (-1,1):
                for offset in (0,85):
                    points=[(361,540),(361+side*137,472+offset),(361+side*209,585+offset),(360+side*117,690)]
                    d.line(points,fill='#a4a898',width=14,joint='curve')
                    for x,y in points[1:-1]:d.ellipse((x-10,y-10,x+10,y+10),fill='#53676b',outline=CREAM,width=2)
            d.polygon([(323,505),(397,505),(414,693),(306,693)],fill='#45655c',outline=CREAM,width=3)
            d.ellipse((326,420,394,503),fill='#be9f83',outline=CREAM,width=3)
            d.rectangle((324,424,397,446),fill='#604c3c')
            d.line((328,462,390,462),fill=INK,width=7);_vial(d,360,720-20*p,1.6)
        elif kind in ('spider_trapped','spider_reach','spider_resolve','spider_lift'):
            lift=min(1,max(0,(p-.12)/.72)) if kind=='spider_lift' else 0
            beam=610-280*lift
            _spider(d,311,670-200*lift,beam,lift)
            _steel(d,beam)
            water=816-27*p
            for i in range(4):
                yy=water+i*22;d.line([(54+n*74,yy+7*math.sin(n+second*2)) for n in range(9)],fill='#508b9b',width=4)
            _vial(d,579,765,1.22)
            if kind=='spider_reach':
                # The connected inset enlarges the medicine without changing its literal size.
                d.ellipse((406,326,654,574),fill='#19333c',outline=CREAM,width=4)
                _vial(d,530,453,2.05)
                d.line((584,571,579,716),fill=CREAM,width=3)
            if kind=='spider_resolve':
                # A distinct close-up for the internal turning point rather than a fourth wide hold.
                d.rectangle((66,276,660,889),fill='#192c36')
                _steel(d,390)
                _spider_mask(d,360,609+3*math.sin(second*2),3.55)
                text_box(d,'UNCLE BEN',(85,803,245,45),CREAM,27,True,minimum=22)
                text_box(d,'AUNT MAY',(422,803,235,45),CREAM,27,True,minimum=22)
        elif kind=='spider_hospital':
            d.rounded_rectangle((144,549,619,731),radius=17,fill='#789194',outline=CREAM,width=4)
            d.ellipse((185,548,267,614),fill='#c0b197',outline=CREAM,width=3)
            d.arc((182,532,272,608),174,358,fill='#d8d6c4',width=12)
            d.polygon([(276,566),(581,573),(608,710),(263,710)],fill='#b7c5b6',outline=CREAM,width=3)
            for x in (175,584):d.line((x,733,x,844),fill=CREAM,width=6)
            _vial(d,550,513,1.1)
            d.line((443,492,443,513,631,513,631,787),fill='#819f9d',width=5)
            glow(layer,(551,482),63,(138,221,184),70)
