"""Bounded series ingestion for recorded or explicitly permitted sources."""
from datetime import datetime,timezone
import json
from pathlib import Path
import re
from urllib.parse import urlparse

from shorts_editor.store import write_json
from .assets import register_asset,asset_record
from .core import Held,digest,now,file_hash
from .net import fetch,public_url
from .transcripts import parse_subtitles,transcribe


def source_path(ws,id):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',id):raise ValueError('Invalid source ID')
    folder=ws.root/'sources';folder.mkdir(exist_ok=True)
    return folder/(id+'.json')


def register_source(ws,record):
    if not isinstance(record,dict) or not record.get('title'):raise ValueError('A source needs a title and explicit permission record')
    permission=record.get('permission',{})
    if not permission.get('evidence'):raise Held('source_permission','Record actual source permission evidence.')
    if permission.get('commercial') is not True or permission.get('editing') is not True:raise Held('source_permission','Commercial edited reuse must be explicitly recorded.')
    if not record.get('local_media') and not record.get('episodes') and (not isinstance(record.get('urls'),list) or not record['urls']):raise ValueError('Supply local media or a bounded list of source URLs/episodes')
    if record.get('episodes') and (not isinstance(record['episodes'],list) or any(not isinstance(e,dict) or not e.get('url') or not e.get('episode') for e in record['episodes'])):raise ValueError('Each series episode needs its actual URL and episode label')
    id=record.get('id') or digest([record['title'],record.get('urls'),record.get('episodes'),record.get('local_media')])[:24]
    path=source_path(ws,id)
    if path.exists():raise Held('source_exists','Source profile exists. Use a new version ID for changed permissions.')
    value={**record,'id':id,'registered_at':now()};write_json(path,value);return value


class Quiet:
    def debug(self,*args):pass
    def warning(self,*args):pass
    def error(self,*args):pass


def download_source(ws,profile,url,folder):
    if profile['permission'].get('download_allowed') is not True:raise Held('source_permission','Downloading is not authorized in this source profile.')
    public_url(url);host=urlparse(url).hostname
    if host in ('www.youtube.com','youtube.com','youtu.be','m.youtube.com'):
        try:import yt_dlp
        except ImportError:raise Held('downloader_missing','Install the optional source downloader dependencies.')
        def bounded(progress):
            if progress.get('downloaded_bytes',0)>500_000_000:raise Held('source_size','Source download exceeded 500 MB.')
        options={'outtmpl':str(folder/'source.%(ext)s'),'format':'bestvideo[height<=720]+bestaudio/best[height<=720]',
                 'merge_output_format':'mp4','noplaylist':True,'quiet':True,'no_warnings':True,'logger':Quiet(),'max_filesize':500_000_000,
                 'retries':1,'fragment_retries':1,'socket_timeout':20,'progress_hooks':[bounded],
                 'writesubtitles':True,'writeautomaticsub':True,'subtitleslangs':['en','en-US','en-orig'],'subtitlesformat':'vtt/srt/best'}
        try:
            with yt_dlp.YoutubeDL(options) as downloader:downloader.extract_info(url,download=True)
        except Held:raise
        except Exception:raise Held('source_download_failed','The source could not be downloaded. No login, restriction or payment barrier was bypassed.')
        files=[p for p in folder.glob('source.*') if p.suffix.lower() in ('.mp4','.webm','.mkv','.mov')]
        if not files:raise Held('source_download_failed','No completed source video was produced.')
        return files[0]
    suffix=Path(urlparse(url).path).suffix.lower()
    if suffix not in ('.mp4','.webm','.mov','.mkv'):raise Held('source_url','Use an actual permitted video URL or a supported YouTube source.')
    body,_,_=fetch(url,maximum=180_000_000);path=folder/('source'+suffix);path.write_bytes(body);return path


def ingest_source(ws,id,limit=3):
    profile=json.loads(source_path(ws,id).read_text(encoding='utf-8'));permission=profile['permission']
    if permission.get('expires_at'):
        expiry=datetime.fromisoformat(permission['expires_at'].replace('Z','+00:00'))
        if expiry.tzinfo is None or expiry<=datetime.now(timezone.utc):raise Held('source_expired','Source permission expired or has no timezone.')
    entries=profile.get('episodes') or [{'url':u,'work':profile.get('work'),'episode':profile.get('episode')} for u in profile.get('urls',[])]
    entries=entries[:max(1,min(5,int(limit)))] if not profile.get('local_media') else [{'url':'local','work':profile.get('work'),'episode':profile.get('episode')}]
    records=[]
    for entry in entries:
        url=entry['url']
        folder=ws.root/'sources'/(id+'-'+digest(url)[:12]);folder.mkdir(exist_ok=True)
        checkpoint=folder/'ingested.json'
        if checkpoint.exists():
            cached=json.loads(checkpoint.read_text(encoding='utf-8'));asset_record(ws,cached['asset_id'])
            if cached.get('profile_sha256')!=file_hash(source_path(ws,id)):raise Held('source_changed','Source profile changed after ingestion. Register a new version before reuse.')
            if file_hash(cached['transcript_file'])!=cached['transcript_sha256']:raise Held('transcript_changed','Source transcript changed after ingestion.')
            records.append(cached);continue
        path=Path(profile['local_media']).resolve() if url=='local' else download_source(ws,profile,url,folder)
        evidence={'source_profile':id,'profile_sha256':file_hash(source_path(ws,id)),'source_url':url if url!='local' else None,'permission':permission,'work':entry.get('work') or profile.get('work'),'episode':entry.get('episode')}
        asset=register_asset(ws,path,'owner_recording' if profile.get('owner_recording') else 'licensed_creator',evidence,
            expires_at=permission.get('expires_at'),attribution=permission.get('attribution',''),test_only=profile.get('test_only',False))
        subtitle=Path(profile['transcript_file']).resolve() if profile.get('transcript_file') else next(iter(sorted(folder.glob('*.vtt'))+sorted(folder.glob('*.srt'))),None)
        transcript={'origin':'supplied_subtitles','cues':parse_subtitles(subtitle)} if subtitle else transcribe(ws,path,profile.get('asr_model','base.en'))
        transcript_path=folder/'transcript.json';write_json(transcript_path,transcript)
        result={'source_id':id,'asset_id':asset['id'],'title':profile['title'],'source_url':url if url!='local' else None,
                'work':entry.get('work') or profile.get('work'),'episode':entry.get('episode'),'profile_sha256':file_hash(source_path(ws,id)),'transcript_file':str(transcript_path),
                'transcript_sha256':file_hash(transcript_path),'transcript_origin':transcript['origin'],'ingested_at':now()}
        write_json(checkpoint,result);records.append(result)
    return {'source_id':id,'episodes':records,'limit':limit,'note':'Only explicit permitted episode URLs are ingested; series titles alone do not trigger arbitrary downloads.'}
