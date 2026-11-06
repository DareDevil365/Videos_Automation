"""Geometric scene recipes for the first Beta Ray Bill arc."""
import math

from PIL import ImageDraw

from .lore_actions import draw_hammer


THUNDER_KINDS = ("thor_hammer_hook", "bill_fleet", "bill_lifts", "thor_duel",
                 "thor_ledge", "thor_rescue", "stormbreaker_forged", "thor_two_hammers")
SILVER = "#a1b4bc"
GOLD = "#d9af76"


def warrior(d, who, x, y, s, facing):
    """Shared body, distinct helmet, face, shoulder width and palette."""
    bill = who == "bill"
    skin = "#bc7d51" if bill else "#d4a487"
    armor = "#383c45" if bill else "#2e4b5d"
    rim = GOLD if bill else SILVER
    cape = "#7d473c" if bill else "#89404b"

    def poly(points, fill, edge=rim, width=2):
        d.polygon([(x+facing*a*s,y+b*s) for a,b in points],
                  fill=fill, outline=edge, width=max(1,round(width*s)))

    wide = 69 if bill else 60
    poly([(-42,25),(-79,48),(-107,190),(-23,171),(46,187),(57,72),(38,32)], cape)
    poly([(-wide,55),(-32,32),(36,31),(wide,54),(53,131),(36,167),
          (-42,167),(-54,130)], armor)
    poly([(-56,54),(-33,40),(-3,67),(-10,87),(-49,78)], "#6a6660" if bill else "#46687a")
    poly([(22,47),(38,37),(wide,54),(53,77),(24,82)], "#6a6660" if bill else "#46687a")
    for dx in (-27,26):
        for dy in (80,111):
            cx,cy=x+dx*s,y+dy*s
            d.ellipse((cx-9*s,cy-9*s,cx+9*s,cy+9*s),fill=rim,outline=armor,width=max(1,round(2*s)))
    poly([(-42,154),(44,153),(48,170),(-46,170)], "#63503d")
    if bill:
        poly([(-31,15),(-33,-29),(-16,-48),(6,-51),(33,-35),(38,-13),
              (60,11),(55,30),(18,40),(-5,30)], skin)
        poly([(8,-18),(36,-18),(53,5),(34,8),(14,4)], "#d99860")
        poly([(15,12),(58,13),(54,22),(19,25),(4,19)], "#271f28")
        poly([(19,12),(52,14),(49,19),(17,20)], "#e4ca97", None)
        poly([(8,-20),(26,-23),(30,-17),(16,-13)], "#222b33", None)
        poly([(-33,-11),(-36,-30),(-20,-49),(12,-54),(31,-42),(18,-29),
              (0,-24),(-19,-1)], "#69696b")
        poly([(-32,-18),(-53,-32),(-64,-60),(-35,-47),(-25,-36)], "#7f8784")
    else:
        poly([(-28,18),(-39,-14),(-31,-34),(-8,-45),(22,-41),(34,-18),
              (44,1),(33,8),(28,25),(2,38),(-19,31)], skin)
        poly([(-42,39),(-45,4),(-38,-27),(-18,-32),(-21,8),(-12,44)], "#bb934f")
        poly([(-38,-16),(-35,-37),(-18,-53),(13,-54),(34,-39),(36,-24),
              (13,-18),(-7,-10),(-19,1)], "#778c98")
        poly([(-27,-29),(-49,-36),(-60,-63),(-38,-53),(-19,-40)], SILVER)
        poly([(17,-11),(29,-14),(30,-8),(17,-6)], "#282931", None)
    return ((x+facing*46*s,y+56*s), armor, rim, skin)


def reach(d, actor, elbow, hand, s=1):
    shoulder, armor, rim, skin = actor
    d.line([shoulder, elbow, hand], fill=rim,width=round(24*s),joint="curve")
    d.line([shoulder, elbow, hand], fill=armor,width=round(18*s),joint="curve")
    x,y=hand
    d.ellipse((x-9*s,y-8*s,x+9*s,y+8*s),fill=skin,outline=rim,width=2)


def fire_world(d, second):
    d.polygon([(39,846),(39,576),(98,437),(167,471),(266,323),(307,535),
               (478,426),(543,298),(667,529),(684,846)], fill="#42283b", outline="#94555d", width=4)
    d.polygon([(48,848),(49,706),(196,677),(299,702),(398,660),
               (501,675),(674,734),(674,848)], fill="#673637", outline="#a65f51", width=3)
    for index in range(4):
        y=750+index*26
        line=[(57+n*85,y+10*math.sin(second*2+n+index)) for n in range(8)]
        d.line(line,fill="#dc7850" if index%2 else "#f3a66a",width=5)


def bolt(d, x, y, second, length):
    points = [(x,y)] + [(x+math.sin(second*23+j*2.4)*j*10,y-j*length/5) for j in range(1,6)]
    d.line(points,fill="#5c99df",width=11,joint="curve")
    d.line(points,fill="#daedfd",width=4,joint="curve")


