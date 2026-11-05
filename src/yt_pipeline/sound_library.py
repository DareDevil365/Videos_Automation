"""Original UI signals and separately permitted ambience for the local editor."""
from array import array
import hashlib
import json
import math
from pathlib import Path
import random
import subprocess
import wave

from shorts_editor.store import write_json
from .assets import asset_record, register_asset
from .core import Held, digest, file_hash, now
from .net import fetch


def sound_catalog():
    return json.loads(Path(__file__).with_name('sound_catalog.json').read_text(encoding='utf-8'))


def _state(workspace):
    path = workspace.root / 'sound-library.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'version': 1, 'items': {}}


def original_signal(item, rate=24000):
    """Synthesize bounded non-imitative signals, never an app's sampled chime."""
    recipe = item['recipe']
    seconds = recipe['seconds']
    rng = random.Random(item['key'])
    result = array('h')
    smooth = 0
    phase = 0
    for i in range(round(seconds * rate)):
        t = i / rate
        progress = t / seconds
        envelope = math.sin(math.pi * progress) ** 2
        frequency = recipe['frequency'] + (recipe['end_frequency'] - recipe['frequency']) * progress
        phase += 2 * math.pi * frequency / rate
        kind = recipe['type']
        if kind == 'double':
            half = seconds / 2
            local = (t % half) / half
            envelope = math.sin(math.pi * local) ** 3
            frequency = recipe['frequency'] if t < half else recipe['end_frequency']
            value = math.sin(2 * math.pi * frequency * t)
        elif kind in ('whoosh', 'glitch'):
            smooth = .80 * smooth + .20 * rng.uniform(-1, 1)
            value = smooth * 2.8
            if kind == 'glitch':
                value *= .5 + .5 * math.sin(2 * math.pi * 31 * t)
        elif kind == 'impact':
            value = math.sin(phase) * math.exp(-progress * 4)
        else:
            value = (math.sin(phase) + .10 * math.sin(phase * 2)) / 1.1
            envelope *= math.exp(-progress * 2)
        result.append(round(max(-.95, min(.95, value * envelope * recipe['peak'])) * 32767))
    return result


def install_sound_library(workspace, include_ambience=True, keys=None):
    """Explicitly prepare original WAVs and pinned licensed ambience downloads."""
    catalog = sound_catalog()
    items = [r for r in catalog['items'] if include_ambience or r['source_kind'] == 'original_software_sfx']
    if keys is not None:
        selected = set(keys)
        items = [r for r in items if r['key'] in selected]
        if selected != {r['key'] for r in items}:
            raise ValueError('Choose available sound catalog keys.')
    folder = workspace.root / 'assets' / 'sound-library'
    folder.mkdir(parents=True, exist_ok=True)
    state = _state(workspace)
    results = []
    snapshots = {}
    for item in items:
        signature = digest(item)
        old = state['items'].get(item['key'])
        if old:
            asset = asset_record(workspace, old['asset_id'])
            if old['definition_sha256'] != signature or old['sha256'] != asset['sha256']:
                raise Held('sound_library_changed', 'A sound definition or recording changed; install a reviewed new catalog version.')
            results.append({'key': item['key'], 'asset_id': asset['id'], 'reused': True})
            continue
        path = folder / (item['key'] + '.wav')
        if item['source_kind'] == 'original_software_sfx':
            pcm = original_signal(item)
            with wave.open(str(path), 'wb') as output:
                output.setnchannels(1)
                output.setsampwidth(2)
                output.setframerate(24000)
                output.writeframes(pcm.tobytes())
            source_type = 'original_graphic'
            evidence = {'generator': item['generator'], 'media_type': 'audio', 'recipe': item['recipe'],
                        'rights': item['license'], 'note': 'Original deterministic signal; existing original_graphic source bucket covers software-made assets. No third-party or trademark sound sampled.'}
        else:
            source_type = 'licensed_stock'
            if not item['download_url'].startswith('https://assets.mixkit.co/active_storage/sfx/'):
                raise Held('sound_download_host', 'Ambience download must use the checked rights-holder media URL.')
            urls = [item['source_url'], item['source_download_page'], item['license_terms_url']]
            for url in urls:
                if url not in snapshots:
                    body, _, _ = fetch(url, maximum=6_000_000)
                    saved = folder / (digest(url)[:16] + '.source')
                    saved.write_bytes(body)
                    snapshots[url] = {'url': url, 'path': str(saved), 'sha256': file_hash(saved)}
            if not path.exists():
                body, _, _ = fetch(item['download_url'], maximum=40_000_000)
                if hashlib.sha256(body).hexdigest() != item['sha256']:
                    raise Held('sound_source_changed', 'The ambience recording changed from the checked source.')
                temporary = path.with_suffix('.partial.wav')
                temporary.write_bytes(body)
                temporary.replace(path)
            if file_hash(path) != item['sha256']:
                raise Held('sound_source_changed', 'The local ambience recording differs from the checked source.')
            evidence = {k: item[k] for k in ('title', 'source_url', 'source_download_page', 'download_url', 'license', 'license_url', 'license_terms_url')}
            evidence['snapshots'] = [snapshots[url] for url in urls]
        evidence.update(catalog_key=item['key'], checked_at=now())
        asset = register_asset(workspace, path, source_type, evidence, attribution=item['attribution'])
        if not asset['has_audio']:
            raise Held('sound_audio', 'The registered sound has no audio stream.')
        state['items'][item['key']] = {'asset_id': asset['id'], 'sha256': asset['sha256'], 'definition_sha256': signature}
        write_json(workspace.root / 'sound-library.json', state)
        results.append({'key': item['key'], 'asset_id': asset['id'], 'reused': False})
    return {'installed': results, 'catalog_checked_on': catalog['checked_on']}


