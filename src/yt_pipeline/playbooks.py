"""Executable creative constraints. Research observations remain in research/.

These rules encode owner feedback and testable format requirements, not a
prediction of views. Keep the prompt and edit capability contract together.
"""
from copy import deepcopy
import re
from .core import Held

PLAYBOOKS={
 'horror_stock':{'format':'lesson','seconds':[30,45],'words':[75,95],'units':[8,13],
   'voice':{'voice_id':'af_heart','length_scale':1.08,'pause':.28},
   'music':{'category':'horror','mood':'quiet eerie atmospheric suspense, no comic beat','volume':.10},
   'layout':'story_stock','bottom':['none','asmr'],
   'writing':'Original fictional mystery: one impossible specific detail immediately; believable setup; 2-3 clues that change the interpretation; reveal the cause/identity or a concrete reversal before the end. A warning such as do not turn around alone is NOT a payoff. No cliffhanger replacing the answer. Use 8-13 short voiced units and 75-95 total words, aiming around 85. Resolve the opening question in the final two units. Put an optional genuine interpretation question only AFTER that answer. Software will enforce actual 30-45 second voice timing, not assume that a word count guarantees it.',
   'visuals':'Relevant real stock photos/clips: dark elevator, hallway, alley, room, phone in hand. No generated schematic placeholder art. Never show search instructions as visible prop text. Reuse a location for continuity but change the viewpoint/action as the story advances. Small captions; hold tense shots rather than force random 2-second cuts.',
   'sound':'Female narrator, restrained slower delivery with bounded pauses before the reveal; do not promise acting/emotion beyond the TTS model. Quiet licensed eerie bed, clear voice, no random phonk.'},
 'tea_chat':{'format':'chat','seconds':[30,45],'words':[90,140],'units':[10,18],
   'voice':{'voice_id':'af_heart','length_scale':.83,'pause':.10},
   'music':{'category':'storytime','mood':'light restrained tension, speech first','volume':.06},
   'layout':'chat_asmr','bottom':['asmr','gameplay'],
   'writing':'Original fictional relationship/friendship chat: specific incriminating message first, establish who is speaking, escalating contradiction with a concrete social consequence, a planted clue, then reveal who was actually texting or why the apparent betrayal happened. The clue must make the answer understandable in retrospect. Avoid an unmentioned twin/hacker/dream suddenly solving everything at the end. End with the answer, followed by at most one optional natural question about the choice; do not spend the ending announcing what a great plot twist it was. No generic moral lecture, no real private conversation or accusation.',
   'visuals':'Readable conversational message states over a continuous supplied ASMR or gameplay lower panel. Short actual message text, consistent speaker names, one reveal at a time; optional inserts must show what the line means.',
   'sound':'Brisk intelligible storytime, distinct consistent voices per speaker if supported; short pauses around the reveal. ASMR lower track muted or quiet under speech, never competing at full volume.'},
 'cutout_ensemble':{'format':'cutout','seconds':[30,50],'words':[90,150],'units':[9,18],
   'voice':{'voice_id':'am_adam','length_scale':.88,'pause':.12},
   'music':{'category':'storytime','mood':'subtle comic tension; short reaction cue at payoff','volume':.07},
   'layout':'cutout_cast','bottom':['none','gameplay','asmr'],
   'writing':'Original funny or tea-style micro-story with 2-4 recurring fictional characters plus an optional Narrator. First spoken line must immediately state a specific absurd conflict with a stake or consequence; no greetings or delayed premise. Plant a detail, escalate through opposing goals, then make the final line reverse power or turn the opening rule against its maker. Explaining an ordinary device noise, saying mystery solved, arriving normally or praising the twist does not qualify as comedy. Prefer setup -> escalating bad strategy -> callback/backfire. End on the actual punchline, not an explanation after it. Assign every line to its exact speaker.',
   'visuals':'Photo/collage cutouts inspired by fast reaction editing: establish the cast together, then close-up the active speaker by hiding others and enlarging that actor. Use the same background/location until the story moves. Consistent cast heads, clothes and voice IDs. Static poses and simple crop/scale are supported; do not request full rigging, realistic lip-sync or complex physical acting.',
   'sound':'Brisk narrative anchor and consistent per-character voices. Pauses/cuts on reactions; no narration over another character\'s line.'},
 'aura_progression':{'format':'aura','seconds':[12,24],'words':[12,45],'units':[5,8],
   'voice':None,'music':{'category':'aura','mood':'permitted phonk or similar strong rhythmic beat with a drop','volume':.55},
   'layout':'aura_progression','bottom':['none','gameplay'],
   'writing':'Original short editorial caption edit: establish a real documented before/after contrast, transition at the beat drop, escalate through distinct verified visual moments, and deliver the strongest final frame. Captions 1-5 words, aura-minus to aura-plus can be a clearly playful gauge. No invented biography, possessions, girlfriend, money, endorsement or quote about a real person. Use only what the supplied visual inventory supports.',
   'visuals':'At least four distinct usable images/clips. Early image then different later/event/achievement images supplied with evidence. Never use ASMR beneath aura. Beat-aligned crop, quick flash/punch, optional generic decorative coins explicitly not evidence of the subject\'s wealth. No one-photo loop.',
   'sound':'No TTS by default. Require a registered suitable rhythmic track and a specified drop point. Do not silently use the rejected synthetic loop or a comic stock tune.'},
 'education_demo':{'format':'lesson','seconds':[25,45],'words':[70,115],'units':[7,12],
   'voice':{'voice_id':'am_adam','length_scale':.80,'pause':.10},
   'music':{'category':'learning','mood':'quiet unobtrusive instrumental or none','volume':.05},
   'layout':'education_demo','bottom':['none','gameplay'],
   'writing':'One useful AI, interview/job skill, confidence, study or accessible-knowledge takeaway. Hook with a visible specific problem or before/after. Demonstrate the actual step/example. End with the resulting comparison or answer, then optionally ask a relevant choice question. No lecture intro, fake personal test, invented free feature, income claim or guaranteed outcome. Factual units need source claim IDs.',
   'visuals':'Original screen recording or relevant stock/diagram at each beat. Small captions and a new meaningful visual roughly every 2-3 seconds during explanation, longer when needed to read a real result. No unrelated stock carousel; screenshots must match the actual current interface.',
   'sound':'Accepted clear brisk male voice, articulate and energetic rather than shouting. Background stays below voice.'},
 'movie_countdown':{'format':'lesson','seconds':[35,55],'words':[75,135],'units':[10,13],
   'voice':{'voice_id':'am_adam','length_scale':.85,'pause':.12},
   'music':{'category':'storytime','mood':'quiet cinematic rhythmic instrumental','volume':.08},
   'layout':'movie_cards','bottom':['none'],
   'writing':'A specific theme and useful short original reasons, not just peak/goated. If asking viewers to choose number one, promise nine picks plus their number one at the START; count 10 down to 2 and invite their choice. Do not promise to reveal the best movie then withhold it. A separate guess-the-film round may show an authorized clue and clearly invite a guess. Never obscure credits/source rights to provoke comments.',
   'visuals':'One supplied usable poster/clip per ranked item, readable rank and title when this is a recommendation, concise verdict/reason. Separate guess round explicitly labelled. No repetitive same card or unsupported movie facts.',
   'sound':'Crisp short deliveries, room to read titles, consistent quiet music; no copyrighted movie score by default.'}
}


