from copy import deepcopy
import json
from pathlib import Path
import shutil
import wave
from array import array

from PIL import ImageChops
import pytest

from yt_pipeline.core import Workspace, Held, redact
from yt_pipeline.contracts import script_contract
from yt_pipeline.phone_editor.contract import validate_phone_story, compile_beats
from yt_pipeline.phone_editor.story import story_frame
from yt_pipeline.phone_editor.writing import critique, reviewed_script
from yt_pipeline.chat_editing import reading_timing
from yt_pipeline.batches import default_phone_plan, _playbook_request
from yt_pipeline.text_provider import OpenAI, strict_schema, configured_provider


def phone_script():
    rows=[('Unknown','Why did you unlock the empty flat?','unknown'),
          ('Ari',"I haven't touched that door.",'unknown'),
          ('Unknown','Your phone opened it at six.','unknown'),
          ('Mira','Did you take my old phone?','wife'),
          ('Ari','No. Where did you leave it?','wife'),
          ('Mira',"Charging beside the empty flat's door.",'wife'),
          ('Kit',"Mum's old phone keeps flashing.",'daughter'),
          ('Ari',"Don't touch it. Where are you?",'daughter'),
          ('Kit',"Outside. The door just opened.",'daughter'),
          ('Mira',"That phone isn't mine. Mine's with me.",'wife'),
          ('Ari','Whose phone did we leave there?','unknown'),
          ('Unknown','Mine. You took it home yesterday.','unknown'),
          ('Ari',"You're the courier from yesterday?",'unknown'),
          ('Unknown',"Yes. Kit returned my phone. Door's unlocked.",'unknown')]
    units=[{'id':f'u{i}','speaker':s,'text':text,'onscreen':text,'kind':'fiction','claim_ids':[]} for i,(s,text,t) in enumerate(rows)]
    story={'pov':'Ari','contacts':[{'id':name,'name':label} for name,label in [('c1','Unknown'),('c2','Mira'),('c3','Kit')]],
           'threads':[{'id':name,'contact_id':cid,'theme':theme} for name,cid,theme in [('unknown','c1','dark'),('wife','c2','sage'),('daughter','c3','rose')]],
           'beats':[{'unit_id':f'u{i}','thread_id':t,'time':'18:31' if i<9 else '21:31',
                     'events':['low_battery','glitch','blackout','time_jump','notification'] if i==9 else []} for i,(s,text,t) in enumerate(rows)]}
    return {'version':1,'title':'Synthetic phone editor fixture','description':'Technical test data, not an approved story.',
            'format':'chat','fiction':True,'hook':units[0]['text'],'payoff':units[-1]['text'],'units':units,
            'edit':{'effect':'none','payoff_unit_id':units[-1]['id'],'cta':False},'phone_story':story}


def phone_request(tmp_path):
    plan=default_phone_plan(tmp_path/'Resources')
    return _playbook_request(Workspace(tmp_path/'ws'),plan['items'][0],tmp_path/'item')


def test_contract_preserves_phone_story_and_rejects_impossible_private_chat(tmp_path):
    script=phone_script();original=deepcopy(script)
    parsed=script_contract(script,{'kind':'fiction','claims':[]},'chat')
    assert parsed['phone_story']==original['phone_story'] and script==original
    broken=deepcopy(script);broken['units'][3]['speaker']='Kit'
    with pytest.raises(Held,match='private conversation'):validate_phone_story(broken['phone_story'],broken['units'])
    for change in ('future','unknown','bad_event'):
        broken=deepcopy(script)
        if change=='future':broken['phone_story']['beats'][4]['time']='17:30'
        if change=='unknown':broken['phone_story']['beats'][0]['thread_id']='missing'
        if change=='bad_event':broken['phone_story']['beats'][0]['events']=[{}]
        with pytest.raises(Held):validate_phone_story(broken['phone_story'],broken['units'])
    assert phone_request(tmp_path)['chat_script_review'] is True


