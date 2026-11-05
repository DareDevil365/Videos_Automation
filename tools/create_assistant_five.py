"""Build the owner's five assistant-authored reviews through the existing toolbox.

No remote text/image/video generation. Inputs are the checked local stock/art
manifest and committed original scripts. State and exports are resumable.
"""
from copy import deepcopy
import argparse
import json
from pathlib import Path
import sys
import subprocess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset
from yt_pipeline.batches import _copy_outputs
from yt_pipeline.core import Workspace,digest,file_hash
from yt_pipeline.pipeline import Pipeline


class ClosedProvider:
    name='prepared_by_assistant'
    origin='assistant_authored_at_owner_request'
    def __init__(self,plan):self.plan=plan
    def generate(self,purpose,*args,**kwargs):
        if purpose!='creative-director-v1' or self.plan is None:
            raise RuntimeError('Remote generation forbidden in this batch: '+purpose)
        return deepcopy(self.plan)


def base_request(script):
    return {'script':script,'fiction':True,'test_only':True,'visual_review':'off','editorial_review':'off',
        'hook_options':False,'require_music':False,'bottom_kind':'none',
        'brief':{'title':script['title'],'question':script['hook'],'kind':'fiction','claims':[],'sources':[],
                 'notes':'Original assistant-authored fiction/edit captions at the owner request. Not a Gemini-generated script or independent model verdict.'}}


def plan_for(script,template,media):
    return {'version':1,'template':template,'cast':[{'id':'n','speaker':script['units'][0]['speaker'],'role':'voice-only narrator' if template=='illustrated_story' else 'edit captions',
        'avatar_kind':'narrator','avatar_query':'','voice_id':'af_heart','costume':''}],
        'scenes':[{'unit_id':u['id'],'text':u['text'],'speaker_id':'n','stage':'hook' if i==0 else 'payoff' if i==len(script['units'])-1 else 'setup',
                   'background_query':'permitted illustrative art' if template=='illustrated_story' else 'actual basketball practice',
                   'visual_query':'registered source scene','asset_id':ref,'visible_cast':[],'focus_id':'',
                   'framing':'wide','motion':'slow_push' if template=='illustrated_story' else 'hold','emotion':'calm',
                   'pause_after':.24,'sound_cue':'none','rank':0,'display_title':''} for i,(u,ref) in enumerate(zip(script['units'],media))],
        'music_mood':'none','opening_promise':script['hook'],'delivered_payoff':script['payoff'],'comment_question':'',
        'review':{**{k:True for k in ('payoff_delivered','hook_honest','no_invented_evidence','continuity_consistent')},'issues':[]}}


def register_inputs(ws,folder):
    state=folder/'registered-inputs.json'
    if state.exists():
        result=json.loads(state.read_text(encoding='utf-8'))
        if 'freeze' not in result:
            from yt_pipeline.assets import asset_record
            source=asset_record(ws,result['video'][2]);image=folder/'media/aura-peak.png'
            subprocess.run(['ffmpeg','-v','error','-y','-ss','8.7','-i',source['path'],'-frames:v','1',str(image)],check=True)
            result['freeze']=register_asset(ws,image,'licensed_stock',{'source_asset_id':source['id'],'operation':'Freeze the actual dunk at 8.7 seconds','source_url':'https://mixkit.co/free-stock-video/basketball-player-dribbling-then-dunking-2285/','license':'Mixkit Stock Video Free License','license_url':'https://mixkit.co/license/#videoFree'},test_only=True)['id']
            write_json(state,result)
        if 'story_music' not in result:
            music=folder/'media/story-piano.mp3'
            if not music.is_file():raise RuntimeError('Prepare permitted Beautiful Dream piano soundtrack before this batch.')
            result['story_music']=register_asset(ws,music,'licensed_stock',{'title':'Beautiful Dream','artist':'Diego Nava','source_url':'https://mixkit.co/free-stock-music/piano/','license':'Mixkit Stock Music Free License','license_url':'https://mixkit.co/license/#musicFree'},attribution='Beautiful Dream by Diego Nava, Mixkit',test_only=True)['id']
            write_json(state,result)
        return result
    arts=json.loads((folder/'media/art-sources.json').read_text(encoding='utf-8'))
    videos=json.loads((folder/'media/stock-video-sources.json').read_text(encoding='utf-8'))
    gif=json.loads((folder/'media/gif-source.json').read_text(encoding='utf-8'))
    result={'art':[register_asset(ws,a['file'],'licensed_stock',a,test_only=True)['id'] for a in arts],
            'video':[register_asset(ws,a['file'],'licensed_stock',a,test_only=True)['id'] for a in videos],
            'gif':register_asset(ws,gif['file'],'licensed_stock',gif,test_only=True)['id'],
            'music':register_asset(ws,folder/'media/aura-beat.mp3','licensed_stock',{
                'title':'C.B.P.D','artist':'Arulo','source_url':'https://mixkit.co/free-stock-music/trap/',
                'download_url':'https://assets.mixkit.co/music/400/400.mp3','license':'Mixkit Stock Music Free License',
                'license_url':'https://mixkit.co/license/#musicFree'},attribution='C.B.P.D by Arulo, Mixkit Stock Music Free License',test_only=True)['id']}
    write_json(state,result);return register_inputs(ws,folder)


