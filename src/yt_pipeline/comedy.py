"""Bounded original-comedy planning and script critique; no reference dialogue."""
from .core import Held

STRING={'type':'string'}
CONCEPT_SCHEMA={'type':'object','properties':{'concepts':{'type':'array','minItems':3,'maxItems':3,'items':{'type':'object','properties':{
    'id':STRING,'hook':STRING,'goal':STRING,'escalation':STRING,'planted_detail':STRING,'final_punchline':STRING,'consequence':STRING},
    'required':['id','hook','goal','escalation','planted_detail','final_punchline','consequence'],'additionalProperties':False}}},'required':['concepts'],'additionalProperties':False}
REVIEW_SCHEMA={'type':'object','properties':{'passes':{'type':'boolean'},'punchline_unit_id':STRING,'punchline_exact_text':STRING,
    'setup_unit_id':STRING,'reversal_explanation':STRING,'works_with_static_cast':{'type':'boolean'},'issues':{'type':'array','items':STRING}},
    'required':['passes','punchline_unit_id','punchline_exact_text','setup_unit_id','reversal_explanation','works_with_static_cast','issues'],'additionalProperties':False}


def choose_concept(provider,request):
    candidates=provider.generate('comedy-concepts-v1',{'topic':request.get('topic'),'brief':request.get('creative_brief','')[:2000],
        'reference_mechanics':request.get('reference_mechanics',[]),
        'task':'Propose THREE DISTINCT original short comedy concepts for two talking animal-headed humans Alex/Mike. Use everyday things and plain words a twelve-year-old understands. Hook at most 14 words, final punchline at most 18 words. No abstract legal/financial jargon about licenses, monetization, portfolios, royalties, projections or copyright. Each opens directly on a concrete absurd conflict, not greetings or a generic question. A character pursues a sensible goal by a bad strategy, the other exploits its precise logic, and the final line reverses power or causes a specific consequence. Plant a detail used at the end. State the exact prospective final punchline; no reactions after it. No elevator/intercom/phone malfunction/misunderstood audio/podcast, no twins/hackers/dreams. Static cast and captions only, so no joke relying on an unseen stunt. No borrowed creator lines, catchphrases, premise, signature characters or quotations. The reference mechanics are general structural observations, not a script to paraphrase.'},CONCEPT_SCHEMA)
    eligible=[c for c in candidates.get('concepts',[]) if len(c.get('hook','').split())<=14 and len(c.get('final_punchline','').split())<=18]
    if not eligible:raise Held('comedy_concept','No short plain-language hook/punchline candidate; revise the concept brief')
    schema={'type':'object','properties':{'selected_id':STRING,'reason':STRING,'passes':{'type':'boolean'},'issues':{'type':'array','items':STRING}},'required':['selected_id','reason','passes','issues'],'additionalProperties':False}
    verdict=provider.generate('comedy-concept-selector-v1',{'candidates':eligible,'task':'Pick the clearest genuine reversal/payoff, not merely the most words. Prefer familiar objects and simple language, not legal/business jargon dressed up as a joke. Reject a banal explanation, nonsensical ending, unplanted solution or joke requiring an unseen prop/action. Do not reward calling it funny. If all fail, passes=false. Do not write dialogue.'},schema)
    chosen=next((c for c in eligible if c.get('id')==verdict.get('selected_id')),None)
    if not chosen or verdict.get('passes') is not True or verdict.get('issues'):raise Held('comedy_concept','No candidate passed the bounded comedy concept review')
    return {'selected':chosen,'candidates':candidates,'selection':verdict}


def review_comedy(provider,script,concept):
    if len(script['units'][0]['text'].split())>14 or any(len(u['text'].split())>22 for u in script['units']) or len(script['units'][-1]['text'].split())>18:
        raise Held('creative_review','Use a specific hook of at most 14 words, short dialogue turns (at most 22 words), and a final punchline of at most 18 words; avoid explanatory jargon')
    result=provider.generate('comedy-script-review-v1',{'script':script,'concept':concept,
        'task':'Be a skeptical comedy editor. Inspect the ACTUAL spoken lines. Hook must give the specific conflict in the first line, not metadata. Identify the exact last/penultimate punchline and the earlier line planting it. Explain the reversal or concrete comic consequence. A normal explanation of a noise/device, polite reaction, mystery solved, or routine arrival is NOT a comic payoff. Reject if the setup is not paid off, premise contradicts itself, end merely explains normal events, joke needs unseen action, or dialogue narrates rather than interacts. Require a payoff that changes the situation or turns the opening rule against its maker. No flattery or automatic passes.'},REVIEW_SCHEMA)
    units={u['id']:u for u in script['units']};payoff=units.get(result.get('punchline_unit_id'))
    if (result.get('passes') is not True or result.get('works_with_static_cast') is not True or result.get('issues') or
        not payoff or payoff['text']!=result.get('punchline_exact_text') or payoff['id']!=script['edit']['payoff_unit_id'] or
        result.get('setup_unit_id') not in units or result['setup_unit_id']==payoff['id'] or len(result.get('reversal_explanation',''))<20):
        raise Held('creative_review','Comedy payoff failed: '+'; '.join(result.get('issues',[]))[:500]+'; identify a planted setup and an actual final punchline/consequence, not a normal explanation')
    return result
