"""Compile source-aware portrait news/movie graphics without model editing."""
from copy import deepcopy
from pathlib import Path
import math
import re

from PIL import Image,ImageDraw
from shorts_editor.graphics import font, text_box
from shorts_editor.store import write_json
from .assets import register_asset
from .core import Held,digest
from .scene_blocks import validate_block
from .transcripts import write_srt
from .source_delivery import delivery_for
from .source_sets import resolve_source_set, source_painter


MODES={'movie_brief':('masks','role','film','powers','ensemble','ticket','film','books'),
       'current_affairs':('routes','date','route','coverage','filter','origin','costs','routes')}


def plan_brief(script,request,brief):
    if not brief or brief['kind']!='fact':raise Held('missing_evidence','News/movie briefs require sources about the actual subject.')
    if len({u['speaker'] for u in script['units']})!=1:raise Held('brief_voice','Short source briefs use one consistent narrator.')
    choices=request.get('brief_graphics',{})
    if not isinstance(choices,dict) or set(choices)-{u['id'] for u in script['units']}:raise Held('brief_graphic','Graphics must reference actual spoken units.')
    preset=request.get('playbook')
    if preset not in MODES:raise Held('brief_graphic','Choose the movie or current-affairs brief format.')
    motifs=request.get('brief_motifs',{})
    if not isinstance(motifs,dict) or set(motifs)-{u['id'] for u in script['units']} or any(v not in ('headline','media',*MODES[preset]) for v in motifs.values()):
        raise Held('brief_graphic','Use a supported motif for an actual script unit.')
    scenes=[]
    for i,unit in enumerate(script['units']):
        block=deepcopy(choices.get(unit['id'],{'kind':'callout','title':'','labels':[unit['onscreen']]}))
        validate_block(block,unit,script)
        if block['kind'] not in ('callout','comparison','process'):raise Held('brief_graphic','Choose a concise callout, comparison or process graphic.')
        scenes.append({'unit_id':unit['id'],'text':unit['text'],'speaker_id':'n',**delivery_for(unit,request,.18),
            'visible_cast':[],'focus_id':'','framing':'wide','motion':'hold','graphic':block,'rank':0,
            'claim_ids':unit['claim_ids'],'background_query':'','visual_query':'','asset_id':'',
            'headline':unit['onscreen'],'visual_mode':motifs.get(unit['id'],'headline'),'preset':preset,
            'stage':'hook' if i==0 else 'payoff' if unit['id']==script['edit']['payoff_unit_id'] else 'setup'})
    plan={'version':1,'template':'source_brief','cast':[{'id':'n','speaker':script['units'][0]['speaker'],
        'voice_id':'am_adam','avatar_kind':'narrator'}],'scenes':scenes,'comment_question':'',
        'sources':brief['sources'],'claims':brief['claims'],'evidence_scope':'Script claim/source links retained; source review is a separate recorded step.'}
    return {'plan':plan,'origin':'compiled_factual_brief_v1','script_sha256':digest(script),'repairs':0}


