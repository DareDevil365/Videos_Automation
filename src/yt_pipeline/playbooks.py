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
   'visuals':'Relevant real stock photos/clips matched to the narrated scene. Prefer distinct actual sources as the story advances, not a cycle of repeated pictures. A necessary detail revisit, adjacent continuity or later clue replay must explain why that exact source returns. In scene direction v2, small visible clues such as eyes moving/following need a source-grounded circle/arrow callout on a still image; highlighting is not evidence of actual motion. No generated schematic placeholder art or search instructions displayed as prop text. Small captions; hold tense shots rather than force random 2-second cuts.',
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
   'visuals':'Stage the recurring characters together in two-person wide/medium shots, interspersed with selective closeups and relevant real animal/object/action inserts. Show the mentioned dog, food or other essential prop rather than only swapping faces. Narrator is voice-only unless explicitly shown as a character. Keep each individual head, distinct outfit and voice stable; supported outfit silhouettes include shirt, t-shirt, hoodie, jacket and sweater, with simple talk/point/react poses. Location backdrops can continue naturally. Do not request full rigging, realistic lip-sync or complex physical acting. Scene direction v2 preserves group shots and compiles actual inserts; legacy jobs retain their original blocking policy.',
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


# These presets reuse the trusted graphic renderer and accepted education voice.
for _name, _description, _writing in (
    ('rewrite_reveal', 'Before/after wording with a delivered hypothetical rewrite',
     'Show and speak a specific weak answer, explain the exact weakness, then speak its truthful improved version. '
     'Clearly introduce practice answers as hypothetical instructional examples. Use a comparison on the rewrite '
     'with both exact phrases. End on the useful difference, with at most one optional relevant question. '
     'Do not invent experience, results, hiring outcomes or endorsements.'),
    ('myth_fact', 'One sourced misconception and a concrete bounded correction',
     'Introduce one specific claim as a misconception or question, never assert it as truth. '
     'Correct it using source-linked claims, explain the boundary and give a concrete example. '
     'Use a comparison with Myth/Fact headings and exact claim/correction phrases. '
     'Do not invent a universally held belief or overstate evidence. End with the supported correction.'),
    ('quiz_pause', 'An original question, real thinking interval and explained answer',
     'Present one original, self-contained puzzle/question with exactly one demonstrable answer. '
     'Give the necessary conditions, then one short thinking-instruction unit. The director puts a 2-6 second '
     'silent countdown AFTER that unit speech, then the answer and its concrete explanation. '
     'Do not disclose the answer before the thinking interval or use a subjective dilemma with a claimed unique answer. '
     'End with the explanation and at most one optional specific question, not a mandatory comment CTA.'),
):
    PLAYBOOKS[_name] = {
        'format': 'lesson', 'seconds': [20, 40] if _name == 'quiz_pause' else [25, 45],
        'words': [45, 90] if _name == 'quiz_pause' else [65, 115],
        'units': [5, 9] if _name == 'quiz_pause' else [6, 12],
        'voice': deepcopy(PLAYBOOKS['education_demo']['voice']),
        'music': deepcopy(PLAYBOOKS['education_demo']['music']), 'layout': 'education_demo', 'bottom': ['none'],
        'writing': _writing,
        'visuals': 'Original trusted graphic on EVERY unit: callout, process or exact-phrase comparison. '
                   'Show the concrete question/example immediately, without a generic title card. '
                   'For quiz_pause exactly one timer scene repeats the earlier question and precedes the answer. '
                   'Do not request stock, fabricated interfaces, real-person images or screenshots as evidence.',
        'sound': 'Retain the accepted clear education voice. Optional bounded internal silence/speed uses speech_segments.',
        'description': _description, 'graphics_only': True}


