"""Transcript-grounded clip selection and researcher-to-downloader handoffs."""
import json
from pathlib import Path
import re

from shorts_editor.store import write_json
from .assets import asset_record
from .core import Held,now,digest
from .source_agent import ingest_source,source_path
from .transcripts import clip_cues
from .writer import Gemini


def normalize(text):return re.sub(r'\W+',' ',text.lower()).strip()


def select_moments(transcript,provider,hint='',maximum=3):
    cues=transcript['cues']
    schema={'type':'object','properties':{'moments':{'type':'array','items':{'type':'object','properties':{
        'start_cue':{'type':'integer'},'end_cue':{'type':'integer'},'title':{'type':'string'},'reason':{'type':'string'}},
        'required':['start_cue','end_cue','title','reason'],'additionalProperties':False}}},'required':['moments'],'additionalProperties':False}
    candidates=[]
    # Bound the actual transcript context; keep each returned range inside its source chunk.
    for chunk_start in range(0,min(len(cues),1000),180):
        chunk=cues[chunk_start:chunk_start+180];context=[];chars=0
        for offset,cue in enumerate(chunk):
            if chars+len(cue['text'])>16000:break
            context.append({'cue':chunk_start+offset,**{k:cue[k] for k in ('start','end','text')}});chars+=len(cue['text'])
        if not context:continue
        result=provider.generate('clip-moments-v1',{'transcript':context,'reference_hint':hint[:1000],
            'task':f'Select at most {maximum} self-contained 5–60 second moments with a hook, necessary context and complete payoff. Return only actual cue indices from this chunk, no invented timestamps or speech. Reference hints are leads, not authoritative source content. Do not call something famous or trending without supplied evidence.'},schema)
        for row in result.get('moments',[]):
            start,end=row.get('start_cue'),row.get('end_cue')
            if type(start)!=int or type(end)!=int or not context[0]['cue']<=start<=end<=context[-1]['cue']:
                raise Held('clip_range_invented','Clip selection referred to cue indices outside the actual source transcript.')
            duration=cues[end]['end']-cues[start]['start']
            if not 5<=duration<=60:continue
            text=' '.join(c['text'] for c in cues[start:end+1])
            candidates.append({'start':cues[start]['start'],'end':cues[end]['end'],'title':str(row['title'])[:100],
                               'reason':str(row['reason'])[:700],'text':text,'start_cue':start,'end_cue':end})
        if len(candidates)>=maximum:break
    if not candidates:raise Held('clip_not_found','No complete eligible moment was found in the supplied transcript.')
    unique=[]
    for row in candidates:
        if any(abs(row['start']-old['start'])<2 for old in unique):continue
        unique.append(row)
    return unique[:maximum]


