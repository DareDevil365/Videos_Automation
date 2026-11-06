"""Verify a completed local package and sample every directed cut for visual review.

This makes a contact sheet and technical evidence, not a subjective acceptance.
"""
from argparse import ArgumentParser
import json
from pathlib import Path
import re
import subprocess
import sys

from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from yt_pipeline.core import file_hash
from yt_pipeline.lore_cuts import cut_schedule
from shorts_editor.store import write_json


def review(folder):
    folder=folder.resolve()
    batch=json.loads((folder.parent/'batch.json').read_text(encoding='utf8'))
    item=next(i for i in batch['items'] if Path(i['output_folder']).resolve()==folder)
    if item['status']!='ready':raise ValueError('Review only a completed export.')
    for path,expected in item['output_hashes'].items():
        if file_hash(Path(path))!=expected:raise ValueError('Changed package file: '+path)
    voice=json.loads((folder/'voice.json').read_text(encoding='utf8'))
    visuals=json.loads((folder/'visuals.json').read_text(encoding='utf8'))
    quality=json.loads((folder/'quality.json').read_text(encoding='utf8'))
    samples=[];cta=None
    for frame,spoken in zip(visuals['frames'],voice['units']):
        scene=frame['resolved_scene']
        schedule=cut_schedule(scene,spoken,voice.get('word_timings',[]))
        for cut in schedule or [{'start':0,'end':spoken['duration'],'kind':scene['kind']}]:
            start=spoken['start']+cut['start'];end=spoken['start']+cut['end']
            samples.append({'unit':scene['unit_id'],'kind':cut['kind'],'start':start,'end':end,'sample':(start+end)/2})
            if cut['kind']=='end_subscribe':cta={'start':start,'end':end,'anchor':cut['on']}
    if not cta or cta['anchor']!='For more stories':raise ValueError('Missing speech-anchored subscribe ending.')
    if cta['start']<voice['units'][-1]['start']:raise ValueError('Subscribe appears before the ending unit.')
    temp=folder/'review-frames';temp.mkdir(exist_ok=True)
    sheet=Image.new('RGB',(1152,536*((len(samples)+3)//4)),'#191919')
    for n,row in enumerate(samples):
        target=temp/f'{n:02d}.jpg'
        subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-ss',str(row['sample']),'-i',str(folder/'video.mp4'),'-frames:v','1','-q:v','2',str(target)],check=True)
        with Image.open(target) as im:sheet.paste(im.resize((288,512)),(n%4*288,n//4*536))
        ImageDraw.Draw(sheet).text((n%4*288+4,n//4*536+514),f"{row['sample']:.2f}s {row['kind']}",fill='white')
    sheet.save(folder/'export-review.jpg',quality=94)
    check=subprocess.run(['ffmpeg','-v','info','-nostdin','-i',str(folder/'narration.wav'),'-af','silencedetect=noise=-42dB:d=0.3','-f','null','-'],capture_output=True,text=True,check=True)
    quiet=len(re.findall(r'silence_start:',check.stderr))
    result={'duration':quality['duration'],'technical_pass':quality['technical_pass'],
            'video_sha256':file_hash(folder/'video.mp4'),'verified_package_hashes':len(item['output_hashes']),
            'sampled_shots':samples,'subscribe':cta,'speech_silence_over_0_3s_at_minus42dB':quiet,
            'audio_clipped_fraction':quality['audio']['clipped_fraction'],'voices':voice['cast_voices'],
            'publication_ready':quality['publication_ready'],'visual_inspection':'Contact sheet prepared; inspect it before recording acceptance.'}
    write_json(folder/'finished-review.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='sampled_shots'},indent=2))
    print(folder/'export-review.jpg')


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__);parser.add_argument('folder',type=Path)
    review(parser.parse_args().folder)
