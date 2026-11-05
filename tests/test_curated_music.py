import json
from pathlib import Path
import wave

import pytest

from shorts_editor.store import write_json
from yt_pipeline.assets import asset_record, register_asset
from yt_pipeline.core import Held, Workspace
from yt_pipeline.curated_music import install_music_catalog, music_catalog, select_genre_music


def installed_fixture(tmp_path, monkeypatch):
    ws = Workspace(tmp_path / 'pipeline')
    tracks = []
    state = {'version': 1, 'tracks': {}}
    assets = []
    for i in range(3):
        source = tmp_path / f'music-{i}.wav'
        with wave.open(str(source), 'wb') as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(8000)
            output.writeframes(bytes([i + 1, 1]) * 8000)
        asset = register_asset(ws, source, 'licensed_stock', {'license': 'Synthetic fixture only'}, test_only=i == 2)
        key = f'track-{i}'
        tracks.append({'key': key, 'title': key, 'artist': 'Fixture', 'genres': ['comedy'],
                       'sha256': asset['sha256'], 'priority': i + 1, 'fit_note': 'Fixture',
                       'popularity': {'status': 'unverified'}, 'dialogue_music_volume': .08,
                       'montage_music_volume': .4, 'edit_notes': 'Fixture'})
        state['tracks'][key] = {'asset_id': asset['id'], 'sha256': asset['sha256']}
        assets.append(asset)
    write_json(ws.root / 'curated-music-library.json', state)
    monkeypatch.setattr('yt_pipeline.curated_music.music_catalog', lambda: {'tracks': tracks, 'checked_on': '2026-11-05'})
    return ws, tracks, assets


def test_selection_avoids_recent_and_never_uses_test_only_track(tmp_path, monkeypatch):
    ws, tracks, assets = installed_fixture(tmp_path, monkeypatch)
    assert select_genre_music(ws, 'comedy')['id'] == assets[0]['id']
    job = ws.create('entertainment', {'music_id': assets[0]['id']})
    ws.update(job['id'], status='ready')
    assert select_genre_music(ws, 'comedy')['id'] == assets[1]['id']
    assert select_genre_music(ws, 'comedy', selection_key='same-key', avoid_recent=0) == select_genre_music(ws, 'comedy', selection_key='same-key', avoid_recent=0)
    for i in range(12):
        assert select_genre_music(ws, 'comedy', str(i))['id'] != assets[2]['id']


def test_modified_audio_is_excluded_instead_of_silently_selected(tmp_path, monkeypatch):
    ws, tracks, assets = installed_fixture(tmp_path, monkeypatch)
    Path(asset_record(ws, assets[0]['id'])['path']).write_bytes(b'changed')
    assert select_genre_music(ws, 'comedy')['id'] == assets[1]['id']
    Path(asset_record(ws, assets[1]['id'])['path']).write_bytes(b'changed too')
    with pytest.raises(Held, match='Install the permitted'):
        select_genre_music(ws, 'comedy')


def test_all_recent_options_choose_the_least_recent_genre_track(tmp_path, monkeypatch):
    ws, tracks, assets = installed_fixture(tmp_path, monkeypatch)
    for i in range(2):
        job = ws.create('entertainment', {'music_id': assets[i]['id']})
        ws.update(job['id'], status='ready')
        with ws.connect() as db:
            db.execute('UPDATE jobs SET created_at=? WHERE id=?', (f'2026-11-0{i+1}T00:00:00+00:00', job['id']))
    unrelated = ws.create('entertainment', {'music_id': 'another-genre-track'})
    ws.update(unrelated['id'], status='ready')
    assert select_genre_music(ws, 'comedy', avoid_recent=2)['id'] == assets[0]['id']


def test_selection_is_offline_and_empty_library_is_actionable(tmp_path, monkeypatch):
    ws = Workspace(tmp_path / 'pipeline')
    def forbidden(*args, **kwargs):
        raise AssertionError('Selection unexpectedly made a network call')
    monkeypatch.setattr('yt_pipeline.curated_music.fetch', forbidden)
    with pytest.raises(Held, match='Install the permitted'):
        select_genre_music(ws, 'mystery')
    with pytest.raises(ValueError):
        select_genre_music(ws, 'viral')
    with pytest.raises(ValueError):
        select_genre_music(ws, 'comedy', avoid_recent=True)


def test_install_refuses_changed_recording_before_registration(tmp_path, monkeypatch):
    ws = Workspace(tmp_path / 'pipeline')
    row = dict(music_catalog()['tracks'][0])
    row['sha256'] = '0' * 64
    monkeypatch.setattr('yt_pipeline.curated_music.music_catalog', lambda: {'tracks': [row], 'checked_on': '2026-11-05'})
    monkeypatch.setattr('yt_pipeline.curated_music.fetch', lambda *a, **kw: (b'changed recording', 'audio/mpeg', a[0]))
    with pytest.raises(Held, match='changed from the checked'):
        install_music_catalog(ws)
    assert not (ws.root / 'curated-music-library.json').exists()
    with pytest.raises(ValueError, match='reference-only'):
        install_music_catalog(ws, ['not-a-downloadable-track'])


def test_catalog_keeps_popularity_and_platform_references_out_of_rights():
    catalog = music_catalog()
    assert len(catalog['tracks']) == 14
    by_title = {t['title']: t for t in catalog['tracks']}
    familiar = by_title['Monkeys Spinning Monkeys']
    assert familiar['attribution_required'] and familiar['license'] == 'CC BY 4.0'
    assert familiar['popularity']['status'] == 'historical_platform_evidence'
    assert '2021-04-01' in familiar['popularity']['event_dates']
    assert all('download_url' not in ref and ref['bake_in_eligible'] is False for ref in catalog['platform_only_references'])
    assert not any(ref['title'] == track['title'] for ref in catalog['platform_only_references'] for track in catalog['tracks'])
    assert all(len(track['sha256']) == 64 and track['license_url'].startswith('https://') for track in catalog['tracks'])
