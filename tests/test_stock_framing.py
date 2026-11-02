import pytest
from PIL import Image,ImageDraw

from yt_pipeline.core import Held,file_hash
from yt_pipeline.planned_visuals import stock_closeup,_stock_frame


def test_model_selected_closeup_is_applied_to_actual_source_pixels(tmp_path):
    source=tmp_path/'source.png';picture=Image.new('RGB',(400,400),'red')
    ImageDraw.Draw(picture).rectangle((100,100,300,300),fill='green');picture.save(source)
    before=file_hash(source)
    class Provider:
        def generate(self,purpose,content,schema,*,images):
            assert purpose=='stock-closeup-v1' and images==[source]
            return {'box':[.25,.25,.75,.75],'subject':'Technical green center fixture'}
    crop=stock_closeup(None,{'path':str(source)},{'framing':'closeup','visual_query':'green center'},
        {'text':'A technical fixture.'},Provider())
    output=tmp_path/'frame.png'
    _stock_frame({'path':str(source)},'Fixture caption',output,crop=crop)
    with Image.open(output) as frame:
        r,g,b=frame.getpixel((360,200));assert g>r and frame.size==(720,1280)
    assert file_hash(source)==before


@pytest.mark.parametrize('box',[[-.1,0,1,1],[0,.5,1,.5],[True,0,1,1],[0,0,float('nan'),1]])
def test_invalid_crop_never_reaches_the_renderer(box):
    class Provider:
        def generate(self,*args,**kwargs):return {'box':box,'subject':'Invalid technical crop'}
    with pytest.raises(Held) as error:
        stock_closeup(None,{'path':'unused.png'},{'framing':'closeup','visual_query':'fixture'},
            {'text':'Fixture.'},Provider())
    assert error.value.code=='stock_framing'


def test_wide_shots_make_no_crop_call_and_closeup_provider_holds_propagate():
    class Provider:
        def generate(self,*args,**kwargs):raise Held('gemini_quota','Wait',retry_after=300)
    asset={'path':'unused.png'};unit={'text':'Fixture.'}
    assert stock_closeup(None,asset,{'framing':'wide'},unit,Provider()) is None
    with pytest.raises(Held) as error:
        stock_closeup(None,asset,{'framing':'closeup','visual_query':'fixture'},unit,Provider())
    assert error.value.code=='gemini_quota' and error.value.retry_after==300
