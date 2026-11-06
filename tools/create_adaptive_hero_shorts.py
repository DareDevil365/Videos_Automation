"""Build source-reviewed Vision and Spider-Man examples with per-shot art and varied voices."""
from argparse import ArgumentParser
import html
import json
from pathlib import Path
import re
import sys
from urllib.request import urlopen

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset
from yt_pipeline.batches import run_batch
from yt_pipeline.core import Workspace,file_hash
from yt_pipeline.lore_visuals import plan_lore,lore_frame
from yt_pipeline.lore_style_assets import load_character_cutouts,validate_execution
from yt_pipeline.lore_identity import IDENTITY_KINDS
from yt_pipeline.source_series import create_series_plan


SOURCE=ROOT/'Resources/Drafts/adaptive-heroes'
SPECS={
 'vision':('vision-theseus',['vision','white_vision']),
 'spider':('spider-man-last-lift',['spider_man']),
}
MEDIA={
 'vision':{'file':'vision-film.png','url':'https://image.pngaaa.com/767/1478767.png',
           'page':'https://www.pngaaa.com/detail/1478767','credit':'Marvel Studios character likeness, via PNGaaa. Illustrative MCU cutout.'},
 'white_vision':{'file':'white_vision.png','page':'https://www.deviantart.com/metropolis-hero1125/art/Wandavision-White-Vision-PNG-889226489',
                 'credit':'White Vision fan-prepared cutout by Metropolis-Hero1125, based on Marvel Studios imagery.'},
 'spider_man':{'file':'spider_man-hq.png','url':'https://1.bp.blogspot.com/-OShbtZwHdek/YSkDtO7F0NI/AAAAAAAARxY/Gh4ZFcZySwoZOpSSq1atYMiayrl36lcbwCLcBGAsYHQ/s2048/Spiderman-PNG-Descarga-gratis49.png',
               'page':'https://www.png.utilidadeswebblog.com/2021/08/imagenes-de-el-hombre-arana-con-fondo.html',
               'credit':'Spider-Man modern film-costume cutout, via Utilidades Webblog. Illustrative likeness, not a panel from the 1966 story.'},
}


def prepare(workspace,key,target,build):
    folder,names=SPECS[key];recipe=ROOT/'examples/lore-series'/folder
    local=SOURCE/folder;local.mkdir(parents=True,exist_ok=True)
    refs={}
    for name in names:
        spec=MEDIA[name];raw=SOURCE/spec['file'];url=spec.get('url')
        if not raw.exists():
            if not url:
                with urlopen(spec['page'],timeout=35) as response:page=response.read().decode('utf-8')
                url=html.unescape(re.findall(r'<meta[^>]+(?:property|name)="og:image"[^>]+content="([^"]+)',page)[0])
            with urlopen(url,timeout=40) as response:raw.write_bytes(response.read())
        with Image.open(raw) as source:im=source.convert('RGBA')
        # Comparable waist-up crops preserve facial scale in the identity two-shot.
        if name=='vision':im=im.crop((200,0,734,838))
        if name=='white_vision':im=im.crop((70,0,600,838))
        path=local/(name+'-cutout.png');im.save(path)
        asset=register_asset(workspace,path,'test',{'url':spec['page'],'media_url':url or 'Public page og:image at download time',
              'derived_from':file_hash(raw),'preparation':'Transparent crop, then common scene grade.'},
              commercial=False,editing=False,test_only=True,attribution=spec['credit']+' Local preview; no reuse permission inferred.')
        refs[name]=asset['id']
    series=json.loads((recipe/'series.json').read_text(encoding='utf-8'))
    series['parts'][0]['character_cutouts']=refs
    write_json(local/'series.json',series)
    (local/'part-1.json').write_bytes((recipe/'part-1.json').read_bytes())
    review={'reviewer':'Codex, cited publisher/interview source comparison','supported':True,
            'brief_sha256':file_hash(recipe/'brief.json'),'script_sha256':{'part-1.json':file_hash(local/'part-1.json')},
            'limitations':'Public source summaries and creator interview, not a complete issue or shot-for-shot transcription. Cutouts and geometric movements illustrate the source-linked recap. Preview-only image rights.'}
    write_json(recipe/'source-review.json',review)
    write_json(recipe/'media-sources.json',{n:MEDIA[n] for n in names})
    earlier=ROOT/'Resources/Productions'/(folder+'-adaptive-20261106')/'batch.json'
    previous=json.loads(earlier.read_text(encoding='utf-8')) if earlier.exists() else {}
    create_series_plan(workspace,local/'series.json',recipe/'brief.json',target,recipe/'source-review.json',build_id=build,assistant_authored=True,
                       revise_batch=earlier if key=='spider' and previous.get('status')=='ready' else None)


def preview(workspace,target,key):
    request=json.loads(target.read_text(encoding='utf-8'))['items'][0]['request']
    record=plan_lore(request['script'],request,request['brief'])
    images,_=load_character_cutouts(workspace,request)
    sheet=Image.new('RGB',(1152,1024),'#080e17')
    for i,scene in enumerate(record['plan']['scenes']):
        validate_execution(scene,request,images,None,IDENTITY_KINDS)
        im=lore_frame(scene,2.5,4,character_cutouts=images)
        sheet.paste(im.resize((288,512)),((i%4)*288,(i//4)*512))
    sheet.save(SOURCE/(key+'-storyboard.jpg'),quality=94)
    write_json(SOURCE/(key+'-visual-decisions.json'),record['plan']['visual_selection'])
    print(key,request['source_voices'],SOURCE/(key+'-storyboard.jpg'),flush=True)


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--only',choices=SPECS)
    parser.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args();workspace=Workspace(ROOT/'data/pipeline')
    for key in ([args.only] if args.only else SPECS):
        folder,_=SPECS[key];build=folder+('-adaptive-polished-20261106' if key=='spider' else '-adaptive-20261106')
        target=ROOT/'Resources/Plans'/(build+'.json')
        if not target.exists():prepare(workspace,key,target,build)
        preview(workspace,target,key)
        if args.prepare_only:continue
        with workspace.connect() as db:before=dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider'))
        result=run_batch(workspace,target,progress=lambda state:print(key,[(r['status'],r.get('error_code'),r.get('message')) for r in state['items']],flush=True))
        with workspace.connect() as db:assert before==dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider'))
        if result['status']!='ready':return 2
        output=Path(result['items'][0]['output_folder'])
        (output/'visual-decisions.json').write_bytes((SOURCE/(key+'-visual-decisions.json')).read_bytes())
        metadata=json.loads((output/'metadata.json').read_text(encoding='utf-8'))
        (output/'description.md').write_text(metadata['title']+'\n\n'+metadata['description']+'\n',encoding='utf-8')
        print(output/'video.mp4',flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