PLAYBOOKS['server_chat']={
    'format':'chat','seconds':[30,55],'words':[85,125],'units':[16,18],
    'voice':{'voice_id':'am_adam','length_scale':.88,'pause':.13},
    'music':{'category':'storytime','mood':'optional restrained comic tension','volume':.05},
    'layout':'server_chat','bottom':['none'],
    'writing':'Invent an original fictional server-chat comedy between 2-3 recurring people with distinct goals. Short actual messages, mostly 3-9 words, no narration. The opening message establishes a concrete immediately understandable conflict. Escalate through replies and a planted detail; deliver a causal final reversal/consequence that turns the opening rule against its maker. Do not finish with a generic reaction or explanation. End on the payoff. Use original names, no creator characters, plots, catchphrases or copied dialogue. All onscreen fields MUST equal the actual full message text verbatim. No real platform exploits, private information, real-person allegations, or engagement promises. Keep messages short enough to read on a phone.',
    'visuals':'Full-screen original dark server-chat interface, consistent colored initial avatars and names. One actual message at a time, smooth entry/scroll while preserving previous context. No unrelated stock backdrop, character bodies, lower panel or external screenshots. The conversation itself is the scene. This is fictional UI, not a real conversation or authentic Discord screenshot.',
    'sound':'Distinct consistent local voices per character read actual messages. Short restrained pauses and a beat before the payoff. This pilot retains accessible voiced dialogue; it does not claim to reproduce a creator audio track.'}


PLAYBOOKS['illustrated_story']={
    'format':'lesson','seconds':[75,130],'words':[180,270],'units':[12,18],
    'voice':{'voice_id':'af_heart','length_scale':1.0,'pause':.3},
    'music':{'category':'storytime','mood':'optional quiet atmospheric bed','volume':.035},
    'layout':'illustrated_story','bottom':['none'],
    'writing':'Original fictional cinematic story with a specific mystery opening, visible planted clues, a coherent cause and a resolved emotional ending. One voice-only narrator. Characters, outfits, important objects and locations stay consistent. Avoid a list of talking-head swaps, an unplanted twin/dream/hacker and a cliffhanger replacing the answer. Narration must match the supplied illustration inventory. This preset requires registered original illustrations and cannot silently search for unrelated footage.',
    'visuals':'Full-frame landscape original story illustrations, selective reframing, actual frame-timed weather/light effects and an optional supplied source-pixel callout. Narrator has no body. Shared scenes should visibly contain the people/animals mentioned. These effects do not animate character bodies or provide lip sync.',
    'sound':'Consistent local narrator with bounded pauses; no imitated creator voice.'}

PLAYBOOKS['documentary_chapter']={
    'format':'lesson','seconds':[60,90],'words':[155,195],'units':[8,12],
    'voice':{'voice_id':'am_adam','length_scale':.98,'pause':.22},
    'music':{'category':'learning','mood':'optional quiet documentary bed','volume':.05},
    'layout':'documentary','bottom':['none'],
    'writing':'Write one original factual documentary chapter for a general audience. One clear question, causal progression and a concrete supported answer, not a list of slogans. Use the supplied chapter objective and episode context to avoid repeating other chapters. One consistent Narrator. Aim at 175 spoken words across 8-12 complete short units. The first line is a specific question or contrast within 18 words. Explain technical ideas in plain language, with a clearly hypothetical everyday analogy if useful. Every factual statement needs supporting claim_ids; transitions and recommendations must not smuggle unsupported assertions. No invented statistics, benchmarks, quotes, companies or demonstrations. Onscreen fields are concise phrases of at most 85 characters that can label a diagram, not paragraphs. Deliver the chapter answer in the final two units without claiming to conclude the whole episode unless this is its last chapter. No greetings, subscription prompts or repeated intro/outro.',
    'visuals':'Original landscape explanatory motion graphics. The separate director chooses comparison, process, timeline, relationship, source highlight or sourced bars, using exact script phrases. Supply short phrases useful for diagram labels in text/onscreen. No stock carousel, fabricated interface or copied creator assets.',
    'sound':'One consistent clear local narrator, measured pacing and bounded pauses. No imitated creator voice.'}


