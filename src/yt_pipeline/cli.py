import argparse
import importlib.util
import json
import os
import re
from pathlib import Path
import shutil
import sys
import time

from .core import Workspace, Held, STAGES, load_env_file, redact
from .pipeline import Pipeline
from .gemini_projects import project_status
from .assets import register_asset, pexels_video
from .voice import install_default_voice as setup_voice,install_kokoro_voice
from .research import discover
from .publishing import authorize, approve, publish, reconcile
from .monitor import supervise, observe, growth_report, alerts, incident, WINDOWS
from .benchmarks import benchmark
from .source_agent import register_source,ingest_source
from .clip_agent import create_clip_jobs,research_handoff
from .media_agent import commons_search,acquire_visual
from .music_agent import discover_music,choose_music,register_music,CATEGORIES
from .browser_agent import create_generation,run_generation,import_generation,setup_browser,selector_template,asmr_prompt,production_from_generation,PROVIDERS,browser_folder,read_generation
from .generation_settings import plan_settings


def doctor(ws):
    config=ws.config()
    engine=config['voice'].get('engine','piper')
    voice={**config['voice'],**config['voice'].get('kokoro',{})} if engine=='kokoro' else config['voice']
    return {"text_provider":config.get("text_provider","gemini"),
            "gemini_projects":project_status(ws),
            "selected_key_present":bool(os.environ.get(config.get(config.get("text_provider","gemini"),{}).get("key_env","OPENAI_API_KEY" if config.get("text_provider")=="openai" else "GEMINI_API_KEY"))),
            "root":str(ws.root),"ffmpeg":bool(shutil.which("ffmpeg")),"ffprobe":bool(shutil.which("ffprobe")),
            "piper_runtime":importlib.util.find_spec("piper") is not None,
            "voice_engine":engine,"voice_runtime":importlib.util.find_spec('kokoro_onnx' if engine=='kokoro' else 'piper') is not None,
            "voice_model":ws.resolve(voice["model"]).is_file(),
            "gemini_key_present":bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")),
            "gemini_free_tier_confirmed":config["gemini"].get("free_tier_confirmed",False),
            "gemini_quota":ws.quota_status('gemini',ws.gemini_budget_cap()),
            "youtube_search_key_present":bool(os.environ.get("YOUTUBE_API_KEY")),
            "pexels_key_present":bool(os.environ.get("PEXELS_API_KEY")),
            "channels":{name:{"paused":p["paused"],"format":p["format"],"footage_count":len(p["footage_ids"]),
                         "publication_mode":p["publication_mode"],"oauth_file_present":(ws.root/"credentials"/(name+".json")).exists(),
                         "channel_identity_configured":bool(p["youtube_channel_id"])} for name,p in config["channels"].items()}}


