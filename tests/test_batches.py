"""Batch control boundaries: no live model, media generation or account access."""
import json
from pathlib import Path
import threading

import pytest

from shorts_editor.store import write_json
from yt_pipeline import batches
from yt_pipeline.core import Workspace,Held,file_hash,digest


@pytest.fixture
def setup(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'workspace')
    plan=tmp_path/'plan.json'
    write_json(plan,{'version':1,'id':'test-batch','output_root':str(tmp_path/'outputs'),
                     'items':[{'id':'mystery-one','kind':'mystery'},{'id':'mystery-two','kind':'mystery'}]})
    counts={'created':0,'ran':0}
    def create(ws,spec,folder,resources,token=None):
        counts['created']+=1
        return ws.create('entertainment',{'topic':spec['id'],'batch_item_token':token})
    class Production:
        def __init__(self,ws):self.ws=ws
        def run(self,id):
            counts['ran']+=1;folder=self.ws.job_dir(id);video=folder/'render.mp4';video.write_bytes(b'a stable technical fixture, not real media')
            (folder/'cover.png').write_bytes(b'cover');(folder/'captions.srt').write_text('fixture captions')
            write_json(folder/'manifest.json',{'test_fixture':True})
            write_json(folder/'script.json',{'origin':'fixture','script':{'units':[]}})
            write_json(folder/'quality.json',{'duration':3,'video_sha256':file_hash(video)})
            write_json(folder/'render.json',{'video':str(video),'cover':str(folder/'cover.png'),'captions':str(folder/'captions.srt'),'manifest':str(folder/'manifest.json')})
            self.ws.update(id,status='ready',stage='ready',message='Fixture complete',artifacts={'render':{'path':str(folder/'render.json')}})
            return self.ws.get(id)
    monkeypatch.setattr(batches,'_create_job',create);monkeypatch.setattr(batches,'Pipeline',Production)
    return ws,plan,counts


def test_resuming_ready_batch_never_creates_or_runs_jobs_again(setup):
    ws,plan,counts=setup
    first=batches.run_batch(ws,plan);second=batches.run_batch(ws,plan)
    assert first['status']==second['status']=='ready'
    assert counts=={'created':2,'ran':2}
    assert [i['job_id'] for i in first['items']]==[i['job_id'] for i in second['items']]
    assert all(i['output_hashes'] for i in second['items'])


def test_stop_before_start_and_between_completed_videos(setup,tmp_path):
    ws,plan,counts=setup;stop=tmp_path/'stop';stop.touch()
    paused=batches.run_batch(ws,plan,stop_file=stop)
    assert paused['status']=='paused' and counts['created']==0
    stop.unlink()
    def progress(m):
        if m['items'][0]['status']=='ready':stop.touch()
    paused=batches.run_batch(ws,plan,stop_file=stop,progress=progress)
    assert paused['status']=='paused' and counts=={'created':1,'ran':1}
    stop.unlink();complete=batches.run_batch(ws,plan,stop_file=stop)
    assert complete['status']=='ready' and counts=={'created':2,'ran':2}


def test_status_reconciles_pipeline_and_detects_tampered_copy(setup):
    ws,plan,counts=setup
    complete=batches.run_batch(ws,plan)
    Path(complete['items'][0]['video']).write_bytes(b'changed Resources copy')
    status=batches.batch_status(ws,plan)
    assert status['status']=='waiting' and status['items'][0]['status']=='export_pending'
    restored=batches.run_batch(ws,plan)
    assert restored['status']=='ready' and counts=={'created':2,'ran':2}
    first=restored['items'][0]
    ws.update(first['job_id'],status='held',stage='render',message='Changed externally')
    status=batches.batch_status(ws,plan)
    assert status['status']=='waiting' and status['items'][0]['status']=='held'


