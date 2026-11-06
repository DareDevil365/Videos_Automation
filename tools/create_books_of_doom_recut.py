"""Render the geometric Books of Doom pilot using local source photos and speech."""
from copy import deepcopy

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from create_comic_lore_recut import write_descriptions
from create_source_photo_revision import ROOT, load, script
from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset
from yt_pipeline.batches import run_batch
from yt_pipeline.contracts import brief_contract, script_contract
from yt_pipeline.core import Workspace, digest, now
from yt_pipeline.playbooks import validate_playbook_script


BUILD = "books-of-doom-forge-recut"
SOURCE = ROOT / "Resources/Drafts/comic-format-v2"
SIDESHOW = "https://www.sideshow.com/collectibles/marvel-dr-doom-sideshow-collectibles-300198"
SIDESHOW_PHOTO = "https://www.sideshow.com/storage/product-images/300198/dr-doom_marvel_gallery_5c4b98707fc88.jpg"
AUDIENCE = "https://www.pexels.com/photo/people-sitting-in-a-cinema-7991267/"


def register_doom(workspace):
    original = SOURCE / "sideshow-5c4b98707fc88.jpg"
    outline = [(45,400),(55,378),(74,350),(89,316),(118,285),(161,263),(189,257),
               (196,219),(188,207),(223,217),(293,217),(304,164),(318,138),
               (349,116),(337,89),(326,46),(326,28),(336,12),(353,4),(374,0),
               (429,0),(456,19),(463,40),(466,68),(448,87),(440,104),(460,99),
               (484,104),(515,122),(530,135),(544,161),(551,188),(551,213),
               (573,228),(585,254),(583,268),(568,281),(535,290),(517,324),
               (496,359),(479,400)]
    with Image.open(original) as image:
        portrait = ImageEnhance.Brightness(image.convert("RGB")).enhance(1.28).convert("RGBA")
        alpha = Image.new("L", portrait.size)
        ImageDraw.Draw(alpha).polygon([(round(x*portrait.width/600), round(y*portrait.height/400))
                                       for x, y in outline], fill=255)
        alpha = alpha.filter(ImageFilter.GaussianBlur(1.2))
        portrait.putalpha(alpha)
        prepared = SOURCE / "doom-sideshow-cutout.png"
        portrait.crop(alpha.getbbox()).save(prepared)
    return register_asset(workspace, prepared, "test",
                          {"url": SIDESHOW, "media_url": SIDESHOW_PHOTO,
                           "note": "Preview-only product photograph, manually masked and brightened."},
                          commercial=False, editing=False, test_only=True,
                          attribution="Doctor Doom figure photograph by Sideshow Collectibles. " + SIDESHOW)


def create_plan(workspace, target):
    recipe = load(ROOT / "examples/lore-series/books-of-doom/forge-recut.json")
    previous = load(ROOT / "Resources/Plans/books-of-doom-pilot.json")
    manifest = load(ROOT / "Resources/Productions/books-of-doom-pilot/batch.json")
    entry = deepcopy(previous["items"][0])
    request = entry["request"]
    brief = brief_contract(load(ROOT / "examples/lore-series/books-of-doom/forge-brief.json"))
    data = script(recipe["title"], recipe["rows"], recipe["description"], hosts=True, payoff=-2)
    validate_playbook_script(script_contract(data, brief, "lesson"), "comic_lore", request)
    doom = register_doom(workspace)
    audience = register_asset(workspace, SOURCE / "audience-7991267.png", "licensed_stock",
                              {"url": AUDIENCE, "license": "https://www.pexels.com/license/"},
                              attribution="Tima Miroshnichenko / Pexels. " + AUDIENCE)
    music = load(workspace.root / "curated-music-library.json")["tracks"]["mixkit-565"]
    request.pop("reaction_preset", None)
    request.update(
        brief=brief, script=data, test_only=True, auto_publish=False,
        hook_options=False, editorial_review="off", visual_review="off",
        prototype_revision_of=manifest["items"][0]["job_id"],
        lore_scenes={f"u{i}": row[2] for i, row in enumerate(recipe["rows"], 1)},
        lore_cameras={f"u{i}": camera for i, camera in enumerate(recipe["cameras"], 1)},
        source_panels={"u8": [{"asset_id": doom["id"], "box": [30, 210, 690, 870]}]},
        reaction_set={"setting": "cinema", "cast": [], "backdrop": audience["id"]},
        music_id=music["asset_id"], source_music={"start": 8.0, "volume": .095},
        source_delivery={"tight_speech": True, "speed": 1.10, "pause_after": .055,
                         "pauses_after": {"u5": .115, "u6": .095},
                         "linked_phrases": ["Doctor Doom", "Books of Doom", "Victor von Doom"]},
        source_review={"reviewer": "Codex, public sources", "supported": True,
                       "brief_digest": digest(brief), "script_digest": digest(data),
                       "limitations": "Public collection and origin descriptions. Forge staging is illustrative."},
    )
    entry["topic"] = data["title"]
    write_json(target, {**previous, "id": BUILD, "created_at": now(), "items": [entry],
                        "note": "Geometric forge action, short cuts, and a local preview-only sourced Doom reveal."})


def main():
    workspace = Workspace(ROOT / "data/pipeline")
    target = ROOT / "Resources/Plans" / (BUILD + ".json")
    if not target.exists():
        create_plan(workspace, target)
    result = run_batch(workspace, target, progress=lambda state: print(
        [(item["status"], item.get("error_code"), item.get("message")) for item in state["items"]],
        flush=True))
    if result["status"] != "ready":
        return 2
    write_descriptions(result, title="Books of Doom · The Burning Mask")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
