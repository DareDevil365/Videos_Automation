"""Geometric noir staging for Kraven's Last Hunt; no generated bitmap art."""
import math
from PIL import ImageDraw
from shorts_editor.graphics import text_box


HUNT_KINDS=('hunt_burial','hunt_hunter','hunt_impostor','hunt_vermin','hunt_coffin','hunt_rise','hunt_confront','hunt_test','hunt_confession')
EDGE='#e0ceb1'


def black_spider(d,x,y,s=1,hand=None):
    q=lambda a,b:(x+a*s,y+b*s)
    for side in (-1,1):
        d.line([q(side*20,85),q(side*36,158),q(side*47,234)],fill='#121319',width=round(28*s))
        target=hand if side==1 and hand else q(side*71,104)
        d.line([q(side*30,1),q(side*55,49),target],fill=EDGE,width=round(20*s))
        d.line([q(side*30,1),q(side*55,49),target],fill='#17161e',width=round(15*s))
        tx,ty=target;r=10*s
        d.rounded_rectangle((tx-r,ty-r,tx+r,ty+r*1.25),radius=max(2,round(3*s)),fill='#17161e',outline=EDGE,width=2)
        for i in (-1,0,1):d.line((tx+i*5*s,ty-r,tx+i*5*s,ty+2*s),fill='#bcb8ac',width=2)
        d.line([q(side*47,230),q(side*67,235)],fill='#d7d1c6',width=round(8*s))
    d.polygon([q(-33,-7),q(33,-7),q(40,87),q(0,111),q(-40,87)],fill='#17161d',outline=EDGE,width=3)
    d.ellipse((*q(-11,12),*q(11,39)),fill='#e2e0d7')
    d.ellipse((*q(-9,38),*q(9,68)),fill='#e2e0d7')
    for side in (-1,1):
        for i in range(3):d.line([q(side*5,26+i*10),q(side*23,14+i*19),q(side*34,10+i*25)],fill='#e2e0d7',width=round(3*s))
    d.polygon([q(-28,-60),q(-12,-78),q(16,-78),q(31,-57),q(22,-24),q(0,-10),q(-24,-26)],fill='#17151c',outline=EDGE,width=3)
    for side in (-1,1):d.polygon([q(side*24,-56),q(side*4,-44),q(side*10,-29),q(side*24,-38)],fill='#eee9dc')


def hunter(d,x,y,s=1):
    q=lambda a,b:(x+a*s,y+b*s)
    d.polygon([q(-60,32),q(60,32),q(69,202),q(-69,202)],fill='#573c2d',outline=EDGE,width=3)
    for side in (-1,1):
        d.line([q(side*52,50),q(side*79,105),q(side*73,190)],fill='#bf8f69',width=round(27*s))
        d.polygon([q(side*12,20),q(side*58,18),q(side*50,143),q(side*16,120)],fill='#c59a52',outline=EDGE,width=3)
        for i in range(5):
            xx=side*(28+11*(i%2));yy=43+17*i
            d.ellipse((*q(xx-4,yy-4),*q(xx+4,yy+4)),fill='#483326')
        d.line([q(side*30,195),q(side*37,300)],fill='#5d4431',width=round(32*s))
    d.polygon([q(-35,-52),q(-20,-78),q(22,-78),q(41,-50),q(32,4),q(0,27),q(-30,2)],fill='#c49976',outline=EDGE,width=3)
    d.polygon([q(-38,-44),q(-36,-65),q(-17,-84),q(24,-80),q(38,-59),q(5,-66),q(-12,-53)],fill='#342627')
    d.line([q(-22,-26),q(-7,-22)],fill='#30232b',width=4)
    d.line([q(6,-22),q(23,-26)],fill='#30232b',width=4)
    d.polygon([q(-22,-5),q(0,-12),q(21,-5),q(10,4),q(0,-1),q(-12,5)],fill='#392629')


def grave(d,ground=545):
    d.polygon([(38,ground),(680,ground-16),(680,942),(38,942)],fill='#4d352d',outline='#b69b79',width=3)
    for i in range(34):
        x=62+i*61%590;y=ground+35+i*71%max(1,900-ground)
        d.line((x,y,x+15,y-4),fill='#806047',width=2)
    d.rounded_rectangle((87,ground-147,229,ground+12),radius=33,fill='#79766b',outline=EDGE,width=3)
    text_box(d,'PARKER',(104,ground-92,112,40),'#ece1c9',23,True,'center',minimum=20)