def config_set(ws, path, value):
    # Strict allowlist: credentials are environment/local OAuth files, never config values.
    allowed={"text_provider","gemini.key_env","gemini.model","gemini.thinking_level","openai.key_env","openai.model","openai.api_usage_enabled","openai.requests_per_day","openai.max_output_tokens","gemini.free_tier_confirmed","gemini.requests_per_day","gemini.enforce_local_budget","voice.length_scale","voice.engine","voice.normalize_loudness"}
    for channel in ws.config()["channels"]:
        allowed.update("channels."+channel+"."+key for key in ("paused","daily_cap","publication_mode","auto_private_upload","feed_urls","source_urls","research_queries","footage_ids","music_id","style","media_mode","source_ids"))
    if path not in allowed:raise ValueError("This config field cannot be changed through this command.")
    config=ws.config()
    from .core import default_config
    defaults=default_config()
    config.setdefault("text_provider",defaults["text_provider"])
    config.setdefault("openai",defaults["openai"])
    config["gemini"].setdefault("key_env","GEMINI_API_KEY")
    config["gemini"].setdefault("thinking_level","low")
    parts=path.split(".");target=config
    for part in parts[:-1]:target=target[part]
    key=parts[-1]
    old=target.get(key,[]) if key in ('research_queries','source_ids') else target.get(key,'piper') if key=='engine' else target.get(key,True) if key in ('normalize_loudness','enforce_local_budget') else target.get(key,'stock') if key=='media_mode' else target[key]
    if type(old)!=type(value) and not (isinstance(old,float) and type(value) in (int,float)):raise ValueError("Config value has the wrong type.")
    if path=='text_provider' and value not in ('gemini','openai'):raise ValueError('Choose gemini or openai.')
    if key=='key_env' and not re.fullmatch(r'[A-Z][A-Z0-9_]{0,79}',value):raise ValueError('Use an environment variable name, never an API key.')
    if path=='gemini.model':
        from .writer import FREE_MODELS
        if value not in FREE_MODELS:raise ValueError('Choose a configured free Gemini text model.')
    if path=='gemini.thinking_level' and value not in ('low','medium','high'):raise ValueError('Choose low, medium or high.')
    if path=='openai.model' and not re.fullmatch(r'[A-Za-z0-9._-]{1,100}',value):raise ValueError('Set an explicit API model name.')
    if key=='max_output_tokens' and not 256<=value<=16384:raise ValueError('Use 256-16384 output tokens.')
    if key=="publication_mode" and value not in ("disabled","private","public","scheduled"):raise ValueError("Use disabled, private, public or scheduled.")
    if key=='engine' and value not in ('piper','kokoro'):raise ValueError('Choose piper or kokoro')
    if key=='media_mode' and value not in ('stock','graphic'):raise ValueError('Choose stock or graphic')
    if key in ("daily_cap","requests_per_day") and not 1<=value<=100:raise ValueError("Use a daily cap from 1 to 100.")
    if key=="length_scale" and not .6<=value<=1.8:raise ValueError("Use a voice length scale from 0.6 to 1.8.")
    if isinstance(value,list) and (len(value)>50 or not all(isinstance(v,str) for v in value)):raise ValueError("Use at most 50 text entries.")
    target[key]=value;ws.save_config(config)
    return {"updated":path,"value":value}


def plan(ws, channel, query=""):
    candidates=discover(ws,channel,query)
    comparison=None
    if query and os.environ.get('YOUTUBE_API_KEY'):
        comparison=benchmark(ws,channel,query,candidates['candidates'])
        scores={r['url']:r['views_per_hour_since_publish'] for r in comparison['videos']}
        candidates['candidates'].sort(key=lambda r:scores.get(r['url'],0),reverse=True)
    previous={j["request"].get("candidate_url") for j in ws.jobs(10000)}
    jobs=[];profile=ws.config()["channels"][channel]
    if profile["paused"]:raise Held("channel_paused","Channel is paused.")
    today=time.strftime("%Y-%m-%d",time.gmtime())
    count=sum(j["channel"]==channel and j["created_at"].startswith(today) for j in ws.jobs(10000))
    for item in candidates["candidates"]:
        if len(jobs)+count>=profile["daily_cap"]:break
        if item["url"] in previous:continue
        request={"topic":item["title"],"candidate_url":item["url"],"candidate":item}
        if profile["format"]=="lesson":
            if item["kind"]!="feed":continue # Video metadata is not an article transcript.
            request["source_urls"]=[item["url"]];request["fiction"]=False
        else:request["fiction"]=True # Reference is a premise; never a fake true story or copied script.
        jobs.append(ws.create(channel,request)["id"])
    return {"created_jobs":jobs,"candidates":candidates,"public_comparison":comparison,"note":"Discovery can be empty. Counts generate hypotheses, not rights or causal performance claims."}


