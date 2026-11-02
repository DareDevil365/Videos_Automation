"""Actual FFmpeg exports using clearly labelled synthetic technical fixtures."""
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import threading
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import wave

import pytest

from shorts_editor.server import make_server
from shorts_editor.store import Store, write_json
from yt_pipeline.core import Workspace, Held, now
from yt_pipeline.assets import register_asset
from yt_pipeline.pipeline import Pipeline
from yt_pipeline.publishing import approve


ROOT=Path(__file__).resolve().parents[1]
pytestmark=pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')


def fixture_voice(calls):
    def make(ws,script,folder):
        calls.append('voice');folder.mkdir(exist_ok=True)
        path=folder/'fixture.wav';rate=16000;duration=len(script['units'])
        with wave.open(str(path),'wb') as wav:
            wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate)
            wav.writeframes(b''.join(struct.pack('<h',int(3000*math.sin(2*math.pi*440*i/rate))) for i in range(rate*duration)))
        return {'audio':str(path),'duration':duration,'voice':'SINE TECHNICAL FIXTURE, NOT SPEECH','model_sha256':'fixture',
                'units':[{'id':u['id'],'duration':1,'start':i,'end':i+1,'speech_end':i+.8,'text':u['text']} for i,u in enumerate(script['units'])]}
    return make


def clip_fixture(tmp_path):
    output=tmp_path/'technical-video.mp4'
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=navy:s=180x320:r=30:d=3','-f','lavfi','-i','sine=frequency=330:duration=3',
                    '-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(output)],check=True,capture_output=True)
    return output


def test_held_chat_resumes_without_regenerating_voice(tmp_path):
    ws=Workspace(tmp_path/'pipeline');request=json.loads((ROOT/'examples/chat-request.json').read_text())
    request['script']['units']=request['script']['units'][:2];request['script']['edit']['payoff_unit_id']='two'
    job=ws.create('entertainment',request);calls=[];pipeline=Pipeline(ws,voice_fn=fixture_voice(calls))
    held=pipeline.run(job['id'])
    assert held['status']=='held' and held['error_code']=='background_missing'
    assert set(held['artifacts'])=={'research','script','voice','visuals'}
    asset=register_asset(ws,clip_fixture(tmp_path),'test',{'reference':'Synthetic technical fixture'})
    config=ws.config();config['channels']['entertainment']['footage_ids']=[asset['id']];ws.save_config(config)
    ws.reset(job['id'],'direct');ready=pipeline.run(job['id'])
    assert ready['status']=='ready',ready['message']
    assert calls==['voice']
    qa=json.loads(Path(ready['artifacts']['quality']['path']).read_text())
    assert qa['technical_pass'] and qa['test_only'] and not qa['publication_ready']
    with pytest.raises(Held):approve(ws,job['id'])
    project=json.loads((ws.job_dir(job['id'])/'render-project.json').read_text())
    assert project['scenes'][0]['effect_at']==180
    assert project['scenes'][1]['effect_at']<1
    assert all(not s['source_audio'] for s in project['scenes'])
    assert project['narration']


def test_source_clip_exports_original_audio_without_tts(tmp_path):
    ws=Workspace(tmp_path/'pipeline');asset=register_asset(ws,clip_fixture(tmp_path),'test',{'reference':'Synthetic clip test'})
    request=json.loads((ROOT/'examples/chat-request.json').read_text());request['format']='clip'
    script=request['script'];script['format']='clip';script['units']=script['units'][:1]
    script['edit'].update(effect='none',payoff_unit_id='one')
    request.update(clip_asset_id=asset['id'],clip_start=.5,clip_end=2.5)
    job=ws.create('entertainment',request)
    result=Pipeline(ws,voice_fn=lambda *_:pytest.fail('TTS called for source speech')).run(job['id'])
    assert result['status']=='ready',result['message']
    voice=json.loads(Path(result['artifacts']['voice']['path']).read_text())
    assert voice['source']=='original_clip'
    rendered=json.loads(Path(result['artifacts']['render']['path']).read_text())
    assert Path(rendered['captions']).read_text()==''
    project=json.loads((ws.job_dir(job['id'])/'render-project.json').read_text())
    assert not project['narration'] and project['scenes'][0]['source_audio']
    assert project['scenes'][0]['media_start']==.5


def test_production_http_control_and_isolation(tmp_path):
    server=make_server(Store(tmp_path/'editor'),0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        with urlopen(base+'/api/bootstrap') as r:token=json.load(r)['token']
        with urlopen(base+'/production') as r:assert b'From idea to export.' in r.read()
        with urlopen(base+'/api/production-example') as r:example=json.load(r)
        assert example['script']['format']=='lesson'
        body=json.dumps({'action':'create','channel':'education','request':{'topic':'Control test'},'run':False}).encode()
        with pytest.raises(HTTPError) as exc:urlopen(Request(base+'/api/production',body,{'Content-Type':'application/json'}))
        assert exc.value.code==403
        with urlopen(Request(base+'/api/production',body,{'Content-Type':'application/json','X-Editor-Token':token})) as r:job=json.load(r)
        with urlopen(base+'/api/production') as r:state=json.load(r)
        assert state['jobs'][0]['id']==job['id']
        assert 'session' not in json.dumps(state) and 'credentials' not in json.dumps(state['profiles'])
        with pytest.raises(HTTPError):urlopen(Request(base+'/api/production',body,{'Host':'evil.example','X-Editor-Token':token}))
    finally:
        server.shutdown();server.server_close();server.jobs.close();thread.join(timeout=2)
