"""Explicit episode/shot art direction; legacy plans keep their existing look."""
import math
from copy import deepcopy

from PIL import Image, ImageDraw

from .core import Held


PALETTES = {
    'paper': dict(canvas='#eee3ce', field='#d5bf9d', ink='#30251f', edge='#806547', accent='#a34932', wall='#c1a984', recess='#ad916c'),
    'ember': dict(canvas='#27110f', field='#54231b', ink='#ffe8c4', edge='#ba784a', accent='#ff9238', wall='#70392b', recess='#3e211c'),
    'plum': dict(canvas='#211329', field='#452544', ink='#f8e1cf', edge='#ac7a98', accent='#e595bd', wall='#59344d', recess='#35213c'),
    'concrete': dict(canvas='#26231f', field='#4e4b45', ink='#fff0d4', edge='#a89d88', accent='#d1b46f', wall='#625d52', recess='#3b3935'),
    'daylight': dict(canvas='#f4eadb', field='#dfc9ac', ink='#352822', edge='#a37850', accent='#c75a3a', wall='#d3b48e', recess='#baa080'),
    'crimson': dict(canvas='#230f18', field='#572432', ink='#ffe8db', edge='#c67a78', accent='#ffb56a', wall='#72323d', recess='#411f2a'),
    'hex': dict(canvas='#241126', field='#41223e', ink='#fff0e3', edge='#ba8bba', accent='#fb91a7', wall='#51254f', recess='#351f3f'),
}
ATMOSPHERES = ('none', 'embers', 'dust', 'hex', 'rain')
FONTS = ('Arial', 'Trebuchet MS', 'Georgia')


def compile_design(request, units):
    value=request.get('lore_design')
    if value is None:return None
    if not isinstance(value,dict) or set(value)-{'palette','atmosphere','font','reason','audience_required','shots'}:
        raise Held('lore_design','Use a named palette, atmosphere, font, rationale and per-shot overrides.')
    ids={u['id'] for u in units};shots=value.get('shots',{})
    if not isinstance(shots,dict) or set(shots)-ids:raise Held('lore_design','Art direction must reference actual beats.')
    if type(value.get('audience_required',True)) is not bool:raise Held('lore_design','audience_required must be a boolean.')
    if value.get('audience_required',True) and not (request.get('reaction_preset') or request.get('reaction_set')):
        raise Held('lore_audience','This episode requires its lower audience set before rendering.')
    if not isinstance(value.get('reason'),str) or not value['reason'].strip():
        raise Held('lore_design','Record why the episode uses this visual direction.')
    result={'version':1,'reason':value['reason'],'audience_required':value.get('audience_required',True),'shots':{}}
    for uid in ids:
        row=shots.get(uid,{})
        if not isinstance(row,dict) or set(row)-{'palette','atmosphere','reason','elements'}:
            raise Held('lore_design','Shot direction uses palette, atmosphere, rationale and element purposes.')
        palette=row.get('palette',value.get('palette','paper'))
        atmosphere=row.get('atmosphere',value.get('atmosphere','none'))
        font=value.get('font','Arial')
        if not all(isinstance(v,str) for v in (palette,atmosphere,font)) or palette not in PALETTES or atmosphere not in ATMOSPHERES or font not in FONTS:
            raise Held('lore_design','Choose a supported palette, atmosphere and readable font.')
        reason=row.get('reason',value['reason']);elements=row.get('elements',[])
        if not isinstance(reason,str) or not reason.strip() or not isinstance(elements,list) or any(not isinstance(e,str) or not e.strip() for e in elements):
            raise Held('lore_design','Explain the shot purpose and each selected element in plain language.')
        result['shots'][uid]={'palette':palette,'colors':deepcopy(PALETTES[palette]),'atmosphere':atmosphere,'font':font,'reason':reason,'elements':elements}
    return result


def paint_atmosphere(image, scene, second):
    """Motion stays behind the cast and inside the story viewport."""
    spec=scene.get('design')
    if not spec:return
    mode=spec['atmosphere'];colors=spec['colors']
    overlay=Image.new('RGBA',image.size);d=ImageDraw.Draw(overlay)
    if mode=='hex':
        for i,color in enumerate(('#ed6b93','#9e6dc4','#eea15b','#69b6a7')):
            cx=360+210*math.sin(second*.35+i*1.7);cy=555+220*math.cos(second*.29+i*1.5)
            for radius in range(240,25,-24):
                a=round(22+(240-radius)/5)
                rgb=tuple(bytes.fromhex(color[1:]));d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=(*rgb,a))
        for i in range(8):
            x=72+(i*83)%570;y=250+(i*97+second*18)%620;r=35+8*math.sin(second+i)
            pts=[(x+r*math.cos(n*math.pi/3),y+r*math.sin(n*math.pi/3)) for n in range(7)]
            d.line(pts,fill=(246,143,185,64),width=2)
    elif mode in ('embers','dust'):
        for i in range(44 if mode=='embers' else 25):
            x=52+(i*137)%610+8*math.sin(second*.7+i);y=920-((i*71+second*(48 if mode=='embers' else 13))%685)
            r=1+i%3;rgb=(255,154,64) if mode=='embers' else tuple(bytes.fromhex(colors['accent'][1:]))
            d.ellipse((x-r,y-r,x+r,y+r),fill=(*rgb,110+i%100))
            if mode=='embers':d.line((x,y+8,x-2,y+17),fill=(*rgb,64),width=2)
    elif mode=='rain':
        for i in range(38):
            x=45+(i*103)%620;y=205+(i*71+second*230)%710
            d.line((x,y,x-7,y+25),fill=(224,217,207,75),width=2)
    image.alpha_composite(overlay.crop((20,180,700,950)),dest=(20,180))
