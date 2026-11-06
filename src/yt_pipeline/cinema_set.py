"""Local theater artwork and motion for a row of seated audience cutouts."""
from functools import lru_cache
import math

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


def light_actor(actor):
    alpha = actor.getchannel("A")
    rgb = ImageEnhance.Color(actor.convert("RGB")).enhance(.88)
    projected = ImageOps.colorize(rgb.convert("L"), "#121929", "#ece3cc", mid="#70888c")
    lit = Image.blend(rgb, projected, .26).convert("RGBA")
    lit.putalpha(alpha)
    return lit


@lru_cache(maxsize=1)
def theater_room():
    room = Image.new("RGB", (720, 288), "#161825")
    halo = Image.new("RGBA", room.size)
    glow = ImageDraw.Draw(halo)
    glow.ellipse((125, -103, 596, 115), fill=(84, 112, 128, 112))
    halo = halo.filter(ImageFilter.GaussianBlur(34))
    room.paste(halo, (0, 0), halo)
    draw = ImageDraw.Draw(room)
    draw.line(((25, 16), (360, 4), (695, 16)), fill="#8b7565", width=2)
    draw.line(((25, 22), (360, 10), (695, 22)), fill="#3e4050")
    draw.line(((14, 49), (360, 24), (705, 49)), fill="#343948")
    for x in (40, 680):
        draw.rounded_rectangle((x-15, 27, x+15, 79), 4, fill="#302632", outline="#705968")
        draw.rectangle((x-6, 36, x+6, 69), fill="#a1856b")
        draw.line((x, 42, x, 65), fill="#d8ac76", width=2)
    for x in range(-42, 734, 78):
        draw.rounded_rectangle((x, 89, x+68, 170), 14, fill="#2a2230", outline="#4d3d4d", width=2)
        draw.arc((x+6, 94, x+62, 132), 185, 355, fill="#51424e")
    for x in range(-6, 758, 105):
        draw.rounded_rectangle((x, 128, x+91, 221), 17, fill="#372633", outline="#59414f", width=2)
    draw.rectangle((0, 235, 720, 287), fill="#211923")
    return room


def draw_theater(frame, cast, props, time):
    """Composite one room at the bottom of the Shorts frame."""
    room = theater_room().copy()
    draw = ImageDraw.Draw(room)
    for x, prop in zip((59, 661), props):
        room.paste(prop, (x - prop.width//2, 226 - prop.height), prop)
    spacing = min(221, 640 / len(cast))
    centers = [round(360 + (index - (len(cast)-1)/2)*spacing) for index in range(len(cast))]
    for index, (x, actor) in enumerate(zip(centers, cast)):
        draw.rounded_rectangle((x-102, 92, x+102, 277), 30, fill="#533142", outline="#825b62", width=3)
        draw.rounded_rectangle((x-92, 102, x+92, 253), 25, outline="#6b4351", width=2)
        draw.arc((x-84, 104, x+84, 159), 185, 355, fill="#9a6e70", width=2)
        y = 34 + round(2 * math.sin(time * 2.4 + index))
        room.paste(actor, (x - actor.width//2, y), actor)
        draw.rounded_rectangle((x-108, 241, x+108, 296), 19, fill="#352432", outline="#664653", width=2)
        for edge in (x-100, x+100):
            draw.rounded_rectangle((edge-13, 223, edge+13, 285), 8, fill="#3b2b3a", outline="#79515d", width=2)
        carton_x = x + (43 if index % 2 == 0 else -41)
        draw_popcorn(draw, carton_x)
        if index == len(cast)-1:
            progress = (time / 3.2 + .13) % 1
            if .16 < progress < .64:
                lift = (progress - .16) / .48
                px = carton_x + (x - carton_x)*lift
                py = 190 - 99*lift - 12*math.sin(math.pi*lift)
                draw.ellipse((px-3, py-3, px+3, py+3), fill="#f6deb0", outline="#876651")
    frame.paste(room, (0, 992))


def draw_popcorn(draw, x):
    draw.polygon([(x-25, 199), (x+25, 199), (x+17, 257), (x-16, 257)],
                 fill="#c49a79", outline="#3c2630", width=2)
    for stripe in (-13, 0, 13):
        draw.line((x+stripe, 205, x+stripe*.66, 252), fill="#9f514c", width=5)
    for dx, dy, radius in ((-18, 1, 7), (-9, -6, 8), (1, 0, 8), (9, -8, 7), (17, 0, 7)):
        draw.ellipse((x+dx-radius, 194+dy-radius, x+dx+radius, 194+dy+radius),
                     fill="#ecd6a9", outline="#987b61")
    draw.line((x-23, 204, x+23, 204), fill="#f1c8a0", width=2)
