"""Reusable recognizable geometric MCU actors with anchored hands and props."""
from PIL import ImageDraw


EDGE='#decbb0'
SUITS={'cap':'#344e63','iron':'#9a3f37','bucky':'#333a3e','panther':'#29252f','spider':'#ad403a',
       'ant':'#69413d','war':'#4c5055','falcon':'#696b65','wanda':'#8d3d48','widow':'#353035',
       'vision':'#567774','hawkeye':'#534153','zemo':'#746554','strange':'#3e5867','supreme':'#503254',
       'christine':'#985447','ancient':'#bba67e','watcher':'#655371','tchalla':'#4f4145','sharon':'#8c8069',
       'tony':'#4b4545','steve':'#344e63','steve_civilian':'#6d6a60','rhodey':'#4b4857'}


def shield(d,x,y,r=48):
    for fraction,color in ((1,'#bd5145'),(.75,'#e0d6bb'),(.54,'#b85045'),(.35,'#39576d')):
        v=r*fraction;d.ellipse((x-v,y-v,x+v,y+v),fill=color,outline=EDGE,width=2)
    d.polygon([(x,y-r*.25),(x+r*.07,y-r*.07),(x+r*.26,y-r*.07),(x+r*.11,y+r*.04),
               (x+r*.16,y+r*.23),(x,y+r*.11),(x-r*.16,y+r*.23),(x-r*.11,y+r*.04),(x-r*.26,y-r*.07),(x-r*.07,y-r*.07)],fill='#f1e6ce')


def actor(layer,who,x,y,s=1,*,hand=None,facing=1,cape=True,missing_arm=False):
    """y is the shoulder; supplied hand is an absolute story-canvas contact point."""
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
        target=hand if side==facing and hand is not None else q(side*66,103)
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
    skin='#bc9376' if who not in ('panther','falcon','tchalla','rhodey') else '#8c6651'
    helmet=who in ('iron','war','panther','spider','ant','cap')
    face=suit if helmet else '#a74e64' if who=='vision' else skin
    d.polygon([q(-28,-64),q(-14,-83),q(15,-83),q(30,-63),q(25,-26),q(0,-11),q(-25,-27)],fill=face,outline=EDGE,width=3)
    if who in ('iron','war'):
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
        elif who not in ('ancient','vision','cap','watcher'):
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


def text_box_local(d,text,point,size):
    from shorts_editor.graphics import font
    d.text(point,text,font=font(size,True),fill='#e6dcc9')
