from copy import deepcopy

import pytest
from PIL import Image,ImageChops

from yt_pipeline.core import Held,Workspace
from yt_pipeline.lore_style import decide_style,attach_styles
from yt_pipeline.lore_style_assets import place_cutout,validate_execution,load_style_layers
from yt_pipeline.lore_voices import choose_series_voices,validate_voices


def test_doom_changes_medium_for_the_purpose_of_the_shot():
    fitting=decide_style({'focus':'object','motion':'contact','characters':['doom'],
                         'props':[{'id':'mask','changes_state':True}]})
    portrait=decide_style({'focus':'identity','characters':['doom']})
    assert fitting['characters']['doom']['representation']=='geometric'
    assert fitting['props'][0]['representation']=='geometric'
    assert portrait['characters']['doom']['representation']=='cutout'


def test_complex_lookalikes_keep_likeness_but_simple_action_can_be_drawn():
    result=decide_style({'focus':'action','motion':'contact','characters':['thor','bill']})
    assert result['characters']['bill']['representation']=='cutout'
    assert result['characters']['bill']['motion_requirement']=='rigged'
    assert result['characters']['thor']['representation']=='geometric'
    result=decide_style({'focus':'identity','characters':['thor','bill']})
    assert all(p['representation']=='cutout' for p in result['characters'].values())


def test_props_and_setting_are_chosen_independently_from_cast():
    result=decide_style({'focus':'location','characters':['hellboy'],
                         'props':[{'id':'inscription','readable_detail':True}]})
    assert result['characters']['hellboy']['representation']=='geometric'
    assert result['props'][0]['representation']=='cutout'
    assert result['setting']['representation']=='photographic'
    result=decide_style({'focus':'action','motion':'contact','characters':['spider_man'],
        'props':[{'id':'car','appearance_matters':True}], 'setting':{'atmosphere':True}})
    assert result['characters']['spider_man']['representation']=='geometric'
    assert result['props'][0]['representation']=='cutout' and result['setting']['representation']=='photographic'
    result=decide_style({'focus':'location','setting':{'needs_layout':True,'atmosphere':True},
        'props':[{'id':'mask','appearance_matters':True,'changes_state':True}]})
    assert result['props'][0]['representation']=='geometric' and result['setting']['representation']=='geometric'


def test_direction_never_rewrites_words_or_invents_unknown_profiles():
    scenes=[{'unit_id':'u1','kind':'mask_fitting','text':'The mask was hot.'}]
    before=deepcopy(scenes)
    report=attach_styles(scenes,{'visual_selection':{'mode':'auto'}})
    assert scenes[0]['text']==before[0]['text']
    assert report['scenes']['u1']['characters']['doom']['representation']=='geometric'
    with pytest.raises(Held):decide_style({'focus':'identity','characters':['unknown']})
    with pytest.raises(Held):attach_styles(scenes,{'visual_selection':{'shots':{'missing':{}}}})


def test_missing_asset_or_action_rig_cannot_silently_render_wrong_style():
    style=decide_style({'focus':'identity','characters':['doom']})
    with pytest.raises(Held,match='registered cutout'):
        validate_execution({'kind':'portrait','visual_style':style},{},{},None)
    style=decide_style({'focus':'identity','characters':['vision']})
    with pytest.raises(Held,match='anchored cutout rig'):
        validate_execution({'kind':'vision_unlock','visual_style':decide_style({'focus':'identity','characters':['vision','white_vision']})},{},{'vision':object()},None,('vision_unlock',))
    with pytest.raises(Held,match='higher-resolution'):
        place_cutout(Image.new('RGBA',(720,1280)),{'doom':Image.new('RGBA',(30,40))},'doom',(100,200,600,900))