def test_concurrent_start_cannot_create_duplicate_jobs(setup,monkeypatch):
    ws,plan,counts=setup;entered=threading.Event();release=threading.Event();original=batches._create_job;errors=[]
    def create(*a,**kw):entered.set();release.wait(10);return original(*a,**kw)
    monkeypatch.setattr(batches,'_create_job',create)
    def run():
        try:batches.run_batch(ws,plan)
        except Exception as exc:errors.append(exc)
    worker=threading.Thread(target=run);worker.start();assert entered.wait(5)
    try:
        with pytest.raises(Held) as exc:batches.run_batch(ws,plan)
        assert exc.value.code=='worker_busy'
    finally:release.set();worker.join(10)
    assert not errors and counts=={'created':2,'ran':2}


def test_crash_between_job_creation_and_manifest_save_recovers_existing_job(setup):
    ws,plan,counts=setup
    manifest=batches.prepare_batch(ws,plan);_,_,_,manifest_path=batches._paths(plan)
    token=digest([str(manifest_path),manifest['plan_sha256'],'mystery-one'])
    orphan=ws.create('entertainment',{'topic':'first','batch_item_token':token})
    result=batches.run_batch(ws,plan)
    assert result['items'][0]['job_id']==orphan['id']
    assert counts=={'created':1,'ran':2}


def test_changed_pipeline_checkpoint_cannot_be_reexported_as_verified(setup):
    ws,plan,counts=setup
    result=batches.run_batch(ws,plan);job=ws.get(result['items'][0]['job_id'])
    render=Path(job['artifacts']['render']['path']);artifacts=job['artifacts']
    artifacts['render']['sha256']=file_hash(render);ws.update(job['id'],artifacts=artifacts)
    render.write_text('{}')
    status=batches.batch_status(ws,plan)
    assert status['items'][0]['status']=='export_pending'
    retried=batches.run_batch(ws,plan)
    assert retried['items'][0]['error_code']=='batch_artifact_changed'
    assert counts=={'created':2,'ran':2}


def test_plan_mutation_or_missing_selected_plan_is_not_silently_replaced(setup,tmp_path):
    ws,plan,_=setup;batches.prepare_batch(ws,plan)
    value=json.loads(plan.read_text());value['items'][0]['id']='different';write_json(plan,value)
    with pytest.raises(Held) as exc:batches.prepare_batch(ws,plan)
    assert exc.value.code=='batch_plan_changed'
    missing=tmp_path/'misspelled.json'
    with pytest.raises(ValueError,match='does not exist'):batches.prepare_batch(ws,missing)
    assert not missing.exists()


@pytest.mark.parametrize('change',[
    {'id':'../escape'}, {'items':[]}, {'items':[{'id':'one','kind':'unknown'}]},
    {'items':[{'id':'one','kind':'asmr'}]}, {'output_root':None}])
def test_invalid_plan_contract_is_rejected(setup,change):
    ws,plan,_=setup;value=json.loads(plan.read_text());value.update(change);write_json(plan,value)
    with pytest.raises(ValueError):batches.prepare_batch(ws,plan)


def playbook_item(name='horror_stock',**request):
    return {'id':'new-format','kind':'playbook','playbook':name,
            'topic':'A specific original topic with a delivered answer',
            'channel':'education' if name=='education_demo' else 'entertainment','request':request}


@pytest.mark.parametrize('name',list(batches.PLAYBOOKS))
def test_all_playbooks_create_channel_jobs_and_preserve_request_options(tmp_path,monkeypatch,name):
    ws=Workspace(tmp_path/'ws')
    assets={'music':{'id':'music','has_audio':True,'kind':'audio','sha256':'music'}}
    assets.update({str(i):{'id':str(i),'kind':'image','sha256':str(i)} for i in range(4)})
    assets['bottom']={'id':'bottom','kind':'video','sha256':'bottom'}
    monkeypatch.setattr(batches,'asset_record',lambda ws,ref:assets[ref])
    request={'music_id':'music','creative_brief':'Keep the exact plot setup','resolution':'1080p',
             'asset_roles':{'0':'before'},'visual_asset_ids':list(map(str,range(4))),'bottom_kind':'none'}
    if name=='tea_chat':request.update(bottom_kind='asmr',bottom_asset_id='bottom')
    spec=playbook_item(name,**request);original=json.loads(json.dumps(spec))
    job=batches._create_job(ws,spec,tmp_path/'item',tmp_path,token='stable-recovery-token')
    assert job['channel']==spec['channel']
    assert job['request']['playbook']==name and job['request']['topic']==spec['topic']
    assert job['request']['format']==batches.PLAYBOOKS[name]['format']
    assert job['request']['batch_item_token']=='stable-recovery-token'
    assert all(job['request'][key]==value for key,value in request.items())
    assert spec==original


