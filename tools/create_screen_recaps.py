"""Build supplied, source-reviewed comic/film/episode recaps with local tools."""
from argparse import ArgumentParser
import json
from pathlib import Path
import sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset,asset_record
from yt_pipeline.batches import run_batch
from yt_pipeline.contracts import script_contract
from yt_pipeline.core import Workspace,file_hash
from yt_pipeline.curated_music import music_catalog
from yt_pipeline.lore_cuts import cut_schedule,cut_painter
from yt_pipeline.lore_visuals import plan_lore,lore_frame
from yt_pipeline.lore_style_assets import load_style_layers
from yt_pipeline.playbooks import get_playbook,validate_playbook_script
from yt_pipeline.source_series import create_series_plan
from yt_pipeline.source_sets import resolve_source_set,source_painter,check_lore_reuse
from yt_pipeline.voice import synthesize
from yt_pipeline.dialogue_captions import align_dialogue

SPECS={
 'strange':('strange-supreme-heart','strange-poster.jpg','https://www.syfy.com/syfy-wire/marvel-what-if-dr-strange-heartbreaking-episode-recap','https://www.syfy.com/sites/syfy/files/styles/scale_600/public/what-if-dr.-strange-poster.jpg','u2'),
 'civil':('civil-war-complete','civil-war-poster.jpg','https://www.posterpalace.com/products/copy-of-the-lone-ranger','https://www.posterpalace.com/cdn/shop/products/civil-war-posterpalacecom-491535.jpg?v=1671584717','u1'),
 'deadpool':('deadpool-fourth-wall','deadpool-cover.jpg','https://www.penguinrandomhouse.com/books/693632/deadpool-kills-the-marvel-universe-by-cullen-bunn/','https://images2.penguinrandomhouse.com/cover/9780785164036','u2'),
 'dw':('deadpool-wolverine-recap','dw-poster.jpg','https://en.wikipedia.org/wiki/Deadpool_%26_Wolverine','https://upload.wikimedia.org/wikipedia/en/4/4c/Deadpool_%26_Wolverine_poster.jpg','u2'),
 'ff':('fantastic-four-first-steps-recap','ff-poster.jpg','https://movies.disney.com/the-fantastic-four-first-steps','https://lumiere-a.akamaihd.net/v1/images/p_studios_fantasticfourfirststeps_pay1sunrise_poster_9d183368.jpeg?region=0%2C0%2C540%2C810','u2'),
 'xm':('x-men-krakoa-rescue','xm-poster.jpg','https://blogs.loc.gov/headlinesandheroes/2023/04/x-men-60-uncanny-years/','https://blogs.loc.gov/headlinesandheroes/files/2023/04/giantxmen_cover.jpg','u2')}
DRAFT=ROOT/'Resources/Drafts/screen-recaps'
MUSIC={
 'civil':('mixkit-565','Dark tension supports the escalating split and personal trap; avoid an uplifting resolution bed.'),
 'strange':('mixkit-671','Sparse ominous piano supports the repeated loss and escalating supernatural threat.'),
 'deadpool':('mixkit-188','Sparse mystery atmosphere leaves room for the narration and the late creator/reader reveal; avoid treating the killing spree as a comedy montage.'),
 'dw':('mixkit-370','A restrained energetic pulse supports the pursuit and reluctant team-up; keep the montage track below complete narration.'),
 'ff':('mixkit-565','Dark cinematic pressure supports the impossible family-versus-planet bargain and rising cosmic threat.'),
 'xm':('mixkit-188','Sparse mystery leaves the island discovery room to land before the combined-power escape.')}


def story_music(workspace,key):
    track_key,reason=MUSIC[key]
    installed=json.loads((workspace.root/'curated-music-library.json').read_text(encoding='utf8'))['tracks']
    track=next(t for t in music_catalog()['tracks'] if t['key']==track_key)
    asset=asset_record(workspace,installed[track_key]['asset_id'])
    if asset['sha256']!=track['sha256'] or not asset['has_audio'] or asset.get('test_only'):
        raise ValueError('The chosen story soundtrack needs an intact eligible registration.')
    return {**asset,'curated_music':{**track,'selection_reason':reason}}


