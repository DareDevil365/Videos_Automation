"""Composition acceptance: supplied media geometry, source audio and timed effects."""
from array import array
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw
import pytest

from shorts_editor.composition import require_inputs
from shorts_editor.jobspec import materialize_job
from shorts_editor.models import template_project, validate_project, ValidationError
from shorts_editor.render import preview, render_project
from shorts_editor.store import Store, probe


@pytest.fixture(scope="module")
def supplied(tmp_path_factory):
    root=tmp_path_factory.mktemp("supplied-clips")
    store=Store(root/"workspace")
    # Clearly marked synthetic fixtures test the media slots; never presented as gameplay.
    for name,color,frequency,size in (("background","blue",330,"180x320"),("foreground","green",660,"320x160")):
        subprocess.run(["ffmpeg","-v","error","-f","lavfi","-i",f"color=c={color}:s={size}:r=30:d=2",
                        "-f","lavfi","-i",f"sine=frequency={frequency}:duration=2", "-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",
                        "-t","2",str(root/(name+".mp4"))],check=True)
    image=Image.new("RGB",(320,160),"green")
    draw=ImageDraw.Draw(image);draw.rectangle((25,25,60,60),fill="white")
    image.save(root/"screenshot.png")
    return root,store


def job_for(root, format_id="overlay"):
    return {"template":format_id,"name":"Supplied media test","duration":2,"effect_at":1,
            "inputs":{"background":"background.mp4","foreground":"foreground.mp4"}}


@pytest.mark.parametrize("format_id",["overlay","stack","focus"])
def test_compositions_render_supplied_clips(supplied,tmp_path,format_id):
    root,store=supplied
    p=materialize_job(job_for(root,format_id),store,root)
    output=tmp_path/(format_id+".mp4")
    manifest=render_project(p,store,output)
    subprocess.run(["ffmpeg","-v","error","-i",str(output),"-f","null","-"],capture_output=True,check=True)
    assert (manifest["width"],manifest["height"])==(720,1280)
    assert abs(manifest["duration"]-2)<.15
    assert output.with_suffix(".srt").read_text()=="" # No fabricated captions from a chat screenshot.
    with Image.open(output.with_suffix(".png")) as frame:
        if format_id=="overlay":
            assert frame.getpixel((300,220))[1]>80 # Actual foreground pixels.
            assert frame.getpixel((300,600))[2]>150 # Actual background remains visible.
        if format_id=="stack":
            assert frame.getpixel((300,300))[1]>80
            assert frame.getpixel((300,1000))[2]>150


def test_contain_does_not_cover_background_with_padding(supplied):
    root,store=supplied
    job=job_for(root);job["inputs"]["foreground"]="screenshot.png"
    p=materialize_job(job,store,root)
    with Image.open(preview(p,store,at=.2)) as frame:
        assert frame.getpixel((180,100))[1]>70
        assert frame.getpixel((180,250))[2]>150 # Below the short screenshot but inside its max-height box.


@pytest.mark.parametrize("effect",["punch","flash","shake"])
def test_effects_and_cta_are_timed_not_permanent(supplied,tmp_path,effect):
    root,store=supplied
    job=job_for(root);job["inputs"]["foreground"]="screenshot.png"
    job["composition"]={"effect":effect,"border_width":4,"glow":8,"cta":True,"cta_at":1,"cta_duration":.7}
    p=materialize_job(job,store,root)
    with Image.open(preview(p,store,at=.1)) as early, Image.open(preview(p,store,at=1.05)) as late:
        assert ImageChops.difference(early,late).getbbox() is not None
        # The CTA occupies the lower frame only at its configured time.
        assert early.getpixel((180,550))[2]>150
        assert late.getpixel((180,550))[0]>180
    render_project(p,store,tmp_path/(effect+".mp4"))


def test_foreground_speech_track_is_selected(supplied,tmp_path):
    root,store=supplied
    p=materialize_job(job_for(root),store,root)
    output=tmp_path/"foreground-audio.mp4"
    render_project(p,store,output)
    raw=subprocess.run(["ffmpeg","-v","error","-ss","0.2","-i",str(output),"-t","1","-vn","-ac","1","-ar","24000","-f","s16le","-"],capture_output=True,check=True).stdout
    samples=array("h");samples.frombytes(raw)
    frequency=sum(a<=0<b for a,b in zip(samples,samples[1:]))/(len(samples)/24000)
    assert 640<frequency<680,frequency # Foreground is 660 Hz; background is 330 Hz.


