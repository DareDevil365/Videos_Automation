"""Independent, explicitly declared Google projects with separate quota state."""
import math
import os
from pathlib import Path
import re

from .core import Held


def profiles(workspace):
    settings=workspace.config()['gemini'];items=settings.get('projects',[])
    if not isinstance(items,list) or len(items)>30:raise Held('gemini_projects','Use at most 30 explicit project profiles.')
    result=[];seen=set();seen_env=set();seen_keys=set()
    for item in items:
        if (not isinstance(item,dict) or set(item)-{'id','key_env','free_tier_confirmed','requests_per_day'} or
                not isinstance(item.get('id'),str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,60}',item['id']) or item['id'] in seen or
                not isinstance(item.get('key_env'),str) or not re.fullmatch(r'[A-Z][A-Z0-9_]{0,79}',item['key_env']) or
                item.get('free_tier_confirmed') is not True or
                type(item.get('requests_per_day',30)) is not int or not 1<=item.get('requests_per_day',30)<=100):
            raise Held('gemini_projects','Each profile needs a unique project ID, environment key name, confirmed free-tier status and bounded local daily allowance.')
        secret=os.environ.get(item['key_env'])
        if item['key_env'] in seen_env or (secret and secret in seen_keys):raise Held('gemini_projects','A credential may belong to only one declared project profile.')
        seen.add(item['id']);seen_env.add(item['key_env'])
        if secret:seen_keys.add(secret)
        result.append(item)
    return result


def project_status(workspace):
    return [{'project_id':p['id'],'key_present':bool(os.environ.get(p['key_env'])),
             **workspace.quota_status('gemini:'+p['id'],p.get('requests_per_day',30) if workspace.gemini_budget_cap() is not None else None)} for p in profiles(workspace)]


class GeminiProjects:
    name='gemini'

    def __init__(self,workspace,transport=None):self.workspace,self.transport=workspace,transport

    def generate(self,purpose,content,schema,*,images=()):
        from .writer import Gemini
        ws=self.workspace;settings=ws.config()['gemini'];available=[];delays=[]
        for order,p in enumerate(profiles(ws)):
            state=ws.quota_status('gemini:'+p['id'],p.get('requests_per_day',30) if ws.gemini_budget_cap() is not None else None)
            if not os.environ.get(p['key_env']):continue
            if state['cooldown_seconds']:delays.append(state['cooldown_seconds']);continue
            if state['local_remaining']==0:
                from datetime import datetime,timezone,timedelta
                now=datetime.now(timezone.utc);reset=(now+timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
                delays.append(math.ceil((reset-now).total_seconds()));continue
            available.append((state['local_calls_today'],order,p))
        if not available and delays:
            for p in profiles(ws):
                if os.environ.get(p['key_env']):
                    try:return Gemini(ws,self.transport,settings={**settings,**p},quota_scope='gemini:'+p['id']).generate(purpose,content,schema,images=images)
                    except Held as exc:
                        if exc.code not in ('gemini_quota','provider_cooldown','project_budget'):raise
                    break
        if not available:
            raise Held('gemini_quota' if delays else 'gemini_key_missing',
                       'No configured Gemini project is currently available; project cooldowns and balances are retained.',retry_after=min(delays) if delays else None)
        # Fair distribution across available independent projects. A single
        # invocation makes at most three attempts; it never exhaustively probes keys.
        last=None
        for _,_,p in sorted(available)[:3]:
            scope='gemini:'+p['id']
            provider=Gemini(ws,self.transport,settings={**settings,**p},quota_scope=scope)
            try:return provider.generate(purpose,content,schema,images=images)
            except Held as exc:
                if exc.code not in ('gemini_quota','provider_cooldown','gemini_access','project_budget'):raise
                last=exc
                if exc.code=='gemini_access':ws.cool_provider(scope,3600)
                if exc.retry_after:delays.append(exc.retry_after)
        raise Held(last.code if last else 'gemini_quota',
                   'The attempted Gemini projects are unavailable. Other project state is preserved; the queued job can resume.',
                   retry_after=min(delays) if delays else 60)


def import_project_keys(workspace,key_file,env_file,*,distinct_projects=False,free_tier_confirmed=False):
    """Import only explicit key tokens locally. Return counts/labels, never keys."""
    if distinct_projects is not True or free_tier_confirmed is not True:
        raise Held('gemini_projects','Import requires explicit confirmation that these keys represent separate free-tier projects.')
    source=Path(key_file).resolve();target=Path(env_file).resolve()
    if target.name=='.env.example' or (target.name!='.env' and not target.name.startswith('.env.')):raise Held('gemini_projects','Use a private .env or .env.* file, never an example, prompt or document.')
    if source==target:raise Held('gemini_projects','Choose a separate private environment output file; the source key file is never overwritten.')
    text=source.read_text(encoding='utf-8-sig')
    keys=list(dict.fromkeys(re.findall(r'(?:AIza[\w-]{20,}|AQ\.[A-Za-z0-9_-]{20,})',text)))
    if not 1<=len(keys)<=30:raise Held('gemini_projects','The file needs 1-30 distinct recognized Google API keys.')
    existing=target.read_text(encoding='utf-8') if target.exists() else ''
    # Deterministic slots make repeated imports idempotent. Caller must keep this
    # environment file private/ignored; no credential value goes into config.
    entries={f'GEMINI_API_KEY_PROJECT_{i:02d}':key for i,key in enumerate(keys,1)}
    lines=[line for line in existing.splitlines() if line.partition('=')[0].strip() not in entries]
    target.parent.mkdir(parents=True,exist_ok=True)
    temporary=target.with_name(target.name+'.partial')
    temporary.write_text('\n'.join(lines)+('\n' if lines else '')+'\n'.join(k+'='+v for k,v in entries.items())+'\n',encoding='utf-8')
    temporary.replace(target)
    cfg=workspace.config()
    cfg['gemini']['projects']=[{'id':f'project_{i:02d}','key_env':f'GEMINI_API_KEY_PROJECT_{i:02d}',
                              'free_tier_confirmed':True,'requests_per_day':30} for i in range(len(keys),0,-1)]
    workspace.save_config(cfg)
    return {'projects_imported':len(keys),'environment_file':str(target),'quota_scope':'per declared project',
            'limits':'Project identity is owner-declared; keys for the same Google project must share one profile.'}
