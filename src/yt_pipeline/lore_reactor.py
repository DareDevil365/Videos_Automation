"""Iron Man's reactor drawn as a consistent object across different story shots."""
import math
from PIL import ImageDraw

from .lore_reactor_cast import PEPPER, STANE, TONY, arm, person


REACTOR_KINDS = ("reactor_tease", "cave_battery", "reactor_build", "cave_escape",
                 "reactor_case", "reactor_gift", "reactor_theft", "reactor_return")


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


def _gift(layer, glow, second, progress):
    d = ImageDraw.Draw(layer)
    d.polygon([(39,820),(39,340),(659,316),(681,807)], fill="#172e37", outline="#577780", width=4)
    d.polygon([(74,477),(134,367),(560,347),(621,440),(621,580),(74,581)],
              fill="#223b43", outline="#67807c", width=3)
    for x in range(129, 604, 67):
        d.line((x,390,x,576), fill="#35545a", width=2)
    placing = progress < .67
    if placing:
        shoulder, _ = person(d, PEPPER, 206, 472, 1.05)
        travel = min(1, progress / .42)
        x = 314 + 48 * travel
        y = 593 + 53 * travel
        arm(d, PEPPER, shoulder, (289,617), (x-43,y+30), 1.05)
    else:
        shoulder, _ = person(d, TONY, 496, 472, 1.05, facing=-1)
        x, y = 362, 646
        reach = min(1, (progress-.67) * 8)
        arm(d, TONY, shoulder, (433,637), (428-16*reach,685-15*reach), 1.05)
    d.polygon([(79,682),(620,682),(671,734),(53,734)], fill="#4e4941", outline="#a49374", width=4)
    d.rectangle((57,734,667,781), fill="#322f30", outline="#746555", width=3)
    d.polygon([(x-54,y-45),(x-32,y-65),(x+51,y-65),(x+61,y-45),(x+61,y+33),(x-54,y+33)],
              fill="#29404a", outline="#a8c0b9", width=3)
    _reactor(layer, glow, x+3, y-11, 28, .85, second)
    d.polygon([(397,687),(476,682),(481,708),(402,715)], fill="#c6b289", outline="#edd5aa", width=2)
    d.line((414,695,463,691), fill="#74604c", width=2)
    d.line((415,704,444,701), fill="#74604c", width=2)


def _take_reactor(layer, glow, second, progress):
    d = ImageDraw.Draw(layer)
    d.polygon([(43,832),(43,331),(661,303),(680,812)], fill="#242d39", outline="#6a7887", width=3)
    d.polygon([(86,704),(120,658),(371,658),(403,706),(399,803),(90,803)],
              fill="#4e3a3f", outline="#877070", width=3)
    d.line((94,742,394,742), fill="#79595b", width=4)
    recoil = max(0, min(1, (progress-.46)*5))
    _, chest = person(d, TONY, 211-28*recoil, 464+40*recoil, 1.15)
    shoulder, _ = person(d, STANE, 514, 421, 1.25, facing=-1)
    approach = min(1, progress/.37)
    grab = max(0, min(1, (progress-.46)*3.3))
    chest_x, chest_y = chest
    hand_x = chest_x+169*(1-approach)+180*grab
    hand_y = chest_y-34*(1-approach)-124*grab
    arm(d, STANE, shoulder, (388,614-49*grab), (hand_x+22,hand_y+13), 1.23)
    d.ellipse((chest_x-42,chest_y-42,chest_x+42,chest_y+42),
              fill="#101923",outline="#819599",width=4)
    if grab:
        chest_x, chest_y = hand_x, hand_y
    _reactor(layer, glow, chest_x, chest_y, 36, .92, second)


def reactor_art(layer, kind, second, progress, glow):
    d = ImageDraw.Draw(layer)
    if kind == "reactor_gift":
        _gift(layer, glow, second, progress)
        return
    if kind == "reactor_theft":
        _take_reactor(layer, glow, second, progress)
        return
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
        _, chest = person(d, TONY, 521, 452, 1.13, facing=-1)
        d.rounded_rectangle((91,628,269,752),14,fill="#32434b",outline="#b5bfb1",width=4)
        d.rectangle((112,615,144,641),fill="#be6255")
        d.rectangle((215,615,242,641),fill="#7ca6ae")
        wire=[(128,625),(143,563),(236,529),(337,582),chest]
        d.line(wire,fill="#b87d59",width=7,joint="curve")
        for index in range(len(wire)-1):
            (x,y),(xx,yy) = wire[index:index+2]
            p = (progress*2+index*.21)%1
            x,y = x+(xx-x)*p,y+(yy-y)*p
            d.ellipse((x-5,y-5,x+5,y+5),fill="#ffe4a2")
        _reactor(layer,glow,*chest,28,.5,second)
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
    shoulder, (cx, cy) = person(d, TONY, 303, 445, 1.3)
    move = min(1, progress*1.38)
    x = 538+(cx-538)*move
    y = cy+67*(1-move)
    d.ellipse((cx-42,cy-42,cx+42,cy+42),fill="#101923",outline="#819599",width=4)
    arm(d, TONY, shoulder, (453,727), (x+20,y+19), 1.24)
    _reactor(layer,glow,x,y,39,1,second)
    if move == 1:
        d.line([(144,790),(248,790),(276,763),(311,811),(343,765),
                (375,790),(574,790)],fill="#94d4ce",width=4)
