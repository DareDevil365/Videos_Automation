"""Validated speech delivery separate from immutable script words/captions."""
import math
import re

from .core import Held


SEGMENT_SCHEMA = {'type': 'array', 'maxItems': 8, 'items': {'type': 'object', 'properties': {
    'text': {'type': 'string'}, 'pause_after': {'type': 'number', 'minimum': 0, 'maximum': 1.2},
    'speed': {'type': 'number', 'minimum': .9, 'maximum': 1.25}},
    'required': ['text', 'pause_after', 'speed'], 'additionalProperties': False}}


def number(value, minimum, maximum, code='speech_delivery'):
    if type(value) not in (int, float) or not math.isfinite(value) or not minimum <= value <= maximum:
        raise Held(code, f'Value must be finite and between {minimum} and {maximum}.')
    return float(value)


def speech_segments(text, scene=None):
    raw = (scene or {}).get('speech_segments', [])
    if not isinstance(raw, list) or len(raw) > 8:
        raise Held('speech_delivery', 'Use at most eight speech segments per unit.')
    if not raw:
        return [{'text': text, 'pause_after': 0., 'speed': 1.}]
    result = []
    for row in raw:
        if not isinstance(row, dict) or set(row) != {'text', 'pause_after', 'speed'}:
            raise Held('speech_delivery', 'Speech segments need exact text, pause_after and speed.')
        part = row['text']
        if not isinstance(part, str) or not part.strip() or re.search(r'\[(?:P{1,3}|FAST|NORMAL)\]', part):
            raise Held('speech_delivery', 'Speech segment text must contain dialogue, without control tags.')
        result.append({'text': part, 'pause_after': number(row['pause_after'], 0, 1.2),
                       'speed': number(row['speed'], .9, 1.25)})
    if ' '.join(' '.join(s['text'].split()) for s in result) != ' '.join(text.split()):
        raise Held('speech_delivery', 'Speech segments must preserve every script word, punctuation and order.')
    if result[-1]['pause_after'] != 0 or sum(s['pause_after'] for s in result) > 2.4:
        raise Held('speech_delivery', 'Use internal pauses totaling at most 2.4 seconds; the final segment pause is zero.')
    return result
