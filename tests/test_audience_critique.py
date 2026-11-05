import pytest

from shorts_editor.store import write_json
from yt_pipeline.audience_critique import critique_job,role_for,validate_critique
from yt_pipeline.core import Held,Workspace,file_hash


SCRIPT={'format':'lesson','fiction':False,'title':'Do not give the critic the sales pitch','units':[
    {'id':'u1','speaker':'Narrator','text':'Doom kept the pieces.','onscreen':'Doom','claim_ids':['c1']},
    {'id':'u2','speaker':'Narrator','text':'Then some more things happened.','onscreen':'Next','claim_ids':[]}]}


def finding(frame_id=''):
    return {'would_continue':False,'first_attention_loss_unit_id':'u2','reason':'The second beat becomes vague.',
        'findings':[{'unit_id':'u2','quote':SCRIPT['units'][1]['text'],'severity':'major','dimension':'attention',
        'problem':'The beat gives no new event.','why_leave':'I still do not know what changed.','fix':'Show the first consequence.','frame_id':frame_id}]}


def test_script_critic_persists_exact_findings_without_changing_job(tmp_path):
    ws=Workspace(tmp_path/'ws');job=ws.create('entertainment',{'playbook':'comic_lore'});folder=ws.job_dir(job['id'])
    paths={'script':{'script':SCRIPT},'research':{'claims':[],'sources':[]}}
    for k,v in paths.items():write_json(folder/(k+'.json'),v)
    ws.update(job['id'],artifacts={k:{'path':str(folder/(k+'.json')),'sha256':file_hash(folder/(k+'.json'))} for k in paths})
    before=ws.get(job['id'])
    class Critic:
        name='fixture'
        def generate(self,purpose,prompt,schema):
            assert purpose=='audience-critique-v1-comic-lore-script'
            assert 'canon' in prompt['focus'] and 'title' not in prompt and not prompt['samples']
            return finding()
    report=critique_job(ws,job['id'],Critic())
    assert report['outcome']=='revise' and report['first_attention_loss_unit_id']=='u2'
    assert 'timestamp_seconds' not in report['findings'][0] and ws.get(job['id'])==before


def test_no_invented_quote_or_timestamp_and_frame_must_match_unit():
    raw=finding();raw['findings'][0]['quote']='Never spoken.'
    with pytest.raises(Held):validate_critique(raw,SCRIPT)
    with pytest.raises(Held):validate_critique(finding('f1'),SCRIPT)
    sample={'frame_id':'f1','unit_id':'u1','time':4.2,'sha256':'frame'}
    with pytest.raises(Held):validate_critique(finding('f1'),SCRIPT,[sample])
    sample['unit_id']='u2'
    assert validate_critique(finding('f1'),SCRIPT,[sample])['findings'][0]['timestamp_seconds']==4.2


@pytest.mark.parametrize(('playbook','role'),[('comic_lore','comic-lore'),('movie_brief','movie'),('current_affairs','current-affairs'),('ai_tools','ai-tools')])
def test_roles_are_selected_by_content(playbook,role):
    assert role_for({'playbook':playbook},SCRIPT)==role
