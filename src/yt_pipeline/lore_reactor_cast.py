"""Flat, articulated portraits for the Iron Man story and workshop."""
from PIL import Image, ImageDraw


TONY = "tony"
PEPPER = "pepper"
STANE = "stane"
HAPPY = "happy"

SKIN = {TONY: "#c89574", PEPPER: "#e2ad89", STANE: "#d8a98d", HAPPY: "#c48d70"}
CLOTHES = {TONY: "#365463", PEPPER: "#706273", STANE: "#333749", HAPPY: "#304341"}
LINE = "#b9aa93"


def person(draw, who, x, y, scale=1, *, facing=1, jacket=None):
    """Draw a bust. The returned anchors are on the inner shoulder and chest."""
    def point(dx, dy):
        return (x + dx * scale * facing, y + dy * scale)

    def face(points, fill, outline=None, width=2):
        draw.polygon([point(dx, dy) for dx, dy in points],
                     fill=fill, outline=outline, width=max(1, round(width * scale)))

    def feature(points, color, width):
        draw.line([point(dx, dy) for dx, dy in points], fill=color, width=max(1, round(width * scale)))

    shoulder, waist = {TONY: (74, 67), PEPPER: (62, 50), STANE: (92, 86), HAPPY: (92, 86)}[who]
    skin, clothes = SKIN[who], jacket or CLOTHES[who]
    if who == PEPPER:
        face([(-49,-9),(-40,-47),(-5,-61),(32,-48),(41,-19),(37,31),
              (49,66),(22,61),(-21,64),(-52,50)], "#935338", "#d4a278")
    face([(-waist,214),(-shoulder,101),(-shoulder+15,77),(-33,64),
          (33,64),(shoulder-14,77),(shoulder,102),(waist,214)], clothes, LINE)
    face([(-18,30),(23,28),(22,70),(0,85),(-20,71)], "#a9745c")
    if who == TONY:
        feature([(-24,70),(-11,83),(4,87),(22,80),(31,69)], "#81a0a3", 4)
        feature([(-50,92),(-46,161),(-38,197)], "#4a6a74", 3)
    else:
        face([(-33,66),(0,87),(32,66),(18,132),(-15,132)], "#c9c5b5")
        face([(-34,67),(-11,111),(0,174),(-43,114),(-30,101),(-49,94)], clothes, LINE, 1)
        face([(33,67),(11,112),(0,174),(40,114),(28,100),(48,94)], clothes, LINE, 1)
        if who in (STANE, HAPPY):
            tie = "#a87968" if who == STANE else "#687b87"
            face([(-8,92),(8,92),(9,103),(4,110),(9,151),(0,168),(-9,150),(-4,110),(-9,103)], tie)
    if who == STANE:
        face([(-43,-1),(-38,-34),(-22,-48),(12,-51),(35,-38),(44,-15),
              (42,15),(31,38),(9,53),(-19,48),(-40,29)], skin, LINE)
        face([(-38,16),(-17,28),(15,22),(38,18),(31,39),(9,54),(-18,49),(-35,35)],
             "#8d8d88")
        face([(-28,-32),(-13,-43),(13,-46),(29,-35),(8,-31)], "#e6bca0")
    elif who == HAPPY:
        face([(-44,-13),(-38,-37),(-13,-50),(23,-46),(40,-27),(44,-3),
              (48,10),(33,19),(30,39),(11,49),(-20,42),(-39,20)], skin, LINE)
        face([(-42,16),(-49,-7),(-43,-34),(-25,-52),(-8,-57),(25,-52),(44,-37),
              (43,-20),(24,-29),(10,-31),(-13,-26),(-27,-8),(-30,19)], "#352e30", "#7f685b")
    else:
        face([(-36,-31),(-20,-50),(16,-51),(35,-33),(40,-6),(48,8),
              (37,14),(30,40),(11,49),(-14,40),(-32,21)], skin, LINE)
        if who == TONY:
            face([(-38,14),(-46,-15),(-39,-40),(-19,-56),(20,-58),(42,-41),
                  (18,-38),(0,-44),(-18,-29),(-24,9),(-30,20)], "#332a2b", "#79675d")
            face([(4,22),(30,19),(30,32),(21,44),(9,46),(-3,37),(5,30)], "#403030")
        else:
            face([(-39,25),(-44,-15),(-31,-43),(-6,-55),(19,-51),(35,-36),
                  (11,-33),(-8,-24),(-22,-4),(-28,36)], "#b6714d")
            feature([(-35,-16),(-24,-35),(-7,-45),(12,-46)], "#d18b5e", 3)
    feature([(11,-10),(22,-13),(31,-10)], "#4e3a35", 3)
    feature([(18,-3),(28,-3)], "#2a292f", 3)
    feature([(17,25),(26,25)], "#6b4841", 2)
    return point(shoulder-12, 92), point(9, 141)


def arm(draw, who, shoulder, elbow, hand, scale=1, *, jacket=None):
    sleeve = max(4, round((33 if who in (STANE, HAPPY) else 25) * scale))
    draw.line([shoulder, elbow, hand], fill=LINE, width=sleeve+3, joint="curve")
    draw.line([shoulder, elbow, hand], fill=jacket or CLOTHES[who], width=sleeve, joint="curve")
    radius = 10 * scale
    x, y = hand
    draw.ellipse((x-radius,y-radius,x+radius,y+radius), fill=SKIN[who], outline=LINE, width=2)


def workshop_tony():
    """Transparent seated cutout for the existing lower workshop set."""
    image = Image.new("RGBA", (380, 360))
    draw = ImageDraw.Draw(image)
    shoulder, chest = person(draw, TONY, 184, 82, 1.16)
    arm(draw, TONY, shoulder, (270,267), (236,290), 1.16)
    arm(draw, TONY, (109,189), (89,258), (130,283), 1.16)
    draw.polygon([(121,307),(189,311),(245,302),(278,320),(283,347),(99,347)],
                 fill="#263741", outline=LINE, width=3)
    x,y = chest
    draw.ellipse((x-16,y-16,x+16,y+16), fill="#256777", outline="#a9edf0", width=3)
    draw.ellipse((x-7,y-7,x+7,y+7), fill="#c6faff")
    return image.crop(image.getbbox())
