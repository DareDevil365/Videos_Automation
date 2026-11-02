"""Persistent-profile browser generation jobs with bounded, inspectable actions.

Provider selectors are explicit configuration, never guessed from an LLM's HTML.
The worker does not sign in, solve challenges, buy credits or enable billing.
"""
from contextlib import contextmanager
import json
from pathlib import Path
import os
import re
import time
import threading
from urllib.parse import urlparse
import uuid

from shorts_editor.store import write_json
from .assets import register_asset,asset_record
from .core import Held,now,digest,file_hash
from .generation_settings import validate_settings,plan_settings,apply_settings


PROVIDERS={'ai_studio':'https://aistudio.google.com/','gemini':'https://gemini.google.com/app','flow':'https://labs.google/fx/tools/flow'}
DIRECT_PAGES={'image':'https://aistudio.google.com/prompts/new_chat?model=gemini-3.1-flash-image',
              'video':'https://aistudio.google.com/u/5/prompts/new_chat'}


def provider_url(provider,url):
    parsed=urlparse(url);expected=urlparse(PROVIDERS[provider])
    if parsed.scheme!='https' or parsed.hostname!=expected.hostname or parsed.port not in (None,443) or parsed.username or parsed.password or parsed.fragment:
        raise ValueError('Generation URL must be an HTTPS page on the selected provider without credentials or fragment')
    return url


def brave_executable():
    candidates=[Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'BraveSoftware/Brave-Browser/Application/brave.exe',
                Path(os.environ.get('PROGRAMFILES(X86)','C:/Program Files (x86)'))/'BraveSoftware/Brave-Browser/Application/brave.exe',
                Path(os.environ.get('LOCALAPPDATA',''))/'BraveSoftware/Brave-Browser/Application/brave.exe']
    for path in candidates:
        if path.is_file():return str(path)
    raise Held('browser_brave_missing','Brave executable was not found; configure its installed executable_path')


def browser_folder(ws):
    path=ws.root/'browser-generation';path.mkdir(exist_ok=True);return path


def create_generation(ws,prompt,provider='ai_studio',kind='video',model=None,credit_limit=0,url=None,settings=None,requirements=None,capabilities=None):
    if provider not in PROVIDERS or kind not in ('image','video'):raise ValueError('Unknown browser generation provider/type')
    if not isinstance(prompt,str) or not 10<=len(prompt.strip())<=12000:raise ValueError('Supply a concrete generation prompt')
    if type(credit_limit) is not int or credit_limit<0:raise ValueError('Credit limit must be a nonnegative integer')
    target=provider_url(provider,url or (DIRECT_PAGES[kind] if provider=='ai_studio' else PROVIDERS[provider]))
    plan=plan_settings(kind,requirements,capabilities) if requirements is not None else None
    if requirements is not None and settings:raise ValueError('Use either shot requirements or explicit settings, not both')
    selected=validate_settings(plan['settings'] if plan else (settings or {}))
    id=uuid.uuid4().hex;folder=browser_folder(ws)/id;folder.mkdir()
    job={'id':id,'provider':provider,'provider_url':target,'kind':kind,'model_hint':model or ('gemini-3.1-flash-image' if kind=='image' else 'Veo|Omni'),
         'settings':selected,'setting_plan':plan,'requirements':requirements,'prompt':prompt.strip(),
         'included_credit_limit':credit_limit,'created_at':now(),'status':'queued','message':'Ready for browser preflight. No generation submitted.','submission_started':False}
    write_json(folder/'job.json',job);return job


def read_generation(ws,id):
    if not re.fullmatch(r'[a-f0-9]{32}',id):raise ValueError('Invalid generation job ID')
    return json.loads((browser_folder(ws)/id/'job.json').read_text(encoding='utf-8'))


def selector_template():
    return {'prompt_selector':'','generate_selector':'','download_selector':'',
            'model_selector':'','model_name_pattern':'','included_allowance_selector':'','cost_selector':'','cost_mode':'included_credits',
            'settings':{},
            'blocked_selector':'[role="dialog"], [role="alert"]',
            'blocked_text_pattern':'sign in|log in|captcha|verify you|buy credits|purchase|set up billing|enable billing|upgrade|quota exceeded|insufficient credits|out of credits',
            'note':'Calibrate actual visible controls. Settings bindings use selector/type and read-back verification. Preflight must prove the model and included/free cost. No guessed provider selectors.'}