def test_video_punch_with_glow_keeps_fixed_frames(supplied,tmp_path):
    """Regression for the Windows heap crash on the aura payoff scene."""
    root,store=supplied
    job=job_for(root,'stack');job['duration']=3;job['effect_at']=2.65
    job['composition']={'effect':'punch','height':.65,'border_width':2,'glow':8,'effect_duration':.3}
    p=materialize_job(job,store,root)
    output=tmp_path/'video-punch-glow.mp4'
    result=render_project(p,store,output)
    assert abs(result['duration']-3)<.15
    checked=subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],capture_output=True)
    assert checked.returncode==0
    assert (result['width'],result['height'])==(720,1280)


def test_empty_layout_is_previewable_but_cannot_export(supplied,tmp_path):
    _,store=supplied
    p=template_project("overlay")
    assert preview(p,store).is_file()
    with pytest.raises(ValidationError,match="background/primary"):
        render_project(p,store,tmp_path/"empty.mp4")
    p["composition"]["x"]=.8
    with pytest.raises(ValidationError,match="inside the canvas"):
        validate_project(p)


def test_layout_json_can_be_rebound_without_old_media(supplied,tmp_path):
    root,store=supplied
    p=template_project("overlay");p["composition"].update(border_width=6,x=.05,width=.9)
    layout=tmp_path/"layout.json";layout.write_text(json.dumps(p),encoding="utf-8")
    job=job_for(root);job["template"]=str(layout)
    prepared=materialize_job(job,store,root)
    assert prepared["composition"]["border_width"]==6
    assert prepared["scenes"][0]["media"]
    job["inputs"]["background"]="https://example.com/clip.mp4"
    with pytest.raises(ValidationError,match="does not download"):
        materialize_job(job,store,root)


def test_program_can_export_and_read_one_json_result_without_browser(supplied,tmp_path):
    root,_=supplied
    payload=job_for(root)
    payload["inputs"]={key:str(root/value) for key,value in payload["inputs"].items()}
    payload["shots"]=[{"duration":1,"media_start":0,"secondary_start":0},
                      {"duration":1,"media_start":1,"secondary_start":1}]
    job=tmp_path/"agent-edit.json";job.write_text(json.dumps(payload),encoding="utf-8")
    output=tmp_path/"automatic.mp4"
    command=[sys.executable,str(Path(__file__).resolve().parents[1]/"run_editor.py"),
             "--data",str(tmp_path/"workspace"),"compose",str(job),"--output",str(output),"--json"]
    result=subprocess.run(command,capture_output=True,text=True,encoding="utf-8",timeout=45)
    assert result.returncode==0,result.stderr
    message=json.loads(result.stdout) # No progress text mixed into the JSON channel.
    assert message["schema_version"]==1 and message["status"]=="complete"
    assert all(Path(path).is_file() for path in message["outputs"].values())
    assert message["outputs"]["video"]==str(output.resolve())
    assert abs(message["duration"]-2)<.15
    assert "Rendering scene" in result.stderr
    # Repeating an AI job must not overwrite a finished video.
    repeated=subprocess.run(command,capture_output=True,text=True,encoding="utf-8",timeout=20)
    assert repeated.returncode!=0
    assert json.loads(repeated.stdout)["status"]=="failed"
    assert "already exists" in json.loads(repeated.stdout)["error"]["message"]


def test_missing_media_returns_structured_failure_to_the_caller(tmp_path):
    job=tmp_path/"broken.json"
    job.write_text(json.dumps({"template":"overlay","inputs":{"background":"missing.mp4"}}),encoding="utf-8")
    result=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/"run_editor.py"),
                           "--data",str(tmp_path/"workspace"),"compose",str(job),"--output",str(tmp_path/"bad.mp4"),"--json"],
                          capture_output=True,text=True,encoding="utf-8",timeout=20)
    assert result.returncode!=0
    message=json.loads(result.stdout)
    assert message["status"]=="failed" and message["error"]["type"]=="ValidationError"
    assert not (tmp_path/"bad.mp4").exists()
