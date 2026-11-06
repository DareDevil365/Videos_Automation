"""Draw a comic workshop in layers around one isolated Tony reference."""
from argparse import ArgumentParser
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

INK = "#09141e"
SCALE = 2


class Art:
    """Draw in 760 × 320 panel coordinates, with oversampling for clean curves."""

    def __init__(self, fill=None):
        self.image = Image.new("RGBA", (760 * SCALE, 320 * SCALE), fill)
        self.draw = ImageDraw.Draw(self.image)

    def shape(self, segments, fill, edge=None, width=1):
        points = [segments[0]]
        for segment in segments[1:]:
            if len(segment) == 2:
                points.append(segment)
                continue
            x0, y0 = points[-1]
            x1, y1, x2, y2, x3, y3 = segment
            for step in range(1, 13):
                t = step / 12
                u = 1 - t
                points.append((
                    u**3*x0 + 3*u*u*t*x1 + 3*u*t*t*x2 + t**3*x3,
                    u**3*y0 + 3*u*u*t*y1 + 3*u*t*t*y2 + t**3*y3,
                ))
        if fill is not None:
            self.draw.polygon(self._points(points), fill=fill)
        if edge:
            self.line([*points, points[0]] if fill is not None else points, edge, width)

    def line(self, points, fill, width=1):
        self.draw.line(self._points(points), fill=fill, width=round(width * SCALE), joint="curve")

    def ellipse(self, box, fill, edge=None, width=1):
        self.draw.ellipse(tuple(round(value * SCALE) for value in box), fill=fill,
                          outline=edge, width=round(width * SCALE))

    def _points(self, points):
        return [(round(x * SCALE), round(y * SCALE)) for x, y in points]

    def finish(self):
        return self.image.resize((760, 320), Image.Resampling.LANCZOS)


def draw_suit(art, x, y, height, plates, *, width_scale=1, riveted=False):
    dark, body, rim, mask = plates
    scale = height / 122

    def path(points, fill, edge=INK, width=1):
        converted = [
            tuple(x + value * scale * width_scale if index % 2 == 0 else y + value * scale
                  for index, value in enumerate(segment))
            for segment in points
        ]
        art.shape(converted, fill, edge, width)

    # One armored silhouette with colored panel breaks. Vary the plating by bay.
    path([(0, 0), (11, 1), (16, 9), (14, 22), (27, 29), (33, 46), (34, 68),
          (27, 74), (22, 56), (19, 51), (17, 70), (20, 94), (19, 114), (26, 119),
          (23, 123), (10, 123), (8, 116), (3, 93), (0, 83), (-4, 101), (-7, 119),
          (-13, 123), (-26, 123), (-27, 119), (-20, 112), (-20, 91), (-16, 69),
          (-18, 49), (-23, 59), (-27, 75), (-34, 68), (-33, 49), (-28, 31), (-14, 23),
          (-15, 8), (-9, 1)], dark)
    path([(-25, 32), (-13, 25), (-2, 31), (0, 47), (-11, 49), (-21, 43)], body)
    path([(2, 31), (13, 25), (26, 31), (22, 42), (12, 49), (0, 47)], body)
    path([(-17, 50), (-7, 52), (0, 55), (8, 52), (17, 49), (13, 65),
          (6, 73), (-6, 73), (-13, 65)], body)
    path([(-13, 76), (-4, 81), (-9, 106), (-15, 114), (-18, 110), (-17, 96)], rim)
    path([(12, 76), (5, 81), (9, 105), (16, 114), (18, 109), (17, 94)], body)
    path([(-29, 49), (-24, 47), (-25, 64), (-29, 69), (-32, 65)], rim)
    path([(24, 47), (28, 47), (32, 65), (29, 70), (25, 63)], body)
    path([(-9, 5), (1, 3), (10, 6), (12, 12), (8, 20), (2, 24), (-6, 22),
          (-11, 15)], mask)
    path([(-9, 12), (-3, 13), (0, 12), (8, 11)], None, "#c3ded4", 1.3)
    path([(-6, 19), (0, 21), (6, 18)], None, "#18242b", 1.1)
    path([(-3, 40), (0, 37), (5, 40), (1, 45)], "#d5e6cd", "#5b8c84")
    path([(-13, 28), (-5, 31), (0, 34), (12, 28)], None, rim, 1.1)
    if riveted:
        path([(-11, 9), (11, 9), (11, 17), (-11, 17)], "#748477", "#293c40")
        path([(-8, 12), (-2, 12), (3, 12), (8, 12)], None, "#13222b", 1.6)
        for side in (-1, 1):
            for row in (54, 59, 64):
                path([(side * 9, row), (side * 13, row)], None, rim)


