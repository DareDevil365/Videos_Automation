"""Generation controls: real local DOM/downloads, no Google or user profile."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import io
from pathlib import Path
import threading

import pytest
from PIL import Image

from yt_pipeline.core import Workspace,Held
from yt_pipeline.generation_settings import plan_settings,validate_settings,apply_settings
from yt_pipeline.browser_agent import create_generation,selector_template,execute_page,read_generation,browser_context


CAPABILITIES={'aspect_ratios':['9:16'],
 'resolutions':[{'label':'720p','width':720,'height':1280},{'label':'1080p','width':1080,'height':1920},{'label':'4K','width':2160,'height':3840}],
 'durations_seconds':[4,6,8,10],'thinking_levels':['Low','High'],'optional_tools':['grounding']}


def test_smallest_adequate_settings_not_4k_or_long_default():
    result=plan_settings('video',{'slot_width':360,'slot_height':640,'usable_seconds':3},CAPABILITIES)
    assert result['settings']=={'aspect_ratio':'9:16','resolution':'720p','duration_seconds':4,'thinking_level':'Low','grounding':False}
    assert result['usable_seconds']==3
    assert plan_settings('image',{'slot_width':800,'slot_height':1420,'complexity':'complex'},CAPABILITIES)['settings']['resolution']=='1080p'


def test_no_undersized_or_unsupported_fallback():
    with pytest.raises(Held) as e:plan_settings('video',{'usable_seconds':11},CAPABILITIES)
    assert e.value.code=='generation_duration'
    with pytest.raises(Held) as e:plan_settings('image',{'slot_width':5000},CAPABILITIES)
    assert e.value.code=='generation_resolution'


@pytest.mark.parametrize('settings',[{'duration_seconds':float('nan')},{'duration_seconds':-1},{'resolution':False},{'grounding':'false'},{'arbitrary_code':'x'}])
def test_settings_contract_rejects_bad_values(settings):
    with pytest.raises(ValueError):validate_settings(settings)


def test_direct_routes_and_origin_validation(tmp_path):
    ws=Workspace(tmp_path/'workspace')
    job=create_generation(ws,'An original simple material texture image.',kind='image',settings={'resolution':'720p'})
    assert 'model=gemini-3.1-flash-image' in job['provider_url']
    assert job['settings']['resolution']=='720p'
    for url in ['https://aistudio.google.com.evil.test/','http://aistudio.google.com/','https://user@aistudio.google.com/','https://aistudio.google.com:444/']:
        with pytest.raises(ValueError):create_generation(ws,'Concrete original media generation prompt.',url=url)


HTML='''<!doctype html><title>Local sidebar fixture, not Google</title>
<p id="model">Gemini image test</p><p id="allowance">50 included credits</p><p id="cost">5 credits</p>
<textarea id="prompt"></textarea>
<select id="resolution" onchange="document.querySelector('#cost').textContent=this.value==='720'?'0 credits':'5 credits'">
<option value="1080">1080p</option><option value="720">720p</option></select>
<select id="ratio"><option>Auto</option><option>9:16</option></select>
<input id="duration" type="range" min="1" max="10" step="1" value="10">
<input id="grounding" type="checkbox" checked>
<button id="thinking" onclick="document.querySelector('#menu').hidden=false">High</button>
<div id="menu" hidden><button onclick="document.querySelector('#thinking').textContent='Low';this.parentElement.hidden=true">Low</button></div>
<button id="generate" onclick="this.dataset.calls=Number(this.dataset.calls||0)+1;document.querySelector('#download').hidden=false">Generate</button>
<a id="download" hidden href="/image.png" download="image.png">Download</a>'''
BINDINGS={'resolution':{'selector':'#resolution','type':'select','values':{'720p':'720','1080p':'1080'}},
 'aspect_ratio':{'selector':'#ratio','type':'select'},
 'duration_seconds':{'selector':'#duration','type':'slider'},
 'thinking_level':{'selector':'#thinking','type':'dropdown','option_selector':'#menu button'},
 'grounding':{'selector':'#grounding','type':'checkbox'}}


@pytest.fixture
def local_page(tmp_path):
    picture=io.BytesIO();Image.new('RGB',(160,284),'turquoise').save(picture,'PNG')
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            body=picture.getvalue() if self.path=='/image.png' else HTML.encode()
            self.send_response(200);self.send_header('Content-Type','image/png' if self.path=='/image.png' else 'text/html');self.end_headers();self.wfile.write(body)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    ws=Workspace(tmp_path/'workspace');url=f'http://127.0.0.1:{server.server_port}/'
    selectors={**selector_template(),'model_selector':'#model','prompt_selector':'#prompt','generate_selector':'#generate',
               'download_selector':'#download','cost_selector':'#cost','included_allowance_selector':'#allowance','settings':BINDINGS}
    try:
        with browser_context(ws,headed=False) as context:
            page=context.new_page();page.goto(url);yield ws,page,url,selectors
    finally:server.shutdown();server.server_close();thread.join(timeout=2)


def test_sidebar_readback_cost_after_settings_and_download(local_page):
    ws,page,url,selectors=local_page
    settings={'resolution':'720p','aspect_ratio':'9:16','duration_seconds':3,'thinking_level':'Low','grounding':False}
    job=create_generation(ws,'Original material pattern for a small visual panel.',kind='image',model='Gemini image test',settings=settings)
    preview=execute_page(ws,job,page,selectors,test_url=url)
    assert preview['preflight']['credit_cost']==0
    assert page.locator('#prompt').input_value()==''
    assert page.locator('#duration').input_value()=='3'
    assert not page.locator('#grounding').is_checked()
    result=execute_page(ws,job,page,selectors,apply=True,test_url=url)
    assert result['status']=='downloaded' and result['settings_observed']['resolution']['observed']=='720'
    assert Path(result['file']).is_file()
    execute_page(ws,job,page,selectors,apply=True,test_url=url)
    assert page.locator('#generate').get_attribute('data-calls')=='1'


def test_mismatch_and_stale_result_never_submit(local_page):
    ws,page,url,selectors=local_page
    job=create_generation(ws,'Original material pattern for a small panel.',kind='image',model='Gemini image test',settings={'resolution':'720p'})
    selectors['settings']={'resolution':{**BINDINGS['resolution'],'observed_values':{'720p':'wrong'}}}
    with pytest.raises(Held) as e:apply_settings(page,job['settings'],selectors['settings'],timeout_ms=150)
    assert e.value.code=='browser_setting_mismatch'
    assert not page.locator('#generate').get_attribute('data-calls')
    page.locator('#download').evaluate('element => element.hidden=false')
    with pytest.raises(Held) as e:execute_page(ws,job,page,selectors,apply=True,test_url=url)
    assert e.value.code=='browser_existing_result'


def test_reconcile_downloads_without_generating_again(local_page):
    ws,page,url,selectors=local_page
    job=create_generation(ws,'Original material pattern for a small panel.',kind='image',model='Gemini image test',settings={'resolution':'720p'})
    execute_page(ws,job,page,selectors,test_url=url)
    original=selectors['download_selector'];selectors['download_selector']='#never-arrives'
    with pytest.raises(Held) as e:execute_page(ws,job,page,selectors,apply=True,test_url=url,timeout=5)
    assert e.value.code=='browser_generation_timeout'
    assert read_generation(ws,job['id'])['submission_started']
    selectors['download_selector']=original
    result=execute_page(ws,job,page,selectors,apply=True,test_url=url,reconcile=True)
    assert result['status']=='downloaded'
    assert page.locator('#generate').get_attribute('data-calls')=='1'


def test_free_label_must_be_explicit(local_page):
    ws,page,url,selectors=local_page
    job=create_generation(ws,'Original material pattern image.',kind='image',model='Gemini image test')
    selectors['cost_mode']='free'
    page.locator('#cost').evaluate('e => e.textContent="Free"')
    assert execute_page(ws,job,page,selectors,test_url=url)['preflight']['cost_mode']=='free'
    page.locator('#cost').evaluate('e => e.textContent="Upgrade for free credits"')
    with pytest.raises(Held) as e:execute_page(ws,job,page,selectors,test_url=url)
    assert e.value.code=='browser_cost_unverified'


def test_brave_launch_uses_dedicated_profile_and_attachment_does_not_close_owner(monkeypatch,tmp_path):
    from types import SimpleNamespace
    import playwright.sync_api
    import yt_pipeline.browser_agent as module
    calls=[]
    context=SimpleNamespace(close=lambda:calls.append('context_closed'))
    browser=SimpleNamespace(contexts=[context])
    chromium=SimpleNamespace(launch_persistent_context=lambda path,**kw:(calls.append((path,kw)) or context),
                            connect_over_cdp=lambda endpoint,**kw:(calls.append(('attached',endpoint)) or browser))
    @contextmanager
    def runtime():
        try:yield SimpleNamespace(chromium=chromium)
        finally:calls.append('client_disconnected')
    monkeypatch.setattr(playwright.sync_api,'sync_playwright',runtime)
    monkeypatch.setattr(module,'brave_executable',lambda:'installed-brave.exe')
    ws=Workspace(tmp_path/'workspace')
    with browser_context(ws,channel='brave'):pass
    path,options=calls[0]
    assert path==str(ws.root/'credentials/generation-browser-profile')
    assert options['executable_path']=='installed-brave.exe'
    assert calls.count('context_closed')==1
    calls.clear()
    with browser_context(ws,options={'mode':'cdp','cdp_url':'http://127.0.0.1:9222'}):pass
    assert 'context_closed' not in calls
    assert 'client_disconnected' in calls
    with pytest.raises(Held) as e:
        with browser_context(ws,options={'mode':'cdp','cdp_url':'http://remote.example:9222'}):pass
    assert e.value.code=='browser_endpoint'
