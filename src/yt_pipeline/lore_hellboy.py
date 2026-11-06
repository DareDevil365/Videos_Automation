"""Authored geometric Hellboy actors over registered photographic settings and props."""
import math

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from .assets import asset_record
from .core import Held


HELLBOY_KINDS = ('hellboy_question', 'hellboy_child', 'hellboy_case', 'hellboy_key',
                 'hellboy_destiny', 'hellboy_refusal', 'hellboy_choice', 'hellboy_hunter')
INK = '#11151c'
RED = '#c8443b'
LIGHT = '#ee7961'
COAT = '#a48d68'
CREAM = '#e0c7a3'


def load_hellboy_media(workspace, request):
    names = request.get('hellboy_media')
    if names is None:
        return {}, []
    if not isinstance(names, dict) or set(names) != {'lava', 'ruins', 'book'}:
        raise Held('hellboy_media', 'Supply registered lava and ruins photographs and a book cutout.')
    media, assets = {}, []
    for name, asset_id in names.items():
        if not isinstance(asset_id, str):
            raise Held('hellboy_media', 'Use a registered image ID.')
        asset = asset_record(workspace, asset_id, allow_preview=request.get('test_only') is True)
        if asset['kind'] != 'image':
            raise Held('hellboy_media', 'Hellboy photographic layers must be images.')
        with Image.open(asset['path']) as source:
            picture = ImageOps.exif_transpose(source).convert('RGBA')
        if name == 'book':
            if picture.getchannel('A').getextrema() != (0, 255):
                raise Held('hellboy_media', 'The book prop needs transparent edges.')
            picture = ImageOps.contain(picture, (270, 360), Image.Resampling.LANCZOS)
        else:
            picture = ImageOps.fit(picture, (760, 850), Image.Resampling.LANCZOS)
            picture = ImageEnhance.Color(picture).enhance(.50)
            picture = ImageEnhance.Brightness(picture).enhance(.51 if name == 'ruins' else .72)
        media[name] = picture
        assets.append(asset)
    return media, assets


def _plate(layer, media, name, p, *, offset=0):
    if not media:
        return
    picture = media[name]
    left = round(24+54*p) if offset == 0 else round(78-54*p)
    tile = picture.crop((left, 35, left+660, 775))
    # The photograph sits behind actors, inside the familiar skewed cream panel.
    mask = Image.new('L', tile.size)
    ImageDraw.Draw(mask).polygon([(0,22),(659,0),(659,712),(6,739)], fill=255)
    tile.putalpha(mask)
    layer.alpha_composite(tile, (30,196))


