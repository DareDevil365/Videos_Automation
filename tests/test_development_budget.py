import pytest

from yt_pipeline.cli import config_set
from yt_pipeline.core import Held,Workspace


def test_explicit_development_override_keeps_accounting_and_production_restores_cap(tmp_path):
    ws=Workspace(tmp_path/'ws')
    config_set(ws,'gemini.requests_per_day',1)
    ws.reserve_call('gemini',ws.gemini_budget_cap())
    with pytest.raises(Held):ws.reserve_call('gemini',ws.gemini_budget_cap())
    config_set(ws,'gemini.enforce_local_budget',False)
    assert ws.gemini_budget_cap() is None
    ws.reserve_call('gemini',ws.gemini_budget_cap())
    ws.reserve_call('gemini',ws.gemini_budget_cap())
    status=ws.quota_status('gemini',ws.gemini_budget_cap())
    assert status['local_calls_today']==3 and status['local_remaining'] is None
    assert status['local_daily_cap'] is None and status['local_budget_enforced'] is False
    config_set(ws,'channels.entertainment.publication_mode','private')
    assert ws.gemini_budget_cap()==1
    with pytest.raises(Held):ws.reserve_call('gemini',ws.gemini_budget_cap())


def test_old_config_defaults_to_enforcement_and_override_requires_boolean(tmp_path):
    ws=Workspace(tmp_path/'ws');config=ws.config()
    config['gemini'].pop('enforce_local_budget');ws.save_config(config)
    assert ws.gemini_budget_cap()==30
    with pytest.raises(ValueError):config_set(ws,'gemini.enforce_local_budget','false')
    config_set(ws,'gemini.enforce_local_budget',False)
    assert ws.gemini_budget_cap() is None
    config_set(ws,'gemini.enforce_local_budget',True)
    assert ws.gemini_budget_cap()==30
