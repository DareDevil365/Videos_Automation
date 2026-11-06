import pytest
from PIL import Image,ImageChops

from yt_pipeline.core import Held
from yt_pipeline.lore_design import PALETTES,compile_design
from yt_pipeline.lore_visuals import lore_frame
from yt_pipeline.source_sets import source_painter


def request(palette='paper',atmosphere='none'):
    return {'reaction_preset':'theater','lore_design':{'palette':palette,'atmosphere':atmosphere,
            'font':'Trebuchet MS','audience_required':True,'reason':'A readable story-specific environment.'}}


def test_audience_omission_and_invalid_art_direction_stop_before_render():
    units=[{'id':'u1'}];r=request()
    design=compile_design(r,units)
    assert design['shots']['u1']['reason'] and design['audience_required']
    r.pop('reaction_preset')
    with pytest.raises(Held,match='lower audience'):compile_design(r,units)
    for field,bad in [('palette','made-up'),('palette',{}),('atmosphere','explosion'),('font','Comic Sans'),('reason','')]:
        r=request();r['lore_design'][field]=bad
        with pytest.raises(Held):compile_design(r,units)
    r=request();r['lore_design']['shots']={'missing':{'palette':'ember'}}
    with pytest.raises(Held,match='actual beats'):compile_design(r,units)


def test_palette_heading_contrast_is_readable_on_each_canvas():
    def luminance(color):
        channels=[int(color[i:i+2],16)/255 for i in (1,3,5)]
        channels=[n/12.92 if n<=.04045 else ((n+.055)/1.055)**2.4 for n in channels]
        return sum(a*b for a,b in zip(channels,(.2126,.7152,.0722)))
    for palette in PALETTES.values():
        a,b=sorted((luminance(palette['ink']),luminance(palette['canvas'])))
        assert (b+.05)/(a+.05)>=4.5


@pytest.mark.parametrize(('palette','effect'),[('ember','embers'),('hex','hex'),('concrete','rain')])
def test_contextual_atmosphere_moves_within_story_not_caption_or_audience(palette,effect):
    design=compile_design(request(palette,effect),[{'id':'u1'}])['shots']['u1']
    scene={'unit_id':'u1','kind':'vision_aftermath','label':'The environment supports the story','design':design,'framing':'wide'}
    first=lore_frame(scene,.6,4);later=lore_frame(scene,2.6,4)
    assert first.getpixel((2,100))!= (8,14,23)
    assert ImageChops.difference(first,later).getbbox()
    assert ImageChops.difference(first.crop((0,960,720,1280)),later.crop((0,960,720,1280))).getbbox() is None


def test_photo_and_story_are_transformed_together_above_audience():
    def base(*args):return Image.new('RGB',(720,1280),'#998866')
    prop=Image.new('RGBA',(60,60),'#ff00ff')
    cast=Image.new('RGBA',(40,80),(0,0,0,0))
    setup=('cinema',[cast],[],None,None)
    paint=source_painter(base,[(prop,(290,845,350,905),None)],setup,0)
    frame=paint({'design':{'reason':'Keep caption contrast.'}},1,4)
    # 875 in the original art maps to about 819 after reserving the lower set.
    assert frame.getpixel((320,819))==(255,0,255)
    assert frame.getpixel((320,875))!=(255,0,255)
    assert frame.getpixel((320,930))==(33,27,32)
    assert frame.getpixel((320,1100))!=(153,136,102)
