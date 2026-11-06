"""Prepare the reviewed workshop photo layers from the supplied reference crops."""
from argparse import ArgumentParser
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps


def mask(image, points, feather=1):
    alpha = Image.new("L", image.size)
    ImageDraw.Draw(alpha).polygon(points, fill=255)
    output = image.convert("RGBA")
    output.putalpha(alpha.filter(ImageFilter.GaussianBlur(feather)))
    return output.crop(output.getchannel("A").getbbox())


def garage(armor, ford, audi):
    width, height = 760, 320
    room = ImageOps.colorize(Image.linear_gradient("L").resize((width, height)), "#101922", "#28333b").convert("RGBA")
    draw = ImageDraw.Draw(room)
    draw.polygon(((0, 224), (760, 144), (760, 320), (0, 320)), fill="#303842")
    for x in (-150, 45, 276, 508, 755, 970):
        draw.line(((380, 181), (x, 320)), fill="#46515a", width=1)
    for y in (232, 260, 301):
        draw.line(((0, y), (760, y - 13)), fill="#414951", width=1)
    draw.polygon(((0, 4), (760, 4), (760, 22), (0, 38)), fill="#0b111a")
    draw.line(((0, 45), (760, 26)), fill="#627580", width=2)
    draw.line(((9, 40), (316, 33)), fill="#acc2ce", width=3)
    draw.line(((518, 31), (731, 26)), fill="#9aaab4", width=2)
    for x in (316, 472, 731):
        draw.line(((x, 32), (x, 208)), fill="#3c4b54", width=4)

    # Keep the actual photographed suits in the recessed display bays.
    left = ImageOps.fit(armor.crop((89, 51, 344, 316)), (250, 226))
    right = ImageOps.fit(armor.crop((478, 50, 737, 316)), (215, 198))
    room.paste(ImageEnhance.Brightness(left).enhance(.84), (15, 47))
    room.paste(ImageEnhance.Brightness(right).enhance(.72), (251, 42))
    draw.rectangle((13, 45, 265, 274), outline="#7d929f", width=2)
    draw.rectangle((249, 40, 467, 240), outline="#5d6e78", width=2)

    shadow = Image.new("RGBA", room.size)
    shadows = ImageDraw.Draw(shadow)
    shadows.ellipse((505, 157, 735, 186), fill=(4, 9, 15, 230))
    shadows.ellipse((484, 241, 752, 303), fill=(2, 6, 12, 220))
    room.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)))

    def park(car, size, xy, brightness):
        car = ImageOps.contain(car, size, Image.Resampling.LANCZOS)
        alpha = car.getchannel("A")
        car = ImageEnhance.Brightness(car.convert("RGB")).enhance(brightness).convert("RGBA")
        car.putalpha(alpha)
        reflection_height = 14
        reflection = ImageOps.flip(car).resize((car.width, reflection_height), Image.Resampling.BILINEAR)
        fade = Image.new("L", reflection.size)
        ramp = ImageDraw.Draw(fade)
        for y in range(reflection_height):
            ramp.line((0, y, car.width, y), fill=round(55 * (1 - y / reflection_height)))
        reflection.putalpha(ImageChops.multiply(reflection.getchannel("A"), fade))
        room.alpha_composite(reflection, (xy[0], xy[1] + car.height - 2))
        room.alpha_composite(car, xy)

    park(audi, (227, 116), (506, 84), .8)
    park(ford, (265, 153), (477, 143), .86)
    wash = Image.new("RGBA", room.size)
    ImageDraw.Draw(wash).ellipse((514, 45, 663, 208), fill=(120, 178, 207, 42))
    room.alpha_composite(wash.filter(ImageFilter.GaussianBlur(35)))
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
    seated.save(output / "tony-sofa-cutout.png")

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