def wheel(art, x, y, rx, ry, metal):
    art.ellipse((x-rx, y-ry, x+rx, y+ry), "#080e17", "#45575a", 1.4)
    art.ellipse((x-rx*.68, y-ry*.73, x+rx*.68, y+ry*.73), metal, "#20323c")
    art.ellipse((x-rx*.48, y-ry*.5, x+rx*.48, y+ry*.5), "#273b42")
    for a, b in ((.0, -.55), (.49, -.18), (.32, .47), (-.32, .47), (-.5, -.18)):
        art.line(((x, y), (x+a*rx, y+b*ry)), metal, 1.25)
    art.ellipse((x-2.3, y-2.3, x+2.3, y+2.3), "#c0b598")


def draw_coupe(art):
    art.ellipse((510, 177, 727, 203), "#102028")
    wheel(art, 561, 178, 15, 20, "#86918a")
    wheel(art, 687, 172, 14, 17, "#86918a")
    art.shape([(513, 174), (515, 161, 528, 154, 550, 150),
               (575, 149), (598, 133, 609, 121, 632, 120),
               (659, 117, 686, 124, 701, 137), (720, 143), (728, 155), (724, 172),
               (702, 176), (700, 155, 680, 151, 675, 174), (573, 190),
               (570, 163, 549, 161, 547, 185), (520, 183)], "#8aa7a4", INK, 2)
    art.shape([(575, 149), (602, 132, 615, 124, 638, 124), (661, 122, 681, 128, 692, 139),
               (654, 143), (624, 149), (594, 151)], "#243e4a", "#aac1b7")
    art.shape([(614, 133), (635, 127), (653, 128), (637, 142), (602, 145)], "#486773")
    art.shape([(513, 174), (541, 176), (548, 169), (546, 185), (519, 184)], "#27383e")
    art.shape([(572, 179), (625, 173), (661, 160), (675, 157), (672, 175),
               (571, 190)], "#476765")
    art.shape([(519, 162), (540, 157), (546, 158), (541, 163), (520, 168)], "#e2d6a8")
    art.shape([(717, 144), (725, 150), (724, 155), (712, 151)], "#ba734f")
    art.line(((575, 153), (619, 153), (650, 147), (684, 142)), "#cbd5bd")
    art.line(((658, 146), (653, 162), (645, 172)), "#263e47")
    art.line(((614, 155), (623, 154)), "#d0d4b6", 1.25)
    art.line(((524, 174), (537, 174)), "#729a91")


def draw_hot_rod(art):
    art.ellipse((516, 262, 737, 302), "#101e25")
    wheel(art, 557, 263, 21, 25, "#ae9b74")
    wheel(art, 692, 271, 23, 25, "#c8b18a")
    art.shape([(521, 239), (537, 220, 551, 216, 583, 219), (617, 226),
               (647, 230), (672, 226), (699, 236), (715, 251), (713, 262),
               (711, 238, 678, 235, 671, 263), (663, 275), (580, 282),
               (578, 246, 550, 237, 537, 266), (526, 256)], "#344b51", INK, 2.2)
    art.shape([(535, 224), (558, 219, 579, 221, 608, 229), (622, 234),
               (575, 236), (551, 231)], "#70473f", "#b28c64")
    art.shape([(592, 221), (592, 206), (615, 209), (618, 227)], "#648483", "#cbb894", 1.5)
    art.line(((603, 207), (606, 224)), "#b9b798")
    art.shape([(619, 233), (648, 221), (671, 231), (663, 251), (620, 252)], "#87624b", "#c09d6f")
    art.shape([(659, 229), (673, 230), (677, 248), (671, 263), (657, 255)], "#422c2a", "#c59c6b", 1.3)
    for offset in (0, 4, 8, 12):
        art.line(((659+offset, 234), (658+offset, 253)), "#947550", .7)
    art.shape([(576, 245), (588, 248), (593, 242), (601, 243), (614, 247), (623, 243),
               (635, 245), (650, 250), (633, 253), (615, 251), (605, 256), (594, 251),
               (582, 255)], "#bc7450")
    art.line(((584, 267), (629, 266), (662, 256)), "#d1b180", 2)
    art.line(((586, 270), (624, 270), (657, 262)), "#655b51", 1.2)
    art.ellipse((669, 243, 679, 251), "#e2cf99", "#5d634e")
    art.ellipse((650, 239, 656, 245), "#c5c195", "#68745e")
    art.line(((540, 227), (555, 223), (576, 225)), "#ac9774")
    art.line(((624, 227), (627, 219), (635, 217), (640, 223), (649, 221)), "#d0a773", 1.5)


