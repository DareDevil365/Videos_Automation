"""Offline technical rewrite pilot using prepared public evidence and local speech.

No Gemini request or channel upload is made. The prepared scene plan is explicitly
attributed as an offline fixture, never a live model judgement.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))

from shorts_editor.store import write_json
from yt_pipeline.core import Workspace,digest,file_hash
from yt_pipeline.contracts import brief_contract
from yt_pipeline.pipeline import Pipeline
from yt_pipeline.batches import _copy_outputs


def prepared_episode():
    lines=[
        ('This interview answer hides the work you actually did.','Show your actual contribution'),
        ('Here is a hypothetical practice answer: I helped my team during a busy shift.','I helped my team'),
        ('That sounds positive, but it gives no concrete action a listener can picture.','Name a concrete action'),
        ('Try this example instead: I checked the receipts against the delivery list.','I checked the receipts'),
        ('The improved answer names your action and the material you checked, without inventing a result.','Action and material'),
        ('Use your real experience. Explain what you personally did, then describe the actual result.','Use your real experience')]
    units=[{'id':f'u{i+1}','speaker':'Narrator','text':text,'onscreen':caption,
            'kind':'instruction','claim_ids':[],'visual_query':'original explanatory typography'} for i,(text,caption) in enumerate(lines)]
    script={'version':1,'title':'Show your contribution in an interview answer',
            'description':'Original hypothetical practice wording; a technical local speech/graphics demonstration, not hiring advice or an outcome guarantee.',
            'format':'lesson','fiction':False,'hook':lines[0][0],'payoff':lines[-1][0],'units':units,
            'edit':{'effect':'none','payoff_unit_id':'u6','cta':False}}
    scenes=[{'unit_id':unit['id'],'text':unit['text'],'speaker_id':'n','stage':'hook' if i==0 else 'payoff' if i==5 else 'setup',
             'background_query':'original explanatory typography','visual_query':'actual supplied phrase','asset_id':'',
             'visible_cast':[],'focus_id':'','framing':'wide','motion':'hold','emotion':'calm','pause_after':.1,
             'sound_cue':'none','rank':0,'display_title':'',
             'graphic':{'kind':'callout','title':'Example','labels':[unit['onscreen']]}} for i,unit in enumerate(units)]
    scenes[3]['graphic']={'kind':'comparison','title':'Before and After','headings':['Before','After'],
                          'labels':['I helped my team','I checked the receipts']}
    scenes[5]['speech_segments']=[{'text':'Use your real experience.','pause_after':.35,'speed':1.},
                                  {'text':'Explain what you personally did, then describe the actual result.','pause_after':0,'speed':1.05}]
    plan={'version':1,'template':'education_demo','cast':[{'id':'n','speaker':'Narrator','role':'narrator','avatar_kind':'narrator',
           'avatar_query':'','voice_id':'am_adam','costume':''}], 'scenes':scenes,'music_mood':'none',
          'opening_promise':lines[0][0],'delivered_payoff':lines[-1][0],'comment_question':'',
          'review':{'payoff_delivered':True,'hook_honest':True,'no_invented_evidence':True,'continuity_consistent':True,'issues':[]}}
    return script,plan


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',default=str(ROOT/'data/pipeline'))
    parser.add_argument('--brief',default=str(ROOT/'Resources/Productions/repo-upgrade-final-2026-11-02/interview-before-after/research.json'))
    parser.add_argument('--output',default=str(ROOT/'Resources/Productions/editorial-rewrite-demo'))
    args=parser.parse_args()
    source=Path(args.brief)
    if not source.is_file():parser.error('Supply an existing prepared public-source brief with --brief; no source is fetched by this tool.')
    evidence=brief_contract(json.loads(source.read_text(encoding='utf-8-sig')))
    # The original hypothetical exercise and scene plan are prepared by this tool;
    # this is an explicitly provided editorial fixture, not a model approval.
    evidence['editorial_verified']=True
    evidence['notes']+=' Technical fixture: manually prepared original instructional example; no live model/source review is claimed.'
    script,plan=prepared_episode()
    request={'playbook':'rewrite_reveal','brief':evidence,'script':script,'test_only':True,
             'visual_review':'off','editorial_review':'off','hook_options':False,'require_music':False}
    output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=True)
    state_path=output/'demo-state.json';ws=Workspace(args.root)
    version=digest([request,plan,file_hash(source)])
    if state_path.exists():
        state=json.loads(state_path.read_text(encoding='utf-8'))
        if state['version']!=version:raise ValueError('Demo inputs changed; choose a fresh output directory instead of changing an initialized demonstration.')
        job=ws.get(state['job_id'])
    else:
        job=ws.create('education',request);write_json(state_path,{'job_id':job['id'],'version':version})
    class PreparedPlan:
        origin='offline_prepared_fixture'
        def generate(self,purpose,*unused,**kwargs):
            if purpose!='creative-director-v1':raise ValueError('This offline demo cannot make model calls: '+purpose)
            return deepcopy(plan)
    with ws.connect() as db:before=db.execute("SELECT COALESCE(SUM(calls),0) FROM usage WHERE provider='gemini'").fetchone()[0]
    result=Pipeline(ws,provider=PreparedPlan()).run(job['id'])
    if result['status']!='ready':
        print(json.dumps({'status':result['status'],'job_id':job['id'],'error_code':result['error_code'],'message':result['message']}))
        return 2
    exported=_copy_outputs(ws,result,output)
    with ws.connect() as db:after=db.execute("SELECT COALESCE(SUM(calls),0) FROM usage WHERE provider='gemini'").fetchone()[0]
    timing=json.loads((ws.job_dir(job['id'])/'voice.json').read_text(encoding='utf-8'))
    check={'job_id':job['id'],'duration':timing['duration'],'spoken_words':sum(len(u['text'].split()) for u in script['units']),
           'aligned_words':len(timing.get('word_timings',[])), 'gemini_calls_used':after-before,
           'script_origin':'provided original example','director_origin':'offline_prepared_fixture',
           'test_only':True,'internal_pause_seconds':.35,
           'limits':['No live hook generation or independent editorial/frame model review.',
                     'Prepared public-source excerpt reused without a fresh network check.',
                     'Technical demonstration, not owner-approved style or hiring/audience evidence.']}
    write_json(output/'demo-validation.json',check)
    print(json.dumps({'status':'ready','output':str(output),'validation':check,'exports':exported},default=str))
    return 0


if __name__=='__main__':raise SystemExit(main())
