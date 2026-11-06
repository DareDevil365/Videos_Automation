"""Turn the reviewed workshop reference crops into inked comic panel layers."""
from argparse import ArgumentParser
from pathlib import Path

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFilter, ImageOps


INK = "#0a121a"
COOL = ("#101b24", "#1a3039", "#28515a", "#477478", "#83a29a", "#dbd6b0")
WARM = ("#181720", "#3f252a", "#6f3d3c", "#a55f48", "#cb9161", "#f3d498")
STEEL = ("#111c25", "#233541", "#395363", "#5d7781", "#96b0ad", "#e0e2c3")


def mask(image, points, feather=1):
    alpha = Image.new("L", image.size)
    ImageDraw.Draw(alpha).polygon(points, fill=255)
    output = image.convert("RGBA")
    output.putalpha(alpha.filter(ImageFilter.GaussianBlur(feather)))
    return output.crop(output.getchannel("A").getbbox())


def ink_component(component, palette=COOL, *, warmth=True):
    """Trace broad tonal shapes and retain the edges that define the subject."""
    rgb = component.convert("RGB").filter(ImageFilter.MedianFilter(3))
    values = rgb.convert("L")
    # Band the smoothed values, then use the detailed pass only for linework.
    bands = values.filter(ImageFilter.GaussianBlur(1.35)).point(
        [sum(level <= value for level in (32, 61, 95, 137, 191)) for value in range(256)]
    )
    colors = [channel for color in palette for channel in ImageColor.getrgb(color)]
    bands = bands.convert("P")
    bands.putpalette(colors)
    paint = bands.convert("RGB")
    if warmth:
        bands.putpalette([channel for color in WARM for channel in ImageColor.getrgb(color)])
        red, green, _ = rgb.split()
        color_mask = ImageChops.subtract(red, green).point(
            [min(255, max(0, (value - 9) * 14)) for value in range(256)]
        ).filter(ImageFilter.GaussianBlur(.8))
        paint = Image.composite(bands.convert("RGB"), paint, color_mask)
    edges = values.filter(ImageFilter.GaussianBlur(.55)).filter(ImageFilter.FIND_EDGES).point(
        [min(150, max(0, (value - 39) * 3)) for value in range(256)]
    )
    alpha = component.getchannel("A")
    # Fine lines reinforce actual contours and leave the color shapes legible.
    inside = alpha.filter(ImageFilter.MinFilter(3))
    rim = ImageChops.subtract(alpha, inside).point(lambda value: value * 0.68)
    paint = Image.composite(Image.new("RGB", paint.size, INK), paint, ImageChops.lighter(edges, rim))
    paint.putalpha(alpha)
    return paint