def test_thread_isolation_correct_outgoing_identity_and_fixed_chrome():
    script=phone_script();beats=compile_beats(script)
    frame,state=story_frame(script,4,1.5,3,.16)
    assert state['thread_id']=='wife' and state['contact']=='Mira' and state['theme']=='sage'
    assert state['camera_zoom']==1
    assert state['outgoing_speaker']=='Ari' # First message was from Unknown.
    assert set(state['visible_unit_ids'])=={'u3','u4'}
    assert not {'u0','u1','u2','u5'}&set(state['visible_unit_ids'])
    before,bstate=story_frame(script,13,.5,3,.38)
    after,astate=story_frame(script,13,1.5,3,.38)
    assert astate['camera_zoom']>1 and not ImageChops.difference(before,after).getbbox() is None
    assert ImageChops.difference(before.crop((0,0,720,210)),after.crop((0,0,720,210))).getbbox() is None
    assert beats[3]['events'][0]['type']=='switch'


def test_events_do_not_shorten_reading_and_blackout_is_black_and_silent(tmp_path):
    ws=Workspace(tmp_path/'ws');req=phone_request(tmp_path);script=phone_script();job=ws.create('entertainment',req)
    timing=reading_timing(ws,job,script,tmp_path/'timing');row=timing['units'][9]
    blackout=next(e for e in row['screen_events'] if e['type']=='blackout')
    second=(blackout['start']+blackout['end'])/2
    picture,state=story_frame(script,9,second,row['duration'],row['typing_seconds'])
    assert state['screen']=='blackout' and picture.getbbox() is None
    with wave.open(timing['audio'],'rb') as sound:
        rate=sound.getframerate();sound.setpos(round((row['start']+blackout['start']+.1)*rate))
        data=array('h',sound.readframes(round((blackout['end']-blackout['start']-.2)*rate)))
    assert max(abs(v) for v in data)==0
    assert row['arrival']>=row['start']+row['prefix_seconds'] and row['hold_seconds']>=1.05
    assert all(r['end']<=n['start']+.001 for r,n in zip(timing['units'],timing['units'][1:]))


def verdict(script,passes=True):
    return {'passes':passes,'opening_unit_id':'u0','opening_quote':script['units'][0]['text'],
            'payoff_unit_id':'u13','payoff_quote':script['units'][-1]['text'],
            'clue_unit_id':'u2','clue_quote':script['units'][2]['text'],
            'issues':[] if passes else ['The final reply repeats an earlier answer.'],'reason':'Synthetic fixture verdict.'}


def test_writing_review_uses_exact_evidence_and_has_bounded_revision():
    script=phone_script();calls=[]
    class Reviewer:
        def generate(self,purpose,*args):
            calls.append(purpose)
            if purpose=='chat-script-revision-v1':return deepcopy(script)
            return verdict(script,passes=len(calls)>1)
    result,record=reviewed_script(Reviewer(),script,{}, {},lambda x:x,'thriller')
    assert len(calls)==3 and record['revisions']==1 and result==script
    class Fabricated:
        def generate(self,*args):return {**verdict(script),'clue_quote':'A line never written'}
    with pytest.raises(Held,match='quote existing'):critique(Fabricated(),script,'thriller')
    class AlwaysFails:
        def generate(self,purpose,*args):return script if purpose.endswith('revision-v1') else verdict(script,False)
    with pytest.raises(Held,match='still fails'):reviewed_script(AlwaysFails(),script,{}, {},lambda x:x,'thriller')


