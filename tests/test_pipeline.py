"""Deterministic contract, recovery and API-boundary tests; no live accounts."""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from http.server import ThreadingHTTPServer
import json
import io
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from urllib.error import HTTPError

import pytest
from PIL import Image

from yt_pipeline.core import Workspace, Held, file_hash, now, load_env_file, redact
from yt_pipeline.contracts import brief_contract, script_contract
from yt_pipeline.writer import Gemini, write_script, quota_retry_delay
from yt_pipeline.pipeline import Pipeline
from yt_pipeline.publishing import approve, publish, load_upload, reconcile, safe_session
from yt_pipeline.assets import register_asset, asset_record
from yt_pipeline.monitor import alerts, incident, supervise, observe, growth_report
from yt_pipeline.cli import config_set
from yt_pipeline.visuals import chat_frame
from yt_pipeline.net import public_url
from yt_pipeline.benchmarks import benchmark
from shorts_editor.store import write_json

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def ws(tmp_path):return Workspace(tmp_path/'pipeline')


@pytest.fixture
def chat():return json.loads((ROOT/'examples/chat-request.json').read_text())


def test_contract_rejects_unknown_claim(chat):
    brief=brief_contract(chat['brief']);script=deepcopy(chat['script'])
    script['units'][0].update(kind='fact',claim_ids=['made_up'])
    with pytest.raises(Held,match='unknown factual'):script_contract(script,brief,'chat')
    script=deepcopy(chat['script']);script['execute']='rm something'
    with pytest.raises(Held,match='unsupported fields'):script_contract(script,brief,'chat')


@pytest.mark.parametrize('source',[None,42,'bad'])
def test_bad_source_contract(source,chat):
    brief={**chat['brief'],'sources':[source]}
    with pytest.raises(Held):brief_contract(brief)


def test_chat_states_are_recent_and_readable(chat,tmp_path):
    script=script_contract(chat['script'],brief_contract(chat['brief']))
    a=chat_frame(script,0,tmp_path/'first.png');b=chat_frame(script,3,tmp_path/'last.png')
    assert a['visible_unit_ids']==['one']
    assert b['visible_unit_ids']==['two','three','four']
    assert b['height']<=1100
    im=Image.open(tmp_path/'last.png');colors=im.getcolors(im.width*im.height)
    assert any(c==(7,132,252) for _,c in colors)
    assert any(c==(48,48,51) for _,c in colors)


def test_sqlite_claim_and_global_lock(ws):
    job=ws.create('entertainment',{'topic':'A'})
    assert ws.claim(job['id'],'one')
    with pytest.raises(Held):ws.claim(job['id'],'two')
    ws.worker_lock('one')
    with pytest.raises(Held):ws.worker_lock('two')
    ws.worker_lock('one',release=True);ws.worker_lock('two');ws.worker_lock('two',release=True)
    ws.update(job['id'],lease_until=time.time()-5)
    assert ws.claim(job['id'],'two')


def test_unknown_job_does_not_leak_worker_lock(ws):
    with pytest.raises(ValueError):Pipeline(ws).run('0'*32)
    ws.worker_lock('another');ws.worker_lock('another',release=True)


def test_budget_and_alert_dedup(ws):
    ws.reserve_call('fake',1)
    with pytest.raises(Held) as exc:ws.reserve_call('fake',1)
    assert exc.value.code=='daily_budget'
    ws.alert('same',None,'one');ws.alert('same',None,'two')
    assert len(alerts(ws))==1
    assert alerts(ws,'same')[0]['acknowledged']==1


