"""Compare public observations without inventing competitors' private data."""
from datetime import datetime, timezone
import json
import os
import re
from urllib.parse import urlencode

from shorts_editor.store import write_json
from .core import Held, now
from .net import fetch
from .research import discover


def benchmark(workspace, channel, query, candidates=None, fetcher=fetch):
    if channel not in workspace.config()['channels']:raise ValueError('Unknown channel profile')
    key=os.environ.get('YOUTUBE_API_KEY')
    if not key:raise Held('youtube_key_missing','Public video benchmarking needs YOUTUBE_API_KEY. Competitor private Analytics are not accessible.')
    candidates=candidates if candidates is not None else discover(workspace,channel,query)['candidates']
    ids=[]
    for row in candidates:
        match=re.fullmatch(r'https://www\.youtube\.com/watch\?v=([A-Za-z0-9_-]{6,20})',row.get('url',''))
        if match and match[1] not in ids:ids.append(match[1])
    if not ids:return {'channel':channel,'query':query,'checked_at':now(),'videos':[],'note':'No supported public video IDs were discovered.'}
    workspace.reserve_call('youtube_benchmark',30)
    body,_,_=fetcher('https://www.googleapis.com/youtube/v3/videos?'+urlencode({'part':'snippet,statistics,contentDetails','id':','.join(ids[:10]),'key':key}))
    checked=datetime.now(timezone.utc);records=[]
    for item in json.loads(body).get('items',[]):
        stats=item.get('statistics',{});snippet=item.get('snippet',{})
        try:
            views=int(stats['viewCount']);published=datetime.fromisoformat(snippet['publishedAt'].replace('Z','+00:00'))
        except (KeyError,ValueError):continue
        if published.tzinfo is None or views<0:continue
        age=(checked-published).total_seconds()/3600
        if age<0:continue
        age=max(.1,age)
        with workspace.connect() as db:
            previous=db.execute('SELECT data FROM public_snapshots WHERE video_id=? ORDER BY at DESC LIMIT 1',(item['id'],)).fetchone()
        delta=None;elapsed=None
        if previous:
            old=json.loads(previous[0]);elapsed=(checked-datetime.fromisoformat(old['checked_at'])).total_seconds()/3600
            if elapsed>=1 and views>=old['views']:delta=(views-old['views'])/elapsed
        record={'video_id':item['id'],'url':'https://www.youtube.com/watch?v='+item['id'],'title':snippet.get('title',''),
                'channel_id':snippet.get('channelId'),'channel_title':snippet.get('channelTitle'),'published_at':published.isoformat(),
                'checked_at':checked.isoformat(),'views':views,'likes':int(stats['likeCount']) if 'likeCount' in stats else None,
                'age_hours':age,'views_per_hour_since_publish':round(views/age,2),
                'observed_views_per_hour_delta':round(delta,2) if delta is not None else None,
                'comparison_hours':elapsed if delta is not None else None,'duration':item.get('contentDetails',{}).get('duration')}
        records.append(record)
        with workspace.connect() as db:db.execute('INSERT INTO public_snapshots(video_id,at,data) VALUES(?,?,?)',(item['id'],record['checked_at'],json.dumps(record)))
    records.sort(key=lambda r:r['views_per_hour_since_publish'],reverse=True)
    result={'channel':channel,'query':query,'checked_at':now(),'videos':records,
            'interpretation':'Use observed topics/hooks as hypotheses for distinct original episodes, not copied scripts.',
            'limitations':['Age-normalized lifetime views are not current growth. Public-view deltas need another observation at least one hour later.',
                          'Search relevance is not a census of the highest-viewed Shorts; short duration does not prove Shorts classification.',
                          'Public counts do not reveal retention, RPM, revenue, US audience share or reuse permission.']}
    write_json(workspace.root/'reports'/(channel+'-benchmarks.json'),result)
    return result
