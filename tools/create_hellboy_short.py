"""Render the authored Hellboy Short with geometric actors and sourced photographic props."""
from argparse import ArgumentParser
import json
from pathlib import Path
import sys
from urllib.request import urlopen

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset
from yt_pipeline.batches import run_batch
from yt_pipeline.core import Workspace, file_hash
from yt_pipeline.lore_hellboy import load_hellboy_media
from yt_pipeline.lore_visuals import lore_frame, plan_lore
from yt_pipeline.source_series import create_series_plan


BUILD = 'hellboy-horns-geometric-final-20261106'
RECIPE = ROOT/'examples/lore-series/hellboy-horns'
SOURCE = ROOT/'Resources/Drafts/hellboy-horns'


def prepare_media(workspace, folder):
    folder.mkdir(parents=True,exist_ok=True)
    sources=json.loads((RECIPE/'media-sources.json').read_text(encoding='utf-8'))
    media={}
    for name, record in sources.items():
        raw=folder/record['file']
        if not raw.exists():
            with urlopen(record['url'],timeout=45) as response:
                raw.write_bytes(response.read())
        image=Image.open(raw).convert('RGBA')
        if name=='ruins':
            # Keep the architecture; exclude the photographed visitors on the right.
            image=image.crop((0,0,round(image.width*.80),image.height))
        elif name=='book':
            w,h=image.size
            alpha=Image.new('L',image.size)
            ImageDraw.Draw(alpha).polygon([(w*.18,h*.045),(w*.81,h*.035),(w*.835,h*.06),
                (w*.845,h*.68),(w*.865,h*.75),(w*.846,h*.96),(w*.205,h*.945),(w*.18,h*.88)],fill=255)
            image.putalpha(alpha)
            image=image.crop(alpha.getbbox())
        target=folder/(name+'-prepared.png')
        image.save(target)
        credit=(f"{record['credit']}. {record['page']} — {record['license']} "
                f"({record['license_url']}). Cropped, graded and composited as illustrative scenery or a prop.")
        asset=register_asset(workspace,target,'licensed_stock',
            {'url':record['page'],'media_url':record['url'],'license':record['license_url'],
             'derived_from':file_hash(raw),'modification':'Crop, cutout matte and scene grading. Real-world setting is illustrative.'},
            attribution=credit)
        media[name]=asset['id']
    return media


def prepare_plan(workspace, target, folder, build_id, revise_batch=None):
    series=json.loads((RECIPE/'series.json').read_text(encoding='utf-8'))
    series['parts'][0]['hellboy_media']=prepare_media(workspace,folder)
    local_series=folder/'series-with-assets.json'
    write_json(local_series,series)
    script=folder/'part-1.json'
    script.write_bytes((RECIPE/'part-1.json').read_bytes())
    review={'reviewer':'Codex, publisher timeline and licensed introduction comparison',
            'supported':True,'brief_sha256':file_hash(RECIPE/'brief.json'),
            'script_sha256':{'part-1.json':file_hash(script)},
            'limitations':'Classic comics premise and Wake the Devil #5, not the conclusion of the entire saga. Horn action is corroborated by a secondary discussion identifying the issue. Final line is original interpretation. Photographs and geometric acting are illustrative.'}
    write_json(RECIPE/'source-review.json',review)
    create_series_plan(workspace,local_series,RECIPE/'brief.json',target,RECIPE/'source-review.json',
                       build_id=build_id,assistant_authored=True,revise_batch=revise_batch)


def storyboard(workspace, target, folder):
    request=json.loads(target.read_text(encoding='utf-8'))['items'][0]['request']
    media,_=load_hellboy_media(workspace,request)
    scenes=plan_lore(request['script'],request,request['brief'])['plan']['scenes']
    sheet=Image.new('RGB',(4*288,2*512),'#080e17')
    for index,scene in enumerate(scenes):
        frame=lore_frame(scene,2.7,4,hellboy_media=media)
        frame.save(folder/(scene['unit_id']+'-storyboard.png'))
        sheet.paste(frame.resize((288,512)),((index%4)*288,(index//4)*512))
    sheet.save(folder/'storyboard.jpg',quality=94)
    print(folder/'storyboard.jpg',flush=True)


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--build-id',default=BUILD)
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--revise-batch',type=Path,help='Prior test batch from this series when making a revision.')
    args=parser.parse_args()
    workspace=Workspace(ROOT/'data/pipeline')
    target=ROOT/'Resources/Plans'/(args.build_id+'.json')
    if not target.exists():
        prepare_plan(workspace,target,SOURCE,args.build_id,args.revise_batch)
    storyboard(workspace,target,SOURCE)
    if args.prepare_only:
        return 0
    with workspace.connect() as db:
        before=dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider'))
    result=run_batch(workspace,target,progress=lambda state: print(
        [(row['status'],row.get('error_code'),row.get('message')) for row in state['items']],flush=True))
    with workspace.connect() as db:
        if before!=dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider')):
            raise RuntimeError('Supplied-script render unexpectedly used a text provider.')
    if result['status']!='ready':
        return 2
    folder=Path(result['items'][0]['output_folder'])
    metadata=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    (folder/'description.md').write_text('# '+metadata['title']+'\n\n'+metadata['description']+'\n',encoding='utf-8')
    print(folder/'video.mp4')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
