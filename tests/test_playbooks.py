from copy import deepcopy
import json
from pathlib import Path

import pytest
from PIL import Image

from yt_pipeline.core import Workspace,Held,digest
from yt_pipeline.creative_plan import validate_plan,plan_edit
from yt_pipeline.playbooks import get_playbook,validate_playbook_script
from yt_pipeline.edit_blocks import capabilities,require_renderer
from yt_pipeline.writer import write_script
from yt_pipeline.contracts import brief_contract
from yt_pipeline.assets import register_asset,asset_record
from yt_pipeline.planned_visuals import build_planned_visuals
from yt_pipeline.creative_plan import active_speaker_scene
from yt_pipeline.dialogue_captions import exact_words,progressive_cues


def draft():
    lines=['My phone received a message from my missing sister at midnight.',
           'She asked me to meet beside the elevator behind our library.',
           'The lights stopped flickering when I reached the empty landing upstairs.',
           'Another message told me to wait because someone was coming down.',
           'Then I heard her familiar ringtone playing inside the locked cupboard.',
           'I opened it and found the old phone we buried last summer.',
           'Its screen showed a scheduled message dated before she went missing.',
           'The final instruction pointed to the key hidden under its battery.']
    return {'version':1,'title':'The scheduled message','description':'Original fictional mystery.','format':'lesson','fiction':True,
      'hook':lines[0],'payoff':lines[-1],
      'units':[{'id':f'u{i}','speaker':'Narrator','text':v,'kind':'fiction','claim_ids':[],'onscreen':'The scheduled message','visual_query':'dark empty library','visual_kind':'image'} for i,v in enumerate(lines)],
      'edit':{'effect':'none','payoff_unit_id':'u7','cta':False}}


def plan(script):
    return {'version':1,'template':'story_stock','cast':[{'id':'narrator','speaker':'Narrator','role':'anchor','avatar_kind':'narrator','avatar_query':'','voice_id':'af_heart','costume':''}],
      'scenes':[{'unit_id':u['id'],'text':u['text'],'speaker_id':'narrator','stage':'hook' if i==0 else 'payoff' if i==7 else 'clue',
       'background_query':'dark empty library','visual_query':'phone in hand','asset_id':'','visible_cast':[],'focus_id':'','framing':'wide','motion':'hold','emotion':'concerned','pause_after':.3,'sound_cue':'none'} for i,u in enumerate(script['units'])],
      'music_mood':'eerie atmospheric','opening_promise':'Who sent this message?','delivered_payoff':'The phone reveals it was scheduled before the disappearance.',
      'comment_question':'','review':{'payoff_delivered':True,'hook_honest':True,'no_invented_evidence':True,'continuity_consistent':True,'issues':[]}}


def test_genre_delivery_and_length_are_distinct():
    horror=get_playbook('horror_stock');chat=get_playbook('tea_chat');edu=get_playbook('education_demo')
    assert horror['voice']['voice_id'].startswith('af_')
    assert horror['voice']['length_scale']>chat['voice']['length_scale']
    assert horror['voice']['pause']>chat['voice']['pause']
    assert horror['music']['category']=='horror'
    assert 'asmr' not in get_playbook('aura_progression')['bottom']
    assert edu['voice']['voice_id']=='am_adam'
    assert validate_playbook_script(draft(),'horror_stock')['words']>=70
    short=draft();short['units']=short['units'][:2]
    with pytest.raises(Held) as e:validate_playbook_script(short,'horror_stock')
    assert e.value.code=='playbook_length'


def test_each_actor_gets_the_same_active_speaker_blocking():
    cast=[{'id':'alex','avatar_kind':'cat'},{'id':'mike','avatar_kind':'dog'}]
    for speaker,framing in [('alex','closeup'),('mike','medium')]:
        original={'speaker_id':speaker,'framing':framing,'visible_cast':['alex','mike'],'focus_id':'alex'}
        resolved=active_speaker_scene(original,cast)
        assert resolved['framing']=='closeup' and resolved['visible_cast']==[speaker] and resolved['focus_id']==speaker
        assert original['visible_cast']==['alex','mike']


