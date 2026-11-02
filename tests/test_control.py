from pathlib import Path

import pytest

from yt_pipeline.control import command,Controls


def test_standalone_uses_local_entrypoint_and_env_file_only(tmp_path):
    args=command(tmp_path,'batch-run',tmp_path/'plan.json',tmp_path/'stop')
    assert args[1]==str(tmp_path/'run_pipeline.py')
    assert args[2:4]==['--env-file',str(tmp_path/'.env')]
    assert args[4:] == ['batch-run','--plan',str(tmp_path/'plan.json'),'--stop-file',str(tmp_path/'stop')]
    assert not any('openai' in a.lower() or 'chatgpt' in a.lower() for a in args)


def test_pause_is_local_cooperative_marker_not_forced_kill(tmp_path):
    controller=Controls(tmp_path)
    class Running:
        def poll(self):return None
    controller.process=Running();controller.mode='batch-run'
    controller.stop_file.parent.mkdir(parents=True)
    assert 'current video' in controller.request_stop()
    assert controller.stop_file.is_file()
    controller.mode='generation-setup'
    assert 'Close' in controller.request_stop()
    with pytest.raises(ValueError):command(tmp_path,'arbitrary-shell-command')
