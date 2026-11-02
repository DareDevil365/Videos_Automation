"""Reusable aura-photo and cut-out storytime scenes with actual media provenance."""
from pathlib import Path
import math
import subprocess

from PIL import Image,ImageDraw,ImageOps
from shorts_editor.graphics import text_box
from shorts_editor.store import write_json
from .assets import asset_record,choose_background
from .core import Held,digest
from .media_agent import select_visuals
from .music_agent import choose_music


def aura_timing(ws,job,script,creative_plan=None):
    request=job['request'];profile=ws.config()['channels'][job['channel']]
    if request.get('playbook')=='aura_progression':
        if request.get('bottom_kind')=='asmr':raise Held('playbook_background','ASMR is reserved for story formats, not aura edits')
        if not creative_plan:raise Held('creative_plan_missing','Aura progression needs its validated edit plan')
        request={**request,'media_assets':{s['unit_id']:s['asset_id'] for s in creative_plan['scenes']}}
        job={**job,'request':request}
        if not request.get('music_id'):raise Held('playbook_music_missing','Aura needs an explicit suitable permitted beat track; no rejected synthetic fallback')
    selected=select_visuals(ws,{**job,'request':{**request,'media_kind':'image'}},script)
    music_id=request.get('music_id') or profile.get('music_id')
    music=asset_record(ws,music_id) if music_id else choose_music(ws,request.get('music_category','aura'),request.get('auto_download_music',False),request.get('music_query'))
    if not music['has_audio']:raise Held('music_audio','Aura montage needs a permitted audio track.')
    rows=[];elapsed=0
    for i,unit in enumerate(script['units']):
        default=(2.2 if i<len(script['units'])-1 else 3.2) if request.get('playbook')=='aura_progression' else (2 if i<len(script['units'])-1 else 3)
        duration=float(request.get('shot_durations',{}).get(unit['id'],default))
        if not math.isfinite(duration) or not 1<=duration<=10:raise Held('aura_duration','Aura shot duration must be 1–10 seconds.')
        duration=round(duration*30)/30
        rows.append({'id':unit['id'],'start':elapsed,'end':elapsed+duration,'speech_end':elapsed+duration,'duration':duration,'text':''})
        elapsed+=duration
    if elapsed>90:raise Held('aura_duration','Keep this aura montage under 90 seconds.')
    if request.get('playbook')=='aura_progression' and not 12<=elapsed<=24:raise Held('playbook_duration','Aura progression must resolve within its 12-24 second preset')
    result={'source':'aura_music','voice':'No narration — original edit captions and licensed music','duration':elapsed,'units':rows,
            'selected_media':selected,'music_id':music['id'],'model_sha256':digest([m['asset']['sha256'] for m in selected]+[music['sha256']]),'license_evidence':[]}
    if creative_plan:result['creative_scenes']=creative_plan['scenes']
    return result


def aura_scene(script,index,asset,duration,folder,progression=False,motion='slow_push'):
    folder=Path(folder);poster=folder/(script['units'][index]['id']+'-poster.png')
    score=round(-100+200*index/max(1,len(script['units'])-1))
    if asset['kind']=='video':
        from .planned_visuals import _video_scene
        output=folder/(script['units'][index]['id']+'.mp4')
        caption=script['units'][index]['onscreen']+(f' | AURA {score:+d}' if progression else '')
        _video_scene(asset,caption,duration,output,832,motion=motion)
        return output
    with Image.open(asset['path']) as raw:picture=ImageOps.fit(raw.convert('RGB'),(720,832),centering=(.5,.35))
    draw=ImageDraw.Draw(picture);draw.rectangle((0,680,720,832),fill='#0c0c10')
    text_box(draw,script['units'][index]['onscreen'],(35,705,650,100),'#ffffff',43,True,'center',minimum=26)
    if progression:
        draw.rounded_rectangle((24,25,350,100),radius=12,fill='#101014')
        text_box(draw,f'AURA {score:+d}',(38,36,298,48),'#ed5c6b' if score<0 else '#79d9a1',35,True)
    picture.save(poster);output=folder/(script['units'][index]['id']+'.mp4')
    if progression:
        from .planned_visuals import _motion
        _motion(poster,duration,output,motion,832)
        return output
    frames=math.ceil(duration*30)
    result=subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-i',str(poster),'-vf',
        f"scale=1440:1664,zoompan=z='min(zoom+0.0008,1.10)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s=720x832:fps=30",
        '-t',str(duration),'-an','-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p',str(output)],capture_output=True,timeout=90)
    if result.returncode:raise Held('aura_scene','Aura photo animation failed.')
    return output


def cutout_scene(script,index,duration,folder):
    """Original simple characters, not copied TV bodies or celebrity performances."""
    folder=Path(folder);base=folder/'stage.png'
    if not base.exists():
        image=Image.new('RGB',(720,1000),'#eee7d9');d=ImageDraw.Draw(image)
        d.rectangle((0,730,720,1000),fill='#c6b9a1');d.rectangle((55,100,665,680),outline='#9b8e79',width=5)
        d.rectangle((180,110,540,380),fill='#adc1c9');d.line((360,110,360,380),fill='white',width=6)
        image.save(base)
    colors=['#325c9a','#ae493a'];actors=[]
    for i in range(2):
        path=folder/(f'actor-{i}.png')
        if not path.exists():
            image=Image.new('RGBA',(270,580));d=ImageDraw.Draw(image)
            d.rounded_rectangle((70,260,220,490),radius=35,fill=colors[i]);d.line((105,480,90,565),fill='#28282d',width=28);d.line((185,480,200,565),fill='#28282d',width=28)
            d.ellipse((20,20,260,270),fill='#efbd91',outline='#202027',width=6)
            d.ellipse((75,120,95,140),fill='#222222');d.ellipse((175,120,195,140),fill='#222222')
            d.arc((100,155,170,215),0,180,fill='#202027',width=6);image.save(path)
        actors.append(path)
    caption=folder/(script['units'][index]['id']+'-caption.png')
    image=Image.new('RGBA',(720,220));d=ImageDraw.Draw(image);d.rounded_rectangle((25,15,695,200),radius=24,fill='#16161df0')
    text_box(d,script['units'][index]['onscreen'],(50,40,620,130),'#ffffff',43,True,'center',minimum=25);image.save(caption)
    output=folder/(script['units'][index]['id']+'.mp4')
    active=index%2
    filters=f"[0:v][1:v]overlay=x=30:y='390+{12 if active==0 else 2}*sin(t*13)'[l];[l][2:v]overlay=x=410:y='390+{12 if active==1 else 2}*sin(t*13)'[r];[r][3:v]overlay=x=0:y=20[out]"
    args=[]
    for path in [base,*actors,caption]:args+=['-loop','1','-framerate','30','-i',str(path)]
    result=subprocess.run(['ffmpeg','-v','error','-nostdin','-y',*args,'-filter_complex_threads','1','-filter_complex',filters,'-map','[out]','-t',str(duration),'-an',
                           '-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-pix_fmt','yuv420p',str(output)],capture_output=True,timeout=120)
    if result.returncode:raise Held('cutout_scene','Original cut-out scene rendering failed.')
    return output
