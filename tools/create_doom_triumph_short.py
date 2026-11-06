"""Build the sourced-character Doom story through the normal local batch pipeline."""
from argparse import ArgumentParser
import json
from pathlib import Path
import sys

from PIL import Image, ImageEnhance, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset
from yt_pipeline.batches import run_batch
from yt_pipeline.core import Workspace, file_hash
from yt_pipeline.source_series import create_series_plan


BUILD = "doom-triumph-torment-final-20261106"
RECIPE = ROOT/"examples/lore-series/doom-triumph-torment"
SOURCE = ROOT/"Resources/Drafts/doom-triumph-cutouts"
MATTES = {
    "doom_magic": {
        "file":"doom-kabam.png", "reference":[640,360],
        "page":"https://www.mcocguideblog.com/2020/03/mcoc-alliance-quest-season-7-update.html",
        "media":"https://1.bp.blogspot.com/-pX4yot8AJoU/XnHW7KDQjKI/AAAAAAAADmg/AhFgyQ2kpoUM1DQUbK-ieEO759NkwQHFgCLcBGAsYHQ/s1600/MCOC%2BDoctor%2BDoom.png",
        "outline":[(153,356),(148,310),(132,302),(105,280),(96,253),(102,230),(119,213),(149,204),
                   (166,184),(170,152),(181,136),(208,132),(235,117),(252,77),(264,31),(281,16),
                   (310,12),(335,15),(348,31),(365,65),(373,92),(382,123),(398,132),(414,132),
                   (440,148),(451,178),(449,201),(476,203),(501,215),(518,247),(520,272),
                   (501,297),(477,311),(475,353)],
        "credit":"Doctor Doom promotional artwork by Marvel Contest of Champions / Kabam, via MCOC Guide Blog."
    },
    "doom": {
        "file":"doom-sideshow-alt.jpg", "reference":[640,640],
        "page":"https://www.toyshow.com.br/doctor-doom-premium-format-estatua-escala-14-sideshow",
        "media":"https://images.tcdn.com.br/img/img_prod/460977/doctor_doom_premium_format_estatua_escala_1_4_sideshow_8651_2_20201211172103.jpg",
        "outline":[(121,381),(125,357),(146,297),(179,241),(218,201),(253,154),(269,135),(296,122),
                   (318,105),(330,66),(344,36),(354,25),(366,30),(383,52),(391,75),(393,104),
                   (407,128),(415,159),(414,188),(433,188),(446,198),(454,213),(443,227),
                   (421,240),(432,271),(456,301),(468,331),(467,350),(452,382),(439,403),
                   (441,462),(457,475),(444,485),(405,483),(397,463),(396,421),(388,393),
                   (363,416),(354,452),(356,488),(371,507),(356,527),(320,532),(309,515),
                   (304,473),(291,433),(259,436),(221,428),(180,427),(142,420),(119,400)],
        "holes":[[(353,417),(370,404),(388,394),(387,424),(395,456),(398,481),
                  (375,480),(373,499),(365,502),(355,486),(354,454)]],
        "credit":"Doctor Doom statue photograph by Sideshow Collectibles, via Toyshow."
    },
    "strange": {
        "file":"strange-kabam.png", "reference":[498,491],
        "page":"https://marvelcoc.blogspot.com/p/dr-strange.html",
        "media":"https://3.bp.blogspot.com/-HhL4Q_IPOCo/VSi_M_YZP6I/AAAAAAABAIE/35NrnLVDMJA/s1600/Dr.%2BStrange%2BMarvel%2BContest%2Bof%2BChampions%2Bmarvelcoc.blogspot.com.PNG",
        "outline":[(82,275),(97,250),(129,213),(156,174),(171,144),(185,109),(201,94),
                   (210,69),(213,53),(202,37),(207,30),(228,38),(245,41),(263,44),
                   (276,36),(298,32),(320,36),(307,46),(296,62),(297,86),(307,101),
                   (307,124),(326,144),(334,170),(344,213),(342,243),(345,267),(342,281),
                   (333,295),(321,299),(318,327),(319,368),(330,400),(331,449),(326,463),
                   (312,464),(302,453),(298,428),(287,402),(277,365),(267,335),(258,310),
                   (247,340),(242,370),(238,396),(243,414),(231,430),(211,435),(178,433),
                   (176,421),(191,412),(200,394),(204,363),(210,327),(209,288),(178,291),
                   (156,296),(129,291),(106,283)],
        "credit":"Doctor Strange character render from Marvel Contest of Champions / Kabam, via MarvelCoC Blog."
    },
    "mephisto": {
        "file":"mephisto-kabam.jpg", "reference":[401,573],
        "page":"https://frontlinemcoc.home.blog/2019/09/09/champion-guide-mephisto/",
        "media":"https://frontlinemcoc.home.blog/wp-content/uploads/2019/08/img_6470-1.jpg",
        "outline":[(86,385),(96,335),(108,301),(115,258),(121,209),(129,173),(139,146),(162,128),
                   (170,102),(169,86),(159,80),(178,74),(175,55),(179,28),(190,49),(204,56),
                   (215,53),(232,46),(239,33),(245,55),(240,77),(253,65),(246,92),(236,102),
                   (238,120),(263,126),(286,138),(296,162),(298,183),(310,195),(317,193),
                   (317,204),(312,212),(314,229),(307,246),(287,252),(286,291),(291,331),
                   (303,396),(308,434),(302,442),(299,473),(299,502),(288,516),(265,514),
                   (257,502),(261,478),(251,431),(241,394),(229,365),(217,349),(204,325),
                   (191,356),(178,398),(166,436),(154,475),(132,489),(100,497),(92,489),
                   (100,480),(123,467),(131,429),(136,406),(123,414),(110,401),(95,397)],
        "credit":"Mephisto character render from Marvel Contest of Champions / Kabam, via Frontline MCOC."
    },
    "cynthia": {
        "file":"cynthia.webp", "reference":[640,320],
        "page":"https://guides.justwatch.com/us/avengers-doomsday-cynthia-von-doom-explained",
        "media":"https://guides.justwatch.com/sgassets/images/editorial/29187_cynthia-von-doom_1400.webp",
        "outline":[(1,316),(19,263),(32,229),(44,208),(61,182),(86,157),(103,130),(118,93),
                   (130,54),(143,18),(151,1),(230,1),(249,23),(272,64),(284,95),(290,136),
                   (309,163),(320,185),(337,209),(314,232),(289,248),(278,271),(260,293),
                   (252,319)],
        "credit":"Cynthia von Doom comic portrait, via JustWatch editorial. Original character artwork belongs to Marvel."
    },
}


