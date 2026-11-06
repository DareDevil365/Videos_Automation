"""Rebuild the Thor Short with prepared source character layers and the same narration."""
from argparse import ArgumentParser
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset
from yt_pipeline.batches import run_batch
from yt_pipeline.core import Workspace, file_hash, now


SOURCE = ROOT / "Resources/Drafts/thor-source-cutouts"
PREVIOUS = "thor-beta-ray-bill-recut-20261106"
BUILD = "thor-beta-ray-bill-source-cutouts-20261106"
REFERENCES = {
    "bill": ("bill-kabam.jpg", "https://x.com/MarvelChampions/status/1798474975898140688",
             "https://pbs.twimg.com/media/GPV3cQ7XUAAN7za.jpg?name=orig",
             "Beta Ray Bill character art by Marvel Contest of Champions / Kabam."),
    "thor": ("thor-kabam.png", "https://www.pngkey.com/detail/u2a9o0i1w7o0e6i1_thor-thor-contest-of-champions/",
             "https://www.pngkey.com/png/detail/2-28246_thor-thor-contest-of-champions.png",
             "Thor Marvel Contest of Champions render, sourced from the PNGkey copy."),
}
MATTES = {
    "bill": {
        "body": (
            [(194,285),(197,242),(208,222),(221,213),(236,181),(246,178),(262,193),(277,212),(290,221),
             (284,203),(276,190),(271,175),(275,161),(287,168),(300,184),(309,165),(322,149),
             (337,141),(354,141),(377,151),(351,153),(334,163),(324,180),(331,189),(349,182),
             (348,198),(338,212),(325,219),(327,237),(341,244),(357,254),(373,270),(376,289),
             (369,299),(352,290),(353,311),(347,324),(356,346),(344,369),(349,389),(358,417),
             (331,433),(241,437),(218,407),(207,376),(198,340)],
            {"start": (314,207), "end": (305,370), "shoulder": (349,276)},
        ),
        "upper": (
            [(329,252),(355,257),(374,269),(376,292),(365,303),(371,322),(361,339),
             (345,336),(338,321),(328,301),(326,283)],
            {"start": (351,272), "end": (355,325)},
        ),
        "forearm": (
            [(348,326),(363,324),(378,326),(397,319),(414,315),(419,307),(416,301),(422,298),
             (431,304),(439,303),(444,294),(451,292),(455,296),(455,306),(452,314),
             (444,321),(438,337),(426,349),(409,356),(384,365),(369,369),(357,363),(352,350)],
            {"start": (362,345), "end": (435,320)},
        ),
    },
    "thor": {
        "body": (
            [(196,214),(207,192),(224,160),(229,145),(226,154),(227,122),(243,100),(262,79),(282,66),
             (304,66),(300,52),(295,42),(292,29),(309,42),(320,35),(343,33),(352,38),(356,33),
             (356,55),(353,75),(359,89),(371,94),(379,108),(389,127),(388,147),(383,159),
             (392,182),(387,200),(378,211),(381,231),(371,240),(351,246),(317,240),(299,232),
             (294,214),(251,219),(234,215),(217,221)],
            {"start": (333,69), "end": (346,224), "shoulder": (376,155)},
        ),
        "upper": (
            [(368,134),(381,144),(392,166),(401,182),(410,198),(425,212),(421,227),
             (404,232),(393,221),(381,206),(369,192),(364,174)],
            {"start": (374,155), "end": (407,211)},
        ),
        "forearm": (
            [(397,209),(413,208),(428,217),(436,224),(444,234),(454,246),(459,253),(462,268),
             (458,279),(453,278),(450,271),(446,282),(440,280),(438,271),(433,275),
             (429,272),(428,267),(422,268),(420,264),(426,255),(424,246),(414,243),(407,235)],
            {"start": (408,221), "end": (443,258)},
        ),
    },
}


def prepare_layers(workspace, directory):
    names = {}
    for actor, (filename, page, media, credit) in REFERENCES.items():
        path = directory / filename
        names[actor] = {}
        with Image.open(path) as raw:
            source = raw.convert("RGBA")
        scale = source.width / 600
        for part, (outline, points) in MATTES[actor].items():
            alpha = Image.new("L", source.size)
            ImageDraw.Draw(alpha).polygon([(x*scale,y*scale) for x,y in outline], fill=255)
            alpha = alpha.filter(ImageFilter.GaussianBlur(.68))
            box = alpha.getbbox()
            cutout = source.copy()
            cutout.putalpha(alpha)
            target = directory / f"{actor}-{part}.png"
            cutout.crop(box).save(target)
            anchors = {name: [x*scale-box[0], y*scale-box[1]] for name, (x,y) in points.items()}
            asset = register_asset(workspace,target,"test",
                                   {"url":page,"media_url":media,"derived_from":file_hash(path),
                                    "matte_reference_width":600,"matte":outline,"part":part,**anchors},
                                   commercial=False,editing=False,test_only=True,attribution=credit)
            names[actor][part] = asset["id"]
    return names


def build_plan(workspace, target, directory):
    plan = json.loads((target.with_name(PREVIOUS+".json")).read_text(encoding="utf-8"))
    batch = json.loads((ROOT/"Resources/Productions"/PREVIOUS/"batch.json").read_text(encoding="utf-8"))
    request = plan["items"][0]["request"]
    request["prototype_revision_of"] = batch["items"][0]["job_id"]
    request["thunder_cast"] = prepare_layers(workspace, directory)
    plan.update(id=BUILD,created_at=now(),note="Same Thor episode with articulated sourced cast and original geometric props.")
    write_json(target, plan)
    return plan


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=SOURCE)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    workspace = Workspace(ROOT/"data/pipeline")
    plan = ROOT/"Resources/Plans"/(BUILD+".json")
    if not plan.exists():
        build_plan(workspace, plan, args.input)
    if args.prepare_only:
        return 0
    with workspace.connect() as db:
        before = dict(db.execute("SELECT provider,SUM(calls) FROM usage GROUP BY provider"))
    result = run_batch(workspace, plan, progress=lambda state: print(
        [(item["status"],item.get("error_code"),item.get("message")) for item in state["items"]],flush=True))
    with workspace.connect() as db:
        after = dict(db.execute("SELECT provider,SUM(calls) FROM usage GROUP BY provider"))
    if before != after:
        raise RuntimeError("Provider usage changed during a local visual-only revision.")
    if result["status"] != "ready":
        return 2
    folder = Path(result["items"][0]["output_folder"])
    meta = json.loads((folder/"metadata.json").read_text(encoding="utf-8"))
    (folder/"description.md").write_text("# "+meta["title"]+"\n\n"+meta["description"]+
                                         "\n\n[Watch the preview](video.mp4)\n",encoding="utf-8")
    print(folder/"video.mp4")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
