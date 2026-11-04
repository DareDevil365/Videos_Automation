from copy import deepcopy
import json
import shutil
import subprocess

import pytest
from PIL import Image

from yt_pipeline.core import Workspace,Held,digest
from yt_pipeline.server_chat import server_chat_frame,render_server_message,message_layout,speaker_color
from yt_pipeline.planned_visuals import build_planned_visuals
from yt_pipeline.playbooks import prepare_request,validate_playbook_script


def script_fixture():
    units=[{'id':f'u{i}','speaker':'Milo' if i%2==0 else 'Nova',
        'text':f'This is technical message number {i} for the scrolling fixture.',
        'onscreen':f'This is technical message number {i} for the scrolling fixture.',
        'kind':'fiction','claim_ids':[],'visual_query':'fictional server chat','visual_kind':'image'} for i in range(16)]
    for unit in units:unit.update(text=unit['text'].replace('for the scrolling fixture.','fixture.'),onscreen=unit['onscreen'].replace('for the scrolling fixture.','fixture.'))
    return {'version':1,'title':'Technical server-chat fixture','description':'Original technical fictional fixture.',
        'format':'chat','fiction':True,'hook':units[0]['text'],'payoff':units[-1]['text'],'units':units,
        'edit':{'effect':'none','payoff_unit_id':'u15','cta':False}}


def test_full_screen_chat_preserves_messages_and_hides_the_future():
    script=script_fixture();original=deepcopy(script)
    frame,start=server_chat_frame(script,8,0)
    final,end=server_chat_frame(script,8,1)
    assert frame.size==final.size==(720,1280) and end['scroll_offset']>start['scroll_offset']
    assert end['active_unit_id']=='u8' and 'u8' in end['visible_unit_ids']
    assert not {'u9','u10','u11'}&set(end['visible_unit_ids'])
    assert 'u0' not in end['visible_unit_ids'] and script==original
    assert speaker_color('Milo')==speaker_color('Milo')
    assert len(set(end['speaker_colors'].values()))==len(end['speaker_colors'])


def test_chat_contract_rejects_hidden_speech_narrator_and_unreadable_messages():
    script=script_fixture();assert validate_playbook_script(script,'server_chat')['words']>85
    script['units'][3]['onscreen']='A paraphrase that omits spoken text'
    with pytest.raises(Held,match='verbatim'):validate_playbook_script(script,'server_chat')
    script=script_fixture();script['units'][0]['speaker']='Narrator'
    with pytest.raises(Held,match='no narrator'):validate_playbook_script(script,'server_chat')
    script=script_fixture();script['units'][0]['text']='Averylongunbreakableword '*70
    with pytest.raises(Held,match='readable lines'):message_layout(script)
    with pytest.raises(Held,match='frame'):prepare_request({'playbook':'server_chat','bottom_kind':'asmr'})


