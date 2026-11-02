"""Editorial metadata/holds, exact delivery and real quiz timeline regressions."""
from copy import deepcopy
import json
import math
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace
import wave

from PIL import Image
import pytest

from yt_pipeline.core import Workspace, Held, digest, now
from yt_pipeline.contracts import brief_contract
from yt_pipeline.creative_plan import validate_plan
from yt_pipeline.playbooks import prepare_request
from yt_pipeline.pipeline import Pipeline
from yt_pipeline.script_quality import validate_hook, unpack_hooks, review_editorial
from yt_pipeline.speech_delivery import speech_segments
from yt_pipeline.scene_blocks import validate_block, block_frame, render_block
from yt_pipeline.voice import synthesize
from shorts_editor.store import probe


def episode(name='rewrite_reveal'):
    lines = [
        'This answer hides the work you actually did.',
        'Here is a fictional practice answer: I helped the team.',
        'That version gives no concrete action a listener can picture.',
        'Try this example instead: I checked the receipts against the delivery list.',
        'The improved answer names the action and the material you checked.',
        'Use your real experience and describe what you personally did in a specific situation.']
    if name == 'quiz_pause':
        lines = ['Which box can hold exactly two of these tokens?',
                 'This is an original puzzle with three tokens and two boxes.',
                 'One box holds one token; the other box holds two tokens.',
                 'Take a moment to choose the box with the larger capacity.',
                 'The second box holds two tokens, because its capacity was stated explicitly.']
    units = [{'id': f'u{i}', 'speaker': 'Narrator', 'text': line, 'onscreen': line,
              'kind': 'instruction', 'claim_ids': [], 'visual_query': 'original exact text diagram'} for i, line in enumerate(lines)]
    script = {'version': 1, 'title': 'Technical editorial fixture', 'description': 'Original technical test, not audience content.',
              'format': 'lesson', 'fiction': False, 'hook': lines[0], 'payoff': lines[-1], 'units': units,
              'edit': {'effect': 'none', 'payoff_unit_id': units[-1]['id'], 'cta': False}}
    scenes = [{'unit_id': u['id'], 'text': u['text'], 'speaker_id': 'n',
               'stage': 'hook' if i == 0 else 'payoff' if i == len(units)-1 else 'setup',
               'background_query': 'original typography', 'visual_query': u['visual_query'], 'asset_id': '',
               'visible_cast': [], 'focus_id': '', 'framing': 'wide', 'motion': 'hold', 'emotion': 'calm',
               'pause_after': .1, 'sound_cue': 'none', 'rank': 0, 'display_title': '',
               'graphic': {'kind': 'callout', 'title': 'Example', 'labels': [u['onscreen']]}} for i,u in enumerate(units)]
    if name == 'quiz_pause':
        scenes[3].update(thinking_seconds=3, graphic={'kind': 'timer', 'title': 'Question', 'labels': [lines[0]]})
    else:
        scenes[3]['graphic'] = {'kind': 'comparison', 'title': 'Myth and Fact' if name == 'myth_fact' else 'Before and After',
                                'headings': ['Myth', 'Fact'] if name == 'myth_fact' else ['Before', 'After'],
                                'labels': ['I helped the team', 'I checked the receipts']}
    plan = {'version': 1, 'template': 'education_demo', 'cast': [{'id': 'n', 'speaker': 'Narrator', 'role': 'narrator',
             'avatar_kind': 'narrator', 'avatar_query': '', 'voice_id': 'am_adam', 'costume': ''}],
            'scenes': scenes, 'music_mood': 'none', 'opening_promise': lines[0], 'delivered_payoff': lines[-1],
            'comment_question': '', 'review': {'payoff_delivered': True, 'hook_honest': True,
             'no_invented_evidence': True, 'continuity_consistent': True, 'issues': []}}
    return script, plan


def brief(verified=True):
    return brief_contract({'title': 'Original technical fixture', 'question': 'Does the implementation preserve its contract?',
        'kind': 'fact', 'editorial_verified': verified, 'sources': [{'id': 'fixture', 'url': 'https://example.com/technical-fixture',
        'title': 'Synthetic test-only evidence', 'excerpt': 'This is a controlled software fixture, not external advice or a real user outcome.',
        'checked_at': now()}], 'claims': []})