def garage():
    art = Art("#10212a")
    art.shape([(0, 64), (454, 43), (760, 79), (760, 220), (0, 234)], "#203d42")
    art.shape([(0, 211), (449, 194), (760, 231), (760, 320), (0, 320)], "#253e44")
    art.shape([(0, 18), (454, 21), (760, 54), (760, 79), (454, 43), (0, 64)], "#0b1823")
    art.line(((0, 64), (454, 43), (760, 79)), "#ad9c73", 1.4)
    art.line(((0, 70), (454, 49), (760, 85)), "#54716b")
    art.shape([(447, 49), (483, 54), (483, 202), (447, 210)], "#12262e", "#486861")
    art.line(((453, 51), (453, 207)), "#809284", 1.5)
    art.shape([(493, 60), (760, 91), (760, 202), (493, 170)], "#182e36", "#456562")
    for y in (101, 112, 123, 134, 145):
        art.line(((504, y), (748, y+25)), "#304d50")
    art.shape([(487, 170), (672, 158), (760, 174), (760, 194), (564, 213), (487, 194)],
              "#496967", "#78958a")
    art.shape([(487, 194), (564, 213), (760, 194), (760, 207), (564, 228), (487, 207)],
              "#233e46", "#50716a")
    art.line(((566, 217), (754, 198)), "#baa77c")
    for x in (25, 223, 450, 678, 911):
        art.line(((456, 203), (x, 320)), "#4d6661")
    for y in (251, 277, 311):
        art.line(((0, y), (465, y-14), (760, y-5)), "#425f5c")
    for y in range(91, 310, 5):
        for x in range(13 + y % 3, 752, 7):
            if (y < 145 and x > 498) or (y > 234 and x < 105):
                art.ellipse((x, y, x+.7, y+.7), "#47655f")

    palettes = (
        ("#28383e", "#586365", "#899386", "#adaf98"),
        ("#233844", "#637b7b", "#9ab0a5", "#abbcae"),
        ("#3b2d32", "#844c42", "#ad7752", "#c7a172"),
        ("#2f2833", "#714346", "#a3644c", "#ba8a5d"),
    )
    for index, palette in enumerate(palettes):
        x = 29 + index * 104
        y = 79 - index * 2
        art.shape([(x,y+10), (x+12,y), (x+87,y), (x+95,y+9), (x+95,y+143),
                   (x,y+151)], "#15272f", "#5c7c75", 1.5)
        art.shape([(x+10,y+15), (x+18,y+8), (x+78,y+8), (x+85,y+15), (x+85,y+132),
                   (x+10,y+140)], "#2e5053", "#76958a")
        art.shape([(x+12,y+131), (x+80,y+125), (x+89,y+136), (x+10,y+144)], "#53706a")
        art.line(((x+20,y+12), (x+76,y+12)), "#cfc299", 2)
        art.line(((x+14,y+21), (x+14,y+126)), "#799e91", 1.5)
        art.line(((x+82,y+20), (x+82,y+125)), "#83a899", 1.5)
        draw_suit(art, x+48, y+20, 110, palette, width_scale=(1.12, .88, 1, .94)[index],
                  riveted=index == 0)
    draw_coupe(art)
    draw_hot_rod(art)
    draw_sofa(art)
    return art.finish().convert("RGB")


