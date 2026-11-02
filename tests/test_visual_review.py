import json
from pathlib import Path
import shutil

from PIL import Image
import pytest

from yt_pipeline.core import Workspace,Held,file_hash
from yt_pipeline.writer import Gemini
from yt_pipeline.assets import register_asset,asset_record
from yt_pipeline.visual_review import review_assets,review_render,validate_observations
from yt_pipeline.scene_blocks import validate_block,render_block
from yt_pipeline.media_library import search_library
from shorts_editor.store import probe


@pytest.fixture
def ws(tmp_path):return Workspace(tmp_path/'workspace')


class Critic:
    def __init__(self,status='pass'):self.status=status;self.calls=[]
    def generate(self,purpose,content,schema,*,images):
        self.calls.append((purpose,content,images))
        assert images and all(Path(p).is_file() for p in images)
        return {'observations':[{'id':row['id'],'status':self.status,'reason':'Inspected labelled frames.',
            'issues':[] if self.status=='pass' else ['Wrong visible subject.']} for row in content['items']]}


def source(ws,tmp_path):
    path=tmp_path/'library.jpg';Image.new('RGB',(500,700),'navy').save(path)
    return register_asset(ws,path,'original_graphic',{'title':'Dark library night','query':'empty library'})


def test_multimodal_request_contains_actual_pixels_and_content_bound_cache(ws,tmp_path,monkeypatch):
    config=ws.config();config['gemini']['free_tier_confirmed']=True;ws.save_config(config)
    monkeypatch.setenv('GEMINI_API_KEY','test-only');calls=[]
    def transport(model,body):
        calls.append(body)
        assert body['contents'][0]['parts'][1]['inlineData']['mimeType']=='image/jpeg'
        return {'candidates':[{'content':{'parts':[{'text':'{"ok":true}'}]}}]}
    provider=Gemini(ws,transport);path=tmp_path/'frame.png'
    Image.new('RGB',(100,200),'red').save(path)
    schema={'type':'object'}
    assert provider.generate('review',{},schema,images=[path])=={'ok':True}
    provider.generate('review',{},schema,images=[path]);assert len(calls)==1
    Image.new('RGB',(100,200),'blue').save(path)
    provider.generate('review',{},schema,images=[path]);assert len(calls)==2


@pytest.mark.parametrize('status',['fail','unknown'])
def test_required_wrong_or_unknown_asset_is_held_with_saved_evidence(ws,tmp_path,status):
    asset=source(ws,tmp_path);job={'request':{'visual_review':'required'}}
    visuals={'source_bindings':[{'unit_id':'opening','asset_id':asset['id'],'query':'sunny beach','text':'A beach.'}]}
    folder=tmp_path/'review'
    with pytest.raises(Held) as exc:review_assets(ws,job,visuals,Critic(status),folder)
    assert exc.value.code=='visual_assets_review'
    report=json.loads((folder/'assets-1/assets-review.json').read_text())
    assert report['status']!='pass' and report['sheets']


def test_duplicate_source_query_reuses_one_asset_judgement(ws,tmp_path):
    asset=source(ws,tmp_path);critic=Critic()
    rows=[{'unit_id':str(i),'asset_id':asset['id'],'query':'library','text':''} for i in range(10)]
    result=review_assets(ws,{'request':{'visual_review':'required'}},{'source_bindings':rows},critic,tmp_path/'review')
    assert result['status']=='pass' and len(critic.calls)==1 and len(critic.calls[0][1]['items'])==1


def test_required_review_does_not_mask_quota_failure(ws,tmp_path):
    asset=source(ws,tmp_path)
    class Quota(Critic):
        def generate(self,*args,**kwargs):raise Held('gemini_quota','Quota unavailable',retry_after=60)
    with pytest.raises(Held) as exc:
        review_assets(ws,{'request':{'visual_review':'required'}},{'source_bindings':[{'unit_id':'u','asset_id':asset['id'],'query':'library'}]},Quota(),tmp_path/'review')
    assert exc.value.code=='gemini_quota'
    saved=json.loads((tmp_path/'review/assets-1/assets-review.json').read_text())
    assert saved['status']=='unknown' and saved['error_code']=='gemini_quota'


def test_critic_cannot_omit_duplicate_or_invent_items():
    for rows in ([],[{'id':'made-up'}],[{'id':'u','status':'pass','reason':'fine','issues':['clipped']} ]):
        with pytest.raises(Held):validate_observations({'observations':rows},{'u'})


def test_graphic_cannot_invent_claim_or_execute_code():
    unit={'text':'Read the notes. Close the notes. Explain it.','onscreen':'Read then recall'}
    assert validate_block({'kind':'process','title':'Read then recall','labels':['Close the notes','Explain it']},unit)
    for block in ({'kind':'callout','title':'','labels':['Guaranteed top grades']},
                  {'kind':'python','title':'','labels':['import os']},
                  {'kind':'comparison','title':'','labels':['Read the notes']}):
        with pytest.raises(Held):validate_block(block,unit)


def test_comparison_can_reference_a_previous_exact_script_phrase():
    script={'units':[{'id':'a','text':'I helped.','onscreen':'I helped'},
                     {'id':'b','text':'I checked the receipt.','onscreen':'Checked the receipt'}]}
    block={'kind':'comparison','title':'Before and After','labels':['I helped','Checked the receipt']}
    assert validate_block(block,script['units'][1],script)
    with pytest.raises(Held):validate_block({**block,'labels':['Guaranteed job','Checked the receipt']},script['units'][1],script)


def test_inadequate_graphic_panel_is_a_clear_hold(tmp_path):
    from yt_pipeline.scene_blocks import block_frame
    with pytest.raises(Held) as exc:block_frame({'kind':'callout','title':'','labels':['Test']},tmp_path/'x.png',height=448)
    assert exc.value.code=='scene_block_layout'


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
def test_real_motion_scene_reveals_and_final_review_is_bound_to_export(ws,tmp_path):
    output=tmp_path/'comparison.mp4'
    block={'kind':'comparison','title':'Show the change','labels':['I helped','I solved the problem']}
    detail=render_block(block,2.4,output)
    info=probe(output);assert abs(float(info['format']['duration'])-2.4)<.15
    assert len(detail['plates'])==2
    a=Image.open(detail['plates'][0]);b=Image.open(detail['plates'][1]);assert a.tobytes()!=b.tobytes()
    written={'script':{'units':[{'id':'u','text':'Show the change','speaker':'Narrator'}]}}
    timing={'units':[{'id':'u','start':0,'duration':2.4}]}
    critic=Critic();job={'request':{'visual_review':'required'}}
    result=review_render(ws,job,written,timing,{'video':str(output),'duration':2.4},critic,tmp_path/'review')
    assert result['status']=='pass'
    report=json.loads(Path(result['file']).read_text())
    assert len(report['samples'])==2 and report['input_identity']==result['input_identity']
    assert all(row['sha256']==file_hash(row['file']) for row in report['samples'])
    assert 'No audio was submitted' in report['limits'][1]


def test_library_returns_candidates_and_rechecks_changed_media(ws,tmp_path):
    asset=source(ws,tmp_path)
    assert search_library(ws,'library')['results'][0]['id']==asset['id']
    assert search_library(ws,'library',kind='video')['results']==[]
    Path(asset_record(ws,asset['id'])['path']).write_bytes(b'changed')
    result=search_library(ws,'library')
    assert not result['results'] and result['ineligible_skipped']==1
