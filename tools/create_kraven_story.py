"""Measure/prepare the reviewed story, then explicitly render its local preview."""
from argparse import ArgumentParser
import json
from pathlib import Path
import sys
from urllib.request import urlopen

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset
from yt_pipeline.batches import run_batch
from yt_pipeline.contracts import script_contract
from yt_pipeline.core import Workspace,file_hash
from yt_pipeline.lore_visuals import plan_lore,lore_frame
from yt_pipeline.lore_cuts import cut_schedule,cut_painter
from yt_pipeline.playbooks import get_playbook,validate_playbook_script
from yt_pipeline.source_series import create_series_plan
from yt_pipeline.source_sets import resolve_source_set,source_painter,check_lore_reuse
from yt_pipeline.lore_style_assets import load_style_layers
from yt_pipeline.voice import synthesize

RECIPE=ROOT/'examples/lore-series/kraven-last-hunt'
DRAFT=ROOT/'Resources/Drafts/kraven-last-hunt'
BUILD='kraven-last-hunt-subscribe-final-20261107'
COVER_URL='https://cdn.marvel.com/u/prod/marvel/i/mg/a/40/4bc668a38f9e6/clean.jpg'


def inputs(workspace):
    script=json.loads((RECIPE/'part-1.json').read_text(encoding='utf8'))
    brief=json.loads((RECIPE/'brief.json').read_text(encoding='utf8'))
    series=json.loads((RECIPE/'series.json').read_text(encoding='utf8'))
    part=series['parts'][0]
    request={**part,'source_voices':series['source_voices'],'test_only':True}
    validate_playbook_script(script_contract(script,brief,'lesson'),'comic_lore',request)
    return script,brief,series,request


def prepare(workspace,target):
    script,brief,series,request=inputs(workspace)
    DRAFT.mkdir(parents=True,exist_ok=True)
    cover=DRAFT/'cover.jpg'
    if not cover.exists():
        with urlopen(COVER_URL,timeout=30) as response:cover.write_bytes(response.read())
    asset=register_asset(workspace,cover,'test',{'url':'https://www.marvel.com/comics/series/129/spiderman_kravens_last_hunt_1999','media_url':COVER_URL},
                         commercial=False,editing=False,test_only=True,attribution='Marvel Comics. Kraven’s Last Hunt collected-edition cover; original story 1987. J.M. DeMatteis, Mike Zeck, Bob McLeod. Local review only.')
    presets=json.loads((workspace.root/'reaction-presets.json').read_text())
    # Keep a Marvel theater, replacing the old blue Doom photo with Captain America.
    audience={**presets['crossover-theater'],'cast':[presets['captain-america-and-bucky']['cast'][0],*presets['crossover-theater']['cast'][1:]]}
    part=series['parts'][0];part.pop('reaction_preset',None);part['reaction_set']=audience
    part['visual_selection']['layers']={'u2':{'props':{'source_cover':{'asset_id':asset['id'],'box':[136,204,584,923],
        'repeat_reason':'A revision of this same episode retains its identifying source cover; the story staging is being improved.'}}}}
    preflight={**part,'test_only':True,'lore_fresh_visuals':True}
    resolve_source_set(workspace,preflight,script)
    load_style_layers(workspace,preflight,script)
    check_lore_reuse(workspace,{'id':'preflight','channel':'entertainment','request':preflight})
    write_json(DRAFT/'series.json',series)
    (DRAFT/'part-1.json').write_bytes((RECIPE/'part-1.json').read_bytes())
    review={'reviewer':'Codex, indexed official Marvel history/recaps/issue and reading-order comparison','supported':True,
            'limitations':brief['notes'],'brief_sha256':file_hash(RECIPE/'brief.json'),'script_sha256':{'part-1.json':file_hash(RECIPE/'part-1.json')}}
    write_json(RECIPE/'source-review.json',review)
    earlier=ROOT/'Resources/Productions/kraven-last-hunt-complete-20261107/batch.json'
    create_series_plan(workspace,DRAFT/'series.json',RECIPE/'brief.json',target,RECIPE/'source-review.json',build_id=BUILD,
                       assistant_authored=True,revise_batch=earlier if earlier.exists() else None)


def storyboard(workspace,target):
    request=json.loads(target.read_text(encoding='utf8'))['items'][0]['request']
    plan=plan_lore(request['script'],request,request['brief'])['plan']
    _,reaction,_=resolve_source_set(workspace,request,request['script'])
    backdrops,props,_=load_style_layers(workspace,request,request['script'])
    frames=[]
    for n,scene in enumerate(plan['scenes']):
        span=max(6,len(scene['text'].split())/2.6)
        cuts=cut_schedule(scene,{'start':n*6,'duration':span},[],preview=True)
        painter=source_painter(cut_painter(lambda s,t,d:lore_frame(s,t,d,style_backdrops=backdrops),cuts),props.get(scene['unit_id'],()),reaction,n*6)
        for row in cuts or [{'start':0,'end':span}]:
            frames.append(painter(scene,(row['start']+row['end'])/2,span))
    sheet=Image.new('RGB',(1152,512*((len(frames)+3)//4)),'#211b20')
    for n,frame in enumerate(frames):sheet.paste(frame.resize((288,512)),(n%4*288,n//4*512))
    sheet.save(DRAFT/'storyboard.jpg',quality=94)
    write_json(DRAFT/'design-decisions.json',plan['design'])


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--measure-only',action='store_true')
    parser.add_argument('--render',action='store_true',help='Render only after the source/script/design and editor checks are complete.')
    args=parser.parse_args();workspace=Workspace(ROOT/'data/pipeline')
    target=ROOT/'Resources/Plans'/(BUILD+'.json')
    if args.measure_only:
        script,brief,series,request=inputs(workspace)
        plan=plan_lore(script,request,brief)['plan']
        voice=synthesize(workspace,script,DRAFT/'speech-draft',creative_plan=plan,delivery=get_playbook('comic_lore',request)['voice'])
        print('Measured speech:',voice['duration'],'seconds');return 0
    if not target.exists():prepare(workspace,target)
    storyboard(workspace,target)
    print('Storyboard:',DRAFT/'storyboard.jpg',flush=True)
    if not args.render:return 0
    with workspace.connect() as db:before=dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider'))
    result=run_batch(workspace,target,progress=lambda state:print([(r.get('stage',r['status']),r.get('error_code')) for r in state['items']],flush=True))
    with workspace.connect() as db:assert before==dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider'))
    if result['status']!='ready':print(result);return 2
    output=Path(result['items'][0]['output_folder'])
    (output/'design-decisions.json').write_bytes((DRAFT/'design-decisions.json').read_bytes())
    metadata=json.loads((output/'metadata.json').read_text(encoding='utf8'))
    (output/'description.md').write_text(metadata['title']+'\n\n'+metadata['description'],encoding='utf8')
    print(output/'video.mp4');return 0


if __name__=='__main__':raise SystemExit(main())