def envelope(script):
    return {'script': deepcopy(script), 'selected_hook_index': 0, 'hook_options': [
        {'type': 'mistake_then_fix', 'first_line': script['hook'], 'first_caption': script['units'][0]['onscreen'],
         'first_frame': 'Show the concrete existing example wording.'},
        {'type': 'visible_contrast', 'first_line': 'Two answers describe the same work differently.', 'first_caption': 'Compare both answers',
         'first_frame': 'Show two actual hypothetical answer phrases.'},
        {'type': 'viewer_question', 'first_line': 'Which answer names the actual action?', 'first_caption': 'Which answer is concrete?',
         'first_frame': 'Show the exact before and after phrases.'}]}


def verdict(script):
    return {'passes': True, 'hook_honest': True, 'hook_specific': True, 'continuity_consistent': True,
            'opening_promise': script['hook'], 'payoff_unit_id': script['edit']['payoff_unit_id'],
            'payoff_exact_text': script['units'][-1]['text'], 'reason': 'The exact ending answers the supplied controlled example.', 'issues': []}


def test_short_hooks_and_source_clip_metadata_are_not_globally_banned():
    script, _ = episode(); script['units'][0]['text'] = script['hook'] = 'Look closer.'
    assert validate_hook(script, 'rewrite_reveal', strict=True)
    script['units'][0]['text'] = 'Have you ever wondered about this?'; script['hook'] = script['units'][0]['text']
    with pytest.raises(Held, match='preamble'): validate_hook(script, 'rewrite_reveal', strict=True)
    script['format'] = 'clip'; script['hook'] = 'Actual source title'; validate_hook(script, strict=True)
    script['format'] = 'aura'; script['units'][0]['text'] = 'Calm.'; validate_hook(script, strict=True)


@pytest.mark.parametrize('mutation', [
    lambda e:e.update(selected_hook_index=3),
    lambda e:e['hook_options'][1].update(type=e['hook_options'][0]['type']),
    lambda e:e['script']['units'][0].update(onscreen='Unwritten promise'),
    lambda e:e['hook_options'][2].update(first_line='Have you ever seen this?')])
def test_bad_hook_envelopes_do_not_silently_choose_or_paraphrase(mutation):
    value = envelope(episode()[0]); mutation(value)
    with pytest.raises(Held):unpack_hooks(value, 'rewrite_reveal')


def test_hook_candidates_use_same_writer_call_and_separate_exact_editorial_pass(tmp_path):
    from yt_pipeline.writer import write_script
    ws = Workspace(tmp_path/'ws'); script, plan = episode(); calls = []
    class Provider:
        def generate(self, purpose, content, schema):
            calls.append(purpose)
            if purpose == 'scripter-hooks-v1':return envelope(script)
            if purpose == 'creative-director-v1':
                assert content['selected_opening']['first_line'] == script['hook']; return deepcopy(plan)
            assert purpose == 'independent-editorial-v1'; return verdict(script)
    job = ws.create('education', {'playbook': 'rewrite_reveal', 'topic': 'Technical fixture'})
    result = write_script(ws, job, brief(), Provider())
    assert calls == ['scripter-hooks-v1', 'creative-director-v1', 'independent-editorial-v1']
    assert result['hook_options']['active'] and result['editorial_review']['payoff_exact_text'] == script['units'][-1]['text']


@pytest.mark.parametrize('failure', ['daily_budget', 'gemini_quota'])
def test_separate_editorial_provider_holds_propagate_without_fallback(tmp_path, failure):
    from yt_pipeline.writer import write_script
    ws=Workspace(tmp_path/'ws'); script,plan=episode(); calls=[]
    class Provider:
        def generate(self,purpose,*args):
            calls.append(purpose)
            if purpose=='scripter-hooks-v1':return envelope(script)
            if purpose=='creative-director-v1':return deepcopy(plan)
            raise Held(failure,'Test provider hold',retry_after=60)
    job=ws.create('education',{'playbook':'rewrite_reveal','topic':'Fixture'})
    with pytest.raises(Held) as error:write_script(ws,job,brief(),Provider())
    assert error.value.code==failure and len(calls)==3


