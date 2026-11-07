"""Reusable geometric comic/film actors with anchored hands and props."""
from PIL import ImageDraw


EDGE='#decbb0'
SUITS={'cap':'#344e63','iron':'#9a3f37','bucky':'#333a3e','panther':'#29252f','spider':'#ad403a',
       'ant':'#69413d','war':'#4c5055','falcon':'#696b65','wanda':'#8d3d48','widow':'#353035',
       'vision':'#567774','hawkeye':'#534153','zemo':'#746554','strange':'#3e5867','supreme':'#503254',
       'christine':'#985447','ancient':'#bba67e','watcher':'#655371','tchalla':'#4f4145','sharon':'#8c8069',
       'tony':'#4b4545','steve':'#344e63','steve_civilian':'#6d6a60','rhodey':'#4b4857',
       'deadpool':'#a63f3b','hulk':'#638351','banner':'#726a60','doctor':'#c4b99f',
       'manthing':'#5a6950','writer':'#725f53','artist':'#65576c',
       'wolverine':'#b79c40','cassandra':'#b4a282','paradox':'#78634f','peter':'#a34239',
       'blade':'#302d31','gambit':'#745443','elektra':'#9f4446','laura':'#4c4240',
       'reed':'#416681','sue':'#416681','johnny':'#416681','torch':'#c76a3b','thing':'#b1784b',
       'surfer':'#b9b9ac','galactus':'#734b67','doom':'#405c41','cyclops':'#374e6b',
       'storm':'#575164','nightcrawler':'#353b66','colossus':'#9a9d94','polaris':'#4e7552',
       'xavier':'#6f6558','sunfire':'#aa513c','banshee':'#528160','thunderbird':'#865341',
       'jean':'#62794e','iceman':'#b4c3be','havok':'#353941','happy':'#62564a','wade_civilian':'#6c655e'}


def shield(d,x,y,r=48):
    for fraction,color in ((1,'#bd5145'),(.75,'#e0d6bb'),(.54,'#b85045'),(.35,'#39576d')):
        v=r*fraction;d.ellipse((x-v,y-v,x+v,y+v),fill=color,outline=EDGE,width=2)
    d.polygon([(x,y-r*.25),(x+r*.07,y-r*.07),(x+r*.26,y-r*.07),(x+r*.11,y+r*.04),
               (x+r*.16,y+r*.23),(x,y+r*.11),(x-r*.16,y+r*.23),(x-r*.11,y+r*.04),(x-r*.26,y-r*.07),(x-r*.07,y-r*.07)],fill='#f1e6ce')


