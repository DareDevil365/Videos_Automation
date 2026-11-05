from copy import deepcopy
from pathlib import Path
import json
import shutil
import subprocess

import pytest
from PIL import Image,ImageChops

from yt_pipeline.core import Workspace,Held
from yt_pipeline.phone_editor.writing import (CRITERIA,diagnose,reviewed_script,unpack_draft,validate_anchors)
from yt_pipeline.phone_editor.attachments import Attachment
from yt_pipeline.phone_editor.messenger import chat_frame


ROOT=Path(__file__).resolve().parents[1]


def script():return json.loads((ROOT/'examples/assistant-five/comedy-chat.json').read_text(encoding='utf-8'))


def diagnostic(s,revise=False):
    checks={key:{'verdict':'pass','unit_id':s['units'][0]['id'],'quote':s['units'][0]['text'],'reason':'Fixture evidence only.'} for key in CRITERIA}
    checks['payoff'].update(unit_id=s['units'][-1]['id'],quote=s['units'][-1]['text'])
    if revise:checks['cause']['verdict']='revise'
    return {'reader_question':'Why did the boss join?','reader_answer':'Literal invitation expands upward.','missing_assumptions':[],'checks':checks}


def envelope(s):
    options=[{'situation':'Technical original fixture','conflicting_wants':'Different ordinary priorities.',
              'opening':s['units'][0]['text'],'early_plant':s['units'][1]['text'],'ending':s['units'][-1]['text'],
              'cause':'An earlier literal request causes a later consequence.','mechanism':m} for m in ('literal interpretation','escalating commitment','changed-meaning callback')]
    return {'sketches':options,'selected_index':0,'script':s}


def test_planning_records_ending_before_script_and_checks_actual_anchors():
    s=script();raw=envelope(s);parsed,development=unpack_draft(raw);validate_anchors(parsed,development)
    changed=deepcopy(parsed);changed['units'][-1]['text']='A different arbitrary ending.'
    with pytest.raises(Held,match='selected opening'):validate_anchors(changed,development)
    raw['sketches'][1]['mechanism']=raw['sketches'][0]['mechanism']
    with pytest.raises(Held,match='Vary'):unpack_draft(raw)


def test_cold_reader_is_not_primed_with_writer_pitch_or_favorable_metadata():
    s=script();captured=[]
    class Reader:
        def generate(self,purpose,body,schema):
            assert purpose=='chat-cold-reader-v2';captured.append(body);return diagnostic(s)
    result=diagnose(Reader(),s,'comedy')
    assert result['passes'] and not {'title','hook','payoff','description','story_development','selected_story'}&set(captured[0])
    assert set(captured[0]['messages'][0])=={'id','speaker','text'}


def test_all_criteria_and_exact_evidence_are_required_even_when_reviewer_is_positive():
    s=script()
    class Reader:
        def __init__(self,value):self.value=value
        def generate(self,*args):return self.value
    value=diagnostic(s);value['missing_assumptions']=['A cause is absent.']
    assert diagnose(Reader(value),s,'comedy')['passes'] is False
    value=diagnostic(s);value['checks']['voice']['quote']='Invented proof'
    with pytest.raises(Held,match='quote real dialogue'):diagnose(Reader(value),s,'comedy')
    value=diagnostic(s);del value['checks']['knowledge']
    with pytest.raises(Held,match='every writing criterion'):diagnose(Reader(value),s,'comedy')
    repeated=deepcopy(s);repeated['units'][-1]['text']=repeated['units'][0]['text']
    assert diagnose(Reader(diagnostic(repeated)),repeated,'comedy')['passes'] is False


def test_revision_retains_original_owner_brief_and_bounds_and_is_bounded():
    s=script();calls=[];context={'owner_constraints':'Only phone messages. No magic technology.','bounds':{'units':[8,20],'words':[35,105]},'tone':'comedy'}
    class Writer:
        def generate(self,purpose,body,schema):
            calls.append((purpose,body))
            if purpose=='chat-script-revision-v2':return deepcopy(s)
            return diagnostic(s,revise=len(calls)==1)
    final,review=reviewed_script(Writer(),s,{}, {},lambda x:x,'comedy',context=context,version=2)
    assert len(calls)==3 and calls[1][1]['writing_constraints']==context and review['revisions']==1