@pytest.mark.parametrize('supported',[True,False])
def test_factual_playbook_combines_review_without_skipping_evidence(tmp_path,supported):
    ws=Workspace(tmp_path/'workspace');script=draft();script['fiction']=False
    script['hook']=script['units'][0]['text'];script['payoff']=script['units'][-1]['text']
    for unit in script['units']:unit.update(kind='instruction',claim_ids=[])
    value=plan(script);value['template']='education_demo'
    value['scenes'][0]['graphic']={'kind':'process','title':'Example','labels':[script['units'][0]['onscreen']]}
    value['evidence_review']={'supported':supported,'issues':[] if supported else ['Unsupported assertion.']}
    brief=brief_contract({'title':'Test evidence','question':'Test?','kind':'fact','sources':[
        {'id':'s','url':'https://example.com/fixture','title':'Synthetic test evidence','excerpt':'Technical fixture, not real advice.','checked_at':'2026-11-02T00:00:00+00:00'}],'claims':[]})
    calls=[]
    class Provider:
        def generate(self,purpose,prompt,schema):
            calls.append(purpose)
            if purpose=='scripter-v3':
                assert schema['properties']['fiction']['enum']==[False]
                assert 'fiction' not in schema['properties']['units']['items']['properties']['kind']['enum']
                return deepcopy(script)
            assert purpose=='creative-director-evidence-v1'
            assert prompt['brief']['sources'] and 'evidence_review' in schema['required']
            return deepcopy(value)
    job=ws.create('education',{'playbook':'education_demo','topic':'Evidence fixture','motion_graphics':True})
    if supported:
        result=write_script(ws,job,brief,Provider())
        assert result['review']['supported'] and result['review']['method']=='gemini_evidence_and_director_review'
        assert result['creative_plan']['plan']['scenes'][0]['graphic']=={'kind':'callout','title':'Example','labels':[script['units'][0]['onscreen']]}
    else:
        with pytest.raises(Held) as error:write_script(ws,job,brief,Provider())
        assert error.value.code=='unsupported_claim'
    assert calls==['scripter-v3','creative-director-evidence-v1']


def test_character_clothing_does_not_change_when_cast_order_changes():
    from yt_pipeline.cast_body import shirt_color
    alex={'speaker':'Alex'};mike={'speaker':'Mike'}
    first={r['speaker']:shirt_color(r) for r in [alex,mike]}
    second={r['speaker']:shirt_color(r) for r in [mike,alex]}
    assert first==second and first=={'Alex':'#325c9a','Mike':'#ad493a'}


def test_subtitles_keep_every_original_word_and_reveal_on_audio_times():
    text="You charged me for my own chair?"
    words=text.split();alignment=[{'word':(' ' if i else '')+w,'start':i*.2,'end':(i+1)*.2} for i,w in enumerate(words)]
    aligned=exact_words(text,alignment,1.4);cues=progressive_cues(aligned)
    assert ' '.join(w['text'] for w in aligned)==text
    assert len(cues)==len(words) and cues[0]['text']=='You'
    assert cues[-1]['text'].endswith('chair?')
    assert all(c['start']==w['start'] for c,w in zip(cues,aligned))
    with pytest.raises(Held,match='complete spoken script'):exact_words(text,alignment[:-1],1.4)


def test_zero_length_alignment_is_locally_repaired_without_dropping_word():
    aligned=exact_words('a real word',[{'word':'a','start':0,'end':.5},{'word':' real','start':.5,'end':.5},{'word':' word','start':.5,'end':1}],1)
    assert [r['text'] for r in aligned]==['a','real','word']
    assert all(r['start']<r['end'] for r in aligned)
    assert any(r.get('timing_estimated') for r in aligned)
    assert len(progressive_cues(aligned))==3