for _name,_writing,_voice in (
    ('comic_lore','Retell one coherent, sourced fictional canon as an original short recap. Clearly name the comic/run/year in metadata and distinguish it from film announcements or fan theories. Open with a specific story question, reveal a new concrete consequence, and deliver this chapter\'s answer before an earned next-part lead. Explain people by their role; avoid alias lists and repeated thematic morals. Every plot claim needs a supplied claim ID. Never claim to have read a full issue when only publisher recaps were available.','bm_george'),
    ('movie_brief','Give one useful movie recommendation, confirmed announcement or clearly sourced movie-news answer. Lead with the actual viewer question and resolve it. Distinguish the actor from the character, confirmed facts from rumors, comic canon from film continuity, gross from budget and dated estimates from final totals. Do not invent feuds, release dates, box-office records, streaming availability or prediction-as-fact.','am_adam'),
    ('current_affairs','Explain one dated development and its concrete meaning for an India/world-current-affairs viewer. State the actual event date, define one useful term and answer what changed. Distinguish direction, denominator, eligibility and exceptions; avoid turning a narrow concession into a blanket claim. No fake breaking-news urgency, invented election result or nationalistic claim beyond the evidence.','am_adam')):
    PLAYBOOKS[_name]={'format':'lesson','seconds':[25,80],'words':[75,175],'units':[7,12],
        'voice':{'voice_id':_voice,'length_scale':1.0,'pause':.18},
        'music':{'category':'storytime' if _name!='current_affairs' else 'learning','mood':'quiet licensed bed below speech','volume':.06},
        'layout':'comic_lore' if _name=='comic_lore' else 'education_demo','bottom':['none'],'writing':_writing,
        'visuals':'Trusted original portrait panels or explanatory motion graphics bound to exact script labels. No generated photos/videos or assumed permission to reuse comic panels/film clips.',
        'sound':'One clear local narrator, complete measured speech and reading holds; optional permitted music below voice.'}