@pytest.mark.parametrize('failure',['hook','length'])
@pytest.mark.parametrize('always_bad',[False,True])
def test_contract_repair_receives_measured_limits_and_stays_bounded(tmp_path,failure,always_bad):
    from yt_pipeline.writer import write_script
    ws=Workspace(tmp_path/'ws');script,plan=episode();bad=envelope(script);calls=[]
    if failure=='hook':bad['hook_options'][2]['first_line']='Have you ever wondered about a generic opening?'
    else:bad['script']['units'][-1]['text']+=' '+'extra '*200
    class Provider:
        def generate(self,purpose,content,schema):
            calls.append(purpose)
            if purpose=='scripter-hooks-v1':return deepcopy(bad)
            if purpose=='scripter-contract-repair-v1':
                assert content['required_bounds']['target_spoken_words']>0
                assert content['hook_contract']['max_caption_words']==12
                assert len(content['measured_draft']['hook_options'])==3
                if failure=='length':assert content['measured_draft']['spoken_words']>200
                else:assert 'option 2' in content['validation_error']
                return deepcopy(bad) if always_bad else envelope(script)
            if purpose=='creative-director-v1':return deepcopy(plan)
            assert purpose=='independent-editorial-v1';return verdict(script)
    job=ws.create('education',{'playbook':'rewrite_reveal','topic':'Measured repair fixture'})
    if always_bad:
        with pytest.raises(Held):write_script(ws,job,brief(),Provider())
        assert len(calls)==2
    else:
        result=write_script(ws,job,brief(),Provider())
        assert result['contract_repairs']==1
        assert [u['text'] for u in result['script']['units']]==[u['text'] for u in script['units']]
    assert calls.count('scripter-contract-repair-v1')==1


@pytest.mark.parametrize('always_bad',[False,True])
def test_separate_editorial_critique_shares_the_single_rewrite_budget(tmp_path,always_bad):
    from yt_pipeline.writer import write_script
    ws=Workspace(tmp_path/'ws');script,plan=episode();calls=[];reviews=0
    class Provider:
        def generate(self,purpose,*args):
            nonlocal reviews
            calls.append(purpose)
            if purpose=='scripter-hooks-v1':return envelope(script)
            if purpose=='creative-script-rewrite-v1':return deepcopy(script)
            if purpose=='creative-director-v1':return deepcopy(plan)
            assert purpose=='independent-editorial-v1';reviews+=1;value=verdict(script)
            if reviews==1 or always_bad:value.update(passes=False,issues=['The promise was not concretely delivered.'])
            return value
    job=ws.create('education',{'playbook':'rewrite_reveal','topic':'Fixture'})
    if always_bad:
        with pytest.raises(Held) as error:write_script(ws,job,brief(),Provider())
        assert error.value.code=='creative_review'
    else:
        result=write_script(ws,job,brief(),Provider());assert result['creative_rewrites']==1 and result['hook_options']['active']
    assert calls.count('creative-script-rewrite-v1')==1 and reviews==2


@pytest.mark.parametrize('mutation',[
    lambda r:r.update(payoff_exact_text='A better line nobody actually says.'),
    lambda r:r.update(payoff_unit_id='u0'),
    lambda r:r.update(issues=['Unresolved contradiction.'])])
def test_editor_cannot_pass_unspoken_payoff_or_unresolved_issues(mutation):
    script,plan=episode();value=verdict(script);mutation(value)
    provider=SimpleNamespace(generate=lambda *args:value)
    with pytest.raises(Held):review_editorial(provider,script,plan,brief())