def test_comedy_review_must_identify_the_actual_final_spoken_punchline():
    from yt_pipeline.comedy import review_comedy
    script={'units':[{'id':'start','text':'Using my cushion costs two dollars.'},{'id':'end','text':'Cancelling costs ten.'}],
            'edit':{'payoff_unit_id':'end'}}
    class Provider:
        def generate(self,*args):return {'passes':True,'works_with_static_cast':True,'issues':[],
            'setup_unit_id':'start','punchline_unit_id':'end','punchline_exact_text':'A stronger joke that is not actually spoken.',
            'reversal_explanation':'The original rule turns against the person who introduced it.'}
    with pytest.raises(Held) as error:review_comedy(Provider(),script,None)
    assert error.value.code=='creative_review'


@pytest.mark.parametrize('mutation,code',[
    (lambda p:p['scenes'][0].update(text='New invented dialogue'),'creative_rewrite'),
    (lambda p:p['scenes'][0].update(speaker_id='someone_else'),'creative_speaker'),
    (lambda p:p['scenes'][0].update(asset_id='invented-file'),'creative_asset'),
    (lambda p:p['scenes'][-1].update(stage='question'),'creative_payoff'),
    (lambda p:p['review'].update(payoff_delivered=False),'creative_review'),
    (lambda p:p['scenes'][0].update(pause_after=10),'creative_pause'),
    (lambda p:p['cast'][0].update(voice_id='am_adam'),'creative_cast'),
])
def test_director_cannot_rewrite_or_invent_capabilities(mutation,code):
    script=draft();value=plan(script);mutation(value)
    with pytest.raises(Held) as e:validate_plan(value,script,'horror_stock')
    assert e.value.code==code


def test_writer_then_director_keeps_exact_original_dialogue(tmp_path):
    ws=Workspace(tmp_path/'workspace');script=draft();directed=plan(script);calls=[]
    class Provider:
        def generate(self,purpose,prompt,schema):
            calls.append((purpose,prompt));return deepcopy(script if purpose.startswith('scripter') else directed)
    job=ws.create('entertainment',{'playbook':'horror_stock','fiction':True,'topic':script['title']})
    brief=brief_contract({'title':script['title'],'question':'Who sent the message?','kind':'fiction','sources':[],'claims':[]})
    result=write_script(ws,job,brief,Provider())
    assert [x[0] for x in calls]==['scripter-v3','creative-director-v1']
    assert result['origin']=='gemini'
    assert result['creative_plan']['script_sha256']==digest(result['script'])
    assert [s['text'] for s in result['creative_plan']['plan']['scenes']]==[u['text'] for u in result['script']['units']]
    assert calls[1][1]['edit_blocks']
    assert capabilities('premiere')['adapter_implemented'] is False
    with pytest.raises(Held):require_renderer('after_effects')


@pytest.mark.parametrize('always_bad',[False,True])
def test_substantive_director_critique_gets_at_most_one_script_rewrite(tmp_path,always_bad):
    ws=Workspace(tmp_path/'workspace');script=draft();calls=[];directors=0
    class Provider:
        def generate(self,purpose,prompt,schema):
            nonlocal directors
            calls.append(purpose)
            if purpose in ('scripter-v3','creative-script-rewrite-v1'):return deepcopy(script)
            assert purpose=='creative-director-v1'
            directors+=1;value=plan(script)
            if directors==1 or always_bad:value['review'].update(continuity_consistent=False,issues=['The cause is not coherent.'])
            return value
    job=ws.create('entertainment',{'playbook':'horror_stock','fiction':True,'topic':script['title']})
    brief=brief_contract({'title':script['title'],'question':'Who sent it?','kind':'fiction','sources':[],'claims':[]})
    if always_bad:
        with pytest.raises(Held) as error:write_script(ws,job,brief,Provider())
        assert error.value.code=='creative_review'
    else:
        result=write_script(ws,job,brief,Provider());assert result['creative_rewrites']==1 and result['origin']=='gemini'
    assert calls==['scripter-v3','creative-director-v1','creative-script-rewrite-v1','creative-director-v1']


def test_hook_cannot_exist_only_in_metadata():
    value=draft();value['hook']='A much stronger hook which nobody actually says.'
    with pytest.raises(Held,match='first spoken unit'):validate_playbook_script(value,'horror_stock')


