import json
from pathlib import Path

import pytest

from shorts_editor.store import write_json
from yt_pipeline.core import Held,Workspace
from yt_pipeline.source_series import create_series_plan
from yt_pipeline.brief_visuals import MODES,brief_frame,plan_brief
from yt_pipeline.contracts import brief_contract,script_contract
from yt_pipeline.playbooks import validate_playbook_script


ROOT=Path(__file__).resolve().parents[1]
SERIES=ROOT/'examples/lore-series/secret-wars-2015'
BRIEF=ROOT/'research/content-lore/SECRET_WARS_2015_BRIEF.json'


def test_series_plan_binds_actual_three_parts_review_and_music(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');target=tmp_path/'Plans'/'series.json'
    monkeypatch.setattr('yt_pipeline.curated_music.select_genre_music',lambda *a,**k:{'id':'soundtrack'})
    result=create_series_plan(ws,SERIES/'series.json',BRIEF,target,SERIES/'source-review.json')
    plan=json.loads(target.read_text(encoding='utf-8'));assert result['parts']==3
    assert [x['request']['series']['next_part'] for x in plan['items']]==[2,3,None]
    assert all(x['request']['test_only'] and not x['request']['auto_publish'] and x['request']['brief']['editorial_verified'] for x in plan['items'])
    assert {x['request']['music_id'] for x in plan['items']}=={'soundtrack'}
    assert len({x['request']['script']['hook'] for x in plan['items']})==3
    with pytest.raises(Held):create_series_plan(ws,SERIES/'series.json',BRIEF,target,SERIES/'source-review.json')


def test_series_rejects_rewritten_dialogue_under_an_older_source_review(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');source=tmp_path/'series';source.mkdir()
    for path in SERIES.glob('*.json'):(source/path.name).write_bytes(path.read_bytes())
    script=source/'part-1.json';s=json.loads(script.read_text(encoding='utf-8'));s['units'][2]['text']+=' A new sentence.';write_json(script,s)
    monkeypatch.setattr('yt_pipeline.curated_music.select_genre_music',lambda *a,**k:{'id':'soundtrack'})
    with pytest.raises(Held,match='each exact supplied script'):
        create_series_plan(ws,source/'series.json',BRIEF,tmp_path/'Plans'/'bad.json',source/'source-review.json')


@pytest.mark.parametrize(('folder','stem','preset'),[('movie-content','doomsday-actor-character','movie_brief'),('current-affairs','india-nz-fta','current_affairs')])
def test_sourced_short_keeps_script_and_rejects_invented_graphics(folder,stem,preset):
    root=ROOT/'examples'/folder
    b=brief_contract(json.loads((root/(stem+'.brief.json')).read_text(encoding='utf-8')))
    s=script_contract(json.loads((root/(stem+'.script.json')).read_text(encoding='utf-8')),b,'lesson')
    validate_playbook_script(s,preset,{})
    plan=plan_brief(s,{'playbook':preset},b)['plan']
    assert plan['sources']==b['sources'] and [x['text'] for x in plan['scenes']]==[x['text'] for x in s['units']]
    with pytest.raises(Held):plan_brief(s,{'playbook':preset,'brief_graphics':{'u1':{'kind':'callout','title':'','labels':['Unsupported 9000%']}}},b)
    with pytest.raises(Held):plan_brief(s,{'playbook':preset,'brief_motifs':{'u1':'fabricated_chart'}},b)
    plan=plan_brief(s,{'playbook':preset,'brief_motifs':{f'u{i+1}':mode for i,mode in enumerate(MODES[preset])}},b)['plan']
    images=[brief_frame(scene,.8,3) for scene in plan['scenes']]
    assert all(im.size==(720,1280) for im in images)
    assert len({im.crop((40,250,680,950)).tobytes() for im in images})>=6