@pytest.mark.parametrize('name',['rewrite_reveal','myth_fact','quiz_pause'])
def test_new_presets_have_complete_graphics_and_retain_accepted_voice(name):
    from yt_pipeline.playbooks import get_playbook
    script,plan=episode(name);assert validate_plan(plan,script,name)
    request=prepare_request({'playbook':name})
    assert request['motion_graphics'] and request['editorial_review']=='required'
    assert get_playbook(name)['voice']==get_playbook('education_demo')['voice']
    plan['scenes'][0]['graphic']['kind']='none'
    plan['scenes'][0]['graphic'].update(labels=[],title='')
    with pytest.raises(Held,match='graphic on every beat'):validate_plan(plan,script,name)


@pytest.mark.parametrize('change', ['missing','two','after_answer','no_silence'])
def test_quiz_requires_one_real_thinking_interval_before_answer(change):
    script,plan=episode('quiz_pause')
    if change=='missing':plan['scenes'][3].update(thinking_seconds=0,graphic={'kind':'callout','title':'Example','labels':[script['units'][3]['text']]})
    elif change=='two':plan['scenes'][2].update(thinking_seconds=3,graphic=deepcopy(plan['scenes'][3]['graphic']))
    elif change=='after_answer':plan['scenes'][3],plan['scenes'][4]=plan['scenes'][4],plan['scenes'][3]
    else:plan['scenes'][3]['thinking_seconds']=0
    with pytest.raises(Held):validate_plan(plan,script,'quiz_pause')


def test_delivery_keeps_all_clean_words_and_bounds():
    text='Wait. Then answer.'
    scene={'speech_segments':[{'text':'Wait.','pause_after':.3,'speed':1.1},{'text':'Then answer.','pause_after':0,'speed':1}]}
    assert speech_segments(text,scene)==scene['speech_segments']
    for mutation in (lambda s:s[1].update(text='Invented answer.'),lambda s:s[0].update(speed=float('nan')),
                     lambda s:s[0].update(pause_after=8),lambda s:s[1].update(pause_after=.3)):
        value=deepcopy(scene);mutation(value['speech_segments'])
        with pytest.raises(Held):speech_segments(text,value)


def fake_voice(ws,monkeypatch,word_seconds=.2):
    np=pytest.importorskip('numpy')
    calls=[]
    class Kokoro:
        def __init__(self,*args):pass
        def get_voices(self):return ['am_adam']
        def create(self,text,voice,speed,lang):
            calls.append((text,voice,speed));rate=8000
            frames=round(max(.2,len(text.split())*word_seconds/speed)*rate)
            return (np.sin(np.arange(frames)*2*np.pi*220/rate)*.15).astype(np.float32),rate
    monkeypatch.setitem(sys.modules,'kokoro_onnx',SimpleNamespace(Kokoro=Kokoro))
    (ws.root/'voices/fake.onnx').write_bytes(b'LOCAL FAKE MODEL')
    (ws.root/'voices/fake.bin').write_bytes(b'LOCAL FAKE VOICE PACK')
    config=ws.config();config['voice']={'engine':'kokoro','model':'voices/fake.onnx','voices':'voices/fake.bin',
        'voice_id':'am_adam','length_scale':1.,'commercial_use_checked':True,'license_evidence':['Synthetic local test only'],
        'normalize_loudness':False};ws.save_config(config)
    return calls


