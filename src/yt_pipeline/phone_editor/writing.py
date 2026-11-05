"""Focused story development, evidence-based critique and one bounded revision."""
from copy import deepcopy
from ..core import Held

COMEDY_BRIEF = (
    'Vary comic mechanisms: conflicting priorities, literal interpretation, escalating commitment or a changed-meaning callback. '
    'A specific surprising opening, an unresolved contradiction or a concrete desire can create curiosity; choose what suits this story, not a compulsory formula. '
    'Plant a fair clue early. Every exchange must change the situation, evidence or leverage. '
    'The LAST message must resolve the opening and add new causally planted information, not recap the reveal, explain the joke or add a moral. '
    'Keep characters distinct by wants/reactions; no repeated disbelief loops or arbitrary final props. Choose an earned ending before writing its setup.')

REVIEW_SCHEMA={'type':'object','properties':{
    'passes':{'type':'boolean'},'opening_unit_id':{'type':'string'},'opening_quote':{'type':'string'},
    'payoff_unit_id':{'type':'string'},'payoff_quote':{'type':'string'},
    'clue_unit_id':{'type':'string'},'clue_quote':{'type':'string'},
    'issues':{'type':'array','maxItems':8,'items':{'type':'string'}},'reason':{'type':'string'}},
    'required':['passes','opening_unit_id','opening_quote','payoff_unit_id','payoff_quote','clue_unit_id','clue_quote','issues','reason'], 'additionalProperties':False}


CRITERIA=('opening','cause','knowledge','progression','voice','payoff','genre')
CHECK_SCHEMA={'type':'object','properties':{'verdict':{'type':'string','enum':['pass','revise']},
    'unit_id':{'type':'string'},'quote':{'type':'string'},'reason':{'type':'string'}},
    'required':['verdict','unit_id','quote','reason'],'additionalProperties':False}
DIAGNOSTIC_SCHEMA={'type':'object','properties':{
    'reader_question':{'type':'string'},'reader_answer':{'type':'string'},
    'missing_assumptions':{'type':'array','items':{'type':'string'},'maxItems':8},
    'checks':{'type':'object','properties':{k:CHECK_SCHEMA for k in CRITERIA},'required':list(CRITERIA),'additionalProperties':False}},
    'required':['reader_question','reader_answer','missing_assumptions','checks'],'additionalProperties':False}
SKETCH_KEYS=('situation','conflicting_wants','opening','early_plant','ending','cause','mechanism')
SKETCH_SCHEMA={'type':'object','properties':{k:{'type':'string'} for k in SKETCH_KEYS},'required':list(SKETCH_KEYS),'additionalProperties':False}


def draft_schema(schema):
    return {'type':'object','properties':{'sketches':{'type':'array','minItems':3,'maxItems':3,'items':SKETCH_SCHEMA},
        'selected_index':{'type':'integer','minimum':0,'maximum':2},'script':deepcopy(schema)},
        'required':['sketches','selected_index','script'],'additionalProperties':False}


def writing_context(brief,request,rules,feedback):
    return {'topic':request.get('topic',brief.get('title','')),'tone':request.get('chat_tone','thriller' if request.get('phone_story') else 'comedy'),
        'owner_constraints':str(request.get('creative_brief',''))[:2000],'owner_feedback':feedback,
        'conversation_mode':'private threads' if request.get('phone_story') else 'group' if request.get('chat_group_name') else 'conversation','group_name':request.get('chat_group_name',''),
        'bounds':{k:rules[k] for k in ('words','units','seconds')},'format_rules':rules['writing'],
        'policy':'Original fictional messages only. Fragments and natural short replies are welcome. onscreen equals text; claim_ids is empty. '
        'No stock searches, visual_query, captions, narrator, TTS, directing, music or effect instructions. '
        'Phone occurrences are optional story facts only when phone_story is enabled; do not add events just to demonstrate features.',
        'craft':('Character wants, a meaningful choice and a specific earned emotional change. Do not force a threat, twist or joke into a gentle story. End with an action that fulfills the opening.' if request.get('chat_tone')=='story' else COMEDY_BRIEF) if request.get('chat_tone','comedy') in ('comedy','story') else
            'Track who knows what in each private conversation. Plan a mundane or explicitly established cause before the opening. '
            'Threatening behavior needs a motive. No invented SMS powers or technical jargon to conceal a missing cause. '
            'A surprise should change the meaning of an early ordinary detail, not introduce the missing explanation at the end.'}


