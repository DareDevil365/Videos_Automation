from copy import deepcopy
from pathlib import Path
import shutil

import pytest
from PIL import Image,ImageChops

from yt_pipeline.assets import register_asset
from yt_pipeline.cast_body import resolve_wardrobes,draw_human_body
from yt_pipeline.core import Workspace,Held,digest
from yt_pipeline.planned_visuals import build_planned_visuals,_motion,crop_character_head
from yt_pipeline.scene_direction import compose_scene,validate_direction,check_stock_reuse,locate_callout,draw_callout


def actors():
    return [{'id':'a','speaker':'A','role':'Friend','avatar_kind':'human','costume':'blue hoodie','avatar_query':'human portrait'},
            {'id':'b','speaker':'B','role':'Friend','avatar_kind':'human','costume':'red jacket','avatar_query':'human portrait'},
            {'id':'n','speaker':'Narrator','role':'Narrator','avatar_kind':'human','costume':'green shirt','avatar_query':'must not be acquired'}]


def scene(unit='u1',**extra):
    return {'unit_id':unit,'speaker_id':'a','shot_type':'two_shot','pose':'talk','framing':'medium',
            'visible_cast':['a','b','n'],'focus_id':'a','asset_id':'','background_query':'technical room',
            'visual_query':'technical object','motion':'hold','callout':{'kind':'none','target':'','label':''},
            'reuse_purpose':'none','reuse_reason':'',**extra}


def test_composition_preserves_two_people_and_makes_narrator_optional():
    original=scene();cast=actors()
    result=compose_scene(original,cast)
    assert result['visible_cast']==['a','b'] and result['framing']=='medium'
    assert original['visible_cast']==['a','b','n']
    assert compose_scene(original,cast,True)['visible_cast']==['a','b','n']
    insert=compose_scene(scene(shot_type='insert'),cast)
    assert insert['visible_cast']==[] and insert['focus_id']==''


def test_scene_mode_rejects_an_episode_that_only_swaps_faces():
    plan={'template':'cutout_cast','cast':actors(),'scenes':[scene(shot_type='dialogue',visible_cast=['a'])]}
    script={'units':[{'text':'Fixture.','onscreen':'Fixture.'}]}
    with pytest.raises(Held,match='two-shot'):validate_direction(plan,script,{'scene_direction_version':2})
    plan['scenes']=[scene()]
    validate_direction(plan,script,{'scene_direction_version':2})


def test_insert_omits_cast_and_callouts_cannot_invent_labels_or_track_video():
    plan={'template':'cutout_cast','cast':actors(),'scenes':[scene(),scene('u2',shot_type='insert')]}
    script={'units':[{'text':'Fixture.','onscreen':'Fixture.'}]*2}
    with pytest.raises(Held,match='omit'):validate_direction(plan,script,{'scene_direction_version':2})
    plan['scenes'][1].update(visible_cast=[],focus_id='',callout={'kind':'circle_arrow','target':'eye','label':'Invented'})
    with pytest.raises(Held,match='quote'):validate_direction(plan,script,{'scene_direction_version':2})
    plan['scenes'][1]['callout']['label']=''
    script['units'][1]={'text':'Fixture.','onscreen':'Fixture.','visual_kind':'video'}
    with pytest.raises(Held,match='tracking'):validate_direction(plan,script,{'scene_direction_version':2})


def test_eye_clue_requires_a_callout_without_claiming_photo_motion():
    plan={'template':'story_stock','cast':actors(),'scenes':[scene(shot_type='insert',visible_cast=[],focus_id='')]}
    script={'units':[{'text':'His eyes rolled toward the door.','onscreen':'Eyes rolled','visual_kind':'image'}]}
    with pytest.raises(Held,match='moving-eye clue'):validate_direction(plan,script,{'scene_direction_version':2})
    plan['scenes'][0]['callout']={'kind':'circle_arrow','target':'portrait eyes','label':''}
    validate_direction(plan,script,{'scene_direction_version':2})


