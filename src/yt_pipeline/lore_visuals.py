"""Original code-drawn comic-lore diagrams; no publisher panels or generated assets."""
from copy import deepcopy
from functools import lru_cache
import math
from pathlib import Path
import random
import subprocess

from PIL import Image, ImageDraw, ImageFilter
from shorts_editor.graphics import text_box
from shorts_editor.store import write_json
from .assets import register_asset
from .core import Held, digest
from .transcripts import write_srt


KINDS=('collapse','life_raft','battleworld','throne','control','hidden_power','meal','confrontation','rebuilding','restoration',
       'dominion','memory','source_closeup','meal_detail','absence','duel','consequence')
SIZE=(720,1280)
ART=(20,180,700,950)
NOTE='Original symbolic code-drawn illustration, not an official comic panel, movie frame, literal character performance or additional evidence.'


def _kind(text):
    value=text.casefold()
    for words,kind in ((('hamburger','hungry','food','thank-you'),'meal'),
        (('mother','family restored'),'restoration'),(('rebuild','creating worlds','worlds back'),'rebuilding'),
        (('admit','confront','rival','concede','power passed'),'confrontation'),
        (('beneath','underneath','hidden','source sustaining'),'hidden_power'),(('raft',),'life_raft'),
        (('worship','throne'),'throne'),(('territory','answered','owning','control'),'control'),
        (('planet','battleworld'),'battleworld'),(('collaps','destroyed','dying','end'),'collapse')):
        if any(word in value for word in words):return kind
    return 'battleworld'


def plan_lore(script,request,brief):
    if not isinstance(brief,dict) or brief.get('kind')!='fact' or not brief.get('sources') or not brief.get('claims'):
        raise Held('lore_evidence','Comic lore needs a factual brief about the identified fictional canon.')
    units=script['units'];ids={u['id'] for u in units};overrides=request.get('lore_scenes',{})
    if not isinstance(overrides,dict) or set(overrides)-ids or any(v not in KINDS for v in overrides.values()):
        raise Held('lore_scene','Map known message IDs to a supported original lore scene kind.')
    claims={c['id']:c for c in brief['claims']};sources={s['id'] for s in brief['sources']}
    speakers={u['speaker'] for u in units}
    if len(speakers)!=1:raise Held('lore_voice','This lore format uses one consistent voice-only narrator.')
    scenes=[]
    for index,unit in enumerate(units):
        refs=unit.get('claim_ids',[])
        if not isinstance(refs,list) or any(c not in claims or claims[c]['source_id'] not in sources for c in refs) or (unit['kind']=='fact' and not refs):
            raise Held('lore_evidence','Every lore fact must retain actual source-linked claim IDs.')
        label=unit['onscreen']
        if not isinstance(label,str) or not label.strip() or len(label)>70:
            raise Held('lore_label','Use an exact short onscreen phrase, at most 70 characters.')
        scenes.append({'unit_id':unit['id'],'text':unit['text'],'speaker_id':'narrator','kind':overrides.get(unit['id'],_kind(unit['text'])),
            'label':label,'claim_ids':list(refs),'pause_after':.28 if index==len(units)-1 else .18,
            'visible_cast':[],'framing':'wide','motion':'panel_reveal','illustration_note':NOTE})
    plan={'version':1,'template':'comic_lore','cast':[{'id':'narrator','speaker':next(iter(speakers)),'voice_id':'bm_george','avatar_kind':'narrator','role':'voice-only narrator'}],
        'scenes':scenes,'sources':deepcopy(brief['sources']),'claims':deepcopy(brief['claims']),
        'script_sha256':digest(script),'brief_sha256':digest(brief),'comment_question':'','illustration_note':NOTE}
    return {'plan':plan,'script_sha256':digest(script),'origin':'compiled_lore_rules_v1',
        'scope':'Finite source-linked illustration rules, not an independent factual or audience-quality verdict.'}


def _ease(value):return 1-(1-max(0,min(1,value)))**3


