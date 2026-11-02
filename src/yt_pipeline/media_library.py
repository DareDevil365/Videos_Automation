"""A rebuildable local text index of registered media; not a semantic classifier."""
import json
import re
from .assets import asset_record
from .core import Held,now


def index_library(ws):
    with ws.connect() as db:
        db.execute('CREATE VIRTUAL TABLE IF NOT EXISTS media_search USING fts5(asset_id UNINDEXED,kind UNINDEXED,body)')
        rows=db.execute('SELECT id,data FROM assets LIMIT 10001').fetchall()
        if len(rows)>10000:raise Held('library_budget','Index at most 10,000 registered assets at a time.')
        db.execute('DELETE FROM media_search')
        for row in rows:
            asset=json.loads(row['data']);evidence=asset.get('evidence',{})
            fields=[asset.get('name',''),asset.get('kind',''),asset.get('source_type','')]
            fields.extend(str(evidence.get(k,''))[:1000] for k in ('title','query','description','operation'))
            db.execute('INSERT INTO media_search(asset_id,kind,body) VALUES(?,?,?)',(row['id'],asset.get('kind',''),' '.join(fields)))
    return {'indexed':len(rows),'checked_at':now(),'method':'SQLite full-text metadata search; no image understanding'}


def search_library(ws,query,kind=None,limit=8):
    words=re.findall(r'[^\W_]+',str(query),re.UNICODE)[:12]
    if not words:raise Held('library_query','Supply a few descriptive search words.')
    if kind not in (None,'image','video','audio'):raise Held('library_query','Unsupported media kind.')
    if type(limit) is not int or not 1<=limit<=20:raise Held('library_query','Choose 1-20 results.')
    index_library(ws)
    match=' OR '.join('"'+w+'"' for w in words)
    with ws.connect() as db:
        rows=db.execute('SELECT asset_id,bm25(media_search) AS score FROM media_search WHERE media_search MATCH ? '+
            ('AND kind=? ' if kind else '')+'ORDER BY score LIMIT 100',([match,kind] if kind else [match])).fetchall()
    results=[];skipped=0
    for row in rows:
        try:asset=asset_record(ws,row['asset_id'])
        except (Held,FileNotFoundError):skipped+=1;continue
        results.append({'id':asset['id'],'kind':asset['kind'],'file':asset['path'],
            'title':asset.get('evidence',{}).get('title',asset.get('name','')),
            'test_only':asset.get('test_only',False),'match_score':-row['score']})
        if len(results)>=limit:break
    return {'query':str(query)[:180],'results':results,'ineligible_skipped':skipped,
        'limits':['Metadata matches are candidates, not proof of visual relevance or permission. Eligibility is rechecked on use.']}