def test_openai_adapter_is_explicit_cached_and_keeps_keys_out_of_payload(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');cfg=ws.config();cfg['text_provider']='openai'
    cfg['openai'].update(api_usage_enabled=True,model='explicit-test-model',key_env='OPENAI_API_KEY_STORY');ws.save_config(cfg)
    monkeypatch.setenv('OPENAI_API_KEY_STORY','synthetic-test-secret-123456');calls=[]
    def transport(body):
        calls.append(body)
        return {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'{"answer":"ok","optional":null}'}]}]}
    provider=OpenAI(ws,transport)
    schema={'type':'object','properties':{'answer':{'type':'string'},'optional':{'type':'string'}},'required':['answer'],'additionalProperties':False}
    assert provider.generate('fixture',{},schema)=={'answer':'ok'}
    assert provider.generate('fixture',{},schema)=={'answer':'ok'} and len(calls)==1
    assert calls[0]['store'] is False and 'synthetic-test-secret' not in json.dumps(calls)
    assert strict_schema(schema)['required']==['answer','optional']
    assert isinstance(configured_provider(ws),OpenAI)
    assert 'synthetic-test-secret' not in redact('failed synthetic-test-secret-123456')
    cfg['openai']['api_usage_enabled']=False;ws.save_config(cfg)
    with pytest.raises(Held,match='Enable OpenAI'):provider.generate('new',{},schema)


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
def test_phone_format_runs_through_normal_pipeline_with_writer_and_review_only(tmp_path):
    from yt_pipeline.pipeline import Pipeline
    ws=Workspace(tmp_path/'ws');script=phone_script();calls=[]
    job=ws.create('entertainment',phone_request(tmp_path))
    class StoryModel:
        def generate(self,purpose,*args,**kwargs):
            calls.append(purpose)
            if purpose=='scripter-v3':return deepcopy(script)
            if purpose=='chat-script-review-v1':return verdict(script)
            raise AssertionError('No model editing or direction is allowed.')
    def no_voice(*args,**kwargs):raise AssertionError('Phone story must not call TTS.')
    result=Pipeline(ws,provider=StoryModel(),voice_fn=no_voice).run(job['id'])
    assert result['status']=='ready',result.get('message')
    assert calls==['scripter-v3','chat-script-review-v1']
    qa=json.loads(Path(result['artifacts']['quality']['path']).read_text())
    assert qa['technical_pass'] and qa['width']==720 and qa['height']==1280
    Pipeline(ws,provider=StoryModel(),voice_fn=no_voice).run(job['id'])
    assert len(calls)==2


def test_provider_config_and_gemini_wire_schema_keep_local_limits(tmp_path,monkeypatch):
    from yt_pipeline.cli import config_set,doctor
    from yt_pipeline.writer import Gemini,gemini_wire_schema
    from yt_pipeline.contracts import SCRIPT_SCHEMA
    ws=Workspace(tmp_path/'config-ws')
    assert config_set(ws,'openai.model','account-selected-model')['value']=='account-selected-model'
    assert config_set(ws,'openai.api_usage_enabled',True)['value'] is True
    config_set(ws,'gemini.key_env','GEMINI_API_KEY_STORY')
    with pytest.raises(ValueError):config_set(ws,'gemini.key_env','not-an-env-key')
    with pytest.raises(ValueError):config_set(ws,'text_provider','automatic')
    schema=deepcopy(SCRIPT_SCHEMA);schema['properties']['units']['minItems']=12
    wire=gemini_wire_schema(schema)
    assert 'minItems' not in wire['properties']['units']
    assert schema['properties']['units']['minItems']==12
    monkeypatch.setenv('GEMINI_API_KEY_STORY','synthetic-story-key-only')
    assert doctor(ws)['selected_key_present'] is True
    calls=[]
    cfg=ws.config();cfg['gemini']['free_tier_confirmed']=True;ws.save_config(cfg)
    def transport(model,body):
        calls.append(body)
        return {'candidates':[{'content':{'parts':[{'text':'{"status":"ok"}'}]}}]}
    assert Gemini(ws,transport).generate('fixture',{}, {'type':'object','properties':{'status':{'type':'string'}}})=={'status':'ok'}
    assert 'synthetic-story-key-only' not in json.dumps(calls)


def test_late_clue_cannot_be_passed_as_early_plant():
    script=phone_script()
    class LateClue:
        def generate(self,*args):return {**verdict(script),'clue_unit_id':'u10','clue_quote':script['units'][10]['text']}
    result=critique(LateClue(),script,'thriller')
    assert result['passes'] is False and 'first third' in result['issues'][-1]


def test_battery_warning_can_causally_precede_blackout_in_earlier_beat():
    script=phone_script();beats=script['phone_story']['beats']
    beats[8]['events']=['low_battery'];beats[9]['events']=['blackout','time_jump','notification']
    assert validate_phone_story(script['phone_story'],script['units'])
    beats[8]['events']=[]
    with pytest.raises(Held,match='Plant a battery'):validate_phone_story(script['phone_story'],script['units'])
