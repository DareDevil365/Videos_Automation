from copy import deepcopy
import json
from pathlib import Path
import shutil

from PIL import ImageChops
import pytest

from yt_pipeline.core import Workspace,Held
from yt_pipeline.chat_editing import compile_chat_plan,reading_timing,chat_frame
from yt_pipeline.playbooks import prepare_request,get_playbook


def conversation():
    lines=['Who labelled the shared chair again?', 'That chair is clearly mine now.', 'You labelled the cereal box too.',
        'Please read the very clear label.', 'And now the wireless router too?', 'My name means it belongs here.',
        'Then here is your electricity bill.', 'Why is my name on this?', 'Because you requested a clear label.',
        'We normally split the electricity bill.', 'But this label clearly names you.', 'Fine, the chair can stay shared.']
    units=[{'id':f'u{i}','speaker':'Oak' if i%2==0 else 'Fern','text':s,'onscreen':s,'kind':'fiction','claim_ids':[]} for i,s in enumerate(lines)]
    return {'version':1,'format':'chat','fiction':True,'title':'Technical original chat fixture','description':'Synthetic test conversation, not a published comedy.',
        'hook':lines[0],'payoff':lines[-1],'units':units,'edit':{'effect':'none','payoff_unit_id':'u11','cta':False}}


def request():return prepare_request({'playbook':'server_chat','chat_editing_version':2,'fiction':True,'test_only':True})


def test_editor_compiles_without_provider_and_keeps_exact_dialogue():
    script=conversation();original=deepcopy(script);record=compile_chat_plan(script,request())
    assert record['origin']=='compiled_chat_rules_v2' and record['script_sha256']==record['plan']['script_sha256']
    assert [s['text'] for s in record['plan']['scenes']]==[u['text'] for u in script['units']] and script==original
    assert request()['hook_options'] is False and request()['editorial_review']=='off' and request()['visual_review']=='off'
    assert get_playbook('server_chat')['voice'] and get_playbook('server_chat',request())['voice'] is None
    with pytest.raises(Held,match='writing only'):prepare_request({**request(),'visual_review':'required'})
    with pytest.raises(Held,match='fictional'):prepare_request({**request(),'fiction':False})


def test_reading_timeline_audio_and_no_future_message_reveal(tmp_path):
    script=conversation();ws=Workspace(tmp_path/'ws');job=ws.create('entertainment',request())
    timing=reading_timing(ws,job,script,tmp_path/'timing')
    assert timing['narration'] is False and 18<=timing['duration']<=55 and Path(timing['audio']).is_file()
    assert all(u['hold_seconds']>=1.05 for u in timing['units'])
    before,state=chat_frame(script,5,0,2,.16)
    after,settled=chat_frame(script,5,1,2,.16)
    assert before.size==after.size==(720,1280)
    assert 'u5' not in state['visible_unit_ids'] and 'u5' in settled['visible_unit_ids']
    assert not {'u6','u7','u8'}&set(settled['visible_unit_ids']) and ImageChops.difference(before,after).getbbox()


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
def test_full_program_uses_only_writer_no_model_director_or_tts(tmp_path):
    from yt_pipeline.pipeline import Pipeline
    ws=Workspace(tmp_path/'ws');script=conversation();calls=[]
    job=ws.create('entertainment',{**request(),'topic':'A technical original conversation about shared objects'})
    class WriterOnly:
        def generate(self,purpose,*args,**kwargs):
            calls.append(purpose)
            assert purpose=='scripter-v3', 'The editor must never ask the model for decisions.'
            return deepcopy(script)
    def forbidden_voice(*args,**kwargs):raise AssertionError('Reading-led chat must not use TTS.')
    result=Pipeline(ws,provider=WriterOnly(),voice_fn=forbidden_voice).run(job['id'])
    assert result['status']=='ready',result.get('message')
    assert calls==['scripter-v3']
    written=json.loads(Path(result['artifacts']['script']['path']).read_text())
    assert written['origin']=='gemini' and written['creative_plan']['origin']=='compiled_chat_rules_v2'
    qa=json.loads(Path(result['artifacts']['quality']['path']).read_text())
    assert qa['technical_pass'] and (qa['width'],qa['height'])==(720,1280)
    assert qa['chat_editing']['editing_model_calls']==0
    resumed=Pipeline(ws,provider=WriterOnly(),voice_fn=forbidden_voice).run(job['id'])
    assert resumed['status']=='ready' and calls==['scripter-v3']


def test_chat_plan_is_standalone_and_preflights_without_sources_or_models(tmp_path):
    from yt_pipeline.batches import default_chat_plan,_playbook_request
    ws=Workspace(tmp_path/'ws');plan=default_chat_plan(tmp_path/'Resources','A short fictional roommate argument')
    assert plan['items'][0]['request']['chat_auto_music'] and plan['items'][0]['request']['chat_voiceover']
    plan['items'][0]['request']['chat_auto_music']=False # Offline content-only preflight remains available.
    req=_playbook_request(ws,plan['items'][0],tmp_path/'item')
    assert req['chat_editing_version']==2 and req['visual_review']=='off' and req['editorial_review']=='off'
    assert req['hook_options'] is False and req['test_only'] is True and req['require_music'] is False
    assert not req.get('script') and not req.get('script_file')
    assert plan['output_root']==str((tmp_path/'Resources/Productions').resolve())
    with pytest.raises(ValueError):default_chat_plan(tmp_path,'a'*181)
