"""Load a small trusted genre skill into writer/reviewer context."""
from pathlib import Path
from .core import digest


ROOT=Path(__file__).with_name('skills')/'short-video-writing'


def craft_context(genre='story',medium='chat'):
    mode='comedy' if genre=='comedy' else 'mystery' if genre in ('mystery','thriller','horror_stock','tea_chat') else 'aura' if genre in ('aura','aura_progression') else 'factual' if genre in ('documentary_chapter','education_demo','rewrite_reveal','myth_fact','quiz_pause','movie_countdown','movie_brief','current_affairs') else 'story'
    core=(ROOT/'SKILL.md').read_text(encoding='utf-8').split('---',2)[-1].strip()
    selected=(ROOT/'references'/(mode+'.md')).read_text(encoding='utf-8')
    timing=(ROOT/'references/timing.md').read_text(encoding='utf-8')
    return {'name':'short-video-writing','version':1,'genre':mode,'medium':medium,
        'guidance':core+'\n\n'+selected+'\n\n'+timing,
        'sha256':digest([core,selected,timing]),
        'scope':'Trusted writing guidance; current JSON/content contracts take precedence. No quality or engagement guarantee.'}