def garage(armor, ford, audi):
    room = Image.new("RGBA", (760, 320), "#121f2a")
    draw = ImageDraw.Draw(room)
    draw.polygon(((0, 72), (464, 49), (760, 78), (760, 241), (0, 252)), fill="#192f36")
    draw.polygon(((0, 226), (462, 193), (760, 213), (760, 320), (0, 320)), fill="#243c42")
    draw.polygon(((457, 54), (760, 83), (760, 213), (457, 193)), fill="#172b33", outline="#395957", width=2)
    draw.polygon(((0, 22), (468, 17), (760, 50), (760, 81), (465, 52), (0, 73)), fill="#0c1822")
    draw.line(((0, 71), (464, 49), (760, 78)), fill="#8c8969", width=2)
    draw.line(((476, 65), (718, 88)), fill="#c0b589", width=2)
    draw.line(((459, 52), (459, 199)), fill="#91a699", width=3)
    draw.line(((464, 52), (464, 196)), fill="#0c181e", width=4)
    for x in (33, 252, 524, 761, 1040):
        draw.line(((462, 192), (x, 320)), fill="#47625f", width=1)
    for offset in (7, 28, 59, 101):
        draw.line(((0, 224 + offset), (462, 193 + offset), (760, 213 + offset)), fill="#425c59", width=1)
    for y in range(83, 310, 5):
        for x in range(6 + y % 3, 760, 7):
            if (x < 430 and y > 229) or (x > 472 and y < 107):
                draw.point((x, y), fill="#4a615d")
    # The rear parking deck and its lip make the Audi's wheel contact visible.
    draw.polygon(((467, 159), (664, 146), (760, 155), (760, 185), (516, 209), (467, 191)),
                 fill="#395957", outline="#668679", width=2)
    draw.polygon(((467, 191), (516, 209), (760, 185), (760, 195), (516, 222), (467, 201)),
                 fill="#1e3338", outline="#45635f", width=2)
    draw.line(((525, 210), (741, 187)), fill="#998e69", width=2)

    # Silhouettes from left to right in the original armor reference.
    contours = (
        [
            (188, 119), (193, 103), (200, 97), (214, 97), (218, 102), (218, 118),
            (228, 126), (232, 146), (233, 180), (230, 202), (226, 210), (223, 201),
            (221, 179), (222, 162), (216, 185), (217, 214), (218, 244), (233, 279),
            (224, 284), (209, 281), (200, 250), (196, 218), (192, 239), (190, 268),
            (198, 285), (184, 287), (174, 281), (174, 246), (174, 220), (177, 190),
            (178, 164), (175, 179), (173, 201), (167, 211), (164, 201), (165, 172),
            (165, 150), (172, 132),
        ],
        [
            (295, 111), (298, 99), (307, 93), (317, 95), (322, 104), (321, 119),
            (335, 129), (341, 151), (342, 172), (337, 189), (333, 192), (329, 185),
            (330, 164), (327, 153), (322, 177), (322, 200), (326, 222), (326, 248),
            (321, 271), (330, 276), (326, 284), (313, 284), (308, 277), (308, 254),
            (306, 226), (301, 211), (300, 246), (298, 276), (284, 283), (277, 279),
            (285, 268), (283, 246), (282, 223), (285, 200), (289, 177), (286, 155),
            (283, 173), (284, 186), (277, 194), (274, 183), (275, 160), (278, 136),
            (286, 126),
        ],
        [
            (506, 114), (507, 105), (515, 98), (524, 98), (531, 105), (531, 120),
            (541, 128), (548, 145), (549, 160), (553, 177), (548, 189), (541, 188),
            (538, 171), (534, 150), (529, 177), (530, 198), (535, 222), (538, 246),
            (535, 271), (548, 282), (541, 289), (527, 283), (522, 272), (521, 251),
            (515, 227), (511, 212), (506, 232), (505, 259), (505, 276), (498, 285),
            (486, 284), (485, 277), (492, 268), (489, 243), (489, 225), (493, 202),
            (497, 179), (497, 152), (492, 169), (487, 188), (480, 194), (475, 188),
            (480, 174), (482, 148), (490, 132),
        ],
        [
            (603, 102), (606, 93), (616, 89), (626, 93), (630, 102), (628, 119),
            (640, 125), (647, 143), (647, 167), (651, 188), (648, 195), (640, 191),
            (638, 169), (634, 151), (629, 182), (630, 204), (637, 226), (637, 248),
            (633, 271), (645, 283), (639, 290), (624, 285), (618, 274), (618, 246),
            (612, 219), (609, 205), (604, 226), (603, 248), (604, 275), (595, 289),
            (583, 286), (585, 279), (591, 270), (586, 248), (587, 224), (592, 205),
            (596, 182), (595, 158), (589, 176), (589, 189), (582, 195), (576, 190),
            (582, 170), (583, 146), (591, 129), (605, 119),
        ],
    )
    for index, contour in enumerate(contours):
        x = 30 + index * 102
        draw.polygon(((x, 77), (x+16, 65), (x+83, 65), (x+92, 77), (x+92, 226), (x, 233)),
                     fill="#17252b", outline="#53716b", width=2)
        draw.polygon(((x+18, 72), (x+76, 72), (x+81, 84), (x+81, 211), (x+12, 220), (x+12, 83)),
                     fill="#2c4b4a")
        draw.line((x+10, 89, x+10, 211), fill="#a2b9a1", width=2)
        draw.line((x+80, 87, x+80, 207), fill="#789b89", width=2)
        draw.line((x+16, 81, x+75, 81), fill="#ccbd8e", width=3)
        draw.polygon(((x+10, 217), (x+78, 212), (x+86, 224), (x+10, 230)), fill="#385955")
        suit = ink_component(mask(armor, contour), STEEL)
        suit = ImageOps.contain(suit, (75, 132), Image.Resampling.LANCZOS)
        room.alpha_composite(suit, (x + (90 - suit.width)//2, 219 - suit.height))

    def park(car, size, xy, palette, warmth):
        car = ImageOps.contain(ink_component(car, palette, warmth=warmth), size, Image.Resampling.LANCZOS)
        x, y = xy
        floor = y + car.height
        draw.ellipse((x+10, floor-15, x+car.width+5, floor+7), fill="#14292d")
        draw.line((x+36, floor+7, x+car.width-24, floor+7), fill="#60776b", width=1)
        room.alpha_composite(car, xy)

    park(audi, (185, 84), (550, 106), STEEL, False)
    park(ford, (196, 115), (542, 185), COOL, True)
    draw.line(((27, 27), (730, 28)), fill="#8b8d72", width=1)
    draw.line(((27, 292), (730, 304)), fill="#8b8d72", width=1)
    return room.convert("RGB")


def build(armor_path, sofa_path, ford_path, audi_path, output):
    output.mkdir(parents=True, exist_ok=True)
    with Image.open(armor_path) as source:
        armor = source.convert("RGB").resize((823, 401))
    with Image.open(sofa_path) as source:
        sofa = source.convert("RGB").resize((562, 221))
    seated = mask(sofa, [(59, 106), (193, 103), (201, 83), (221, 78), (231, 86), (234, 67), (243, 53),
                         (255, 45), (271, 45), (284, 51), (292, 63), (293, 90), (300, 103), (460, 102),
                         (460, 197), (59, 197)], feather=1.25)
    ink_component(seated).save(output / "tony-sofa-cutout.png")

    with Image.open(ford_path) as source:
        ford = ImageOps.exif_transpose(source).resize((758, 540))
    ford = mask(ford, [(15, 197), (20, 170), (40, 149), (57, 143), (58, 120), (70, 98), (115, 88), (159, 78),
                       (220, 74), (239, 70), (235, 63), (249, 62), (265, 111), (365, 101), (418, 93), (447, 95),
                       (438, 53), (452, 48), (460, 100), (474, 111), (484, 126), (489, 138), (488, 171),
                       (526, 177), (554, 165), (586, 164), (614, 180), (635, 207), (685, 209), (714, 221),
                       (738, 245), (749, 275), (746, 306), (730, 335), (697, 360), (683, 384), (637, 426),
                       (610, 458), (583, 458), (538, 427), (517, 429), (508, 464), (491, 494), (466, 511),
                       (429, 513), (398, 499), (374, 475), (351, 437), (340, 400), (338, 365), (344, 338),
                       (363, 319), (310, 310), (285, 307), (265, 321), (240, 308), (229, 286), (149, 264),
                       (100, 250), (88, 275), (67, 288), (44, 275), (27, 248), (17, 224)])
    with Image.open(audi_path) as source:
        audi = ImageOps.exif_transpose(source).resize((720, 540))
    audi = mask(audi, [(49, 285), (64, 261), (104, 248), (200, 228), (280, 161), (318, 147), (382, 130),
                       (446, 128), (500, 138), (550, 156), (601, 178), (637, 190), (666, 211), (674, 235),
                       (676, 269), (670, 296), (658, 310), (641, 321), (614, 324), (585, 320), (395, 355),
                       (378, 375), (350, 384), (323, 378), (304, 365), (240, 367), (158, 356), (81, 350),
                       (50, 336), (49, 315)])
    garage(armor, ford, audi).save(output / "workshop-backdrop.jpg", quality=94)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    for name in ("armor_reference", "sofa_reference", "roadster_photo", "audi_photo", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    build(args.armor_reference, args.sofa_reference, args.roadster_photo, args.audi_photo, args.output)
