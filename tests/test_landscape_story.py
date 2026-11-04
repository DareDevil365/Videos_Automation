from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image,ImageChops
import pytest

from shorts_editor.jobspec import materialize_job
from shorts_editor.models import new_project,new_scene,validate_project,dimensions,ValidationError
from shorts_editor.render import render_project,preview
from shorts_editor.store import Store
from yt_pipeline.core import Workspace,Held
from yt_pipeline.illustrated_story import story_frame,normalized_box,render_story_shot
from yt_pipeline.transcripts import burn_captions


def test_landscape_profile_is_explicit_and_retains_short_limits():
    p=new_project('focus');assert dimensions(p)==(720,1280)
    p['profile']='documentary';assert dimensions(validate_project(p))==(1280,720)
    p['resolution']='1080p';assert dimensions(validate_project(p))==(1920,1080)
    p['format']='chat'
    with pytest.raises(ValidationError,match='full-frame'):validate_project(p)
    p=new_project('focus');p['scenes']=[{**new_scene(),'duration':100},{**new_scene(),'duration':100}]
    with pytest.raises(ValidationError,match='180'):validate_project(p)
    p['profile']='documentary'
    with pytest.raises(ValidationError,match='180'):validate_project(p)


def test_story_motion_light_and_source_coordinates():
    source=Image.new('RGB',(1280,720),'#547781')
    effect={'crop_start':[0,0,1,1],'crop_end':[0,0,1,1],'flash_box':[.7,.2,.8,.3]}
    on=story_frame(source,{},0,4,effect);off=story_frame(source,{},.2,4,effect)
    assert on.size==off.size==(1280,720)
    assert sum(on.getpixel((960,180)))>sum(off.getpixel((960,180)))
    assert on.getpixel((300,300))==off.getpixel((300,300))
    rain=story_frame(source,{},.3,4,{'rain':True})
    assert ImageChops.difference(on,rain).getbbox()
    with pytest.raises(Held):normalized_box([0,0,float('nan'),1],'crop')
    with pytest.raises(Held):normalized_box([0,0,1.1,1],'crop')


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
def test_actual_landscape_composition_preview_and_caption_resolution(tmp_path):
    art=tmp_path/'art.png';Image.new('RGB',(1280,720),'#2d454e').save(art)
    moving=tmp_path/'moving.mp4';render_story_shot(art,{},1,moving,{'rain':True})
    store=Store(tmp_path/'media')
    project=materialize_job({'template':'focus','profile':'documentary','composition':{
        'x':0,'y':0,'width':1,'height':1,'foreground_fit':'cover','audio_source':'none'},
        'shots':[{'duration':1,'inputs':{'background':str(moving)}}]},store,tmp_path)
    poster=preview(project,store)
    with Image.open(poster) as image:assert image.size==(640,360)
    output=tmp_path/'final.mp4';manifest=render_project(project,store,output)
    assert (manifest['width'],manifest['height'])==(1280,720)
    burn_captions(output,[{'start':0,'end':.9,'text':'A readable landscape caption.'}],caption_bar=True,canvas=(1280,720))
    ass=output.with_suffix('.ass').read_text(encoding='utf-8')
    assert 'PlayResX: 1280' in ass and 'PlayResY: 720' in ass and 'Arial,30,' in ass
    assert '1280-bar_height' not in ass
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(output)]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert (video['width'],video['height'])==(1280,720)


def test_assistant_story_uses_provided_text_and_closed_local_provider(tmp_path):
    from yt_pipeline.writer import write_script
    spec=importlib.util.spec_from_file_location('story_pilot',Path(__file__).resolve().parents[1]/'tools/create_storytelling_pilot.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    script=json.loads((Path(__file__).resolve().parents[1]/'examples/storytelling-last-light.json').read_text())
    request,plan=module.prepare(script,{f'{i:02d}':f'asset{i}' for i in range(1,7)})
    original=deepcopy(script);ws=Workspace(tmp_path/'ws');job=ws.create('entertainment',request);calls=[]
    class Local:
        origin='assistant_authored_at_owner_request'
        def generate(self,purpose,*args,**kwargs):
            calls.append(purpose)
            assert purpose=='creative-director-v1'
            return deepcopy(plan)
    result=write_script(ws,job,request['brief'],Local())
    assert result['origin']=='provided_script' and result['creative_plan']['origin']==Local.origin
    assert calls==['creative-director-v1'] and script==original
    with ws.connect() as db:assert db.execute('select count(*) from usage').fetchone()[0]==0
