"""Iron Man's reactor drawn as a consistent object across different story shots."""
import math
from PIL import ImageDraw


REACTOR_KINDS = ("reactor_tease", "cave_battery", "reactor_build", "cave_escape",
                 "reactor_case", "reactor_theft", "reactor_return")


def _reactor(layer, glow, x, y, r, heat, time):
    d = ImageDraw.Draw(layer)
    if heat:
        glow(layer, (x,y), r, (91,209,251), round(90*heat))
    d.ellipse((x-r,y-r,x+r,y+r), fill="#23353d", outline="#b0bec0", width=4)
    d.ellipse((x-r*.79,y-r*.79,x+r*.79,y+r*.79), fill="#111d28",
              outline="#628791", width=3)
    for index in range(10):
        angle = math.tau*index/10
        dx,dy = math.cos(angle),math.sin(angle)
        d.line([(x+dx*r*.78,y+dy*r*.78),(x+dx*r*.93,y+dy*r*.93)],
               fill="#c69565",width=max(2,round(r*.075)))
    color = "#bff6ff" if heat else "#3a5360"
    d.ellipse((x-r*.57,y-r*.57,x+r*.57,y+r*.57), outline=color,width=max(3,round(r*.12)))
    d.ellipse((x-r*.29,y-r*.29,x+r*.29,y+r*.29),fill=color,outline="#cbdcdb")
    if heat:
        d.arc((x-r*.67,y-r*.67,x+r*.67,y+r*.67),time*120,time*120+68,fill="#f4ffff",width=3)


def _chest(d, x, y, armored):
    color = "#6b3c3a" if armored else "#334953"
    d.polygon([(x-235,y+242),(x-204,y-62),(x-106,y-124),(x-57,y-113),
               (x+57,y-113),(x+106,y-124),(x+204,y-62),(x+235,y+242)],
              fill=color,outline="#bbada0",width=4)
    d.line([(x-190,y-49),(x-105,y+46),(x-48,y+75)],fill="#a18d80",width=3)
    d.line([(x+190,y-49),(x+105,y+46),(x+48,y+75)],fill="#a18d80",width=3)
    d.ellipse((x-57,y-57,x+57,y+57),fill="#101923",outline="#a5b5b3",width=5)


def reactor_art(layer, kind, second, progress, glow):
    d = ImageDraw.Draw(layer)
    if kind in ("reactor_tease", "reactor_case"):
        bright = kind == "reactor_case"
        y = 554 if bright else 570
        d.polygon([(131,719),(568,719),(613,777),(109,777)],fill="#414754",outline="#a49374",width=4)
        d.polygon([(159,402),(219,345),(541,345),(583,402),(583,718),
                   (159,718)],fill="#132430",outline="#526a75",width=4)
        d.polygon([(159,402),(219,345),(541,345),(491,402)],
                  fill="#273945",outline="#708591",width=3)
        d.line([(491,402),(491,713),(583,718)],fill="#536f7c",width=3)
        _reactor(layer,glow,359,y,119 if bright else 93,.72 if bright else 0,second)
        d.line([(189+130*progress,427),(171+130*progress,625)],fill="#59737d",width=4)
        d.rectangle((226,680,488,716),fill="#655341" if bright else "#323a43",outline="#b69e7a",width=2)
        if bright:
            d.line((251,699,461,699),fill="#e5c194",width=3)
        return
    if kind == "cave_battery":
        d.polygon([(39,840),(39,434),(102,290),(213,266),(322,339),
                   (355,458),(355,840)],fill="#332a2a",outline="#8c705c",width=4)
        d.polygon([(430,447),(530,388),(631,448),(669,794),(395,794)],
                  fill="#485355",outline="#a4b0a6",width=4)
        d.rounded_rectangle((91,628,269,752),14,fill="#32434b",outline="#b5bfb1",width=4)
        d.rectangle((112,615,144,641),fill="#be6255")
        d.rectangle((215,615,242,641),fill="#7ca6ae")
        wire=[(128,625),(143,563),(236,529),(337,582),(488,604)]
        d.line(wire,fill="#b87d59",width=7,joint="curve")
        for index in range(len(wire)-1):
            (x,y),(xx,yy) = wire[index:index+2]
            p = (progress*2+index*.21)%1
            x,y = x+(xx-x)*p,y+(yy-y)*p
            d.ellipse((x-5,y-5,x+5,y+5),fill="#ffe4a2")
        _reactor(layer,glow,500,604,36,.5,second)
        return
    if kind == "reactor_build":
        d.polygon([(67,700),(634,700),(678,764),(38,764)],fill="#3a3c39",outline="#a89673",width=4)
        for i,x in enumerate((161,232,484,553)):
            y=469+(i%2)*139
            shift=40*(1-progress)
            x=x+(shift if i>1 else -shift)
            d.polygon([(x-43,y-22),(x+38,y-18),(x+49,y+21),(x-35,y+32)],
                      fill="#786851",outline="#bda283",width=3)
        _reactor(layer,glow,359,563,145,progress,second)
        return
    if kind == "cave_escape":
        d.polygon([(36,881),(36,435),(174,289),(544,286),(685,452),(685,881)],
                  fill="#211e23",outline="#695242",width=5)
        for side in (-1,1):
            x=359+side*189
            d.polygon([(x-42,831),(x-68,692),(x-31,739),(x,649),(x+42,831)],
                      fill="#ae663f",outline="#e5a36e",width=3)
        y=593-55*progress
        _chest(d,359,y,False)
        d.polygon([(299,y-150),(311,y-248),(407,y-248),(421,y-154),(388,y-123),(330,y-123)],
                  fill="#69716b",outline="#bdc7b3",width=5)
        d.line((325,y-193,391,y-193),fill="#1b2c2f",width=9)
        _reactor(layer,glow,359,y,48,1,second)
        return
    theft = kind == "reactor_theft"
    y = 542
    _chest(d, 312, y, armored=False)
    move = min(1, progress*1.38)
    x = 312+208*move if theft else 550-238*move
    y2 = y-102*move if theft else y+78*(1-move)
    d.line((310,y,x,y2),fill="#567682",width=4)
    _reactor(layer,glow,x,y2,51,1,second)
    if not theft and move == 1:
        d.line([(144,790),(248,790),(276,763),(311,811),(343,765),
                (375,790),(574,790)],fill="#94d4ce",width=4)
