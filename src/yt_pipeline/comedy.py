"""Bounded original-comedy planning and script critique; no reference dialogue."""
from .core import Held
from copy import deepcopy

STRING={'type':'string'}
CONCEPT_SCHEMA={'type':'object','properties':{'concepts':{'type':'array','minItems':3,'maxItems':3,'items':{'type':'object','properties':{
    'id':STRING,'hook':STRING,'goal':STRING,'escalation':STRING,'planted_detail':STRING,'final_punchline':STRING,'consequence':STRING},
    'required':['id','hook','goal','escalation','planted_detail','final_punchline','consequence'],'additionalProperties':False}}},'required':['concepts'],'additionalProperties':False}
REVIEW_SCHEMA={'type':'object','properties':{'passes':{'type':'boolean'},'punchline_unit_id':STRING,'punchline_exact_text':STRING,
    'setup_unit_id':STRING,'reversal_explanation':STRING,'works_with_static_cast':{'type':'boolean'},'issues':{'type':'array','items':STRING}},
    'required':['passes','punchline_unit_id','punchline_exact_text','setup_unit_id','reversal_explanation','works_with_static_cast','issues'],'additionalProperties':False}


def choose_concept(provider,request):
    from .editorial import creative_feedback
    feedback=creative_feedback(provider.workspace,request.get('playbook'))[-4:] if hasattr(provider,'workspace') else []
    scene_mode=request.get('scene_direction_version',1)==2
    chat_mode=request.get('playbook')=='server_chat'
    schema=deepcopy(CONCEPT_SCHEMA)
    if scene_mode:
        concept_schema=schema['properties']['concepts']['items']
        concept_schema['properties']['visual_beats']={'type':'array','minItems':2,'maxItems':4,'items':{'type':'string','maxLength':160}}
        concept_schema['required'].append('visual_beats')
    candidates=provider.generate('comedy-concepts-v1',{'topic':request.get('topic'),'brief':request.get('creative_brief','')[:2000],
        'reference_mechanics':request.get('reference_mechanics',[]),
        'owner_feedback':feedback,'owner_feedback_policy':'Do not recycle a rejected story by paraphrasing or renaming its characters. Respect the specific criticism; a model opinion cannot overrule owner rejection.',
        'chat_direction':('This is a short group-chat comedy: the messages themselves are the scene. Invent a relatable everyday conflict between 2-3 people with opposite goals, then an earned consequence/reversal that is enacted by the final message. A culprit simply admitting they ate the food is a confession, not a comic reversal. A technically impossible bot banning its owner is not a coherent payoff. Avoid food-theft investigations, moderation, bans, hacks and magic. No copied creator cast/plot/catchphrases. Use short casual messages, no stiff explanatory padding; your final line must change the situation. All action must be understandable from messages alone. Invent all three premises independently and choose a precise planted detail that matters at the end.' if chat_mode else None),
        'scene_direction':('Design a two-person scene with distinct personalities and a concrete conflict. Each concept must list 2-4 visible beats including the shared interaction and any essential real animal/object/action insert. A strange animal/job label is not itself a joke. Escalation must change the situation; a routine explanation, predictable bribe or random final fact is too weak. Require an earned consequence or reversal of the opening assumption. Prefer visual beats that can be illustrated with ordinary licensed photos/clips; no joke depending on unavailable stunts or fabricated footage. Hook at most twelve words. Narrator is optional voiceover; do not give every line a new character.' if scene_mode else None),
        'task':'Propose THREE DISTINCT original short comedy concepts for two recurring characters. Use everyday things and plain words a twelve-year-old understands. Hook at most 14 words, final punchline at most 18 words. No abstract legal/financial jargon about licenses, monetization, portfolios, royalties, projections or copyright. Each opens directly on a concrete absurd conflict, not greetings or a generic question. A character pursues a sensible goal by a bad strategy, the other exploits its precise logic, and the final line reverses power or causes a specific consequence. Plant a detail used at the end. State the exact prospective final punchline; no reactions after it. No elevator/intercom/phone malfunction/misunderstood audio/podcast, no twins/hackers/dreams. No joke relying on an unseen stunt. No borrowed creator lines, catchphrases, premise, signature characters or quotations. The reference mechanics are general structural observations, not a script to paraphrase.'},schema)
    eligible=[c for c in candidates.get('concepts',[]) if len(c.get('hook','').split())<=(12 if scene_mode else 14) and len(c.get('final_punchline','').split())<=18
        and (not scene_mode or isinstance(c.get('visual_beats'),list) and 2<=len(c['visual_beats'])<=4
             and all(isinstance(v,str) and 1<=len(v.strip())<=160 for v in c['visual_beats']))]
    if not eligible:raise Held('comedy_concept','No short plain-language hook/punchline candidate; revise the concept brief')
    schema={'type':'object','properties':{'selected_id':STRING,'reason':STRING,'passes':{'type':'boolean'},'issues':{'type':'array','items':STRING}},'required':['selected_id','reason','passes','issues'],'additionalProperties':False}
    verdict=provider.generate('comedy-concept-selector-v1',{'candidates':eligible,'scene_direction_version':2 if scene_mode else 1,'task':'Pick the clearest genuine reversal/payoff, not merely the most words. Prefer familiar objects and simple language, not legal/business jargon dressed up as a joke. Reject a banal explanation, nonsensical ending, unplanted solution, predictable routine payment/bribe, random animal quirk, or joke requiring an unseen prop/action. An absurd premise alone is insufficient. Compare the exact proposed ending to its planted setup and the actual consequence. In scene mode inspect visual_beats: people interacting and necessary inserts must make sense. Do not reward calling it funny. If all fail, passes=false. Do not write dialogue.'},schema)
    chosen=next((c for c in eligible if c.get('id')==verdict.get('selected_id')),None)
    if not chosen or verdict.get('passes') is not True or verdict.get('issues'):raise Held('comedy_concept','No candidate passed the bounded comedy concept review')
    return {'selected':chosen,'candidates':candidates,'selection':verdict}


