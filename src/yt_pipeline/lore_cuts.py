"""Speech-anchored visual cuts without fragmenting or rewriting narration."""
from copy import deepcopy
import re

from .core import Held


def tokens(text):return re.findall(r'[a-z0-9]+',text.casefold())


def compile_cuts(scenes,request,kinds,cameras):
    raw=request.get('lore_cuts',{})
    if not isinstance(raw,dict) or set(raw)-{s['unit_id'] for s in scenes}:
        raise Held('lore_cut','Cuts must reference existing spoken beats.')
    for scene in scenes:
        if scene['unit_id'] not in raw:continue
        rows=raw[scene['unit_id']]
        if not isinstance(rows,list) or not 2<=len(rows)<=6:raise Held('lore_cut','Use two to six purposeful shots within one spoken beat.')
        compiled=[];spoken=tokens(scene['text']);previous=-1
        for n,row in enumerate(rows):
            if (not isinstance(row,dict) or set(row)-{'on','kind','camera','reason'} or not isinstance(row.get('on'),str)
                    or row.get('kind') not in kinds or row.get('camera','wide') not in cameras
                    or not isinstance(row.get('reason'),str) or not row['reason'].strip()):
                raise Held('lore_cut','Each shot needs a supported scene/camera, an exact speech anchor and a purpose.')
            anchor=tokens(row['on'])
            if n==0:
                if anchor:raise Held('lore_cut','The first shot starts with the beat: use an empty anchor.')
                index=0
            else:
                matches=[i for i in range(len(spoken)-len(anchor)+1) if spoken[i:i+len(anchor)]==anchor] if anchor else []
                if len(matches)!=1 or matches[0]<=previous:raise Held('lore_cut','Use unique, ordered phrases from this exact spoken beat.')
                index=matches[0]
            previous=index
            compiled.append({**deepcopy(row),'camera':row.get('camera','wide'),'token_index':index})
        if compiled[0]['kind']!=scene['kind']:raise Held('lore_cut','The first shot must match the beat’s base scene.')
        scene['cuts']=compiled


def cut_schedule(scene,spoken,word_timings,*,preview=False):
    cuts=scene.get('cuts')
    if not cuts:return []
    aligned=[]
    for word in word_timings:
        if word.get('unit_id')==scene['unit_id']:
            aligned.extend((t,word['start']-spoken['start']) for t in tokens(word['text']))
    if not aligned and not preview:raise Held('lore_cut_timing','Speech-anchored cuts require this beat’s actual aligned word times.')
    starts=[]
    for n,cut in enumerate(cuts):
        if n==0:time=0
        elif preview:time=spoken['duration']*cut['token_index']/len(tokens(scene['text']))
        else:
            anchor=tokens(cut['on']);words=[w[0] for w in aligned]
            matches=[i for i in range(len(words)-len(anchor)+1) if words[i:i+len(anchor)]==anchor]
            if len(matches)!=1:raise Held('lore_cut_timing','The exact cut anchor is missing or ambiguous in aligned speech.')
            time=max(0,aligned[matches[0]][1])
        starts.append(time)
    ends=[*starts[1:],spoken['duration']]
    if any(end-start<.5 for start,end in zip(starts,ends)):
        raise Held('lore_cut_timing','A planned shot is shorter than half a second; revise its anchor for readable complete visuals.')
    return [{**cut,'start':start,'end':end} for cut,start,end in zip(cuts,starts,ends)]


def cut_painter(paint,schedule):
    if not schedule:return paint
    def frame(scene,second,duration):
        active=next((s for s in reversed(schedule) if second>=s['start']),schedule[0])
        shot={**scene,'kind':active['kind'],'framing':active['camera']}
        shot.pop('cuts',None)
        return paint(shot,max(0,second-active['start']),active['end']-active['start'])
    return frame
