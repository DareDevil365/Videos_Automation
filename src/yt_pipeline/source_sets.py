"""Reusable lower sets and asset placements for source-based Shorts."""
import json
import math

from PIL import Image, ImageDraw, ImageOps

from .assets import asset_record
from .cinema_set import draw_theater, light_actor, light_audience
from .core import Held
from .lore_actions import draw_action


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


def check_lore_reuse(workspace, job):
    """Avoid immediate repeats of registered story photos, including re-cropped copies."""
    def identities(asset):
        evidence = asset.get("evidence", {})
        return {value for value in (asset.get("sha256"), evidence.get("derived_from"),
                                    evidence.get("media_url")) if isinstance(value, str) and value}

    def rows(request):
        panels = request.get("source_panels") or {}
        if not isinstance(panels, dict):
            return []
        result=[row for placements in panels.values() if isinstance(placements, list) for row in placements
                if isinstance(row, dict) and isinstance(row.get("asset_id"), str)]
        selection=request.get('visual_selection') or {}
        for layer in selection.get('layers',{}).values():
            if not isinstance(layer,dict):continue
            if isinstance(layer.get('setting'),str):
                result.append({'asset_id':layer['setting'],'repeat_reason':layer.get('setting_repeat_reason')})
            props=layer.get('props',{})
            if isinstance(props,dict):result.extend(p for p in props.values() if isinstance(p,dict) and isinstance(p.get('asset_id'),str))
        return result

    with workspace.connect() as db:
        previous = db.execute(
            "SELECT request FROM jobs WHERE id<>? AND channel=? "
            "AND status IN ('ready','processing','published','scheduled','uploaded_private') "
            "AND json_extract(request,'$.playbook')='comic_lore' "
            "ORDER BY created_at DESC LIMIT 3", (job["id"], job["channel"]),
        ).fetchall()
        recent = [row["asset_id"] for old in previous for row in rows(json.loads(old[0]))]
        seen = set(recent)
        for asset_id in set(recent):
            record = db.execute("SELECT data FROM assets WHERE id=?", (asset_id,)).fetchone()
            if record:
                seen.update(identities(json.loads(record[0])))
        for panel in rows(job["request"]):
            asset_id = panel["asset_id"]
            record = db.execute("SELECT data FROM assets WHERE id=?", (asset_id,)).fetchone()
            current = {asset_id}
            if record:
                current.update(identities(json.loads(record[0])))
            reason = panel.get("repeat_reason")
            if current.intersection(seen) and (not isinstance(reason, str) or not reason.strip()):
                raise Held("lore_repeat", "A recent story image repeats. Choose a different image or record why this callback needs the same one.")
            seen.update(current)


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
            if request.get("lore_fresh_visuals"):
                scale = (max if fit == "cover" else min)(size[0] / image.width, size[1] / image.height)
                if scale > 1.25:
                    raise Held("lore_image_quality", "The story image needs more native pixels or a smaller placement.")
            image = ImageOps.fit(image, size) if fit == "cover" else ImageOps.contain(image, size)
            motion = row.get("motion")
            if motion is not None:
                if (not isinstance(motion, dict) or motion.get("kind") not in ("drop", "arc", "crush", "knock")
                        or set(motion) - {"kind", "offset"}):
                    raise Held("source_panel", "Choose drop, arc, crush or knock for a moving cutout.")
                offset = motion.get("offset", [0, 0])
                if (not isinstance(offset, list) or len(offset) != 2
                        or any(type(n) is not int or abs(n) > 560 for n in offset)
                        or image.getchannel("A").getextrema() == (255, 255)):
                    raise Held("source_panel", "Moving props need a transparent cutout and bounded pixel offsets.")
                motion = (motion["kind"], offset)
            prepared.append((image, box, motion))
        placements[beat] = prepared

    set_data = None
    if reaction is not None:
        if not isinstance(reaction, dict) or not isinstance(reaction.get("setting"), str) or reaction["setting"] not in SETTINGS:
            raise Held("reaction_set", "Choose a registered set layout.")
        setting = reaction["setting"]
        backdrop_id = reaction.get("backdrop")
        cast = reaction.get("cast")
        if not isinstance(cast, list) or not (0 if setting == "cinema" and backdrop_id else 1) <= len(cast) <= 3:
            raise Held("reaction_set", "Supply one to three registered cast cutouts.")
        props = reaction.get("props", [])
        if not isinstance(props, list) or len(props) > 2:
            raise Held("reaction_set", "Use up to two registered background props.")
        if backdrop_id is not None and (setting not in ("workshop", "cinema")
                                        or (setting == "workshop" and (len(cast) != 1 or props))):
            raise Held("reaction_set", "Use a cinema or one-person workshop backdrop.")
        backdrop = ImageOps.fit(picture(backdrop_id).convert("RGB"), (760, 320)) if backdrop_id is not None else None
        foreground_id = reaction.get("foreground")
        if foreground_id is not None and (backdrop is None or setting != "workshop"):
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

        if setting == "cinema" and backdrop is not None:
            backdrop = light_audience(backdrop)
        size = (465, 204) if setting == "workshop" and backdrop is not None else (210, 212 if setting == "cinema" else 255)
        actors = [cutout(asset_id, size) for asset_id in cast]
        set_data = (
            setting,
            [light_actor(actor) for actor in actors] if setting == "cinema" else actors,
            [cutout(asset_id, (112, 186)) for asset_id in props],
            backdrop,
            foreground,
        )
    return placements, set_data, list(assets.values())


