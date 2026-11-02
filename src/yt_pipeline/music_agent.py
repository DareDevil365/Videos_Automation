"""Separate music fit/eligibility from evidence of current popularity."""
import json
from .assets import asset_record
from .core import Held,now
from .media_agent import commons_acquire,commons_search
from .benchmarks import benchmark
from shorts_editor.store import write_json

CATEGORIES={'aura':'dark electronic instrumental','cringe':'playful instrumental','learning':'quiet instrumental',
            'gameplay':'electronic instrumental','storytime':'ambient instrumental','horror':'quiet eerie suspense ambient instrumental','asmr':'gentle ambient'}


def register_music(ws,asset_id,categories):
    if not categories or any(c not in CATEGORIES for c in categories):raise ValueError('Choose known music categories')
    asset=asset_record(ws,asset_id)
    if not asset['has_audio']:raise Held('music_audio','The selected asset has no audio.')
    path=ws.root/'music-library.json';library=json.loads(path.read_text()) if path.exists() else []
    library=[r for r in library if r['asset_id']!=asset_id]
    library.append({'asset_id':asset_id,'categories':categories,'checked_at':now()});write_json(path,library)
    return library[-1]


def choose_music(ws,category,auto_download=False,query=None):
    if category not in CATEGORIES:raise ValueError('Unknown music category')
    path=ws.root/'music-library.json';library=json.loads(path.read_text()) if path.exists() else []
    for item in library:
        if category in item['categories']:return asset_record(ws,item['asset_id'])
    if not auto_download:raise Held('music_library_empty','No permitted track is registered for this category. Search/acquire or import a licensed track first.')
    asset=commons_acquire(ws,query or CATEGORIES[category],'audio');register_music(ws,asset['id'],[category]);return asset


def discover_music(ws,category,query=None,trends=False):
    if category not in CATEGORIES:raise ValueError('Unknown category')
    result={'category':category,'checked_at':now(),'fit_query':query or CATEGORIES[category],
            'licensed_candidates':commons_search(ws,query or CATEGORIES[category],'audio'),
            'note':'Category fit is an editorial hypothesis. A downloadable licensed track is not automatically a currently trending sound.'}
    if trends:result['public_reference_counts']=benchmark(ws,'entertainment',category+' music shorts')
    write_json(ws.root/'reports'/('music-'+category+'.json'),result);return result
