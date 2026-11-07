"""Finite ensemble staging for the requested movie recaps and Krakoa rescue."""
import math
from PIL import Image,ImageDraw
from shorts_editor.graphics import text_box
from .lore_screen_cast import actor,EDGE
from .lore_screen import city,car,ring

ENSEMBLE_KINDS=tuple('dw_'+x for x in ('ripper','rejected','tva','grave','variants','void','johnny','car','resistance','helmet','mercy','pyro','portal','army','peter','alone','wires','home'))+tuple('ff_'+x for x in ('family','herald','worldship','bargain','chase','baby','protest','bridges','language','evacuate','galactus','stretch','push','surfer','loss','revive','doom'))+tuple('xm_'+x for x in ('missing','recruits','jungle','prison','island','energy','launch','escape','team'))


def label(d,text,box,color=EDGE,size=25):text_box(d,text,box,color,size,True,'center',minimum=18)


def beam(d,points,color='#d6b36e',width=6):
    d.line(points,fill=EDGE,width=width+4);d.line(points,fill=color,width=width)


def portal(d,x,y,r,t,color='#d5a76d'):
    for n in range(3):
        a=t*45+n*38;d.arc((x-r-n*10,y-r*1.3-n*10,x+r+n*10,y+r*1.3+n*10),a,a+311,fill=color,width=4)


def baby(d,x,y,r=24):
    d.ellipse((x-r,y-r,x+r,y+r),fill='#c5a083',outline=EDGE,width=2)
    d.polygon([(x-r*1.2,y+r*.4),(x+r*1.2,y+r*.4),(x+r*.6,y+r*2.8),(x-r*.7,y+r*2.8)],fill='#ddd2b6',outline=EDGE,width=2)


def prone(layer,who,x,y,s=.8):
    canvas=Image.new('RGBA',layer.size);actor(canvas,who,360,500,s)
    sprite=canvas.crop(canvas.getbbox()).rotate(90,expand=True)
    layer.alpha_composite(sprite,dest=(round(x-sprite.width/2),round(y-sprite.height/2)))


def jet(d,x,y,s=1):
    d.polygon([(x,y-20*s),(x+64*s,y+27*s),(x+36*s,y+30*s),(x+49*s,y+50*s),(x,y+39*s),(x-49*s,y+50*s),(x-36*s,y+30*s),(x-64*s,y+27*s)],fill='#8a918c',outline=EDGE,width=3)


def island(d,x,y,s=1,face=False):
    points=[(-172,31),(-133,-44),(-78,-58),(-20,-96),(44,-77),(74,-36),(144,-19),(177,47),(105,83),(-83,81)]
    d.polygon([(x+a*s,y+b*s) for a,b in points],fill='#65754b',outline=EDGE,width=3)
    for dx in (-98,-58,47,93):
        d.line((x+dx*s,y-9*s,x+(dx+7)*s,y-64*s),fill='#91875a',width=max(3,round(8*s)))
    if face:
        for dx in (-40,40):d.polygon([(x+(dx-15)*s,y-15*s),(x+(dx+18)*s,y-9*s),(x+(dx+6)*s,y+8*s)],fill='#c58c54')
        d.line((x-51*s,y+38*s,x+51*s,y+38*s),fill='#3c3e30',width=max(3,round(8*s)))