def prepare_request(request):
    """Resolve defaults only for new presets, preserving historical requests."""
    value = deepcopy(request)
    if value.get('playbook') in ('comic_lore','movie_brief','current_affairs'):
        for key,setting in {'bottom_kind':'none','require_music':False,'hook_options':False,'editorial_review':'off','visual_review':'off','motion_graphics':True}.items():value.setdefault(key,setting)
        if value.get('fiction') is True or value['bottom_kind']!='none' or value.get('bottom_asset_id'):raise Held('factual_brief','Source-aware short recaps need factual briefs and a full portrait frame.')
    if value.get('playbook')=='illustrated_story':
        if value.get('story_canvas','landscape') not in ('portrait','landscape'):raise Held('story_layout','Choose portrait or landscape story canvas.')
        if type(value.get('allow_licensed_illustrations',False)) is not bool:raise Held('story_layout','allow_licensed_illustrations must be a boolean.')
        for key,setting in {'bottom_kind':'none','require_music':False}.items():value.setdefault(key,setting)
        if value['bottom_kind']!='none' or value.get('bottom_asset_id'):
            raise Held('story_layout','Illustrated stories need the whole landscape frame.')
    if value.get('playbook')=='documentary_chapter':
        for key,setting in {'hook_options':True,'hook_validation':'strict','editorial_review':'required','bottom_kind':'none','require_music':False}.items():
            value.setdefault(key,setting)
        if value.get('fiction') is True or value.get('bottom_kind')!='none' or value.get('bottom_asset_id'):
            raise Held('documentary_layout','Documentary chapters require factual evidence and a full landscape frame.')
    if value.get('playbook')=='server_chat':
        version=value.get('chat_editing_version',1)
        if type(version) is not int or version not in (1,2):raise Held('chat_config','Choose chat editing version 1 or 2.')
        if type(value.get('chat_writing_version',1)) is not int or value.get('chat_writing_version',1) not in (1,2):raise Held('chat_config','Choose chat writing version 1 or 2.')
        if value.get('chat_writing_version')==2 and version!=2:raise Held('chat_config','Writing v2 needs the local chat editor.')
        value.setdefault('chat_tone','thriller' if value.get('phone_story') else 'comedy')
        defaults={'hook_options':False,'hook_validation':'strict','editorial_review':'off','visual_review':'off','bottom_kind':'none','require_music':False} if version==2 else {'hook_options':True,'hook_validation':'strict','editorial_review':'required','bottom_kind':'none','require_music':False}
        for key,setting in defaults.items():
            value.setdefault(key,setting)
        if value.get('phone_story') is not None and type(value['phone_story']) is not bool:raise Held('phone_story','phone_story must be a boolean request setting.')
        if value.get('phone_story') and version!=2:raise Held('phone_story','Phone stories require the local v2 editor.')
        if value.get('chat_tone','comedy') not in ('comedy','mystery','thriller','story'):raise Held('chat_config','Choose comedy, mystery or thriller tone.')
        if type(value.get('chat_script_review',False)) is not bool:raise Held('chat_config','chat_script_review must be a boolean.')
        if type(value.get('chat_voiceover',False)) is not bool:raise Held('chat_voice','chat_voiceover must be a boolean.')
        from .phone_editor.audio import voice_styles
        voice_styles(value)
        if type(value.get('chat_sound_library',False)) is not bool:raise Held('chat_sound','chat_sound_library must be a boolean.')
        events=value.get('chat_sound_events',[])
        if not isinstance(events,list) or len(events)>8 or any(not isinstance(e,dict) for e in events):raise Held('chat_sound','Supply at most eight explicit sound events.')
        if events and not value.get('chat_sound_library'):raise Held('chat_sound','Explicit sound events need chat_sound_library enabled.')
        if type(value.get('chat_auto_music',False)) is not bool:raise Held('chat_music','chat_auto_music must be a boolean.')
        pauses=value.get('chat_pause_before',{})
        if not isinstance(pauses,dict) or len(pauses)>26 or any(not isinstance(k,str) or type(v) not in (int,float) or not 0<=v<=1.5 for k,v in pauses.items()):raise Held('chat_timing','Message anticipation pauses must map message IDs to 0-1.5 seconds.')
        voices=value.get('chat_voice_ids',{})
        if not isinstance(voices,dict) or len(voices)>6 or any(not isinstance(k,str) or not isinstance(v,str) or not v for k,v in voices.items()):raise Held('chat_voice','Map up to six actual character names to installed voice IDs.')
        if value.get('chat_voiceover') and version!=2:raise Held('chat_voice','Character speech needs the compiled chat editor.')
        volume=value.get('chat_music_volume',.20)
        if type(volume) not in (int,float) or not 0<=volume<=.35:raise Held('chat_music','Keep chat background music between 0 and 0.35.')
        if not isinstance(value.get('chat_attachment_ids',{}),dict) or len(value.get('chat_attachment_ids',{}))>8:raise Held('chat_attachment','Use a mapping of at most eight message IDs to registered GIF/image IDs.')
        if value.get('chat_group_name') is not None and (not isinstance(value['chat_group_name'],str) or not 1<=len(value['chat_group_name'])<=40):raise Held('chat_config','Use a short actual conversation name.')
        if not isinstance(value.get('phone_wallpaper_ids',{}),dict) or len(value.get('phone_wallpaper_ids',{}))>5:raise Held('phone_wallpaper','Supply at most five registered thread wallpaper IDs.')
        if version==2 and (value['hook_options'] is not False or value['editorial_review']!='off' or value['visual_review']!='off'):
            raise Held('chat_provider_scope','Chat v2 uses the model for script writing only; hooks, model direction and model reviews must be off.')
        if version==2 and (value.get('fiction') is False or value.get('brief',{}).get('kind','fiction')!='fiction' or value.get('source_urls') or value.get('brief_file')):
            raise Held('chat_provider_scope','Chat v2 is original fictional conversation; factual research belongs to a separate evidence-reviewed route.')
        if value['bottom_kind']!='none' or value.get('bottom_asset_id'):raise Held('chat_layout','Server chat fills the frame and does not use a lower panel.')
    if PLAYBOOKS.get(value.get('playbook'), {}).get('graphics_only'):
        for key, setting in {'motion_graphics': True, 'hook_options': True, 'hook_validation': 'strict',
                             'editorial_review': 'required', 'bottom_kind': 'none', 'require_music': False}.items():
            value.setdefault(key, setting)
        if value['motion_graphics'] is not True or value['bottom_kind']!='none' or value.get('bottom_asset_id') or value.get('bottom_source_file'):
            raise Held('playbook_graphics','These original-graphics presets require motion_graphics true and no lower panel.')
    return value