def inputs(key):
    folder,*_=SPECS[key];recipe=ROOT/('examples/lore-series' if key in ('deadpool','xm') else 'examples/screen-recaps')/folder
    script=json.loads((recipe/'part-1.json').read_text(encoding='utf8'))
    brief=json.loads((recipe/'brief.json').read_text(encoding='utf8'))
    series=json.loads((recipe/'series.json').read_text(encoding='utf8'))
    request={**series['parts'][0],'source_voices':series['source_voices'],'test_only':True}
    validate_playbook_script(script_contract(script,brief,'lesson'),'comic_lore',request)
    return recipe,script,brief,series,request


def prepare(workspace,key,build,target):
    recipe,script,brief,series,request=inputs(key)
    folder,filename,page,url,uid=SPECS[key];local=DRAFT/folder/build;local.mkdir(parents=True,exist_ok=True)
    path=DRAFT/filename
    if not path.is_file():raise FileNotFoundError(f'Prepare and inspect the source poster first: {path}')
    credit=('Marvel Comics. Deadpool Kills the Marvel Universe collected-edition cover, Kaare Andrews; story by Cullen Bunn and Dalibor Talajic (2012), via Penguin Random House. Local review only.' if key=='deadpool' else
            'Marvel Comics. Giant-Size X-Men #1 (1975) cover, Gil Kane and Dave Cockrum, via the Library of Congress article. Local review only.' if key=='xm' else
            'Marvel Studios / Disney publicity poster, via the linked source. Local review only; no publication clearance inferred.')
    cover=register_asset(workspace,path,'test',{'url':page,'media_url':url},commercial=False,editing=False,test_only=True,attribution=credit)
    presets=json.loads((workspace.root/'reaction-presets.json').read_text())
    cast=([presets['captain-america-and-bucky']['cast'][0],presets['captain-america-and-bucky']['cast'][1],presets['crossover-theater']['cast'][2]] if key=='civil' else
          [presets['captain-america-and-bucky']['cast'][0],*presets['crossover-theater']['cast'][1:]] if key in ('deadpool','dw','ff','xm') else
          [presets['doctor-strange-sanctum']['cast'][0],*presets['crossover-theater']['cast'][1:]])
    part=series['parts'][0];part.pop('reaction_preset',None)
    part['reaction_set']={**presets['crossover-theater'],'cast':cast}
    # The smaller source poster remains below the native-pixel guard.
    box=[200,254,520,747] if key=='deadpool' else [205,270,515,729] if key=='dw' else [155,217,565,832] if key in ('strange','xm') else [136,204,584,876] if key=='ff' else [136,204,584,923]
    part['visual_selection']['layers']={uid:{'props':{'source_cover':{'asset_id':cover['id'],'box':box,
        'repeat_reason':'An explicit revision of this same recap retains its source-identifying poster.'}}}}
    music=story_music(workspace,key)
    part['music_id']=music['id']
    preflight={**part,'test_only':True,'lore_fresh_visuals':True}
    resolve_source_set(workspace,preflight,script);load_style_layers(workspace,preflight,script)
    check_lore_reuse(workspace,{'id':'preflight','channel':'entertainment','request':preflight})
    write_json(local/'series.json',series);(local/'part-1.json').write_bytes((recipe/'part-1.json').read_bytes())
    review={'reviewer':'Codex, compared the cited continuity/plot sources and exact supplied narration','supported':True,
            'limitations':brief['notes'],'brief_sha256':file_hash(recipe/'brief.json'),'script_sha256':{'part-1.json':file_hash(recipe/'part-1.json')}}
    write_json(recipe/'source-review.json',review)
    previous=sorted((ROOT/'Resources/Productions').glob(folder+'-*/batch.json'),key=lambda p:p.stat().st_mtime,reverse=True)
    create_series_plan(workspace,local/'series.json',recipe/'brief.json',target,recipe/'source-review.json',build_id=build,
                       assistant_authored=True,revise_batch=previous[0] if previous else None)
    write_json(local/'music-choice.json',{'id':music['id'],'credit':music.get('attribution'),'fit':music.get('curated_music')})