def test_program_selects_concept_writes_and_reviews_chat_without_provided_dialogue(tmp_path):
    from yt_pipeline.writer import write_script
    from yt_pipeline.contracts import brief_contract
    from yt_pipeline.creative_plan import validate_plan
    script=script_fixture();ws=Workspace(tmp_path/'ws');calls=[]
    cast=[{'id':'a','speaker':'Milo','role':'participant','avatar_kind':'narrator','avatar_query':'','voice_id':'am_adam','costume':''},
          {'id':'b','speaker':'Nova','role':'participant','avatar_kind':'narrator','avatar_query':'','voice_id':'af_bella','costume':''}]
    plan={'version':1,'template':'server_chat','cast':cast,'scenes':[
        {'unit_id':u['id'],'text':u['text'],'speaker_id':'a' if i%2==0 else 'b','stage':'payoff' if i==15 else 'hook' if i==0 else 'setup',
         'background_query':'fictional server chat','visual_query':'fictional server chat','asset_id':'','visible_cast':[],'focus_id':'',
         'framing':'wide','motion':'hold','emotion':'calm','pause_after':.1,'sound_cue':'none','rank':0,'display_title':''}
        for i,u in enumerate(script['units'])], 'music_mood':'none','opening_promise':'Technical fictional test promise.',
        'delivered_payoff':'Technical fictional fixture payoff.','comment_question':'',
        'review':{**{k:True for k in ['payoff_delivered','hook_honest','no_invented_evidence','continuity_consistent']},'issues':[]}}
    class Provider:
        workspace=ws
        def generate(self,purpose,content,schema):
            calls.append(purpose)
            if purpose=='comedy-concepts-v1':
                assert content['chat_direction']
                return {'concepts':[{'id':str(i),'hook':'Technical hook.','final_punchline':'Technical consequence.'} for i in range(3)]}
            if purpose=='comedy-concept-selector-v1':return {'selected_id':'0','reason':'Technical fixture.','passes':True,'issues':[]}
            if purpose=='scripter-hooks-v1':
                assert content['selected_story_concept']['selected']['id']=='0'
                return {'script':deepcopy(script),'selected_hook_index':0,'hook_options':[
                    {'type':kind,'first_line':line,'first_caption':line,'first_frame':'Actual fictional chat.'} for kind,line in
                    [('story_reversal',script['hook']),('viewer_question','Which technical example applies?'),('surprising_specific','This is another technical example.')]]}
            if purpose=='comedy-script-review-v1':
                assert content['chat_payoff_check']
                return {'passes':True,'punchline_unit_id':'u15','punchline_exact_text':script['payoff'],
                    'setup_unit_id':'u0','reversal_explanation':'Technical exact-quote fixture for a planted consequence.',
                    'works_with_static_cast':True,'issues':[]}
            if purpose=='creative-director-v1':return deepcopy(plan)
            assert purpose=='independent-editorial-v1'
            return {'passes':True,'hook_honest':True,'hook_specific':True,'continuity_consistent':True,
                'opening_promise':'Technical promise.','payoff_unit_id':'u15','payoff_exact_text':script['payoff'],'reason':'Technical fixture.','issues':[]}
    job=ws.create('entertainment',{'playbook':'server_chat','fiction':True,'topic':'Original technical fixture'})
    brief=brief_contract({'title':script['title'],'question':'Technical fictional fixture?','kind':'fiction','sources':[],'claims':[]})
    result=write_script(ws,job,brief,Provider())
    assert result['origin']=='gemini' and result['comedy_concept']['selected']['id']=='0'
    assert calls==['comedy-concepts-v1','comedy-concept-selector-v1','scripter-hooks-v1','comedy-script-review-v1','creative-director-v1','independent-editorial-v1']
    plan['cast'][1]['voice_id']='am_adam'
    with pytest.raises(Held,match='distinct'):validate_plan(plan,script,'server_chat')


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
def test_real_message_animation_and_pipeline_use_no_stock_or_character_bodies(tmp_path,monkeypatch):
    script=script_fixture();script['units']=script['units'][:2]
    from yt_pipeline import planned_visuals
    def forbidden(*args,**kwargs):pytest.fail('Full-screen server chat must not acquire stock or cast faces')
    monkeypatch.setattr(planned_visuals,'acquire_visual',forbidden)
    ws=Workspace(tmp_path/'ws');timing={'units':[{'id':u['id'],'text':u['text'],'start':i*.5,'speech_end':i*.5+.4,'duration':.5} for i,u in enumerate(script['units'])]}
    plan={'template':'server_chat','cast':[],'scenes':[{'unit_id':u['id']} for u in script['units']]}
    result=build_planned_visuals(ws,{'request':{'playbook':'server_chat','test_only':True}},script,timing,tmp_path/'visuals',
        {'plan':plan,'script_sha256':digest(script)})
    assert all(row['kind']=='directed_server_chat' for row in result['frames'])
    assert not result['planned_provenance'] and not result['wardrobes']
    output=result['frames'][1]['file']
    info=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-of','json',output]))
    assert abs(float(info['format']['duration'])-.5)<.06
    pictures=[]
    for second in [0,.3]:
        data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(second),'-i',output,'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
        pictures.append(data)
    assert pictures[0]!=pictures[1]
