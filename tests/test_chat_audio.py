from array import array
from copy import deepcopy
import math
import wave

import pytest

from yt_pipeline.core import Workspace,Held
from yt_pipeline.assets import register_asset
from yt_pipeline.chat_editing import reading_timing
from yt_pipeline.phone_editor.audio import cast_voices,mix_chat_effects,mix_music,style_speech,voice_styles
from yt_pipeline.voice import wav_metrics


def script():
    return {'units':[{'id':f'u{i}','speaker':'A' if i%2==0 else 'B','text':'This is the whole message.'} for i in range(8)]}


def wav(path,seconds=2.8,rate=24000):
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate)
        f.writeframes(array('h',(round(4000*math.sin(2*math.pi*330*i/rate)) for i in range(round(seconds*rate)))).tobytes())


def test_character_speech_waits_for_bubble_and_finishes_without_overlap(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');s=script();source=tmp_path/'speech.wav';wav(source)
    voices={'A':'am_adam','B':'af_heart'}
    def fake(*args):
        return {'units':[{**u,'file':str(source),'voice_id':voices[u['speaker']],'metrics':{'duration':2.8}} for u in s['units']],
                'cast_voices':voices,'engine':'fixture','model_sha256':'fixture','license_evidence':['fixture']}
    monkeypatch.setattr('yt_pipeline.phone_editor.audio.character_speech',fake)
    job=ws.create('entertainment',{'chat_editing_version':2,'chat_writing_version':2,'chat_voiceover':True,'chat_pause_before':{'u3':.7}})
    timing=reading_timing(ws,job,s,tmp_path/'timing')
    assert timing['narration'] and timing['cast_voices']==voices
    for row in timing['units']:
        assert row['speech_start']==pytest.approx(row['arrival']+.06)
        assert row['speech_end']+ .25<=row['end']
        assert row['voice_id']==voices[row['speaker']]
    assert timing['units'][3]['typing_seconds']==pytest.approx(.86)
    with wave.open(timing['audio'],'rb') as f:
        f.setpos(round(timing['units'][1]['speech_start']*24000))
        pcm=array('h',f.readframes(24000))
    assert max(abs(v) for v in pcm)>3000
    assert all(a['speech_end']<b['arrival'] for a,b in zip(timing['units'],timing['units'][1:]))


def test_distinct_cast_and_invalid_pause_are_held(tmp_path):
    assert len(set(cast_voices(script(),{}).values()))==2
    with pytest.raises(Held):cast_voices(script(),{'chat_voice_ids':{'A':'am_adam','B':'am_adam'}})
    with pytest.raises(Held):cast_voices(script(),{'chat_voice_ids':{'Ghost':'am_adam'}})
    ws=Workspace(tmp_path/'ws');job=ws.create('entertainment',{'chat_pause_before':{'missing':1}})
    with pytest.raises(Held):reading_timing(ws,job,script(),tmp_path/'timing')


def test_notification_speaks_once_on_first_visibility_and_stays_until_finished(tmp_path,monkeypatch):
    from yt_pipeline.phone_editor.story import story_frame
    ws=Workspace(tmp_path/'ws');s=script();source=tmp_path/'speech.wav';wav(source)
    s['phone_story']={'pov':'A','contacts':[{'id':'b','name':'B'}],
        'threads':[{'id':'thread','contact_id':'b','theme':'dark'}],
        'beats':[{'unit_id':u['id'],'thread_id':'thread','time':'18:30','events':['notification'] if i==7 else []} for i,u in enumerate(s['units'])]}
    monkeypatch.setattr('yt_pipeline.phone_editor.audio.character_speech',lambda *a:{'units':[{**u,'file':str(source),'voice_id':'am_adam' if u['speaker']=='A' else 'af_heart','metrics':{'duration':2.8}} for u in s['units']],
        'cast_voices':{'A':'am_adam','B':'af_heart'},'engine':'fixture','model_sha256':'fixture','license_evidence':['fixture']})
    job=ws.create('entertainment',{'chat_editing_version':2,'chat_writing_version':2,'phone_story':True,'chat_voiceover':True})
    timing=reading_timing(ws,job,s,tmp_path/'timing');row=timing['units'][-1];event=row['screen_events'][0]
    assert row['speech_display']=='notification' and row['speech_start']==pytest.approx(row['start']+event['start']+.06)
    assert row['speech_end']<row['start']+event['end']
    second=row['speech_end']-row['start']-.1
    _,state=story_frame(s,7,second,row['duration'],row['typing_seconds'],timed_beat=row)
    assert state['screen']=='notification' and state['visible_unit_ids']==['u7']
    assert row['arrival']>row['speech_end']


def test_music_ducks_during_speech_and_preserves_blackout_silence(tmp_path):
    ws=Workspace(tmp_path/'ws');source=tmp_path/'music.wav';wav(source,6)
    asset=register_asset(ws,source,'original_graphic',{'generator':'test tone'},test_only=True)
    job=ws.create('entertainment',{'music_id':asset['id'],'chat_music_volume':.25})
    rows=[{'start':0,'speech_start':1,'speech_end':2,'screen_events':[{'type':'blackout','start':3,'end':4}]}]
    samples=array('h',[0])*(6*24000)
    meta=mix_music(ws,job,samples,24000,rows)
    assert meta['mixed_music_id']==asset['id']
    rms=lambda start,end:math.sqrt(sum(v*v for v in samples[int(start*24000):int(end*24000)])/((end-start)*24000))
    assert rms(1.3,1.7)<rms(4.5,4.9)*.5
    assert not any(samples[3*24000:4*24000])
    assert max(abs(v) for v in samples)<32000


def test_youthful_style_changes_only_selected_character_and_remeasures(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');source=tmp_path/'source.wav';wav(source,2)
    folder=tmp_path/'styled';folder.mkdir()
    metrics=wav_metrics(source)
    timing={'units':[{'id':'u1','speaker':'Dad','text':'A test line.','voice_id':'am_adam','file':str(source),'metrics':metrics},
                     {'id':'u2','speaker':'Lily','text':'Another test line.','voice_id':'af_bella','file':str(source),'metrics':metrics}],
            'metrics':metrics,'cast_voices':{'Dad':'am_adam','Lily':'af_bella'},'model_sha256':'fixture'}
    result=style_speech(ws,timing,{'Lily':'light_youthful'},folder)
    assert result['units'][0]['file']==str(source)
    tuned=result['units'][1]
    assert tuned['file']!=str(source) and tuned['source_speech_file']==str(source)
    assert 1.85<tuned['metrics']['duration']<2.05 and tuned['metrics']['sample_rate']==24000
    assert tuned['metrics']['clipped_fraction']==0 and tuned['voice_style']['pitch_semitones']==1.25
    with wave.open(tuned['file'],'rb') as f:pcm=array('h',f.readframes(f.getnframes()))
    middle=pcm[round(.4*24000):round(1.4*24000)]
    crossings=sum(a<=0<b for a,b in zip(middle,middle[1:]))
    assert 345<crossings<365 # Original source is 330 Hz; verify a modest real pitch change.
    assert result['units'][0]['end']==result['units'][1]['start']
    monkeypatch.setattr('yt_pipeline.phone_editor.audio.subprocess.run',lambda *a,**k:pytest.fail('An intact style cache must be reused.'))
    again=style_speech(ws,timing,{'Lily':'light_youthful'},folder)
    assert again['units'][1]['file']==tuned['file']
    with pytest.raises(Held):voice_styles({'chat_voice_styles':{'Ghost':'light_youthful'}},['Lily'])
    with pytest.raises(Held):voice_styles({'chat_voice_styles':{'Lily':'cartoon'}})


def test_chat_effect_routing_does_not_sound_same_notification_twice(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');job=ws.create('entertainment',{})
    rows=[{'id':'u1','speaker':'A','start':0,'arrival':.2,'screen_events':[]},
          {'id':'u2','speaker':'B','start':2,'arrival':4.2,'speech_start':2.71,'speech_end':3.8,
           'screen_events':[{'type':'switch','start':0,'end':.35},{'type':'notification','start':.65,'end':2.1}]},
          {'id':'u3','speaker':'A','start':5,'arrival':6.6,'screen_events':[{'type':'blackout','start':0,'end':1.5}]}]
    monkeypatch.setattr('yt_pipeline.sound_library.install_sound_library',lambda ws,include_ambience:assert_false(include_ambience))
    def verify(ws,samples,rate,events,silence,speech):
        assert [(e['category'],round(e['start'],2)) for e in events]==[
            ('message_outgoing',.2),('notification',2.65),('message_outgoing',6.6),('transition',2)]
        assert silence==[(5,6.5)] and speech==[(2.71,3.8)]
        return {'effects':events}
    monkeypatch.setattr('yt_pipeline.sound_library.mix_sound_events',verify)
    assert len(mix_chat_effects(ws,job,script(),array('h',[0]),24000,rows)['effects'])==4


def assert_false(value):
    assert value is False