def _body(draw, x, y, scale=1, *, horns=0, hand=None, left=None, coat=True, child=False):
    """An angular red silhouette, horn stubs, heavy brow, goatee and one stone right hand.

    Coordinates are stage anchors rather than a fixed whole-actor bitmap, allowing
    the hand and elbow to stay connected as the gesture changes.
    """
    s = scale
    def q(a, b):
        return x+a*s, y+b*s
    def poly(points, fill, outline=INK, width=3):
        draw.polygon([q(a,b) for a,b in points],fill=fill,outline=outline,width=max(1,round(width*s)))
    # Tail behind coat, boots, trousers, broad asymmetrical coat panels.
    draw.line([q(40,154),q(91,163),q(111,139),q(107,111)], fill=RED, width=max(3,round(9*s)))
    poly([(107,111),(99,119),(112,121)], RED, width=1)
    poly([(-42,113),(-7,113),(-11,227),(-57,227)], '#252a30')
    poly([(3,113),(42,113),(56,227),(13,227)], '#252a30')
    poly([(-57,216),(-12,216),(-12,240),(-69,240)], '#171d25')
    poly([(13,216),(56,216),(70,239),(13,239)], '#171d25')
    poly([(-47,-16),(45,-16),(59,110),(0,136),(-57,110)], RED)
    poly([(-7,-9),(45,-16),(59,110),(0,136)], '#a63232', width=1)
    if coat:
        poly([(-52,-23),(-25,-21),(-9,18),(-20,170),(-75,189),(-64,63)], COAT)
        poly([(24,-21),(51,-20),(66,65),(80,186),(23,169),(10,17)], '#75634f')
        poly([(-48,-26),(-15,-12),(-8,21),(-35,12)], '#c4ae83')
        poly([(20,-15),(50,-27),(36,17),(9,23)], '#baa17a')
        draw.line([q(-53,106),q(-29,103)],fill=CREAM,width=max(2,round(3*s)))
    # Arms terminate at actual wrists, including the lifted hand in the horn action.
    rx,ry = hand if hand is not None else (x-95*s,y+90*s)
    lx,ly = left if left is not None else (x+88*s,y+88*s)
    shoulder=q(-43,2)
    elbow=((shoulder[0]+rx)/2-14*s,(shoulder[1]+ry)/2+18*s)
    draw.line([shoulder,elbow,(rx,ry)], fill=INK,width=max(4,round(35*s)))
    draw.line([shoulder,elbow,(rx,ry)], fill=COAT if coat else RED,width=max(3,round(29*s)))
    draw.line([q(43,4),q(71,42),(lx,ly)], fill=INK,width=max(4,round(25*s)))
    draw.line([q(43,4),q(71,42),(lx,ly)], fill=COAT if coat else RED,width=max(3,round(19*s)))
    draw.ellipse((lx-10*s,ly-10*s,lx+10*s,ly+10*s),fill=RED,outline=INK,width=2)
    _fist(draw,rx,ry,s*.86)
    # Neck and faceted skull. Broad cheek plane and black beard read at phone size.
    poly([(-18,-40),(19,-40),(20,-12),(-19,-12)], RED)
    poly([(-36,-111),(-16,-128),(24,-124),(41,-101),(36,-58),(16,-36),(-18,-38),(-36,-61)], RED)
    poly([(7,-122),(24,-124),(41,-101),(36,-58),(16,-36),(8,-59)], '#a83230', width=1)
    poly([(-34,-101),(-8,-94),(-4,-85),(-34,-88)], '#351c22', width=1)
    poly([(5,-94),(34,-101),(34,-88),(7,-85)], '#351c22', width=1)
    draw.line([q(-27,-86),q(-12,-84)],fill='#efc66d',width=max(2,round(4*s)))
    draw.line([q(12,-84),q(29,-87)],fill='#efc66d',width=max(2,round(4*s)))
    poly([(-2,-84),(-10,-65),(8,-65)], LIGHT, width=1)
    draw.line([q(-16,-54),q(16,-54)],fill=INK,width=max(2,round(3*s)))
    if not child:
        poly([(-12,-48),(13,-48),(8,-22),(-5,-16)], '#22202a', width=1)
    for side in (-1,1):
        hx=x+side*25*s
        if horns:
            h=horns*s
            draw.polygon([(hx-side*12*s,y-112*s),(hx+side*18*s,y-132*s-h*.30),
                          (hx+side*24*s,y-145*s-h*.70),(hx+side*12*s,y-143*s-h),
                          (hx+side*46*s,y-129*s-h*.70),(hx+side*44*s,y-122*s-h*.25),
                          (hx+side*12*s,y-112*s)],
                         fill='#bf8a5e',outline=INK,width=max(2,round(3*s)))
        draw.ellipse((hx-13*s,y-120*s,hx+13*s,y-104*s),fill='#aa4238',outline=INK,width=max(1,round(3*s)))
        draw.line((hx-8*s,y-114*s,hx+8*s,y-111*s),fill=LIGHT,width=max(1,round(2*s)))


