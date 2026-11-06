"""Register reusable Marvel reaction sets and export silent local motion previews."""
from argparse import ArgumentParser
from pathlib import Path
import shutil
import subprocess

from create_source_photo_revision import CC, COMMONS, ROOT, SOURCES
from PIL import Image, ImageDraw
from shorts_editor.graphics import font
from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset
from yt_pipeline.core import Workspace, file_hash
from yt_pipeline.source_sets import draw_reaction_set, resolve_source_set


LAYERS = {
    **{name: SOURCES[name] for name in ("doom-cutout.png", "miles-cutout.png", "miles-theater.png", "iron-cutout.png")},
    "iron-red-cutout.png": (COMMONS + "Iron_Man_Comic_Con_1.jpg", CC + "licenses/by-sa/2.0/", "greyloch. Masked Iron Man cosplay."),
    "cap-cutout.png": (COMMONS + "Stucky_(48853107183).jpg", CC + "licenses/by/2.0/", "istolethetv. Masked Captain America cosplay."),
    "bucky-cutout.png": (COMMONS + "Stucky_(48853107183).jpg", CC + "licenses/by/2.0/", "istolethetv. Masked Winter Soldier cosplay."),
    "strange-cutout.png": (COMMONS + "Doctor_Strange_Cosplay.jpg", CC + "licenses/by-sa/4.0/", "Simon King. Masked Doctor Strange cosplay."),
    "tony-gauntlet-cutout.png": ("https://caps2.b-cdn.net/200/8-iron-man1/full/iron-man1-movie-screencaps.com-8803.jpg",
                                 "Film frame. Local review.",
                                 "© Marvel Studios. Tony and gauntlet isolated from Iron Man (2008), gallery frame 8803."),
    "workshop-backdrop.png": ("tools/compose_workshop_reference.py", "Original editor illustration",
                              "Workshop, armor displays, cars and sofa back drawn by the editor."),
    "workshop-foreground.png": ("tools/compose_workshop_reference.py", "Original editor illustration",
                                "Sofa arms and cushion rail drawn by the editor."),
}

PRESETS = {
    "crossover-theater": ("cinema", ["doom-cutout", "miles-theater", "iron-red-cutout"], []),
    "iron-man-workshop": ("workshop", ["tony-gauntlet-cutout"], []),
    "spider-man-city": ("city", ["miles-cutout"], []),
    "captain-america-and-bucky": ("living_room", ["cap-cutout", "bucky-cutout"], []),
    "doctor-strange-sanctum": ("sanctum", ["strange-cutout"], []),
}


def still(setup, time):
    frame = Image.new("RGB", (720, 1280))
    draw_reaction_set(frame, setup, time)
    return frame.crop((0, 992, 720, 1280))


def clip(path, setup):
    partial = path.with_suffix(".partial.mp4")
    with subprocess.Popen([
        "ffmpeg", "-v", "error", "-nostdin", "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
        "-video_size", "720x288", "-framerate", "24", "-i", "pipe:0", "-an", "-c:v", "libx264",
        "-threads", "2", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(partial),
    ], stdin=subprocess.PIPE) as process:
        for index in range(96):
            process.stdin.write(still(setup, index / 24).tobytes())
        process.stdin.close()
        if process.wait():
            raise RuntimeError(f"Could not encode {path.name}")
    partial.replace(path)


def build(workspace, source, destination):
    layers = destination / "layers"
    layers.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / "library.json"
    if manifest_path.exists():
        raise FileExistsError("Choose a new library folder to preserve existing preset IDs.")
    assets = {}
    for name, (source_ref, license_name, credit) in LAYERS.items():
        target = layers / name
        shutil.copyfile(source / name, target)
        reference_key = "url" if source_ref.startswith("https://") else "recipe"
        evidence = {reference_key: source_ref, "license": license_name}
        record = register_asset(workspace, target, "test", evidence,
                                commercial=False, editing=False, attribution=credit)
        assets[target.stem] = {
            "id": record["id"], "file": f"layers/{name}", "sha256": record["sha256"],
            **evidence, "credit": credit,
        }
    presets = {}
    board = Image.new("RGB", (1104, 1044), "#0c1119")
    labels = ImageDraw.Draw(board)
    labels.text((22, 20), "MARVEL REACTION SETS", font=font(33, True), fill="#efe3d2")
    for index, (name, (setting, cast, props)) in enumerate(PRESETS.items()):
        request = {"setting": setting, "cast": [assets[key]["id"] for key in cast],
                   "props": [assets[key]["id"] for key in props]}
        if name == "iron-man-workshop":
            request["backdrop"] = assets["workshop-backdrop"]["id"]
            request["foreground"] = assets["workshop-foreground"]["id"]
        _, setup, _ = resolve_source_set(workspace, {"test_only": True, "reaction_set": request}, {"units": []})
        x, y = 22 + index % 2 * 546, 76 + index // 2 * 317
        labels.text((x, y), name.replace("-", " ").title(), font=font(26, True), fill="#efe3d2")
        poster = still(setup, .7)
        board.paste(poster.resize((514, 206), Image.Resampling.LANCZOS), (x, y + 42))
        if name == "iron-man-workshop":
            poster.save(destination / "iron-man-workshop.png")
        path = destination / (name + ".mp4")
        clip(path, setup)
        presets[name] = {"reaction_set": request, "preview": path.name, "sha256": file_hash(path)}
    board.save(destination / "sets.png")
    write_json(manifest_path, {"version": 1, "test_only": True, "assets": assets, "presets": presets})
    write_json(workspace.root / "reaction-presets.json", {name: entry["reaction_set"] for name, entry in presets.items()})


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("cutouts", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(Workspace(ROOT / "data/pipeline"), args.cutouts, args.output)


if __name__ == "__main__":
    main()
