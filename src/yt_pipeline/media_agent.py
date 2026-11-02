"""Search, acquire and cache actual licensed media for the compositor's slots."""
import html
import json
import os
from pathlib import Path
import re
from urllib.parse import urlencode, urlparse
import uuid

from shorts_editor.store import write_json
from .assets import register_asset, asset_record, pexels_video
from .core import Held, digest, now
from .net import fetch


def clean(value):return html.unescape(re.sub(r'<[^>]*>','',str(value))).strip()[:1800]


def commons_license(meta):
    name=clean(meta.get('LicenseShortName',{}).get('value',''))
    url=clean(meta.get('LicenseUrl',{}).get('value',''))
    if any(x in name.lower() for x in ('by-sa','by-nc','by-nd')):return None
    if name=='Public domain':return {'name':name,'url':url or 'https://commons.wikimedia.org/wiki/Commons:Public_domain'}
    if name=='CC0' and 'creativecommons.org/publicdomain/zero/' in url:return {'name':name,'url':url}
    if re.fullmatch(r'CC BY (2\.0|2\.5|3\.0|4\.0)',name) and 'creativecommons.org/licenses/by/' in url:return {'name':name,'url':url}
    return None


def commons_search(workspace, query, kind='image', fetcher=fetch):
    if kind not in ('image','video','audio'):raise ValueError('Choose image, video or audio')
    query=str(query).strip()[:160]
    if not query:raise Held('media_query_missing','A media search needs a literal query.')
    workspace.reserve_call('commons_search',100)
    file_filter={'image':'filetype:bitmap','video':'filetype:video','audio':'filetype:audio'}[kind]
    params={'action':'query','format':'json','generator':'search','gsrsearch':query+' '+file_filter,'gsrnamespace':6,'gsrlimit':12,
            'prop':'imageinfo','iiprop':'url|extmetadata|mime|size','iiurlwidth':1200}
    body,_,_=fetcher('https://commons.wikimedia.org/w/api.php?'+urlencode(params))
    pages=json.loads(body).get('query',{}).get('pages',{})
    candidates=[]
    for item in pages.values():
        info=item.get('imageinfo',[{}])[0];meta=info.get('extmetadata',{});license=commons_license(meta)
        mime=info.get('mime','')
        if not license or not mime.startswith(kind+'/'):continue
        if kind=='image' and min(info.get('width',0),info.get('height',0))<250:continue
        if kind=='video' and mime not in ('video/webm','video/ogg','video/mp4'):continue
        if kind=='audio' and mime not in ('audio/ogg','audio/mpeg','audio/wav','audio/flac','audio/x-wav'):continue
        url=info.get('thumburl') if kind=='image' else info.get('url')
        url=url or info.get('url','')
        if urlparse(url).scheme!='https' or urlparse(url).hostname not in ('upload.wikimedia.org','thumb.wikimedia.org'):continue
        artist=clean(meta.get('Artist',{}).get('value',''))
        if not artist:continue
        title=clean(item.get('title',''));terms=re.findall(r'[a-z]{3,}',query.lower())
        candidates.append({'provider':'commons','kind':kind,'query':query,'title':title,'download_url':url,
            'source_url':info.get('descriptionurl',''),'artist':artist,'license':license,'checked_at':now(),
            'mime':mime,'score':sum(word in title.lower() for word in terms),'width':info.get('width'),'height':info.get('height')})
    candidates.sort(key=lambda row:row['score'],reverse=True)
    result={'query':query,'kind':kind,'checked_at':now(),'candidates':candidates,
            'limits':['Search ranking is not a visual relevance guarantee. Stock people do not endorse the narration.',
                      'Only the recorded license allowlist is accepted; no NC/ND/SA or unknown-license fallback.']}
    write_json(workspace.root/'reports'/('media-search-'+digest([kind,query])[:16]+'.json'),result)
    return result


def commons_acquire(workspace, query, kind='image', fetcher=fetch):
    cache=workspace.root/'cache'/('media-'+digest(['commons-v1',kind,query])+'.json')
    if cache.exists():return asset_record(workspace,json.loads(cache.read_text())['asset_id'])
    results=commons_search(workspace,query,kind,fetcher)
    if not results['candidates']:raise Held('media_not_found',f'No eligible {kind} matched the query. Add a permitted local asset or refine the search.')
    row=results['candidates'][0];url=row['download_url']
    suffix={'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp','image/gif':'.gif','video/webm':'.webm','video/ogg':'.ogg',
            'video/mp4':'.mp4','audio/ogg':'.ogg','audio/mpeg':'.mp3','audio/wav':'.wav','audio/x-wav':'.wav','audio/flac':'.flac'}.get(row['mime'])
    if not suffix:raise Held('media_type','Unsupported downloaded media type.')
    body,_,final=fetcher(url,maximum=20_000_000 if kind=='image' else 180_000_000)
    if urlparse(final).hostname not in ('upload.wikimedia.org','thumb.wikimedia.org'):raise Held('media_host','Media redirected outside the selected provider.')
    path=workspace.root/'assets'/('commons-'+uuid.uuid4().hex+suffix);path.write_bytes(body)
    evidence={**row,'modifications':'Crop/resize, placement, captions and audio mixing may be applied in the edit.'}
    attribution=f"{row['title']} — {row['artist']}. {row['license']['name']}: {row['license']['url']}. Source: {row['source_url']}. Cropped/edited."
    asset=register_asset(workspace,path,'licensed_stock',evidence,attribution=attribution)
    write_json(cache,{'asset_id':asset['id'],'checked_at':now()})
    return asset_record(workspace,asset['id'])


def acquire_visual(workspace, query, kind='image'):
    if kind=='video' and os.environ.get('PEXELS_API_KEY'):
        cache=workspace.root/'cache'/('media-'+digest(['pexels-v1',query])+'.json')
        if cache.exists():return asset_record(workspace,json.loads(cache.read_text())['asset_id'])
        asset=pexels_video(workspace,query);write_json(cache,{'asset_id':asset['id']})
        return asset_record(workspace,asset['id'])
    return commons_acquire(workspace,query,kind)


def select_visuals(workspace, job, script):
    request=job['request'];selected=[];mapping=request.get('media_assets',{})
    for unit in script['units']:
        supplied=mapping.get(unit['id']) or (request.get('portrait_asset_id') if script['format']=='aura' else None)
        if supplied:
            if str(supplied).startswith('generation:'):
                from .browser_agent import read_generation
                generation=read_generation(workspace,supplied.partition(':')[2])
                if not generation.get('asset_id'):raise Held('generated_media_pending','Waiting for the browser generation/download job. Completed script and speech are retained.',retry_after=60)
                supplied=generation['asset_id']
            asset=asset_record(workspace,supplied)
        else:
            query=request.get('media_queries',{}).get(unit['id']) or request.get('media_query') or unit.get('visual_query') or script['title']
            kind=request.get('media_kind') or unit.get('visual_kind','image')
            # Images are a deliberate keyless option for ordinary stock illustrations.
            if kind=='video' and not os.environ.get('PEXELS_API_KEY') and request.get('allow_image_fallback',True):kind='image'
            asset=acquire_visual(workspace,query,kind)
        selected.append({'unit_id':unit['id'],'asset':asset})
    return selected
