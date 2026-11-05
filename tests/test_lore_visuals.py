from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess

import pytest
from PIL import ImageChops

from yt_pipeline.core import Held,Workspace,digest
from yt_pipeline.lore_visuals import KINDS,plan_lore,lore_frame,render_lore_shot,build_lore_visuals


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