@lru_cache(maxsize=20)
def _background(kind):
    palette={'collapse':('#190e20','#ed6648'),'life_raft':('#101b35','#70dae0'),'battleworld':('#0d2420','#89ce98'),
        'throne':('#0c201b','#bba562'),'control':('#14221d','#d5b36d'),'hidden_power':('#101c25','#6be5d6'),
        'meal':('#272031','#edbd75'),'confrontation':('#141c2d','#a6b7f5'),'rebuilding':('#10232f','#9ed7e5'),
        'restoration':('#2c2120','#f0cba1'),'dominion':('#12201b','#b6a364'),'memory':('#182432','#9ccedb'),
        'source_closeup':('#10292b','#a2fcde'),'meal_detail':('#33231f','#f7c785'),
        'absence':('#222331','#9e9cc2'),'duel':('#141e2d','#bbc6eb'),'consequence':('#272723','#dbca89')}
    base,accent=palette[kind];image=Image.new('RGB',SIZE,'#080e17');d=ImageDraw.Draw(image)
    d.polygon([(24,202),(693,180),(694,911),(30,947)],fill=base,outline='#d7d1bf',width=4)
    rng=random.Random(8821)
    for _ in range(110):
        x=rng.randrange(40,680);y=rng.randrange(215,920);r=rng.choice([1,1,1,2])
        d.ellipse((x-r,y-r,x+r,y+r),fill='#819087' if r==1 else accent)
    for y in range(220,925,18):
        for x in range(36,694,18):
            if (x+y)%54==0:d.ellipse((x,y,x+2,y+2),fill='#27343a')
    # Quiet caption-safe area: no characters, labels or decorative banners.
    for y in range(950,1280):d.line((0,y,720,y),fill=(8,14,23))
    return image


def _glow(layer,xy,radius,color,alpha=90):
    # Blur a small local tile, not a full 720x1280 sheet for every frame.
    radius=round(radius);size=radius*4
    halo=_halo(radius,color,alpha)
    layer.alpha_composite(halo,dest=(round(xy[0]-size/2),round(xy[1]-size/2)))


@lru_cache(maxsize=48)
def _halo(radius,color,alpha):
    r=max(1,round(radius/4));tile=Image.new('RGBA',(r*4,r*4));d=ImageDraw.Draw(tile)
    d.ellipse((r,r,3*r,3*r),fill=(*color,alpha))
    return tile.filter(ImageFilter.GaussianBlur(max(1,r/3))).resize((radius*4,radius*4),Image.Resampling.BILINEAR)


def _world(layer,cx,cy,radius,fill='#317879',progress=1,patchwork=False):
    d=ImageDraw.Draw(layer);r=radius;ink='#08151f'
    d.ellipse((cx-r+5,cy-r+7,cx+r+5,cy+r+7),fill=(0,0,0,150))
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=fill,outline='#cfddd3',width=4)
    mask=Image.new('L',layer.size);md=ImageDraw.Draw(mask);md.ellipse((cx-r+3,cy-r+3,cx+r-3,cy+r-3),fill=255)
    terrain=Image.new('RGBA',layer.size);td=ImageDraw.Draw(terrain)
    if patchwork:
        colors=['#7f704e','#315d7d','#786347','#567251','#624b73','#23615c']
        sectors=[ [(-1.4,-1.3),(-.15,-1.3),(-.35,-.43),(-.12,-.1),(-.65,.12),(-1.4,-.08)],
            [(-.15,-1.3),(1.3,-1.3),(.62,-.35),(.22,-.4),(-.12,-.1),(-.35,-.43)],
            [(1.3,-1.3),(1.4,.4),(.55,.18),(.32,.44),(-.12,-.1),(.22,-.4),(.62,-.35)],
            [(1.4,.4),(1.4,1.3),(.15,1.3),(.02,.65),(.32,.44),(.55,.18)],
            [(.15,1.3),(-1.3,1.4),(-.72,.5),(-.38,.44),(-.12,-.1),(.32,.44),(.02,.65)],
            [(-1.3,1.4),(-1.4,-.08),(-.65,.12),(-.12,-.1),(-.38,.44),(-.72,.5)]]
        for i,points in enumerate(sectors):
            scaled=[(cx+x*r,cy+y*r) for x,y in points]
            td.polygon(scaled,fill=colors[i]);td.line(scaled+[scaled[0]],fill='#dbbe70',width=4)
        for i in range(5):
            x=cx-r*.68+i*r*.105;h=r*(.11+(i%3)*.07)
            td.rectangle((x,cy-r*.29-h,x+r*.07,cy-r*.29),fill='#c3b885')
        for i in range(3):
            x=cx+r*.20+i*r*.16;y=cy+r*.58
            td.polygon([(x-r*.1,y),(x,y-r*.2),(x+r*.1,y)],fill='#bda27e')
    else:
        pts=[(-.8,-.35),(-.45,-.7),(-.12,-.43),(.06,-.5),(.28,-.16),(.01,.06),(.2,.32),(-.04,.73),(-.28,.5),(-.31,.13),(-.69,.07)]
        td.polygon([(cx+x*r,cy+y*r) for x,y in pts],fill='#b5ad73',outline='#d8cf9b')
        td.polygon([(cx+.48*r,cy+.22*r),(cx+.82*r,cy+.12*r),(cx+.67*r,cy+.63*r),(cx+.35*r,cy+.53*r)],fill='#82996c')
    terrain.putalpha(Image.composite(terrain.getchannel('A'),Image.new('L',layer.size),mask));layer.alpha_composite(terrain)
    d=ImageDraw.Draw(layer);d.arc((cx-r*.90,cy-r*.84,cx+r*.95,cy+r*.85),210,310,fill='#ecedca',width=3)
    d.arc((cx-r*.78,cy-r*.75,cx+r*.83,cy+r*.9),20,120,fill=ink,width=max(4,round(r*.06)))