def prepare_cast(workspace, source):
    cast = {}
    for name, recipe in MATTES.items():
        path = source/recipe["file"]
        with Image.open(path) as raw:
            image = raw.convert("RGBA")
        width, height = recipe["reference"]
        alpha = Image.new("L", image.size)
        points = [(x*image.width/width,y*image.height/height) for x,y in recipe["outline"]]
        ImageDraw.Draw(alpha).polygon(points,fill=255)
        for hole in recipe.get("holes", []):
            ImageDraw.Draw(alpha).polygon([(x*image.width/width,y*image.height/height) for x,y in hole],fill=0)
        alpha = alpha.filter(ImageFilter.GaussianBlur(.8))
        if name=="doom":
            image = ImageEnhance.Brightness(image).enhance(1.16)
        image.putalpha(alpha)
        target = source/(name+"-cutout.png")
        image.crop(alpha.getbbox()).save(target)
        asset = register_asset(workspace,target,"test",
                               {"url":recipe["page"],"media_url":recipe["media"],
                                "derived_from":file_hash(path),"matte":recipe["outline"],"holes":recipe.get("holes",[]),
                                "reference_size":recipe["reference"]},
                               commercial=False,editing=False,test_only=True,attribution=recipe["credit"])
        cast[name] = asset["id"]
    return cast


def prepare_plan(workspace, target, source):
    cast = prepare_cast(workspace, source)
    series = json.loads((RECIPE/"series.json").read_text(encoding="utf-8"))
    # The source-aware series schema already preserves cast references.
    local_series = source/"series-with-assets.json"
    series["parts"][0]["script"] = str("part-1.json")
    series["parts"][0]["pact_cast"] = cast
    write_json(local_series,series)
    script_path = source/"part-1.json"
    script_path.write_bytes((RECIPE/"part-1.json").read_bytes())
    review = {
        "reviewer":"Codex, publisher and source comparison",
        "supported":True,"brief_sha256":file_hash(RECIPE/"brief.json"),
        "script_sha256":{"part-1.json":file_hash(script_path)},
        "limitations":"Public publisher recaps and corroborating summaries. The device, contract and movement are original illustration. Doom's intent remains a question."
    }
    review_path = RECIPE/"source-review.json"
    write_json(review_path,review)
    earlier=ROOT/"Resources/Productions/doom-triumph-torment-cutouts-20261106/batch.json"
    previous=json.loads(earlier.read_text(encoding="utf-8")) if earlier.is_file() else {}
    create_series_plan(workspace,local_series,RECIPE/"brief.json",target,review_path,
                       build_id=BUILD,assistant_authored=True,
                       revise_batch=earlier if previous.get("status")=="ready" else None)


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=SOURCE)
    parser.add_argument("--prepare-only",action="store_true")
    args=parser.parse_args()
    workspace=Workspace(ROOT/"data/pipeline")
    plan=ROOT/"Resources/Plans"/(BUILD+".json")
    if not plan.exists():
        prepare_plan(workspace,plan,args.source)
    if args.prepare_only:
        return 0
    with workspace.connect() as db:
        before=dict(db.execute("SELECT provider,SUM(calls) FROM usage GROUP BY provider"))
    result=run_batch(workspace,plan,progress=lambda state:print(
        [(row["status"],row.get("error_code"),row.get("message")) for row in state["items"]],flush=True))
    with workspace.connect() as db:
        if before!=dict(db.execute("SELECT provider,SUM(calls) FROM usage GROUP BY provider")):
            raise RuntimeError("Text provider usage changed during the supplied-script render.")
    if result["status"]!="ready":
        return 2
    folder=Path(result["items"][0]["output_folder"])
    metadata=json.loads((folder/"metadata.json").read_text(encoding="utf-8"))
    (folder/"description.md").write_text("# "+metadata["title"]+"\n\n"+metadata["description"]+
                                         "\n\n[Watch the preview](video.mp4)\n",encoding="utf-8")
    print(folder/"video.mp4")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
