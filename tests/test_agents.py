from copy import deepcopy
from datetime import datetime,timezone,timedelta
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import io
import json
from pathlib import Path
import subprocess
import threading

import pytest
from PIL import Image

from yt_pipeline.core import Workspace,Held,now,file_hash
from yt_pipeline.assets import register_asset,asset_record
from yt_pipeline.editorial import editorial_context,HOOK_FRAMEWORKS
from yt_pipeline.media_agent import commons_license,commons_acquire
from yt_pipeline.transcripts import parse_subtitles,clip_cues,burn_captions
from yt_pipeline.source_agent import register_source,ingest_source
from yt_pipeline.clip_agent import select_moments,research_handoff
from yt_pipeline.browser_agent import create_generation,execute_page,selector_template,browser_context,read_generation
from yt_pipeline.pipeline import Pipeline

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def ws(tmp_path):return Workspace(tmp_path/'pipeline')


def test_agreed_editorial_scope():
    with pytest.raises(Held) as exc:editorial_context({'channel':'education','request':{'topic':'Python floating point arithmetic'}})
    assert exc.value.code=='off_strategy'
    policy=editorial_context({'channel':'education','request':{'topic':'Stop procrastinating on studying'}})
    assert any('studying' in item for item in policy['pillars'])
    assert 'hook_frameworks' in policy
    assert any(item['name']=='skeptical value reaction' for item in HOOK_FRAMEWORKS)


@pytest.mark.parametrize('name,url,accepted',[
    ('CC BY 4.0','https://creativecommons.org/licenses/by/4.0',True),
    ('CC0','https://creativecommons.org/publicdomain/zero/1.0',True),
    ('Public domain','',True),('CC BY-SA 4.0','https://creativecommons.org/licenses/by-sa/4.0',False),
    ('CC BY-NC 4.0','https://creativecommons.org/licenses/by-nc/4.0',False),('Unknown','',False)])
def test_license_allowlist(name,url,accepted):
    assert bool(commons_license({'LicenseShortName':{'value':name},'LicenseUrl':{'value':url}}))==accepted


def test_real_image_download_contract_and_cache(ws):
    picture=io.BytesIO();Image.new('RGB',(400,500),'orange').save(picture,format='JPEG')
    calls=[]
    metadata={'query':{'pages':{'1':{'title':'File:Notebook.jpg','imageinfo':[{'mime':'image/jpeg','width':400,'height':500,
        'url':'https://upload.wikimedia.org/owned.jpg','thumburl':'https://thumb.wikimedia.org/owned.jpg','descriptionurl':'https://commons.wikimedia.org/wiki/File:Notebook.jpg',
        'extmetadata':{'Artist':{'value':'Example author'},'LicenseShortName':{'value':'CC BY 4.0'},'LicenseUrl':{'value':'https://creativecommons.org/licenses/by/4.0'}}}]}}}}
    def fake(url,**kwargs):
        calls.append(url)
        return (json.dumps(metadata).encode(),'application/json',url) if '/w/api.php?' in url else (picture.getvalue(),'image/jpeg',url)
    asset=commons_acquire(ws,'notebook','image',fake)
    assert asset['kind']=='image' and 'Example author' in asset['attribution']
    assert asset['evidence']['license']['name']=='CC BY 4.0'
    again=commons_acquire(ws,'notebook','image',fake)
    assert again['id']==asset['id'] and len(calls)==2


def test_subtitle_import_dedup_numeric_text_and_clip_offsets(tmp_path):
    path=tmp_path/'source.vtt';path.write_text('WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nHello <b>world</b>\n\n00:00:02.000 --> 00:00:04.000\nHello world\n\n00:00:05.000 --> 00:00:06.000\n42\n',encoding='utf-8')
    cues=parse_subtitles(path)
    assert len(cues)==2 and cues[0]['end']==4 and cues[1]['text']=='42'
    trimmed=clip_cues(cues,2,5.5)
    assert trimmed[0]['start']==0 and trimmed[0]['end']==2
    assert trimmed[1]['end']==3.5


def test_moment_selection_rejects_invented_indices():
    transcript={'cues':[{'start':0,'end':8,'text':'A complete source sentence.'}]}
    class Bad:
        def generate(self,*args):return {'moments':[{'start_cue':3,'end_cue':7,'title':'Invented','reason':'bad'}]}
    with pytest.raises(Held) as exc:select_moments(transcript,Bad())
    assert exc.value.code=='clip_range_invented'


def test_source_permission_and_expiry(ws,tmp_path):
    source={'id':'example','title':'Owned source','local_media':str(tmp_path/'not-yet.mp4'),'permission':{'evidence':'owner declaration','commercial':False,'editing':True}}
    with pytest.raises(Held):register_source(ws,source)
    source['permission'].update(commercial=True,expires_at='2020-01-01T00:00:00Z')
    register_source(ws,source)
    with pytest.raises(Held) as exc:ingest_source(ws,'example')
    assert exc.value.code=='source_expired'