def tick(ws, remote=False):
    result=Pipeline(ws).work_once()
    uploads=[]
    for job in ws.jobs():
        profile=ws.config()["channels"][job["channel"]]
        if job['request'].get('auto_publish') and job['status'] in ('ready','processing'):
            from .production import finish_production
            uploads.append(finish_production(ws,job['id']))
            continue
        if profile.get("auto_private_upload") and profile["publication_mode"]=="private" and not profile["paused"] and job["status"]=="ready":
            try:
                approve(ws,job["id"]);uploads.append(publish(ws,job["id"],apply=True))
            except Held as exc:ws.alert(job["id"]+":"+exc.code,job["id"],str(exc))
    observations=[]
    if remote:
        for job in ws.jobs():
            if job["status"]!="published":continue
            for window in WINDOWS:
                with ws.connect() as db:existing=db.execute("SELECT data FROM observations WHERE job_id=? AND window=?",(job["id"],window)).fetchone()
                if existing:
                    saved=json.loads(existing[0])
                    if saved.get('available') and not saved.get('data_may_be_delayed',True):continue
                    from datetime import datetime,timezone
                    if (datetime.now(timezone.utc)-datetime.fromisoformat(saved['checked_at'])).total_seconds()<12*3600:continue
                try:observations.append(observe(ws,job["id"],window))
                except Held as exc:
                    if exc.code not in ("observation_early","not_public"):ws.alert(job["id"]+":"+exc.code,job["id"],str(exc))
    return {"job":result,"uploads":uploads,"observations":observations}