def _figure(draw,x,y,scale=1,color='#0b111a',hood=False,arm=None):
    # Deliberately symbolic original silhouettes, without franchise costumes/logos.
    s=scale
    draw.ellipse((x-18*s,y-80*s,x+18*s,y-44*s),fill=color,outline='#a0b1b4',width=2)
    if hood:
        draw.polygon([(x,y-96*s),(x-45*s,y-62*s),(x-64*s,y+80*s),(x+64*s,y+80*s),(x+45*s,y-62*s)],fill=color,outline='#c4b474',width=3)
        draw.polygon([(x-18*s,y-73*s),(x+18*s,y-73*s),(x+17*s,y-49*s),(x,y-39*s),(x-17*s,y-49*s)],fill='#aab9ab',outline='#dae1ce',width=2)
        draw.line((x-12*s,y-60*s,x-3*s,y-59*s),fill='#182a24',width=max(2,round(3*s)))
        draw.line((x+3*s,y-59*s,x+12*s,y-60*s),fill='#182a24',width=max(2,round(3*s)))
        draw.line((x,y-52*s,x,y-44*s),fill='#677c70',width=2)
    else:
        draw.polygon([(x-25*s,y-43*s),(x+25*s,y-43*s),(x+36*s,y+35*s),(x+18*s,y+40*s),(x+15*s,y+95*s),(x+2*s,y+95*s),(x,y+38*s),(x-7*s,y+95*s),(x-22*s,y+95*s),(x-18*s,y+35*s),(x-38*s,y+35*s)],fill=color,outline='#84969d',width=2)
    if arm:
        tx,ty=arm;draw.line((x+20*s,y-30*s,tx,ty),fill=color,width=max(6,round(16*s)));draw.ellipse((tx-6*s,ty-6*s,tx+6*s,ty+6*s),fill='#b8ac93')


def _throne(layer,center=360,top=335,scale=1,figure=True):
    d=ImageDraw.Draw(layer);x=center;y=top;s=scale
    points=[(x-100*s,y+340*s),(x-100*s,y+150*s),(x-75*s,y+150*s),(x-75*s,y),(x-35*s,y+30*s),(x,y-40*s),(x+35*s,y+30*s),(x+75*s,y),(x+75*s,y+150*s),(x+100*s,y+150*s),(x+100*s,y+340*s)]
    d.polygon(points,fill='#294135',outline='#c8b870',width=4)
    d.rectangle((x-120*s,y+280*s,x+120*s,y+330*s),fill='#354c39',outline='#d0bd76',width=3)
    if figure:_figure(d,x,y+220*s,1.15*s,'#12271e',hood=True)
    d.polygon([(x-165*s,y+340*s),(x+165*s,y+340*s),(x+210*s,y+385*s),(x-210*s,y+385*s)],fill='#263b30',outline='#6f7c61',width=3)


