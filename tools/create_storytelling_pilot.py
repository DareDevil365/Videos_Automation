"""Owner-requested assistant-authored story. Never calls a remote text model."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset
from yt_pipeline.batches import _copy_outputs
from yt_pipeline.contracts import brief_contract
from yt_pipeline.core import Workspace,digest,file_hash
from yt_pipeline.pipeline import Pipeline


def prepare(script,assets):
    ids=['01','02','01','02','03','03','04','04','04','05','05','05','06','06']
    scenes=[{'unit_id':u['id'],'text':u['text'],'speaker_id':'n','stage':'hook' if i==0 else 'payoff' if i==13 else 'clue' if i in (2,4,10) else 'setup',
        'background_query':'original lighthouse story','visual_query':'original scene illustration','asset_id':assets[key],
        'visible_cast':[],'focus_id':'','framing':'wide','motion':'slow_push','emotion':'calm','pause_after':.28,
        'sound_cue':'none','rank':0,'display_title':''} for i,(u,key) in enumerate(zip(script['units'],ids))]
    scenes[2]['pause_after']=.55;scenes[5]['pause_after']=.65;scenes[12]['pause_after']=.5
    plan={'version':1,'template':'illustrated_story','cast':[{'id':'n','speaker':'Narrator','role':'voice-only narrator',
        'avatar_kind':'narrator','avatar_query':'','voice_id':'af_heart','costume':''}],
        'scenes':scenes,'music_mood':'none','opening_promise':script['hook'],'delivered_payoff':script['payoff'],'comment_question':'',
        'review':{**{k:True for k in ('payoff_delivered','hook_honest','no_invented_evidence','continuity_consistent')},'issues':[]}}
    window=[.834,.407,.851,.440]
    effects={'u1':{'rain':True,'flash_box':window},
        'u2':{'crop_start':[0,0,1,1],'crop_end':[0,0,.93,.93]},
        'u3':{'rain':True,'crop_start':[.53,.18,.99,.64],'crop_end':[.58,.22,.98,.62],'flash_box':window,
            'callout_box':window,'target':'ground-floor window'},
        'u4':{'crop_start':[0,.02,.79,.81],'crop_end':[.02,.04,.76,.78]},
        'u5':{'crop_start':[.43,.23,1,.80],'crop_end':[.46,.26,.98,.78]},
        'u6':{'crop_start':[.43,.07,1,.64],'crop_end':[.45,.07,.97,.59]},
        'u7':{'crop_start':[0,0,1,1],'crop_end':[.015,.015,.985,.985]},
        'u8':{'crop_start':[0,.2,.62,.82],'crop_end':[0,.22,.59,.81]},
        'u9':{'crop_start':[.02,.04,.98,1],'crop_end':[0,0,1,1]},
        'u10':{'crop_start':[0,0,1,1],'crop_end':[.03,.03,.97,.97]},
        'u11':{'crop_start':[.27,.35,.91,.99],'crop_end':[.29,.37,.89,.97],
            'flash_box':[.438,.651,.525,.844]},
        'u12':{'crop_start':[.04,.04,.96,.96],'crop_end':[0,0,1,1]},
        'u13':{'crop_start':[0,0,1,1],'crop_end':[.02,.02,.98,.98]},
        'u14':{'crop_start':[.02,.02,.98,.98],'crop_end':[.055,.055,.945,.945]}}
    reuse={u['id']:'Continue the same rescue location and character interaction, with a distinct closer/reverse camera crop.' for u in script['units']}
    reuse['u3']='Revisit the established lighthouse for the actual low-window clue, now tightly reframed and flashing.'
    reuse['u4']='Return to Mara after the clue insert to show her reaction in the same continuous scene.'
    reuse['u11']='Move closer to the same lantern and muddy paw to explain the already-planted flashing clue.'
    reuse['u12']='Hold the lantern/dog explanation until its causal connection to the rescue has been delivered.'
    reuse['u14']='Continue the dawn reunion for the resolved closing line, with a gentle final push toward the group.'
    brief=brief_contract({'title':script['title'],'question':'Who is making the low window flash, and why?',
        'kind':'fiction','sources':[],'claims':[],'notes':'Original assistant-authored fiction at the owner\'s explicit request; no model self-review is claimed.'})
    request={'playbook':'illustrated_story','brief':brief,'script':script,'test_only':True,'visual_review':'off','editorial_review':'off',
        'hook_options':False,'require_music':False,'bottom_kind':'none','visual_asset_ids':list(assets.values()),
        'illustration_effects':effects,'illustration_reuse':reuse}
    return request,plan


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',default=str(ROOT/'data/pipeline'))
    parser.add_argument('--art',required=True,help='Directory containing original 01.png through 06.png and prompts.json')
    parser.add_argument('--output',default=str(ROOT/'Resources/Productions/the-last-light-20261105'))
    args=parser.parse_args();ws=Workspace(args.root);art=Path(args.art).resolve();output=Path(args.output).resolve()
    script=json.loads((ROOT/'examples/storytelling-last-light.json').read_text(encoding='utf-8'))
    files=[art/(f'{i:02d}.png') for i in range(1,7)]
    if any(not f.is_file() for f in files):parser.error('All six original artwork files must exist before starting.')
    prompts=json.loads((art/'prompts.json').read_text(encoding='utf-8'))
    output.mkdir(parents=True,exist_ok=True);state_path=output/'story-state.json'
    version=digest([script,[file_hash(f) for f in files],prompts])
    if state_path.exists():
        saved=json.loads(state_path.read_text(encoding='utf-8'))
        if saved['version']!=version:raise ValueError('Story/art inputs changed. Choose a new output directory.')
        job=ws.get(saved['job_id']);plan=saved['direction']
    else:
        assets={f'{i:02d}':register_asset(ws,f,'original_graphic',{'generator':'built-in imagegen','synthetic':True,
            'prompt':prompts[f'{i:02d}'],'purpose':'Original assistant-directed fictional story scene'},test_only=True)['id'] for i,f in enumerate(files,1)}
        request,plan=prepare(script,assets);job=ws.create('entertainment',request)
        write_json(state_path,{'version':version,'job_id':job['id'],'direction':plan,'author':'assistant at owner request'})
    class PreparedDirection:
        origin='assistant_authored_at_owner_request'
        def generate(self,purpose,*args,**kwargs):
            if purpose!='creative-director-v1':raise RuntimeError('No remote model is allowed for this run: '+purpose)
            return deepcopy(plan)
    with ws.connect() as db:before=db.execute("SELECT COALESCE(SUM(calls),0) FROM usage WHERE provider='gemini'").fetchone()[0]
    result=Pipeline(ws,provider=PreparedDirection()).run(job['id'])
    if result['status']!='ready':
        print(json.dumps({'status':result['status'],'job_id':job['id'],'code':result['error_code'],'message':result['message']}));return 2
    exports=_copy_outputs(ws,result,output)
    with ws.connect() as db:after=db.execute("SELECT COALESCE(SUM(calls),0) FROM usage WHERE provider='gemini'").fetchone()[0]
    timing=json.loads((output/'voice.json').read_text(encoding='utf-8'))
    validation={'job_id':job['id'],'script_origin':'assistant-authored provided_script','director_origin':PreparedDirection.origin,
        'gemini_calls_used':after-before,'duration':timing['duration'],'artwork_count':6,'shot_count':len(script['units']),
        'aligned_words':len(timing.get('word_timings',[])),'test_only':True,
        'limits':['No independent model review; owner explicitly requested assistant-authored direction.',
            'Illustrations use source-camera/weather/light motion; no character rigs or lip-sync.']}
    if after!=before:raise RuntimeError('Unexpected remote text-model usage detected.')
    write_json(output/'story-validation.json',validation)
    (output/'SCRIPT.md').write_text('# The Last Light\n\nOriginal fiction. Written and directed by the assistant at the owner\'s request.\n\n'+'\n\n'.join(u['text'] for u in script['units']),encoding='utf-8')
    (output/'ART_PROMPTS.json').write_text(json.dumps(prompts,indent=2),encoding='utf-8')
    print(json.dumps({'status':'ready','output':str(output),'validation':validation,'exports':exports}));return 0


if __name__=='__main__':raise SystemExit(main())