def review_comedy(provider,script,concept,*,scene_mode=False,chat_mode=False):
    from .editorial import check_script_feedback
    feedback=check_script_feedback(provider.workspace,script,'server_chat' if chat_mode else 'cutout_ensemble') if hasattr(provider,'workspace') else []
    if len(script['units'][0]['text'].split())>14 or any(len(u['text'].split())>22 for u in script['units']) or len(script['units'][-1]['text'].split())>18:
        raise Held('creative_review','Use a specific hook of at most 14 words, short dialogue turns (at most 22 words), and a final punchline of at most 18 words; avoid explanatory jargon')
    result=provider.generate('comedy-script-review-v1',{'script':script,'concept':concept,
        'owner_feedback':feedback,
        'chat_payoff_check':('The actual final line must deliver the comic consequence or turn the opening setup against a character. Reject an ordinary confession, a culprit admitting the obvious, an arbitrary insult, a disconnected random fact, a merely explained technical mechanism, or an unsupported gotcha. An earnest investigation plus an admission is not enough. Verify causality and short natural texting language. Identify the exact planted setup and the exact funny reversal; if the words do not support them, fail. No assumed visuals or unspoken action. works_with_static_cast here means the chat messages alone communicate the complete joke.' if chat_mode else None),
        'scene_direction':('The editor supports two-person shots, distinct outfits/poses and literal licensed animal/object/action inserts. Static character acting is still limited: no lip sync or full rig. Check that essential visual actions have a plausible insert rather than being described while only swapping faces. Do not treat an animal doing an ordinary thing or a predictable bribe/explanation as a sufficient punchline. Require clear cause, escalation, a planted detail and a specific consequence/reversal in the actual final line. works_with_static_cast means feasible with these simple actors plus real inserts, not that every shot must be a head closeup.' if scene_mode else None),
        'task':'Be a skeptical comedy editor. Inspect the ACTUAL spoken lines. Hook must give the specific conflict in the first line, not metadata. Identify the exact last/penultimate punchline and the earlier line planting it. Explain the reversal or concrete comic consequence. A normal explanation of a noise/device, polite reaction, mystery solved, or routine arrival is NOT a comic payoff. Reject if the setup is not paid off, premise contradicts itself, end merely explains normal events, joke needs unseen action, or dialogue narrates rather than interacts. Require a payoff that changes the situation or turns the opening rule against its maker. No flattery or automatic passes.'},REVIEW_SCHEMA)
    units={u['id']:u for u in script['units']};payoff=units.get(result.get('punchline_unit_id'))
    if (result.get('passes') is not True or result.get('works_with_static_cast') is not True or result.get('issues') or
        not payoff or payoff['text']!=result.get('punchline_exact_text') or payoff['id']!=script['edit']['payoff_unit_id'] or
        result.get('setup_unit_id') not in units or result['setup_unit_id']==payoff['id'] or len(result.get('reversal_explanation',''))<20):
        raise Held('creative_review','Comedy payoff failed: '+'; '.join(result.get('issues',[]))[:500]+'; identify a planted setup and an actual final punchline/consequence, not a normal explanation')
    return result