@contextmanager
def browser_context(ws,headed=True,channel=None,options=None):
    try:from playwright.sync_api import sync_playwright
    except ImportError:raise Held('browser_runtime_missing','Install the browser optional dependencies and Playwright Chromium.')
    with sync_playwright() as runtime:
        options=options or {}
        if options.get('mode','persistent') not in ('persistent','cdp'):
            raise Held('browser_mode','Choose persistent worker profile or an explicit local CDP attachment')
        if options.get('mode')=='cdp':
            endpoint=urlparse(options.get('cdp_url',''))
            if endpoint.scheme not in ('http','ws') or endpoint.hostname not in ('127.0.0.1','localhost','::1') or not endpoint.port or endpoint.username or endpoint.password:
                raise Held('browser_endpoint','Use an explicitly configured local owner-started debugging endpoint')
            try:browser=runtime.chromium.connect_over_cdp(options['cdp_url'],timeout=15000)
            except Exception:raise Held('browser_connection','Cannot attach to the configured owner-started browser; no other session was launched')
            if len(browser.contexts)!=1:raise Held('browser_context_ambiguous','Expected one browser context for the configured attachment')
            # Exiting Playwright disconnects this client. Never close the attached browser/context.
            yield browser.contexts[0]
            return
        kwargs={'headless':not headed,'accept_downloads':True,'viewport':{'width':1280,'height':900}}
        selected=options.get('browser',channel)
        if options.get('executable_path'):kwargs['executable_path']=str(Path(options['executable_path']).resolve())
        elif selected=='brave':kwargs['executable_path']=brave_executable()
        elif selected:kwargs['channel']=selected
        profile=ws.root/'credentials'/'generation-browser-profile';profile.mkdir(exist_ok=True)
        try:context=runtime.chromium.launch_persistent_context(str(profile),**kwargs)
        except Exception:raise Held('browser_profile_busy','Could not start the saved browser profile. Close its other worker or install the selected browser.')
        try:yield context
        finally:context.close()


def visible(page,selector):
    if not selector:return None
    matches=page.locator(selector);count=matches.count()
    found=[matches.nth(i) for i in range(count) if matches.nth(i).is_visible()]
    if len(found)>1:raise Held('browser_selector_ambiguous','A configured UI selector matches multiple visible controls; recalibrate it.')
    return found[0] if found else None


def allowed_page(page,job,test_url=None):
    current=urlparse(page.url)
    if test_url:
        expected=urlparse(test_url)
        if current.scheme==expected.scheme and current.hostname==expected.hostname and current.port==expected.port:return
    expected=urlparse(job['provider_url'])
    if current.scheme!='https' or current.hostname!=expected.hostname or current.port not in (None,443) or current.username or current.password:
        raise Held('browser_navigation','The worker left the configured provider. Sign-in/redirect needs owner attention.')


def check_session(page,job,selectors,test_url=None):
    allowed_page(page,job,test_url)
    blocked=selectors.get('blocked_selector')
    if blocked:
        for item in page.locator(blocked).all():
            if item.is_visible() and re.search(selectors['blocked_text_pattern'],item.inner_text(),re.I):
                raise Held('browser_owner_action','The provider shows login, billing, challenge or quota controls. The worker stopped without interacting with them.')
    model=visible(page,selectors.get('model_selector'))
    pattern=selectors.get('model_name_pattern') or re.escape(job.get('model_hint','Veo'))
    if job.get('model_hint')=='Veo|Omni' and not selectors.get('model_name_pattern'):pattern='Veo|Omni'
    if not model or not re.search(pattern,model.inner_text(),re.I):
        raise Held('browser_model_setup','Selected model cannot be verified. Open the desired video/image model and calibrate its visible selector.')