def get_playbook(name,request=None):
    if name not in PLAYBOOKS:raise Held('playbook_unknown','Choose a supported creative playbook')
    rules={'id':name,**deepcopy(PLAYBOOKS[name])}
    if name=='server_chat' and (request or {}).get('chat_editing_version')==2:
        rules.update(seconds=[18,55],words=[40,100],units=[12,22],voice=None)
        rules['writing']='Write an ORIGINAL casual chat comedy between 2-3 recurring people. The conversation itself tells the complete story; no Narrator. 12-22 short actual messages, 40-100 words total, mostly 2-7 words per message, at most 12 words each. Start immediately on a specific relatable conflict. Escalate with replies that change the situation, plant a concrete detail and end on an earned action/concession/reversal. The final line must land the joke, not explain it afterwards. Avoid formal prose, legal/business jargon, magic bot powers, technical exploits, random new facts and mere confessions. Keep every onscreen field EXACTLY equal to its message text. Use original names and dialogue, never creator cast or copied lines. Metadata describes the actual conversation. Do not invent visual assets or editing commands.'
        from .phone_editor.writing import COMEDY_BRIEF
        rules['writing']+=' '+COMEDY_BRIEF
        if (request or {}).get('phone_story'):
            tone=(request or {}).get('chat_tone','thriller')
            rules.update(seconds=[22,90],words=[55,150],units=[12,28])
            rules['writing']=f'Write an ORIGINAL {tone} story told ENTIRELY through a fictional phone screen. 12-28 actual messages, 55-150 words total, at most 12 words each. One phone owner and 1-5 named contacts; no narrator. Use private conversations with distinct purposes, not random switches. Start with a specific curiosity, surprising message or unresolved problem, plant a fair clue, escalate through new information and deliver a causal answer in the final two messages. A cliffhanger may add a new implication only after resolving the opening. Avoid repetitive reactions and arbitrary unplanted endings. Do not escape the mystery with an unplanted prank, dream, burner app or newly invented sibling; the reveal must follow from evidence in actual earlier messages. Each onscreen equals its message text exactly. The outer script version MUST be integer 1, including repairs. Deliver at least 12 message units; count them before returning. Return phone_story: pov is the phone owner name, contacts give unique IDs/names, threads reference contact IDs and choose light/dark/rose/sage theme, and beats map EVERY actual unit in order to thread_id, explicit fictional same-day 24-hour HH:MM time, and events array. Each message speaker must be the phone owner or that thread contact. Events are optional story occurrences: low_battery, glitch, blackout, time_jump, notification; switch navigation is automatic. Events happen BEFORE the associated message; notification previews that incoming message. Battery/glitch must precede blackout; advance time for time_jump. Use interruptions only when they serve this story, never cram in every capability. No duration, camera, code, URLs or downloads. The program chooses rendering and all timing. Do not falsely present fiction as an actual phone recording.'
            if tone=='comedy':rules['writing']+=' '+COMEDY_BRIEF
        if (request or {}).get('chat_writing_version')==2:
            rules.update(units=[10,26] if (request or {}).get('phone_story') else [8,20],words=[50,145] if (request or {}).get('phone_story') else [35,105],seconds=[18,90] if (request or {}).get('phone_story') else [12,55])
            rules['writing']+=' For writing version 2, the numeric words/units/seconds fields override older counts in the format description. Do not pad to twelve messages; fewer meaningful exchanges within those numeric bounds are preferred.'
        if (request or {}).get('chat_writing_version')==2:
            rules['writing']=rules['writing'].replace('12-22 short actual messages, 40-100 words total','8-20 short actual messages, 35-105 words total').replace('12-28 actual messages, 55-150 words total','10-26 actual messages, 50-145 words total').replace('Deliver at least 12 message units; count them before returning.','Use only meaningful exchanges within the supplied unit bounds.')
        rules['visuals']='The SOFTWARE handles editing: portrait 9:16, close-cropped message cards, previous context, typing beats, reaction emphasis, readable holds, stable names/avatars and notification sound. Return ONLY dialogue/content; do not plan timings, camera moves or music. Text must work without a narrator or unseen physical action.'
        rules['sound']='Reading-led chat, no narrator or TTS. Quiet original message pops; interruption/blackout sections stay silent.'
    if name=='illustrated_story' and (request or {}).get('story_canvas')=='portrait':rules.update(seconds=[35,80],words=[100,190],units=[8,14])
    return rules


