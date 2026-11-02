"""Render local block previews, not a finished episode or an AI-written story.

Uses registered permitted sample assets. No model, generation or browser call.
"""
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from PIL import Image,ImageDraw,ImageOps
from shorts_editor.store import write_json
from yt_pipeline.assets import asset_record
from yt_pipeline.core import Workspace
from yt_pipeline.planned_visuals import _cast_frame,_stock_frame,_motion
from yt_pipeline.playbooks import export_playbooks


def main():
    ws=Workspace();folder=ROOT/'Resources/Templates/Previews';folder.mkdir(parents=True,exist_ok=True)
    inventory=json.loads((ROOT/'Resources/Plans/stock-pilot-assets.json').read_text())['assets']
    background=asset_record(ws,next(r['id'] for r in inventory if r['role']=='elevator'))
    heads=json.loads((ROOT/'Resources/Plans/cast-preview-assets.json').read_text())
    avatars={r['role']:asset_record(ws,r['asset_id']) for r in heads}
    cast={'cat':{'speaker':'Alex','costume':'blue shirt'},'dog':{'speaker':'Mike','costume':'red shirt'}}
    scenes=[('group',{'visible_cast':['cat','dog'],'focus_id':'','framing':'wide','motion':'hold'},'Two consistent cast identities'),
            ('alex-closeup',{'visible_cast':['cat','dog'],'focus_id':'cat','framing':'closeup','motion':'slow_push'},'Only the active speaker remains'),
            ('mike-closeup',{'visible_cast':['cat','dog'],'focus_id':'dog','framing':'closeup','motion':'punch'},'Same place; different speaker'),
            ('group-return',{'visible_cast':['cat','dog'],'focus_id':'','framing':'wide','motion':'hold'},'Return to the group for a reaction')]
    rows=[]
    for name,scene,caption in scenes:
        poster=folder/(name+'.png');clip=folder/(name+'.mp4')
        _cast_frame(background,cast,avatars,scene,caption,poster)
        _motion(poster,2,clip,scene['motion'])
        rows.append({'name':name,'scene':scene,'poster':str(poster),'video':str(clip)})
    sheet=Image.new('RGB',(720,1340),'#eeeeee');draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(rows):
        with Image.open(row['poster']) as im:thumb=ImageOps.contain(im,(350,620))
        x=(i%2)*360;y=(i//2)*670
        sheet.paste(thumb,(x,y+30));draw.text((x+12,y+8),row['name'],fill='black')
    sheet.save(folder/'cast-contact-sheet.jpg')
    clips=[f"[{i}:v]setpts=PTS-STARTPTS[v{i}]" for i in range(4)]
    command=['ffmpeg','-v','error','-y','-nostdin']
    for row in rows:command+=['-i',row['video']]
    graph=';'.join(clips)+';'+''.join(f'[v{i}]' for i in range(4))+'concat=n=4:v=1:a=0[out]'
    command+=['-filter_complex_threads','1','-filter_complex',graph,'-map','[out]','-an','-c:v','libx264','-preset','veryfast','-threads','2',str(folder/'cast-framing-demo.mp4')]
    subprocess.run(command,check=True,capture_output=True,timeout=120)
    sources=[background,*avatars.values()]
    write_json(folder/'preview-manifest.json',{'test_only':True,'purpose':'Technical framing/effect previews, not finished publishable episodes',
        'scenes':rows,'sources':[{'id':r['id'],'attribution':r['attribution'],'evidence':r['evidence']} for r in sources]})
    export_playbooks(ROOT/'Resources/Prompts')
    print(json.dumps({'preview':str(folder/'cast-framing-demo.mp4'),'contact_sheet':str(folder/'cast-contact-sheet.jpg'),'model_calls':0}))


if __name__=='__main__':main()