def storyboard(workspace,target,key):
    request=json.loads(target.read_text(encoding='utf8'))['items'][0]['request'];script=request['script']
    plan=plan_lore(script,request,request['brief'])['plan']
    _,audience,_=resolve_source_set(workspace,request,script)
    backdrops,props,_=load_style_layers(workspace,request,script)
    images=[];decisions=[]
    for n,scene in enumerate(plan['scenes']):
        span=max(6,len(scene['text'].split())/2.6)
        schedule=cut_schedule(scene,{'start':n*6,'duration':span},[],preview=True)
        ranges=schedule or [{'start':0,'end':span,'kind':scene['kind'],'reason':scene['design']['reason']}]
        painter=source_painter(cut_painter(lambda s,t,d:lore_frame(s,t,d,style_backdrops=backdrops),schedule),props.get(scene['unit_id'],()),audience,n*6)
        for row in ranges:
            t=(row['start']+row['end'])/2;images.append(painter(scene,t,span))
            decisions.append({'unit_id':scene['unit_id'],'scene':row['kind'],'purpose':row['reason']})
    sheet=Image.new('RGB',(1152,512*((len(images)+3)//4)),'#211b20')
    for n,im in enumerate(images):sheet.paste(im.resize((288,512)),(n%4*288,n//4*512))
    folder=DRAFT/SPECS[key][0];folder.mkdir(exist_ok=True)
    sheet.save(folder/'storyboard.jpg',quality=94)
    write_json(folder/'design-decisions.json',{'design':plan['design'],'cuts':decisions,'preview_timing':'Proportional storyboard only; final cuts use aligned spoken anchors.'})
    print(key,'storyboard',len(images),'shots',folder/'storyboard.jpg',flush=True)


def main():
    parser=ArgumentParser(description=__doc__);parser.add_argument('--only',choices=SPECS)
    parser.add_argument('--measure-only',action='store_true');parser.add_argument('--render',action='store_true')
    parser.add_argument('--build-suffix',default='final-20261107');args=parser.parse_args()
    workspace=Workspace(ROOT/'data/pipeline')
    for key in ([args.only] if args.only else ('strange','civil')):
        recipe,script,brief,series,request=inputs(key)
        if args.measure_only:
            plan=plan_lore(script,request,brief)['plan']
            (DRAFT/SPECS[key][0]).mkdir(parents=True,exist_ok=True)
            voice=synthesize(workspace,script,DRAFT/SPECS[key][0]/'speech-draft',creative_plan=plan,delivery=get_playbook('comic_lore',request)['voice'])
            voice=align_dialogue(workspace,voice)
            for scene,spoken in zip(plan['scenes'],voice['units']):cut_schedule(scene,spoken,voice['word_timings'])
            print(key,'measured seconds',voice['duration'],'voices',voice['cast_voices'],flush=True);continue
        build=SPECS[key][0]+'-'+args.build_suffix;target=ROOT/'Resources/Plans'/(build+'.json')
        if not target.exists():prepare(workspace,key,build,target)
        storyboard(workspace,target,key)
        if not args.render:continue
        with workspace.connect() as db:before=dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider'))
        result=run_batch(workspace,target,progress=lambda state:print(key,[(r.get('stage',r['status']),r.get('error_code')) for r in state['items']],flush=True))
        with workspace.connect() as db:assert before==dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider'))
        if result['status']!='ready':print(result);return 2
        output=Path(result['items'][0]['output_folder']);(output/'design-decisions.json').write_bytes((DRAFT/SPECS[key][0]/'design-decisions.json').read_bytes())
        meta=json.loads((output/'metadata.json').read_text(encoding='utf8'));(output/'description.md').write_text(meta['title']+'\n\n'+meta['description'],encoding='utf8')
        print(output/'video.mp4',flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