def writing_prompt(name,request=None):
    value=get_playbook(name,request)
    from .writing_craft import craft_context
    value['writing_skill']=craft_context((request or {}).get('chat_tone',(request or {}).get('story_tone','comedy' if name in ('server_chat','cutout_ensemble') else name)),value['format'])
    if name in ('comic_lore','movie_brief','current_affairs'):
        return {**value,'task':'Write the source-bound script only, preserving claim IDs and the chosen canon/event date. Open on the actual question and deliver the concrete answer by the penultimate unit. A comic chapter may then lead to its actual next part. The local editor compiles illustrations, captions and timing; do not invent footage, source URLs or release links.',
            'editorial_policy':'Check the scope of each claim against the supplied evidence. Audience critique is a separate pass; it cannot verify an unsourced claim or prove engagement.'}
    if name=='server_chat' and (request or {}).get('chat_editing_version')==2:
        return {**value,'task':'Write only the complete conversation in the script JSON contract. The hook equals the first actual message, and onscreen equals text for every message. Do not create a storyboard or timing. The software compiles all editing without another model call.',
            'editorial_policy':'One writing call, at most one structural repair. Optional writing-only critique allows at most one revision and one recheck; software still owns all edits. Structural checks/model opinions cannot certify humor or viewer response.'}
    return {**value,'task':'Write ONLY the story/content script first. hook must be the exact first spoken unit, not a stronger unwritten marketing summary. The first words must establish the specific curiosity/problem. The actual answer must occupy the final or penultimate unit with no filler ending; edit.payoff_unit_id identifies it. Do not plan an unsupported edit or choose unverified asset URLs. The separate director call will preserve these exact words.',
            'editorial_policy':'New playbook batches generate three typed hooks in the same writing call and request a separate exact-payoff review. Comment prompts are optional and follow the delivered answer. Clean dialogue never contains speech-control markup. Director speech_segments can express bounded pace/internal silence without changing words. Source clips and caption-led aura keep their separate contracts.',
            'retention_note':'Patterns are testable editorial hypotheses, not a retention guarantee.'}


