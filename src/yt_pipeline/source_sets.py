"""Reusable lower sets and asset placements for source-based Shorts."""
import json
import math

from PIL import Image, ImageDraw, ImageOps

from .assets import asset_record
from .core import Held


SETTINGS = {
    "cinema": "#151728",
    "workshop": "#172328",
    "city": "#192840",
    "living_room": "#31252f",
    "sanctum": "#251e35",
}


def apply_reaction_preset(workspace, request):
    name = request["reaction_preset"]
    if (request.get("playbook") not in ("comic_lore", "movie_brief")
            or not isinstance(name, str) or "reaction_set" in request):
        raise Held("reaction_set", "Choose one named preset or an explicit set for a comic or movie short.")
    path = workspace.root / "reaction-presets.json"
    presets = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    if name not in presets:
        raise Held("reaction_set", "This reaction preset is not installed in this workspace.")
    request["reaction_set"] = presets[name]


def resolve_source_set(workspace, request, script):
    panels = request.get("source_panels", {})
    reaction = request.get("reaction_set")
    if not isinstance(panels, dict) or set(panels) - {u["id"] for u in script["units"]}:
        raise Held("source_panel", "Place source images on existing beats.")
    assets = {}

    pictures = {}

    def picture(asset_id):
        if not isinstance(asset_id, str):
            raise Held("source_panel", "Use a registered image ID.")
        if asset_id not in assets:
            asset = asset_record(workspace, asset_id, allow_preview=request.get("test_only") is True)
            if asset["kind"] != "image" or (asset["test_only"] and request.get("test_only") is not True):
                raise Held("source_panel", "Use an eligible registered image for this export.")
            assets[asset_id] = asset
            with Image.open(asset["path"]) as source:
                image = ImageOps.exif_transpose(source).convert("RGBA")
                image.thumbnail((1440, 1440), Image.Resampling.LANCZOS)
                pictures[asset_id] = image
        return pictures[asset_id]

    placements = {}
    for beat, rows in panels.items():
        if not isinstance(rows, list) or len(rows) > 4:
            raise Held("source_panel", "Use up to four images in one beat.")
        prepared = []
        for row in rows:
            if not isinstance(row, dict):
                raise Held("source_panel", "Each placement needs an image and a box.")
            box = row.get("box")
            fit = row.get("fit", "contain")
            bottom = 890 if reaction else 950
            if (not isinstance(box, list) or len(box) != 4 or any(type(n) is not int for n in box)
                    or not (0 <= box[0] < box[2] <= 720 and 185 <= box[1] < box[3] <= bottom)
                    or fit not in ("contain", "cover")):
                raise Held("source_panel", "Keep source images in the main story area.")
            size = (box[2] - box[0], box[3] - box[1])
            image = picture(row.get("asset_id"))
            image = ImageOps.fit(image, size) if fit == "cover" else ImageOps.contain(image, size)
            prepared.append((image, box))
        placements[beat] = prepared

    set_data = None
    if reaction is not None:
        if not isinstance(reaction, dict) or not isinstance(reaction.get("setting"), str) or reaction["setting"] not in SETTINGS:
            raise Held("reaction_set", "Choose a registered set layout.")
        cast = reaction.get("cast")
        if not isinstance(cast, list) or not 1 <= len(cast) <= 3:
            raise Held("reaction_set", "Supply one to three registered cast cutouts.")
        props = reaction.get("props", [])
        if not isinstance(props, list) or len(props) > 2:
            raise Held("reaction_set", "Use up to two registered background props.")
        backdrop_id = reaction.get("backdrop")
        if backdrop_id is not None and (reaction["setting"] != "workshop" or len(cast) != 1 or props):
            raise Held("reaction_set", "Use a workshop backdrop with one seated cast cutout.")
        backdrop = ImageOps.fit(picture(backdrop_id).convert("RGB"), (760, 320)) if backdrop_id is not None else None
        foreground_id = reaction.get("foreground")
        if foreground_id is not None and backdrop is None:
            raise Held("reaction_set", "Use a foreground layer with a workshop backdrop.")
        foreground = None
        if foreground_id is not None:
            overlay = picture(foreground_id)
            minimum, maximum = overlay.getchannel("A").getextrema()
            if minimum != 0 or maximum == 0:
                raise Held("reaction_set", "The foreground must have painted and transparent areas.")
            foreground = ImageOps.fit(overlay, (760, 320))

        def cutout(asset_id, size):
            image = picture(asset_id)
            alpha = image.getchannel("A")
            if alpha.getextrema() != (0, 255):
                raise Held("reaction_set", "Cast and props require transparent cutout images.")
            return ImageOps.contain(image.crop(alpha.getbbox()), size)

        set_data = (
            reaction["setting"],
            [cutout(asset_id, (465, 204) if backdrop is not None else (210, 255)) for asset_id in cast],
            [cutout(asset_id, (112, 186)) for asset_id in props],
            backdrop,
            foreground,
        )
    return placements, set_data, list(assets.values())