def test_normal_writer_route_uses_clean_chat_brief_and_no_stock_or_narration_tasks(tmp_path):
    from yt_pipeline.writer import write_script
    from yt_pipeline.contracts import brief_contract
    ws=Workspace(tmp_path/'ws');s=script();calls=[]
    request={'playbook':'server_chat','chat_editing_version':2,'chat_writing_version':2,'chat_script_review':True,
             'fiction':True,'test_only':True,'topic':'A technical chat fixture','creative_brief':'Keep the whole story inside the chat.'}
    job=ws.create('entertainment',request)
    class Writer:
        def generate(self,purpose,body,schema):
            calls.append((purpose,body,schema))
            if purpose=='chat-story-draft-v2':return envelope(deepcopy(s))
            if purpose=='chat-cold-reader-v2':return diagnostic(s)
            raise AssertionError('No model directing or other generation is allowed: '+purpose)
    result=write_script(ws,job,brief_contract({'title':'Fixture','question':'A fixture?','kind':'fiction','claims':[],'sources':[]}),Writer())
    assert [c[0] for c in calls]==['chat-story-draft-v2','chat-cold-reader-v2']
    assert not {'visual_brief','scene_direction','hook_selection','motion_graphics'}&set(calls[0][1])
    props=calls[0][2]['properties']['script']['properties']['units']['items']['properties']
    assert 'visual_query' not in props and result['story_development']['anchor_status']=='retained'


def test_registered_gif_is_animated_and_never_revealed_before_message(tmp_path):
    first=Image.new('RGBA',(50,50),'red');second=Image.new('RGBA',(50,50),'blue');path=tmp_path/'reaction.gif'
    first.save(path,save_all=True,append_images=[second],duration=[100,100],loop=0)
    gif=Attachment(path);assert gif.animated and ImageChops.difference(gif.at(.05).convert('RGB'),gif.at(.15).convert('RGB')).getbbox()
    s=script();settings={'attachments':{'u8':gif},'contact':'Family'}
    _,before=chat_frame(s,7,0,3,.16,settings=settings)
    _,after=chat_frame(s,7,.5,3,.16,settings=settings)
    assert before['visible_attachments']==[] and after['visible_attachments']==['u8']


def test_portrait_art_frame_keeps_requested_dimensions():
    from yt_pipeline.illustrated_story import story_frame
    image=Image.new('RGB',(900,1200),'#abcdef')
    assert story_frame(image,{},1,3,canvas=(720,1280)).size==(720,1280)


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
def test_clean_aura_renders_portrait_video_and_freeze_without_legacy_score_panel(tmp_path):
    from yt_pipeline.entertainment import aura_scene
    from shorts_editor.store import probe
    source=tmp_path/'source.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=green:s=180x320:r=30:d=1.2',
                    '-c:v','libx264','-threads','1','-pix_fmt','yuv420p',str(source)],check=True)
    s={'units':[{'id':'u1','onscreen':'ONE MORE.'}]}
    made=aura_scene(s,0,{'kind':'video','path':str(source),'duration':1.2},1,tmp_path,progression=True,clean=True,motion='hold')
    stream=next(r for r in probe(made)['streams'] if r['codec_type']=='video')
    assert (stream['width'],stream['height'])==(720,1280)
    overlay=Image.open(made.with_suffix('.caption.png')).convert('RGBA')
    assert overlay.getpixel((50,80))[3]==0 # No top score decoration.
    still=tmp_path/'freeze.png';Image.new('RGB',(180,320),'blue').save(still)
    freeze=aura_scene({'units':[{'id':'u2','onscreen':'LET THAT ANSWER.'}]},0,{'kind':'image','path':str(still)},1,tmp_path,progression=True,clean=True)
    stream=next(r for r in probe(freeze)['streams'] if r['codec_type']=='video')
    assert (stream['width'],stream['height'])==(720,1280)


def test_portrait_canvas_and_registered_attachment_configuration_are_explicit():
    from yt_pipeline.playbooks import prepare_request
    with pytest.raises(Held):prepare_request({'playbook':'illustrated_story','story_canvas':'accidentally-wide'})
    with pytest.raises(Held):prepare_request({'playbook':'server_chat','chat_editing_version':2,'chat_attachment_ids':['not-a-map']})