def test_segment_audio_cache_silence_and_thinking_share_actual_timeline(tmp_path,monkeypatch):
    np=pytest.importorskip('numpy')
    ws=Workspace(tmp_path/'ws');calls=fake_voice(ws,monkeypatch)
    script={'units':[{'id':'one','speaker':'Narrator','text':'Wait. Then answer.'},{'id':'two','speaker':'Narrator','text':'Answer now.'}]}
    plan={'cast':[{'id':'n','speaker':'Narrator','voice_id':'am_adam'}],
          'scenes':[{'unit_id':'one','speaker_id':'n','pause_after':.1,'thinking_seconds':3,'graphic':{'kind':'timer'},
                     'speech_segments':[{'text':'Wait.','pause_after':.3,'speed':1.1},{'text':'Then answer.','pause_after':0,'speed':1}]},
                    {'unit_id':'two','speaker_id':'n','pause_after':.1}]}
    result=synthesize(ws,script,tmp_path/'voice',creative_plan=plan)
    row=result['units'][0];assert row['text']=='Wait. Then answer.' and len(calls)==3
    with wave.open(row['file'],'rb') as wav:
        data=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2');rate=wav.getframerate()
    first=row['segment_timings'][0];gap=data[round(first['speech_end']*rate):round(first['end']*rate)]
    assert len(gap)==round(.3*rate) and not np.any(gap)
    with wave.open(result['audio'],'rb') as wav:whole=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2')
    thinking=whole[round(row['speech_end']*rate):round((row['speech_end']+3)*rate)]
    assert len(thinking)==3*rate and not np.any(thinking)
    assert result['units'][1]['start']==row['end'] and calls[0][2]==1.1
    again=synthesize(ws,script,tmp_path/'again',creative_plan=plan)
    assert len(calls)==3 and again['duration']==result['duration']
    plan['scenes'][0]['speech_segments'][0]['pause_after']=.4
    changed=synthesize(ws,script,tmp_path/'changed',creative_plan=plan)
    assert len(calls)==3 and changed['units'][0]['file']!=row['file'] and changed['duration']>result['duration']


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
def test_real_timer_render_changes_only_after_measured_instruction(tmp_path):
    block={'kind':'timer','title':'Question','labels':['Which box holds two tokens?']}
    output=tmp_path/'timer.mp4';detail=render_block(block,4.2,output,speech_duration=1,thinking_seconds=3)
    assert abs(float(probe(output)['format']['duration'])-4.2)<.1
    assert detail['countdown_start']==1 and detail['countdown_end']==4
    from yt_pipeline.visual_review import sample_frame
    pictures=[]
    for i,time in enumerate((.1,.8,1.2,2.2,3.2)):
        path=tmp_path/f'frame-{i}.png';sample_frame(output,path,time);pictures.append(Image.open(path).crop((20,490,340,530)).convert('RGB'))
    from PIL import ImageChops,ImageStat
    difference=lambda a,b:sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
    assert difference(pictures[0],pictures[1])<1
    assert all(difference(pictures[a],pictures[b])>.5 for a,b in ((2,3),(3,4),(2,4)))


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
def test_quiz_pipeline_exports_real_silence_timer_and_full_captions(tmp_path,monkeypatch):
    import yt_pipeline.dialogue_captions as alignment
    # Controlled synthetic speech has no real words for an ASR kernel to hear.
    # Real alignment is validated separately; these exact cue boundaries exercise burn-in/timeline routing.
    monkeypatch.setattr(alignment,'align_dialogue',lambda ws,timing:{**timing,'caption_style':'dialogue_bar',
        'caption_cues':[{'start':u['start'],'end':u['speech_end'],'text':u['text']} for u in timing['units']]})
    ws=Workspace(tmp_path/'ws');calls=fake_voice(ws,monkeypatch,word_seconds=.42);script,plan=episode('quiz_pause')
    class Provider:
        def generate(self,purpose,*args):
            assert purpose=='creative-director-v1';return deepcopy(plan)
    job=ws.create('education',{'playbook':'quiz_pause','brief':brief(),'script':script,'test_only':True,
        'visual_review':'off','editorial_review':'off'})
    result=Pipeline(ws,provider=Provider()).run(job['id'])
    assert result['status']=='ready',result['message']
    voice=json.loads((ws.job_dir(job['id'])/'voice.json').read_text());timer=voice['units'][3]
    assert timer['thinking_seconds']==3 and 20<=voice['duration']<=40
    visuals=json.loads((ws.job_dir(job['id'])/'visuals.json').read_text())
    assert visuals['frames'][3]['graphic']['countdown_start']==timer['metrics']['duration']
    captions=Path(visuals['captions']).read_text()
    assert all(u['text'] in captions for u in script['units']) and '[P]' not in captions
    qa=json.loads((ws.job_dir(job['id'])/'quality.json').read_text())
    assert qa['technical_pass'] and qa['test_only'] and not qa['publication_ready']
    before=len(calls);Pipeline(ws,provider=Provider()).run(job['id']);assert len(calls)==before
