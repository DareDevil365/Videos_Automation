import io
import json

import pytest
from PIL import Image

from yt_pipeline import media_agent
from yt_pipeline.assets import register_asset,asset_record
from yt_pipeline.core import Held,Workspace


def test_refined_acquisition_is_bounded_and_reuses_the_checked_asset(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');picture=tmp_path/'portrait.png'
    Image.new('RGB',(300,300),'blue').save(picture)
    asset=register_asset(ws,picture,'test',{'description':'Technical matching fixture'})
    searches=[];calls=[]
    def acquire(workspace,query,kind,**kwargs):
        searches.append(query)
        if query!='man face':raise Held('media_not_found','No match')
        assert kwargs['match_query']=='young man smiling cutout'
        assert kwargs['context']=={'narration':'An anonymous person.'}
        return asset
    class Provider:
        def generate(self,purpose,content,schema):
            calls.append(purpose)
            assert content['original_query']=='young man smiling cutout'
            return {'queries':['young man portrait','man face']}
    monkeypatch.setattr(media_agent,'commons_acquire',acquire)
    context={'narration':'An anonymous person.'}
    result=media_agent.acquire_visual(ws,'young man smiling cutout',provider=Provider(),context=context)
    again=media_agent.acquire_visual(ws,'young man smiling cutout',provider=Provider(),context=context)
    assert result['id']==again['id']==asset['id']
    assert searches==['young man smiling cutout','young man portrait','man face']
    assert calls==['media-query-refinement-v1']


@pytest.mark.parametrize('code',['source_rate_limited','source_unavailable','media_host'])
def test_refinement_does_not_swallow_provider_or_permission_holds(tmp_path,monkeypatch,code):
    ws=Workspace(tmp_path/'ws')
    def acquire(*args,**kwargs):raise Held(code,'Original hold',retry_after=60)
    class Provider:
        def generate(self,*args):pytest.fail('Must not refine a provider/permission failure')
    monkeypatch.setattr(media_agent,'commons_acquire',acquire)
    with pytest.raises(Held) as error:media_agent.acquire_visual(ws,'portrait',provider=Provider())
    assert error.value.code==code and error.value.retry_after==60


@pytest.mark.parametrize('queries',[['portrait','portrait'],['portrait'],['portrait','']])
def test_invalid_refinements_do_not_start_more_searches(tmp_path,monkeypatch,queries):
    ws=Workspace(tmp_path/'ws');searches=[]
    def acquire(workspace,query,kind,**kwargs):
        searches.append(query);raise Held('media_not_found','No match')
    class Provider:
        def generate(self,*args):return {'queries':queries}
    monkeypatch.setattr(media_agent,'commons_acquire',acquire)
    with pytest.raises(Held) as error:media_agent.acquire_visual(ws,'cast portrait',provider=Provider())
    assert error.value.code=='media_query_invalid' and searches==['cast portrait']


def test_missing_refinements_stop_after_two_and_quota_is_not_hidden(tmp_path,monkeypatch):
    ws=Workspace(tmp_path/'ws');searches=[]
    def acquire(workspace,query,kind,**kwargs):
        searches.append(query);raise Held('media_not_found','No match')
    class Provider:
        def generate(self,*args):return {'queries':['museum hallway','museum interior']}
    monkeypatch.setattr(media_agent,'commons_acquire',acquire)
    with pytest.raises(Held) as error:media_agent.acquire_visual(ws,'empty dark museum hallway',provider=Provider())
    assert error.value.code=='media_not_found' and len(searches)==3
    class Quota:
        def generate(self,*args):raise Held('gemini_quota','Wait',retry_after=300)
    with pytest.raises(Held) as error:media_agent.acquire_visual(ws,'another hallway',provider=Quota())
    assert error.value.code=='gemini_quota' and error.value.retry_after==300


def test_actual_candidate_pixels_reject_first_hit_and_accept_jpeg_tiff_thumbnail(tmp_path):
    ws=Workspace(tmp_path/'ws');downloads=[];reviews=[]
    def page(i,color):
        return {'title':f'File:Portrait man {i}.tif','imageinfo':[{'mime':'image/tiff','thumbmime':'image/jpeg',
            'width':1000,'height':1200,'thumburl':f'https://upload.wikimedia.org/{color}.jpg',
            'descriptionurl':f'https://commons.wikimedia.org/wiki/File:Portrait_{i}.tif',
            'extmetadata':{'Artist':{'value':'Fixture photographer'},'LicenseShortName':{'value':'Public domain'}}}]}
    metadata={'query':{'pages':{'1':page(1,'red'),'2':page(2,'green'),'3':page(3,'blue')}}}
    def fetcher(url,**kwargs):
        if '/w/api.php?' in url:return json.dumps(metadata).encode(),'application/json',url
        downloads.append(url);picture=io.BytesIO()
        Image.new('RGB',(300,400),url.rsplit('/',1)[-1].split('.')[0]).save(picture,format='JPEG')
        return picture.getvalue(),'image/jpeg',url
    class Provider:
        def generate(self,purpose,content,schema,*,images):
            assert purpose=='stock-candidate-pixels-v1'
            with Image.open(images[0]) as picture:r,g,b=picture.getpixel((0,0))
            reviews.append(content['source_title'])
            return {'status':'pass' if g>r else 'fail','reason':'Technical actual-pixel fixture verdict'}
    asset=media_agent.commons_acquire(ws,'portrait man',fetcher=fetcher,provider=Provider())
    again=media_agent.commons_acquire(ws,'portrait man',fetcher=fetcher,provider=Provider())
    assert asset['id']==again['id'] and len(downloads)==len(reviews)==2
    assert asset['path'].endswith('.jpg') and asset['evidence']['mime']=='image/jpeg'
    assert asset['evidence']['original_mime']=='image/tiff'
    assert 'Fixture photographer' in asset['attribution']


def test_candidate_checks_retain_original_scene_context(tmp_path):
    ws=Workspace(tmp_path/'ws');picture=tmp_path/'source.png'
    Image.new('RGB',(300,400),'green').save(picture)
    asset=register_asset(ws,picture,'test',{'description':'Technical context fixture'})
    asset=asset_record(ws,asset['id'])
    seen=[]
    class Provider:
        def generate(self,purpose,content,schema,*,images):
            seen.append(content)
            assert content['query']=='security camera monitor room'
            assert content['scene_context']['narration']=='He reviews the indoor camera.'
            return {'status':'fail','reason':'The depicted conference room does not show security monitors.'}
    assert not media_agent._candidate_matches(ws,Provider(),'security camera monitor room',asset,
        {'narration':'He reviews the indoor camera.'})
    assert len(seen)==1