def draw_reaction_set(frame, setup, time):
    setting, cast, props, backdrop, foreground = setup
    if setting == "cinema":
        draw_theater(frame, cast, props, time, backdrop=backdrop)
        return
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
    if setting == "city":
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
        frame.paste(actor, (center - actor.width // 2, y), actor)
        if setting in ("workshop", "living_room"):
            x = center + 56
            cushion = "#274245" if setting == "workshop" else "#553541"
            draw.rounded_rectangle((center - 108, 1224, center + 108, 1289), 20, fill=cushion)
            draw.rounded_rectangle((x-13, 1208, x+12, 1250), 6, fill="#171c23", outline="#98b4b4")
            draw.ellipse((x-4, 1214, x+4, 1222), fill="#d5926b")


def move_cutout(source, motion, p):
    kind, (dx, dy) = motion
    after = max(0, min(1, (p-.46)*5))
    if kind == "crush":
        height = max(1, round(source.height*(1-.44*after)))
        return source.resize((source.width, height), Image.Resampling.BICUBIC), 0, source.height-height
    if kind == "drop":
        travel = 1-min(1, p/.46)**2
        return source, round(dx*travel), round(dy*travel+40*after)
    if kind == "arc":
        travel = max(0,min(1,(p-.17)/.65))
        return source.rotate(-48*travel, resample=Image.Resampling.BICUBIC), round(dx*travel), round(dy*travel-125*math.sin(travel*math.pi))
    return source.rotate(-45*after, resample=Image.Resampling.BICUBIC), round(dx*after), round(dy*after)


def source_painter(paint, placements, reaction, start, *, action=None):
    def frame(scene, second, duration):
        image = paint(scene, second, duration)
        for source, (left, top, right, bottom), motion in placements:
            x = left + (right-left-source.width)//2
            y = top + (bottom-top-source.height)//2
            if motion:
                source, dx, dy = move_cutout(source, motion, second/duration)
                x, y = x+dx, y+dy
            reveal = min(1, .6 + second * 2.5)
            alpha = source.getchannel("A").point(lambda n: round(n * reveal)) if reveal < 1 else source.getchannel("A")
            safe_top, safe_bottom = max(185, y), min(950, y+source.height)
            if safe_top < safe_bottom:
                crop = (0, safe_top-y, source.width, safe_bottom-y)
                image.paste(source.crop(crop), (x, safe_top), alpha.crop(crop))
        if action:
            draw_action(image, action, second, duration)
        if reaction:
            # Transform the complete story composition once, including photo props
            # and contact effects, so inserts cannot drift away from their actors.
            art=image.crop((0,180,720,952)).resize((720,710),Image.Resampling.LANCZOS)
            ImageDraw.Draw(image).rectangle((0,180,720,991),fill=image.getpixel((2,951)))
            image.paste(art,(0,180))
            if scene.get('design'):
                ImageDraw.Draw(image).rectangle((0,891,720,991),fill='#211b20')
            draw_reaction_set(image, reaction, start + second)
        return image
    return frame
