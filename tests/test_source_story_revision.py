import json
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest

from yt_pipeline.core import Held
from yt_pipeline.playbooks import get_playbook
from yt_pipeline.source_delivery import delivery_for
from yt_pipeline.speech_delivery import speech_segments


ROOT=Path(__file__).resolve().parents[1]


def test_measured_story_window_is_opt_in_and_does_not_change_legacy_rules():
    original=get_playbook('comic_lore')['seconds']
    rule=get_playbook('comic_lore',{'source_duration':[42,50]})
    assert rule['seconds']==[42,50] and rule['words'][1]>=178
    assert 'why each transition happens' in rule['writing']
    assert get_playbook('comic_lore')['seconds']==original
    assert get_playbook('comic_lore',{'source_duration':[75,115]})['words'][1]>=268
    for invalid in ([50,42],[42,float('inf')],[True,50],'42-50'):
        with pytest.raises(Held):get_playbook('comic_lore',{'source_duration':invalid})


def test_faster_delivery_keeps_complete_words_and_stays_bounded():
    unit={'id':'u1','text':'The Amazing Spider-Man, issue thirty-three.'}
    scene=delivery_for(unit,{'source_delivery':{'tight_speech':True,'speed':1.24}},.05)
    parts=speech_segments(unit['text'],scene)
    assert parts[0]['text']==unit['text'] and parts[0]['speed']==1.24
    with pytest.raises(Held):delivery_for(unit,{'source_delivery':{'speed':1.26}},.05)
    parts[0]['speed']=1.26
    with pytest.raises(Held):speech_segments(unit['text'],{'speech_segments':parts})


def test_library_lookup_works_offline_from_another_directory(tmp_path):
    result=subprocess.run([sys.executable,str(ROOT/'tools/query_comic_library.py'),'Spider Man','--ready-only'],
                          cwd=tmp_path,capture_output=True,text=True,check=True,encoding='utf-8')
    matches=json.loads(result.stdout)['matches']
    rescue=next(row for row in matches if row['id']=='spider-man-last-lift')
    assert rescue['packet_status']=='reviewed_claim_scope'
    assert rescue['claims'] and rescue['sources']
    assert all(row['packet_status']=='reviewed_claim_scope' for row in matches)


def test_library_accepts_checkout_line_endings_but_not_changed_fact():
    spec=importlib.util.spec_from_file_location('comic_library',ROOT/'tools/query_comic_library.py')
    library=importlib.util.module_from_spec(spec);spec.loader.exec_module(library)
    reviewed=b'{"fact":"Peter escaped."}\r\n'
    review={'supported':True,'brief_sha256':hashlib.sha256(reviewed).hexdigest()}
    assert library.review_match(reviewed,review)=='exact'
    assert library.review_match(reviewed.replace(b'\r\n',b'\n'),review)=='line_endings_only'
    assert library.review_match(reviewed.replace(b'escaped',b'died'),review) is None
    assert library.review_match(reviewed,{**review,'supported':False}) is None