def _energy(draw,points,color='#88eadb',width=5):
    draw.line(points,fill='#173d42',width=width+8,joint='curve');draw.line(points,fill=color,width=width,joint='curve')


def _burger(d,x,y,scale=1):
    def box(a,b,c,e):return (x+a*scale,y+b*scale,x+c*scale,y+e*scale)
    d.rounded_rectangle(box(-70,-31,70,32),radius=round(18*scale),fill='#d9a153',outline='#f1cf8b',width=3)
    d.ellipse(box(-70,-57,70,9),fill='#e7bb6e',outline='#f5d697',width=3)
    d.rectangle(box(-71,-3,71,12),fill='#456745');d.rectangle(box(-72,11,72,25),fill='#6e382a')
    for i in range(5):d.ellipse(box(-42+i*20,-37-(i%2)*6,-37+i*20,-33-(i%2)*6),fill='#f6e7b2')
    d.line((x-91*scale,y+44*scale,x+91*scale,y+44*scale),fill='#cedbd3',width=max(2,round(8*scale)))


def _art(scene,second,duration):
    kind=scene['kind'];p=max(0,min(1,second/duration));reveal=_ease(second/.65)
    layer=Image.new('RGBA',SIZE);d=ImageDraw.Draw(layer)
    if kind=='dominion':
        _glow(layer,(360,525),230,(100,149,98),105)
        _world(layer,189,696,115,'#395951',patchwork=True);_world(layer,550,698,104,'#6b5b67')
        d=ImageDraw.Draw(layer)
        for i in range(10):
            a=i*.628+second*.12;x=360+math.cos(a)*254;y=565+math.sin(a)*210
            d.polygon([(x-18,y),(x+10,y-15),(x+17,y+17)],fill='#8b8062',outline='#c5b77f')
        _throne(layer,360,318,1.17)
    elif kind=='collapse':
        shift=round(34*p)
        _glow(layer,(360,550),135,(238,92,59),90)
        _world(layer,245-shift,472,155,'#285d72');_world(layer,476+shift,680,158,'#684e73')
        d=ImageDraw.Draw(layer);crack=[(410,245),(365,365),(410,455),(320,550),(385,625),(326,730),(355,877)]
        _energy(d,crack[:max(2,round(2+5*reveal))],'#f4bc81',7)
        for i in range(12):
            a=i*2.4;r=90+p*190;x=360+math.cos(a)*r;y=550+math.sin(a)*r
            d.polygon([(x,y),(x+17,y+4),(x+5,y+21)],fill='#95684b',outline='#d9a570')
    elif kind=='life_raft':
        _world(layer,135-30*p,690,190,'#4b516e');d=ImageDraw.Draw(layer)
        for i in range(9):d.line((68+i*55,270+i*44,110+i*55,235+i*44),fill='#688ea5',width=2)
        x=390+55*p;y=510-30*p
        _glow(layer,(x-95,y+65),80,(89,204,226),100);d=ImageDraw.Draw(layer)
        d.polygon([(x-145,y+55),(x-62,y-72),(x+95,y-42),(x+152,y+58),(x+55,y+105),(x-110,y+100)],fill='#c0c2ad',outline='#eef0d8',width=5)
        d.polygon([(x-60,y-35),(x+70,y-17),(x+105,y+35),(x-93,y+25)],fill='#263951',outline='#4a7185',width=3)
        for i in range(4):d.ellipse((x-55+i*35,y+43,x-36+i*35,y+62),fill='#d9e6bc')
        d.polygon([(x-150,y+65),(x-222-25*p,y+95),(x-143,y+92)],fill='#6ed9db')
    elif kind=='battleworld':
        _glow(layer,(360,565),245,(83,169,139),75);_world(layer,360,565,235,'#2d7871',patchwork=True)
        d=ImageDraw.Draw(layer)
        for i in range(4):
            a=.7+i*1.5;x=360+math.cos(a+p*.18)*285;y=565+math.sin(a+p*.18)*245
            d.polygon([(x-18,y),(x+8,y-18),(x+25,y+13),(x-12,y+27)],fill='#74816d',outline='#b9bb89')
    elif kind in ('throne','control'):
        _glow(layer,(360,455),145,(95,159,100),60);_throne(layer)
        d=ImageDraw.Draw(layer)
        if kind=='control':
            for x,y in [(120,790),(595,770),(350,855)]:
                _energy(d,[(360,615),(360+(x-360)*.4,680),(x,y)],'#d5bc73',3)
                d.ellipse((x-38,y-23,x+38,y+23),fill='#47594a',outline='#b7b67c',width=3)
        else:
            for i in range(7):_figure(d,105+i*84,844+abs(3-i)*10,.45,'#0a1318')
        d.arc((290,335,430,475),210,330,fill='#d3ca82',width=round(3+2*reveal))
    elif kind=='hidden_power':
        _throne(layer,360,255,.62);d=ImageDraw.Draw(layer)
        d.polygon([(50,598),(672,570),(673,615),(49,646)],fill='#d4d1b6')
        d.polygon([(105,683),(615,664),(641,871),(87,897)],fill='#112e36',outline='#5d9b9a',width=4)
        discovery=_ease((second-.25)/min(1.2,max(.45,duration*.24)))
        hidden=Image.new('RGBA',SIZE);hd=ImageDraw.Draw(hidden)
        hd.ellipse((288,708,432,852),fill='#318b86',outline='#bdfff2',width=4)
        _figure(hd,360,790,.82,'#c0f8e6')
        hidden.putalpha(hidden.getchannel('A').point(lambda a:round(a*discovery)))
        layer.alpha_composite(hidden)
        _glow(layer,(360,780),round(85+25*discovery),(102,234,217),round(105*discovery))
        d=ImageDraw.Draw(layer)
        if discovery>.2:
            _energy(d,[(360,702),(360,610),(360,535)],'#7ae8d9',7)
            d.polygon([(360,515),(344,547),(376,547)],fill='#b4ffeb')
            for i in range(3):
                pulse=(second*.72+i/3)%1;y=700-pulse*155
                d.ellipse((350,y-9,370,y+9),fill='#e0fff5')
            d.arc((262,683,458,871),25+second*55,155+second*55,fill='#70d9d0',width=4)
        # Role labels are allowed only when already named in this bound line.
        text=(scene.get('text','')+' '+scene.get('label','')).casefold()
        if 'doom' in text:text_box(d,'DOOM',(463,398,180,48),'#ede4bb',30,True,minimum=26)
        if 'molecule man' in text:text_box(d,'MOLECULE MAN',(120,870,480,43),'#c7fff1',30,True,'center',minimum=26)
    elif kind=='memory':
        _world(layer,360,534,194,'#375b72');d=ImageDraw.Draw(layer)
        for i in range(6):
            a=i*1.05;dx=math.cos(a);dy=math.sin(a);r=20+160*p
            x=360+dx*r;y=530+dy*r
            d.polygon([(x,y),(x+30*dy,y-30*dx),(x+66*dx,y+66*dy)],fill='#a2d5d2',outline='#e0f2e4')
        for x in (230,360,490):_figure(d,x,811,.82,'#263b49')
    elif kind=='source_closeup':
        _glow(layer,(360,600),200,(94,236,202),105);d=ImageDraw.Draw(layer)
        for i in range(4):
            r=130+i*28;d.arc((360-r,600-r,360+r,600+r),second*100+i*75,second*100+i*75+240,fill='#6edac1',width=5)
        _figure(d,360,655,2.3,'#437d75')
        _energy(d,[(360,475),(360,357),(360,292)],'#9bfff1',8)
        d.polygon([(360,275),(342,312),(378,312)],fill='#bdffed')
    elif kind in ('meal','meal_detail'):
        _glow(layer,(480,625),110,(100,190,178),55);d=ImageDraw.Draw(layer)
        if kind=='meal':
            _figure(d,205,705,1.35,'#253e57',arm=(363,655));_figure(d,504,705,1.2,'#214f48',arm=(428,657))
            _burger(d,369+23*reveal,642-3*reveal)
        else:
            for i in range(12):
                a=i*.524+second*.07;d.line((360+math.cos(a)*215,597+math.sin(a)*178,360+math.cos(a)*285,597+math.sin(a)*253),fill='#b68b53',width=4)
            _burger(d,360,590,2.4+.14*p)
    elif kind=='absence':
        d.polygon([(150,794),(561,794),(625,906),(84,906)],fill='#3a404a')
        _figure(d,271,713,1.6,'#536982');d.ellipse((372,449,535,619),outline='#a2a8c2',width=5)
        d.arc((347,590,564,840),181,358,fill='#858da7',width=4)
        d.line((353,830,563,830),fill='#6f7890',width=4)
    elif kind in ('confrontation','duel'):
        _glow(layer,(360,565),140,(143,154,235),75);d=ImageDraw.Draw(layer)
        _figure(d,195,660,1.6,'#1d3b2b',hood=True);_figure(d,525,660,1.6,'#304b72',arm=(428,589))
        d.polygon([(360,330),(328,475),(370,559),(336,660),(367,835)],fill='#e0d7a9')
        if kind=='confrontation':
            orb_x=230+270*_ease((p-.2)/.6)
            _glow(layer,(orb_x,510),58,(150,245,213),100);d=ImageDraw.Draw(layer)
            d.ellipse((orb_x-25,485,orb_x+25,535),fill='#c9ffe6',outline='#f3f9c8',width=4)
            _energy(d,[(200,560),(orb_x,510),(510,560)],'#92cecb',3)
    elif kind=='rebuilding':
        _glow(layer,(360,600),185,(103,190,229),70)
        for i,(cx,cy,r) in enumerate([(207,405,107),(500,550,137),(260,774,125)]):
            q=_ease((p-i*.12)/.6);_world(layer,round(360+(cx-360)*q),round(600+(cy-600)*q),max(20,round(r*(.3+.7*q))),['#2d7779','#3b6885','#5c7961'][i])
        d=ImageDraw.Draw(layer)
        for i in range(12):
            a=i*1.8;x=360+math.cos(a)*(270-150*p);y=610+math.sin(a)*(240-120*p)
            d.line((x-5,y,x+5,y),fill='#deefcc',width=2);d.line((x,y-5,x,y+5),fill='#deefcc',width=2)
    elif kind=='restoration':
        _world(layer,360,415,160,'#547c78');d=ImageDraw.Draw(layer)
        _figure(d,290,734,1.2,'#65645c',arm=(385,695));_figure(d,424,751,.95,'#40576b',arm=(325,704))
        d.arc((201,602,519,885),200,340,fill='#ead8ae',width=5)
        d.polygon([(117,879),(601,879),(662,922),(52,922)],fill='#3a3637')
    elif kind=='consequence':
        _world(layer,241,492,119,'#408579',patchwork=True);d=ImageDraw.Draw(layer)
        d.line((87,642,636,642),fill='#a19678',width=4)
        _burger(d,225,765,.88)
        _figure(d,468,779,.87,'#6d6b5f',arm=(495,749));_figure(d,553,799,.70,'#495b71',arm=(501,755))
        _energy(d,[(306,765),(374,759),(418,751)],'#dfc184',5)
        d.polygon([(430,749),(406,740),(409,760)],fill='#dfc184')
    # Reveal the artwork, then retain gentle motion during the complete line.
    layer.putalpha(layer.getchannel('A').point(lambda a:round(a*(.57+.43*reveal))))
    return layer


