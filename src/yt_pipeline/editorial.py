"""The owner's agreed channel scope, shared by research and scripting."""
import re
from .core import Held

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
