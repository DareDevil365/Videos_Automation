"""Geometric origin-story panels for the comic-lore illustration viewport."""
import math

from PIL import ImageDraw


FORGE_KINDS = ("hot_mask", "lab_blast", "mountain_pass", "forge", "forge_warning",
               "mask_fitting", "mask_cooling")
GOLD = "#d2be88"
INK = "#101a22"


def mask(draw, x, y, scale, heat):
    cold = (137, 161, 161)
    hot = (255, 105, 41)
    steel = tuple(round(a + (b - a) * heat) for a, b in zip(cold, hot))
    rim = "#ffd298" if heat > .2 else "#d8e0d5"

    def poly(points, color, outline=None):
        draw.polygon([(x + a * scale, y + b * scale) for a, b in points],
                     fill=color, outline=outline, width=max(1, round(3 * scale)))

    poly([(-45, -46), (0, -61), (45, -46), (50, 12), (27, 51),
          (0, 59), (-27, 51), (-50, 12)], steel, rim)
    poly([(0, -58), (44, -45), (49, 11), (26, 50), (0, 57)], "#323a3c" if heat < .25 else "#a74332")
    poly([(-37, -17), (-7, -12), (-11, -1), (-33, -5)], INK, rim)
    poly([(7, -12), (37, -17), (33, -5), (11, -1)], INK, rim)
    poly([(-6, 13), (0, -13), (8, 14)], "#422b29", rim)
    poly([(-21, 26), (21, 26), (16, 36), (-16, 36)], INK, rim)


def monk(draw, x, y, scale, color, hands, worried=False):
    def point(a, b):
        return x + a * scale, y + b * scale

    def poly(points, fill):
        draw.polygon([point(a, b) for a, b in points], fill=fill, outline=GOLD, width=2)

    poly([(-75, 115), (-53, -31), (-30, -54), (30, -54), (53, -31), (75, 115)], color)
    poly([(-43, -39), (-37, -87), (0, -116), (37, -87), (43, -39), (0, -15)], color)
    poly([(-29, -71), (0, -93), (29, -71), (24, -38), (0, -24), (-24, -38)], "#cb986d")
    for side in (-1, 1):
        draw.line([point(side * 21, -65), point(side * 8, -71 if worried else -64)],
                  fill=INK, width=max(2, round(3 * scale)))
        draw.ellipse((*point(side * 13 - 3, -61), *point(side * 13 + 3, -55)), fill=INK)
    draw.ellipse((*point(-7, -49), *point(7, -35 if worried else -45)), fill=INK)
    for side, (hx, hy) in zip((-1, 1), hands):
        draw.line([point(side * 40, -13), point(side * 48, 18), (hx, hy)],
                  fill=GOLD, width=max(2, round(20 * scale)), joint="curve")
        draw.line([point(side * 40, -13), point(side * 48, 18), (hx, hy)],
                  fill=color, width=max(2, round(16 * scale)), joint="curve")
        radius = 8 * scale
        draw.ellipse((hx - radius, hy - radius, hx + radius, hy + radius),
                     fill="#cb986d", outline=GOLD, width=2)