def test_wardrobes_are_distinct_stable_and_actually_different_pixels():
    cast=actors()[:2]
    clothes=resolve_wardrobes(cast)
    assert clothes==resolve_wardrobes(list(reversed(cast)))
    assert clothes['a']['style']=='hoodie' and clothes['b']['style']=='jacket'
    twins=[{**a,'costume':'blue hoodie'} for a in cast]
    assert len({(w['style'],w['shirt']) for w in resolve_wardrobes(twins).values()})==2
    first=Image.new('RGB',(400,500),'white');second=first.copy()
    draw_human_body(first,130,40,90,'blue',style='hoodie',pose='talk')
    draw_human_body(second,130,40,90,'blue',style='jacket',pose='neutral')
    assert ImageChops.difference(first,second).getbbox() is not None


def test_stock_repeats_require_a_specific_necessary_visual_change():
    seen={};first=scene(visible_cast=[],asset_id='x',framing='wide')
    check_stock_reuse(seen,'same-file-sha',first,0)
    with pytest.raises(Held,match='necessary repeat'):check_stock_reuse(seen,'same-file-sha',scene('u2'),1)
    detail=scene('u2',framing='closeup',reuse_purpose='detail',reuse_reason='Revisit this exact clue in a tight detail view.')
    assert check_stock_reuse(seen,'same-file-sha',detail,1)['previous_unit_id']=='u1'
    with pytest.raises(Held,match='change framing'):check_stock_reuse(seen,'same-file-sha',{**detail,'unit_id':'u3'},2)
    replay=scene('u4',reuse_purpose='replay',reuse_reason='Replay the opening clue after the intervening reveal.')
    assert check_stock_reuse(seen,'same-file-sha',replay,4)['purpose']=='replay'


def test_source_callout_maps_through_crop_and_draws_both_marks():
    picture=Image.new('RGB',(500,800),'#222222')
    callout={'kind':'circle_arrow','target':'eyes','label':'','box':[.4,.25,.6,.35]}
    result=draw_callout(picture,(1000,1000),callout,{'box':[.2,.1,.8,.9]})
    assert result['display_box']==[150,150,350,250]
    red=[(x,y) for y in range(500) for x in range(500) if picture.getpixel((x,y))==(255,48,56)]
    assert any(y<130 for x,y in red) and any(y>240 for x,y in red)
    assert result['stroke_width']>=10 and result['color']=='#ff3038'
    with pytest.raises(Held,match='cropped out'):draw_callout(picture,(1000,1000),{**callout,'box':[0,0,.05,.1]}, {'box':[.2,.1,.8,.9]})


@pytest.mark.parametrize('result',[{'visible':False,'box':[0,0,1,1]}, {'visible':True,'box':[.8,.2,.1,.5]}, {'visible':True,'box':[True,0,1,1]}])
def test_callout_never_fabricates_an_unlocated_target(result):
    class Provider:
        def generate(self,*args,**kwargs):return result
    with pytest.raises(Held):locate_callout(None,{'path':'unused.png','sha256':'fixture'},
        {'kind':'circle_arrow','target':'eyes','label':''},Provider())


