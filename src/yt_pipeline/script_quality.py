"""Format-aware hook metadata and exact-text editorial checks; no extra writer call."""
from copy import deepcopy
import re

from .core import Held


HOOK_TYPES = ['visible_contrast', 'small_live_test', 'mistake_then_fix', 'story_reversal',
              'unfinished_object', 'narrow_promise', 'surprising_specific', 'viewer_question']
_PREAMBLE = re.compile(r"^(?:have you ever(?:\s|$)|ever wondered(?:\s|$)|in this video(?:\s|$)|"
                       r"welcome back(?:\s|$)|hey (?:guys|everyone|folks)(?:\s|[!,]|$))", re.I)
_MARKERS = re.compile(r'\[(?:P{1,3}|FAST|NORMAL)\]')


def validate_hook(script, playbook=None, strict=False):
    if not script.get('units'):
        raise Held('playbook_hook', 'A hook needs an actual opening unit.')
    text = script['units'][0]['text'].strip()
    if _MARKERS.search(' '.join(u['text'] for u in script['units'])):
        raise Held('playbook_hook', 'Keep speech control tags out of dialogue; use director speech_segments.')
    if script['format'] in ('clip', 'aura'):
        return  # Clip titles are metadata; aura has short caption-led hooks, not TTS.
    if script['hook'].strip() != text:
        raise Held('playbook_hook', 'The hook must be the exact first spoken unit.')
    if strict:
        maximum = 14 if playbook == 'cutout_ensemble' else 18
        if len(text.split()) > maximum or _PREAMBLE.match(text):
            raise Held('playbook_hook', f'Open on the specific conflict/question/result, without a greeting or preamble; at most {maximum} words.')
    return {'first_line': text, 'policy': 'specific_opening_v1' if strict else 'structural'}


def hook_envelope(script_schema):
    string = {'type': 'string'}
    option = {'type': 'object', 'properties': {
        'type': {'type': 'string', 'enum': HOOK_TYPES}, 'first_line': string,
        'first_caption': string, 'first_frame': string},
        'required': ['type', 'first_line', 'first_caption', 'first_frame'], 'additionalProperties': False}
    return {'type': 'object', 'properties': {'script': deepcopy(script_schema),
        'hook_options': {'type': 'array', 'minItems': 3, 'maxItems': 3, 'items': option},
        'selected_hook_index': {'type': 'integer', 'minimum': 0, 'maximum': 2}},
        'required': ['script', 'hook_options', 'selected_hook_index'], 'additionalProperties': False}


def unpack_hooks(raw, playbook=None):
    if not isinstance(raw, dict) or set(raw) != {'script', 'hook_options', 'selected_hook_index'}:
        raise Held('playbook_hook', 'Return the script, three hook_options and selected_hook_index together.')
    options = raw['hook_options']; index = raw['selected_hook_index']
    if not isinstance(options, list) or len(options) != 3 or type(index) is not int or not 0 <= index < 3:
        raise Held('playbook_hook', 'Choose one of exactly three hook options; never clamp an invalid index.')
    kinds = set()
    maximum = 14 if playbook == 'cutout_ensemble' else 18
    for index_option,option in enumerate(options):
        if not isinstance(option, dict) or set(option) != {'type', 'first_line', 'first_caption', 'first_frame'}:
            raise Held('playbook_hook', 'A hook option needs its type, spoken line, caption and first-frame intent.')
        if option['type'] not in HOOK_TYPES:
            raise Held('playbook_hook', 'Unknown hook type.')
        kinds.add(option['type'])
        for key, limit in (('first_line', 350), ('first_caption', 110), ('first_frame', 500)):
            value = option[key]
            if not isinstance(value, str) or not value.strip() or len(value) > limit or _MARKERS.search(value):
                raise Held('playbook_hook', 'Hook option text must be nonempty, bounded and free of speech tags.')
        if len(option['first_line'].split()) > maximum or _PREAMBLE.match(option['first_line'].strip()):
            raise Held('playbook_hook', f'Hook option {index_option}: {len(option["first_line"].split())} spoken words; maximum {maximum}; greetings and generic preambles are forbidden for every candidate.')
        if len(option['first_caption'].split()) > 12:
            raise Held('playbook_hook', f'Hook option {index_option}: {len(option["first_caption"].split())} caption words; maximum 12.')
    if len(kinds) != 3 or len({o['first_line'].casefold().strip() for o in options}) != 3:
        raise Held('playbook_hook', 'Use three distinct hook types and three different spoken lines. Returned types: '+', '.join(o['type'] for o in options)+'.')
    script = raw['script']; chosen = options[index]
    if not isinstance(script, dict) or not isinstance(script.get('units'), list) or not script['units'] or not isinstance(script['units'][0], dict):
        raise Held('playbook_hook', 'The selected hook needs an actual script opening.')
    opening = script['units'][0]
    if script.get('format') in ('chat','cutout') and chosen['first_caption']!=chosen['first_line']:
        raise Held('playbook_hook','Dialogue hooks display the actual spoken words, not a substituted summary caption.')
    if script.get('hook') != chosen['first_line'] or opening.get('text') != chosen['first_line'] or opening.get('onscreen') != chosen['first_caption']:
        raise Held('playbook_hook', 'Use the selected spoken line and caption verbatim in the actual first unit.')
    return script, {'options': options, 'selected_index': index, 'selected': chosen,
                    'method': 'same writing call', 'active': True,
                    'limits': 'First-frame intent is a plan; actual rendered frames still require review.'}