def validate_playbook_script(script,name,request=None):
    value=get_playbook(name,request)
    if script['format']!=value['format']:raise Held('playbook_script','Script format differs from its selected playbook')
    if name in ('documentary_chapter','comic_lore','movie_brief','current_affairs'):
        speakers = [unit['speaker'] for unit in script['units']]
        hosted = name == 'comic_lore' and speakers == ['Host', *(['Narrator'] * (len(speakers)-2)), 'Host']
        if script['fiction'] or (len(set(speakers)) != 1 and not hosted) or any(len(u['onscreen'])>85 for u in script['units']):
            raise Held('playbook_script','Use one narrator or a comic host who opens and closes around the storyteller.')
    if name=='server_chat':
        maximum=6 if (request or {}).get('phone_story') else 3
        if not 2<=len({u['speaker'] for u in script['units']})<=maximum or any(u['speaker'].strip().lower()=='narrator' for u in script['units']):
            raise Held('playbook_script',f'Chat needs 2-{maximum} actual participants and no narrator.')
        limit=12 if (request or {}).get('chat_editing_version')==2 else 15
        if any(u['onscreen']!=u['text'] or len(u['text'].split())>limit for u in script['units']):
            raise Held('playbook_script',f'Display every complete chat message verbatim; keep each message at most {limit} words.')
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
    from .script_quality import validate_hook
    validate_hook(script, name)
    return {'playbook':name,'words':count,'word_tolerance':3,'units':len(script['units']),'duration_target':value['seconds'],'semantic_payoff_verified':False}


def export_playbooks(folder):
    from pathlib import Path
    from shorts_editor.store import write_json
    from .creative_plan import PLAN_SCHEMA,CAPABILITIES
    from .edit_blocks import capabilities
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    for name in PLAYBOOKS:write_json(folder/(name+'.writer.json'),writing_prompt(name))
    write_json(folder/'server_chat.v2.writer.json',writing_prompt('server_chat',{'chat_editing_version':2}))
    from .phone_editor.contract import PHONE_SCHEMA
    write_json(folder/'phone-story.schema.json',PHONE_SCHEMA)
    for tone in ('comedy','mystery','thriller','story'):write_json(folder/('phone-story.'+tone+'.writer.json'),writing_prompt('server_chat',{'chat_editing_version':2,'phone_story':True,'chat_tone':tone}))
    from .phone_editor.writing import DIAGNOSTIC_SCHEMA,draft_schema
    from .contracts import SCRIPT_SCHEMA
    write_json(folder/'chat-writing-v2.reader-schema.json',DIAGNOSTIC_SCHEMA)
    write_json(folder/'chat-writing-v2.draft-schema.json',draft_schema(SCRIPT_SCHEMA))
    write_json(folder/'chat-writing-v2.writer.json',writing_prompt('server_chat',{'chat_editing_version':2,'chat_writing_version':2}))
    write_json(folder/'server_chat.v2.editor.json',{'version':2,'canvas':[720,1280],
        'provider_scope':'One story-writing request and at most one structural repair. Optional writing-only review, one revision and one recheck. No model directing.',
        'timing':'Frame-clock reading hold per complete message, with code-selected entry/typing/reaction states.',
        'sound':'One quiet original message pop; no typing chirps, TTS or copied creator audio.',
        'avatar':'Optional registered photo IDs and normalized crop slots; otherwise stable initials.',
        'limits':'Deterministic editing and structural checks do not establish comedy quality.'})
    write_json(folder/'director-schema.json',PLAN_SCHEMA)
    write_json(folder/'director-capabilities.json',CAPABILITIES)
    write_json(folder/'edit-blocks.json',capabilities())
    from .contracts import SCRIPT_SCHEMA
    from .script_quality import hook_envelope,REVIEW_SCHEMA
    from .speech_delivery import SEGMENT_SCHEMA
    write_json(folder/'script-hooks-schema.json',hook_envelope(SCRIPT_SCHEMA))
    write_json(folder/'editorial-review-schema.json',REVIEW_SCHEMA)
    write_json(folder/'speech-segments-schema.json',SEGMENT_SCHEMA)
    return {'folder':str(folder.resolve()),'playbooks':list(PLAYBOOKS),'renderer':'ffmpeg','adobe_adapter_implemented':False}