def preflight(page,job,selectors,test_url=None):
    check_session(page,job,selectors,test_url)
    allowance=visible(page,selectors.get('included_allowance_selector'))
    if not allowance:raise Held('browser_allowance_unverified','Included account allowance is not visible/verified; generation was not submitted.')
    cost=visible(page,selectors.get('cost_selector'))
    if not cost:raise Held('browser_cost_unverified','Per-generation included-credit cost is not visible; generation was not submitted.')
    if not visible(page,selectors.get('prompt_selector')) or not visible(page,selectors.get('generate_selector')):
        raise Held('browser_controls','Prompt/generate controls could not be verified; no submission occurred.')
    if selectors.get('cost_mode')=='free':
        if not re.fullmatch(r'free(?: tier| of charge)?|0(?:\.00)?\s*(?:credits?|USD|INR|\$|₹)',cost.inner_text().strip(),re.I):
            raise Held('browser_cost_unverified','The dedicated free-cost element does not explicitly show free/zero use')
        if not re.search(r'free|included',allowance.inner_text(),re.I):
            raise Held('browser_allowance_unverified','Free/included access is not visible; no submission')
        return {'selected_model_verified':True,'included_allowance_visible':True,'credit_cost':0,'cost_mode':'free'}
    if selectors.get('cost_mode','included_credits')!='included_credits':raise Held('browser_cost_unverified','Unknown generation cost mode')
    # A dedicated cost element prevents parsing a credit balance as a price.
    label=cost.inner_text().strip()
    match=re.fullmatch(r'(\d+)\s*(?:included\s+)?credits?',label,re.I)
    if not match or int(match[1])>job['included_credit_limit']:
        raise Held('browser_credit_limit','Visible generation cost exceeds the allowed included-credit budget or is unclear.')
    balance=re.search(r'(\d+)\s*(?:included\s+)?credits?',allowance.inner_text(),re.I)
    if not balance or int(balance[1])<int(match[1]):raise Held('browser_allowance_unverified','Visible included credit balance is insufficient or unclear.')
    if not visible(page,selectors.get('prompt_selector')) or not visible(page,selectors.get('generate_selector')):
        raise Held('browser_controls','Prompt/generate controls could not be verified; no submission occurred.')
    return {'selected_model_verified':True,'included_allowance_visible':True,'credit_cost':int(match[1])}


def execute_page(ws,job,page,selectors,apply=False,test_url=None,timeout=240,reconcile=False):
    job=read_generation(ws,job['id'])
    folder=browser_folder(ws)/job['id'];path=folder/'job.json'
    if job.get('asset_id'):return {**job,'asset':asset_record(ws,job['asset_id'])}
    if job.get('submission_started') and not reconcile:
        raise Held('browser_submission_unresolved','This job already submitted a generation. Inspect/reconcile that result before creating anything again.')
    if reconcile:
        if not job.get('submission_started'):raise Held('browser_no_submission','There is no submitted result to reconcile')
        allowed_page(page,job,test_url);audit=job.get('preflight',{})
        if not apply:return {'dry_run':True,'id':job['id'],'reconcile':True,'message':'No generation or download submitted'}
    else:
        check_session(page,job,selectors,test_url)
        if visible(page,selectors.get('download_selector')):
            raise Held('browser_existing_result','A previous download is already visible. Open a fresh prompt before submitting this job')
        observed=apply_settings(page,job.get('settings',{}),selectors.get('settings',{}))
        audit=preflight(page,job,selectors,test_url);audit['settings']=observed
        job['settings_observed']=observed;job['preflight']=audit;write_json(path,job)
        if not apply:return {'dry_run':True,'id':job['id'],'preflight':audit,'message':'Sidebar settings verified; no prompt submitted and no generation credit used.'}
        prompt=visible(page,selectors['prompt_selector'])
        if not prompt or not visible(page,selectors['generate_selector']):raise Held('browser_controls','Prompt or generate control is unavailable')
        prompt.fill(job['prompt']);preflight(page,job,selectors,test_url)
        # Read back the settings immediately before a chargeable operation without changing them.
        apply_settings(page,job.get('settings',{}),selectors.get('settings',{}),verify_only=True)
        job.update(status='submitted',submission_started=True,submitted_at=now(),preflight=audit,result_url=page.url)
        write_json(path,job) # Persist intent before click, preventing blind duplicate submissions.
        visible(page,selectors['generate_selector']).click()
    deadline=time.monotonic()+max(5,min(timeout,900))
    while time.monotonic()<deadline:
        allowed_page(page,job,test_url)
        if job.get('result_url')!=page.url:
            job['result_url']=page.url;write_json(path,job)
        for item in page.locator(selectors.get('blocked_selector','[role="alert"]')).all():
            if item.is_visible() and re.search(selectors['blocked_text_pattern'],item.inner_text(),re.I):
                raise Held('browser_provider_stopped','Generation shows a provider limitation; the submitted job was preserved for reconciliation.')
        download=visible(page,selectors.get('download_selector'))
        if download:
            with page.expect_download(timeout=30000) as event:download.click()
            item=event.value
            if item.failure():raise Held('browser_download','Provider download failed; generation was not resubmitted.')
            suffix=Path(item.suggested_filename).suffix.lower()
            allowed={'.mp4','.webm','.mov'} if job['kind']=='video' else {'.png','.jpg','.jpeg','.webp'}
            if suffix not in allowed:raise Held('browser_download_type','Provider returned an unexpected file type.')
            output=folder/('generated'+suffix);item.save_as(str(output))
            asset=register_asset(ws,output,'original_graphic',{'generation_job':job['id'],'provider':job['provider'],
                'provider_url':job['provider_url'],'model_hint':job['model_hint'],'prompt':job['prompt'],'synthetic':True,'preflight':audit},test_only=bool(test_url))
            job.update(status='downloaded',file=str(output),file_sha256=file_hash(output),asset_id=asset['id'],completed_at=now())
            write_json(path,job);return job
        time.sleep(.5)
    raise Held('browser_generation_timeout','Generation did not produce a download in time. The submitted job was retained; no duplicate was started.')