REVIEW_SCHEMA = {'type': 'object', 'properties': {
    **{k: {'type': 'boolean'} for k in ('passes', 'hook_honest', 'hook_specific', 'continuity_consistent')},
    **{k: {'type': 'string'} for k in ('opening_promise', 'payoff_unit_id', 'payoff_exact_text', 'reason')},
    'issues': {'type': 'array', 'items': {'type': 'string'}}},
    'required': ['passes', 'hook_honest', 'hook_specific', 'continuity_consistent', 'opening_promise',
                 'payoff_unit_id', 'payoff_exact_text', 'reason', 'issues'], 'additionalProperties': False}


def review_editorial(provider, script, plan, brief):
    result = provider.generate('independent-editorial-v1', {
        'script': script, 'brief': brief,
        'opening_visual': plan['scenes'][0],
        'task': 'Give a separate skeptical judgement of the ACTUAL frozen script, not the director self-grade. '
                'State the specific opening promise and quote the existing unit that delivers it. '
                'Fiction needs a coherent reversal/answer; education needs an actual supported answer or worked example, '
                'not merely a framework or praise. Check who knows what, chronology and planted explanations. '
                'For caption-led edits judge the actual visible captions. For a quiz check that the explained answer '
                'follows from the supplied puzzle, not merely that the writer asserts it. '
                'Do not require a comment question; a finished punchline can end immediately. '
                'Reject contradictory, withheld, unplanted or unsupported endings. No audio or rendered video was supplied; '
                'do not claim to assess delivery, visible pixels, humor, retention or factual truth independently. '
                'Return passes=false and concrete issues for a substantive problem; if no payoff exists, use empty '
                'payoff_unit_id/payoff_exact_text rather than inventing a quote. Never rewrite the dialogue.'}, REVIEW_SCHEMA)
    if not isinstance(result, dict) or set(result) != set(REVIEW_SCHEMA['properties']):
        raise Held('editorial_review_invalid', 'Editorial review omitted or invented fields.')
    if any(type(result[k]) is not bool for k in ('passes', 'hook_honest', 'hook_specific', 'continuity_consistent')):
        raise Held('editorial_review_invalid', 'Editorial verdicts must be explicit booleans.')
    if (any(not isinstance(result[k], str) or not result[k].strip() or len(result[k]) > 1800
            for k in ('opening_promise', 'reason')) or
            any(not isinstance(result[k], str) or len(result[k]) > 1800 for k in ('payoff_unit_id','payoff_exact_text'))):
        raise Held('editorial_review_invalid', 'Editorial review needs bounded supporting text.')
    issues = result['issues']
    if not isinstance(issues, list) or len(issues) > 12 or any(not isinstance(v, str) or len(v) > 600 for v in issues):
        raise Held('editorial_review_invalid', 'Malformed editorial issues.')
    payoff = next((u for u in script['units'][-2:] if u['id'] == result['payoff_unit_id']), None)
    if (not all(result[k] for k in ('passes', 'hook_honest', 'hook_specific', 'continuity_consistent')) or issues or
            not payoff or payoff['id'] != script['edit']['payoff_unit_id'] or payoff['text'] != result['payoff_exact_text']):
        raise Held('creative_review', 'Separate editorial review did not support the exact promised payoff: ' +
                   '; '.join(issues)[:600] + ' ' + result['reason'][:500])
    return {**result, 'method': 'separate model call; exact payoff identity checked',
            'limits': 'A second model opinion is not proof of creative quality or independent factual verification.'}
