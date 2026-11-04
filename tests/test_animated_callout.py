import shutil
import subprocess

import pytest
from PIL import Image

from yt_pipeline.scene_direction import callout_animation_state,draw_callout
from yt_pipeline.planned_visuals import _motion


def pixels(picture):
    data=picture.convert('RGB').tobytes()
    return sum(r>150 and r>g*1.8 and r>b*1.8 for r,g,b in zip(data[0::3],data[1::3],data[2::3]))


def test_callout_draws_on_then_disappears_and_preserves_target_geometry():
    input={'source_size':(720,1280),'callout':{'kind':'circle_arrow','target':'eyes','label':'','box':[.4,.3,.6,.35]}}
    counts=[];boxes=[]
    for second in [0,.22,.50,1.15,2.7]:
        picture=Image.new('RGB',(720,1280),'#303030')
        metadata=draw_callout(picture,**input,**callout_animation_state(second,3))
        counts.append(pixels(picture));boxes.append(metadata['display_box'])
    assert counts[0]==counts[-1]==0 and 0<counts[1]<counts[2]<counts[3]
    assert all(box==boxes[0] for box in boxes)


def test_thick_ring_leaves_a_tiny_landscape_clue_visible():
    picture=Image.new('RGB',(1280,720),'#f4dda0')
    draw_callout(picture,(1280,720),{'kind':'circle_arrow','target':'small window','label':'','box':[.68,.35,.715,.40]})
    for x in range(871,914):
        for y in range(253,287):
            assert picture.getpixel((x,y))==(244,221,160)


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
def test_actual_animation_video_has_red_entry_full_circle_and_clear_exit(tmp_path):
    poster=tmp_path/'base.png';Image.new('RGB',(720,1280),'#303030').save(poster)
    output=tmp_path/'callout.mp4'
    _motion(poster,1.4,output,'hold',callout={'source_size':(720,1280),
        'callout':{'kind':'circle_arrow','target':'eyes','label':'','box':[.4,.3,.6,.35]}})
    counts=[]
    for second in [0,.1,.6,1.35]:
        data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(second),'-i',str(output),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
        counts.append(pixels(Image.frombytes('RGB',(720,1280),data)))
    assert counts[0]==counts[-1]==0 and 0<counts[1]<counts[2]
