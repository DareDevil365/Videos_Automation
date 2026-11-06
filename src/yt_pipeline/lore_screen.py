"""Authored film/TV recap shots: recognizable cast, connected action and late reveals."""
import math
from PIL import ImageDraw
from shorts_editor.graphics import text_box
from .lore_screen_cast import actor,shield,EDGE


SCREEN_KINDS=tuple('cw_'+k for k in ('lagos','grief','accords','funeral','vienna','chase','interrogation','helicopter','soldier_map','wanda_exit','gear','teams','shield','giant','escape','fall','raft','truth','bunker','soldiers','zemo','tape','fight','arm_loss','reactor_disabled','shield_drop','arrest','rescue','rehab','letter','wakanda'))+tuple('ss_'+k for k in ('clock','car','dormammu','routes','absolute','warning','book','library','absorb','split','duel','consume','revive','collapse','watcher','prison','alone'))+('end_subscribe',)


def label(d,text,box,size=28,color=EDGE):text_box(d,text,box,color,size,True,'center',minimum=18)


def ring(d,x,y,r,time,color='#e4ac58'):
    for scale in (1,.84,.66):d.arc((x-r*scale,y-r*scale,x+r*scale,y+r*scale),time*65,time*65+305,fill=color,width=3)
    pts=[(x+r*.75*math.cos(i*math.tau/6+time*.4),y+r*.75*math.sin(i*math.tau/6+time*.4)) for i in range(7)]
    d.line(pts,fill=color,width=2)


def city(d,colors,night=False):
    for i,x in enumerate(range(42,680,85)):
        top=330+(i*53)%180
        d.rectangle((x,top,x+71,881),fill=colors.get('wall','#6d6254'),outline=colors.get('edge',EDGE),width=2)
        for y in range(top+24,855,52):
            for dx in (14,43):d.rectangle((x+dx,y,x+dx+12,y+21),fill='#cca16b' if night else '#b1a38b')
    d.line((35,880,682,880),fill=EDGE,width=4)


def chamber(d,colors,*,ice=False):
    edge=colors.get('edge',EDGE);wall=colors.get('wall','#61564e')
    d.polygon([(40,326),(360,264),(680,326),(680,916),(40,916)],fill=wall,outline=edge,width=3)
    for x in (80,561):
        d.rectangle((x,324,x+79,853),outline=edge,width=3)
        for y in (405,587,775):d.line((x,y,x+79,y),fill=edge,width=2)
    for x in range(60,680,95):d.line((360,650,x,913),fill=edge,width=1)
    d.line((40,650,680,650),fill=edge,width=2)
    if ice:
        for x in (47,610):d.polygon([(x,330),(x+30,355),(x+43,419),(x+18,392)],fill='#d4d0be')


def runway(d):
    d.rectangle((36,548,685,911),fill='#827c6c',outline=EDGE,width=3)
    d.polygon([(80,380),(594,380),(670,548),(43,548)],fill='#b7ac94',outline=EDGE,width=3)
    for x in range(95,650,77):d.line((x,400,x+35,530),fill='#7b7468',width=3)
    for y in (637,735,837):d.line((330,y,390,y),fill='#e2c879',width=9)


def car(d,x,y,s=1):
    q=lambda a,b:(x+a*s,y+b*s)
    d.polygon([q(-110,20),q(-99,-21),q(-54,-34),q(-20,-72),q(53,-68),q(86,-31),q(113,-10),q(110,23)],fill='#494443',outline=EDGE,width=3)
    d.polygon([q(-38,-34),q(-11,-60),q(46,-57),q(71,-30)],fill='#9a9b94',outline=EDGE,width=2)
    for dx in (-66,68):d.ellipse((x+(dx-19)*s,y+4*s,x+(dx+19)*s,y+42*s),fill='#24252a',outline=EDGE,width=3)
    d.line([q(-85,-17),q(-62,-17)],fill='#dcbb6d',width=5)


def beam(d,start,end,color='#dfbd73',width=7):
    d.line([start,end],fill='#f1ddbb',width=width+7)
    d.line([start,end],fill=color,width=width)


