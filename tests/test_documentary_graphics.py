from copy import deepcopy
import pytest
from PIL import ImageChops
from yt_pipeline.core import Held
from yt_pipeline.documentary_graphics import validate_scenes,diagram_frame


def fixture():
    script={'units':[{'id':'u1','kind':'fact','text':'The first group has 3, the second has 7.',
        'onscreen':'first group / second group','claim_ids':['c1']}]}
    brief={'sources':[{'id':'s1','excerpt':'In the trial, first group: 3; second group: 7.','url':'https://example.com'}],
        'claims':[{'id':'c1','source_id':'s1','text':'The groups have 3 and 7.'}]}
    row={'unit_id':'u1','kind':'bars','labels':['first group','second group'],'claim_ids':['c1'],'source_id':'s1',
        'quote':brief['sources'][0]['excerpt'],'values':[3,7],'measure':'count','pause_after':.2}
    return {'scenes':[row],'evidence_review':{'supported':True,'issues':[]}},script,brief


def test_source_grounded_bars_reject_invented_values_labels_quotes_and_claims():
    raw,script,brief=fixture();assert validate_scenes(raw,script,brief)==raw['scenes']
    for key,value in [('values',[3,99]),('labels',['invented','second group']),('quote','Made up quotation 3 7'),('claim_ids',['missing'])]:
        bad=deepcopy(raw);bad['scenes'][0][key]=value
        with pytest.raises(Held):validate_scenes(bad,script,brief)
    raw['evidence_review']['supported']=False
    with pytest.raises(Held,match='factual'):validate_scenes(raw,script,brief)


def test_diagrams_actually_reveal_and_hold_final_values():
    raw,_,_=fixture();scene={**raw['scenes'][0],'title':'Compare the groups'}
    start=diagram_frame(scene,0,5);settled=diagram_frame(scene,3,5)
    assert start.size==settled.size==(1280,720)
    assert ImageChops.difference(start,settled).getbbox()
    for kind in ('comparison','process','timeline','relationship','source'):
        frame=diagram_frame({**scene,'kind':kind},2,5)
        assert frame.size==(1280,720)
