"""Save a bounded standalone demo plan with a fresh public evidence excerpt."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from yt_pipeline.research import page
from yt_pipeline.core import now
from shorts_editor.store import write_json


def main():
    url='https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/'
    source=page(url)
    brief={'version':1,'title':'A clear interview example',
        'question':'How can a vague answer become a specific example?','kind':'fact',
        'sources':[{'id':'mit_star','url':url,'title':source['title'],
                    'excerpt':source['excerpt'],'checked_at':now()}],
        'claims':[{'id':'star','text':'The STAR structure explains the situation, task, personal actions and result when answering behavioral interview questions.','source_id':'mit_star'},
                  {'id':'personal_action','text':'The Action part focuses on the actions the candidate personally took.','source_id':'mit_star'}],
        'notes':'Create original illustrative sample wording, not an invented true personal experience. No hiring guarantees. Do not copy the source example.'}
    request={'fiction':False,'brief':brief,'motion_graphics':True,'visual_review':'required',
        'require_music':False,'bottom_kind':'none','resolution':'720p','test_only':True,
        'creative_brief':('Make a clear, specific job-interview Short with 85-95 words across 8-9 units, targeting 28-35 seconds. '
            'Start immediately with a weak example answer and a sharper alternative; no generic motivational opener. '
            'Show a fictional tiny everyday/teamwork example (explicitly say example/imagine), what the person actually did '
            'and the resulting concrete outcome. No manufactured real testimonial, statistics or guarantee of getting hired. '
            'Do not copy the source example. Keep the STAR framework plain and brief, avoid spending the video spelling acronyms. '
            'Each spoken unit must work as a trusted typographic comparison/process/callout scene: use exact short labels naturally inside that unit. '
            'All scenes for this pilot should have a graphic block, not searched photographs, so we can judge the new supported motion blocks. '
            'Use comparison for a weak/strong distinction, a process for clear short steps, callout only for short emphasis. '
            'Title and labels must be exact phrases in that same unit. End with a visibly improved answer that pays off the opening. '
            'Use a comparison in at least one scene and a process in at least one scene. No stock people or fake UI. '
            'Narrator voice am_adam; brisk, clear and conversational. Keep captions small in the bottom bar.')}
    plan={'version':1,'id':'repo-upgrade-final-2026-11-02','created_at':now(),
        'output_root':str(ROOT/'Resources/Productions'),
        'note':'Standalone Gemini/local-voice/local-motion pilot. Required finished-frame review. Publishing disabled.',
        'items':[{'id':'interview-before-after','kind':'playbook','playbook':'education_demo',
                  'channel':'education','topic':'Turn a vague interview answer into a concrete action and result','request':request}]}
    request['creative_brief']=('Create a practical interview-before/after Short, 85-95 words across 8-9 units. '
        'The entire point is to SHOW a stronger sample answer, not lecture about STAR. '
        'Make up a clearly marked hypothetical cafe teamwork example: a drinks order is wrong, the worker checks the receipt, '
        'tells the teammate exactly what to remake, and gets the corrected drinks to that table. '
        'First spoken line immediately contrasts a vague skill claim with concrete action. '
        'Explicitly introduce the cafe example as an example, not our true work history. '
        'In the final two units SPEAK the improved first-person sample answer in plain words with action and outcome, '
        'not just say now your answer is better. Avoid inventing percentages, testimonials or job guarantees. '
        'Do not copy MITs tutoring example. Do not spend units listing acronyms. '
        'For this motion-block pilot, EVERY unit must be representable as a short original graphic. '
        'Onscreen should hold concise exact phrases that can be selected as labels. '
        'Director: use a graphic in EVERY scene, at least one comparison and one process; other scenes callout. '
        'These are typographic illustrations, no stock or fake tool screenshots. '
        'Narrator am_adam, clear and brisk. Aim measured 28-35 seconds. End on the stronger answer.')
    path=ROOT/'Resources/Plans/repo-upgrade-final.json'
    if path.exists():raise SystemExit('Plan already exists. Use batch-run to resume it; existing plans are immutable.')
    write_json(path,plan)
    print(json.dumps({'plan':str(path),'source_chars':len(source['excerpt'])}))


if __name__=='__main__':main()