def create_clip_jobs(ws,source_id,channel='entertainment',hint='',maximum=2,provider=None,ingested=None):
    if channel not in ws.config()['channels']:raise ValueError('Unknown channel')
    profile=ws.config()['channels'][channel]
    if profile.get('paused'):raise Held('channel_paused','The channel is paused.')
    maximum=max(1,min(3,int(maximum)))
    count=sum(j['channel']==channel and j['created_at'].startswith(now()[:10]) and not j['request'].get('test_only') and j['status']!='cancelled' for j in ws.jobs(10000))
    available=max(0,int(profile.get('daily_cap',4))-count)
    if not available:raise Held('production_daily_cap','The channel daily planning cap is reached.',retry_after=3600)
    provider=provider or Gemini(ws);ingested=ingested or ingest_source(ws,source_id)
    jobs=[]
    for episode in ingested['episodes']:
        asset=asset_record(ws,episode['asset_id']);transcript=json.loads(Path(episode['transcript_file']).read_text(encoding='utf-8'))
        for moment in select_moments(transcript,provider,hint,maximum):
            if len(jobs)>=available:break
            if moment['end']>asset['duration']+.1:raise Held('transcript_range','Transcript exceeds the actual source video duration.')
            version=digest([asset['sha256'],moment['start'],moment['end']])
            if any(job['request'].get('source_clip_version')==version for job in ws.jobs(10000)):continue
            source_url=episode.get('source_url') or 'asset://'+asset['id']
            brief={'title':moment['title'],'question':'What is the complete source moment and its context?','kind':'fact',
                'sources':[{'id':'recording','url':source_url,'title':episode['title'],'excerpt':moment['text'][:18000],'checked_at':now()}],
                'claims':[{'id':'quote','source_id':'recording','text':'The source speaker says: '+moment['text'][:650]}],
                'notes':'Transcript is a source record, not independent verification of every claim made by a speaker. Preserve context.','editorial_verified':False}
            script={'version':1,'title':moment['title'],'description':f"Source moment from {episode['title']}. Captions: {transcript['origin']}.\n{moment['reason']}",
                'format':'clip','fiction':False,'hook':moment['title'],'payoff':'Complete original source moment, with necessary context.',
                'units':[{'id':'clip','speaker':'Original speaker','text':moment['text'][:340],'kind':'fact','claim_ids':['quote'],'onscreen':'Original source clip'}],
                'edit':{'effect':'none','payoff_unit_id':'clip','cta':False}}
            request={'format':'clip','brief':brief,'script':script,'clip_asset_id':asset['id'],'clip_start':moment['start'],'clip_end':moment['end'],
                'caption_cues':clip_cues(transcript['cues'],moment['start'],moment['end']),'caption_origin':transcript['origin'],
                'source_clip_version':version,'source_profile':source_id,'source_episode':episode,'test_only':asset.get('test_only',False)}
            jobs.append(ws.create(channel,request)['id'])
    result={'source_id':source_id,'created_jobs':jobs,'checked_at':now(),'publishing':'Uses the existing separate exact-version approval/private/schedule policy.'}
    write_json(ws.root/'reports'/('clips-'+source_id+'.json'),result);return result


def research_handoff(ws,trend_evidence,source_ids,provider=None):
    candidates=trend_evidence.get('candidates') or trend_evidence.get('videos') or []
    if not candidates:raise Held('trend_evidence_missing','A movie/show source plan needs actual dated trend/reference observations first.')
    catalog=[json.loads(source_path(ws,id).read_text(encoding='utf-8')) for id in source_ids]
    schema={'type':'object','properties':{'requests':{'type':'array','items':{'type':'object','properties':{
        'source_id':{'type':'string'},'work':{'type':'string'},'episode':{'type':'string'},'target_moment':{'type':'string'},
        'evidence_url':{'type':'string'},'reason':{'type':'string'}},'required':['source_id','work','episode','target_moment','evidence_url','reason'],'additionalProperties':False}}},'required':['requests'],'additionalProperties':False}
    result=(provider or Gemini(ws)).generate('source-handoff-v1',{'dated_reference_evidence':candidates,'permitted_catalog':[
        {k:p.get(k) for k in ('id','title','work','episode','urls')} for p in catalog],
        'task':'Plan source/transcript retrieval only for an exact catalog source ID matching the work/episode. Use only actual reference URLs from the evidence. If the needed movie/version/episode is absent, return no request; do not invent source URLs, permissions or famous timestamps.'},schema)
    known={p['id'] for p in catalog};urls={r.get('url') for r in candidates}
    for item in result['requests']:
        if item['source_id'] not in known or item['evidence_url'] not in urls:raise Held('invalid_source_handoff','Research proposed an unknown source or unobserved reference URL.')
        selected=next(p for p in catalog if p['id']==item['source_id'])
        works={normalize(str(p)) for p in [selected.get('work') or selected['title'],*[e.get('work') or selected.get('work') or selected['title'] for e in selected.get('episodes',[])]]}
        episodes={str(e['episode']) for e in selected.get('episodes',[])} or ({str(selected['episode'])} if selected.get('episode') else set())
        if normalize(item['work']) not in works or (episodes and item['episode'] not in episodes):raise Held('invalid_source_handoff','Research work/episode does not match the actual permitted source catalog.')
    result.update(checked_at=now(),note='Source planning does not clear arbitrary movie/creator footage. Downloading and timestamp selection use the exact source profile and real transcript.')
    write_json(ws.root/'reports'/'research-source-handoff.json',result);return result