def test_voice_rotation_is_stable_and_is_not_tied_to_character_gender(tmp_path):
    ws=Workspace(tmp_path/'ws')
    first=choose_series_voices(ws,'episode-one')
    assert choose_series_voices(ws,'episode-one')==first
    job=ws.create('entertainment',{'playbook':'comic_lore','series':{'id':'episode-one'},'source_voices':first})
    ws.update(job['id'],status='ready')
    assert choose_series_voices(ws,'episode-one')==first
    second=choose_series_voices(ws,'episode-two')
    assert second!=first and second['Narrator']!=first['Narrator']
    assert validate_voices({'Host':'am_michael','Narrator':'af_bella'})['Narrator']=='af_bella'
    with pytest.raises(Held):validate_voices({'Host':'af_bella','Narrator':'af_bella'})


def test_voice_rotation_can_choose_a_female_storyteller_after_male_series(tmp_path):
    ws=Workspace(tmp_path/'ws')
    for i in range(4):
        job=ws.create('entertainment',{'playbook':'comic_lore','series':{'id':str(i)}})
        ws.update(job['id'],status='ready')
    assert choose_series_voices(ws,'next-story')['Narrator'].startswith('af_')


def test_photo_location_and_prop_are_applied_under_and_beside_geometric_actor(tmp_path):
    from yt_pipeline.assets import register_asset
    from yt_pipeline.lore_visuals import lore_frame
    from yt_pipeline.source_sets import source_painter
    ws=Workspace(tmp_path/'ws')
    photo=tmp_path/'location.png';Image.new('RGB',(1600,1400),'#3d755a').save(photo)
    prop=tmp_path/'detail.png';Image.new('RGB',(500,700),'#c3924a').save(prop)
    bg=register_asset(ws,photo,'test',{'review':'fixture'})
    obj=register_asset(ws,prop,'test',{'review':'fixture'})
    request={'test_only':True,'visual_selection':{'layers':{'u1':{'setting':bg['id'],'props':{
        'inscription':{'asset_id':obj['id'],'box':[70,640,210,880]}}}}}}
    scene={'unit_id':'u1','kind':'portrait','label':'A location and an exact detail',
           'visual_style':decide_style({'focus':'location','characters':['hellboy'],
                                       'props':[{'id':'inscription','readable_detail':True}]})}
    backdrops,props,assets=load_style_layers(ws,request,{'units':[{'id':'u1'}]})
    validate_execution(scene,request,{},None)
    paint=lambda s,t,d:lore_frame(s,t,d,style_backdrops=backdrops)
    base=paint(scene,1,3)
    final=source_painter(paint,props['u1'],None,0)(scene,1,3)
    assert len(assets)==2
    assert final.getpixel((130,750))[:3]==(195,146,74)
    assert final.getpixel((360,480))!=final.getpixel((75,250))
    assert ImageChops.difference(base.crop((0,960,720,1280)),final.crop((0,960,720,1280))).getbbox() is None
    broken={'test_only':True,'visual_selection':{'layers':{'u1':{'props':request['visual_selection']['layers']['u1']['props']}}}}
    with pytest.raises(Held,match='photographic setting'):validate_execution(scene,broken,{},None)


def test_photo_location_reuse_needs_a_continuity_reason(tmp_path):
    from yt_pipeline.assets import register_asset
    from yt_pipeline.source_sets import check_lore_reuse
    ws=Workspace(tmp_path/'ws');path=tmp_path/'place.png';Image.new('RGB',(900,1000),'#335577').save(path)
    asset=register_asset(ws,path,'test',{'review':'fixture'})
    request={'playbook':'comic_lore','visual_selection':{'layers':{'u1':{'setting':asset['id']}}}}
    old=ws.create('entertainment',request);ws.update(old['id'],status='ready')
    with pytest.raises(Held,match='recent story image'):check_lore_reuse(ws,ws.create('entertainment',request))
    request['visual_selection']['layers']['u1']['setting_repeat_reason']='Return to the established room for this continuation.'
    check_lore_reuse(ws,ws.create('entertainment',request))