def select_sound(workspace, category, selection_key='', genre=None, avoid_asset_ids=()):
    """Offline eligible sound selection; silence is a timeline rule, not an asset."""
    catalog = sound_catalog()
    if category not in {r['category'] for r in catalog['items']}:
        raise ValueError('Choose a known sound category; blackout/typing do not generate a sound.')
    installed = _state(workspace)['items']
    candidates = []
    for item in catalog['items']:
        if item['category'] != category or (genre and genre not in item['genres']):
            continue
        ref = installed.get(item['key'])
        if not ref or ref['definition_sha256'] != digest(item):
            continue
        try:
            asset = asset_record(workspace, ref['asset_id'])
        except Held:
            continue
        if asset['has_audio'] and not asset.get('test_only') and asset['sha256'] == ref['sha256']:
            candidates.append((item, asset))
    if not candidates:
        raise Held('sound_library_empty', 'Install an eligible sound for this category before editing.')
    fresh = [pair for pair in candidates if pair[1]['id'] not in avoid_asset_ids]
    pool = sorted(fresh or candidates, key=lambda pair: pair[0]['key'])
    index = int(digest([category, str(selection_key)])[:12], 16) % len(pool) if selection_key else 0
    item, asset = pool[index]
    return {**asset, 'sound': {k: item[k] for k in ('key', 'title', 'category', 'source_kind', 'recommended_gain', 'maximum_gain', 'use_note', 'loop_allowed')}}


def mix_sound_events(workspace, samples, rate, events, silence=(), speech_ranges=()):
    """Mix explicit events into mono PCM, duck ambience and preserve hard silence.

    An event supplies category/start and optional genre, selection_key, gain,
    duration (ambience only). No automatic environment or reveal is invented.
    The caller should retain the returned resolved asset IDs with its checkpoint.
    """
    if type(rate) is not int or not 8000 <= rate <= 192000 or not isinstance(samples, array) or samples.typecode != 'h':
        raise Held('sound_events', 'Mix into mono 16-bit PCM at a supported sample rate.')
    if len(events) > 48:
        raise Held('sound_events', 'Keep an episode within 48 explicit sound events.')
    duration = len(samples) / rate
    for start, end in [*silence, *speech_ranges]:
        if not all(math.isfinite(v) for v in (start, end)) or not 0 <= start < end <= duration + .001:
            raise Held('sound_events', 'Audio intervals must fit the actual timeline.')
    result = []
    for event in events:
        asset = select_sound(workspace, event['category'], event.get('selection_key', ''), event.get('genre'))
        start = event['start']
        gain = event.get('gain', asset['sound']['recommended_gain'])
        if type(start) not in (int, float) or not math.isfinite(start) or start < 0:
            raise Held('sound_events', 'Effect start must be a finite non-negative timestamp.')
        if type(gain) not in (int, float) or not math.isfinite(gain) or not 0 <= gain <= asset['sound']['maximum_gain']:
            raise Held('sound_events', 'Effect gain is outside this sound preset limit.')
        seconds = event.get('duration', asset['duration'])
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or not 0 < seconds <= asset['duration'] + .001:
            raise Held('sound_events', 'Sound duration must fit its actual source; seamless looping is not assumed.')
        if 'duration' in event and not event['category'].startswith('ambience_') and abs(seconds - asset['duration']) > .001:
            raise Held('sound_events', 'Do not truncate an effect; select an appropriate bounded cue.')
        if start + seconds > duration + .001:
            raise Held('sound_events', 'The complete sound must fit the episode timeline.')
        decoded = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', asset['path'], '-t', str(seconds),
                                  '-ac', '1', '-ar', str(rate), '-f', 's16le', '-'], capture_output=True, timeout=45)
        if decoded.returncode:
            raise Held('sound_decode', 'The registered effect could not be decoded.')
        pcm = array('h')
        pcm.frombytes(decoded.stdout)
        first = round(start * rate)
        for i, value in enumerate(pcm):
            target = first + i
            if target >= len(samples):
                break
            t = target / rate
            envelope = min(1, i / max(1, rate * .015), (len(pcm) - 1 - i) / max(1, rate * .04))
            if event['category'].startswith('ambience_'):
                envelope *= min(1, i / max(1, rate * .25), (len(pcm) - 1 - i) / max(1, rate * .35))
                for a, b in speech_ranges:
                    if a - .10 <= t <= b + .15:
                        duck = min(1, max(0, (t - a + .10) / .10), max(0, (b + .15 - t) / .15))
                        envelope *= 1 - .65 * duck
            samples[target] = max(-30000, min(30000, samples[target] + round(value * gain * envelope)))
        result.append({'category': event['category'], 'asset_id': asset['id'], 'source_sha256': asset['sha256'],
                       'start': start, 'end': start + seconds, 'gain': gain, 'attribution': asset['attribution']})
    # Last stage wins even when a cue overlaps an intentional blackout.
    for start, end in silence:
        samples[round(start * rate):round(end * rate)] = array('h', [0]) * (round(end * rate) - round(start * rate))
    return {'effects': result, 'blackout_silence': True, 'typing_loops': False}