def _fist(draw, x, y, s=1):
    pts=[(-42,-43),(-17,-57),(30,-50),(46,-25),(41,24),(21,43),(-26,39),(-46,13)]
    draw.polygon([(x+a*s,y+b*s) for a,b in pts],fill='#a6503a',outline=INK,width=max(2,round(4*s)))
    draw.polygon([(x-42*s,y-43*s),(x-17*s,y-57*s),(x+30*s,y-50*s),(x+13*s,y-28*s),(x-26*s,y-24*s)],fill='#d1835d')
    for a in (-18,2,22):
        draw.line((x+a*s,y-35*s,x+(a-3)*s,y+16*s),fill='#592d2b',width=max(2,round(3*s)))
    draw.line((x-30*s,y+16*s,x+31*s,y+20*s),fill='#592d2b',width=max(2,round(3*s)))
    draw.arc((x-24*s,y-16*s,x+18*s,y+31*s),15,310,fill='#df9c6e',width=max(2,round(3*s)))


def _broom(draw, x, y, s, hand):
    def q(a,b): return x+a*s,y+b*s
    draw.polygon([q(-28,77),q(-1,77),q(-6,131),q(-39,131)],fill='#28353f',outline=INK,width=2)
    draw.polygon([q(5,77),q(29,77),q(43,131),q(14,131)],fill='#28353f',outline=INK,width=2)
    draw.line([q(-41,134),q(-6,134)],fill=INK,width=round(9*s))
    draw.line([q(13,134),q(47,134)],fill=INK,width=round(9*s))
    draw.polygon([q(-28,-34),q(26,-34),q(39,86),q(-43,86)],fill='#4c6171',outline=CREAM,width=2)
    draw.polygon([q(-30,-61),q(-18,-87),q(15,-85),q(31,-61),q(22,-31),q(-19,-31)],fill='#c0a685',outline=INK,width=3)
    draw.polygon([q(-31,-62),q(-31,-84),q(11,-97),q(30,-78),q(22,-72),q(0,-82)],fill='#c8c9b7')
    for cx in (-13,11):
        a,b=q(cx,-60);draw.ellipse((a-9*s,b-6*s,a+9*s,b+6*s),outline=INK,width=max(2,round(2*s)))
    draw.line([q(-3,-60),q(3,-60)],fill=INK,width=2)
    draw.line([q(-23,-18),q(-37,9),hand],fill='#7c96a0',width=round(13*s))
    hx,hy=hand;draw.ellipse((hx-8*s,hy-8*s,hx+8*s,hy+8*s),fill='#c0a685')


def _embers(draw, second, color='#e4ac7d'):
    for i in range(12):
        x=56+(i*137)%603
        y=920-((second*28+i*71)%665)
        draw.line((x,y,x+2,y-5),fill=color,width=2)


