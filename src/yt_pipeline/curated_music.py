"""Versioned permitted tracks, explicit installation and genre-aware rotation.

Music fit is an editorial hypothesis. Historical popularity never grants rights
or predicts performance. Selection is local; downloading is explicitly requested.
"""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from shorts_editor.store import write_json
from .assets import asset_record, register_asset
from .core import Held, digest, file_hash, now
from .music_agent import register_music
from .net import fetch


GENRES = ('comedy', 'mystery', 'thriller', 'story', 'cinematic', 'aura')
CATEGORY = {'comedy': 'cringe', 'mystery': 'horror', 'thriller': 'horror',
            'story': 'storytime', 'cinematic': 'storytime', 'aura': 'aura'}


def music_catalog():
    return json.loads(Path(__file__).with_name('music_catalog.json').read_text(encoding='utf-8'))


def _installed(workspace):
    path = workspace.root / 'curated-music-library.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'version': 1, 'tracks': {}}


def install_music_catalog(workspace, keys=None):
    """Download selected pinned recordings from official sources and register evidence.

    Existing intact registrations are reused. Source/license snapshots and audio
    remain private local runtime files. No platform-only reference is downloadable.
    """
    catalog = music_catalog()
    selected = set(keys) if keys is not None else {t['key'] for t in catalog['tracks']}
    tracks = [t for t in catalog['tracks'] if t['key'] in selected]
    if selected != {t['key'] for t in tracks}:
        raise ValueError('Choose known downloadable catalog keys, not reference-only songs.')
    folder = workspace.root / 'assets' / 'curated-music'
    folder.mkdir(parents=True, exist_ok=True)
    state = _installed(workspace)
    snapshots = {}
    results = []
    for track in tracks:
        previous = state['tracks'].get(track['key'])
        if previous:
            asset = asset_record(workspace, previous['asset_id'])
            if asset['sha256'] != track['sha256']:
                raise Held('music_catalog_changed', 'An installed track differs from this curated recording. Recheck its provenance.')
            results.append({'key': track['key'], 'asset_id': asset['id'], 'reused': True})
            continue
        urls = dict.fromkeys([track['source_url'], track['source_metadata_url'], track['license_terms_url']])
        evidence_files = []
        for url in urls:
            if url not in snapshots:
                body, _, _ = fetch(url, maximum=6_000_000)
                path = folder / (digest(url)[:16] + '.source')
                path.write_bytes(body)
                snapshots[url] = {'url': url, 'path': str(path), 'sha256': file_hash(path)}
            evidence_files.append(snapshots[url])
        host = urlparse(track['download_url']).hostname
        if host not in ('assets.mixkit.co', 'incompetech.com'):
            raise Held('music_download_host', 'Curated downloads must use the recorded rights-holder media host.')
        path = folder / (track['key'] + '.mp3')
        if not path.exists():
            body, _, _ = fetch(track['download_url'], maximum=30_000_000)
            if hashlib.sha256(body).hexdigest() != track['sha256']:
                raise Held('music_catalog_changed', 'Downloaded audio changed from the checked recording; verify the new source before using it.')
            temporary = path.with_suffix('.partial.mp3')
            temporary.write_bytes(body)
            temporary.replace(path)
        if file_hash(path) != track['sha256']:
            raise Held('music_catalog_changed', 'The local soundtrack differs from its checked recording.')
        evidence = {k: track[k] for k in ('key', 'title', 'artist', 'source_url', 'download_url', 'license', 'license_url', 'license_terms_url', 'restrictions')}
        evidence.update(catalog_checked_on=catalog['checked_on'], checked_at=now(), snapshots=evidence_files)
        asset = register_asset(workspace, path, 'licensed_creator' if track['attribution_required'] else 'licensed_stock',
                               evidence, attribution=track['attribution'])
        if not asset['has_audio']:
            raise Held('music_audio', 'A curated source did not contain audio.')
        register_music(workspace, asset['id'], sorted({CATEGORY[g] for g in track['genres']}))
        state['tracks'][track['key']] = {'asset_id': asset['id'], 'sha256': asset['sha256']}
        state.update(catalog_checked_on=catalog['checked_on'])
        write_json(workspace.root / 'curated-music-library.json', state)
        results.append({'key': track['key'], 'asset_id': asset['id'], 'reused': False})
    return {'installed': results, 'catalog_checked_on': catalog['checked_on']}


def select_genre_music(workspace, genre, selection_key='', avoid_recent=3, download_missing=False):
    """Return an eligible registered asset plus fit metadata, without model calls.

    A stable job ID makes a retry choose the same track. Recent ready/published
    jobs are avoided when alternatives exist. Callers retain explicit music_id
    overrides; this function never overwrites requests or creates an upload.
    """
    if genre not in GENRES:
        raise ValueError('Choose comedy, mystery, thriller, story, cinematic or aura.')
    if type(avoid_recent) is not int or not 0 <= avoid_recent <= 100:
        raise ValueError('avoid_recent must be an integer from 0 to 100.')
    installed = _installed(workspace)['tracks']
    matching = [t for t in music_catalog()['tracks'] if genre in t['genres']]
    if download_missing:
        install_music_catalog(workspace, [t['key'] for t in matching if t['key'] not in installed])
        installed = _installed(workspace)['tracks']
    candidates = []
    for track in matching:
        item = installed.get(track['key'])
        if not item:
            continue
        # An eligible registration is checked again on every selection; stale or
        # tampered media must never be silently chosen because its mood fits.
        try:
            asset = asset_record(workspace, item['asset_id'])
        except Held:
            continue
        if asset['sha256'] == track['sha256'] and asset['has_audio'] and not asset.get('test_only'):
            candidates.append((track, asset))
    if not candidates:
        raise Held('music_library_empty', 'Install the permitted genre music catalog before production, or select an eligible music_id.')
    recent = []
    candidate_ids = {asset['id'] for _, asset in candidates}
    if avoid_recent:
        for job in sorted(workspace.jobs(10000), key=lambda j: j['created_at'], reverse=True):
            ref = job['request'].get('music_id')
            if ref in candidate_ids and job['status'] in ('ready', 'processing', 'uploaded_private', 'scheduled', 'published'):
                recent.append(ref)
                if len(recent) >= avoid_recent:
                    break
    fresh = [pair for pair in candidates if pair[1]['id'] not in recent]
    if not fresh and recent:
        # If every option was used recently, prefer the least recently heard
        # rather than arbitrarily repeating the immediately preceding track.
        oldest = max(recent.index(asset['id']) for _, asset in candidates)
        fresh = [pair for pair in candidates if recent.index(pair[1]['id']) == oldest]
    pool = sorted(fresh or candidates, key=lambda pair: (pair[0]['priority'], pair[0]['key']))
    index = int(digest([genre, str(selection_key)])[:12], 16) % len(pool) if selection_key else 0
    track, asset = pool[index]
    return {**asset, 'curated_music': {k: track[k] for k in ('key', 'title', 'artist', 'genres', 'fit_note',
            'popularity', 'dialogue_music_volume', 'montage_music_volume', 'edit_notes')}}