def draw_reaction_set(frame, setup, time):
    setting, cast, props, backdrop, foreground = setup
    if backdrop is not None:
        # Small independent movement on the room and sofa gives the plate depth.
        x = 20 + round(9 * math.sin(time * .85))
        crop = (x, 12, x + 720, 300)
        frame.paste(backdrop.crop(crop), (0, 992))
        actor = cast[0]
        actor_x = 330 - actor.width // 2 + round(2 * math.sin(time * 1.6))
        frame.paste(actor, (actor_x, 1280 - actor.height), actor)
        if foreground is not None:
            overlay = foreground.crop(crop)
            frame.paste(overlay, (0, 992), overlay)
        return
    draw = ImageDraw.Draw(frame)
    draw.rectangle((0, 992, 720, 1280), fill=SETTINGS[setting])
    draw.line((30, 1000, 690, 1000), fill="#936b5e", width=3)
    centers = [round(720 * (index + .5) / len(cast)) for index in range(len(cast))]
    if setting == "cinema":
        for x in range(-40, 760, 97):
            draw.rounded_rectangle((x, 1044, x + 85, 1175), 21, fill="#302333", outline="#493249", width=3)
    elif setting == "city":
        for index, x in enumerate(range(0, 720, 76)):
            top = 1060 + (index * 37) % 85
            draw.rectangle((x, top, x + 69, 1280), fill="#101b2c", outline="#33475e", width=2)
            for row in range(top + 15, 1260, 29):
                draw.rectangle((x + 15, row, x + 24, row + 11), fill="#a28863")
                draw.rectangle((x + 42, row, x + 51, row + 11), fill="#6a725e")
    elif setting == "sanctum":
        for radius in (57, 78):
            draw.ellipse((360-radius, 1100-radius, 360+radius, 1100+radius), outline="#9c70b2", width=3)
        for x in (63, 657):
            draw.line((x, 1025, x, 1260), fill="#635175", width=9)
        draw.line((0, 1232, 720, 1232), fill="#635175", width=3)
    elif setting == "workshop":
        draw.line((38, 1044, 682, 1044), fill="#608483", width=4)
        draw.rounded_rectangle((132, 1117, 588, 1264), 29, fill="#304e51", outline="#50716f", width=4)
    else:
        draw.rounded_rectangle((121, 1110, 599, 1264), 29, fill="#694956", outline="#956c77", width=4)
        draw.ellipse((72, 1100, 119, 1147), outline="#7fa4a1", width=4)
        draw.line((96, 1124, 96, 1245), fill="#7fa4a1", width=5)
        draw.rectangle((476, 1030, 552, 1094), outline="#957477", width=4)

    for center, prop in zip((87, 633), props):
        frame.paste(prop, (center - prop.width // 2, 1217 - prop.height), prop)

    for index, (center, actor) in enumerate(zip(centers, cast)):
        y = 1035 + round(3 * math.sin(time * 2.4 + index))
        if setting == "city":
            swing = math.sin(time * 1.8 + index)
            x = center + round(45 * swing)
            actor = actor.rotate(-12 * swing, resample=Image.Resampling.BICUBIC, expand=True)
            draw.line((center + 18, 1001, x, y + 83), fill="#ccdce6", width=2)
            frame.paste(actor, (x - actor.width // 2, y + round(17 * abs(swing))), actor)
            continue
        if setting == "cinema":
            draw.rounded_rectangle((center - 106, 1100, center + 106, 1268), 26,
                                   fill="#572d40", outline="#814e5f", width=4)
        frame.paste(actor, (center - actor.width // 2, y), actor)
        if setting == "cinema":
            draw.rounded_rectangle((center - 108, 1224, center + 108, 1289), 20, fill="#482333")
            x = center + 36
            draw.polygon([(x-27, 1194), (x+26, 1194), (x+17, 1251), (x-18, 1251)], fill="#e2ad79")
            for stripe in (-13, 1, 15):
                draw.line((x+stripe, 1198, x+stripe*.6, 1249), fill="#9e4946", width=5)
            for k in range(5):
                px = x - 19 + 9*k
                draw.ellipse((px, 1186 - k % 2 * 3, px + 12, 1199), fill="#ffe4aa")
            progress = (time / 3.1 + index * .25) % 1
            if progress < .58:
                move = progress / .58
                px = x + (center - x)*move
                py = 1190 - 57*move - 26*math.sin(math.pi*move)
                draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill="#ffeac0")
        elif setting in ("workshop", "living_room"):
            x = center + 56
            cushion = "#274245" if setting == "workshop" else "#553541"
            draw.rounded_rectangle((center - 108, 1224, center + 108, 1289), 20, fill=cushion)
            draw.rounded_rectangle((x-13, 1208, x+12, 1250), 6, fill="#171c23", outline="#98b4b4")
            draw.ellipse((x-4, 1214, x+4, 1222), fill="#d5926b")


def source_painter(paint, placements, reaction, start):
    def frame(scene, second, duration):
        image = paint(scene, second, duration)
        if reaction:
            art = image.crop((0, 180, 720, 952)).resize((720, 710), Image.Resampling.LANCZOS)
            ImageDraw.Draw(image).rectangle((0, 180, 720, 991), fill="#0c121c")
            image.paste(art, (0, 180))
        for source, (left, top, right, bottom) in placements:
            reveal = min(1, .6 + second * 2.5)
            alpha = source.getchannel("A").point(lambda n: round(n * reveal)) if reveal < 1 else source.getchannel("A")
            image.paste(source, (left + (right-left-source.width)//2,
                                 top + (bottom-top-source.height)//2), alpha)
        if reaction:
            draw_reaction_set(image, reaction, start + second)
        return image
    return frame