def main():
    parser=argparse.ArgumentParser(description="Local, resumable two-channel video pipeline. All command results are JSON.")
    parser.add_argument("--root",default="data/pipeline");parser.add_argument("--env-file")
    sub=parser.add_subparsers(dest="command",required=True)
    for name in ("init","doctor","status"):sub.add_parser(name)
    p=sub.add_parser('voice-setup');p.add_argument('--engine',choices=['piper','kokoro'],default='piper');p.add_argument('--voice',default='am_adam')
    config=sub.add_parser("config");config.add_argument("path");config.add_argument("value",help="JSON value, e.g. true, 4, or a quoted string")
    create=sub.add_parser("create");create.add_argument("channel",choices=["education","entertainment"]);create.add_argument("--request");create.add_argument("--topic")
    p=sub.add_parser('produce');p.add_argument('--topic');p.add_argument('--genre',choices=['comedy','mystery','thriller','story'],default='comedy')
    p.add_argument('--format',choices=['chat','phone'],default='chat');p.add_argument('--visibility',choices=['public','private','none'],default='public')
    p.add_argument('--request');p.add_argument('--resume')
    p=sub.add_parser('finish-production');p.add_argument('job')
    p=sub.add_parser('music-library');p.add_argument('--install',action='store_true');p.add_argument('--key',action='append')
    p=sub.add_parser('music-pick');p.add_argument('genre',choices=['comedy','mystery','thriller','story','cinematic','aura'])
    p.add_argument('--selection-key',default='');p.add_argument('--avoid-recent',type=int,default=3);p.add_argument('--download-missing',action='store_true')
    for name in ("run","cancel","approve","reconcile"):
        p=sub.add_parser(name);p.add_argument("job")
    p=sub.add_parser('feedback');p.add_argument('job');p.add_argument('--verdict',choices=['accepted','rejected','needs_revision'],required=True);p.add_argument('--reason',required=True)
    p=sub.add_parser("retry");p.add_argument("job");p.add_argument("--from-stage",choices=STAGES,default=None)
    p=sub.add_parser("publish");p.add_argument("job");p.add_argument("--apply",action="store_true")
    p=sub.add_parser("worker");p.add_argument("--once",action="store_true");p.add_argument("--interval",type=float,default=60);p.add_argument("--remote-monitor",action="store_true");p.add_argument("--plan-feeds",action="store_true");p.add_argument('--clip-sources',action='store_true')
    p=sub.add_parser("asset");p.add_argument("file");p.add_argument("--source-type",choices=["owner_recording","licensed_stock","licensed_creator","original_graphic","test"],required=True);p.add_argument("--evidence",required=True);p.add_argument("--channel",choices=["education","entertainment"]);p.add_argument("--test-only",action="store_true");p.add_argument("--expires-at")
    p=sub.add_parser("stock");p.add_argument("query")
    p=sub.add_parser('media-search');p.add_argument('query');p.add_argument('--kind',choices=['image','video','audio'],default='image')
    p=sub.add_parser('media-get');p.add_argument('query');p.add_argument('--kind',choices=['image','video'],default='image')
    sub.add_parser('library-index')
    p=sub.add_parser('library-search');p.add_argument('query');p.add_argument('--kind',choices=['image','video','audio']);p.add_argument('--limit',type=int,default=8)
    p=sub.add_parser('source-register');p.add_argument('file')
    p=sub.add_parser('source-ingest');p.add_argument('source');p.add_argument('--limit',type=int,default=3)
    p=sub.add_parser('clip-agent');p.add_argument('source');p.add_argument('--channel',choices=['education','entertainment'],default='entertainment');p.add_argument('--hint',default='');p.add_argument('--maximum',type=int,default=2)
    p=sub.add_parser('source-handoff');p.add_argument('evidence_file');p.add_argument('sources',nargs='+')
    p=sub.add_parser('music-search');p.add_argument('category',choices=CATEGORIES);p.add_argument('--query');p.add_argument('--trends',action='store_true')
    p=sub.add_parser('music-get');p.add_argument('category',choices=CATEGORIES);p.add_argument('--query')
    p=sub.add_parser('music-register');p.add_argument('asset');p.add_argument('categories',nargs='+',choices=CATEGORIES)
    p=sub.add_parser('generation-create');p.add_argument('--provider',choices=PROVIDERS,default='ai_studio');p.add_argument('--prompt');p.add_argument('--scenario',choices=['clay_loop','room_reveal','sand_loop']);p.add_argument('--kind',choices=['image','video'],default='video');p.add_argument('--credit-limit',type=int,default=0);p.add_argument('--model');p.add_argument('--url');p.add_argument('--settings');p.add_argument('--requirements');p.add_argument('--capabilities')
    p=sub.add_parser('generation-plan');p.add_argument('--kind',choices=['image','video'],required=True);p.add_argument('--requirements',required=True);p.add_argument('--capabilities',required=True)
    p=sub.add_parser('generation-run');p.add_argument('job');p.add_argument('--selectors',required=True);p.add_argument('--apply',action='store_true');p.add_argument('--headless',action='store_true');p.add_argument('--browser','--channel',dest='browser',default='brave');p.add_argument('--browser-config');p.add_argument('--reconcile',action='store_true')
    p=sub.add_parser('generation-import');p.add_argument('job');p.add_argument('file')
    p=sub.add_parser('generation-use');p.add_argument('job');p.add_argument('--title',default='Original AI-generated visual');p.add_argument('--channel',choices=['education','entertainment'],default='entertainment');p.add_argument('--loop-count',type=int,default=1);p.add_argument('--run',action='store_true')
    p=sub.add_parser('generation-worker');p.add_argument('--selectors',required=True);p.add_argument('--apply',action='store_true');p.add_argument('--produce',action='store_true');p.add_argument('--once',action='store_true');p.add_argument('--browser','--channel',dest='browser',default='brave');p.add_argument('--browser-config');p.add_argument('--interval',type=float,default=60)
    p=sub.add_parser('generation-setup');p.add_argument('--provider',choices=PROVIDERS,default='ai_studio');p.add_argument('--browser','--channel',dest='browser',default='brave');p.add_argument('--browser-config')
    sub.add_parser('generation-selectors')
    p=sub.add_parser('batch-run');p.add_argument('--plan');p.add_argument('--stop-file')
    p=sub.add_parser('batch-status');p.add_argument('--plan')
    p=sub.add_parser('playbooks');p.add_argument('--export')
    p=sub.add_parser('gemini-projects-import');p.add_argument('--file',required=True);p.add_argument('--env-output',default='.env');p.add_argument('--distinct-projects',action='store_true');p.add_argument('--free-tier-confirmed',action='store_true')
    p=sub.add_parser('phone-plan');p.add_argument('--topic');p.add_argument('--tone',choices=['comedy','mystery','thriller','story'],default='thriller');p.add_argument('--output',required=True)
    p=sub.add_parser('chat-plan');p.add_argument('--topic');p.add_argument('--output',required=True)
    for name in ("discover","plan","report","benchmark"):
        p=sub.add_parser(name);p.add_argument("channel",choices=["education","entertainment"])
        if name!="report":p.add_argument("--query",default="")
    p=sub.add_parser("authorize");p.add_argument("channel",choices=["education","entertainment"]);p.add_argument("client_file")
    p=sub.add_parser("supervise");p.add_argument("--remote",action="store_true")
    p=sub.add_parser("observe");p.add_argument("job");p.add_argument("--window",choices=WINDOWS,default="24h")
    p=sub.add_parser("alerts");p.add_argument("--acknowledge")
    p=sub.add_parser("incident");p.add_argument("channel",choices=["education","entertainment"]);p.add_argument("message");p.add_argument("--source-id")
    args=parser.parse_args()
    try:
        load_env_file(args.env_file);ws=Workspace(args.root);cmd=args.command
        if cmd in ("init","doctor"):result=doctor(ws)
        elif cmd=="status":result={"jobs":ws.jobs(),"alerts":alerts(ws),"doctor":doctor(ws)}
        elif cmd=="config":result=config_set(ws,args.path,json.loads(args.value))
        elif cmd=="create":
            request=json.loads(Path(args.request).read_text(encoding="utf-8")) if args.request else {"topic":args.topic or ""}
            if request.get('playbook')=='server_chat':request.setdefault('chat_editing_version',2)
            if request.get('playbook') in ('cutout_ensemble','horror_stock'):request.setdefault('scene_direction_version',2)
            if args.request:
                for key in ("brief_file","script_file"):
                    if request.get(key):request[key]=str((Path(args.request).resolve().parent/request[key]).resolve())
            result=ws.create(args.channel,request)
        elif cmd=='produce':
            from .production import create_production,run_production
            from .core import digest
            if args.resume:job=ws.get(args.resume)
            else:
                spec=json.loads(Path(args.request).read_text(encoding='utf-8')) if args.request else {}
                if not isinstance(spec,dict):raise ValueError('Production request must be an object.')
                job=create_production(ws,spec.get('topic',args.topic),spec.get('genre',args.genre),spec.get('format',args.format),
                    spec.get('visibility',args.visibility),spec.get('request'),
                    token=digest([str(Path(args.request).resolve()),spec]) if args.request else None)
            print(json.dumps({'event':'production_started','job_id':job['id'],'resume_command':'produce --resume '+job['id']}),flush=True)
            result=run_production(ws,job['id'])
        elif cmd=='finish-production':
            from .production import finish_production
            result=finish_production(ws,args.job)
        elif cmd=='music-library':
            from .curated_music import music_catalog,install_music_catalog
            result=install_music_catalog(ws,args.key) if args.install else music_catalog()
        elif cmd=='music-pick':
            from .curated_music import select_genre_music
            result=select_genre_music(ws,args.genre,args.selection_key,args.avoid_recent,args.download_missing)
        elif cmd=="run":result=Pipeline(ws).run(args.job)
        elif cmd=='feedback':
            from .editorial import record_creative_feedback
            result=record_creative_feedback(ws,args.job,args.verdict,args.reason)
        elif cmd=="retry":
            job=ws.get(args.job);ws.reset(args.job,args.from_stage or (job["stage"] if job["stage"] in STAGES else "research"));result=ws.get(args.job)
        elif cmd=="cancel":ws.update(args.job,status="cancelled",message="Cancelled by owner");result=ws.get(args.job)
        elif cmd=="voice-setup":result=install_kokoro_voice(ws,args.voice) if args.engine=='kokoro' else setup_voice(ws)
        elif cmd=="asset":
            result=register_asset(ws,Path(args.file).resolve(),args.source_type,{"reference":args.evidence},expires_at=args.expires_at,test_only=args.test_only)
            if args.channel:
                config=ws.config();config["channels"][args.channel]["footage_ids"].append(result["id"]);ws.save_config(config)
        elif cmd=="stock":result=pexels_video(ws,args.query)
        elif cmd=='media-search':result=commons_search(ws,args.query,args.kind)
        elif cmd=='media-get':result=acquire_visual(ws,args.query,args.kind)
        elif cmd=='library-index':
            from .media_library import index_library
            result=index_library(ws)
        elif cmd=='library-search':
            from .media_library import search_library
            result=search_library(ws,args.query,args.kind,args.limit)
        elif cmd=='source-register':result=register_source(ws,json.loads(Path(args.file).read_text(encoding='utf-8')))
        elif cmd=='source-ingest':result=ingest_source(ws,args.source,args.limit)
        elif cmd=='clip-agent':result=create_clip_jobs(ws,args.source,args.channel,args.hint,args.maximum)
        elif cmd=='source-handoff':result=research_handoff(ws,json.loads(Path(args.evidence_file).read_text(encoding='utf-8')),args.sources)
        elif cmd=='music-search':result=discover_music(ws,args.category,args.query,args.trends)
        elif cmd=='music-get':result=choose_music(ws,args.category,True,args.query)
        elif cmd=='music-register':result=register_music(ws,args.asset,args.categories)
        elif cmd=='generation-create':
            if args.requirements and not args.capabilities:raise ValueError('Shot planning needs a calibrated --capabilities file')
            load=lambda path:json.loads(Path(path).read_text(encoding='utf-8')) if path else None
            result=create_generation(ws,asmr_prompt(args.scenario) if args.scenario else args.prompt,args.provider,args.kind,args.model,credit_limit=args.credit_limit,url=args.url,settings=load(args.settings),requirements=load(args.requirements),capabilities=load(args.capabilities))
        elif cmd=='generation-plan':result=plan_settings(args.kind,json.loads(Path(args.requirements).read_text(encoding='utf-8')),json.loads(Path(args.capabilities).read_text(encoding='utf-8')))
        elif cmd=='generation-run':result=run_generation(ws,args.job,json.loads(Path(args.selectors).read_text(encoding='utf-8')),args.apply,not args.headless,args.browser,json.loads(Path(args.browser_config).read_text(encoding='utf-8')) if args.browser_config else None,args.reconcile)
        elif cmd=='generation-import':result=import_generation(ws,args.job,args.file)
        elif cmd=='generation-use':
            result=production_from_generation(ws,args.job,args.title,args.channel,args.loop_count)
            if args.run:result=Pipeline(ws).run(result['id'])
        elif cmd=='generation-worker':
            selectors=json.loads(Path(args.selectors).read_text(encoding='utf-8'))
            browser_options=json.loads(Path(args.browser_config).read_text(encoding='utf-8')) if args.browser_config else None
            while True:
                result=[]
                for file in sorted(browser_folder(ws).glob('*/job.json')):
                    generation=json.loads(file.read_text(encoding='utf-8'))
                    if generation['status']=='queued':
                        try:generation=run_generation(ws,generation['id'],selectors,args.apply,True,args.browser,browser_options);result.append(generation)
                        except Held as exc:ws.alert(generation['id']+':'+exc.code,None,str(exc));continue
                    if args.produce and generation.get('asset_id'):
                        production=production_from_generation(ws,generation['id'])
                        if production['status']=='queued':result.append(Pipeline(ws).run(production['id']))
                print(json.dumps({'status':'ok','result':result}),flush=True)
                if args.once:return
                time.sleep(max(5,args.interval))
        elif cmd=='generation-setup':result=setup_browser(ws,args.provider,args.browser,json.loads(Path(args.browser_config).read_text(encoding='utf-8')) if args.browser_config else None)
        elif cmd=='generation-selectors':result=selector_template()
        elif cmd=='gemini-projects-import':
            from .gemini_projects import import_project_keys
            result=import_project_keys(ws,args.file,args.env_output,distinct_projects=args.distinct_projects,free_tier_confirmed=args.free_tier_confirmed)
        elif cmd in ('chat-plan','phone-plan'):
            from .batches import default_chat_plan,default_phone_plan
            from shorts_editor.store import write_json
            target=Path(args.output).resolve()
            if target.exists():raise Held('chat_plan_exists','Choose a new plan filename; initialized plans are not overwritten.')
            value=default_phone_plan(topic=args.topic,tone=args.tone) if cmd=='phone-plan' else default_chat_plan(topic=args.topic)
            target.parent.mkdir(parents=True,exist_ok=True);write_json(target,value)
            result={'plan':str(target),'id':value['id'],'editing':'compiled chat v2','next':'Run batch-run --plan with this file, or select it in the native panel.'}
        elif cmd=='playbooks':
            from .playbooks import PLAYBOOKS,export_playbooks
            result=export_playbooks(args.export) if args.export else PLAYBOOKS
        elif cmd=='batch-run':
            from .batches import run_batch
            result=run_batch(ws,args.plan,stop_file=args.stop_file,progress=lambda event:print(json.dumps({'event':'batch_progress','result':event},ensure_ascii=False),flush=True))
        elif cmd=='batch-status':
            from .batches import batch_status
            result=batch_status(ws,args.plan)
        elif cmd=="discover":result=discover(ws,args.channel,args.query)
        elif cmd=="plan":result=plan(ws,args.channel,args.query)
        elif cmd=="report":result=growth_report(ws,args.channel)
        elif cmd=="benchmark":result=benchmark(ws,args.channel,args.query)
        elif cmd=="authorize":result=authorize(ws,args.channel,args.client_file)
        elif cmd=="approve":result=approve(ws,args.job)
        elif cmd=="publish":result=publish(ws,args.job,args.apply)
        elif cmd=="reconcile":result=reconcile(ws,args.job)
        elif cmd=="supervise":result=supervise(ws,args.remote)
        elif cmd=="observe":result=observe(ws,args.job,args.window)
        elif cmd=="alerts":result=alerts(ws,args.acknowledge)
        elif cmd=="incident":result=incident(ws,args.channel,args.message,args.source_id)
        elif cmd=="worker":
            last=0
            while True:
                if time.monotonic()-last>=3600 or last==0:
                    if args.clip_sources:
                        for channel,profile in ws.config()['channels'].items():
                            if profile['paused']:continue
                            for source_id in profile.get('source_ids',[])[:3]:
                                try:create_clip_jobs(ws,source_id,channel,maximum=2)
                                except Held as exc:ws.alert(source_id+':'+exc.code,None,str(exc))
                    if args.plan_feeds:
                        for channel in ws.config()["channels"]:
                            try:
                                queries=ws.config()['channels'][channel].get('research_queries') or ['']
                                for query in queries[:3]:
                                    plan(ws,channel,query)
                            except Held as exc:ws.alert(channel+":"+exc.code,None,str(exc))
                    supervise(ws,args.remote_monitor);last=time.monotonic()
                result=tick(ws,args.remote_monitor)
                print(json.dumps({"status":"ok","result":result},ensure_ascii=False),flush=True)
                if args.once:return
                time.sleep(max(5,args.interval))
        print(json.dumps({"status":"ok","result":result},ensure_ascii=False))
        if isinstance(result,dict) and result.get("status") in ("held","failed","retry_wait"):raise SystemExit(2)
    except Held as exc:
        print(json.dumps({"status":"held","error":{"code":exc.code,"message":redact(exc),"retry_after":exc.retry_after}}));raise SystemExit(2)
    except KeyboardInterrupt:return
    except Exception as exc:
        print(json.dumps({"status":"failed","error":{"type":type(exc).__name__,"message":redact(exc)}}));raise SystemExit(1)


if __name__=="__main__":main()
