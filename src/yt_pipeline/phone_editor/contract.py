"""Finite story-data vocabulary; no generated code, URLs or timing commands."""
from copy import deepcopy
import re

from ..core import Held

EVENT_SECONDS = {'switch': .35, 'low_battery': 1.2, 'glitch': .35,
                 'blackout': 1.5, 'time_jump': 1.1, 'notification': 1.25}
THEMES = ('light', 'dark', 'rose', 'sage')


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


PHONE_SCHEMA = obj({
    'pov': {'type': 'string'},
    'contacts': {'type': 'array', 'minItems': 1, 'maxItems': 5, 'items': obj({
        'id': {'type': 'string'}, 'name': {'type': 'string'}})},
    'threads': {'type': 'array', 'minItems': 1, 'maxItems': 5, 'items': obj({
        'id': {'type': 'string'}, 'contact_id': {'type': 'string'},
        'theme': {'type': 'string', 'enum': list(THEMES)}})},
    'beats': {'type': 'array', 'minItems': 1, 'maxItems': 28, 'items': obj({
        'unit_id': {'type': 'string'}, 'thread_id': {'type': 'string'},
        'time': {'type': 'string'},
        'events': {'type': 'array', 'maxItems': 5, 'items': {'type': 'string', 'enum': list(EVENT_SECONDS)}}})}})


def validate_phone_story(value, units):
    def fail(message): raise Held('phone_story', message)
    def text(item, maximum=40):
        return isinstance(item, str) and bool(item.strip()) and len(item) <= maximum
    def safe_id(item): return text(item) and re.fullmatch(r'[A-Za-z0-9_-]+', item)
    if not isinstance(value, dict) or set(value) != set(PHONE_SCHEMA['properties']):
        fail('Phone story needs pov, contacts, threads and one beat per message.')
    if not text(value['pov']) or value['pov'].lower() == 'narrator': fail('Choose one actual phone owner as pov.')
    contacts = value['contacts']; threads = value['threads']; beats = value['beats']
    if not isinstance(contacts, list) or not 1 <= len(contacts) <= 5: fail('Use 1-5 contacts.')
    contact_map = {}
    names = {value['pov']}
    for contact in contacts:
        if (not isinstance(contact, dict) or set(contact) != {'id', 'name'} or
                not safe_id(contact['id']) or not text(contact['name']) or
                contact['id'] in contact_map or contact['name'] in names or contact['name'].lower() == 'narrator'):
            fail('Contact IDs and names must be unique; no narrator or duplicate phone owner.')
        contact_map[contact['id']] = contact; names.add(contact['name'])
    if not isinstance(threads, list) or not 1 <= len(threads) <= 5: fail('Use 1-5 conversations.')
    thread_map = {}
    for thread in threads:
        if (not isinstance(thread, dict) or set(thread) != {'id', 'contact_id', 'theme'} or
                not safe_id(thread['id']) or thread['id'] in thread_map or
                not isinstance(thread['contact_id'],str) or thread['contact_id'] not in contact_map or thread['theme'] not in THEMES):
            fail('Each conversation needs a unique ID, known contact and supported theme.')
        thread_map[thread['id']] = thread
    if not isinstance(beats, list) or len(beats) != len(units): fail('Map every message to exactly one ordered phone beat.')
    previous_minutes = None; interruption_planted=False
    for beat, unit in zip(beats, units):
        if (not isinstance(beat, dict) or set(beat) != {'unit_id', 'thread_id', 'time', 'events'} or
                beat['unit_id'] != unit['id'] or not isinstance(beat['thread_id'],str) or beat['thread_id'] not in thread_map):
            fail('Phone beats must reference actual message IDs in order and known conversations.')
        if not isinstance(beat['time'], str) or not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', beat['time']):
            fail('Use explicit fictional 24-hour HH:MM story timestamps.')
        minutes = int(beat['time'][:2])*60+int(beat['time'][3:])
        if previous_minutes is not None and minutes < previous_minutes: fail('Story time cannot run backward; keep this short story within one day.')
        events = beat['events']
        if not isinstance(events, list) or len(events) > 5 or any(not isinstance(e,str) or e not in EVENT_SECONDS for e in events) or len(events) != len(set(events)):
            fail('Choose distinct supported story events; software sets their duration.')
        if 'notification' in events and unit['speaker'] == value['pov']: fail('Incoming notifications must come from a contact.')
        if 'time_jump' in events and (previous_minutes is None or minutes <= previous_minutes): fail('A time jump needs a later story timestamp.')
        for event in events:
            if event in ('low_battery','glitch'):interruption_planted=True
            if event=='blackout':
                if not interruption_planted:fail('Plant a battery or glitch interruption before a blackout.')
                interruption_planted=False
        if 'blackout' in events and 'time_jump' in events and events.index('blackout') > events.index('time_jump'):
            fail('Show the blackout before advancing story time.')
        contact = contact_map[thread_map[beat['thread_id']]['contact_id']]
        if unit['speaker'] not in (value['pov'], contact['name']): fail('A private conversation may only contain its contact and the phone owner.')
        previous_minutes = minutes
    return deepcopy(value)


def compile_beats(script):
    story = validate_phone_story(script['phone_story'], script['units'])
    result = []; previous = None
    for beat in story['beats']:
        events = list(beat['events'])
        if previous is not None and previous != beat['thread_id'] and 'switch' not in events: events.insert(0, 'switch')
        cursor = 0; timeline = []
        for event in events:
            timeline.append({'type': event, 'start': cursor, 'end': cursor+EVENT_SECONDS[event]})
            cursor += EVENT_SECONDS[event]
        result.append({**beat, 'events': timeline, 'prefix_seconds': cursor})
        previous = beat['thread_id']
    return result
