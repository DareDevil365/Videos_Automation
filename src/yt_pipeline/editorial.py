"""The owner's agreed channel scope, shared by research and scripting."""
import re
import json
from pathlib import Path
from .core import Held,digest,now,file_hash
from shorts_editor.store import write_json


def creative_feedback(workspace,playbook):
    path=workspace.root/'creative-feedback.json'
    if not path.exists():return []
    if path.stat().st_size>2_000_000:raise Held('creative_feedback','Owner feedback file exceeded its bounded input size.')
    try:data=json.loads(path.read_text(encoding='utf-8'))
    except (ValueError,UnicodeError):raise Held('creative_feedback','Owner feedback must be valid UTF-8 JSON.')
    if not isinstance(data,dict) or data.get('version')!=1 or not isinstance(data.get('records'),list):
        raise Held('creative_feedback','Owner feedback records have an invalid format.')
    latest={}
    for row in data['records']:
        if not isinstance(row,dict) or row.get('verdict') not in ('accepted','rejected','needs_revision') or not isinstance(row.get('script_hash'),str):
            raise Held('creative_feedback','An owner feedback record is malformed.')
        if row.get('playbook')==playbook:latest[row['script_hash']]=row
    return list(latest.values())


def check_script_feedback(workspace,script,playbook):
    feedback=creative_feedback(workspace,playbook)
    value=digest(' '.join(u['text'].lower() for u in script['units']))
    if any(row['script_hash']==value and row['verdict']=='rejected' for row in feedback):
        raise Held('owner_rejected','The owner rejected this exact script. A model pass cannot override that feedback; generate a different story.')
    return feedback[-4:]


def record_creative_feedback(workspace,job_id,verdict,reason):
    if verdict not in ('accepted','rejected','needs_revision') or not isinstance(reason,str) or not 1<=len(reason.strip())<=1000:
        raise ValueError('Feedback needs an accepted/rejected/needs_revision verdict and a 1-1000 character reason.')
    job=workspace.get(job_id);artifact=job['artifacts'].get('script')
    if not artifact or file_hash(artifact['path'])!=artifact['sha256']:
        raise Held('creative_feedback','Record feedback against an intact saved script checkpoint.')
    written=json.loads(Path(artifact['path']).read_text(encoding='utf-8'));script=written['script']
    row={'job_id':job_id,'at':now(),'channel':job['channel'],'playbook':job['request'].get('playbook'),
        'script_hash':digest(' '.join(u['text'].lower() for u in script['units'])),'title':script['title'],
        'verdict':verdict,'reason':reason.strip(),'dialogue':'\n'.join(u['speaker']+': '+u['text'] for u in script['units'])[:3000]}
    path=workspace.root/'creative-feedback.json'
    # Validate existing records before changing them; preserve other jobs' feedback.
    creative_feedback(workspace,job['request'].get('playbook'))
    data=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'version':1,'records':[]}
    data['records']=[r for r in data['records'] if r['job_id']!=job_id]+[row]
    if len(data['records'])>200:raise Held('creative_feedback','Archive owner feedback explicitly before adding more than 200 job records.')
    write_json(path,data)
    return {k:v for k,v in row.items() if k!='dialogue'}

EDUCATION_STYLE='Broad-audience Shorts about procrastination, studying, confidence, job preparation, realistic earning skills, and everyday/free AI tools. Relatable situation first, plain language, one practical takeaway; no specialist programming lectures.'
EDUCATION_POLICY={
    'pillars':['procrastination and task initiation','effective studying','confidence and everyday communication',
               'job search and interviews','realistic earning skills','useful AI and free AI tools','accessible general knowledge'],
    'presentation':'A specific everyday problem, a short concrete example, one usable action and a complete payoff. Usually 20–40 seconds. Short caption phrases, not a textbook chapter.',
    'avoid':['specialist coding/computer-science explanations unless explicitly requested as a technical demo',
             'fabricated earnings, job openings, testimonials or personal tool tests','guaranteed psychological, study or income outcomes'],
    'visuals':'Literal photo/clip search phrases showing the situation or action. Illustrative stock people do not endorse our advice.'}

HOOK_FRAMEWORKS=[
    {'name':'specific recognizable scene','pattern':'Concrete tiny behaviour → recognizable cost → a useful change','example':'Ten minutes picking a playlist. Zero minutes on the assignment.'},
    {'name':'before and after','pattern':'Show the weak attempt, then repair it visibly','example':'This interview answer lists a skill. This one shows it.'},
    {'name':'prediction and reveal','pattern':'Give a small example, invite a guess, reveal the answer','example':'Close the notes. Can you answer this one question?'},
    {'name':'missing step','pattern':'Name an appealing workflow, reveal the real missing work','example':'The AI draft is done. The job is not.'},
    {'name':'skeptical value reaction','pattern':'Verified surprising fact → opinionated question → actual evidence/configuration → useful tradeoff','example':'That much for a laptop? Who is this configuration actually for?'},
    {'name':'concrete friction','pattern':'Show an everyday obstacle, then one bounded action','example':'Your task says finish the project. What do you actually click first?'},
    {'name':'franchise what-if','pattern':'Clearly label a hypothetical twist and trace its consequences','example':'What if this character made the opposite choice? A fan theory.'}]


def editorial_context(job):
    if job['channel']!='education':return {'direction':'Original fictional chat, storytime, permitted creator/aura edits and movie recommendations; preserve source context and label fiction.'}
    request=job['request']
    topic=str(request.get('topic',''))
    supplied=bool(request.get('script') or request.get('script_file') or request.get('brief') or request.get('brief_file'))
    if not supplied and not request.get('technical_demo') and re.search(r'floating.?point|binary fractions|python|javascript|algorithm complexity|data structures',topic,re.I):
        raise Held('off_strategy','This topic is a specialist technical lesson. Use the agreed broad-audience education pillars, or explicitly mark a technical demonstration.')
    return {**EDUCATION_POLICY,'hook_frameworks':HOOK_FRAMEWORKS[:-1],
            'hook_rules':'Avoid Have you ever, Ever wondered, Did you know, generic question openers and introductions. Use a specific familiar situation or visible contrast immediately. No fake urgency or guaranteed results. Choose a different suitable framework across episodes.'}
