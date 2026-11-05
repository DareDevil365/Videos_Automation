"""Build two reviewed local source Shorts using the normal resumable batch."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from shorts_editor.store import write_json
from yt_pipeline.batches import run_batch
from yt_pipeline.core import Held,Workspace,now
from yt_pipeline.curated_music import select_genre_music


def make_plan(ws,plan_path,revise_batch=None):
    items=[]
    ancestors={}
    if revise_batch:
        old=json.loads(Path(revise_batch).read_text(encoding='utf-8'))
        for item in old['items']:
            job=ws.get(item['job_id'])
            if not job['request'].get('test_only') or job['request'].get('playbook') not in ('movie_brief','current_affairs'):
                raise Held('pilot_revision','Use a test-only source-short ancestor.')
            ancestors[item['id']]=job['id']
    for name,category,stem,channel in (
        ('doomsday-context','movie_brief','movie-content/doomsday-actor-character','entertainment'),
        ('india-nz-trade','current_affairs','current-affairs/india-nz-fta','education')):
        source=ROOT/'examples'/stem
        script=json.loads(source.with_suffix('.script.json').read_text(encoding='utf-8'))
        brief=json.loads(source.with_suffix('.brief.json').read_text(encoding='utf-8'))
        def callout(index,title):return {'kind':'callout','title':title,'labels':[script['units'][index-1]['onscreen']]}
        graphics={}
        if category=='movie_brief':
            graphics={'u2':callout(2,'DOOMSDAY'),
                'u4':{'kind':'process','title':'DOOM','labels':['Latveria','sorcery','technology']},
                'u5':{'kind':'process','title':'ONE MOVIE FOR CONTEXT','labels':['First Steps','Fantastic Four']},
                'u7':callout(7,'OPTIONAL, NOT HOMEWORK')}
        else:
            graphics={'u2':callout(2,'FREE TRADE AGREEMENT'),
                'u5':{'kind':'process','title':'EXPORT COVERAGE ≠ TARIFF LINE COUNT','labels':['Almost 57% at launch','including dairy']},
                'u6':{'kind':'process','title':'CHECK THE DIRECTION AND ORIGIN','labels':['Rules of origin','which goods qualify']},
                'u8':callout(8,'ZERO DUTY BOTH WAYS?')}
        request={'script':script,'brief':brief,'brief_graphics':graphics,'fiction':False,'test_only':True,'motion_graphics':True,
                 'hook_options':False,'editorial_review':'off','visual_review':'off','bottom_kind':'none','require_music':True,
                 'music_id':select_genre_music(ws,'cinematic',selection_key=name)['id'],'auto_publish':False}
        from yt_pipeline.brief_visuals import MODES
        request['brief_motifs']={u['id']:mode for u,mode in zip(script['units'],MODES[category])}
        if name in ancestors:request['prototype_revision_of']=ancestors[name]
        items.append({'id':name,'kind':'playbook','playbook':category,'channel':channel,'topic':script['title'],'request':request})
    plan={'version':1,'id':plan_path.stem,'created_at':now(),'output_root':str(ROOT/'Resources/Productions'),
          'note':'Provided source-aware scripts and original local graphics. Test-only; no public uploads.', 'items':items}
    plan_path.parent.mkdir(parents=True,exist_ok=True);write_json(plan_path,plan)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--plan',default=str(ROOT/'Resources/Plans/source-short-pilots-20261106-v3.json'));parser.add_argument('--plan-only',action='store_true');parser.add_argument('--revise-batch');args=parser.parse_args()
    ws=Workspace(ROOT/'data/pipeline');plan=Path(args.plan).resolve()
    if not plan.exists():make_plan(ws,plan,args.revise_batch)
    if args.plan_only:print(str(plan));return 0
    with ws.connect() as db:before=dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider'))
    def progress(state):
        print(json.dumps({'state':state['status'],'items':[{k:r.get(k) for k in ('id','status','error_code','message','video')} for r in state['items']]}),flush=True)
    result=run_batch(ws,plan,progress=progress)
    with ws.connect() as db:after=dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider'))
    if after!=before:raise Held('pilot_provider_usage','Provider usage changed during the supplied-source pilot run.')
    return 0 if result['status']=='ready' else 2


if __name__=='__main__':raise SystemExit(main())
