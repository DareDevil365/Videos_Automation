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
from yt_pipeline.lore_style_assets import load_character_cutouts,load_style_layers,validate_execution
from yt_pipeline.lore_identity import IDENTITY_KINDS
from yt_pipeline.source_series import create_series_plan
from yt_pipeline.source_sets import source_painter
from yt_pipeline.lore_voices import choose_series_voices
from yt_pipeline.voice import synthesize
from yt_pipeline.playbooks import get_playbook,validate_playbook_script
from yt_pipeline.contracts import script_contract


SOURCE=ROOT/'Resources/Drafts/adaptive-heroes'
SPECS={
 'vision':('vision-theseus',['vision','white_vision','white_vision_full']),
 'spider':('spider-man-last-lift',['spider_man']),
}
MEDIA={
 'vision':{'file':'vision-film.png','url':'https://image.pngaaa.com/767/1478767.png',
           'page':'https://www.pngaaa.com/detail/1478767','credit':'Marvel Studios character likeness, via PNGaaa. Illustrative MCU cutout.'},
 'white_vision':{'file':'white_vision.png','page':'https://www.deviantart.com/metropolis-hero1125/art/Wandavision-White-Vision-PNG-889226489',
                 'credit':'White Vision fan-prepared cutout by Metropolis-Hero1125, based on Marvel Studios imagery.'},
 'white_vision_full':{'file':'white_vision.png','page':'https://www.deviantart.com/metropolis-hero1125/art/Wandavision-White-Vision-PNG-889226489',
                 'credit':'White Vision fan-prepared cutout by Metropolis-Hero1125, based on Marvel Studios imagery.'},
 'spider_man':{'file':'spider_man-hq.png','url':'https://1.bp.blogspot.com/-OShbtZwHdek/YSkDtO7F0NI/AAAAAAAARxY/Gh4ZFcZySwoZOpSSq1atYMiayrl36lcbwCLcBGAsYHQ/s2048/Spiderman-PNG-Descarga-gratis49.png',
               'page':'https://www.png.utilidadeswebblog.com/2021/08/imagenes-de-el-hombre-arana-con-fondo.html',
               'credit':'Spider-Man modern film-costume cutout, via Utilidades Webblog. Illustrative likeness, not a panel from the 1966 story.'},
}
COVERS={
 'spider':{'file':'spider-cover.jpg','url':'https://i.annihil.us/u/prod/marvel/i/mg/e/70/57a0cce2aa7c0/clean.jpg',
           'page':'https://www.marvel.com/comics/issue/6738/amazing_spider-man_1963_33','credit':'The Amazing Spider-Man #33 cover, Steve Ditko / Stan Goldberg, Marvel Comics.'},
 'vision':{'file':'vision-poster-hq.jpg','url':'https://cdn.marvel.com/content/2x/wandavision_poster.jpg',
           'page':'https://www.marvel.com/articles/tv-shows/wandavision-mid-season-trailer','credit':'Official WandaVision series poster, Marvel Studios / Disney. Show artwork, not a comic cover.'},
}


def prepare(workspace,key,target,build):
    folder,names=SPECS[key];recipe=ROOT/'examples/lore-series'/folder
    local=SOURCE/folder/build;local.mkdir(parents=True,exist_ok=True)
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
    cover=COVERS[key];path=SOURCE/cover['file']
    if not path.exists():
        with urlopen(cover['url'],timeout=40) as response:path.write_bytes(response.read())
    asset=register_asset(workspace,path,'test',{'url':cover['page'],'media_url':cover['url']},
                         commercial=False,editing=False,test_only=True,attribution=cover['credit']+' Local preview only.')
    series['parts'][0]['visual_selection']['layers']={'u1':{'props':{'source_cover':{'asset_id':asset['id'],'box':[136,204,584,923]}}}}
    write_json(local/'series.json',series)
    (local/'part-1.json').write_bytes((recipe/'part-1.json').read_bytes())
    review={'reviewer':'Codex, cited publisher/interview source comparison','supported':True,
            'brief_sha256':file_hash(recipe/'brief.json'),'script_sha256':{'part-1.json':file_hash(local/'part-1.json')},
            'limitations':'Public source summaries and creator interview, not a complete issue or shot-for-shot transcription. Cutouts and geometric movements illustrate the source-linked recap. Preview-only image rights.'}
    write_json(recipe/'source-review.json',review)
    write_json(recipe/'media-sources.json',{**{n:MEDIA[n] for n in names},'source_cover':cover})
    earlier=ROOT/'Resources/Productions'/(folder+('-adaptive-polished-20261106' if key=='spider' else '-adaptive-20261106'))/'batch.json'
    previous=json.loads(earlier.read_text(encoding='utf-8')) if earlier.exists() else {}
    create_series_plan(workspace,local/'series.json',recipe/'brief.json',target,recipe/'source-review.json',build_id=build,assistant_authored=True,
                       revise_batch=earlier if previous.get('status')=='ready' else None)


def preview(workspace,target,key):
    request=json.loads(target.read_text(encoding='utf-8'))['items'][0]['request']
    record=plan_lore(request['script'],request,request['brief'])
    images,_=load_character_cutouts(workspace,request)
    backdrops,props,_=load_style_layers(workspace,request,request['script'])
    sheet=Image.new('RGB',(1152,512*((len(record['plan']['scenes'])+3)//4)),'#080e17')
    for i,scene in enumerate(record['plan']['scenes']):
        validate_execution(scene,request,images,None,IDENTITY_KINDS)
        paint=lambda s,t,d:lore_frame(s,t,d,character_cutouts=images,style_backdrops=backdrops)
        im=source_painter(paint,props.get(scene['unit_id'],()),None,0)(scene,2.5,4)
        sheet.paste(im.resize((288,512)),((i%4)*288,(i//4)*512))
    sheet.save(SOURCE/(key+'-storyboard.jpg'),quality=94)
    write_json(SOURCE/(key+'-visual-decisions.json'),record['plan']['visual_selection'])
    print(key,request['source_voices'],SOURCE/(key+'-storyboard.jpg'),flush=True)


def measure(workspace,key):
    folder,_=SPECS[key];recipe=ROOT/'examples/lore-series'/folder
    series=json.loads((recipe/'series.json').read_text(encoding='utf-8'))
    brief=json.loads((recipe/'brief.json').read_text(encoding='utf-8'))
    script=script_contract(json.loads((recipe/'part-1.json').read_text(encoding='utf-8')),brief,'lesson')
    request={**series['parts'][0],'source_voices':choose_series_voices(workspace,folder,series.get('source_voices'))}
    validate_playbook_script(script,'comic_lore',request)
    plan=plan_lore(script,request,brief)['plan']
    timing=synthesize(workspace,script,SOURCE/folder/'speech-draft',creative_plan=plan,delivery=get_playbook('comic_lore',request)['voice'])
    print(key,'measured seconds',timing['duration'],'voices',timing['cast_voices'],flush=True)


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--only',choices=SPECS)
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--measure-only',action='store_true',help='Measure the draft before freezing a new batch plan.')
    args=parser.parse_args();workspace=Workspace(ROOT/'data/pipeline')
    for key in ([args.only] if args.only else SPECS):
        if args.measure_only:
            measure(workspace,key)
            continue
        folder,_=SPECS[key];build=folder+('-story-revision-final-20261107' if key=='spider' else '-story-revision-20261107')
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