def test_research_handoff_does_not_invent_sources(ws,tmp_path):
    source={'id':'approved','title':'Permitted episode','work':'Example show','episode':'1','local_media':str(tmp_path/'owned.mp4'),
            'permission':{'evidence':'Owner declaration','commercial':True,'editing':True}}
    register_source(ws,source)
    class Bad:
        def generate(self,*args):return {'requests':[{'source_id':'unknown','work':'Example show','episode':'2','target_moment':'a quote','evidence_url':'https://example.com/observed','reason':'lead'}]}
    with pytest.raises(Held):research_handoff(ws,{'candidates':[{'url':'https://example.com/observed'}]},['approved'],Bad())


def make_video(path,color='blue',duration=3):
    subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-f','lavfi','-i',f'color=c={color}:s=180x320:r=30:d={duration}',
                    '-f','lavfi','-i',f'sine=frequency=330:duration={duration}','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(path)],check=True,capture_output=True)
    return path


def test_actual_clip_caption_burn_in(ws,tmp_path):
    asset=register_asset(ws,make_video(tmp_path/'source.mp4'),'test',{'reference':'Technical fixture only'})
    request=json.loads((ROOT/'examples/chat-request.json').read_text())
    request.update(format='clip',clip_asset_id=asset['id'],clip_start=0,clip_end=2,
                   caption_cues=[{'start':0,'end':1.9,'text':'Actual timed subtitle'}])
    request['script']['format']='clip';request['script']['units']=request['script']['units'][:1]
    request['script']['edit'].update(effect='none',payoff_unit_id='one')
    job=ws.create('entertainment',request);result=Pipeline(ws).run(job['id'])
    assert result['status']=='ready',result['message']
    rendered=json.loads(Path(result['artifacts']['render']['path']).read_text())
    video=Path(rendered['video']);manifest=json.loads(video.with_suffix('.manifest.json').read_text())
    assert manifest['caption_burn']['video_sha256']==file_hash(video)
    assert video.with_name('video.clean.mp4').exists()
    assert 'Actual timed subtitle' in Path(rendered['captions']).read_text()
    def pixels(path):
        r=subprocess.run(['ffmpeg','-v','error','-ss','0.5','-i',str(path),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True)
        return Image.open(io.BytesIO(r.stdout)).convert('RGB')
    before=pixels(video.with_name('video.clean.mp4'));after=pixels(video)
    assert sum(max(p)-min(p)<20 and min(p)>220 for p in after.getdata())>sum(max(p)-min(p)<20 and min(p)>220 for p in before.getdata())


def test_browser_worker_download_and_no_duplicate_submission(ws,tmp_path):
    pytest.importorskip('playwright.sync_api')
    media=make_video(tmp_path/'fixture.mp4')
    html='''<!doctype html><title>Local worker contract fixture — not Google</title><h1>Local worker test</h1><p id="model">Veo 3 Fast</p><p id="allowance">50 included credits</p><p id="cost">0 credits</p><label>Prompt<textarea id="prompt"></textarea></label><button id="generate" onclick="document.querySelector('#download').hidden=false;this.dataset.submitted='yes'">Generate mock</button><a id="download" hidden href="/fixture.mp4" download="fixture.mp4">Download mock video</a>'''
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            payload=media.read_bytes() if self.path=='/fixture.mp4' else html.encode()
            self.send_response(200);self.send_header('Content-Type','video/mp4' if self.path=='/fixture.mp4' else 'text/html');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    url=f'http://127.0.0.1:{server.server_port}/';job=create_generation(ws,'An original clay sculpture loop, with a complete payoff.')
    selectors={**selector_template(),'prompt_selector':'#prompt','generate_selector':'#generate','download_selector':'#download',
               'model_selector':'#model','included_allowance_selector':'#allowance','cost_selector':'#cost'}
    try:
        with browser_context(ws,headed=False) as context:
            page=context.new_page();page.goto(url)
            dry=execute_page(ws,job,page,selectors,False,test_url=url)
            assert dry['dry_run'] and page.locator('#prompt').input_value()==''
            result=execute_page(ws,job,page,selectors,True,test_url=url)
            assert result['status']=='downloaded'
            assert asset_record(ws,result['asset_id'])['test_only'] is True
            screenshot=ROOT/'output'/'playwright'/'browser-worker-mock.png';screenshot.parent.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(screenshot))
            assert execute_page(ws,job,page,selectors,True,test_url=url)['asset_id']==result['asset_id']
            another=create_generation(ws,'Another original clay loop, with a complete visual payoff.')
            page.goto(url);page.locator('#cost').evaluate("el=>el.textContent='10 credits'")
            with pytest.raises(Held) as exc:execute_page(ws,another,page,selectors,True,test_url=url)
            assert exc.value.code=='browser_credit_limit'
            assert page.locator('#prompt').input_value()==''
    finally:server.shutdown();server.server_close();thread.join(timeout=2)
