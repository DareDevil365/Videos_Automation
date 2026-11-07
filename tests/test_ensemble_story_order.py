"""Keep the two requested film payoffs out of their preceding setup shots."""
import json
from pathlib import Path

from yt_pipeline.lore_cuts import tokens
from yt_pipeline.lore_visuals import plan_lore
from yt_pipeline.lore_screen_cast import actor
from PIL import Image


ROOT=Path(__file__).resolve().parents[1]


def packet(folder):
    root=ROOT/'examples/screen-recaps'/folder
    read=lambda name:json.loads((root/name).read_text(encoding='utf8'))
    script,series,brief=read('part-1.json'),read('series.json'),read('brief.json')
    request={**series['parts'][0],'source_voices':series['source_voices']}
    return plan_lore(script,request,brief)['plan']


def test_joint_sacrifice_is_not_visible_during_the_solo_attempt():
    scenes=packet('deadpool-wolverine-recap')['scenes']
    setup=next(s for s in scenes if 'Wade locks Logan out' in s['text'])
    assert setup['kind']!='dw_wires' and all(c['kind']!='dw_wires' for c in setup['cuts'])
    payoff=next(s for s in scenes if 'Logan breaks in' in s['text'])
    assert payoff['kind']=='dw_wires'


def test_franklin_revival_waits_for_the_reversal_in_the_spoken_story():
    scenes=packet('fantastic-four-first-steps-recap')['scenes']
    loss=next(s for s in scenes if 'Sue collapses' in s['text'])
    assert loss['kind']=='ff_loss' and loss['cuts'][0]['kind']=='ff_loss'
    revival=next(c for c in loss['cuts'] if c['kind']=='ff_revive')
    assert revival['on']=='Then Franklin' and revival['token_index']>tokens(loss['text']).index('dies')


def test_both_hands_can_meet_independent_absolute_contacts():
    for facing in (-1,1):
        for who in ('deadpool','wolverine'):
            image=Image.new('RGBA',(720,1280))
            actor(image,who,350,500,hand=(505,490),off_hand=(196,530),facing=facing)
            assert image.getpixel((505,490))[3] and image.getpixel((196,530))[3]