def ensemble_art(layer,scene,second,p,glow):
    d=ImageDraw.Draw(layer);k=scene['kind'];c=scene.get('design',{}).get('colors',{});ink=c.get('ink',EDGE)
    e=min(1,max(0,p*1.3));wiggle=math.sin(second*2)*5
    if k=='dw_ripper':
        for x in (160,560):
            d.rectangle((x-49,345,x+49,795),fill='#645847',outline=EDGE,width=4)
            d.ellipse((x-31,376,x+31,438),outline='#d2ad68',width=4)
        beam(d,[(195,508),(302,475),(360,563),(430,475),(525,508)],'#c08d5b',6)
        actor(layer,'deadpool',292,645,.72);actor(layer,'wolverine',452,645,.72)
        label(d,'ONE TIMELINE. ONE DEADLINE.',(107,270,509,48),ink)
    elif k=='dw_rejected':
        d.rectangle((97,359,621,744),outline=EDGE,width=3);d.polygon([(389,600),(608,600),(639,720),(365,720)],fill='#79634d',outline=EDGE,width=3)
        actor(layer,'wade_civilian',205,465,.95);actor(layer,'happy',509,435,1.03,hand=(410,551+wiggle))
        label(d,'AVENGERS APPLICATION: REJECTED',(106,285,510,55),ink)
    elif k=='dw_tva':
        actor(layer,'paradox',174,540,1.0,hand=(315,487))
        d.rectangle((330,319,622,658),fill='#454b48',outline=EDGE,width=4)
        for n in range(3):
            y=403+n*67;d.line((348,y,604,y+wiggle),fill='#be9b64',width=4)
        label(d,'ANCHOR: LOGAN',(350,351,250,40),size=25)
        actor(layer,'deadpool',493,697,.65)
    elif k=='dw_grave':
        d.polygon([(77,735),(645,735),(681,900),(44,900)],fill='#5b4e42',outline=EDGE,width=3)
        d.rounded_rectangle((105,467,248,739),radius=34,fill='#888478',outline=EDGE,width=3)
        label(d,'LOGAN',(121,520,111,42),size=24)
        actor(layer,'deadpool',421,567,1.05,hand=(319,661-22*e))
        for n in range(3):d.line((283+n*17,630,278+n*17,713),fill='#c4c4b7',width=5)
        d.ellipse((303,744,363,793),outline=EDGE,width=4)
    elif k=='dw_variants':
        for n,x in enumerate((164,360,556)):
            portal(d,x,531,67,second+n,'#ac9167');actor(layer,'wolverine',x,526,.49+.12*n)
        label(d,'A DIFFERENT LOGAN',(129,312,463,44),ink)
    elif k=='dw_void':
        d.polygon([(39,743),(195,674),(382,736),(552,649),(682,751),(682,924),(39,924)],fill='#9d7e59',outline=EDGE,width=3)
        actor(layer,'deadpool',246,536,1.0,hand=(359,559+wiggle));actor(layer,'wolverine',494,548,1.0,facing=-1)
        d.ellipse((178,367,525,715),outline='#9b8570',width=2)
    elif k=='dw_johnny':
        actor(layer,'cassandra',513,492,1.1,hand=(393,468))
        actor(layer,'torch',218,527,1.08)
        for n in range(7):
            x=180+n*12;y=486+math.sin(second+n)*24
            d.polygon([(x,y),(x-17,y+71),(x+20,y+63)],fill='#d7954c')
        d.line((389,469,274,478),fill='#d0b9a5',width=3)
        label(d,'CASSANDRA NOVA',(124,306,468,43),ink)
    elif k=='dw_car':
        car(d,364,665,2.35)
        actor(layer,'deadpool',246,523,.71,hand=(385,552+wiggle));actor(layer,'wolverine',456,526,.71,hand=(338,553-wiggle),facing=-1)
        d.line((300,474,344,459,329,492),fill='#d9c5a2',width=4)
    elif k=='dw_resistance':
        for n,who in enumerate(('blade','elektra','gambit','laura')):
            x=135+n*151;actor(layer,who,x,548,.72,hand=(x+51,551+wiggle))
            label(d,who.upper(),(x-64,756,128,36),ink,21)
        label(d,'THE VOID RESISTANCE',(125,323,470,52),ink)
    elif k=='dw_helmet':
        actor(layer,'cassandra',363,530,1.15)
        actor(layer,'deadpool',170,588,.89,hand=(327,424));actor(layer,'wolverine',556,588,.89,hand=(401,424),facing=-1)
        d.pieslice((309,386-14*e,416,488-14*e),180,360,fill='#8c7964',outline=EDGE,width=4)
        d.line((316,434-14*e,409,434-14*e),fill='#77604b',width=12)
    elif k=='dw_mercy':
        actor(layer,'cassandra',433,530,1.12)
        actor(layer,'deadpool',193,585,.88,hand=(291,566))
        actor(layer,'wolverine',583,592,.81,hand=(488,558),facing=-1)
        hx=433-145*e;hy=419+143*e
        d.pieslice((hx-54,hy-49,hx+54,hy+49),180,360,fill='#8c7964',outline=EDGE,width=4)
    elif k=='dw_pyro':
        actor(layer,'cassandra',455,564,1.0)
        actor(layer,'paradox',163,499,.8,hand=(272,528))
        for n in range(4):
            y=650-n*35;x=255+n*24+wiggle;d.polygon([(x,y),(x-23,y+64),(x+25,y+63)],fill='#c58a4c')
        label(d,'PARADOX’S SECRET DEAL',(109,295,511,51),ink)
    elif k=='dw_portal':
        portal(d,467,526,125,second)
        actor(layer,'cassandra',164,539,.94,hand=(317,472))
        actor(layer,'deadpool',351+95*e,577,.78);actor(layer,'wolverine',283+95*e,642,.70)
    elif k=='dw_army':
        city(d,c)
        for row in range(2):
            for col in range(4):actor(layer,'deadpool',123+col*150+wiggle,395+row*180,.40)
        actor(layer,'deadpool',279,677,.70,hand=(390,690));actor(layer,'wolverine',464,671,.78,hand=(359,687),facing=-1)
    elif k=='dw_peter':
        for x in (111,238,485,612):actor(layer,'deadpool',x,553,.55,hand=(x+45,510+wiggle))
        actor(layer,'peter',365,533,1.08,hand=(475,453))
        d.ellipse((325,470,404,560),outline='#a49c88',width=6)
        label(d,'EVERY DEADPOOL KNOWS PETER',(118,307,490,60),ink)
    elif k in ('dw_alone','dw_wires'):
        for x in (115,606):d.rectangle((x-30,315,x+30,832),fill='#6d6658',outline=EDGE,width=4)
        if k=='dw_alone':
            actor(layer,'deadpool',360,519,.96,hand=(581,517),off_hand=(143,517))
            d.rectangle((491,654,644,894),outline=EDGE,width=5)
            actor(layer,'wolverine',568,719,.37,hand=(509,743))
        else:
            actor(layer,'deadpool',264,519,.96,hand=(354,552),off_hand=(143,517))
            actor(layer,'wolverine',456,519,.96,hand=(581,517),off_hand=(354,552))
            d.ellipse((345,543,363,561),fill='#dec088',outline=EDGE,width=2)
        for n in range(7):
            y=391+n*61;x=359+math.sin(second*5+n)*17
            d.line((x-14,y,x+14,y+20,x-3,y+37),fill='#e9c989',width=4)
    elif k=='dw_home':
        actor(layer,'deadpool',187,470,.87);actor(layer,'wolverine',365,465,.87);actor(layer,'laura',536,527,.70)
        d.polygon([(94,654),(623,654),(662,780),(53,780)],fill='#98764f',outline=EDGE,width=3)
        for x in (176,366,542):d.ellipse((x-35,669,x+35,694),outline=EDGE,width=3)
        d.line((358,329,358,399+wiggle),fill='#ad916b',width=3)
        d.ellipse((540,801,599,842),fill='#9c7d61',outline=EDGE,width=2)
        d.ellipse((592,793,627,824),fill='#9c7d61',outline=EDGE,width=2)
        d.polygon([(600,793),(611,780),(619,799)],fill='#8c6a50',outline=EDGE,width=2)
        for x in (553,582):d.line((x,831,x,861),fill='#9c7d61',width=7)
    elif k=='ff_family':
        city(d,c)
        for n,who in enumerate(('reed','sue','thing','johnny')):actor(layer,who,127+n*155,514,.73 if who!='thing' else .89)
        baby(d,291,590,20);label(d,'EARTH-828 · A FAMILY OF FOUR',(94,303,533,50),ink)
    elif k=='ff_herald':
        city(d,c)
        d.ellipse((307,617+wiggle,584,647+wiggle),fill='#b2b4a9',outline=EDGE,width=3)
        actor(layer,'surfer',442,429+wiggle,.8,hand=(556,408))
        actor(layer,'reed',162,653,.65);actor(layer,'sue',284,657,.65)
        label(d,'EARTH IS NEXT',(163,291,390,49),ink,29)
    elif k=='ff_worldship':
        d.ellipse((191,285,612,706),fill='#5c5266',outline=EDGE,width=4)
        for n in range(6):d.arc((221+n*15,315+n*15,582-n*15,676-n*15),second*8,second*8+270,fill='#a68e72',width=3)
        jet(d,161+65*e,754-60*e,.87)
        d.ellipse((97,411,188,502),fill='#a87a51',outline=EDGE,width=3)
    elif k=='ff_bargain':
        actor(layer,'galactus',490,391,1.62,hand=(335,581))
        actor(layer,'reed',159,644,.59);actor(layer,'sue',278,646,.59)
        baby(d,279,663,16);label(d,'THE CHILD FOR THE PLANET',(109,279,505,53),ink)
    elif k=='ff_chase':
        center=(497,522);glow(layer,center,122,(224,201,146),80);d=ImageDraw.Draw(layer)
        for n in range(3):d.ellipse((center[0]-95-n*11,center[1]-95-n*11,center[0]+95+n*11,center[1]+95+n*11),outline='#d7c293',width=3)
        a=2.0+e*1.9;x=497+math.cos(a)*175;y=522+math.sin(a)*175;jet(d,x,y,.78)
        d.ellipse((179,688,348,708),fill='#b3b4a5',outline=EDGE,width=3);actor(layer,'surfer',265,587,.45)
    elif k=='ff_baby':
        actor(layer,'sue',304,493,1.03,hand=(384,582+wiggle));actor(layer,'reed',530,514,.88,hand=(402,597))
        baby(d,371,576,35);d.arc((173,357,520,766),200,334,fill='#bda477',width=4)
    elif k=='ff_protest':
        actor(layer,'sue',360,502,1.06,hand=(431,562));baby(d,424,562,24)
        for n,x in enumerate((104,212,511,615)):
            actor(layer,'writer',x,707,.48)
            d.rectangle((x-45,590+wiggle,x+45,646+wiggle),fill='#c9b58f',outline='#796148',width=3)
        label(d,'SAVE OUR CHILD. SAVE EVERYONE.',(92,293,539,65),ink)
    elif k=='ff_bridges':
        for n,x in enumerate((148,360,572)):
            portal(d,x,524,65,second+n,'#bc9c66')
            if n<2 and p>.4:d.line((x-69,420,x+69,632),fill='#b96948',width=7)
        d.ellipse((272,741,449,918),fill='#7f967d',outline=EDGE,width=3)
        label(d,'MOVE EARTH — OR MOVE GALACTUS',(86,293,547,63),ink,24)
    elif k=='ff_language':
        actor(layer,'torch',181,561,.96,hand=(313,488));actor(layer,'surfer',522,536,.96)
        d.rectangle((297,425,421,574),fill='#655b55',outline=EDGE,width=3)
        for n in range(5):
            y=447+n*20;d.line((313,y,403,y+wiggle),fill='#bcaa83',width=2)
        label(d,'SHALLA-BAL · ZENN-LA',(116,293,491,55),ink)
    elif k=='ff_evacuate':
        city(d,c);d.polygon([(71,719),(650,719),(597,900),(127,900)],fill='#5b5548',outline=EDGE,width=4)
        for n in range(5):actor(layer,'writer',187+n*82,672+n*15,.3)
        d.line((217,822,533,822),fill='#bcaa82',width=5);d.polygon([(540,822),(517,806),(517,838)],fill=EDGE)
        label(d,'EVACUATE UNDERGROUND',(101,297,518,51),ink)
    elif k=='ff_galactus':
        city(d,c);actor(layer,'galactus',423,379,1.81,hand=(226,598));baby(d,221,612,27)
        portal(d,151,660,70,second)
    elif k=='ff_stretch':
        actor(layer,'galactus',498,388,1.49,hand=(316,449))
        actor(layer,'reed',210,584,.91,hand=(316,449))
        actor(layer,'thing',385,714-85*e,1.02,hand=(485,552))
        beam(d,[(259,600),(338,572),(410,572)],'#a7bac1',4)
    elif k=='ff_push':
        portal(d,522,526,107,second);actor(layer,'galactus',408+70*e,428,1.51)
        actor(layer,'sue',159,649,.86,hand=(267,558));d.arc((177,400,416,810),270,90,fill='#d5d7bd',width=8)
        actor(layer,'reed',291,749,.42);baby(d,318,770,13)
    elif k=='ff_surfer':
        portal(d,506,532,123,second);actor(layer,'galactus',463,429,1.35)
        d.ellipse((200+129*e,683,380+129*e,704),fill='#c1bfb0',outline=EDGE,width=3)
        actor(layer,'surfer',289+129*e,539,.72,hand=(432+55*e,514))
        actor(layer,'torch',141,733,.48)
    elif k in ('ff_loss','ff_revive'):
        d.polygon([(139,741),(472,741),(505,816),(107,816)],fill='#9a805f',outline=EDGE,width=3)
        actor(layer,'reed',530,546,.93,hand=(402,684))
        if k=='ff_loss' or p<.64:prone(layer,'sue',318,709,.84)
        else:actor(layer,'sue',321,622,.92)
        baby(d,354,649,28)
        if k=='ff_revive':
            glow(layer,(354,700),80,(235,211,154),round(60+55*e))
            d=ImageDraw.Draw(layer);d.arc((236,565,448,791),second*35,second*35+245,fill='#dfc794',width=4)
    elif k=='ff_doom':
        actor(layer,'sue',158,514,.89);actor(layer,'doom',517,476,1.13,hand=(383,657+wiggle));baby(d,366,659,25)
        d.rectangle((276,720,456,859),fill='#96835e',outline=EDGE,width=3)
        label(d,'FOUR YEARS LATER',(114,293,494,52),ink)
    elif k=='xm_missing':
        island(d,365,622,1.45)
        actor(layer,'cyclops',146,461,.75)
        for n in range(3):
            x=344+n*85;d.ellipse((x-24,583,x+24,631),outline='#cfc4a2',width=3)
        label(d,'ONLY CYCLOPS CAME BACK',(110,297,510,56),ink)
    elif k=='xm_recruits':
        cast=('wolverine','storm','nightcrawler','colossus','sunfire','banshee','thunderbird')
        for n,who in enumerate(cast):
            x=128+(n%4)*151;y=435+(n//4)*247;actor(layer,who,x,y,.49)
        d.line((106,819,604,819+wiggle),fill='#bba273',width=3)
    elif k=='xm_jungle':
        for n,x in enumerate((91,225,498,620)):
            d.line((x,340,x-20,868),fill='#8b845b',width=10)
            d.polygon([(x-55,408),(x+20,327),(x+70,446)],fill='#5a6b48',outline=EDGE,width=2)
        actor(layer,'wolverine',245,573,.85,hand=(357,535));actor(layer,'nightcrawler',477,574,.8)
        portal(d,477,630,92,second,'#9e80ac')
    elif k=='xm_prison':
        for n,who in enumerate(('jean','polaris','iceman')):
            x=180+n*180;actor(layer,who,x,495,.77)
            for dx in (-31,31):d.line((x+dx,384,x+dx+wiggle,769),fill='#718452',width=11)
        label(d,'CAPTIVES, NOT AN ABANDONED TEAM',(95,301,530,54),ink,24)
    elif k=='xm_island':
        island(d,370,552,1.66,True);actor(layer,'cyclops',167,743,.49);actor(layer,'wolverine',493,743,.49)
        for n in range(3):beam(d,[(190+n*30,796),(300,697),(379,661)],'#b7b779',3)
        label(d,'KRAKOA IS THE MUTANT',(111,299,503,52),ink)
    elif k=='xm_energy':
        actor(layer,'storm',169,457,.78,hand=(310,476));actor(layer,'polaris',421,537,1.02,hand=(546,475))
        actor(layer,'cyclops',164,738,.43)
        actor(layer,'havok',578,739,.43)
        beam(d,[(194,415),(267,456),(248,495),(365,516)],'#d9ce9f',6)
        beam(d,[(173,716),(350,558)],'#b75a48',4)
        beam(d,[(574,756),(487,599)],'#d0c8a4',4)
        ring(d,424,572,133,second,'#b4c391')
    elif k=='xm_launch':
        d.ellipse((102,594,609,1101),fill='#667f76',outline=EDGE,width=4)
        island(d,358,521-139*e,.72,True)
        for n in range(5):
            a=n*.55;d.line((215+n*63,690,231+n*61,620-80*e),fill='#c4c597',width=4)
        label(d,'OFF THE PLANET',(131,296,458,52),ink)
    elif k=='xm_escape':
        for n in range(6):
            r=40+n*31;d.arc((360-r,626-r*.55,360+r,626+r*.55),second*45+n*30,second*45+n*30+240,fill='#93aaa0',width=3)
        jet(d,351+32*e,463-69*e,1.5)
        actor(layer,'storm',514,505,.43);actor(layer,'cyclops',194,505,.42)
    elif k=='xm_team':
        for n,who in enumerate(('cyclops','storm','wolverine','nightcrawler','colossus')):
            actor(layer,who,122+n*120,529,.59,hand=(164+n*120,539+wiggle))
        label(d,'A RESCUE BECOMES A NEW TEAM',(97,310,529,59),ink)