def screen_art(layer,scene,second,p,glow):
    d=ImageDraw.Draw(layer);k=scene['kind'];c=scene.get('design',{}).get('colors',{});ease=min(1,max(0,p*1.5))
    if k=='cw_lagos':
        city(d,c);actor(layer,'cap',173,605,.73);actor(layer,'wanda',493,557,.88,hand=(446,446))
        center=(398,440-130*ease);glow(layer,center,85,(245,112,57),125);d=ImageDraw.Draw(layer)
        for i in range(9):
            a=i*math.tau/9;r=30+35*ease
            d.polygon([(center[0]+math.cos(a)*r,center[1]+math.sin(a)*r),(center[0]+math.cos(a+.25)*r*.58,center[1]+math.sin(a+.25)*r*.58),(center[0]+math.cos(a+.5)*r,center[1]+math.sin(a+.5)*r)],fill='#f4b16c')
        ring(d,center[0],center[1],94,second,'#d87279')
    elif k=='cw_grief':
        actor(layer,'tony',220,532,1.13)
        d.rounded_rectangle((410,370,617,662),radius=8,fill='#b49974',outline=EDGE,width=4)
        d.ellipse((460,412,567,520),fill='#655c50',outline=EDGE,width=3)
        d.polygon([(441,606),(460,523),(563,523),(584,606)],fill='#7b7661',outline=EDGE,width=3)
        label(d,'SOKOVIA',(405,690,228,47),27)
        d.line((312,568,392,543),fill='#ba9a69',width=3)
    elif k=='cw_accords':
        actor(layer,'steve',153,488,.95);actor(layer,'tony',564,488,.95)
        d.polygon([(282,343),(437,343),(455,676),(269,676)],fill='#d9c59f',outline='#84704e',width=3)
        label(d,'SOKOVIA\nACCORDS',(284,389,146,111),24,'#47382b')
        for y in range(526,630,22):d.line((294,y,425,y),fill='#8d795b',width=2)
        d.line((360,690,360,886),fill='#b86d59',width=5)
        for x in (255,465):d.polygon([(x,757),(x+(-20 if x<360 else 20),741),(x+(-20 if x<360 else 20),773)],fill=EDGE)
    elif k=='cw_funeral':
        d.polygon([(173,703),(506,703),(574,787),(106,787)],fill='#675047',outline=EDGE,width=4)
        for x in range(199,510,53):d.ellipse((x-9,679,x+9,697),fill='#d8cbb2',outline=EDGE)
        actor(layer,'cap',362,439,.72,cape=False)
        label(d,'PEGGY CARTER',(148,813,423,51),29)
    elif k=='cw_vienna':
        chamber(d,c);d.polygon([(266,472),(453,472),(476,690),(245,690)],fill='#bca57e',outline=EDGE,width=4)
        for i in range(8):
            a=i*.8;r=40+180*ease;x=360+math.cos(a)*r;y=532+math.sin(a)*r
            d.polygon([(x,y),(x+18,y-8),(x+25,y+16)],fill='#d4aa75')
        glow(layer,(360,528),115,(224,154,88),110)
        actor(layer,'tchalla',563,599,.72)
    elif k=='cw_chase':
        city(d,c);travel=45*math.sin(p*math.pi)
        actor(layer,'bucky',255+travel,536,.86,hand=(335+travel,591))
        actor(layer,'panther',503-30*p,488,.98,hand=(398,586))
        actor(layer,'cap',109,626,.65)
        for y in (730,811):d.line((50,y,179,y-12),fill='#aa9575',width=3)
    elif k=='cw_interrogation':
        chamber(d,c);d.rectangle((387,316,638,814),outline=EDGE,width=4)
        actor(layer,'zemo',210,550,.86);actor(layer,'bucky',512,536,.92)
        d.polygon([(237,568),(310,557),(321,618),(248,629)],fill='#a44e44',outline=EDGE,width=3)
        for radius in (39,65,91):d.arc((512-radius,455-radius,512+radius,455+radius),second*65,second*65+230,fill='#be7771',width=2)
    elif k=='cw_helicopter':
        d.polygon([(44,785),(675,785),(675,913),(44,913)],fill='#71695b',outline=EDGE,width=4)
        hx=478+12*math.sin(second*2);hy=480-13*ease
        d.ellipse((hx-114,hy-45,hx+117,hy+56),fill='#6f736b',outline=EDGE,width=4)
        d.polygon([(hx+94,hy-7),(hx+186,hy-38),(hx+190,hy-19),(hx+104,hy+30)],fill='#686b62',outline=EDGE,width=3)
        d.line((hx,hy-46,hx,hy-93),fill=EDGE,width=5)
        d.line((hx-158,hy-95,hx+154,hy-95),fill='#d3ccba',width=5)
        d.ellipse((hx-89,hy-29,hx-12,hy+26),fill='#3c4b4b',outline=EDGE,width=2)
        grip=(hx-73,hy+66);d.line((hx-79,hy+51,hx-66,hy+74),fill=EDGE,width=6)
        actor(layer,'steve_civilian',252,653,1.02,hand=grip)
        # The other hand stays on the roof edge; both anchors remain visible.
        d.line((207,682,167,758,146,787),fill=EDGE,width=19,joint='curve')
    elif k=='cw_soldier_map':
        d.polygon([(84,403),(285,325),(568,378),(645,543),(534,707),(206,686),(66,556)],fill='#8b8270',outline=EDGE,width=4)
        for x in (193,264,335,406,477):d.rounded_rectangle((x,465,x+44,603),radius=17,fill='#4b5150',outline=EDGE,width=3)
        label(d,'FIVE MORE WINTER SOLDIERS',(101,764,520,68),30)
        ring(d,543,404,38,second,'#d8b17b')
    elif k=='cw_wanda_exit':
        chamber(d,c);actor(layer,'wanda',214,500,1.01,hand=(350,581))
        actor(layer,'vision',498,503+211*ease,.87)
        actor(layer,'hawkeye',108,655,.55)
        ring(d,492,630,110,second,'#bc6373')
        d.line((351,581,483,590),fill='#c87886',width=4)
        d.polygon([(392,843),(609,843),(648,913),(353,913)],fill='#36312f',outline=EDGE,width=3)
    elif k=='cw_gear':
        d.polygon([(80,691),(633,691),(662,806),(52,806)],fill='#79614b',outline=EDGE,width=4)
        shield(d,295,650,83);d.polygon([(427,588),(526,588),(539,676),(411,676)],fill='#675d51',outline=EDGE,width=3)
        d.line((459,589,459,566,499,566,499,589),fill=EDGE,width=5)
        actor(layer,'sharon',581,426,.61)
        label(d,'SHARON RETURNS THEIR EQUIPMENT',(74,827,574,56),26)
    elif k=='cw_teams':
        runway(d)
        left=['cap','bucky','falcon','wanda','hawkeye','ant'];right=['iron','war','widow','panther','vision','spider']
        for crew,xbase in ((left,93),(right,442)):
            for i,who in enumerate(crew):
                x=xbase+(i%3)*94;y=395+(i//3)*252
                actor(layer,who,x,y,.45)
                label(d,{'iron':'IRON MAN','cap':'CAP','war':'RHODEY','ant':'ANT-MAN','panther':'PANTHER','spider':'SPIDER-MAN'}.get(who,who.upper()),(x-44,y+111,88,55),19)
        d.line((359,338,359,897),fill='#dbc294',width=3)
    elif k=='cw_shield':
        runway(d);actor(layer,'cap',170,568,.95)
        sx=536-40*ease;sy=558-153*math.sin(math.pi*ease)
        actor(layer,'spider',sx,sy,1.05,hand=(396,sy+71))
        cx=221+175*ease;cy=613-90*ease
        d.line((396,sy+71,cx,cy),fill='#e6dfcd',width=3);shield(d,cx,cy,62)
        d.polygon([(442,809),(641,809),(667,859),(429,859)],fill='#777b70',outline=EDGE,width=3)
        for x in (467,623):d.ellipse((x-17,848,x+17,882),fill='#3f4140',outline=EDGE,width=2)
    elif k=='cw_giant':
        runway(d);actor(layer,'ant',366,383,1.73,hand=(538,439))
        actor(layer,'spider',107,738,.37,hand=(201,735));actor(layer,'iron',607,660,.47)
        d.line((143,772,436,797),fill='#e6dfcd',width=3)
        d.line((144,780,436,805),fill='#e6dfcd',width=2)
    elif k=='cw_escape':
        runway(d);actor(layer,'widow',372,576,.95,hand=(470,604));actor(layer,'panther',556,519,.91)
        d.line((470,604,498,571),fill='#b4d8d5',width=6)
        actor(layer,'cap',117,648,.62);actor(layer,'bucky',224,638,.62)
        d.polygon([(51,397),(230,352),(339,442),(210,468),(107,446)],fill='#666e69',outline=EDGE,width=3)
    elif k=='cw_fall':
        actor(layer,'vision',213,386,.6);actor(layer,'falcon',481,477,.53)
        y=550+200*ease;actor(layer,'war',390,y,.73);actor(layer,'iron',599,514+180*ease,.65,hand=(493,689+80*ease))
        beam(d,(213,344),(390,548),'#e2be6b',4)
        for x in (335,390,445):d.line((x,y-135,x-8,y-84),fill='#bba67e',width=3)
    elif k=='cw_raft':
        d.polygon([(70,503),(647,503),(674,767),(48,767)],fill='#777467',outline=EDGE,width=4)
        for n,who in enumerate(('falcon','wanda','hawkeye','ant')):
            x=149+n*142;actor(layer,who,x,565,.49)
            for xx in (x-45,x-15,x+15,x+45):d.line((xx,492,xx,762),fill='#b9b3a3',width=5)
        for i in range(5):d.line((35,805+i*17,683,805+i*17),fill='#887c6b',width=2)
    elif k=='cw_truth':
        actor(layer,'iron',206,526,1.08)
        d.rounded_rectangle((394,367,646,694),radius=13,fill='#b9ac8e',outline=EDGE,width=4)
        d.ellipse((467,402,573,507),fill='#766a60',outline='#493e36',width=3)
        for y in (553,579,605):d.line((425,y,609,y),fill='#796751',width=4)
        label(d,'BUCKY WAS FRAMED',(393,717,251,66),26)
    elif k=='cw_bunker':
        chamber(d,c,ice=True);actor(layer,'cap',179,554,.8);actor(layer,'bucky',339,559,.8);actor(layer,'iron',541,538,.91)
    elif k=='cw_soldiers':
        chamber(d,c,ice=True)
        for i in range(5):
            x=79+i*117;d.rounded_rectangle((x,365,x+93,792),radius=28,fill='#484b45',outline=EDGE,width=4)
            d.ellipse((x+25,408,x+69,455),fill='#6c6a5d',outline=EDGE,width=2)
            d.polygon([(x+21,478),(x+74,478),(x+80,685),(x+12,685)],fill='#5a5b50')
            d.line((x+22,411,x+69,454),fill='#a67666',width=3)
    elif k=='cw_tape':
        d.rounded_rectangle((81,293,641,648),radius=9,fill='#24272a',outline=EDGE,width=5)
        d.rectangle((101,314,621,625),fill='#88806c')
        car(d,303,529,1.0);actor(layer,'bucky',524,441,.52)
        label(d,'1991 · HOWARD + MARIA STARK',(110,337,501,51),25,'#272a28')
        for y in range(324,625,15):d.line((104,y,617,y),fill='#7a7567',width=1)
        actor(layer,'iron',225,702,.65);actor(layer,'cap',501,721,.58)
    elif k=='cw_zemo':
        chamber(d,c,ice=True);actor(layer,'zemo',470,500,1.17)
        d.rectangle((374,323,635,875),outline='#bda18c',width=5)
        d.polygon([(102,421),(282,410),(303,647),(112,659)],fill='#b2a17f',outline=EDGE,width=4)
        for x,scale in ((151,.8),(208,1),(259,.65)):
            d.ellipse((x-15*scale,476-18*scale,x+15*scale,476+18*scale),fill='#6c5e50')
            d.polygon([(x-19*scale,505),(x+19*scale,505),(x+24*scale,595),(x-24*scale,595)],fill='#706855')
        label(d,'SOKOVIA',(104,685,202,48),26)
    elif k=='cw_fight':
        chamber(d,c,ice=True);actor(layer,'iron',538,489,1.13,hand=(405,561))
        actor(layer,'steve',236,553,1.07,hand=(359,591));shield(d,366,565,80)
        actor(layer,'bucky',104,698,.57,hand=(190,684))
        beam(d,(405,561),(390,567),'#cae3dc',8)
        glow(layer,(396,565),47,(226,188,103),125)
    elif k=='cw_shield_drop':
        chamber(d,c,ice=True);actor(layer,'iron',516,653,.76)
        actor(layer,'steve',188,536,.91);actor(layer,'bucky',298,571,.8,missing_arm=True)
        y=680+178*ease;shield(d,375,y,58)
        d.line((365,760,365,793),fill='#c7b795',width=3)
    elif k=='cw_arm_loss':
        chamber(d,c,ice=True);actor(layer,'iron',200,529,1.0,hand=(336,568))
        actor(layer,'bucky',531,553,1.01,missing_arm=True)
        beam(d,(336,568),(483,563),'#cce0d8',7)
        for i in range(7):
            a=i*.8;r=25+45*ease;x=483+math.cos(a)*r;y=563+math.sin(a)*r
            d.polygon([(x,y),(x+9,y-6),(x+16,y+9)],fill='#c3bdab')
    elif k=='cw_reactor_disabled':
        chamber(d,c,ice=True);actor(layer,'iron',471,655,.95)
        actor(layer,'steve',281,505,1.05,hand=(428,676))
        shield(d,431,681,75);glow(layer,(465,697),42,(220,170,98),round(90*(1-ease)))
    elif k=='cw_arrest':
        d.polygon([(45,740),(193,644),(339,708),(518,629),(681,744),(681,922),(45,922)],fill='#c1bba7',outline=EDGE,width=3)
        actor(layer,'tchalla',262,477,1.0,hand=(400,610));actor(layer,'zemo',493,568,.88)
        label(d,'JUSTICE, NOT REVENGE',(100,828,520,50),30)
    elif k=='cw_rescue':
        chamber(d,c);actor(layer,'cap',181,574,.83)
        for i,who in enumerate(('falcon','wanda','hawkeye','ant')):actor(layer,who,330+i*83,590,.43)
        d.line((270,335,270,840),fill=EDGE,width=5);d.line((284,335,284,840),fill=EDGE,width=5)
    elif k=='cw_rehab':
        chamber(d,c);actor(layer,'rhodey',294,515,1.05);actor(layer,'tony',542,529,.98,hand=(423,601))
        for x in (254,334):
            d.line((x,650,x,757,x+4,855),fill='#c9c9b9',width=9)
            d.ellipse((x-10,747,x+10,767),fill='#686b63',outline=EDGE,width=3)
        d.line((192,685,192,875),fill=EDGE,width=5)
    elif k=='cw_letter':
        d.polygon([(175,351),(530,351),(554,719),(158,719)],fill='#dfcaa6',outline='#8b6c49',width=4)
        for y in range(410,661,32):d.line((211,y,489-(y%3)*17,y),fill='#8f765b',width=3)
        d.rounded_rectangle((391,634,488,807),radius=12,fill='#43413b',outline=EDGE,width=4)
        d.rectangle((404,654,476,750),fill='#a9a58a')
        d.line((70,857,651,857),fill='#8c7354',width=5)
    elif k=='cw_wakanda':
        for x in (55,613):
            d.line((x,450,x,882),fill='#70694c',width=12)
            for yy in (370,450,530):d.polygon([(x-56,yy+81),(x,yy),(x+57,yy+81)],fill='#6d7750',outline='#b1aa77',width=2)
        d.rounded_rectangle((245,321,477,849),radius=50,fill='#6e7971',outline=EDGE,width=5)
        actor(layer,'bucky',361,461,.91,missing_arm=True)
        for y in (391,765):d.line((259,y,463,y),fill='#baccc0',width=6)
        label(d,'WAKANDA',(232,865,257,40),29)
    elif k=='ss_clock':
        actor(layer,'strange',364,559,1.25,hand=(442,552))
        ring(d,439,553,123,second,'#a4bc73');glow(layer,(439,553),90,(128,187,105),70)
        for i in range(12):
            a=i*math.tau/12;d.line((439+104*math.cos(a),553+104*math.sin(a),439+115*math.cos(a),553+115*math.sin(a)),fill='#d4d6a3',width=3)
    elif k=='ss_car':
        city(d,c,True);car(d,357,676,1.85)
        d.ellipse((325,539,357,574),fill='#a07d61');d.ellipse((383,537,415,571),fill='#a77a63')
        d.line((270,802,568,850),fill='#9f8b68',width=4)
        for i in range(4):d.line((76,830+i*17,179,810+i*17),fill='#b5a382',width=2)
    elif k=='ss_dormammu':
        d.polygon([(433,290),(616,355),(653,484),(609,667),(502,739),(414,667),(368,502)],fill='#653e59',outline='#d3967f',width=4)
        d.polygon([(427,463),(501,481),(471,511)],fill='#e7b770');d.polygon([(526,479),(603,460),(559,511)],fill='#e7b770')
        actor(layer,'strange',173,650,.73,hand=(261,678));ring(d,257,677,60,second,'#9fbe7d')
    elif k=='ss_routes':
        center=(366,575);ring(d,*center,209,second,'#c7b57c')
        for i in range(3):
            a=i*math.tau/3-second*.35;x=center[0]+155*math.cos(a);y=center[1]+155*math.sin(a)
            car(d,x,y,.6)
        actor(layer,'christine',366,526,.46)
    elif k=='ss_absolute':
        for x,title in ((159,'LOSS'),(365,'MAGIC'),(567,'TIME')):
            d.ellipse((x-68,464,x+68,600),fill='#6c5d57',outline=EDGE,width=4)
            label(d,title,(x-65,510,130,40),24)
        for x in (236,440):d.line((x,531,x+50,531),fill='#c2a46e',width=5)
        actor(layer,'ancient',360,734,.5)
        d.arc((124,375,601,741),195,345,fill='#c2a46e',width=3)
    elif k=='ss_warning':
        actor(layer,'ancient',221,489,1.1,hand=(355,511));actor(layer,'strange',535,563,.94)
        ring(d,413,402,102,second,'#9e855b')
        d.line((370,326,425,381,389,421,452,476),fill='#ba635d',width=7)
    elif k=='ss_book':
        d.polygon([(103,429),(360,393),(618,429),(594,755),(360,715),(124,755)],fill='#b9a482',outline=EDGE,width=5)
        d.line((360,398,360,714),fill='#765943',width=5)
        for yy in range(476,691,36):d.line((149,yy,322,yy-14),fill='#8e7057',width=3)
        ring(d,479,563,78,second,'#8d5f78')
        d.line((423,688,534,674),fill='#8e7057',width=3)
    elif k=='ss_library':
        for x in (57,496):
            d.rectangle((x,300,x+168,870),fill='#594230',outline=EDGE,width=3)
            for yy in range(378,850,95):
                d.line((x,yy,x+168,yy),fill='#b69569',width=4)
                for i in range(6):d.rectangle((x+9+i*26,yy-62,x+22+i*26,yy-3),fill=('#98744c','#8b4652','#717451')[i%3])
        actor(layer,'strange',362,496,1.05)
        d.polygon([(263,688),(360,669),(459,688),(443,752),(360,731),(276,752)],fill='#d9c49f',outline=EDGE,width=3)
    elif k=='ss_absorb':
        actor(layer,'supreme',368,546,1.12,hand=(447,572))
        for i in range(3):
            a=i*2.2+second*.37;r=223*(1-.65*ease);x=365+math.cos(a)*r;y=579+math.sin(a)*r
            d.ellipse((x-35,y-31,x+35,y+31),fill=('#987149','#8e616d','#6e7655')[i],outline=EDGE,width=3)
            d.polygon([(x-27,y-17),(x-41,y-49),(x-9,y-26)],fill='#bd9568')
            d.ellipse((x-15,y-7,x-5,y+3),fill='#e2ca9d');d.ellipse((x+6,y-7,x+16,y+3),fill='#e2ca9d')
            d.line((x,y,368,582),fill='#bb8fbd',width=3)
        glow(layer,(368,583),68,(191,117,181),100)
    elif k=='ss_split':
        actor(layer,'ancient',363,385,.55)
        actor(layer,'strange',181,590,.93);actor(layer,'supreme',544,590,.93)
        for target in ((181,487),(544,487)):d.line((363,437,*target),fill='#d9ba7e',width=4)
        d.line((362,484,362,875),fill='#b9a383',width=3)
    elif k in ('ss_duel','ss_consume'):
        consume=ease if k=='ss_consume' else 0
        actor(layer,'supreme',525,530,1.05,hand=(404,555))
        actor(layer,'strange',191+266*consume,542,.95*(1-.75*consume),hand=(310+90*consume,568))
        ring(d,315+87*consume,568,75*(1-.7*consume),second,'#d6a467')
        beam(d,(404,555),(315+80*consume,568),'#c082b0',6)
        glow(layer,(401,559),49+65*consume,(176,103,167),90)
    elif k=='ss_revive':
        actor(layer,'supreme',234,566,1.13,hand=(354,587));actor(layer,'christine',512+14*ease,614,.83,hand=(459,647))
        # Added forms show the absorbed creatures without replacing his costume.
        for side in (-1,1):d.polygon([(234+side*25,470),(234+side*76,399),(234+side*40,487)],fill='#775373',outline=EDGE,width=3)
        ring(d,511,645,131,second,'#d1b57d')
    elif k=='ss_collapse':
        actor(layer,'supreme',261,572,1.0,hand=(371,614));actor(layer,'christine',472,622,.79)
        for i in range(12):
            a=i*.9;r=150+100*ease;x=360+math.cos(a)*r;y=575+math.sin(a)*r
            d.polygon([(x,y),(x+37,y-15),(x+49,y+29)],fill='#9b806a',outline=EDGE,width=2)
        for i in range(3):d.arc((153-i*28,362-i*37,566+i*28,805+i*37),second*25,second*25+227,fill='#ba8c9f',width=3)
    elif k=='ss_watcher':
        actor(layer,'supreme',220,691,.78,hand=(335,649))
        d.ellipse((390,321,641,619),fill='#82645d',outline=EDGE,width=3)
        for x in (460,562):d.line((x,461,x+32,461),fill='#e0cba8',width=6)
        d.polygon([(361,814),(407,617),(621,617),(679,814)],fill='#655371',outline=EDGE,width=3)
    elif k in ('ss_prison','ss_alone'):
        scale=1-.4*ease;cx,cy=363,579
        points=[(cx,cy-240*scale),(cx+194*scale,cy-91*scale),(cx+165*scale,cy+193*scale),(cx,cy+259*scale),(cx-173*scale,cy+180*scale),(cx-193*scale,cy-91*scale)]
        d.polygon(points,fill='#493545',outline='#d2a2c0',width=4)
        actor(layer,'supreme',cx-29*scale,cy-7*scale,.61*scale)
        if k=='ss_prison':
            actor(layer,'christine',cx+80*scale,cy+46*scale,.44*scale)
        for point in points:d.line((cx,cy,*point),fill='#825979',width=2)
    elif k=='end_subscribe':
        # A separate speech-anchored closing shot cannot appear during the payoff.
        ink=c.get('ink',EDGE)
        label(d,'MORE STORIES\nLIKE THIS',(107,352,506,142),46,ink)
        width=448+round(8*math.sin(min(second,.4)*math.pi*2))
        d.rounded_rectangle((360-width/2,583,360+width/2,692),radius=24,fill='#aa342f',outline='#ebc0aa',width=4)
        label(d,'SUBSCRIBE',(146,614,428,60),42,'#fff3df')
        d.line((239,769,481,769),fill=c.get('edge',EDGE),width=3)