def unpack_draft(raw):
    if not isinstance(raw,dict) or set(raw)!={'sketches','selected_index','script'}:raise Held('invalid_contract','Return three story sketches, selected_index and script.')
    options=raw['sketches'];index=raw['selected_index']
    if not isinstance(options,list) or len(options)!=3 or type(index) is not int or not 0<=index<3:raise Held('invalid_contract','Choose one of exactly three compact story sketches.')
    for option in options:
        if not isinstance(option,dict) or set(option)!=set(SKETCH_KEYS) or any(not isinstance(v,str) or not v.strip() or len(v)>500 for v in option.values()):
            raise Held('invalid_contract','Each sketch needs short specific wants, opening, early plant, ending, cause and mechanism.')
        if any(len(option[k].split())>12 for k in ('opening','early_plant','ending')):raise Held('invalid_contract','Sketch message anchors must fit the 12-word message limit.')
    if len({o['mechanism'].casefold().strip() for o in options})!=3:raise Held('invalid_contract','Vary the three story mechanisms; do not rename one premise three times.')
    return raw['script'],{'sketches':options,'selected_index':index,'selected':options[index],
        'selection_scope':'Writer chooses; selection is not an independent quality verdict.'}


def validate_anchors(script,development):
    chosen=development['selected'];texts=[u['text'] for u in script['units']]
    if texts[0]!=chosen['opening'] or texts[-1]!=chosen['ending'] or chosen['early_plant'] not in texts[:max(2,len(texts)//3)]:
        raise Held('invalid_contract','Use the selected opening/ending verbatim and plant its exact early_plant message in the first third.')


def diagnose(provider,script,tone):
    # No title, hook/payoff metadata, writer explanation or favorable prior verdict.
    # This is a fresh text-only call, not an independent human/model-family judge.
    content={'tone':tone,'messages':[{'id':u['id'],'speaker':u['speaker'],'text':u['text']} for u in script['units']],
        'task':'Read this unlabelled conversation as a cold reader. Reconstruct its specific opening question and actual ending answer. '
        'List every missing assumption a viewer must invent. Then assess ALL seven criteria with an exact existing message quote each. '
        'opening: specific intelligible curiosity, not compulsory danger/contradiction. cause: explain why this behavior happens and why now; identity alone is not motive. '
        'knowledge: private contacts cannot know unseen messages without being told. progression: distinct changes in evidence/leverage, not repetitive guesses or disbelief. '
        'voice: plausible brief messages and distinct wants, not an essay split into alternating speakers. payoff: last message adds an earned new consequence, not recap, explanation or an arbitrary new prop. '
        'genre: comedy requires a coherent comic mechanism and smaller turns, not random absurdity; mystery requires suspense and a fair causal resolution, not a technical invention; a gentle story needs an earned emotional choice and fulfillment, not a compulsory surprise. '
        'Reject imaginary SMS controls over gates/breakers. Reject a search ending at a random location. A favorable style or correct JSON does not excuse a broken story. '
        'Use revise for substantive weakness; explain the particular defect, not generic praise. Do not rewrite or suggest camera/sound. '
        'No human audience, rendered media or retention measurements were supplied.'}
    if script.get('phone_story'):
        story=script['phone_story'];content['private_conversations']={'pov':story['pov'],'threads':story['threads'],'contacts':story['contacts'],'beats':story['beats']}
    result=provider.generate('chat-cold-reader-v2',content,DIAGNOSTIC_SCHEMA)
    if not isinstance(result,dict) or set(result)!=set(DIAGNOSTIC_SCHEMA['properties']):raise Held('chat_review_invalid','Cold reader omitted its reconstruction or criteria.')
    for field in ('reader_question','reader_answer'):
        if not isinstance(result[field],str) or not 1<=len(result[field])<=1800:raise Held('chat_review_invalid','Cold reader needs a bounded reconstruction.')
    missing=result['missing_assumptions'];checks=result['checks'];units={u['id']:u['text'] for u in script['units']}
    if not isinstance(missing,list) or len(missing)>8 or any(not isinstance(s,str) or not 1<=len(s)<=600 for s in missing):raise Held('chat_review_invalid','Invalid missing-assumption list.')
    if not isinstance(checks,dict) or set(checks)!=set(CRITERIA):raise Held('chat_review_invalid','Assess every writing criterion explicitly.')
    issues=list(missing)
    for name,check in checks.items():
        if (not isinstance(check,dict) or set(check)!=set(CHECK_SCHEMA['properties']) or check['verdict'] not in ('pass','revise') or
            not isinstance(check['unit_id'],str) or check['unit_id'] not in units or check['quote']!=units[check['unit_id']] or
            not isinstance(check['reason'],str) or not 1<=len(check['reason'])<=1200):raise Held('chat_review_invalid','Every criterion must quote real dialogue and explain its judgment.')
        if check['verdict']=='revise':issues.append(name+': '+check['reason'])
    final=script['units'][-1]
    if checks['payoff']['unit_id']!=final['id']:raise Held('chat_review_invalid','Assess the actual final message as the ending.')
    normalized=lambda s:' '.join(s.casefold().split()).rstrip('.!?')
    if normalized(final['text']) in {normalized(u['text']) for u in script['units'][:-1]}:issues.append('The last message repeats an earlier message verbatim.')
    return {**result,'passes':not issues,'issues':issues,'scope':'Cold text reading; same provider, no independent human approval.'}


def critique(provider,script,tone):
    result=provider.generate('chat-script-review-v1',{'script':script,'tone':tone,
        'task':'Judge writing only. Quote the actual opening, an early planted clue, and the designated final payoff exactly. '
        'Check private-chat knowledge/chronology, natural distinct replies, specific curiosity and a fair non-redundant resolution. '
        'For comedy: name the conflicting wants and coherent comic mechanism in your reason. A place-by-place search followed by a random object location is not an earned joke; reject it. The clue MUST occur in the first third, not be a last-minute hint. Check smaller distinct turns and a new planted implication at the ending. For thriller/mystery check suspense, character motive and causal resolution. '
        'For mystery/thriller explicitly test the cause: why did the sender send the OPENING message in that wording, why now, and what do they want? Merely naming the sender or revealing they possess a key is not a motive or causal answer. A vague request to ask someone else is not itself a planted explanation. Check every character knows only what their private messages establish. Reject before approving if a normal reader must invent the missing cause. In a grounded story, ordinary SMS cannot secretly hold gates open, operate utility breakers or control physical equipment; reject invented technical powers used to force the payoff. A cliffhanger is acceptable only AFTER the main opening question is answered. Reject filler, arbitrary reveals and contradictions. '
        'No editing directions, self-praise or claims about rendered quality/retention. Return concrete issues when failing.'},REVIEW_SCHEMA)
    if not isinstance(result,dict) or set(result)!=set(REVIEW_SCHEMA['properties']) or type(result['passes']) is not bool:
        raise Held('chat_review_invalid','Script critique has an invalid contract.')
    if (not isinstance(result['issues'],list) or len(result['issues'])>8 or
            any(not isinstance(s,str) or len(s)>600 for s in result['issues']) or
            not isinstance(result['reason'],str) or not 1<=len(result['reason'])<=1800):
        raise Held('chat_review_invalid','Script critique needs bounded reasons and issues.')
    units={u['id']:u for u in script['units']}
    for prefix in ('opening','payoff','clue'):
        uid=result[prefix+'_unit_id'];quote=result[prefix+'_quote']
        if not isinstance(uid,str) or uid not in units or quote!=units[uid]['text']:
            raise Held('chat_review_invalid','Critique must quote existing script units exactly; invented evidence is refused.')
    if result['opening_unit_id']!=script['units'][0]['id'] or result['payoff_unit_id']!=script['edit']['payoff_unit_id']:
        raise Held('chat_review_invalid','Critique did not assess the actual opening and designated payoff.')
    clue_index=next(i for i,u in enumerate(script['units']) if u['id']==result['clue_unit_id'])
    if clue_index>=max(2,len(script['units'])//3):
        result={**result,'issues':[*result['issues'],'The quoted clue occurs after the first third; plant a useful clue earlier.']}
    return {**result,'passes':result['passes'] and not result['issues'],'scope':'writing only; model judgment is not owner approval'}


def reviewed_script(provider,script,brief,schema,validate,tone,*,context=None,version=1):
    review_fn=diagnose if version==2 else critique
    review=review_fn(provider,script,tone)
    if review['passes']:return script,{'initial':review,'revisions':0}
    raw=provider.generate('chat-script-revision-v2' if version==2 else 'chat-script-revision-v1',{'draft':script,'brief':brief,'critique':review,'writing_constraints':context,
        'task':'Revise the complete story once to fix these writing issues. Preserve the supplied JSON/phone contract and all format bounds. '
        'Preserve the owner constraints and private-chat chronology. If the premise/cause is broken, rebuild it rather than polishing the same faulty ending. '
        'No editing commands or claim of quality. Return the whole revised script.','required_contract':schema},schema)
    revised=validate(raw);final=review_fn(provider,revised,tone)
    if not final['passes']:raise Held('chat_writing_quality','Revised story still fails writing review: '+'; '.join(final['issues'])[:900])
    return revised,{'initial':review,'final':final,'revisions':1}
