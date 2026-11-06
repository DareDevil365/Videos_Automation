"""Resolve real cutouts and enforce that a selected style has an actual renderer."""
import re

from PIL import Image, ImageEnhance, ImageOps

from .assets import asset_record
from .core import Held


def load_style_layers(workspace,request,script):
    """Photographic locations and exact-detail prop inserts for the simple portrait stage."""
    config=request.get('visual_selection') or {}
    layers=config.get('layers',{})
    ids={u['id'] for u in script['units']}
    if not isinstance(layers,dict) or set(layers)-ids:
        raise Held('lore_style_asset','Photo layer placements must reference actual beat IDs.')
    backdrops={};panels={};assets=[]
    from .source_sets import resolve_source_set
    for uid,row in layers.items():
        if not isinstance(row,dict) or set(row)-{'setting','props','setting_repeat_reason'}:
            raise Held('lore_style_asset','Supply setting and named prop layers.')
        if 'setting_repeat_reason' in row and (not isinstance(row['setting_repeat_reason'],str) or not row['setting_repeat_reason'].strip() or len(row['setting_repeat_reason'])>300):
            raise Held('lore_style_asset','Explain the deliberate return to this photographic setting.')
        if 'setting' in row:
            asset=asset_record(workspace,row['setting'],allow_preview=request.get('test_only') is True)
            if asset['kind']!='image':raise Held('lore_style_asset','A photo setting must be a registered image.')
            with Image.open(asset['path']) as raw:im=ImageOps.exif_transpose(raw).convert('RGB')
            if max(680/im.width,770/im.height)>1.25:
                raise Held('lore_style_quality','The photo setting needs more native pixels for this viewport.')
            im=ImageOps.fit(im,(680,770),Image.Resampling.LANCZOS)
            im=ImageEnhance.Color(im).enhance(.65)
            backdrops[uid]=ImageEnhance.Brightness(im).enhance(.64)
            assets.append(asset)
        props=row.get('props',{})
        if not isinstance(props,dict) or len(props)>4:raise Held('lore_style_asset','Place up to four named prop inserts.')
        panels[uid]=list(props.values())
    placements,_,prop_assets=resolve_source_set(workspace,{'source_panels':panels,'test_only':request.get('test_only',False),'lore_fresh_visuals':True},script)
    return backdrops,placements,assets+prop_assets


def load_character_cutouts(workspace,request):
    refs=request.get('character_cutouts',{})
    if not isinstance(refs,dict) or len(refs)>12:
        raise Held('lore_cutout','Map up to twelve character IDs to registered cutouts.')
    images={};assets=[]
    for who,ref in refs.items():
        if not isinstance(who,str) or not re.fullmatch('[a-z_]{1,40}',who) or not isinstance(ref,str):
            raise Held('lore_cutout','Use character IDs and registered asset IDs.')
        asset=asset_record(workspace,ref,allow_preview=request.get('test_only') is True)
        if asset['kind']!='image':raise Held('lore_cutout','Character cutouts must be images.')
        with Image.open(asset['path']) as raw:im=ImageOps.exif_transpose(raw).convert('RGBA')
        alpha=im.getchannel('A')
        if alpha.getextrema()!=(0,255):raise Held('lore_cutout','Use a character cutout with transparent edges.')
        im=im.crop(alpha.getbbox());rgb=ImageEnhance.Color(im.convert('RGB')).enhance(.90).convert('RGBA')
        rgb.putalpha(im.getchannel('A'));images[who]=rgb;assets.append(asset)
    return images,assets


def place_cutout(layer,images,who,box):
    if who not in images:raise Held('lore_style_asset',f'A clean {who} cutout is required by this shot.')
    source=images[who];size=(round(box[2]-box[0]),round(box[3]-box[1]))
    factor=min(size[0]/source.width,size[1]/source.height)
    if factor>1.25:raise Held('lore_style_quality',f'Find a higher-resolution {who} cutout for this framing.')
    cache=source.info.setdefault('style_sizes',{})
    if size not in cache:cache[size]=ImageOps.contain(source,size,Image.Resampling.LANCZOS)
    im=cache[size];layer.alpha_composite(im,(round(box[0]+(size[0]-im.width)/2),round(box[3]-im.height)))