def brief_frame(scene,second,duration):
    """Draw the labels and pictograms beneath any separately registered media."""
    movie=scene['preset']=='movie_brief';bg='#111825' if movie else '#102521'
    accent='#f5c86e' if movie else '#9ce0b4';ink='#f8f2dd';muted='#95aab6' if movie else '#84b9aa'
    im=Image.new('RGB',(720,1280),bg);d=ImageDraw.Draw(im)
    mode=scene['visual_mode'];p=1-(1-max(0,min(1,second/.8)))**3;phase=second*.85
    d.line((48,200,672,200),fill=accent,width=3)
    headline = scene['headline']
    if headline.casefold() in {phrase.casefold() for phrase in scene.get('linked_phrases', ())}:
        size = next((point for point in range(50, 25, -1) if d.textlength(headline, font=font(point, True)) <= 624), None)
        if size is None:
            raise Held('brief_graphic', 'The connected title is too long for a single line.')
        d.text((48, 47), headline, fill=ink, font=font(size, True))
    else:
        text_box(d,headline,(48,47,624,133),ink,50,True,minimum=34)
    def label(text,box,size=31,color=ink):text_box(d,text,box,color,size,True,'center',minimum=23)
    def mask(x,y,scale,fill):
        pts=[(-97,-78),(0,-107),(97,-78),(83,42),(30,107),(-30,107),(-83,42)]
        d.polygon([(x+a*scale,y+b*scale) for a,b in pts],fill=fill,outline=accent,width=4)
        d.line((x-53*scale,y-13*scale,x-15*scale,y-4*scale),fill=bg,width=9)
        d.line((x+15*scale,y-4*scale,x+53*scale,y-13*scale),fill=bg,width=9)
    def film(x,y,w,h):
        d.rounded_rectangle((x,y,x+w,y+h),radius=23,fill='#253143',outline=accent,width=4)
        for i in range(7):
            a=x+16+i*(w-61)/6
            d.rounded_rectangle((a,y+13,a+27,y+34),radius=5,fill=bg);d.rounded_rectangle((a,y+h-34,a+27,y+h-13),radius=5,fill=bg)
        d.polygon([(x+w*.42,y+h*.36),(x+w*.42,y+h*.64),(x+w*.64,y+h*.50)],fill=accent)
    def arrow(x1,y,x2,color=accent):
        sign=1 if x2>x1 else -1;d.line((x1,y,x2-sign*20,y),fill=color,width=8)
        d.polygon([(x2,y),(x2-sign*34,y-18),(x2-sign*34,y+18)],fill=color)
    def crate(x,y,scale=1):
        w=106*scale;h=78*scale
        d.rounded_rectangle((x-w/2,y-h/2,x+w/2,y+h/2),radius=12,fill='#28463e',outline=accent,width=4)
        d.line((x-w/2+9,y-h/2+10,x+w/2-9,y+h/2-10),fill=muted,width=4)
        d.line((x+w/2-9,y-h/2+10,x-w/2+9,y+h/2-10),fill=muted,width=4)
    if mode=='headline':
        x=148;y=363+round(30*(1-p))
        d.rounded_rectangle((x,y,572,y+465),radius=27,fill='#26374a' if movie else '#28463e',outline=accent,width=4)
        d.line((184,y+79,536,y+79),fill=accent,width=8)
        for i in range(4):d.line((184,y+151+i*65,536-i*31,y+151+i*65),fill=muted,width=5)
    elif mode in ('masks','role'):
        x=360 if mode=='role' else 207;y=531-32*p
        d.ellipse((x-151,y-151,x+151,y+151),outline=muted,width=3)
        mask(x,y,1.28 if mode=='role' else 1,'#bd9f66')
        if mode=='masks':
            d.ellipse((399,y-117,633,y+117),outline=muted,width=3);label('?',(419,y-74,195,150),94,accent)
        else:
            for i in range(3):
                r=180+i*23;d.arc((x-r,y-r,x+r,y+r),phase*50+i*25,phase*50+118+i*25,fill=muted,width=3)
    elif mode in ('film','ticket'):
        y=403+round(34*(1-p));film(104,y,512,270)
        if mode=='ticket':
            d.rounded_rectangle((241,719,479,825),radius=22,fill=accent)
            d.line((331,777,351,796,393,750),fill=bg,width=10,joint='curve')
    elif mode=='powers':
        x=198;y=513;d.ellipse((74,389,322,637),outline=accent,width=5)
        for i in range(6):
            a=i*math.pi/3+phase*.22;d.line((x,y,x+math.cos(a)*98,y+math.sin(a)*98),fill=muted,width=4)
        d.rounded_rectangle((416,411,638,627),radius=24,fill='#253143',outline=accent,width=4)
        for a,b,c,e in ((440,454,596,454),(596,454,596,533),(442,518,560,518),(560,518,560,586)):
            d.line((a,b,c,e),fill=muted,width=6);d.ellipse((c-7,e-7,c+7,e+7),fill=accent)
        label('+',(326,468,66,92),60,accent)
    elif mode=='ensemble':
        film(94,411,532,276)
        for i in range(4):
            x=169+127*i;y=760-18*p
            d.ellipse((x-22,y-29,x+22,y+15),fill=accent);d.arc((x-42,y-6,x+42,y+71),180,360,fill=muted,width=7)
    elif mode=='books':
        d.polygon([(90,438),(301,414),(343,463),(343,678),(298,649),(90,675)],fill='#29374a',outline=accent,width=4)
        d.polygon([(343,463),(384,414),(590,438),(590,675),(385,649),(343,678)],fill='#29374a',outline=accent,width=4)
        for y in (488,539,590):d.line((129,y,287,y-16),fill=muted,width=5);d.line((399,y-16,551,y),fill=muted,width=5)
        label('≠',(287,704,146,92),70,accent)
    elif mode in ('routes','route','coverage'):
        context=scene['headline'].casefold();route='new zealand → india' in context
        for x in (150,570):d.ellipse((x-62,484,x+62,608),fill='#234339',outline=accent,width=4)
        crate(150,546,.67);crate(570,546,.67)
        arrow(225,519,493)
        if mode=='routes':arrow(493,576,225,muted)
        x=240+round(228*p);d.ellipse((x-10,509,x+10,529),fill=ink)
        if 'new zealand' in context and 'india' in context:
            label('NEW ZEALAND' if route else 'INDIA',(54,630,193,56),30)
            label('INDIA' if route else 'NEW ZEALAND',(472,630,194,56),30)
        if mode=='coverage':
            # The spoken/approved headline carries the denominator. No chart scale.
            measure=re.search(r'\b\d{1,3}(?:\.\d+)?%',context)
            amount=('≈' if 'almost' in context or 'about' in context else '')+measure[0] if measure else '%'
            d.rounded_rectangle((233,721,487,832),radius=20,outline=muted,width=4);label(amount,(253,728,214,90),60,accent)
    elif mode=='date':
        d.rounded_rectangle((148,379,572,775),radius=32,fill='#29443d',outline=accent,width=5)
        d.line((149,479,571,479),fill=accent,width=6)
        for x in (220,500):d.line((x,349,x,416),fill=accent,width=14)
        for j in range(3):
            for i in range(4):
                x=208+i*91;y=535+j*73;d.ellipse((x-12,y-12,x+12,y+12),fill=muted if i+j else accent)
    elif mode=='filter':
        crate(207,538,1.7);d.line((345,382,345,699),fill=muted,width=4)
        crate(518,538,1.7);d.ellipse((427,447,609,629),outline='#ef9a82',width=7)
        d.line((455,600,581,475),fill='#ef9a82',width=8)
    elif mode=='origin':
        crate(360,402,1.4);d.polygon([(143,483),(577,483),(438,641),(438,772),(282,772),(282,641)],outline=accent,fill='#28463e',width=5)
        d.line((177,510,542,510),fill=muted,width=5)
        d.line((312,695,345,731,414,657),fill=accent,width=12,joint='curve')
    elif mode=='costs':
        crate(213,511,1.55);d.rounded_rectangle((393,400,632,719),radius=20,fill='#2d463e',outline=accent,width=4)
        for i in range(4):d.line((425,455+i*50,601,455+i*50),fill=muted,width=5)
        label('≠',(304,494,78,94),64,accent)
    if scene['graphic']['kind'] in ('process','comparison'):
        labels=scene['graphic']['labels'];w=620/len(labels)
        for i,text in enumerate(labels):
            if p>=i/max(1,len(labels)):
                x=50+round(i*w);d.line((x+10,844,x+round(w)-10,844),fill=muted,width=2)
                label(text,(x+8,855,round(w)-16,62),28)
    return im