def run_generation(ws,id,selectors,apply=False,headed=True,channel=None,browser_options=None,reconcile=False):
    job=read_generation(ws,id)
    owner=uuid.uuid4().hex;ws.worker_lock(owner,name='generation-browser');stop=threading.Event()
    def renew():
        while not stop.wait(30):ws.worker_lock(owner,name='generation-browser')
    thread=threading.Thread(target=renew,daemon=True);thread.start()
    try:
        with browser_context(ws,headed,channel,browser_options) as context:
            # Use a worker-owned tab; do not navigate unrelated personal tabs on CDP attachment.
            page=context.new_page();target=job.get('result_url',job['provider_url']) if reconcile else job['provider_url']
            page.goto(provider_url(job['provider'],target),wait_until='domcontentloaded')
            allowed_page(page,job)
            selector=selectors.get('download_selector' if reconcile else 'prompt_selector')
            if selector:
                try:page.locator(selector).first.wait_for(state='visible',timeout=30000)
                except Exception:raise Held('browser_controls','Provider controls did not become available; finish sign-in/setup or recalibrate')
            try:return execute_page(ws,job,page,selectors,apply,reconcile=reconcile,timeout=(browser_options or {}).get('generation_timeout',240))
            finally:
                if not job.get('submission_started') and not read_generation(ws,id).get('submission_started'):page.close()
    except Held as exc:
        job=read_generation(ws,id);job.update(status='held',code=exc.code,message=str(exc));write_json(browser_folder(ws)/id/'job.json',job)
        raise
    except Exception:
        job=read_generation(ws,id)
        code='browser_submission_unresolved' if job.get('submission_started') else 'browser_interaction'
        message='Browser interaction interrupted. Reconcile the existing submission.' if job.get('submission_started') else 'Browser interaction failed before submission; inspect the page and calibrated controls.'
        job.update(status='held',code=code,message=message);write_json(browser_folder(ws)/id/'job.json',job)
        raise Held(code,message)
    finally:
        stop.set();thread.join(timeout=2);ws.worker_lock(owner,release=True,name='generation-browser')


