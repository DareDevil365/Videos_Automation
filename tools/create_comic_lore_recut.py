"""Build the revised Secret Wars trilogy from registered local photo inputs."""
from argparse import ArgumentParser
from copy import deepcopy
from pathlib import Path

from PIL import Image

from create_source_photo_revision import ROOT, load, script
from create_marvel_set_library import MILES_MATTE, clean_miles_portrait
from shorts_editor.store import write_json
from yt_pipeline.assets import asset_record, register_asset
from yt_pipeline.batches import run_batch
from yt_pipeline.contracts import script_contract
from yt_pipeline.core import Held, Workspace, digest, now
from yt_pipeline.playbooks import validate_playbook_script


RECIPES = ROOT / "examples/lore-series/secret-wars-2015"
SOUND_CUES = {"part-1": {"u4": "impact"}, "part-2": {"u4": "reveal"}}
OUTPUT = ROOT / "Resources/Productions"


def create_plan(workspace, previous, target):
    old = load(previous)
    titles = load(RECIPES / "recut-scripts.json")["parts"]
    music = load(RECIPES / "recut-music.json")["parts"]
    installed = load(workspace.root / "curated-music-library.json")["tracks"]
    manifest = load(OUTPUT / old["id"] / "batch.json")
    ancestors = {entry["id"]: entry["job_id"] for entry in manifest["items"] if entry["status"] == "ready"}
    older = {entry["id"]: entry for entry in old["items"]}
    # Frame the real costume portrait above the source-photo floor.
    portrait_id = older["part-1"]["request"]["source_panels"]["u5"][0]["asset_id"]
    portrait = asset_record(workspace, portrait_id, allow_preview=True)
    prepared = ROOT / "Resources/Drafts/comic-recut"
    prepared.mkdir(parents=True, exist_ok=True)
    portrait_path = prepared / "doom-upper.png"
    framed = portrait
    if portrait["evidence"].get("crop") != [0, 0, 1, .64]:
        with Image.open(portrait["path"]) as original:
            original.crop((0, 0, original.width, round(original.height * .64))).save(portrait_path)
        framed = register_asset(
            workspace, portrait_path, portrait["source_type"],
            {**portrait["evidence"], "derived_from": portrait["sha256"], "crop": [0, 0, 1, .64]},
            commercial=portrait["commercial"], editing=portrait["editing"],
            attribution=portrait["attribution"] + " Framed above the costume's knees.", test_only=True,
        )
    reaction = deepcopy(load(workspace.root / "reaction-presets.json")["crossover-theater"])
    miles = asset_record(workspace, reaction["cast"][1], allow_preview=True)
    miles_path = prepared / "miles-bust-clean.png"
    with Image.open(miles["path"]) as original:
        clean_miles_portrait(original).save(miles_path)
    clean_miles = register_asset(
        workspace, miles_path, miles["source_type"],
        {**miles["evidence"], "derived_from": miles["sha256"], "matte_reference_size": [141,196], "matte": MILES_MATTE},
        commercial=miles["commercial"], editing=miles["editing"],
        attribution=miles["attribution"] + " Remasked around the head and torso.", test_only=True,
    )
    reaction["cast"][1] = clean_miles["id"]
    miles_panels = {
        older["part-2"]["request"]["source_panels"]["u2"][0]["asset_id"],
        older["part-3"]["request"]["source_panels"]["u7"][0]["asset_id"],
    }
    items = []
    for chapter in titles:
        number = chapter["part"]
        part = f"part-{number}"
        entry = deepcopy(older[part])
        request = entry["request"]
        brief = request["brief"]
        data = script(chapter["title"], chapter["rows"], request["script"]["description"], hosts=True, payoff=-2)
        request["series"]["structure"] = "serial_cliffhanger"
        validate_playbook_script(script_contract(data, brief, "lesson"), "comic_lore", request)
        request.pop("reaction_set", None)
        request.pop("reaction_preset", None)
        for panels in request.get("source_panels", {}).values():
            for panel in panels:
                if panel["asset_id"] == portrait_id:
                    panel["asset_id"] = framed["id"]
                elif panel["asset_id"] in miles_panels:
                    panel["asset_id"] = clean_miles["id"]
        track = music[part]
        request.update(
            script=data, reaction_set=reaction,
            creative_brief="Tell one continuing story. End earlier parts on a specific cliffhanger and resolve the arc only in the final part.",
            prototype_revision_of=ancestors[part], auto_publish=False, test_only=True,
            lore_scenes={f"u{i}": row[2] for i, row in enumerate(chapter["rows"], 1)},
            music_id=installed[track["track"]]["asset_id"],
            source_music={"start": track["start_seconds"], "volume": track["gain"]},
            source_cues=SOUND_CUES.get(part, {}),
            source_delivery={
                "tight_speech": True, "speed": 1.08, "pause_after": .055,
                "pauses_after": {"u6": .09, "u7": .16},
                "linked_phrases": ["Miles Morales", "Reed Richards", "Molecule Man", "Doctor Doom"],
            },
            source_review={
                "reviewer": "Codex and comic writing reviewer", "supported": True,
                "brief_digest": digest(brief), "script_digest": digest(data),
                "limitations": "Publisher recaps and reading order; full issues were unavailable.",
            },
        )
        entry["topic"] = data["title"]
        items.append(entry)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_json(target, {**old, "id": target.stem, "created_at": now(),
                        "note": "Serialized cliffhangers, tight speech, host CTAs with actual local next-part links, and distinct chapter music.",
                        "items": items})


def write_descriptions(result, *, title="Doom's Broken Worlds"):
    root = OUTPUT / result["id"]
    entries = []
    items = result["items"]
    for index, item in enumerate(items):
        folder = Path(item["output_folder"])
        data = load(folder / "metadata.json")
        description = f"# {data['title']}\n\n{data['description']}\n\n[Watch this part](video.mp4)\n"
        if index+1 < len(items):
            next_id = items[index+1]["id"]
            description += f"\n[Watch part {index+2}](../{next_id}/video.mp4)\n"
        (folder / "description.md").write_text(description, encoding="utf-8")
        entries.append(f"- [Part {index+1} · {data['title']}]({item['id']}/video.mp4) · {item['duration']:.1f}s")
    (root / "README.md").write_text(
        f"# {title}\n\nLocal review cuts with linked episode descriptions.\n\n"
        + "\n".join(entries) + "\n", encoding="utf-8"
    )


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, default=ROOT / "Resources/Plans/doom-broken-worlds-photo-20261106.json")
    parser.add_argument("--plan", type=Path, default=ROOT / "Resources/Plans/doom-broken-worlds-serial-20261106.json")
    args = parser.parse_args()
    workspace = Workspace(ROOT / "data/pipeline")
    if not args.plan.exists():
        create_plan(workspace, args.previous, args.plan)

    def usage():
        with workspace.connect() as db:
            return dict(db.execute("SELECT provider,SUM(calls) FROM usage GROUP BY provider"))

    before = usage()
    result = run_batch(workspace, args.plan, progress=lambda state: print(
        " ".join(f"{item['id']}={item['status']}" + (f"({item['error_code']}: {item['message']})" if item.get("error_code") else "")
                 for item in state["items"]), flush=True))
    if usage() != before:
        raise Held("pilot_provider_usage", "Provider usage changed during the supplied-script recut.")
    if result["status"] != "ready":
        return 2
    write_descriptions(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