def build_brief_visuals(ws,job,script,timing,folder,record):
    from .lore_visuals import render_lore_shot
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);plan=record['plan']
    if record['script_sha256']!=digest(script) or [s['unit_id'] for s in plan['scenes']]!=[u['id'] for u in timing['units']]:
        raise Held('brief_timing','Source graphics must preserve the exact frozen script and timing.')
    claims={c['id']:c['source_id'] for c in plan['claims']};sources={s['id']:s['url'] for s in plan['sources']};units={u['id']:u for u in script['units']}
    placements,reaction,provenance = resolve_source_set(ws,job['request'],script)
    rows=[];bindings=[]
    for scene,spoken in zip(plan['scenes'],timing['units']):
        unit=units[spoken['id']];validate_block(scene['graphic'],unit,script)
        if (scene['text'],scene['headline'],scene['claim_ids'])!=(unit['text'],unit['onscreen'],unit['claim_ids']):raise Held('brief_graphic','Compiled graphic changed its spoken evidence.')
        urls=list(dict.fromkeys(sources[claims[c]] for c in unit['claim_ids']))
        output=folder/(unit['id']+'-brief.mp4')
        painter = source_painter(brief_frame, placements.get(unit['id'],()), reaction, spoken['start']) if placements or reaction else brief_frame
        render_lore_shot(scene,spoken['duration'],output,paint=painter)
        made=register_asset(ws,output,'original_graphic',{'generator':'source-brief-symbols-v1','unit_id':unit['id'],'source_urls':urls,'note':'Illustration, not a photo, screen capture or additional evidence.'},test_only=job['request'].get('test_only',False))
        rows.append({'unit_id':unit['id'],'file':str(output),'media_id':made['id'],'duration':spoken['duration'],'kind':'source_brief','resolved_scene':scene})
        bindings.append({'unit_id':unit['id'],'claim_ids':unit['claim_ids'],'source_urls':urls})
    captions=folder/'captions.srt';write_srt([{'start':u['start'],'end':u['speech_end'],'text':u['text']} for u in timing['units']],captions)
    result={'version':1,'format':'lesson','frames':rows,'captions':str(captions),'planned_template':'source_brief',
        'planned_provenance':provenance,'selected_media':[],'source_bindings':bindings,'creative_plan_sha256':digest(plan)}
    write_json(folder/'visuals.json',result);return result
