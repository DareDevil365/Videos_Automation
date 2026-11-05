"""Content-grounded packaging: useful choices, never an algorithm/virality claim."""
from .core import Held


EVIDENCE={'type':'object','additionalProperties':False,'required':['unit_id','quote'],
    'properties':{'unit_id':{'type':'string'},'quote':{'type':'string'}}}
CANDIDATE={'type':'object','additionalProperties':False,'required':['title','angle','evidence'],
    'properties':{'title':{'type':'string'},'angle':{'type':'string','enum':['searchable','curiosity','emotional']},
                  'evidence':{'type':'array','items':EVIDENCE}}}
SCHEMA={'type':'object','additionalProperties':False,'required':['titles','selected_index','description','description_evidence','keywords','reason'],
    'properties':{'titles':{'type':'array','items':CANDIDATE},'selected_index':{'type':'integer'},
        'description':{'type':'string'},'description_evidence':{'type':'array','items':EVIDENCE},
        'keywords':{'type':'array','items':{'type':'string'}},'reason':{'type':'string'}}}


def validate_metadata(value,script):
    if not isinstance(value,dict) or set(value)!=set(SCHEMA['required']):raise Held('metadata_contract','Metadata needs three grounded titles and a concise description.')
    titles=value['titles'];units={u['id']:u['text'] for u in script['units']}
    def evidence(rows):
        if not isinstance(rows,list) or not 1<=len(rows)<=4:raise Held('metadata_evidence','Quote one to four actual script messages for each claim/angle.')
        for row in rows:
            if (not isinstance(row,dict) or set(row)!={'unit_id','quote'} or not isinstance(row['unit_id'],str)
                    or row['unit_id'] not in units or row['quote']!=units[row['unit_id']]):
                raise Held('metadata_evidence','Metadata evidence must quote actual script text exactly.')
    if not isinstance(titles,list) or len(titles)!=3:raise Held('metadata_contract','Supply exactly three title alternatives.')
    seen=set()
    for candidate in titles:
        if not isinstance(candidate,dict) or set(candidate)!=set(CANDIDATE['required']):raise Held('metadata_contract','Invalid title candidate.')
        title=candidate['title']
        if not isinstance(title,str) or not 1<=len(title.strip())<=100 or any(c in title for c in '<>\n\r'):raise Held('metadata_title','Titles need 1-100 characters and no markup/newlines.')
        if title.casefold().strip() in seen:raise Held('metadata_title','Use distinct title alternatives.')
        seen.add(title.casefold().strip())
        if candidate['angle'] not in ('searchable','curiosity','emotional'):raise Held('metadata_contract','Unknown title angle.')
        evidence(candidate['evidence'])
    index=value['selected_index']
    if type(index) is not int or not 0<=index<3:raise Held('metadata_contract','Select one of the three titles.')
    description=value['description'];keywords=value['keywords']
    if not isinstance(description,str) or not 15<=len(description.strip())<=900 or '<' in description or '>' in description:raise Held('metadata_description','Use a bounded plain-language description.')
    if not isinstance(keywords,list) or not 1<=len(keywords)<=2 or any(not isinstance(k,str) or not 1<=len(k)<=60 for k in keywords):raise Held('metadata_contract','Choose one or two relevant subject phrases.')
    if not isinstance(value['reason'],str) or not 1<=len(value['reason'])<=600:raise Held('metadata_contract','Explain the selected audience angle briefly.')
    evidence(value['description_evidence'])
    return {**value,'title':titles[index]['title'].strip(),'description':description.strip(),
        'origin':'model_content_packaging_v1','limits':'Exact evidence checks establish source linkage, not semantic truth, audience preference or reach.'}


def make_metadata(provider,script,request):
    prompt={'task':'Create accurate YouTube packaging for the finished script. Return exactly three DISTINCT title alternatives, select one and write a unique 1-3 sentence description. '
        'Use a searchable, curiosity or emotional angle suited to the genre. Put a specific situation/consequence first; preserve the ending when appropriate. '
        'Titles must deliver the promise in THIS video. Descriptions begin with what happens here, using 1-2 natural subject phrases, not a keyword wall. '
        'Never append unrelated trending text, electricity/footstep/Japan copy, fake true-story claims, famous creators, invented numbers, guaranteed reach or a false cliffhanger. '
        'Do not add hashtags, credits, sources, URLs or AI disclosures; software appends required provenance. Quote actual complete script units as evidence for every title and the description. '
        'The quotes prove traceability only: critically check the wording does not make a bigger claim than those units support. Selection is a creative hypothesis, not a measured winner.',
        'script':script,'genre':request.get('chat_tone',request.get('playbook','story')),
        'audience':request.get('audience','English-speaking viewers of short entertainment stories')}
    raw=provider.generate('publication-metadata-v1',prompt,SCHEMA)
    return validate_metadata(raw,script)