@pytest.mark.parametrize('always_bad',[False,True])
def test_head_crop_checks_actual_output_and_allows_only_one_correction(tmp_path,always_bad):
    source=tmp_path/'source.png';Image.new('RGB',(400,600),'blue').save(source)
    calls=[];reviews=0
    class Provider:
        def generate(self,purpose,content,schema,*,images):
            nonlocal reviews
            calls.append(purpose)
            if purpose.startswith('avatar-head-box'):
                if purpose.endswith('repair-v1'):assert len(images)==2 and 'critique' in content
                return {'visible':True,'box_yxyx':[100,100,900,900]}
            assert purpose=='avatar-head-pixels-v1' and Path(images[0]).is_file()
            reviews+=1
            return {'passes':not always_bad and reviews==2,'reason':'Technical output-pixel correction verdict.'}
    if always_bad:
        with pytest.raises(Held,match='one correction'):
            crop_character_head(None,{'path':str(source),'id':'fixture','sha256':'fixture'},
                {'id':'a','avatar_kind':'human'},tmp_path,Provider())
    else:
        avatar,record=crop_character_head(None,{'path':str(source),'id':'fixture','sha256':'fixture'},
            {'id':'a','avatar_kind':'human'},tmp_path,Provider())
        assert record['repairs']==1 and record['review']['passes'] and Path(avatar['path']).is_file()
    assert calls==['avatar-head-box-v1','avatar-head-pixels-v1','avatar-head-box-repair-v1','avatar-head-pixels-v1']


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
@pytest.mark.parametrize('insert_kind',['image','video'])
def test_real_ensemble_and_insert_use_distinct_bodies_and_actual_insert_source(tmp_path,insert_kind):
    ws=Workspace(tmp_path/'ws');registered={}
    for name,color in [('background','silver'),('a','orange'),('b','cyan'),('animal','green')]:
        p=tmp_path/(name+'.png');Image.new('RGB',(600,900),color).save(p)
        registered[name]=register_asset(ws,p,'test',{'description':'Technical scene-direction fixture'})
    if insert_kind=='video':
        clip=tmp_path/'animal.mp4';_motion(tmp_path/'animal.png',.6,clip,'hold')
        registered['animal']=register_asset(ws,clip,'test',{'description':'Technical actual-video insert fixture'})
    units=[{'id':'u1','speaker':'A','text':'Technical ensemble fixture.','onscreen':'Ensemble','visual_kind':'image'},
           {'id':'u2','speaker':'A','text':'Technical insert fixture.','onscreen':'Insert','visual_kind':insert_kind}]
    script={'title':'Technical scene fixture','format':'cutout','fiction':True,'units':units}
    scenes=[scene(asset_id=registered['background']['id']),scene('u2',shot_type='insert',visible_cast=[],focus_id='',framing='wide',asset_id=registered['animal']['id'])]
    plan={'template':'cutout_cast','cast':actors(),'scenes':scenes}
    timing={'units':[{'id':u['id'],'text':u['text'],'start':i*.4,'speech_end':i*.4+.3,'duration':.4} for i,u in enumerate(units)]}
    class Provider:
        def generate(self,purpose,*args,**kwargs):
            if purpose=='avatar-head-box-v1':return {'visible':True,'box_yxyx':[0,0,1000,1000]}
            assert purpose=='avatar-head-pixels-v1'
            return {'passes':True,'reason':'Technical solid-color head fixture.'}
    result=build_planned_visuals(ws,{'request':{'scene_direction_version':2,'test_only':True,
        'cast_assets':{'a':registered['a']['id'],'b':registered['b']['id']}}},script,timing,tmp_path/'visuals',{'plan':plan,'script_sha256':digest(script)},provider=Provider())
    assert result['frames'][0]['resolved_scene']['visible_cast']==['a','b']
    assert set(result['wardrobes'])=={'a','b'}
    assert set(result['avatar_crops'])=={'a','b'}
    assert result['source_bindings'][1]['asset_id']==registered['animal']['id']
    assert result['source_bindings'][1]['role']=='literal animal/object/action illustration'
    with Image.open(tmp_path/'visuals/u1-planned.png') as frame:
        assert frame.getpixel((200,445))[:3]==(255,165,0)
        assert frame.getpixel((520,445))[:3]==(0,255,255)
    if insert_kind=='video':
        from yt_pipeline.visual_review import sample_frame
        sample_frame(result['frames'][1]['file'],tmp_path/'insert-frame.png',.1)
        poster=tmp_path/'insert-frame.png'
        assert result['frames'][1]['kind']=='directed_stock_video'
    else:poster=tmp_path/'visuals/u2-planned.png'
    with Image.open(poster) as frame:
        assert frame.getpixel((frame.width//2,round(frame.height*.39)))[1]>100
    if insert_kind=='image':
        alias=register_asset(ws,tmp_path/'animal.png','test',{'description':'Same pixels, different asset ID'})
        assert alias['id']!=registered['animal']['id']
        duplicate_script={**script,'units':[*units,{**units[-1],'id':'u3'}]}
        duplicate_plan={**plan,'scenes':[*scenes,{**scenes[-1],'unit_id':'u3','asset_id':alias['id']}]}
        duplicate_timing={'units':[*timing['units'],{**timing['units'][-1],'id':'u3','start':.8,'speech_end':1.1}]}
        with pytest.raises(Held,match='necessary repeat'):
            build_planned_visuals(ws,{'request':{'scene_direction_version':2,'test_only':True,
                'cast_assets':{'a':registered['a']['id'],'b':registered['b']['id']}}},duplicate_script,duplicate_timing,
                tmp_path/'duplicate-visuals',{'plan':duplicate_plan,'script_sha256':digest(duplicate_script)},provider=Provider())