def hunt_art(layer,scene,second,p,glow):
    d=ImageDraw.Draw(layer);kind=scene['kind'];colors=scene.get('design',{}).get('colors',{})
    if kind=='hunt_burial':
        grave(d,500);hunter(d,516,281,.58)
        d.polygon([(242,682),(563,665),(591,795),(225,815)],fill='#1f1b22',outline=EDGE,width=4)
        d.ellipse((270,695,324,755),fill='#13131a',outline=EDGE,width=2)
        d.polygon([(277,713),(294,720),(286,737),(276,729)],fill='#dedbd0')
        d.polygon([(302,721),(316,714),(316,729),(306,737)],fill='#dedbd0')
        d.line((332,730,538,724),fill='#32313a',width=38)
        for i in range(5):
            x=280+i*56;y=505+((second*55+i*48)%152)
            d.polygon([(x,y),(x+11,y-3),(x+8,y+8)],fill='#ac8a65')
    elif kind=='hunt_hunter':
        # Trophy-room architecture is subdued; the hunter and stolen identity lead.
        for x in (69,492):
            d.rectangle((x,279,x+153,775),outline=colors.get('edge',EDGE),width=4)
            d.line((x+76,300,x+76,750),fill=colors.get('edge',EDGE),width=2)
        hunter(d,260,450,1.17)
        black_spider(d,526,502,.78)
        d.arc((418,356,640,721),second*25,second*25+160,fill='#dbb36c',width=3)
    elif kind=='hunt_impostor':
        for i,x in enumerate(range(38,680,89)):
            top=451+i*39%190;d.rectangle((x,top,x+76,907),fill='#5e5144',outline='#c2a17a',width=2)
            for y in range(top+22,900,49):d.rectangle((x+15,y,x+27,y+17),fill='#cba46d')
        black_spider(d,358,423,1.48,hand=(492+18*math.sin(second),586))
        d.ellipse((475,254,643,422),fill='#704832',outline=EDGE,width=4)
        hunter(d,559,319,.43)
        d.line((512,422,423,490),fill=EDGE,width=3)
    elif kind=='hunt_vermin':
        black_spider(d,204,449,1.0,hand=(366,535))
        d.polygon([(430,575),(482,521),(541,570),(578,778),(402,778)],fill='#6e7857',outline=EDGE,width=3)
        d.ellipse((450,470,524,548),fill='#909372',outline=EDGE,width=3)
        d.polygon([(454,485),(435,459),(466,473)],fill='#99916c')
        d.polygon([(515,485),(541,462),(525,495)],fill='#99916c')
        d.arc((485,679,653,876),270,72,fill='#9c9273',width=12)
        for x in (395,438,481,524,567):d.line((x,397,x,876),fill='#aaa493',width=7)
        d.line((376,397,590,397),fill=EDGE,width=5)
    elif kind=='hunt_coffin':
        d.polygon([(88,355),(615,337),(639,811),(98,850)],fill='#3b2927',outline=EDGE,width=5)
        black_spider(d,365,504,1.1,hand=(457,558+18*math.sin(second*1.2)))
        d.polygon([(101,761),(632,733),(639,811),(98,850)],fill='#5b3d2d',outline='#9a7654',width=3)
        text_box(d,'TWO WEEKS',(170,268,375,55),EDGE,34,True,'center',minimum=26)
    elif kind=='hunt_rise':
        grave(d,671)
        rise=min(1,max(0,(p-.12)/.7));x=385;y=827-391*rise
        black_spider(d,x,y,1.05,hand=(449,690-231*min(1,rise*1.8)))
        # Dirt occludes the body; the hand/body emerge through one connected plane.
        d.polygon([(245,685),(314,659),(344,681),(381,652),(421,683),(463,658),(552,682),(552,935),(245,935)],fill='#4d352d',outline='#af8e68',width=3)
        for i in range(9):
            xx=275+i*31;yy=674-38*math.sin(math.pi*rise+i*.28)
            d.polygon([(xx,yy),(xx+9,yy-5),(xx+15,yy+4)],fill='#b68c60')
    elif kind=='hunt_confront':
        d.rectangle((64,280,654,895),outline=colors.get('edge',EDGE),width=4)
        for y in (365,740):d.line((65,y,654,y),fill=colors.get('edge',EDGE),width=3)
        black_spider(d,209,496,1.0,hand=(339,571))
        hunter(d,520,445,1.05)
        d.line((371,440,371,820),fill='#b99b74',width=2)
    elif kind=='hunt_test':
        black_spider(d,166,557,.8)
        hunter(d,374,422,1.0)
        # The intervening arm crosses the attack path; the threat stops short.
        stop=min(1,p*2);vx=599-55*stop
        d.polygon([(vx-43,549),(vx+30,549),(vx+54,766),(vx-61,766)],fill='#6e7857',outline=EDGE,width=3)
        d.ellipse((vx-34,481,vx+35,553),fill='#909372',outline=EDGE,width=3)
        for side in (-1,1):d.polygon([(vx+side*27,492),(vx+side*45,470),(vx+side*39,511)],fill='#99916c')
        d.line((vx-24,590,vx-118+40*stop,570),fill='#909372',width=20)
        d.line((424,490,471,545,481,594),fill='#bf8f69',width=25,joint='curve')
        d.arc((456,524,503,613),265,95,fill='#efcc85',width=4)
    elif kind=='hunt_confession':
        d.polygon([(77,690),(637,670),(669,835),(57,853)],fill='#775638',outline=EDGE,width=4)
        d.polygon([(216,465),(509,439),(537,704),(231,733)],fill='#e2cfaa',outline='#9f7a50',width=4)
        text_box(d,'CONFESSION',(247,492,242,53),'#523729',29,True,'center',minimum=23)
        for i in range(5):d.line((263,573+i*22,475-(i%2)*26,555+i*22),fill='#836749',width=3)
        # Absence, not an enacted death, carries the final consequence.
        d.arc((245,303,512,547),second*11,second*11+150,fill='#b99b71',width=3)
