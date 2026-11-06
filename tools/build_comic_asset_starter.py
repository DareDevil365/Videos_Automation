"""Build reusable transparent comic assets and optionally register local IDs."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
import re
import sys

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shorts_editor.store import write_json
from yt_pipeline.assets import asset_record, register_asset
from yt_pipeline.core import Held, Workspace, file_hash
from yt_pipeline.lore_actions import draw_hammer
from yt_pipeline.lore_forge import mask
from yt_pipeline.lore_reactor import _reactor
from yt_pipeline.lore_reactor_cast import HAPPY, PEPPER, STANE, TONY, person, workshop_tony


PACK = ROOT / "Resources/Templates/ComicLore"


def export_images():
    catalog = json.loads((PACK / "catalog.json").read_text(encoding="utf-8"))
    for item in catalog["assets"]:
        path = PACK / item["file"]
        path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGBA", (640,640))
        draw = ImageDraw.Draw(image)
        recipe = item["recipe"]
        if recipe == "person":
            who = {TONY: TONY, PEPPER: PEPPER, STANE: STANE, HAPPY: HAPPY}[item["profile"]]
            person(draw, who, 319, 149, 2, jacket=item.get("jacket"))
        elif recipe == "workshop":
            image = workshop_tony()
        elif recipe == "mask":
            mask(draw, 320, 320, 3.3, item.get("heat", 0))
        elif recipe == "mark_i":
            draw.polygon([(167,176),(445,176),(480,260),(474,423),(413,484),(226,484),(160,411)],
                         fill="#617277", outline="#d5d8c9", width=9)
            draw.polygon([(167,176),(228,217),(221,435),(226,484),(160,411),(160,252)],
                         fill="#364750", outline="#a7b3ae", width=5)
            draw.polygon([(228,217),(413,217),(445,176),(480,260),(450,320),(221,320)],
                         fill="#788583", outline="#c3c5b7", width=5)
            draw.polygon([(239,279),(429,279),(415,315),(246,315)],fill="#111c24",outline="#c8cdbd",width=5)
            draw.rectangle((275,369,388,402), fill="#273b42", outline="#a7b2aa", width=4)
            for x in (210,444):
                draw.ellipse((x-9,354,x+9,372), fill="#dbd0b0", outline="#3b4c4e", width=3)
        elif recipe == "hammer":
            draw_hammer(draw,320,415,6)
        elif recipe == "reactor":
            _reactor(image,None,320,320,183,0,0)
        else:
            raise ValueError(f"Unknown starter asset recipe: {recipe}")
        image.crop(image.getbbox()).save(path)
    return catalog


def install_assets(workspace, catalog):
    ids = {}
    with workspace.connect() as db:
        rows = db.execute("SELECT data FROM assets WHERE json_extract(data, '$.evidence.comic_pack')=1").fetchall()
    prior = {record["sha256"]: record["id"] for record in map(lambda row: json.loads(row["data"]), rows)}
    for item in catalog["assets"]:
        path = PACK / item["file"]
        key = file_hash(path)
        asset_id = prior.get(key)
        if asset_id:
            try:
                asset_record(workspace, asset_id, allow_preview=True)
            except (Held, OSError):
                asset_id = None
        if not asset_id:
            record = register_asset(workspace,path,"original_graphic",
                                    {"comic_pack":1,"name":item["id"],"recipe":item["recipe"]},
                                    attribution="Original geometric comic artwork.",test_only=True)
            asset_id = record["id"]
        ids[item["id"]] = asset_id
    write_json(workspace.root / "comic-starter-asset-ids.json", ids)
    return ids


def prepare_portrait(workspace, asset_id, name, box):
    """Create one reusable circular identifier from an explicitly selected crop."""
    if (not re.fullmatch(r"[a-z0-9_-]{1,48}", name) or not box
            or not (0 <= box[0] < box[2] <= 1 and 0 <= box[1] < box[3] <= 1)):
        raise ValueError("Choose a safe portrait name and normalized left, top, right and bottom coordinates.")
    source = asset_record(workspace, asset_id, allow_preview=True)
    if source["kind"] != "image":
        raise ValueError("A portrait identifier needs a registered still image.")
    with Image.open(source["path"]) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        pixels = tuple(round(value*image.size[index%2]) for index,value in enumerate(box))
        if min(pixels[2]-pixels[0], pixels[3]-pixels[1]) < 144:
            raise ValueError("Choose a clearer source or a crop at least 144 pixels wide and tall.")
        side = min(384,pixels[2]-pixels[0],pixels[3]-pixels[1])
        badge = ImageOps.fit(image.crop(pixels),(side,side),Image.Resampling.LANCZOS).convert("RGBA")
    alpha = Image.new("L", (side,side))
    ImageDraw.Draw(alpha).ellipse((0,0,side-1,side-1),fill=255)
    badge.putalpha(alpha)
    folder = workspace.root/"assets"/"comic-portraits"
    folder.mkdir(parents=True,exist_ok=True)
    pixels_hash = sha256(badge.tobytes()).hexdigest()[:12]
    path = folder/(name+"-"+source["sha256"][:12]+"-"+pixels_hash+".png")
    badge.save(path)
    evidence = {"source_asset_id":source["id"],"derived_from":source["sha256"],"crop":box}
    return register_asset(workspace,path,source["source_type"],evidence,commercial=source["commercial"],
                          editing=source["editing"],expires_at=source.get("expires_at"),
                          attribution=source.get("attribution",""),test_only=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--register", action="store_true")
    parser.add_argument("--workspace", type=Path, default=ROOT/"data/pipeline")
    parser.add_argument("--portrait-asset", help="Existing image asset ID for a local circular face identifier.")
    parser.add_argument("--portrait-name")
    parser.add_argument("--portrait-box", type=float, nargs=4, metavar=("LEFT","TOP","RIGHT","BOTTOM"))
    args = parser.parse_args()
    if args.portrait_asset:
        result = prepare_portrait(Workspace(args.workspace),args.portrait_asset,args.portrait_name or "",args.portrait_box)
        print(json.dumps({"asset_id":result["id"],"test_only":True}))
        return
    catalog = export_images()
    result = install_assets(Workspace(args.workspace), catalog) if args.register else {"exported":len(catalog["assets"])}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