def test_actual_directed_stock_scene_uses_asset_and_small_captions(tmp_path):
    ws=Workspace(tmp_path/'workspace');image=tmp_path/'stock.png';Image.new('RGB',(720,1280),'#253343').save(image)
    source=register_asset(ws,image,'test',{'reference':'Technical stock fixture'})
    script=draft();script['units']=script['units'][:1];value=plan(draft());value['scenes']=value['scenes'][:1]
    value['scenes'][0]['asset_id']=source['id']
    timing={'units':[{'id':'u0','start':0,'speech_end':1,'duration':1.2,'text':script['units'][0]['text']}]}
    folder=tmp_path/'visuals';record={'plan':value,'script_sha256':digest(script)}
    result=build_planned_visuals(ws,{'request':{'media_assets':{},'test_only':True}},script,timing,folder,record)
    assert len(result['frames'])==1
    assert asset_record(ws,result['frames'][0]['media_id'])['duration']>1
    assert result['planned_provenance'][0]['id']==source['id']
    assert 'My phone' in Path(result['captions']).read_text()


def test_asset_kind_and_cache_do_not_replace_requested_video_with_image(monkeypatch):
    from yt_pipeline import planned_visuals as renderer
    calls=[]
    def acquire(ws,query,kind):calls.append(kind);return {'kind':kind}
    monkeypatch.setattr(renderer,'acquire_visual',acquire);cache={}
    assert renderer.resolve_asset(None,None,'typing',cache,'image')['kind']=='image'
    assert renderer.resolve_asset(None,None,'typing',cache,'video')['kind']=='video'
    renderer.resolve_asset(None,None,'typing',cache,'video')
    assert calls==['image','video']


@pytest.mark.parametrize('case,code',[('stale_bottom','creative_layout'),('missing_essential','essential_visual_missing'),('unreviewed_essential','essential_visual_unreviewed')])
def test_layout_and_essential_visuals_hold_before_random_stock_acquisition(tmp_path,monkeypatch,case,code):
    from yt_pipeline import planned_visuals as renderer
    ws=Workspace(tmp_path/'workspace');script=draft();script['units']=script['units'][:1]
    value=plan(draft());value['scenes']=value['scenes'][:1];value['template']='education_demo'
    request={'bottom_kind':'none'}
    if case=='stale_bottom':request['bottom_asset_id']='stale'
    if case=='unreviewed_essential':value['scenes'][0]['asset_id']='supplied-but-unreviewed'
    def forbidden(*args):pytest.fail('A missing factual demonstration must not trigger generic stock search')
    monkeypatch.setattr(renderer,'acquire_visual',forbidden)
    timing={'units':[{'id':'u0','start':0,'speech_end':1,'duration':1.2,'text':script['units'][0]['text']}]}
    with pytest.raises(Held) as error:
        build_planned_visuals(ws,{'request':request},script,timing,tmp_path/'visuals',{'plan':value,'script_sha256':digest(script)})
    assert error.value.code==code


def test_actual_video_scene_keeps_rank_and_executes_planned_camera(tmp_path,monkeypatch):
    import subprocess
    from yt_pipeline import planned_visuals as renderer
    source=tmp_path/'source.mp4'
    subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-f','lavfi','-i','testsrc2=size=160x240:rate=30','-t','0.5',
        '-c:v','libx264','-threads','1',str(source)],check=True,capture_output=True)
    ws=Workspace(tmp_path/'workspace');source_asset=register_asset(ws,source,'test',{'purpose':'Camera/rank technical fixture'})
    asset=asset_record(ws,source_asset['id']);output=tmp_path/'ranked.mp4';calls=[];real=renderer._camera_filter
    def camera(duration,motion,height,repeat):calls.append((motion,repeat));return real(duration,motion,height,repeat)
    monkeypatch.setattr(renderer,'_camera_filter',camera)
    renderer._video_scene(asset,'Example title',.5,output,832,rank=9,motion='pan_right')
    assert calls==[('pan_right',False)]
    with Image.open(output.with_suffix('.caption.png')) as plate:assert plate.getpixel((32,50))[-1]==255
    registered=register_asset(ws,output,'test',{'purpose':'Actual video result'})
    assert asset_record(ws,registered['id'])['duration']>=.49
