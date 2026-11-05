"""Owner-started make → package → upload workflow, separate from preview batches."""
import json
from pathlib import Path
import uuid

from shorts_editor.store import write_json
from .core import Held,now,redact
from .pipeline import Pipeline
from .publishing import approve,publish,metadata_for


def create_production(ws,topic,genre='comedy',format='chat',visibility='public',extra=None,token=None):
    if not token:return _create_production(ws,topic,genre,format,visibility,extra,token)
    owner=uuid.uuid4().hex;name='production-request:'+token
    ws.worker_lock(owner,name=name)
    try:return _create_production(ws,topic,genre,format,visibility,extra,token)
    finally:ws.worker_lock(owner,release=True,name=name)


def _create_production(ws,topic,genre,format,visibility,extra,token):
    if not isinstance(topic,str) or not 1<=len(topic.strip())<=180:raise Held('production_topic','Describe the video in 1-180 characters.')
    if genre not in ('comedy','mystery','thriller','story'):raise Held('production_genre','Choose comedy, mystery, thriller or story.')
    if format not in ('chat','phone'):raise Held('production_format','Choose chat or phone; other finished formats can use finish-production.')
    if visibility not in ('public','private','none'):raise Held('production_visibility','Choose public, private or none.')
    if token:
        with ws.connect() as db:
            saved=db.execute("SELECT id FROM jobs WHERE json_extract(request,'$.production_token')=? ORDER BY created_at LIMIT 1",(token,)).fetchone()
        if saved:return ws.get(saved['id'])
    request=dict(extra or {})
    request.update(topic=topic.strip(),playbook='server_chat',chat_tone=genre,chat_editing_version=2,chat_writing_version=2,
        chat_script_review=True,chat_voiceover=True,fiction=True,test_only=False,bottom_kind='none',require_music=True,
        hook_options=False,editorial_review='off',visual_review='off',phone_story=format=='phone',metadata_version=2,
        auto_publish=visibility!='none',production_workflow=1)
    if visibility!='none':request['publish_visibility']=visibility
    else:request.pop('publish_visibility',None)
    if token:request['production_token']=token
    if not request.get('music_id'):
        from .curated_music import select_genre_music
        request['music_id']=select_genre_music(ws,genre,selection_key=uuid.uuid4().hex)['id']
    # Stored channel policy plus a per-job opt-in prevents old preview/backlog uploads.
    if visibility!='none':
        config=ws.config();config['channels']['entertainment']['publication_mode']=visibility;ws.save_config(config)
    return ws.create('entertainment',request)


def finish_production(ws,job_id,client=None):
    job=ws.get(job_id);request=job['request']
    if not request.get('auto_publish'):
        return {'job_id':job_id,'status':'local_only','message':'Video packaging is complete; this job has no automatic upload request.'}
    path=ws.job_dir(job_id)/'publication.json'
    try:
        _,metadata=metadata_for(ws,job_id)
        profile=ws.config()['channels'][job['channel']]
        if not metadata['qa']['publication_ready']:raise Held('test_media','This preview or unresolved result is not eligible for publication.')
        if not profile.get('youtube_channel_id') or (client is None and not (ws.root/'credentials'/(job['channel']+'.json')).is_file()):
            result={'job_id':job_id,'status':'awaiting_youtube_connection','title':metadata['title'],
                'description':metadata['description'],'visibility':request.get('publish_visibility',profile['publication_mode']),
                'message':'Video and metadata are ready. Connect YouTube later, then resume this exact job; no rerender is needed.'}
        else:
            if job['status']=='ready':approve(ws,job_id)
            result=publish(ws,job_id,apply=True,client=client)
            result['title']=metadata['title']
            if result.get('video_id'):result['url']='https://www.youtube.com/watch?v='+result['video_id']
    except Held as exc:
        result={'job_id':job_id,'status':'publication_held','error_code':exc.code,'message':redact(exc)}
        ws.alert(job_id+':'+exc.code,job_id,str(exc))
    result['checked_at']=now();write_json(path,result)
    return result


def run_production(ws,job_id,pipeline=None,client=None):
    job=ws.get(job_id)
    if job['status'] not in ('ready','processing','published','uploaded_private','scheduled'):
        job=(pipeline or Pipeline(ws)).run(job_id)
    result={'job':job}
    if job['status'] in ('ready','processing','published','uploaded_private','scheduled'):
        result['publication']=finish_production(ws,job_id,client)
    return result
