"""Writing-only critique with exact evidence and one bounded revision."""
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


def reviewed_script(provider,script,brief,schema,validate,tone):
    review=critique(provider,script,tone)
    if review['passes']:return script,{'initial':review,'revisions':0}
    raw=provider.generate('chat-script-revision-v1',{'draft':script,'brief':brief,'critique':review,
        'task':'Revise the complete story once to fix these writing issues. Preserve the supplied JSON/phone contract and all format bounds. '
        'No editing commands or claim of quality. Return the whole revised script.','required_contract':schema},schema)
    revised=validate(raw);final=critique(provider,revised,tone)
    if not final['passes']:raise Held('chat_writing_quality','Revised story still fails writing review: '+'; '.join(final['issues'])[:900])
    return revised,{'initial':review,'final':final,'revisions':1}
