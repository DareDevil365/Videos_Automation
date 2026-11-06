"""Geometric sets, contract and explanatory inserts for the Triumph and Torment recap."""
import math

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from .assets import asset_record
from .core import Held


PACT_KINDS = ("pact_hook", "pact_signed", "pact_favor", "pact_gate",
              "pact_refused", "pact_device", "pact_release", "pact_aftermath")
GOLD = "#d5b777"
RED = "#f07970"
MINT = "#94efc5"


def load_pact_cast(workspace, request):
    names = request.get("pact_cast")
    if names is None:
        return {}, []
    if not isinstance(names, dict) or set(names) != {"doom", "doom_magic", "strange", "mephisto", "cynthia"}:
        raise Held("pact_cast", "Supply five registered character cutouts for the Doom story.")
    cast, assets = {}, []
    for who, asset_id in names.items():
        if not isinstance(asset_id, str):
            raise Held("pact_cast", "Use a registered cutout ID.")
        asset = asset_record(workspace, asset_id, allow_preview=request.get("test_only") is True)
        if asset["kind"] != "image" or (asset["test_only"] and request.get("test_only") is not True):
            raise Held("pact_cast", "Use an eligible character image for this export.")
        with Image.open(asset["path"]) as original:
            image = original.convert("RGBA")
        if image.getchannel("A").getextrema() != (0, 255):
            raise Held("pact_cast", "Character cutouts need transparent edges.")
        color = ImageEnhance.Color(image.convert("RGB")).enhance(.85).convert("RGBA")
        color.putalpha(image.getchannel("A"))
        cast[who] = color
        assets.append(asset)
    return cast, assets


def _actor(layer, cast, who, box, *, opacity=1):
    if not cast:
        return
    source = cast[who]
    size = (round(box[2]-box[0]),round(box[3]-box[1]))
    prepared = source.info.setdefault("pact_sizes", {})
    if size not in prepared:
        prepared[size] = ImageOps.contain(source, size, Image.Resampling.LANCZOS)
    image = prepared[size]
    if opacity != 1:
        image = image.copy()
        image.putalpha(image.getchannel("A").point(lambda alpha: round(alpha*opacity)))
    x = round(box[0]+(box[2]-box[0]-image.width)/2)
    y = round(box[3]-image.height)
    layer.alpha_composite(image, dest=(x,y))


def _contract(draw, x, y, scale, signed=False):
    def point(a, b):
        return x+a*scale,y+b*scale
    draw.polygon([point(-93,-125),point(71,-125),point(94,-105),point(95,101),
                  point(72,124),point(-95,124)], fill="#54413e",outline=GOLD,width=4)
    draw.line([point(71,-125),point(70,-100),point(94,-105)], fill=GOLD,width=3)
    for index,length in enumerate((105,122,93)):
        dy=-59+index*36
        draw.line([point(-58,dy),point(-58+length,dy)],fill="#c4a58d",width=3)
    sx,sy=point(40,72)
    radius=24*scale
    draw.ellipse((sx-radius,sy-radius,sx+radius,sy+radius), fill="#9c494b",outline=RED,width=3)
    if signed:
        draw.line([point(-52,74),point(-31,54),point(-24,75),point(-5,62)],fill="#ffd1a7",width=5)


def _rings(draw, x, y, radius, second, color):
    for index in range(3):
        r=radius+index*21
        a=second*(45+19*index)+index*52
        draw.arc((x-r,y-r,x+r,y+r),a,a+226,fill=color,width=4 if index==0 else 2)
    for index in range(8):
        angle=math.tau*index/8+second*.33
        cx,cy=x+radius*math.cos(angle),y+radius*math.sin(angle)
        draw.polygon([(cx,cy-5),(cx+5,cy),(cx,cy+5),(cx-5,cy)],fill=color)


def _realm(draw, second):
    draw.polygon([(40,880),(40,571),(111,433),(189,496),(253,296),(327,419),
                  (418,354),(471,478),(539,316),(676,461),(681,880)],
                 fill="#3b2634",outline="#8d525c",width=4)
    draw.polygon([(36,852),(247,776),(387,793),(682,744),(681,885),(36,885)],
                 fill="#4a2935",outline="#975552",width=3)
    for i in range(8):
        x=68+i*85;y=816+10*math.sin(second*2+i)
        draw.line([(x,y),(x+30,y+10),(x+61,y-7)],fill="#bd5e57",width=3)


