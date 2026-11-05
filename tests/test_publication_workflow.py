from copy import deepcopy
import json
from pathlib import Path

import pytest

from shorts_editor.store import write_json
from yt_pipeline.core import Workspace,Held,file_hash
from yt_pipeline.production import create_production,finish_production
from yt_pipeline.publication_metadata import validate_metadata,make_metadata
from yt_pipeline.publishing import approve,publish,load_upload


def ready(ws,public=True,test_only=False):
    job=ws.create('entertainment',{'auto_publish':True,'publish_visibility':'public' if public else 'private'})
    folder=ws.job_dir(job['id']);video=folder/'video.mp4';video.write_bytes(b'fixture bytes')
    package={'video':str(video),'title':'The wrong group chat','description':'A fictional chat comedy.',
        'category_id':'23','made_for_kids':False,'contains_synthetic_media':True,
        'qa':{'publication_ready':not test_only,'video_sha256':file_hash(video)}}
    for name,value in [('package',package),('direct',{'provenance':[]}),('research',{'sources':[]})]:write_json(folder/(name+'.json'),value)
    ws.update(job['id'],status='ready',artifacts={n:{'path':str(folder/(n+'.json')),'sha256':file_hash(folder/(n+'.json'))} for n in ('package','direct','research')})
    config=ws.config();config['channels']['entertainment'].update(publication_mode='public' if public else 'private');ws.save_config(config)
    return job['id']


class YouTube:
    def __init__(self,visibility='public',lose_final=False):self.calls=[];self.visibility=visibility;self.lose_final=lose_final;self.done=False
    def identity(self):return {'id':'UCfixture'}
    def call(self,method,url,body=None,headers=None):
        self.calls.append((method,body,headers))
        if method=='POST':return 200,{'Location':'https://www.googleapis.com/upload/youtube/v3/videos?upload_id=test'},b''
        if headers.get('Content-Range','').startswith('bytes */'):return 200,{},b'{"id":"fixture-video"}'
        if self.lose_final:self.lose_final=False;raise Held('youtube_network','Simulated lost final response')
        return 200,{},b'{"id":"fixture-video"}'
    def video(self,id):return {'snippet':{'channelId':'UCfixture'},'status':{'privacyStatus':self.visibility,'uploadStatus':'processed'},'processingDetails':{'processingStatus':'succeeded'}}


def test_connection_can_be_deferred_without_rerender_or_upload(tmp_path):
    ws=Workspace(tmp_path/'ws');job=ready(ws)
    before=deepcopy(ws.get(job)['artifacts']);result=finish_production(ws,job)
    assert result['status']=='awaiting_youtube_connection' and result['visibility']=='public'
    assert ws.get(job)['status']=='ready' and ws.get(job)['artifacts']==before
    assert load_upload(ws,job) is None


def test_public_upload_exact_metadata_and_retry_reuse_one_session(tmp_path):
    ws=Workspace(tmp_path/'ws');job=ready(ws)
    config=ws.config();config['channels']['entertainment']['youtube_channel_id']='UCfixture';ws.save_config(config)
    client=YouTube(lose_final=True)
    first=finish_production(ws,job,client)
    assert first['status']=='publication_held'
    result=finish_production(ws,job,client)
    assert result['status']=='published' and result['url'].endswith('fixture-video')
    assert len([c for c in client.calls if c[0]=='POST'])==1
    body=json.loads(client.calls[0][1]);assert body['status']['privacyStatus']=='public'
    assert body['snippet']['description']=='A fictional chat comedy.'
    finish_production(ws,job,client)
    assert len([c for c in client.calls if c[0]=='POST'])==1


def test_test_media_and_changed_visibility_never_upload(tmp_path):
    ws=Workspace(tmp_path/'ws');job=ready(ws,test_only=True);client=YouTube()
    assert finish_production(ws,job,client)['error_code']=='test_media' and not client.calls
    job=ready(ws);config=ws.config();config['channels']['entertainment']['youtube_channel_id']='UCfixture';ws.save_config(config)
    approve(ws,job)
    config['channels']['entertainment']['publication_mode']='private';ws.save_config(config)
    with pytest.raises(Held,match='policy differs'):publish(ws,job,True,client)
    assert not client.calls


def test_public_visibility_without_confirmed_processing_is_not_called_published(tmp_path):
    ws=Workspace(tmp_path/'ws');job=ready(ws)
    config=ws.config();config['channels']['entertainment']['youtube_channel_id']='UCfixture';ws.save_config(config)
    client=YouTube();original=client.video
    client.video=lambda id:{'snippet':{'channelId':'UCfixture'},'status':{'privacyStatus':'public','uploadStatus':'uploaded'}}
    assert finish_production(ws,job,client)['status']=='processing'
    client.video=original
    assert finish_production(ws,job,client)['status']=='published'
    assert len([c for c in client.calls if c[0]=='POST'])==1


def test_production_request_resumes_stable_token_and_persists_music(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');calls=[]
    monkeypatch.setattr('yt_pipeline.curated_music.select_genre_music',lambda *a,**k:calls.append(k) or {'id':'music-fixture'})
    first=create_production(ws,'A boss joins a family chat',token='stable')
    second=create_production(ws,'A boss joins a family chat',token='stable')
    assert first['id']==second['id'] and len(calls)==1
    req=first['request']
    assert req['music_id']=='music-fixture' and req['chat_voiceover'] and req['metadata_version']==2
    assert req['publish_visibility']=='public' and req['auto_publish'] and not req['test_only']


def metadata_fixture():
    script={'units':[{'id':'u1','text':'I added my boss.'},{'id':'u2','text':'He added his boss.'}]}
    evidence=[{'unit_id':'u1','quote':script['units'][0]['text']}]
    value={'titles':[{'title':title,'angle':'curiosity','evidence':evidence} for title in ('My Boss Joined the Group Chat','The Wrong Group Chat','He Invited His Boss Too')],
        'selected_index':0,'description':'One wrong invitation changes the group chat.','description_evidence':evidence,'keywords':['group chat','boss'],'reason':'A specific consequence creates an honest question.'}
    return script,value


def test_metadata_evidence_and_api_limits():
    s,v=metadata_fixture();result=validate_metadata(v,s)
    assert result['title']==v['titles'][0]['title']
    for change in ('quote','length','index'):
        bad=deepcopy(v)
        if change=='quote':bad['description_evidence'][0]['quote']='Never said this'
        if change=='length':bad['titles'][0]['title']='x'*101
        if change=='index':bad['selected_index']=3
        with pytest.raises(Held):validate_metadata(bad,s)
