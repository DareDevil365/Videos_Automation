"""Freeze varied local narration pairs per series, independent of character gender."""
from collections import Counter
import random

from .core import Held


VOICES = ('am_adam','am_michael','bm_george','af_heart','af_bella')
PAIRS = (
    ('am_adam','bm_george'),('af_heart','am_michael'),('am_michael','af_bella'),
    ('af_bella','am_adam'),('am_adam','af_heart'),('af_heart','bm_george'),
)


def validate_voices(value):
    if not isinstance(value,dict) or set(value)!={'Host','Narrator'} or any(v not in VOICES for v in value.values()):
        raise Held('lore_voice','Choose Host and Narrator from the supported local voice set.')
    if value['Host']==value['Narrator']:
        raise Held('lore_voice','Use distinct host and narrator voices.')
    return dict(value)


def choose_series_voices(workspace, series_id, explicit=None):
    if explicit is not None:
        return validate_voices(explicit)
    jobs=[j for j in workspace.jobs(100) if j['request'].get('playbook')=='comic_lore'
          and j['status'] in ('ready','published','uploaded_private','scheduled','processing')]
    for job in jobs:
        if job['request'].get('series',{}).get('id')==series_id and job['request'].get('source_voices'):
            return validate_voices(job['request']['source_voices'])
    # Seeded tie breaking gives variety without changing voices on a resumed build.
    recent=[]
    seen=set()
    for job in jobs:
        key=job['request'].get('series',{}).get('id') or job['id']
        if key in seen:continue
        seen.add(key)
        pair=job['request'].get('source_voices',{'Host':'am_adam','Narrator':'bm_george'})
        recent.append((pair['Host'],pair['Narrator']))
        if len(recent)==4:break
    counts=Counter(recent);rng=random.Random(series_id);candidates=list(PAIRS);rng.shuffle(candidates)
    family=lambda voice:'female' if voice.startswith(('af_','bf_')) else 'male'
    pair=min(candidates,key=lambda p:(counts[p],sum(old[1]==p[1] for old in recent),
        sum(family(old[1])==family(p[1]) for old in recent),sum(old[0]==p[0] for old in recent)))
    return {'Host':pair[0],'Narrator':pair[1]}