def configure_gemini(ws,monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','test-placeholder-not-a-real-key')
    config=ws.config();config['gemini']['free_tier_confirmed']=True;ws.save_config(config)


def test_gemini_cache_and_no_paid_fallback(ws,monkeypatch):
    configure_gemini(ws,monkeypatch);calls=[]
    def transport(model,body):
        calls.append((model,body));return {'candidates':[{'content':{'parts':[{'text':'{"answer":1}'}]}}]}
    provider=Gemini(ws,transport)
    schema={'type':'object','properties':{'answer':{'type':'integer'}}}
    assert provider.generate('test',{'data':'untrusted'},schema)=={'answer':1}
    assert provider.generate('test',{'data':'untrusted'},schema)=={'answer':1}
    assert len(calls)==1 and 'tools' not in calls[0][1]
    config=ws.config();config['gemini']['model']='paid-model';ws.save_config(config)
    with pytest.raises(Held):provider.generate('changed',{},schema)
    assert len(calls)==1


def test_verified_flash_thinking_is_bounded_and_part_of_cache(ws,monkeypatch):
    configure_gemini(ws,monkeypatch);calls=[]
    config=ws.config();config['gemini'].update(model='gemini-3.8-flash',thinking_level='low');ws.save_config(config)
    def transport(model,body):
        calls.append(body);return {'candidates':[{'content':{'parts':[{'text':'{"ok":true}'}]}}]}
    provider=Gemini(ws,transport);schema={'type':'object','properties':{'ok':{'type':'boolean'}}}
    provider.generate('bounded',{},schema);provider.generate('bounded',{},schema)
    assert len(calls)==1 and calls[0]['generationConfig']['thinkingConfig']=={'thinkingLevel':'low'}
    assert 'tools' not in calls[0]
    config['gemini']['thinking_level']='medium';ws.save_config(config)
    provider.generate('bounded',{},schema);assert len(calls)==2
    config['gemini']['thinking_level']='minimal';ws.save_config(config)
    with pytest.raises(Held) as error:provider.generate('bounded',{},schema)
    assert error.value.code=='thinking_level' and len(calls)==2


def test_gemini_quota_is_a_hold(ws,monkeypatch):
    configure_gemini(ws,monkeypatch)
    def limited(*args):raise HTTPError('https://example.com',429,'limit',{},None)
    with pytest.raises(Held) as exc:Gemini(ws,limited).generate('test',{}, {'type':'object'})
    assert exc.value.code=='gemini_quota' and exc.value.retry_after


def test_shared_quota_cooldown_survives_restart(ws,monkeypatch):
    configure_gemini(ws,monkeypatch);calls=[]
    def limited(*args):
        calls.append('request')
        raise HTTPError('https://example.com',429,'limit',{'Retry-After':'120'},io.BytesIO(b'{}'))
    with pytest.raises(Held) as first:Gemini(ws,limited).generate('one',{}, {'type':'object'})
    assert first.value.retry_after>=119
    reopened=Workspace(ws.root)
    with pytest.raises(Held) as again:Gemini(reopened,limited).generate('another job',{}, {'type':'object'})
    assert again.value.code=='gemini_quota'
    assert calls==['request']
    status=reopened.quota_status('gemini',30)
    assert status['local_calls_today']==1 and status['local_remaining']==29
    assert status['cooldown_seconds']>0 and status['provider_balance_known'] is False
    with ws.connect() as db:assert db.execute("SELECT calls FROM usage WHERE provider='gemini'").fetchone()[0]==1


def test_cached_results_still_work_during_cooldown(ws,monkeypatch):
    configure_gemini(ws,monkeypatch);calls=[]
    def success(*args):
        calls.append('request');return {'candidates':[{'content':{'parts':[{'text':'{"ok":true}'}]}}]}
    schema={'type':'object'};provider=Gemini(ws,success)
    assert provider.generate('saved',{},schema)=={'ok':True}
    ws.cool_provider('gemini',300)
    assert provider.generate('saved',{},schema)=={'ok':True}
    with pytest.raises(Held):provider.generate('new',{},schema)
    assert len(calls)==1


def test_quota_retry_hints_and_daily_hold():
    retry={'error':{'details':[{'@type':'type.googleapis.com/google.rpc.RetryInfo','retryDelay':'92.5s'}]}}
    error=HTTPError('https://example.com',429,'limit',{'Retry-After':'120'},io.BytesIO(json.dumps(retry).encode()))
    assert quota_retry_delay(error)==120
    retry['error']['details'].append({'@type':'type.googleapis.com/google.rpc.QuotaFailure','violations':[{'quotaId':'GenerateRequestsPerDayPerProject'}]})
    error=HTTPError('https://example.com',429,'limit',{},io.BytesIO(json.dumps(retry).encode()))
    assert quota_retry_delay(error)==86400


def test_cooldown_backoff_resets_after_success(ws,monkeypatch):
    configure_gemini(ws,monkeypatch)
    assert 59<=ws.cool_provider('gemini')<=60
    with ws.connect() as db:db.execute("UPDATE provider_cooldowns SET until=0")
    assert 119<=ws.cool_provider('gemini')<=120
    with ws.connect() as db:db.execute("UPDATE provider_cooldowns SET until=0")
    def success(*args):return {'candidates':[{'content':{'parts':[{'text':'{}'}]}}]}
    assert Gemini(ws,success).generate('after-wait',{}, {'type':'object'})=={}
    assert 59<=ws.cool_provider('gemini')<=60


def test_missing_key_does_not_call_network(ws,monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY',raising=False);monkeypatch.delenv('GOOGLE_API_KEY',raising=False)
    with pytest.raises(Held):Gemini(ws,lambda *_:pytest.fail('Network called')).generate('x',{}, {})


def test_script_duplicate_and_resume_upstream(ws,chat):
    job=ws.create('entertainment',chat)
    class NoProvider:
        def generate(self,*args):pytest.fail('Imported script should not call provider')
    brief=brief_contract(chat['brief'])
    result=write_script(ws,job,brief,NoProvider())
    assert result['origin']=='provided_script'
    other=ws.create('entertainment',chat)
    with pytest.raises(Held) as exc:write_script(ws,other,brief,NoProvider())
    assert exc.value.code=='duplicate_script'
    ws.update(job['id'],artifacts={'research':{'path':'saved'},'script':{'path':'later'}},approval_hash='old')
    ws.reset(job['id'],'script')
    assert set(ws.get(job['id'])['artifacts'])=={'research'}
    assert ws.get(job['id'])['approval_hash'] is None


def test_asset_mutation_and_expiry(ws,tmp_path):
    path=tmp_path/'owned.png';Image.new('RGB',(80,80),'blue').save(path)
    asset=register_asset(ws,path,'owner_recording',{'reference':'test declaration'})
    record=asset_record(ws,asset['id']);Path(record['path']).write_bytes(b'changed')
    with pytest.raises(Held) as exc:asset_record(ws,asset['id'])
    assert exc.value.code=='asset_changed'
    Image.new('RGB',(80,80),'red').save(path)
    asset=register_asset(ws,path,'test',{'reference':'fixture'},expires_at='2020-01-01T00:00:00Z')
    assert asset['test_only']
    with pytest.raises(Held) as exc:asset_record(ws,asset['id'])
    assert exc.value.code=='asset_expired'


@pytest.mark.parametrize('url',['http://127.0.0.1/x','http://169.254.169.254/','file:///secret','https://user:pass@example.com','https://example.com:8765'])
def test_research_rejects_private_or_unsafe_sources(url):
    with pytest.raises(Held):public_url(url)


def test_config_types_and_credentials_not_config(ws):
    with pytest.raises(ValueError):config_set(ws,'gemini.key','secret')
    with pytest.raises(ValueError):config_set(ws,'channels.education.daily_cap',True)
    assert config_set(ws,'channels.education.publication_mode','public')['value']=='public'
    with pytest.raises(ValueError):config_set(ws,'channels.education.publication_mode','unknown')
    config_set(ws,'channels.education.paused',True)
    assert ws.config()['channels']['education']['paused']


def test_env_file_preserves_existing_keys(ws,tmp_path,monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','existing')
    path=tmp_path/'local.env';path.write_text('GEMINI_API_KEY=replacement\n# ignored\n')
    load_env_file(path)
    assert os.environ['GEMINI_API_KEY']=='existing'


def test_dotted_credentials_survive_env_loading(tmp_path,monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    value='AQ.fake_test_value_only_0123456789012345'
    path=tmp_path/'credentials.env';path.write_text('GEMINI_API_KEY='+value+'\n',encoding='utf-8')
    load_env_file(path)
    assert os.environ['GEMINI_API_KEY']==value
    assert value not in redact('Credential: '+value)
    monkeypatch.delenv('GEMINI_API_KEY')
    assert value not in redact('Provider error: '+value)


def ready_upload(ws,test_only=False):
    job=ws.create('education',{'topic':'Fixture only'})
    folder=ws.job_dir(job['id']);video=folder/'fixture.mp4';video.write_bytes(b'fixture upload bytes')
    metadata={'title':'Test','description':'Test description','video':str(video),'category_id':'27','made_for_kids':False,'contains_synthetic_media':True,
              'qa':{'publication_ready':not test_only,'video_sha256':file_hash(video)}}
    write_json(folder/'package.json',metadata);write_json(folder/'direct.json',{'provenance':[]});write_json(folder/'research.json',{'sources':[]})
    artifacts={stage:{'path':str(folder/(stage+'.json')),'sha256':file_hash(folder/(stage+'.json'))} for stage in ('package','direct','research')}
    ws.update(job['id'],status='ready',artifacts=artifacts)
    config=ws.config();config['channels']['education'].update(publication_mode='private',youtube_channel_id='UCfixture');ws.save_config(config)
    return job['id'],metadata


class FakeYouTube:
    def __init__(self, lose_final=False):self.calls=[];self.lose_final=lose_final;self.identity_id='UCfixture';self.remote_done=False
    def identity(self):return {'id':self.identity_id}
    def video(self,id):return {'id':id,'snippet':{'channelId':'UCfixture','publishedAt':(datetime.now(timezone.utc)-timedelta(days=9)).isoformat()},'status':{'privacyStatus':'private','uploadStatus':'processed'},'processingDetails':{'processingStatus':'succeeded'}}
    def call(self,method,url,body=None,headers=None):
        self.calls.append((method,url,headers or {}))
        if method=='POST':return 200,{'Location':'https://www.googleapis.com/upload/youtube/v3/videos?upload_id=fixture'},b''
        if method=='PUT':
            if headers['Content-Range'].startswith('bytes */'):
                return (200,{},b'{"id":"video-fixture"}') if self.remote_done else (308,{},b'')
            self.remote_done=True
            if self.lose_final:self.lose_final=False;raise Held('youtube_network','Simulated lost response',retry_after=600)
            return 200,{},b'{"id":"video-fixture"}'
        return 200,{},json.dumps({'columnHeaders':[{'name':'views'},{'name':'averageViewDuration'}],'rows':[[100,20]]}).encode()


def test_publish_dry_run_has_zero_external_calls(ws):
    id,_=ready_upload(ws);client=FakeYouTube()
    result=publish(ws,id,client=client)
    assert result['dry_run'] and result['payload']['status']['privacyStatus']=='private'
    assert not client.calls and load_upload(ws,id) is None


def test_lost_upload_completion_reuses_one_session(ws):
    id,_=ready_upload(ws);approve(ws,id);client=FakeYouTube(lose_final=True)
    with pytest.raises(Held):publish(ws,id,True,client)
    assert load_upload(ws,id)['session']
    result=publish(ws,id,True,client)
    assert result['status']=='uploaded_private'
    assert sum(method=='POST' for method,_,_ in client.calls)==1
    assert any(h.get('Content-Range','').startswith('bytes */') for _,_,h in client.calls)
    with pytest.raises(Held):ws.reset(id,'render')


def test_wrong_channel_and_test_media_cannot_upload(ws):
    id,_=ready_upload(ws);approve(ws,id);client=FakeYouTube();client.identity_id='UCother'
    with pytest.raises(Held) as exc:publish(ws,id,True,client)
    assert exc.value.code=='wrong_channel' and not client.calls
    other,_=ready_upload(ws,test_only=True)
    with pytest.raises(Held) as exc:approve(ws,other)
    assert exc.value.code=='test_media'


def test_changed_video_invalidates_review(ws):
    id,metadata=ready_upload(ws);Path(metadata['video']).write_bytes(b'new version')
    with pytest.raises(Held) as exc:approve(ws,id)
    assert exc.value.code=='video_changed'


def test_changed_evidence_invalidates_publication(ws):
    id,_=ready_upload(ws)
    write_json(ws.job_dir(id)/'direct.json',{'provenance':[],'changed':True})
    with pytest.raises(Held) as exc:approve(ws,id)
    assert exc.value.code=='artifact_changed'


def test_parallel_upload_lease_blocks_other_process(ws):
    id,_=ready_upload(ws);approve(ws,id)
    ws.worker_lock('busy',name='upload:education')
    with pytest.raises(Held):publish(ws,id,True,FakeYouTube())
    assert load_upload(ws,id) is None


@pytest.mark.parametrize('url',['https://evil.com/upload/x','http://www.googleapis.com/upload/x','https://www.googleapis.com/elsewhere'])
def test_upload_session_host_guard(url):
    with pytest.raises(Held):safe_session(url)


def test_monitor_missing_is_not_zero_and_incident_pauses(ws):
    id,_=ready_upload(ws);ws.update(id,video_id='fixture')
    class Analytics(FakeYouTube):
        def video(self,id):
            row=super().video(id);row['status']['privacyStatus']='public';return row
        def call(self,*args,**kwargs):return 200,{},b'{"columnHeaders":[{"name":"views"}]}'
    result=observe(ws,id,'7d',Analytics())
    assert result['metrics'] is None and result['available'] is False
    assert growth_report(ws,'education')['experiments']==[]
    incident(ws,'education','Owner recorded notice')
    assert ws.config()['channels']['education']['paused']
    assert supervise(ws)['remote_checked'] is False


def test_cli_machine_output_without_secrets(tmp_path):
    result=subprocess.run([sys.executable,str(ROOT/'run_pipeline.py'),'--root',str(tmp_path/'root'),'doctor'],capture_output=True,text=True)
    assert result.returncode==0
    data=json.loads(result.stdout)
    assert data['status']=='ok' and 'gemini_key_present' in data['result']
    assert 'GEMINI_API_KEY' not in result.stdout


def test_public_benchmarks_measure_only_observed_counts(ws,monkeypatch):
    monkeypatch.setenv('YOUTUBE_API_KEY','not-a-real-test-key')
    checked=datetime.now(timezone.utc)
    older={'video_id':'abcdef12345','views':100,'checked_at':(checked-timedelta(hours=2)).isoformat()}
    with ws.connect() as db:db.execute('INSERT INTO public_snapshots(video_id,at,data) VALUES(?,?,?)',('abcdef12345',older['checked_at'],json.dumps(older)))
    response={'items':[{'id':'abcdef12345','snippet':{'title':'Example','channelId':'UCpublic','publishedAt':(checked-timedelta(hours=10)).isoformat()},
                        'statistics':{'viewCount':'300'},'contentDetails':{'duration':'PT30S'}}]}
    def fetcher(url):return json.dumps(response).encode(),'application/json',url
    result=benchmark(ws,'entertainment','chat',[{'url':'https://www.youtube.com/watch?v=abcdef12345'}],fetcher)
    item=result['videos'][0]
    assert item['views']==300 and item['likes'] is None
    assert item['views_per_hour_since_publish']==pytest.approx(30,abs=.1)
    assert item['observed_views_per_hour_delta']==pytest.approx(100,abs=.1)
    assert 'revenue' not in item and 'retention' not in item


def test_public_benchmarks_missing_key_and_empty_results(ws,monkeypatch):
    monkeypatch.delenv('YOUTUBE_API_KEY',raising=False)
    with pytest.raises(Held) as exc:benchmark(ws,'education','AI')
    assert exc.value.code=='youtube_key_missing'
    monkeypatch.setenv('YOUTUBE_API_KEY','test-only')
    assert benchmark(ws,'education','AI',[])['videos']==[]