def import_generation(ws,id,file):
    job=read_generation(ws,id)
    if job.get('asset_id'):return job
    path=Path(file).resolve()
    suffix=path.suffix.lower()
    if suffix not in ({'.mp4','.webm','.mov'} if job['kind']=='video' else {'.png','.jpg','.jpeg','.webp'}):
        raise Held('generation_import_type','The downloaded file does not match this generation job type.')
    asset=register_asset(ws,path,'original_graphic',{'generation_job':id,'provider':job['provider'],'prompt':job['prompt'],
                         'synthetic':True,'imported_by_owner':True,'provider_result_verified':False})
    job.update(status='downloaded',asset_id=asset['id'],file=str(path),file_sha256=file_hash(path),completed_at=now(),submission_started=True)
    write_json(browser_folder(ws)/id/'job.json',job);return job


def setup_browser(ws,provider='ai_studio',channel=None,browser_options=None):
    if provider not in PROVIDERS:raise ValueError('Unknown provider')
    with browser_context(ws,True,channel,browser_options) as context:
        if (browser_options or {}).get('mode')=='cdp':
            return {'connected':True,'note':'Attached to the explicitly configured browser. No login or generation was performed.'}
        page=context.pages[0] if context.pages else context.new_page();page.goto(PROVIDERS[provider],wait_until='domcontentloaded')
        print(json.dumps({'status':'owner_setup','message':'Sign in yourself in this dedicated browser, select the included model, then close the browser window to save the profile.'}),flush=True)
        while context.pages:time.sleep(1)
    return {'profile_saved':True,'note':'No authentication fields were entered by the worker. Model/cost selectors still require preflight calibration.'}


def asmr_prompt(scenario='clay_loop'):
    scenes={
        'clay_loop':'A tight overhead macro shot of hands shaping one soft clay lump into a neat tiny bowl, then gently crushing it back into the exact starting lump. Keep the clay amount, hand anatomy, tools and camera consistent. End with the same lump placement and framing as the first frame for a loop.',
        'room_reveal':'A locked-off wide shot of one small empty room. Show a clear sped-up decoration process with consistent furniture placement and physically coherent actions. Reserve the final two seconds for switching on warm lights and revealing the completed room.',
        'sand_loop':'A fixed macro view of a small kinetic-sand mound being shaped into a crisp geometric form, then flattened back into the starting mound. Consistent tools, light and geometry; final framing matches the opening.'}
    if scenario not in scenes:raise ValueError('Unknown generated-video scenario')
    return scenes[scenario]+' Vertical 9:16, about 8 seconds. Close, clean synchronized material/tool ASMR audio; no music, speech, text, logos or identifiable real people. Original scene, no copied characters. The visual payoff must actually occur before the clip ends.'


def production_from_generation(ws,id,title='Original AI-generated visual',channel='entertainment',loop_count=1):
    generation=read_generation(ws,id)
    if not generation.get('asset_id'):raise Held('generated_media_pending','The browser job has not produced an imported/downloaded asset yet.',retry_after=60)
    asset=asset_record(ws,generation['asset_id'])
    if asset['kind']!='video':raise Held('generation_consumer','For images, use generation:JOB_ID in a production request media_assets slot.')
    for job in ws.jobs(10000):
        if job['request'].get('generation_job')==id:return job
    brief={'title':title,'question':'What original synthetic scene was produced?','kind':'fact','editorial_verified':True,
        'sources':[{'id':'generated','url':'asset://'+asset['id'],'title':'Locally archived generated video','excerpt':'This registered asset is an original generated visual, with no claim that it is real footage. Its provider/prompt record is archived.','checked_at':now()}],'claims':[]}
    script={'version':1,'title':title,'description':'Original AI-generated visual. Repeated sections are deliberate loops; no real-world event is claimed.',
        'format':'clip','fiction':False,'hook':title,'payoff':'The generated visual payoff appears before the loop restarts.',
        'units':[{'id':'visual','speaker':'Original audio','text':'Original generated scene with source audio.','kind':'transition','claim_ids':[],'onscreen':'AI-generated visual'}],
        'edit':{'effect':'none','payoff_unit_id':'visual','cta':False}}
    return ws.create(channel,{'format':'clip','brief':brief,'script':script,'clip_asset_id':asset['id'],'clip_start':0,'clip_end':min(asset['duration'],179/loop_count),
                              'loop_count':loop_count,'generation_job':id,'test_only':asset.get('test_only',False)})