def pact_art(layer, kind, second, progress, glow, cast=None):
    d=ImageDraw.Draw(layer)
    if kind=="pact_hook":
        _actor(layer,cast,"doom_magic",(27,286,400,709))
        _actor(layer,cast,"mephisto",(467,344,682,833))
        glow(layer,(370,475),150,(215,72,61),87)
        _rings(d,365,479,142,second,RED)
        _contract(d,382,493,.67)
    elif kind=="pact_signed":
        glow(layer,(380,473),130,(200,69,57),93)
        d.line([(78,727),(631,727),(658,798),(54,798),(78,727)],fill="#996861",width=4)
        _contract(d,372,541,.86,progress>.44)
        for i in range(4):
            cy=412+25*i+42*progress
            d.arc((264,cy,488,cy+114),201+i*17,332+i*17,fill="#a05c59",width=2)
        _actor(layer,cast,"cynthia",(58,418,296,716))
        _actor(layer,cast,"mephisto",(477,368,659,721))
    elif kind=="pact_favor":
        d.line([(60,743),(658,743)],fill="#647981",width=4)
        for x in (99,544):
            d.polygon([(x,742),(x,397),(x+31,372),(x+58,394),(x+58,742)],
                      fill="#283945",outline="#647981",width=3)
        _rings(d,363,472,82,second,GOLD)
        d.line([(326,469),(347,491),(394,439)],fill="#ffdb97",width=7)
        _actor(layer,cast,"doom",(65,329,298,757))
        _actor(layer,cast,"strange",(432,340,661,757))
        _rings(d,574,637,32,second,"#e6ad68")
    elif kind=="pact_gate":
        _realm(d,second)
        _actor(layer,cast,"mephisto",(291,271,479,640),opacity=.62)
        glow(layer,(360,501),205,(211,85,57),105)
        for i in range(4):
            r=106+i*27+14*progress
            d.ellipse((360-r,503-r*1.4,360+r,503+r*1.4),outline=RED if i%2 else GOLD,width=3)
        _contract(d,360,501,.53)
        step=51*min(1,progress*1.3)
        _actor(layer,cast,"doom",(61,485,282,868))
        _actor(layer,cast,"strange",(456-step,484,638-step,841))
        if progress>.49:
            for i in range(3):
                cy=657+i*37
                d.arc((414-step,cy,638-step,cy+60),4,176,fill="#e9b080",width=4)
    elif kind=="pact_refused":
        _realm(d,second)
        _actor(layer,cast,"doom",(55,490,274,868))
        _actor(layer,cast,"cynthia",(454+17*progress,373,668+17*progress,666))
        _actor(layer,cast,"strange",(502,679,621,871),opacity=.65)
        spread=72*max(0,progress-.25)
        _contract(d,359,450,.79,True)
        d.line([(165,661),(277-spread,661),(306-spread,638)],fill=RED,width=7)
        d.line([(413+spread,638),(448+spread,661),(561,661)],fill=RED,width=7)
        d.line([(325,676),(348,641),(342,683),(386,625)],fill="#ffd0a2",width=6)
    elif kind=="pact_device":
        # Wide action stays visible while a circular detail explains the escape device.
        _realm(d,second)
        _actor(layer,cast,"strange",(127,451,365,866))
        _actor(layer,cast,"doom_magic",(45,263,224,424),opacity=.77)
        x,y=507,443
        glow(layer,(x,y),111,(69,194,139),111)
        d.line([(348,623),(416,560),(451,523)],fill=MINT,width=4)
        d.ellipse((394,330,620,556),fill="#163032",outline="#aad9bd",width=5)
        _rings(d,x,y,54,second,MINT)
        d.polygon([(x,y-48),(x+36,y-12),(x+23,y+47),(x-34,y+34),(x-41,y-17)],
                  fill="#527e71",outline=MINT,width=4)
        d.ellipse((x-14,y-14,x+14,y+14),fill="#d4ffee",outline=MINT,width=3)
        for i in range(3):
            dx=152*i+30*progress
            d.arc((116+dx,700,258+dx,817),194,319,fill=RED,width=5)
    elif kind=="pact_release":
        _realm(d,second)
        x,y=370+31*progress,615-212*progress
        glow(layer,(x,y),107,(211,229,188),141)
        _actor(layer,cast,"cynthia",(x-82,y-124,x+82,y+43),opacity=1-.66*progress)
        _actor(layer,cast,"doom_magic",(56,664,279,855))
        _actor(layer,cast,"strange",(480,547,651,857))
        _rings(d,x,y,69,second,"#f2dca0")
        d.polygon([(x,y-34),(x+23,y),(x,y+33),(x-23,y)],fill="#f9e6b2",outline="#fff1c9",width=4)
        for i in range(9):
            px=191+i*39+12*math.sin(i+second)
            py=746-((i*61+second*100)%343)
            d.ellipse((px-2,py-2,px+2,py+2),fill=GOLD)
    else:
        glow(layer,(514,509),172,(76,182,132),82)
        d.polygon([(394,775),(394,506),(463,398),(542,349),(616,398),(667,508),(667,775)],
                  fill="#203a38",outline="#658a77",width=3)
        _rings(d,522,567,88,second,"#88b9a1")
        d.line([(95,761),(299,761),(355,713)],fill="#9d927d",width=3)
        _actor(layer,cast,"doom",(341-12*progress,303,663-12*progress,885))
        _actor(layer,cast,"strange",(54,614,211,882),opacity=.75)