def get_playbook(name):
    if name not in PLAYBOOKS:raise Held('playbook_unknown','Choose a supported creative playbook')
    return {'id':name,**deepcopy(PLAYBOOKS[name])}


def writing_prompt(name):
    value=get_playbook(name)
    return {**value,'task':'Write ONLY the story/content script first. hook must be the exact first spoken unit, not a stronger unwritten marketing summary. The first words must establish the specific curiosity/problem. The actual answer must occupy the final or penultimate unit with no filler ending; edit.payoff_unit_id identifies it. Do not plan an unsupported edit or choose unverified asset URLs. The separate director call will preserve these exact words.',
            'retention_note':'Patterns are testable editorial hypotheses, not a retention guarantee.'}


def validate_playbook_script(script,name):
    value=get_playbook(name)
    if script['format']!=value['format']:raise Held('playbook_script','Script format differs from its selected playbook')
    count=sum(len(re.findall(r"\b[\w]+(?:['-][\w]+)*\b",u['text'])) for u in script['units'])
    # Counts are a rough pacing filter. A three-word tolerance avoids spending a
    # second model call for tokenisation differences; measured audio is the limit.
    issues=[]
    if script['hook'].strip()!=script['units'][0]['text'].strip():issues.append('hook must exactly equal the first spoken unit; do not hide the actual hook only in metadata')
    if not value['words'][0]-3<=count<=value['words'][1]+3:
        issues.append(f'{name} needs {value["words"][0]}-{value["words"][1]} words, got {count}')
    if not value['units'][0]<=len(script['units'])<=value['units'][1]:issues.append(f'Need {value["units"][0]}-{value["units"][1]} units, got {len(script["units"])}')
    payoff=script['edit']['payoff_unit_id']
    if payoff not in {u['id'] for u in script['units'][-2:]}:issues.append('Deliver the payoff in the final two units, before at most one optional question; edit.payoff_unit_id must identify that actual answer')
    if issues:raise Held('playbook_length','; '.join(issues))
    return {'playbook':name,'words':count,'word_tolerance':3,'units':len(script['units']),'duration_target':value['seconds'],'semantic_payoff_verified':False}


def export_playbooks(folder):
    from pathlib import Path
    from shorts_editor.store import write_json
    from .creative_plan import PLAN_SCHEMA,CAPABILITIES
    from .edit_blocks import capabilities
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    for name in PLAYBOOKS:write_json(folder/(name+'.writer.json'),writing_prompt(name))
    write_json(folder/'director-schema.json',PLAN_SCHEMA)
    write_json(folder/'director-capabilities.json',CAPABILITIES)
    write_json(folder/'edit-blocks.json',capabilities())
    return {'folder':str(folder.resolve()),'playbooks':list(PLAYBOOKS),'renderer':'ffmpeg','adobe_adapter_implemented':False}
