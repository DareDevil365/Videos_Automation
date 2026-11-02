from copy import deepcopy

import pytest
from PIL import Image,ImageChops

from yt_pipeline.core import Held
from yt_pipeline.montage import plan_cuts,build_cuts
from yt_pipeline.storyboard import story_specs,story_poster,prop_data


def inputs():
    script={'units':[{'id':'hook','onscreen':'The door was already open','visual_query':'door: a narrow red line beneath the door'},
                     {'id':'reveal','onscreen':'A message from inside','visual_query':'phone: Do not open the door'}],
            'edit':{'payoff_unit_id':'reveal'}}
    timing={'units':[{'id':'hook','start':0,'duration':4.2},{'id':'reveal','start':4.2,'duration':2.1}]}
    frames=[{'unit_id':'hook','file':'hook.png'},{'unit_id':'reveal','file':'reveal.png'}]
    return script,timing,frames


@pytest.fixture
def records(monkeypatch):
    values={key:{'id':key,'kind':'image','sha256':key,'path':key+'.png'} for key in ('door','phone','gameplay')}
    monkeypatch.setattr('yt_pipeline.montage.asset_record',lambda ws,id:values[id])
    return values


def test_each_beat_keeps_its_named_semantic_asset(records):
    script,timing,frames=inputs()
    request={'cut_interval':2.3,'storyboard':{
        'hook':{'top':'door','bottom':'gameplay','bottom_role':'decorative','purpose':'Show the opening door'},
        'reveal':{'top':'phone','bottom':'gameplay','bottom_role':'decorative','purpose':'Show the message'}}}
    planned,pool=plan_cuts(None,{'request':request},script,timing,frames,[])
    assert [row['pair'][0]['id'] for row in planned]==['door','door','phone']
    assert [row['pair'][1]['id'] for row in planned]==['gameplay']*3
    assert sum(round(row['duration']*30) for row in planned)==189
    assert [row['payoff_end'] for row in planned]==[False,False,True]
    assert set(a['id'] for a in pool)=={'door','phone','gameplay'}


def test_missing_storyboard_never_rotates_global_pool(records):
    script,timing,frames=inputs()
    with pytest.raises(Held) as exc:
        plan_cuts(None,{'request':{'montage_assets':['door','phone','gameplay']}},script,timing,frames,[])
    assert exc.value.code=='storyboard_missing'


def test_selected_unit_media_requires_explicit_decorative_background(records):
    script,timing,frames=inputs()
    selected=[{'unit_id':uid,'asset':records[asset]} for uid,asset in [('hook','door'),('reveal','phone')]]
    planned,_=plan_cuts(None,{'request':{'decorative_background_id':'gameplay'}},script,timing,frames,selected)
    assert planned[-1]['pair'][0]['id']=='phone'
    assert all(row['bottom_role']=='decorative' for row in planned)


def test_frame_order_and_missing_unit_hold_before_bed_render(records,monkeypatch):
    script,timing,frames=inputs();calls=[]
    monkeypatch.setattr('yt_pipeline.montage.two_slot_bed',lambda *a:calls.append(a))
    with pytest.raises(Held) as exc:build_cuts(None,{'request':{}},script,timing,list(reversed(frames)),[],'.')
    assert exc.value.code=='storyboard_timing' and calls==[]
    with pytest.raises(Held) as exc:
        plan_cuts(None,{'request':{'storyboard':{'hook':{}}}},script,timing,frames,[])
    assert exc.value.code=='storyboard_units'


def test_cut_limit_is_checked_before_any_bed_render(records,monkeypatch):
    script,timing,frames=inputs();script['units']=script['units'][:1];script['edit']['payoff_unit_id']='hook'
    timing['units']=timing['units'][:1];timing['units'][0]['duration']=80;frames=frames[:1];calls=[]
    monkeypatch.setattr('yt_pipeline.montage.two_slot_bed',lambda *a:calls.append(a))
    row={'top':'door','bottom':'gameplay','bottom_role':'decorative','purpose':'The door'}
    with pytest.raises(Held) as exc:
        build_cuts(None,{'request':{'storyboard':{'hook':row}}},script,timing,frames,[],'.')
    assert exc.value.code=='montage_too_many_cuts' and calls==[]


def test_story_scene_tags_are_model_selected_and_bounded():
    script,_,_=inputs();specs=story_specs(script,{'story_visuals':'from_script'})
    assert specs['hook']['scene']=='door' and specs['reveal']['scene']=='phone'
    script['units'][1]['visual_query']='random: an unrelated stock image'
    with pytest.raises(Held) as exc:story_specs(script,{'story_visuals':'from_script'})
    assert exc.value.code=='storyboard_scene'


def test_story_posters_are_distinct_original_scenes(tmp_path):
    first=tmp_path/'door.png';second=tmp_path/'phone.png'
    story_poster('door','A red line under the door','The door was already open',first)
    story_poster('phone','Do not open the door','A message from inside',second)
    a=Image.open(first);b=Image.open(second)
    assert a.size==b.size==(720,1280)
    # The main picture changes, not just a caption over a reused background.
    assert ImageChops.difference(a.crop((100,200,620,1000)),b.crop((100,200,620,1000))).getbbox() is not None


def test_story_props_use_story_content_not_render_instructions():
    notification=prop_data('phone','glowing screen notification','Phone buzzed with a text','Suddenly my phone buzzed with an incoming text.')
    reveal=prop_data('phone','text message on display','Do not turn around','The message said do not turn around.')
    assert notification['phone_message']=='New message'
    assert reveal['phone_message']=='do not turn around'
    assert 'display' not in reveal['phone_message']
    assert prop_data('elevator','digital floor display minus one','Skipped to negative one')['floor']=='-1'
    assert prop_data('elevator','glowing panel button','Basement level four at midnight')['floor']=='B4'
    assert prop_data('door','opening metal elevator doors','Doors opened slowly')['open_elevator'] is True