def test_default_plan_uses_new_formats_and_only_known_owner_generated_bottom(tmp_path):
    arbitrary=tmp_path/'somebody-elses-video.mp4';arbitrary.write_bytes(b'fixture')
    first=batches.default_plan(tmp_path)
    assert [x['playbook'] for x in first['items']]==['horror_stock','tea_chat','aura_progression']
    assert all(x['kind']=='playbook' for x in first['items'])
    assert 'bottom_source_file' not in first['items'][1]['request']
    known=tmp_path/'Generated Video November 02, 2026 - 12_46AM.mp4';known.write_bytes(b'owner fixture')
    second=batches.default_plan(tmp_path)
    chat=second['items'][1]['request']
    assert chat['bottom_source_file']==str(known.resolve()) and chat['bottom_source_type']=='owner_generated'
    assert chat['bottom_source_evidence']['owner_supplied'] is True
    assert second['items'][2]['request']['visual_asset_ids']==[]
    assert all('music_id' not in x['request'] for x in second['items'])


@pytest.mark.parametrize('change',[
    {'playbook':'not-real'}, {'playbook':[]}, {'topic':''}, {'topic':'x'*181}, {'channel':'unknown'},
    {'request':None}, {'request':{'playbook':'tea_chat'}}, {'request':{'format':'aura'}},
    {'request':{'topic':'silently replaced'}}, {'request':{'batch_item_token':'forged'}},
    {'request':{'require_music':'false'}}])
def test_bad_playbook_contract_rejected_before_job_creation(tmp_path,change):
    ws=Workspace(tmp_path/'ws');plan=tmp_path/'plan.json';item=playbook_item();item.update(change)
    write_json(plan,{'version':1,'id':'bad-playbook','output_root':str(tmp_path/'outputs'),'items':[item]})
    with pytest.raises(ValueError):batches.prepare_batch(ws,plan)
    assert ws.jobs()==[]


@pytest.mark.parametrize('name,options,error',[
    ('horror_stock',{},'playbook_music_missing'),
    ('tea_chat',{'music_id':'music','bottom_kind':'asmr'},'background_missing'),
    ('aura_progression',{'require_music':False},'playbook_music_missing'),
    ('aura_progression',{'music_id':'music','visual_asset_ids':['a']},'aura_progression_assets'),
    ('aura_progression',{'music_id':'music','bottom_kind':'asmr'},'playbook_background'),
    ('horror_stock',{'music_id':'silent'},'music_missing_audio'),
    ('horror_stock',{'music_id':'music','bottom_kind':'none','bottom_asset_id':'unused'},'playbook_background'),
    ('horror_stock',{'music_id':'music','visual_asset_ids':['generation:pending']},'generated_media_pending')])
def test_missing_prerequisites_hold_before_any_pipeline_or_model_call(tmp_path,monkeypatch,name,options,error):
    ws=Workspace(tmp_path/'ws');plan=tmp_path/'plan.json'
    def asset(ws,ref):return {'id':ref,'kind':'audio' if ref in ('music','silent') else 'image','has_audio':ref=='music','sha256':ref}
    monkeypatch.setattr(batches,'asset_record',asset)
    monkeypatch.setattr(batches,'Pipeline',lambda *a:pytest.fail('Held prerequisites must not start the model pipeline'))
    monkeypatch.setattr(batches,'_music',lambda *a:pytest.fail('No synthesized generic music fallback'))
    write_json(plan,{'version':1,'id':'held-playbook','output_root':str(tmp_path/'outputs'),
                     'items':[playbook_item(name,**options)]})
    result=batches.run_batch(ws,plan)
    assert result['items'][0]['status']=='held' and result['items'][0]['error_code']==error
    assert result['items'][0]['job_id'] is None and ws.jobs()==[]


