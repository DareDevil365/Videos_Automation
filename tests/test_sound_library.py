from array import array
import json
from pathlib import Path
import wave

import pytest

from shorts_editor.store import write_json
from yt_pipeline.assets import asset_record, register_asset
from yt_pipeline.core import Held, Workspace, digest
from yt_pipeline.sound_library import install_sound_library, mix_sound_events, original_signal, select_sound, sound_catalog


@pytest.fixture
def ui_library(tmp_path, monkeypatch):
    ws = Workspace(tmp_path / 'pipeline')
    def forbidden(*args, **kwargs):
        raise AssertionError('Original UI signals must not fetch external audio')
    monkeypatch.setattr('yt_pipeline.sound_library.fetch', forbidden)
    install_sound_library(ws, include_ambience=False)
    return ws


def test_originals_install_offline_and_reuse_exact_recordings(ui_library):
    result = install_sound_library(ui_library, include_ambience=False)
    assert len(result['installed']) == 12 and all(r['reused'] for r in result['installed'])
    for item in sound_catalog()['items']:
        if item['source_kind'] != 'original_software_sfx':
            continue
        pcm = original_signal(item)
        assert pcm == original_signal(item)
        assert pcm[0] == 0 and abs(pcm[-1]) <= 1
        assert 10 < max(abs(v) for v in pcm) < 5000


def test_variant_selection_avoids_previous_and_checks_integrity(ui_library):
    first = select_sound(ui_library, 'message_incoming')
    second = select_sound(ui_library, 'message_incoming', avoid_asset_ids=[first['id']])
    assert first['id'] != second['id']
    assert select_sound(ui_library, 'message_incoming', selection_key='same')['id'] == select_sound(ui_library, 'message_incoming', selection_key='same')['id']
    Path(first['path']).write_bytes(b'tampered')
    assert select_sound(ui_library, 'message_incoming')['id'] == second['id']
    with pytest.raises(Held, match='Install an eligible sound'):
        select_sound(ui_library, 'impact', genre='comedy')
    with pytest.raises(ValueError):
        select_sound(ui_library, 'typing')


def test_explicit_effect_cannot_break_blackout_silence(ui_library):
    rate = 24000
    samples = array('h', [300]) * (rate * 2)
    result = mix_sound_events(ui_library, samples, rate,
        [{'category': 'reveal', 'start': .3}], silence=[(.4, .8)])
    assert result['effects'][0]['category'] == 'reveal'
    assert max(samples[round(.4 * rate):round(.8 * rate)]) == 0
    assert min(samples[round(.4 * rate):round(.8 * rate)]) == 0
    assert max(samples[round(.31 * rate):round(.39 * rate)]) > 300


def test_effects_hold_invalid_gain_timing_and_truncation(ui_library):
    rate = 24000
    for event in [{'category': 'glitch', 'start': float('nan')},
                  {'category': 'glitch', 'start': 1.9},
                  {'category': 'glitch', 'start': .2, 'gain': 9},
                  {'category': 'glitch', 'start': .2, 'duration': .05}]:
        with pytest.raises(Held):
            mix_sound_events(ui_library, array('h', [0]) * (rate * 2), rate, [event])


def test_ambience_ducks_for_speech_and_has_no_assumed_loop(tmp_path, monkeypatch):
    ws = Workspace(tmp_path / 'pipeline')
    source = tmp_path / 'fixture.wav'
    with wave.open(str(source), 'wb') as output:
        output.setnchannels(1); output.setsampwidth(2); output.setframerate(24000)
        output.writeframes((array('h', [10000]) * 48000).tobytes())
    asset = register_asset(ws, source, 'licensed_stock', {'note': 'Synthetic unit fixture, not a real field recording'})
    item = {'key': 'fixture', 'title': 'Fixture', 'category': 'ambience_rain', 'source_kind': 'licensed_stock_sfx',
            'genres': ['story'], 'recommended_gain': .1, 'maximum_gain': .2, 'use_note': 'Fixture', 'loop_allowed': False}
    monkeypatch.setattr('yt_pipeline.sound_library.sound_catalog', lambda: {'items': [item]})
    write_json(ws.root / 'sound-library.json', {'items': {'fixture': {'asset_id': asset['id'], 'sha256': asset['sha256'], 'definition_sha256': digest(item)}}})
    samples = array('h', [0]) * 48000
    mix_sound_events(ws, samples, 24000, [{'category': 'ambience_rain', 'start': 0}], speech_ranges=[(.8, 1.1)])
    assert 250 < samples[24000] < 400
    assert 900 < samples[12000] < 1100
    with pytest.raises(Held, match='actual source'):
        mix_sound_events(ws, array('h', [0]) * 72000, 24000, [{'category': 'ambience_rain', 'start': 0, 'duration': 3}])


def test_licensed_ambience_is_separate_from_original_signal_claims():
    data = sound_catalog()
    assert len(data['items']) == 16
    original = [r for r in data['items'] if r['source_kind'] == 'original_software_sfx']
    sourced = [r for r in data['items'] if r['source_kind'] == 'licensed_stock_sfx']
    assert len(original) == 12 and len(sourced) == 4
    assert all('recipe' in r and 'download_url' not in r for r in original)
    assert all(r['license'] == 'Mixkit Sound Effects Free License' and len(r['sha256']) == 64 for r in sourced)
    assert all(r['loop_allowed'] is False for r in sourced)