def draw_sofa(art):
    art.shape([(92, 263), (93, 208, 106, 186, 139, 183), (178, 177, 231, 176, 285, 181),
               (354, 179), (401, 175, 449, 180, 482, 194), (510, 199, 532, 221, 535, 263),
               (510, 294), (104, 297)], "#232c32", INK, 3)
    art.shape([(111, 232), (115, 195, 135, 193, 157, 192), (208, 181, 254, 185, 284, 188),
               (356, 187), (420, 182, 463, 188, 486, 206), (500, 213), (500, 258),
               (110, 269)], "#3a4d50", "#586561")
    for x in (143, 192, 241, 290, 339, 388, 437, 485):
        art.line(((x-22,192), (x,218), (x+20,239)), "#222f36", 1.1)
        art.line(((x+21,190), (x,218), (x-21,240)), "#293a40", 1.2)
        art.line(((x-21,194), (x-4,215)), "#526463")
        art.ellipse((x-2.5,215.5,x+2.5,220.5), "#182931", "#67706a")
    art.shape([(102,254), (165,247), (465,247), (520,257), (531,280), (91,280)], "#32454a", "#62716b")


def sofa_front():
    art = Art()
    art.shape([(91, 291), (86, 267, 84, 244, 94, 230), (105, 214, 134, 218, 142, 235),
               (150, 247), (155, 275), (470, 277), (480, 249),
               (487, 225, 502, 222, 520, 227), (537, 229, 544, 245, 541, 270),
               (535, 306), (105, 309)], "#1b2a31", INK, 2.6)
    art.shape([(97, 238), (105, 226, 127, 227, 136, 237), (144, 251), (147, 275),
               (115, 278), (105, 266)], "#42575a", "#718079", 1)
    art.shape([(479, 272), (487, 237), (503, 230, 524, 233, 531, 244),
               (534, 263), (523, 279)], "#405357", "#657773", 1)
    art.shape([(114, 280), (172, 277), (478, 277), (521, 283), (519, 304),
               (117, 306)], "#304248", "#70817a")
    art.line(((121, 289), (234, 287), (413, 287), (514, 292)), "#536864")
    art.line(((122, 302), (516, 301)), "#101f28", 1.3)
    return art.finish()


def tony_cutout(reference):
    source = reference.convert("RGBA")
    # Hand-matted on frame 8803 of the Iron Man gallery at half resolution.
    contour = [
        (332, 322), (332, 292), (334, 266), (332, 236), (332, 209), (333, 178),
        (330, 156), (333, 134), (338, 123), (349, 119), (352, 111), (366, 108),
        (379, 109), (392, 113), (400, 120), (403, 132), (404, 141), (414, 140),
        (424, 145), (426, 154), (421, 166), (406, 174), (398, 188), (396, 208),
        (413, 212), (423, 208), (426, 204), (438, 199), (447, 195), (454, 183),
        (451, 171), (445, 158), (439, 142), (437, 125), (433, 111), (428, 100),
        (425, 86), (427, 72), (437, 62), (448, 56), (457, 48), (470, 39),
        (483, 36), (497, 37), (511, 41), (524, 48), (535, 58), (542, 72),
        (547, 88), (548, 107), (546, 124), (543, 142), (537, 152), (531, 156),
        (529, 173), (535, 183), (546, 190), (559, 196), (564, 190), (570, 186),
        (578, 188), (584, 183), (594, 182), (603, 184), (611, 181), (621, 185),
        (627, 194), (630, 207), (627, 223), (624, 233), (630, 246), (639, 264),
        (644, 282), (644, 296), (653, 312), (663, 328), (669, 346), (671, 360),
        (669, 373), (661, 383), (646, 389), (625, 389), (610, 391), (592, 395),
        (531, 398), (466, 398), (418, 396), (393, 388), (383, 382), (369, 382),
        (351, 380), (340, 373), (334, 359), (329, 345),
    ]
    alpha = Image.new("L", source.size)
    points = [(x * source.width / 960, y * source.height / 400) for x, y in contour]
    ImageDraw.Draw(alpha).polygon(points, fill=255)
    alpha = alpha.filter(ImageFilter.GaussianBlur(.55 * source.width / 960))
    source.putalpha(alpha)
    return source.crop(alpha.getbbox())


def build(reference, output):
    output.mkdir(parents=True, exist_ok=True)
    with Image.open(reference) as source:
        tony_cutout(source).save(output / "tony-gauntlet-cutout.png")
    garage().save(output / "workshop-backdrop.png")
    sofa_front().save(output / "workshop-foreground.png")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("tony_reference", type=Path, help="Frame 8803 from the Iron Man screencap gallery")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.tony_reference, args.output)
