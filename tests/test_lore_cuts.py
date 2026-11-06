from copy import deepcopy
import json
from pathlib import Path

import pytest
from PIL import Image

from yt_pipeline.core import Held
from yt_pipeline.lore_cuts import compile_cuts,cut_schedule,cut_painter
from yt_pipeline.lore_screen_cast import SUITS,actor


def scene():return {'unit_id':'u1','kind':'wide','text':'They argue. Spider-Man takes the shield. Then Scott grows.'}


def config():return {'lore_cuts':{'u1':[
    {'on':'','kind':'wide','reason':'Establish the conflict.'},
    {'on':'Spider-Man takes','kind':'shield','reason':'Show the theft at the spoken verb.'},
    {'on':'Then Scott','kind':'giant','reason':'Show the size change at the next event.'}]}}


def test_cuts_follow_aligned_phrases_without_rewriting_spoken_text():
    s=scene();original=deepcopy(s);compile_cuts([s],config(),('wide','shield','giant'),('wide',))
    words=[{'unit_id':'u1','text':t,'start':10+n*.6,'end':10+(n+1)*.6} for n,t in enumerate(s['text'].split())]
    schedule=cut_schedule(s,{'start':10,'duration':7},words)
    assert [c['start'] for c in schedule]==pytest.approx([0,1.2,3.6])
    assert s['text']==original['text']
    calls=[]
    def paint(shot,t,d):calls.append((shot['kind'],t,d,shot['text']));return Image.new('RGB',(2,2))
    cut_painter(paint,schedule)(s,2,7)
    assert calls[0][0]=='shield' and calls[0][1]==pytest.approx(.8) and calls[0][3]==original['text']


def test_invalid_or_unaligned_cuts_cannot_silently_guess_final_timing():
    for mutate in [lambda c:c['lore_cuts']['u1'][1].update(on='not in speech'),
                   lambda c:c['lore_cuts']['u1'][1].update(kind='invented'),
                   lambda c:c['lore_cuts']['u1'][0].update(on='They'),
                   lambda c:c['lore_cuts']['u1'][2].update(on='They argue')]:
        c=config();mutate(c)
        with pytest.raises(Held):compile_cuts([scene()],c,('wide','shield','giant'),('wide',))
    s=scene();compile_cuts([s],config(),('wide','shield','giant'),('wide',))
    with pytest.raises(Held,match='actual aligned'):cut_schedule(s,{'start':0,'duration':7},[])
    assert len(cut_schedule(s,{'start':0,'duration':7},[],preview=True))==3


@pytest.mark.parametrize('facing',[-1,1])
def test_cast_profiles_render_in_both_directions_with_fixed_contact(facing):
    for who in SUITS:
        image=Image.new('RGBA',(720,1280))
        actor(image,who,350,500,1.0,facing=facing,hand=(470,565))
        assert image.getpixel((470,565))[3]>0
        assert image.getbbox()[3]<960


def test_recap_reveal_and_subscribe_are_not_moved_into_the_opening():
    root=Path(__file__).resolve().parents[1]
    civil=json.loads((root/'examples/screen-recaps/civil-war-complete/part-1.json').read_text(encoding='utf8'))
    assert not any('parents' in u['text'] for u in civil['units'][:8])
    assert 'parents' in civil['units'][8]['text']
    for folder in ('civil-war-complete','strange-supreme-heart'):
        s=json.loads((root/f'examples/screen-recaps/{folder}/part-1.json').read_text(encoding='utf8'))
        assert s['edit']['cta'] and s['units'][-1]['text'].endswith('For more stories like this, subscribe.')
        assert all('subscribe' not in u['text'] for u in s['units'][:-1])