def test_aura_rejects_duplicate_file_copies_even_with_different_registered_ids(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws')
    monkeypatch.setattr(batches,'asset_record',lambda ws,ref:{'id':ref,'kind':'image','has_audio':True,'sha256':'same-copy'})
    with pytest.raises(Held) as exc:
        batches._playbook_request(ws,playbook_item('aura_progression',music_id='music',visual_asset_ids=['a','b','c','d']),tmp_path/'item')
    assert exc.value.code=='aura_progression_assets' and ws.jobs()==[]


def test_education_can_explicitly_choose_no_music_without_channel_fallback(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');config=ws.config();config['channels']['education']['music_id']='unrelated-profile-track';ws.save_config(config)
    monkeypatch.setattr(batches,'asset_record',lambda *a:pytest.fail('No profile music fallback'))
    job=batches._create_job(ws,playbook_item('education_demo',require_music=False),tmp_path/'item',tmp_path)
    assert job['request']['require_music'] is False and 'music_id' not in job['request']


def test_owner_generated_bottom_is_explicit_checkpointed_and_change_detected(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');source=tmp_path/'owner.mp4';source.write_bytes(b'owner generated media fixture')
    assets={'music':{'id':'music','kind':'audio','has_audio':True,'sha256':'music'}};imports=[]
    def register(ws,path,source_type,evidence,**options):
        imports.append((source_type,evidence,options))
        assets['bottom']={'id':'bottom','kind':'video','sha256':file_hash(path)}
        return assets['bottom']
    monkeypatch.setattr(batches,'register_asset',register)
    monkeypatch.setattr(batches,'asset_record',lambda ws,ref:assets[ref])
    spec=playbook_item('tea_chat',music_id='music',bottom_kind='asmr',bottom_source_file=str(source),
        bottom_source_type='owner_generated',bottom_source_evidence={'owner_supplied':True},test_only=True)
    folder=tmp_path/'item'
    first=batches._playbook_request(ws,spec,folder);second=batches._playbook_request(ws,spec,folder)
    assert first==second and first['bottom_asset_id']=='bottom' and len(imports)==1
    assert imports[0][0]=='original_graphic' and imports[0][1]['source_type']=='owner_generated'
    assert imports[0][2]['test_only'] is True and 'bottom_source_file' not in first
    source.write_bytes(b'changed source')
    with pytest.raises(Held) as exc:batches._playbook_request(ws,spec,folder)
    assert exc.value.code=='batch_source_changed'


@pytest.mark.parametrize('source_type,evidence,error',[
    ('downloaded',{'url':'public-video-page'},'batch_bottom_permission'),
    ('owner_generated',{},'asset_evidence_missing')])
def test_local_path_alone_never_implies_lower_panel_permission(tmp_path,monkeypatch,source_type,evidence,error):
    ws=Workspace(tmp_path/'ws');source=tmp_path/'clip.mp4';source.write_bytes(b'fixture')
    monkeypatch.setattr(batches,'asset_record',lambda ws,ref:{'id':ref,'has_audio':True})
    monkeypatch.setattr(batches,'register_asset',lambda *a,**k:pytest.fail('Unverified footage cannot be imported'))
    spec=playbook_item('tea_chat',music_id='music',bottom_kind='asmr',bottom_source_file=str(source),
        bottom_source_type=source_type,bottom_source_evidence=evidence)
    with pytest.raises(Held) as exc:batches._playbook_request(ws,spec,tmp_path/'item')
    assert exc.value.code==error


def test_registered_ineligible_asset_stops_before_job_creation(tmp_path):
    from PIL import Image
    from yt_pipeline.assets import register_asset
    ws=Workspace(tmp_path/'ws');picture=tmp_path/'not-commercial.png';Image.new('RGB',(40,40)).save(picture)
    asset=register_asset(ws,picture,'licensed_stock',{'license':'noncommercial only'},commercial=False)
    with pytest.raises(Held) as exc:
        batches._create_job(ws,playbook_item(music_id=asset['id']),tmp_path/'item',tmp_path)
    assert exc.value.code=='asset_not_eligible' and ws.jobs()==[]
