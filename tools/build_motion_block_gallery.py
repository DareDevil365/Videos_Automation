"""Render reusable block examples with the same code used in production."""
from pathlib import Path
import sys

from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from yt_pipeline.scene_blocks import block_frame,validate_block
from shorts_editor.graphics import text_box
from shorts_editor.store import write_json


def main():
    folder=ROOT/'Resources/Templates/MotionBlocks';folder.mkdir(parents=True,exist_ok=True)
    blocks=[{'kind':'comparison','title':'Before and After','labels':['I helped the team','I checked the receipt and fixed the order']},
            {'kind':'process','title':'Try this','labels':['Check the receipt','Tell the teammate','Deliver the corrected drinks']},
            {'kind':'callout','title':'Your turn','labels':['What did YOU actually do?']}]
    unit={'text':' '.join(label for b in blocks for label in b['labels']),'onscreen':''}
    gallery=Image.new('RGB',(1080,720),'#ddd8cf');draw=ImageDraw.Draw(gallery)
    for i,block in enumerate(blocks):
        validate_block(block,unit)
        path=folder/(block['kind']+'.png');block_frame(block,path)
        with Image.open(path) as raw:picture=raw.resize((337,600),Image.Resampling.LANCZOS)
        gallery.paste(picture,(i*360+11,55))
        text_box(draw,block['kind'].upper(),(i*360+15,15,330,30),'#20242c',22,True)
    output=folder/'gallery.jpg';gallery.save(output,quality=92)
    write_json(folder/'examples.json',{'version':1,'blocks':blocks,'purpose':'Static capability examples, not a complete scripted production.'})
    print(output)


if __name__=='__main__':main()