def actor(layer,who,x,y,s=1,*,hand=None,off_hand=None,facing=1,cape=True,missing_arm=False):
    """y is the shoulder; hand/off_hand are independent absolute canvas contacts."""
    d=ImageDraw.Draw(layer);suit=SUITS[who];q=lambda a,b:(x+a*s*facing,y+b*s)
    def box(a,b,c,e):
        first,second=q(a,b),q(c,e)
        return (min(first[0],second[0]),min(first[1],second[1]),max(first[0],second[0]),max(first[1],second[1]))
    if who in ('strange','supreme','vision') and cape:
        d.polygon([q(-40,-22),q(-94,228),q(95,228),q(40,-22)],fill='#8d3741' if who=='strange' else '#603c6e' if who=='supreme' else '#a79a6c',outline=EDGE,width=3)
    if who=='falcon':
        for side in (-1,1):
            d.polygon([q(side*29,9),q(side*181,-73),q(side*161,119),q(side*39,83)],fill='#9b9b8e',outline=EDGE,width=3)
            for k in range(4):d.line([q(side*(60+k*28),-26-k*9),q(side*(52+k*24),86-k*4)],fill='#525c5b',width=3)
    for side in (-1,1):
        leg=suit if who not in ('strange','supreme','christine','ancient') else '#39343c'
        d.line([q(side*21,94),q(side*35,166),q(side*43,228)],fill=EDGE,width=max(4,round(28*s)))
        d.line([q(side*21,94),q(side*35,166),q(side*43,228)],fill=leg,width=max(3,round(23*s)))
        if who=='bucky' and side==-1 and missing_arm:continue
        if who=='bucky' and side==-1:arm='#b6b5a7'
        else:arm=suit
        target=hand if side==facing and hand is not None else off_hand if side!=facing and off_hand is not None else q(side*66,103)
        shoulder=q(side*31,12);elbow=(shoulder[0]*.5+target[0]*.5,shoulder[1]*.6+target[1]*.4+13*s)
        d.line([shoulder,elbow,target],fill=EDGE,width=max(4,round(22*s)),joint='curve')
        d.line([shoulder,elbow,target],fill=arm,width=max(3,round(16*s)),joint='curve')
        tx,ty=target;r=9*s;d.rounded_rectangle((tx-r,ty-r,tx+r,ty+r),radius=max(2,round(3*s)),fill=arm,outline=EDGE,width=2)
        if who=='bucky' and side==-1:
            for n in range(3):d.line((shoulder[0]-8*s,shoulder[1]+13*n*s,shoulder[0]+8*s,shoulder[1]+13*n*s),fill='#6d7373',width=2)
    d.polygon([q(-34,-1),q(34,-1),q(42,94),q(0,118),q(-42,94)],fill=suit,outline=EDGE,width=3)
    if who in ('strange','supreme','christine','ancient'):
        d.polygon([q(-36,52),q(37,52),q(61,205),q(-60,205)],fill=suit,outline=EDGE,width=3)
        d.line([q(-36,71),q(36,71)],fill='#aa8664',width=max(2,round(10*s)))
    if who=='deadpool':
        for side in (-1,1):
            d.polygon([q(side*27,4),q(side*11,4),q(side*18,91),q(side*39,90)],fill='#342c30')
            d.line([q(side*18,-15),q(side*54,-99)],fill=EDGE,width=max(3,round(9*s)))
            d.line([q(side*18,-15),q(side*54,-99)],fill='#484144',width=max(2,round(5*s)))
        d.rectangle(box(-41,81,41,93),fill='#725039',outline=EDGE,width=2)
        d.ellipse(box(-12,78,12,102),fill='#a43b37',outline=EDGE,width=2)
        d.line([q(-7,84),q(6,96)],fill='#29252a',width=2);d.line([q(7,84),q(-6,96)],fill='#29252a',width=2)
    skin=({'hulk':'#64834f','thing':'#b1784b','surfer':'#b9b9ac','nightcrawler':'#5d6794','colossus':'#a8ada4','storm':'#8c6651','iceman':'#c1d1c9'}.get(who) or
          ('#bc9376' if who not in ('panther','falcon','tchalla','rhodey') else '#8c6651'))
    helmet=who in ('iron','war','panther','spider','ant','cap','deadpool','manthing','wolverine','galactus','cyclops','doom')
    face=suit if helmet else '#a74e64' if who=='vision' else skin
    d.polygon([q(-28,-64),q(-14,-83),q(15,-83),q(30,-63),q(25,-26),q(0,-11),q(-25,-27)],fill=face,outline=EDGE,width=3)
    if who=='wolverine':
        for side in (-1,1):
            d.polygon([q(side*7,-69),q(side*39,-99),q(side*28,-47),q(side*15,-39)],fill='#344359',outline=EDGE,width=2)
            for n in range(3):
                contact=hand if side==facing and hand is not None else off_hand if side!=facing and off_hand is not None else q(side*66,103)
                start=(contact[0],contact[1]+n*4*s)
                end=(start[0]+side*facing*(33+n*4)*s,start[1]+(-9+n*5)*s)
                d.line([start,end],fill='#e4dcc5',width=max(2,round(3*s)))
        d.rectangle(box(-26,31,26,53),fill='#344359')
    elif who=='cyclops':
        d.rectangle(box(-28,-59,29,-44),fill='#d1ae53',outline=EDGE,width=2)
        d.rectangle(box(-22,-55,23,-49),fill='#bf4a40')
        d.line([q(-27,4),q(27,80)],fill='#bda655',width=max(3,round(12*s)))
    elif who=='galactus':
        for side in (-1,1):d.polygon([q(side*14,-68),q(side*54,-99),q(side*63,-90),q(side*45,-30),q(side*28,-27)],fill='#745067',outline=EDGE,width=3)
        d.rectangle(box(-20,-62,20,-28),fill='#a78473',outline=EDGE,width=2)
        d.line([q(-14,-49),q(-4,-49)],fill='#dfb58d',width=3);d.line([q(4,-49),q(14,-49)],fill='#dfb58d',width=3)
    elif who=='doom':
        d.polygon([q(-39,-18),q(-38,-67),q(0,-104),q(38,-67),q(39,-18),q(23,-28),q(20,-61),q(0,-76),q(-20,-61),q(-23,-28)],fill='#344c37',outline=EDGE,width=3)
        d.polygon([q(-18,-62),q(18,-62),q(17,-33),q(0,-23),q(-17,-33)],fill='#a7aaa0',outline=EDGE,width=2)
        d.line([q(-13,-50),q(-4,-49)],fill='#29322d',width=3);d.line([q(4,-49),q(13,-50)],fill='#29322d',width=3)
    elif who=='deadpool':
        for side in (-1,1):
            d.polygon([q(side*23,-71),q(side*5,-65),q(side*3,-34),q(side*21,-26),q(side*27,-44)],fill='#29272d',outline=EDGE,width=1)
            d.polygon([q(side*21,-55),q(side*6,-51),q(side*10,-44),q(side*22,-46)],fill='#f4e9d5')
    elif who=='manthing':
        for side in (-1,1):
            d.ellipse(box(side*16-7,-64,side*16+7,-50),fill='#cc784a',outline=EDGE,width=1)
        for dx in (-11,0,11):d.line([q(dx,-47),q(dx-4,-17),q(dx+3,-3)],fill='#869768',width=max(3,round(7*s)))
        for dx in (-24,10,27):d.line([q(dx,13),q(dx-8,52),q(dx+3,91)],fill='#829267',width=max(2,round(4*s)))
    elif who in ('iron','war'):
        d.polygon([q(-21,-71),q(21,-71),q(20,-37),q(0,-23),q(-21,-37)],fill='#c4a45d' if who=='iron' else '#9c9e99',outline=EDGE,width=2)
        d.line([q(-17,-56),q(-5,-54)],fill='#cce4df',width=3);d.line([q(5,-54),q(18,-56)],fill='#cce4df',width=3)
        d.ellipse(box(-11,30,11,51),fill='#bfdfd9',outline=EDGE,width=2)
        if who=='war':d.rectangle(box(28,-21,63,-4),fill='#414246',outline=EDGE,width=2)
    elif who=='spider':
        for side in (-1,1):d.polygon([q(side*23,-61),q(side*4,-47),q(side*9,-34),q(side*25,-44)],fill='#f1e9d6',outline='#4b292e',width=2)
        d.line([q(0,-78),q(0,-18)],fill='#573334',width=2)
        for yy in (-64,-35):d.line([q(-22,yy),q(0,yy+9),q(22,yy)],fill='#573334',width=2)
        d.line([q(0,28),q(0,66)],fill='#302a30',width=max(2,round(6*s)))
    elif who=='ant':
        d.polygon([q(-22,-70),q(22,-70),q(23,-34),q(-22,-34)],fill='#a3a39b',outline=EDGE,width=2)
        d.rectangle(box(-4,-78,4,-30),fill='#a84a41')
        for side in (-1,1):d.line([q(side*18,-78),q(side*28,-98)],fill=EDGE,width=3)
        d.line([q(-18,-53),q(-5,-51)],fill='#b94f42',width=4);d.line([q(5,-51),q(18,-53)],fill='#b94f42',width=4)
    elif who=='panther':
        for side in (-1,1):d.polygon([q(side*25,-66),q(side*25,-89),q(side*7,-78)],fill=suit,outline=EDGE,width=2)
        d.line([q(-20,-53),q(-7,-49)],fill='#e0d5c6',width=3);d.line([q(7,-49),q(20,-53)],fill='#e0d5c6',width=3)
        for dx in (-21,-11,0,11,21):d.polygon([q(dx-4,8),q(dx+4,8),q(dx,22)],fill='#c4c1b4')
    else:
        if who in ('bucky','christine','wanda','widow','sharon'):
            hair='#bc9963' if who=='sharon' else '#7a4334' if who in ('wanda','widow','christine') else '#46322e'
            d.polygon([q(-31,-37),q(-33,-66),q(-17,-89),q(18,-88),q(34,-65),q(34,-9),q(21,-24),q(18,-65),q(-15,-69),q(-23,-13),q(-36,-3)],fill=hair,outline=EDGE,width=2)
        elif who not in ('ancient','vision','cap','watcher','cassandra','surfer','xavier','thing','iceman'):
            d.polygon([q(-29,-51),q(-28,-74),q(-12,-89),q(18,-87),q(31,-68),q(11,-74),q(-12,-64)],fill='#a28a5f' if who in ('steve','steve_civilian') else '#3d2b2c')
        d.line([q(-18,-51),q(-6,-49)],fill='#3d2b2b',width=3);d.line([q(6,-49),q(18,-51)],fill='#3d2b2b',width=3)
        if who in ('strange','supreme','tony'):
            d.polygon([q(-14,-31),q(0,-36),q(14,-31),q(8,-22),q(0,-27),q(-8,-22)],fill='#44302c')
            d.polygon([q(-8,-20),q(0,-12),q(8,-20)],fill='#44302c')
            if who!='tony':d.ellipse(box(-10,20,10,41),fill='#c2a15c',outline=EDGE,width=2)
        if who in ('cap','steve'):
            if who=='cap':text_box_local(d,'A',q(-9,-73),max(12,round(19*s)))
            for dx in (-16,0,16):d.line([q(dx,57),q(dx,86)],fill='#bb4f45',width=max(3,round(8*s)))
            d.polygon([q(0,8),q(6,24),q(22,24),q(10,34),q(14,49),q(0,40),q(-14,49),q(-10,34),q(-22,24),q(-6,24)],fill='#ded8c6')
        if who=='falcon':d.line([q(-22,-52),q(23,-52)],fill='#b74840',width=6)
        if who=='vision':d.polygon([q(0,-76),q(-7,-66),q(0,-56),q(7,-66)],fill='#e6c777')
    if who in ('reed','sue','johnny'):
        d.ellipse(box(-13,14,13,40),fill='#e2d8bd',outline=EDGE,width=2)
        text_box_local(d,'4',q(-6,13),max(12,round(19*s)),color='#33516e')
        if who=='reed':
            for side in (-1,1):d.line([q(side*23,-65),q(side*25,-45)],fill='#d3ccba',width=max(2,round(7*s)))
    if who in ('sue','storm','polaris','jean'):
        hair={'sue':'#c0a46f','storm':'#ddd5bf','polaris':'#649364','jean':'#a7603f'}[who]
        d.polygon([q(-33,-22),q(-35,-64),q(-14,-90),q(19,-88),q(35,-60),q(38,-8),q(23,-23),q(18,-66),q(-18,-67),q(-22,-14)],fill=hair,outline=EDGE,width=2)
    if who=='thing':
        for yy in (5,28,51,74):
            for xx in (-27,-5,17):d.rectangle(box(xx,yy,xx+18,yy+18),outline='#735335',width=2)
        d.rectangle(box(-29,83,29,106),fill='#3e596d',outline=EDGE,width=2)
    if who=='blade':d.line([q(-24,-53),q(24,-53)],fill='#262429',width=max(3,round(9*s)))
    if who=='nightcrawler':
        d.polygon([q(-34,1),q(-18,1),q(0,55),q(18,1),q(34,1),q(18,100),q(-18,100)],fill='#a34e45',outline=EDGE,width=2)
        d.arc(box(23,97,104,205),200,530,fill='#586495',width=max(3,round(9*s)))
        d.polygon([q(-31,-62),q(-46,-76),q(-29,-34)],fill='#5d6794',outline=EDGE,width=2)
    if who=='havok':
        for radius in (10,18,26):d.ellipse(box(-radius,40-radius,radius,40+radius),outline='#d7d6bd',width=2)
    if who=='torch':
        for n in range(5):
            xx=-30+n*15;d.polygon([q(xx,-45),q(xx-13,-90-(n%2)*23),q(xx+15,-58)],fill='#e2aa5a',outline='#be6d3b')


def text_box_local(d,text,point,size,color='#e6dcc9'):
    from shorts_editor.graphics import font
    d.text(point,text,font=font(size,True),fill=color)
