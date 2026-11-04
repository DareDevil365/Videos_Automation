import io
import json
from urllib.error import HTTPError

import pytest

from yt_pipeline.core import Workspace,Held
from yt_pipeline.writer import Gemini
from yt_pipeline.gemini_projects import import_project_keys,project_status


def configured(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');cfg=ws.config()
    cfg['gemini']['projects']=[{'id':f'p{i}','key_env':f'GEMINI_API_KEY_P{i}','free_tier_confirmed':True,'requests_per_day':5} for i in range(3)]
    for i in range(3):monkeypatch.setenv(f'GEMINI_API_KEY_P{i}',f'synthetic-private-key-{i}')
    ws.save_config(cfg);return ws


def success():return {'candidates':[{'content':{'parts':[{'text':'{"ok":true}'}]}}]}


def test_project_429_only_cools_that_project_and_other_project_completes(tmp_path,monkeypatch):
    ws=configured(tmp_path,monkeypatch);calls=[]
    def transport(model,body):
        calls.append(body)
        if len(calls)==1:raise HTTPError('https://example.com',429,'limit',{'Retry-After':'120'},io.BytesIO(b'{}'))
        return success()
    assert Gemini(ws,transport).generate('story',{}, {'type':'object'})=={'ok':True}
    states=project_status(ws)
    assert len(calls)==2 and states[0]['cooldown_seconds']>=119 and states[1]['cooldown_seconds']==0
    assert [s['local_calls_today'] for s in states]==[1,1,0]
    assert ws.quota_status('gemini',30)['local_calls_today']==2
    assert Gemini(ws,transport).generate('another',{}, {'type':'object'})=={'ok':True}
    assert project_status(ws)[2]['local_calls_today']==1
    assert 'synthetic-private-key' not in json.dumps(calls)


def test_cached_result_works_when_all_projects_cooling_and_survives_restart(tmp_path,monkeypatch):
    ws=configured(tmp_path,monkeypatch);calls=[]
    def transport(*args):calls.append('network');return success()
    Gemini(ws,transport).generate('saved',{}, {'type':'object'})
    for i in range(3):ws.cool_provider(f'gemini:p{i}',180)
    reopened=Workspace(ws.root)
    assert Gemini(reopened,transport).generate('saved',{}, {'type':'object'})=={'ok':True}
    with pytest.raises(Held) as exc:Gemini(reopened,transport).generate('new',{}, {'type':'object'})
    assert exc.value.retry_after and calls==['network']


def test_atomic_aggregate_cap_is_not_multiplied_by_number_of_keys(tmp_path,monkeypatch):
    ws=configured(tmp_path,monkeypatch);cfg=ws.config();cfg['gemini']['requests_per_day']=1;ws.save_config(cfg);calls=[]
    def transport(*args):calls.append('network');return success()
    Gemini(ws,transport).generate('one',{}, {'type':'object'})
    with pytest.raises(Held) as exc:Gemini(ws,transport).generate('two',{}, {'type':'object'})
    assert exc.value.code=='daily_budget' and len(calls)==1
    assert sum(s['local_calls_today'] for s in project_status(ws))==1


def test_dev_override_retains_counts_and_production_reenables_all_caps(tmp_path,monkeypatch):
    ws=configured(tmp_path,monkeypatch);cfg=ws.config();cfg['gemini']['enforce_local_budget']=False;ws.save_config(cfg)
    assert all(s['local_daily_cap'] is None for s in project_status(ws))
    cfg['channels']['entertainment']['publication_mode']='private';ws.save_config(cfg)
    assert all(s['local_daily_cap']==5 for s in project_status(ws))


def test_import_secrets_stay_only_in_environment_file_and_are_idempotent(tmp_path):
    ws=Workspace(tmp_path/'ws');source=tmp_path/'source.txt';env=tmp_path/'.env'
    secrets=['AQ.'+'a'*40,'AIza'+'b'*35];source.write_text('\n'.join(secrets),encoding='utf-8')
    with pytest.raises(Held):import_project_keys(ws,source,env)
    result=import_project_keys(ws,source,env,distinct_projects=True,free_tier_confirmed=True)
    import_project_keys(ws,source,env,distinct_projects=True,free_tier_confirmed=True)
    assert result['projects_imported']==2 and env.read_text().count('GEMINI_API_KEY_PROJECT_01=')==1
    assert not any(key in json.dumps(result)+json.dumps(ws.config()) for key in secrets)
    assert source.read_text(encoding='utf-8')=='\n'.join(secrets)
    with pytest.raises(Held):import_project_keys(ws,source,source,distinct_projects=True,free_tier_confirmed=True)


def test_duplicate_credentials_are_not_counted_as_independent_projects(tmp_path,monkeypatch):
    ws=configured(tmp_path,monkeypatch)
    monkeypatch.setenv('GEMINI_API_KEY_P1','synthetic-private-key-0')
    with pytest.raises(Held,match='only one'):project_status(ws)