def thunder_art(layer, kind, second, p, glow):
    d=ImageDraw.Draw(layer)
    if kind=="thor_hammer_hook":
        # Read the mystery immediately as a tight portrait and an oversized prop.
        # The later lift uses a medium view so the viewer can see the whole action.
        grip=(211+14*p,655-27*p)
        glow(layer,grip,141,(94,161,233),135)
        d.arc((77,280,635,814),194,348,fill="#426784",width=4)
        bill=warrior(d,"bill",525,567,2.1,-1)
        reach(d,bill,(342,760),grip,1.62)
        draw_hammer(d,*grip,3.75)
        bolt(d,grip[0],grip[1]-153,second,133)
        return
    if kind=="bill_lifts":
        grip=(289,640-196*min(1,p*1.48))
        glow(layer,grip,115,(94,161,233),115)
        bill=warrior(d,"bill",451,507,1.42,-1)
        reach(d,bill,(338,609),grip,1.25)
        draw_hammer(d,*grip,2.35)
        if p>.34:
            bolt(d,grip[0],grip[1]-94,second,111)
        return
    if kind=="bill_fleet":
        for i in range(4):
            x=99+i*127+15*p;y=471-i*34
            d.polygon([(x-39,y+18),(x-27,y-10),(x+36,y-25),(x+51,y+1),(x+17,y+19)],
                      fill="#364e60",outline=SILVER,width=3)
            d.line((x-58,y+16,x-39,y+14),fill="#91cfe2",width=3)
        warrior(d,"bill",396,563,1.5,1)
        d.polygon([(54,796),(633,778),(671,818),(55,839)],fill="#263b49",outline="#627c86",width=3)
        return
    if kind in ("thor_duel","thor_ledge","thor_rescue"):
        fire_world(d,second)
        d.polygon([(52,850),(65,710),(202,684),(296,717),(349,850)],fill="#382d3a",outline="#986653",width=4)
        d.polygon([(357,855),(418,727),(527,698),(666,709),(676,855)],fill="#382d3a",outline="#986653",width=4)
        if kind=="thor_duel":
            approach=min(1,p*1.3)
            thor=warrior(d,"thor",154+53*approach,493,1.12,1)
            bill=warrior(d,"bill",565-57*approach,475,1.19,-1)
            reach(d,thor,(253,592),(265+84*approach,544),1.05)
            reach(d,bill,(466,563),(459-104*approach,544),1.1)
            if p>.63:
                d.line([(338,521),(359,546),(372,512)],fill="#ffe0a4",width=5)
            return
        rescued=kind=="thor_rescue"
        lift=min(1,p*1.42) if rescued else 0
        bill=warrior(d,"bill",530,474,1.29,-1)
        thor=warrior(d,"thor",224+51*lift,669-123*lift+16*math.sin(second*3)*(1-lift),.92,1)
        hand=(351+32*lift,691-91*lift)
        reach(d,thor,(287+40*lift,704-75*lift),hand,.92)
        if rescued:
            reach(d,bill,(446,628),(hand[0]+6,hand[1]-4),1.17)
        else:
            reach(d,bill,(454,626),(396-23*p,652+19*p),1.17)
        return
    if kind=="stormbreaker_forged":
        glow(layer,(362,554),162,(255,147,65),120)
        d.polygon([(159,700),(561,700),(515,748),(428,755),(408,816),(459,837),
                   (262,837),(313,816),(295,755),(212,748)],fill="#4b4b51",outline="#b39c78",width=4)
        draw_stormbreaker(d,370,641-39*p,3.4)
        for index in range(9):
            phase=(second*.7+index*.14)%1
            x=360+(index-4)*phase*49;y=653-phase*(136+index*8)
            d.line((x,y,x+8,y-13),fill="#ffd69c",width=3)
        return
    for index,(who,x,dx) in enumerate((("thor",182,1),("bill",535,-1))):
        y=507+round(8*math.sin(second*2+index))
        actor=warrior(d,who,x,y,1.42,dx)
        hand=(x+95*dx,552-30*p)
        reach(d,actor,(x+67*dx,620),hand,1.35)
        if who=="thor":
            draw_hammer(d,*hand,1.62)
        else:
            draw_stormbreaker(d,*hand,1.62)
    d.line((101,785,622,785),fill="#526f77",width=3)


def draw_stormbreaker(d,x,y,s):
    draw_hammer(d,x,y,s,head="#b98b52",edge="#f0ce8d")
    d.polygon([(x+20*s,y-48*s),(x+47*s,y-66*s),(x+56*s,y-55*s),
               (x+55*s,y-26*s),(x+47*s,y-17*s),(x+20*s,y-34*s)],
              fill="#c89d65",outline="#efd197",width=max(1,round(1.5*s)))