def lore_frame(scene,second,duration):
    if scene.get('kind') not in KINDS:raise Held('lore_scene','Unsupported lore scene kind.')
    if not math.isfinite(duration) or duration<=0 or not math.isfinite(second):raise Held('lore_timing','Use finite measured lore timing.')
    image=_background(scene['kind']).copy().convert('RGBA');art=_art(scene,max(0,second),duration)
    image.alpha_composite(art)
    # Camera only moves the illustration viewport, keeping captions and title stable.
    progress=max(0,min(1,second/duration));zoom=1+.075*progress
    x1,y1,x2,y2=ART;viewport=image.crop(ART);w,h=viewport.size
    cw,ch=w/zoom,h/zoom;left=(w-cw)/2;top=(h-ch)*(.35 if scene['kind']=='hidden_power' else .5)
    image.paste(viewport.crop((round(left),round(top),round(left+cw),round(top+ch))).resize((w,h),Image.Resampling.LANCZOS),(x1,y1))
    label=scene.get('label','')
    text_box(ImageDraw.Draw(image),label,(42,46,636,125),'#f1ead6',44,True,minimum=29)
    return image.convert('RGB')


def render_lore_shot(scene,duration,path,*,paint=None):
    paint=paint or lore_frame
    if type(duration) not in (int,float) or not math.isfinite(duration) or not .5<=duration<=60:raise Held('lore_timing','Lore shots require complete measured 0.5-60 second durations.')
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);partial=path.with_suffix('.partial.mp4');log=path.with_suffix('.ffmpeg.log')
    paint(scene,min(duration*.7,duration-.05),duration).save(path.with_suffix('.png'))
    with log.open('wb') as errors:
        process=subprocess.Popen(['ffmpeg','-v','error','-nostdin','-y','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280',
            '-framerate','30','-i','pipe:0','-an','-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','20',
            '-threads','2','-pix_fmt','yuv420p',str(partial)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=errors)
        try:
            for frame in range(math.ceil(duration*30)):process.stdin.write(paint(scene,frame/30,duration).tobytes())
            process.stdin.close();process.wait(timeout=180)
            if process.returncode:raise Held('lore_render','Lore video encoding failed; inspect its retained log.')
        except BaseException:
            if process.poll() is None:process.kill();process.wait()
            if not process.stdin.closed:process.stdin.close()
            raise
    partial.replace(path)


def build_lore_visuals(ws,job,script,timing,folder,record):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);plan=record['plan']
    if record['script_sha256']!=digest(script) or plan.get('script_sha256')!=digest(script):raise Held('creative_rewrite','Lore scene plan differs from the frozen script.')
    if [s['unit_id'] for s in plan['scenes']]!=[u['id'] for u in timing['units']]:raise Held('lore_timing','Lore scenes must match measured speech in order.')
    units={u['id']:u for u in script['units']};claims={c['id']:c for c in plan['claims']};sources={s['id']:s for s in plan['sources']}
    rows=[];bindings=[];provenance=[]
    for scene,spoken in zip(plan['scenes'],timing['units']):
        unit=units[scene['unit_id']]
        if scene['text']!=unit['text'] or scene['label']!=unit['onscreen'] or scene['claim_ids']!=unit['claim_ids'] or scene['kind'] not in KINDS:
            raise Held('creative_rewrite','A lore illustration changed frozen text, labels or claim references.')
        refs=list(dict.fromkeys(claims[c]['source_id'] for c in scene['claim_ids']))
        urls=[sources[ref]['url'] for ref in refs]
        output=folder/(scene['unit_id']+'-lore.mp4');render_lore_shot(scene,spoken['duration'],output)
        made=register_asset(ws,output,'original_graphic',{'generator':'original-comic-lore-v1','unit_id':scene['unit_id'],
            'scene_kind':scene['kind'],'claim_ids':scene['claim_ids'],'source_urls':urls,'illustration_note':NOTE},test_only=job['request'].get('test_only',False))
        provenance.append(made)
        rows.append({'unit_id':scene['unit_id'],'file':str(output),'media_id':made['id'],'duration':spoken['duration'],'kind':'comic_lore','resolved_scene':scene})
        bindings.append({'unit_id':scene['unit_id'],'claim_ids':scene['claim_ids'],'source_urls':urls,'scope':'Source linkage only; illustration is not factual evidence.'})
    captions=folder/'captions.srt';write_srt([{'start':u['start'],'end':u['speech_end'],'text':u['text']} for u in timing['units']],captions)
    result={'version':1,'format':'lesson','frames':rows,'captions':str(captions),'planned_template':'comic_lore',
        'planned_provenance':provenance,'selected_media':[],'source_bindings':bindings,'creative_plan_sha256':digest(plan),
        'limits':[NOTE,'Finite source-linked diagrams, not model visual review, full comic adaptation, rigged acting or lip sync.']}
    write_json(folder/'visuals.json',result);return result
