"""Original reusable human-shaped collage bodies; no copied TV/body assets."""
from PIL import ImageDraw,ImageColor
from hashlib import sha256
import re


def resolve_wardrobes(cast):
    """Compile distinct, stable outfits; preserve a character's outfit across shots."""
    styles=['shirt','hoodie','jacket','sweater','tshirt'];used=set();used_colors=set();result={}
    colors={'blue':'#325c9a','red':'#ad493a','green':'#4d7257','purple':'#765c90','yellow':'#b58b28','black':'#30343e','white':'#d4d7db'}
    for actor in sorted(cast,key=lambda a:a['id']):
        text=actor.get('costume','').lower();tokens=set(re.findall(r'[a-z]+',text))
        style=next((s for s in ('hoodie','jacket','sweater') if s in tokens),None)
        if style is None:style='tshirt' if 't-shirt' in text or 'tshirt' in tokens else 'shirt'
        color=next((value for word,value in colors.items() if word in tokens),shirt_color(actor))
        original_color=color
        if color in used_colors:color=next((c for c in colors.values() if c not in used_colors),color)
        original=style
        for candidate in [original,*styles]:
            if (candidate,color) not in used:style=candidate;break
        if (style,color) in used:
            color=next(c for c in colors.values() if (style,c) not in used)
        used.add((style,color));used_colors.add(color)
        result[actor['id']]={'style':style,'shirt':color,'pants':'#726754' if style in ('hoodie','tshirt') else '#252c39',
            'requested':actor.get('costume',''),'distinctness_adjustment':style!=original or color!=original_color}
    return result


def shirt_color(actor):
    explicit=actor.get('shirt_color')
    if explicit:
        ImageColor.getrgb(explicit)
        return explicit
    name=actor['speaker'].strip().lower()
    if name=='alex':return '#325c9a'
    if name=='mike':return '#ad493a'
    palette=['#325c9a','#ad493a','#4d7257','#765c90']
    return palette[int(sha256(name.encode()).hexdigest()[:8],16)%len(palette)]


def draw_human_body(image,x,y,head_size,shirt,style='shirt',pose='neutral',pants_color=None):
    """Draw below a head box at (x,y), using head width as the scale unit.

    The normalized model has shoulders, articulated arms, hands, a tapered
    torso, two separated trouser legs and shoes. The same model scales from
    full-body wide shots to shoulder crops without changing character identity.
    """
    draw=ImageDraw.Draw(image);s=head_size;cx=x+s/2
    def point(px,py):return (round(cx+px*s),round(y+py*s))
    def polygon(points,fill):draw.polygon([point(*p) for p in points],fill=fill)
    def line(points,fill,width):draw.line([point(*p) for p in points],fill=fill,width=max(1,round(width*s)),joint='curve')
    def ellipse(box,fill):draw.ellipse((*point(*box[:2]),*point(*box[2:])),fill=fill)
    rgb=ImageColor.getrgb(shirt);shadow=tuple(round(c*.70) for c in rgb)
    skin='#deb38f';skin_shadow='#bd8c6b';pants=pants_color or '#252c39';pants_light=tuple(min(255,round(c*1.15)) for c in ImageColor.getrgb(pants)) if pants_color else '#343e50';shoes='#11151d'
    # Legs are separate tapered shapes with a visible gap between the feet.
    polygon([(-.34,2.17),(.02,2.17),(-.06,3.12),(-.12,3.83),(-.37,3.83),(-.40,3.05)],pants_light)
    polygon([(-.02,2.17),(.34,2.17),(.40,3.05),(.37,3.83),(.12,3.83),(.06,3.12)],pants)
    polygon([(-.38,3.72),(-.12,3.72),(-.10,3.99),(-.53,3.99),(-.55,3.91)],shoes)
    polygon([(.12,3.72),(.38,3.72),(.55,3.91),(.53,3.99),(.10,3.99)],shoes)
    line([(-.49,3.98),(-.12,3.98)],'#8c939e',.025)
    line([(.13,3.98),(.49,3.98)],'#8c939e',.025)
    # Upper arms and short sleeves sit behind the torso; bare forearms end in hands.
    for side in (-1,1):
        if (pose in ('talk','point') and side==1) or pose=='react':
            elbow=(side*.88,1.64);hand=(side*(1.10 if pose=='point' else .89),1.04 if pose=='react' else 1.25)
            line([(side*.37,1.15),elbow],shadow,.25)
            line([elbow,hand],shirt if style in ('hoodie','jacket','sweater') else skin,.16)
            ellipse((hand[0]-.09,hand[1]-.09,hand[0]+.09,hand[1]+.09),skin)
            continue
        polygon([(side*.30,1.03),(side*.53,1.13),(side*.68,1.82),(side*.43,1.88),(side*.30,1.48)],shadow)
        polygon([(side*.47,1.79),(side*.65,1.76),(side*.60,2.36),(side*.45,2.36),(side*.41,2.15)],shirt if style in ('hoodie','jacket','sweater') else skin)
        ellipse((side*.53-.105,2.26,side*.53+.105,2.55),skin)
        line([(side*.58,2.39),(side*.58,2.49)],skin_shadow,.015)
    # Neck and sloped shoulders make the animal head read as attached to a body.
    polygon([(-.13,.76),(.13,.76),(.14,1.13),(-.14,1.13)],skin)
    polygon([(-.12,1.00),(-.43,1.10),(-.46,1.39),(-.31,1.78),(-.33,2.23),(.33,2.23),(.31,1.78),(.46,1.39),(.43,1.10),(.12,1.00),(0,1.12)],shirt)
    if style=='shirt':
        polygon([(-.12,1.00),(0,1.12),(-.08,1.24),(-.22,1.06)],'#e8e8e4')
        polygon([(.12,1.00),(.22,1.06),(.08,1.24),(0,1.12)],'#d6d8d8')
    elif style=='hoodie':
        ellipse((-.24,.78,.24,1.22),shadow)
        ellipse((-.13,.89,.13,1.15),skin)
        line([(-.09,1.13),(-.10,1.55)],'#e2dfd8',.025);line([(.09,1.13),(.10,1.55)],'#e2dfd8',.025)
        polygon([(-.23,1.77),(.23,1.77),(.27,2.05),(-.27,2.05)],shadow)
    elif style=='jacket':
        polygon([(-.15,1.01),(.15,1.01),(.10,2.15),(-.10,2.15)],'#e4e1d8')
        polygon([(-.15,1.01),(-.26,1.16),(-.10,1.65),(0,1.28)],shadow)
        polygon([(.15,1.01),(.26,1.16),(.10,1.65),(0,1.28)],shadow)
        line([(0,1.45),(0,2.19)],shadow,.025)
    else:
        line([(-.15,1.02),(0,1.15),(.15,1.02)],shadow,.055)
    line([(-.31,2.20),(.31,2.20)],shadow,.045)
    line([(-.30,1.29),(-.25,1.77),(-.28,2.12)],shadow,.018)
    line([(.31,1.28),(.25,1.72)],shadow,.018)
    # Small chest pocket and visible device indicator are static collage details.
    if style in ('shirt','jacket'):
        polygon([(.10,1.36),(.28,1.36),(.28,1.57),(.19,1.63),(.10,1.57)],shadow)
        ellipse((.16,1.39,.20,1.43),'#8bd4ff')
    line([(-.31,2.27),(.31,2.27)],'#151923',.055)
    polygon([(-.055,2.24),(.055,2.24),(.055,2.30),(-.055,2.30)],'#aeb1b6')