def validate_execution(scene,request,images,thunder_cast,extra_kinds=()):
    style=scene.get('visual_style')
    if not style:return
    from .lore_forge import FORGE_KINDS
    from .lore_thunder import THUNDER_KINDS
    kind=scene['kind'];people=style['characters']
    layer=request.get('visual_selection',{}).get('layers',{}).get(scene.get('unit_id'),{})
    photo_props=[p['id'] for p in style['props'] if p['representation']=='cutout']
    if layer.get('setting') and style['setting']['representation']!='photographic':
        raise Held('lore_style_recipe','The supplied photo setting conflicts with the selected geometric setting.')
    if set(layer.get('props',{}))-set(photo_props):
        raise Held('lore_style_recipe','A supplied photo prop conflicts with the selected prop treatment.')
    if kind=='portrait' and any(p['representation']=='geometric' for p in style['props']):
        raise Held('lore_style_recipe','Choose a drawing recipe for a geometric prop; the portrait insert stage does not draw arbitrary objects.')
    photographic=style['setting']['representation']=='photographic' or bool(photo_props)
    if photographic:
        if kind!='portrait':raise Held('lore_style_recipe','Use the simple portrait/insert stage or author a compatible photo layer adapter for this action recipe.')
        if style['setting']['representation']=='photographic' and not layer.get('setting'):
            raise Held('lore_style_asset','Register and supply the photographic setting selected for this shot.')
        if set(photo_props)-set(layer.get('props',{})):
            raise Held('lore_style_asset','Register and place each selected photographic prop insert.')
    geometric_only={'vision_magic','vision_unlock','spider_theft','spider_trapped','spider_reach','spider_resolve','spider_lift','spider_hospital'}
    expected=None
    if kind in THUNDER_KINDS:
        expected=set() if kind=='stormbreaker_forged' else {'bill'} if kind in ('thor_hammer_hook','bill_lifts','bill_fleet') else {'thor','bill'}
    elif kind in extra_kinds:
        if kind.startswith('spider_'):expected={'doc_ock'} if kind=='spider_theft' else {'aunt_may'} if kind=='spider_hospital' else {'spider_man'}
        else:expected=set() if kind in ('vision_ship','vision_two_ships') else {'white_vision'} if kind in ('vision_memory','vision_answer') else {'vision','white_vision'}
    if expected is not None and set(people)!=expected:
        raise Held('lore_style_recipe','The directed cast must match the cast actually drawn by this recipe.')
    for who,choice in people.items():
        selected=choice['representation']
        if kind in geometric_only and selected!='geometric':
            raise Held('lore_style_recipe','This physical-action shot needs an anchored cutout rig or a different framing.')
        if kind in THUNDER_KINDS:
            if selected=='cutout' and not thunder_cast:
                raise Held('lore_style_asset','This Thor/Bill shot needs registered anchored cutout layers.')
        elif kind in FORGE_KINDS:
            if selected!='geometric':raise Held('lore_style_recipe','Use a cutout portrait or add a compatible action recipe.')
        elif kind=='portrait' or kind in extra_kinds:
            if selected=='cutout' and who not in images:
                raise Held('lore_style_asset',f'The selected {who} likeness needs a registered cutout.')
            if kind=='portrait' and selected=='geometric' and who not in ('doom','hellboy','spider_man'):
                raise Held('lore_style_recipe','This geometric portrait needs a character-specific drawing recipe.')
        else:
            raise Held('lore_style_recipe','This recipe cannot apply the selected representation; author a compatible shot before rendering.')
    if kind=='portrait' and len(people)>1:
        raise Held('lore_style_recipe','Use a supported two-shot instead of overlapping portrait actors.')
