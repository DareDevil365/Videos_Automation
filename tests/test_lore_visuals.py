from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess

import pytest
from PIL import Image,ImageChops,ImageDraw

from yt_pipeline.core import Held,Workspace,digest
from yt_pipeline.lore_visuals import KINDS,plan_lore,lore_frame,render_lore_shot,build_lore_visuals
from yt_pipeline.lore_actions import COLORS, resolve_actions
from yt_pipeline.source_sets import check_lore_reuse, source_painter
from yt_pipeline.contracts import script_contract
from yt_pipeline.lore_thunder_cutouts import Sprite, ThunderCutouts


ROOT=Path(__file__).resolve().parents[1]


def fixture():
    script=json.loads((ROOT/'examples/lore-series/secret-wars-2015/part-1.json').read_text(encoding='utf-8'))
    brief=json.loads((ROOT/'research/content-lore/SECRET_WARS_2015_BRIEF.json').read_text(encoding='utf-8'))
    return script,brief


def test_compiled_lore_preserves_exact_words_labels_claims_and_explicit_scene_choices():
    script,brief=fixture();original=deepcopy(script)
    result=plan_lore(script,{'lore_scenes':{'u1':'throne'}},brief);plan=result['plan']
    assert script==original and result['script_sha256']==digest(script)
    assert result['origin']=='compiled_lore_rules_v1' and plan['cast'][0]['voice_id']=='bm_george'
    for scene,unit in zip(plan['scenes'],script['units']):
        assert (scene['text'],scene['label'],scene['claim_ids'])==(unit['text'],unit['onscreen'],unit['claim_ids'])
    assert plan['scenes'][0]['kind']=='throne'
    for request in ({'lore_scenes':{'missing':'throne'}},{'lore_scenes':{'u1':'download-panel'}}):
        with pytest.raises(Held):plan_lore(script,request,brief)
    broken=deepcopy(script);broken['units'][0]['claim_ids']=['invented']
    with pytest.raises(Held):plan_lore(broken,{},brief)


def test_authored_beat_visual_choices_are_validated_and_can_be_overridden():
    script, brief = fixture()
    script['units'][0].update(lore_scene='thor_hammer_hook', lore_camera='detail')
    validated = script_contract(script, brief, 'lesson')
    scene = plan_lore(validated, {}, brief)['plan']['scenes'][0]
    assert (scene['kind'],scene['framing']) == ('thor_hammer_hook','detail')
    scene = plan_lore(validated, {'lore_scenes':{'u1':'bill_fleet'},'lore_cameras':{'u1':'wide'}}, brief)['plan']['scenes'][0]
    assert (scene['kind'],scene['framing']) == ('bill_fleet','wide')
    script['units'][0]['lore_scene'] = 'unsupported-animation'
    with pytest.raises(Held, match='supported lore_scene'):
        script_contract(script, brief, 'lesson')


@pytest.mark.parametrize("facing", [1, -1])
def test_sourced_arm_keeps_shoulder_and_grip_anchors_when_rotated(facing):
    part = Image.new("RGBA", (104,42))
    draw = ImageDraw.Draw(part)
    draw.rectangle((3,7,100,35), fill="#677a8c")
    draw.ellipse((10,14,23,28), fill="#eb5838")
    draw.ellipse((77,14,92,28), fill="#5edd80")
    output = Image.new("RGBA", (330,350))
    ThunderCutouts._limb(output, Sprite(part,(16,21),(85,21)), (114,107), (204,237), facing, 1)
    assert output.getpixel((114,107))[:3] == (235,88,56)
    assert output.getpixel((204,237))[:3] == (94,221,128)
    assert output.getpixel((0,0))[3] == 0


def test_scene_art_changes_and_moves_without_intruding_on_caption_safe_area():
    hashes=set()
    for kind in KINDS:
        scene={'kind':kind,'label':'Exact scene phrase'}
        opening=lore_frame(scene,0,4);settled=lore_frame(scene,2.2,4);late=lore_frame(scene,3.6,4)
        assert settled.size==(720,1280)
        assert ImageChops.difference(opening,settled).getbbox()
        assert ImageChops.difference(settled,late).getbbox()
        assert ImageChops.difference(opening.crop((0,960,720,1280)),late.crop((0,960,720,1280))).getbbox() is None
        hashes.add(digest(settled.tobytes().hex()))
    assert len(hashes)==len(KINDS)


def test_lore_builder_rejects_frozen_script_or_order_changes_before_render(tmp_path):
    script,brief=fixture();record=plan_lore(script,{},brief);timing={'units':[{'id':'missing'}]}
    ws=Workspace(tmp_path/'ws');job=ws.create('entertainment',{'test_only':True})
    with pytest.raises(Held):build_lore_visuals(ws,job,script,timing,tmp_path/'visuals',record)
    broken=deepcopy(record);broken['script_sha256']='changed'
    with pytest.raises(Held):build_lore_visuals(ws,job,script,timing,tmp_path/'visuals',broken)


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='ffmpeg required')
def test_actual_lore_shot_is_portrait_video_with_measured_duration(tmp_path):
    path=tmp_path/'lore.mp4';render_lore_shot({'kind':'meal','label':'ONE SMALL GESTURE'},.8,path)
    result=subprocess.run(['ffprobe','-v','error','-show_entries','stream=width,height,r_frame_rate:format=duration','-of','json',str(path)],capture_output=True,text=True,check=True)
    data=json.loads(result.stdout);stream=data['streams'][0]
    assert (stream['width'],stream['height'],stream['r_frame_rate'])==(720,1280,'30/1')
    assert float(data['format']['duration'])==pytest.approx(.8,abs=.04)
    assert path.with_suffix('.png').is_file()


def test_action_and_moving_photo_stay_in_the_story_area():
    still = lambda *args: Image.new("RGB", (720,1280), "#111522")
    prop = Image.new("RGBA", (76,60), "#77777a")
    for kind in COLORS:
        actions = resolve_actions({"lore_actions":{"u1":{"kind":kind,"actor":"symbolic",
                                   "target":[530,420]}}}, {"units":[{"id":"u1"}]})
        paint = source_painter(still, [(prop,(260,640,336,700),("arc",[265,-95]))],
                               None, 0, action=actions["u1"])
        change = ImageChops.difference(paint({},0,3),paint({},2.3,3)).getbbox()
        assert change and 185 <= change[1] < change[3] <= 950


def test_recent_story_photo_needs_an_explicit_repeat_reason(tmp_path):
    from yt_pipeline.assets import register_asset

    ws = Workspace(tmp_path/'ws')
    image = tmp_path/'figure.png'
    Image.new("RGB",(64,64),"#448877").save(image)
    asset = register_asset(ws,image,'test',{"review":"fixture"})
    copy = register_asset(ws,image,'test',{"review":"second registration"})
    old = ws.create('entertainment',{'playbook':'comic_lore','source_panels':{'u1':[{'asset_id':asset['id']}]}})
    ws.update(old['id'], status='ready')
    request = {'playbook':'comic_lore','source_panels':{'u3':[{'asset_id':copy['id']}]}}
    with pytest.raises(Held, match='recent story image'):
        check_lore_reuse(ws, ws.create('entertainment',request))
    request['source_panels']['u3'][0]['repeat_reason'] = 'Callback to the same object before and after.'
    check_lore_reuse(ws, ws.create('entertainment',request))
