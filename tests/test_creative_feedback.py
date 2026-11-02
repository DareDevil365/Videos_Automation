import json

import pytest

from shorts_editor.store import write_json
from yt_pipeline.core import Workspace,Held,file_hash
from yt_pipeline.editorial import record_creative_feedback,creative_feedback,check_script_feedback
from yt_pipeline.comedy import review_comedy,choose_concept


def saved_script(ws,index=0):
    job=ws.create('entertainment',{'playbook':'cutout_ensemble','fiction':True,'topic':'Technical feedback fixture'})
    script={'title':f'Feedback fixture {index}','units':[{'id':'u1','speaker':'Actor','text':f'Technical fixture number {index}.'}]}
    path=ws.job_dir(job['id'])/'script.json';path.parent.mkdir(exist_ok=True)
    write_json(path,{'script':script,'origin':'provided_script'})
    ws.update(job['id'],artifacts={'script':{'path':str(path),'sha256':file_hash(path),'files':{}}})
    return job,script,path


def test_owner_rejection_blocks_a_model_pass_before_any_call(tmp_path):
    ws=Workspace(tmp_path/'ws');job,script,path=saved_script(ws);original=path.read_bytes()
    record_creative_feedback(ws,job['id'],'rejected','The owner rejected the story.')
    class Provider:
        workspace=ws
        def generate(self,*args):pytest.fail('Owner rejection must not be sent back for model approval')
    with pytest.raises(Held) as error:review_comedy(Provider(),script,None,scene_mode=True)
    assert error.value.code=='owner_rejected' and path.read_bytes()==original


def test_rejections_remain_binding_after_the_prompt_examples_are_bounded(tmp_path):
    ws=Workspace(tmp_path/'ws');job,script,_=saved_script(ws)
    record_creative_feedback(ws,job['id'],'rejected','Rejected original fixture.')
    for i in range(1,6):
        other,_,_=saved_script(ws,i);record_creative_feedback(ws,other['id'],'accepted','Different accepted fixture.')
    assert len(creative_feedback(ws,'cutout_ensemble'))==6
    with pytest.raises(Held,match='rejected this exact script'):check_script_feedback(ws,script,'cutout_ensemble')


def test_explicit_new_owner_verdict_replaces_old_one_and_revision_is_not_acceptance(tmp_path):
    ws=Workspace(tmp_path/'ws');job,script,_=saved_script(ws)
    record_creative_feedback(ws,job['id'],'rejected','First verdict.')
    record_creative_feedback(ws,job['id'],'accepted','Owner changed the verdict.')
    assert check_script_feedback(ws,script,'cutout_ensemble')[0]['verdict']=='accepted'
    record_creative_feedback(ws,job['id'],'needs_revision','Visual revision requested.')
    records=check_script_feedback(ws,script,'cutout_ensemble')
    assert len(records)==1 and records[0]['verdict']=='needs_revision'


def test_feedback_does_not_attach_to_a_changed_checkpoint(tmp_path):
    ws=Workspace(tmp_path/'ws');job,_,path=saved_script(ws)
    path.write_text('{}',encoding='utf-8')
    with pytest.raises(Held,match='intact'):record_creative_feedback(ws,job['id'],'rejected','Changed fixture.')
    assert not (ws.root/'creative-feedback.json').exists()


def test_scene_comedy_rejects_unplanned_visuals_before_concept_selection():
    calls=[]
    class Provider:
        def generate(self,purpose,content,schema):
            calls.append(purpose)
            assert purpose=='comedy-concepts-v1'
            assert 'visual_beats' in schema['properties']['concepts']['items']['required']
            return {'concepts':[{'id':str(i),'hook':'Technical hook.','final_punchline':'Technical ending.'} for i in range(3)]}
    with pytest.raises(Held) as error:choose_concept(Provider(),{'scene_direction_version':2})
    assert error.value.code=='comedy_concept' and calls==['comedy-concepts-v1']