def hellboy_art(layer, kind, second, p, glow, media=None):
    media=media or {}
    d=ImageDraw.Draw(layer)
    if kind in ('hellboy_question','hellboy_destiny','hellboy_refusal'):
        _plate(layer,media,'lava',p,offset=kind=='hellboy_refusal')
    elif kind in ('hellboy_child','hellboy_hunter'):
        _plate(layer,media,'ruins',p,offset=kind=='hellboy_hunter')
    d=ImageDraw.Draw(layer)
    if kind=='hellboy_question':
        glow(layer,(345,520),190,(221,82,42),115)
        _body(ImageDraw.Draw(layer),355,591+3*math.sin(second*1.7),1.52,coat=True)
        _embers(ImageDraw.Draw(layer),second)
    elif kind=='hellboy_child':
        glow(layer,(222,667),93,(234,177,109),80)
        reach=min(1,max(0,(p-.12)*2.7))
        _body(ImageDraw.Draw(layer),215,690,.49,coat=False,child=True,left=(268+38*reach,670))
        _broom(ImageDraw.Draw(layer),475,627,1.66,(316,670))
        _embers(ImageDraw.Draw(layer),second,'#b4c9be')
    elif kind=='hellboy_case':
        _body(d,497,590,.97,hand=(369,692),left=(533,698))
        if media:
            book=media['book'];layer.alpha_composite(book,(115,435))
        d=ImageDraw.Draw(layer)
        # A gentle search beam crosses the photographed binding; no invented readable evidence.
        xx=211+80*p
        d.line((xx,454,xx-30,755),fill='#dacbab',width=3)
        _embers(d,second,'#b4c9be')
    elif kind=='hellboy_key':
        glow(layer,(270,509),142,(200,100,65),90)
        _fist(ImageDraw.Draw(layer),254,510,3.1)
        d=ImageDraw.Draw(layer)
        # Abstract visual explanation: the hand is a key, not a literal metal key prop.
        d.line((399,513,468,513),fill=CREAM,width=5)
        d.polygon([(478,513),(459,501),(459,525)],fill=CREAM)
        for i in range(6):
            a=i*math.tau/6+second*.08
            cx,cy=551+math.cos(a)*68,513+math.sin(a)*96
            d.line((cx,cy,cx+24*math.sin(a),cy+33*math.cos(a)),fill='#937c7b',width=9)
            d.ellipse((cx-4,cy-4,cx+4,cy+4),fill='#d09a7a')
        d.ellipse((520,479,582,547),fill='#171c29',outline='#ab8170',width=4)
        if media:
            plate=ImageOps.fit(media['lava'],(600,195),Image.Resampling.LANCZOS)
            layer.alpha_composite(plate,(60,715))
        _embers(ImageDraw.Draw(layer),second)
    elif kind=='hellboy_destiny':
        # Hecate as a distant symbolic silhouette; the face is intentionally unreproduced.
        d.polygon([(563,277),(487,393),(501,716),(659,716),(649,393)],fill='#21212a',outline='#9b7c8b',width=3)
        d.ellipse((539,318,599,386),fill='#716376',outline='#b3969a',width=2)
        for i in range(3):
            d.arc((479+i*16,265,660-i*9,438),192+second*9,328+second*9,fill='#b49485',width=2)
        _body(d,306,636,1.14,horns=95*min(1,max(0,(p-.15)*2.6)),coat=False)
        _embers(ImageDraw.Draw(layer),second)
    elif kind=='hellboy_refusal':
        # Both arms reach the horns before the fragments separate.
        grip=min(1,max(0,p/.14));snap=min(1,max(0,(p-.22)/.11))
        relax=min(1,max(0,(p-.43)/.38))
        grip*=1-relax
        s=1.32;x=361;y=649
        hand=(x-111*s+78*s*grip,y+82*s-237*s*grip)
        left=(x+91*s-61*s*grip,y+85*s-240*s*grip)
        _body(d,x,y,s,horns=95 if snap==0 else 0,hand=hand,left=left,coat=False)
        if snap:
            fall=min(1,max(0,(p-.33)/.50))
            for side in (-1,1):
                hx=x+side*(34+94*snap+120*fall)*s
                hy=y-(175+45*snap-95*snap*snap)*s+600*fall*fall
                d.polygon([(hx-12*s,hy+30*s),(hx+side*20*s,hy-57*s),(hx+17*s,hy+20*s)],fill='#bf8a5e',outline=INK,width=3)
            for i in range(7):
                a=i*.9;dx=math.cos(a);dy=math.sin(a)
                cx=x+dx*(95+70*snap);cy=y-181*s+dy*(42+35*snap)
                d.line((cx,cy,cx+dx*15,cy+dy*15),fill=CREAM,width=3)
        _embers(d,second)
    elif kind=='hellboy_choice':
        if media:
            small=ImageOps.fit(media['lava'],(270,500),Image.Resampling.LANCZOS)
            small.putalpha(round(210*(1-p)))
            layer.alpha_composite(small,(408,353))
        glow(layer,(222,668),95,(224,154,91),65)
        _body(ImageDraw.Draw(layer),269,627,1.2,hand=(132+24*p,729),coat=False,horns=95)
        d=ImageDraw.Draw(layer)
        # Keep the full horns before the refusal; highlight the apocalyptic hand.
        d.arc((67,651,218,807),second*30,second*30+243,fill=CREAM,width=3)
        _embers(d,second,'#b4c9be')
    elif kind=='hellboy_hunter':
        _body(d,355+17*p,573,1.15,hand=(239+17*p,654+6*math.sin(second*2)),coat=True)
        _embers(d,second,'#b4c9be')
