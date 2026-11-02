"""Precompose two actual media slots; the reusable editor adds the caption strip."""
import math
from pathlib import Path
import subprocess

from shorts_editor.store import write_json
from .assets import asset_record,register_asset
from .core import Held,digest


def two_slot_bed(ws,assets,duration,start,folder,index):
    folder=Path(folder);folder.mkdir(exist_ok=True)
    starts=start if isinstance(start,(list,tuple)) else [start,start]
    identity=digest([a['sha256'] for a in assets]+[round(duration,6),[round(v,6) for v in starts],'two-slot-v2'])
    cache=ws.root/'cache'/('bed-'+identity+'.json')
    if cache.exists():
        import json
        return asset_record(ws,json.loads(cache.read_text())['asset_id'])
    path=folder/(f'bed-{index:03d}-'+identity[:8]+'.mp4');args=[]
    for asset,offset in zip(assets,starts):
        if asset['kind']=='image':args+=['-loop','1','-framerate','30','-i',asset['path']]
        elif asset['kind']=='video':args+=['-stream_loop','-1','-ss',str(round(offset%asset['duration'],4)),'-i',asset['path']]
        else:raise Held('montage_input','Visual slots need an image or video.')
    filters=';'.join(f'[{i}:v]scale=720:512:force_original_aspect_ratio=increase,crop=720:512,setsar=1,fps=30,setpts=PTS-STARTPTS[v{i}]' for i in range(2))
    filters+=';[v0][v1]vstack=inputs=2[out]'
    result=subprocess.run(['ffmpeg','-v','error','-nostdin','-y',*args,'-filter_complex_threads','1','-filter_complex',filters,
        '-map','[out]','-an','-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p',str(path)],capture_output=True,timeout=120)
    if result.returncode:raise Held('montage_render','Two-slot visual preparation failed. Its inputs were preserved.')
    asset=register_asset(ws,path,'licensed_stock',{'composed_from':[a['id'] for a in assets],'operation':'two visual blocks, crop and cuts'},
                         test_only=any(a.get('test_only') for a in assets))
    write_json(cache,{'asset_id':asset['id']});return asset_record(ws,asset['id'])


def plan_cuts(ws,job,script,timing,frames,selected):
    """Resolve a complete per-unit storyboard before spending time rendering beds.

    An optional decorative background is explicitly labelled; it is not claimed
    to illustrate the narration. There is no global round-robin media pool.
    """
    request=job['request'];ids=[u['id'] for u in script['units']]
    if ids!=[u['id'] for u in timing['units']] or ids!=[f['unit_id'] for f in frames]:
        raise Held('storyboard_timing','Script, speech and frames must have identical ordered unit IDs')
    mapping=request.get('storyboard')
    if mapping is None:
        decorative=request.get('decorative_background_id')
        selected_map={row['unit_id']:row['asset']['id'] for row in selected}
        if not decorative or len(selected)!=len(ids) or set(selected_map)!=set(ids):
            raise Held('storyboard_missing','Three-block video needs a per-unit storyboard, or per-unit media plus an explicitly decorative_background_id; unrelated asset rotation is disabled')
        mapping={uid:{'top':selected_map[uid],'bottom':decorative,'bottom_role':'decorative',
                      'purpose':'Unit-specific primary visual with explicitly decorative background'} for uid in ids}
    if not isinstance(mapping,dict) or set(mapping)!=set(ids):
        raise Held('storyboard_units','Storyboard must cover exactly the script unit IDs')
    max_length=float(job['request'].get('cut_interval',2.3))
    if not math.isfinite(max_length) or not 1<=max_length<=3:raise Held('cut_interval','Use a cut interval between one and three seconds.')
    planned=[];pool={}
    for unit,frame in zip(timing['units'],frames):
        if not math.isfinite(unit['duration']) or unit['duration']<=0:raise Held('storyboard_timing','Story units need positive finite duration')
        remaining=round(unit['duration']*30)
        if remaining<30:raise Held('storyboard_short_unit','Merge sub-second spoken units before using the three-block compositor')
        count=math.ceil(remaining/(max_length*30))
        count=min(count,max(1,remaining//30))
        rows=mapping[unit['id']];rows=rows if isinstance(rows,list) else [rows]
        if len(rows) not in (1,count):raise Held('storyboard_shots','Give one relevant pair for the unit or one pair per planned cut')
        offset=0
        for part in range(count):
            ticks=remaining//(count-part);remaining-=ticks;duration=ticks/30
            row=rows[part] if len(rows)>1 else rows[0]
            if not isinstance(row,dict) or row.get('bottom_role') not in ('semantic','decorative') or not isinstance(row.get('purpose'),str) or not row['purpose'].strip():
                raise Held('storyboard_intent','Each pair needs a visual purpose and bottom_role semantic/decorative')
            if not row.get('top') or not row.get('bottom') or row['top']==row['bottom']:
                raise Held('storyboard_assets','Each pair needs two distinct registered visual assets')
            pair=[];starts=[]
            for key in ('top','bottom'):
                asset=asset_record(ws,row[key])
                if asset['kind'] not in ('image','video'):raise Held('storyboard_assets','Storyboard slots need actual images or videos')
                pool[asset['id']]=asset;pair.append(asset)
                start=float(row.get(key+'_start',0))
                if not math.isfinite(start) or start<0:raise Held('storyboard_offset','Storyboard offsets must be finite and nonnegative')
                starts.append(start+offset)
            planned.append({'unit_id':unit['id'],'file':frame['file'],'duration':duration,'start':unit['start']+offset,
                            'pair':pair,'media_starts':starts,'purpose':row['purpose'],'bottom_role':row['bottom_role'],
                            'payoff_end':unit['id']==script['edit']['payoff_unit_id'] and part==count-1})
            offset+=duration
    if len(planned)>30:raise Held('montage_too_many_cuts','Shorten this script to fit thirty fast cuts.')
    return planned,list(pool.values())


def build_cuts(ws,job,script,timing,frames,selected,folder):
    planned,pool=plan_cuts(ws,job,script,timing,frames,selected)
    cuts=[]
    for i,row in enumerate(planned):
        bed=two_slot_bed(ws,row['pair'],row['duration'],row['media_starts'],Path(folder)/'beds',i)
        cuts.append({k:v for k,v in row.items() if k not in ('pair','media_starts')}|
                    {'media_id':bed['id'],'source_asset_ids':[a['id'] for a in row['pair']], 'source_offsets':row['media_starts']})
    return cuts,pool