def forge_art(layer, kind, second, progress, glow):
    d = ImageDraw.Draw(layer)
    if kind == "mountain_pass":
        d.polygon([(44, 768), (183, 411), (306, 573), (461, 272), (674, 744),
                   (674, 865), (44, 865)], fill="#223a48", outline="#89aab2", width=4)
        d.polygon([(354, 478), (461, 272), (555, 482), (485, 431), (456, 474),
                   (424, 428)], fill="#a0b9b6", outline="#d4dfd3", width=3)
        path = [(128, 846), (220, 761), (344, 731), (304, 666), (453, 606), (501, 563)]
        d.line(path, fill=GOLD, width=5, joint="curve")
        for index in range(len(path) - 1):
            a, b = path[index:index+2]
            q = (progress * .8 + index * .17) % 1
            x, y = (a[i] + (b[i] - a[i]) * q for i in range(2))
            d.ellipse((x-5, y-5, x+5, y+5), fill="#fff2cb")
        d.rectangle((471, 523, 527, 564), fill="#6f583e", outline=GOLD, width=3)
        d.polygon([(457, 524), (499, 495), (541, 524)], fill="#3e2b2b", outline=GOLD, width=3)
        d.rectangle((493, 542, 505, 563), fill="#ffd295")
        return
    if kind == "lab_blast":
        glow(layer, (358, 511), 108, (255, 132, 76), 110)
        d.rectangle((83, 732, 640, 756), fill="#50616a", outline="#b0c1bd", width=3)
        d.line([(158, 732), (158, 512), (234, 512)], fill="#90a5a8", width=7)
        d.arc((240, 361, 485, 667), 0, 360, fill="#779fa7", width=6)
        rays = 16
        points = []
        for index in range(rays):
            angle = index * math.tau / rays
            radius = (46 if index % 2 else 102) * (1 + .45 * progress)
            points.append((360 + radius * math.cos(angle), 515 + radius * math.sin(angle)))
        d.polygon(points, fill="#e78d5c", outline="#fff0b4", width=4)
        for index in range(7):
            a = index * .78
            x, y = 361 + (125 + 82 * progress) * math.cos(a), 512 + (125 + 82 * progress) * math.sin(a)
            d.polygon([(x, y), (x + 18, y - 5), (x + 9, y + 16)], fill="#dc9a70")
        return
    if kind == "forge":
        glow(layer, (352, 631), 130, (253, 112, 43), 115)
        d.polygon([(41, 790), (41, 447), (90, 372), (146, 372), (190, 447),
                   (190, 790)], fill="#322428", outline="#735849", width=4)
        d.polygon([(59, 743), (77, 636), (93, 697), (123, 599), (148, 689),
                   (166, 662), (176, 743)], fill="#a95337", outline="#e5a06b", width=3)
        strike = (1 - math.cos(second * math.tau / 1.2)) / 2
        hand_y = 510 + 90 * strike
        monk(d, 184, 562, 1.23, "#60443c", [(170, 613), (266, hand_y)])
        monk(d, 548, 557, 1.29, "#6c543c", [(476, 578), (448, 606)])
        d.polygon([(226, 657), (488, 657), (449, 697), (394, 707), (384, 766),
                   (432, 793), (282, 793), (331, 766), (321, 708), (272, 697)],
                  fill="#435052", outline="#a2aaa1", width=4)
        mask(d, 357, 618, .82, .93)
        d.line([(476, 578), (372, 610), (367, 627)], fill="#b9c6bf", width=6)
        d.line([(448, 606), (372, 610), (380, 628)], fill="#d2d6be", width=5)
        d.line([(253, hand_y + 13), (320, hand_y - 37)], fill="#ba895f", width=12)
        y = hand_y - 43
        d.polygon([(304, y - 18), (343, y - 7), (337, y + 19), (298, y + 7)],
                  fill="#819491", outline="#d6dac9", width=3)
        for index in range(11):
            age = ((second + index * .017 + .6) % 1.2)
            if age < .44:
                x = 347 + (index - 5) * age * 55
                sy = 604 - age * (145 + index * 7)
                d.line([(x, sy), (x + (index - 5) * 3, sy - 13)],
                       fill="#ffcb85", width=3)
        return
    if kind == "forge_warning":
        glow(layer, (428, 620), 154, (213, 97, 44), 84)
        monk(d, 302, 557, 2.4, "#674b40", [(198, 593), (445, 500 - progress * 22)], worried=True)
        for radius in (23, 39, 56):
            d.arc((445-radius, 489-radius, 445+radius, 489+radius),
                  238, 318, fill="#ffd8a1", width=4)
        d.line([(520, 654), (559, 684), (609, 684)], fill=GOLD, width=3)
        mask(d, 572, 621, 1.02, .93)
        return

    # Match-cut the same mask silhouette across the teaser, profile and cooldown.
    fitting = kind == "mask_fitting"
    heat = 1 - .99 * progress if kind == "mask_cooling" else .94
    x = 460 - 156 * min(1, progress * 1.55) if fitting else 360
    y = 554
    glow(layer, (x, y), 143, (242, 98, 48), round(25 + heat * 95))
    if fitting:
        d.polygon([(70, 803), (112, 664), (177, 635), (160, 579), (165, 507),
                   (206, 445), (264, 449), (298, 494), (303, 522), (329, 549),
                   (309, 563), (309, 600), (270, 619), (293, 664), (355, 803)],
                  fill="#263c39", outline="#9cb5a2", width=4)
        d.line([(282, 529), (300, 532)], fill="#d3d8c5", width=4)
    else:
        for index in range(3):
            radius = 163 + 30 * index
            d.arc((x-radius, y-radius, x+radius, y+radius),
                  25 + 17 * index, 152 + 17 * index, fill="#716357", width=2)
            d.arc((x-radius, y-radius, x+radius, y+radius),
                  205 + 17 * index, 332 + 17 * index, fill="#716357", width=2)
    mask(d, x, y, 1.23 if fitting else 2.24, heat)
    for index in range(4):
        sx = x + (index - 1.5) * 35
        phase = (second * .8 + index * .24) % 1
        sy = y - 83 - phase * 118
        if heat > .2:
            d.line([(sx, sy), (sx-12, sy-20), (sx+2, sy-39)],
                   fill="#b8937a", width=2)