def run_one(ws,name,inputs,output,revision=False):
    script=json.loads((ROOT/'examples/assistant-five'/(name+'.json')).read_text(encoding='utf-8'))
    request=base_request(script);plan=None
    if name.endswith('-chat'):
        request.update(playbook='server_chat',chat_editing_version=2,chat_writing_version=2,chat_script_review=False,
                       chat_tone='comedy' if name=='comedy-chat' else 'mystery' if name=='mystery-chat' else 'story')
        if script.get('phone_story'):request['phone_story']=True
        if name=='comedy-chat':request.update(chat_attachment_ids={'u8':inputs['gif']},chat_group_name='People I Pretend To Listen To')
    elif name=='cinematic-story':
        request.update(render_revision=3,music_id=inputs['story_music'],playbook='illustrated_story',story_canvas='portrait',allow_licensed_illustrations=True,
                       visual_asset_ids=inputs['art'])
        sequence=[4,0,2,5,0,4,3,1,2,1,4,3]
        plan=plan_for(script,'illustrated_story',[inputs['art'][i] for i in sequence])
        request['illustration_reuse']={u['id']:'Continue the same fictional room, journey or conversation; this closer view develops the established story rather than introducing an unrelated scene.' for u in script['units']}
        request['illustration_effects']={
            'u2':{'crop_start':[0,0,.8,1],'crop_end':[0,.02,.73,.98]},
            'u4':{'crop_start':[0,0,1,1],'crop_end':[.04,.04,.96,.96]},
            'u5':{'inset_asset_id':inputs['art'][5],'inset_box':[.489,.117,.594,.209],
                  'crop_start':[.35,.02,.75,.50],'crop_end':[.38,.04,.70,.47]},
            'u6':{'crop_start':[.1,.05,.95,1],'crop_end':[.15,.08,.9,.98]},
            'u7':{'crop_start':[.14,.12,.92,1],'crop_end':[.17,.15,.89,.97]},
            'u10':{'crop_start':[0,0,1,1],'crop_end':[.06,.04,.96,.94]},
            'u11':{'crop_start':[.06,.02,.96,.98],'crop_end':[.13,.06,.90,.96]},
            'u12':{'crop_start':[.08,.10,.92,.98],'crop_end':[0,0,1,1]}}
    else:
        sequence=[inputs['video'][0],inputs['video'][1],inputs['video'][3],inputs['video'][2],inputs['video'][2],inputs['freeze']]
        plan=plan_for(script,'aura_progression',sequence)
        request.update(render_revision=3,playbook='aura_progression',visual_asset_ids=inputs['video']+[inputs['freeze']],music_id=inputs['music'],
                       require_music=True,aura_clean=True,shot_durations={f'u{i+1}':d for i,d in enumerate([2.5,2.4666667,2.5,2.4666667,2.0,1.6666667])},
                       media_starts={'u1':0,'u2':1,'u3':0,'u4':2.5,'u5':6.7,'u6':0})
    folder=output/name;folder.mkdir(parents=True,exist_ok=True);state=folder/'assistant-state.json'
    version=digest([script,request,plan])
    if state.exists():
        saved=json.loads(state.read_text(encoding='utf-8'))
        if saved['version']!=version:
            if not revision:raise RuntimeError('Inputs changed; use --revision for an explicit test-only revision of '+name)
            write_json(folder/('assistant-state-'+saved['version'][:8]+'.json'),saved)
            request['prototype_revision_of']=saved['job_id']
            job=ws.create('entertainment',request)
            write_json(state,{'version':version,'job_id':job['id'],'author':'assistant at owner request','direction':plan,'revises_job':saved['job_id']})
        else:job=ws.get(saved['job_id'])
    else:
        job=ws.create('entertainment',request)
        write_json(state,{'version':version,'job_id':job['id'],'author':'assistant at owner request','direction':plan})
    with ws.connect() as db:before=dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider').fetchall())
    result=Pipeline(ws,provider=ClosedProvider(plan)).run(job['id'])
    if result['status']!='ready':
        return {'name':name,'status':result['status'],'job_id':job['id'],'error':result.get('error_code'),'message':result.get('message')}
    exports=_copy_outputs(ws,result,folder)
    with ws.connect() as db:after=dict(db.execute('SELECT provider,SUM(calls) FROM usage GROUP BY provider').fetchall())
    if before!=after:raise RuntimeError('Unexpected provider usage during the closed assistant build.')
    qa=json.loads((folder/'quality.json').read_text(encoding='utf-8'))
    validation={'job_id':job['id'],'script_origin':'assistant-authored provided_script','director_origin':ClosedProvider.origin,
        'gemini_calls_used':0,'openai_calls_used':0,'visual_generation_calls':0,'width':qa['width'],'height':qa['height'],
        'duration':qa['duration'],'technical_pass':qa['technical_pass'],'sha256':file_hash(folder/'video.mp4'),
        'test_only':True,'limits':'Assistant-authored creative review, not autonomous Gemini quality or owner approval. Historical paintings are illustrative; stock athletes are different people.'}
    write_json(folder/'AUTHORING_AND_VALIDATION.json',validation)
    (folder/'SCRIPT.md').write_text('# '+script['title']+'\n\nOriginal assistant-authored script at the owner request.\n\n'+'\n\n'.join(u['speaker']+': '+u['text'] for u in script['units'])+'\n',encoding='utf-8')
    return {'name':name,'status':'ready','video':str(folder/'video.mp4'),'validation':validation}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--only',choices=['comedy-chat','mystery-chat','story-chat','cinematic-story','aura'])
    parser.add_argument('--revision',action='store_true');args=parser.parse_args();ws=Workspace(ROOT/'data/pipeline');output=ROOT/'Resources/Productions/assistant-five-20261105'
    inputs=register_inputs(ws,ROOT/'Resources/Drafts/assistant-five-20261105');results=[]
    for name in ([args.only] if args.only else ['comedy-chat','mystery-chat','story-chat','cinematic-story','aura']):
        print(json.dumps({'event':'starting','name':name}),flush=True)
        result=run_one(ws,name,inputs,output,args.revision);results.append(result);print(json.dumps(result),flush=True)
    merged={r['name']:r for r in results}
    for name in ('comedy-chat','mystery-chat','story-chat','cinematic-story','aura'):
        folder=output/name;proof=folder/'AUTHORING_AND_VALIDATION.json'
        if name not in merged and proof.exists():
            validation=json.loads(proof.read_text(encoding='utf-8'))
            if (folder/'video.mp4').is_file() and file_hash(folder/'video.mp4')==validation['sha256']:
                merged[name]={'name':name,'status':'ready','video':str(folder/'video.mp4'),'validation':validation}
    write_json(output/'BATCH_REVIEW.json',list(merged.values()))
    return 0 if all(r['status']=='ready' for r in results) else 2


if __name__=='__main__':raise SystemExit(main())
