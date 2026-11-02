"""Original reusable human-shaped collage bodies; no copied TV/body assets."""
from PIL import ImageDraw,ImageColor
from hashlib import sha256


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


def draw_human_body(image,x,y,head_size,shirt):
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
    skin='#deb38f';skin_shadow='#bd8c6b';pants='#252c39';pants_light='#343e50';shoes='#11151d'
    # Legs are separate tapered shapes with a visible gap between the feet.
    polygon([(-.34,2.17),(.02,2.17),(-.06,3.12),(-.12,3.83),(-.37,3.83),(-.40,3.05)],pants_light)
    polygon([(-.02,2.17),(.34,2.17),(.40,3.05),(.37,3.83),(.12,3.83),(.06,3.12)],pants)
    polygon([(-.38,3.72),(-.12,3.72),(-.10,3.99),(-.53,3.99),(-.55,3.91)],shoes)
    polygon([(.12,3.72),(.38,3.72),(.55,3.91),(.53,3.99),(.10,3.99)],shoes)
    line([(-.49,3.98),(-.12,3.98)],'#8c939e',.025)
    line([(.13,3.98),(.49,3.98)],'#8c939e',.025)
    # Upper arms and short sleeves sit behind the torso; bare forearms end in hands.
    for side in (-1,1):
        polygon([(side*.30,1.03),(side*.53,1.13),(side*.68,1.82),(side*.43,1.88),(side*.30,1.48)],shadow)
        polygon([(side*.47,1.79),(side*.65,1.76),(side*.60,2.36),(side*.45,2.36),(side*.41,2.15)],skin)
        ellipse((side*.53-.105,2.26,side*.53+.105,2.55),skin)
        line([(side*.58,2.39),(side*.58,2.49)],skin_shadow,.015)
    # Neck and sloped shoulders make the animal head read as attached to a body.
    polygon([(-.13,.76),(.13,.76),(.14,1.13),(-.14,1.13)],skin)
    polygon([(-.12,1.00),(-.43,1.10),(-.46,1.39),(-.31,1.78),(-.33,2.23),(.33,2.23),(.31,1.78),(.46,1.39),(.43,1.10),(.12,1.00),(0,1.12)],shirt)
    polygon([(-.12,1.00),(0,1.12),(-.08,1.24),(-.22,1.06)],'#e8e8e4')
    polygon([(.12,1.00),(.22,1.06),(.08,1.24),(0,1.12)],'#d6d8d8')
    line([(-.31,2.20),(.31,2.20)],shadow,.045)
    line([(-.30,1.29),(-.25,1.77),(-.28,2.12)],shadow,.018)
    line([(.31,1.28),(.25,1.72)],shadow,.018)
    # Small chest pocket and visible device indicator are static collage details.
    polygon([(.10,1.36),(.28,1.36),(.28,1.57),(.19,1.63),(.10,1.57)],shadow)
    ellipse((.16,1.39,.20,1.43),'#8bd4ff')
    line([(-.31,2.27),(.31,2.27)],'#151923',.055)
    polygon([(-.055,2.24),(.055,2.24),(.055,2.30),(-.055,2.30)],'#aeb1b6')
