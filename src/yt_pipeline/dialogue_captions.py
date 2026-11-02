"""Align the exact script to its local speech; never replace words with ASR text."""
import re
from pathlib import Path
from .core import Held,digest,file_hash
from shorts_editor.store import write_json


def exact_words(text,alignment,duration):
    words=re.findall(r'\S+',text)
    canonical=lambda value:re.sub(r'\s+','',value)
    if canonical(''.join(r['word'] for r in alignment))!=canonical(text):
        raise Held('caption_alignment_text','Alignment did not preserve the complete spoken script')
    spans=[];cursor=0
    for row in alignment:
        n=len(canonical(row['word']));spans.append((cursor,cursor+n,row));cursor+=n
    result=[];cursor=0
    for word in words:
        stop=cursor+len(canonical(word));hits=[r for a,b,r in spans if a<stop and b>cursor]
        if not hits:raise Held('caption_alignment_text','A spoken word has no alignment')
        start=max(0,float(hits[0]['start']));end=min(duration,float(hits[-1]['end']))
        if not 0<=start<=end<=duration+.001:raise Held('caption_alignment_timing','A word could not be aligned to usable speech timing')
        result.append({'text':word,'start':start,'end':end});cursor=stop
    # DTW occasionally assigns two words the same boundary. Redistribute only
    # that local cluster between its neighbouring audio anchors, retaining words.
    boundaries=[r['start'] for r in result]+[result[-1]['end']]
    i=0
    while i<len(boundaries)-1:
        if boundaries[i]<boundaries[i+1]:i+=1;continue
        a=i
        while i+1<len(boundaries) and boundaries[i+1]<=boundaries[i]:i+=1
        lo=max(0,a-1);hi=min(len(boundaries)-1,i+1)
        left=boundaries[lo];right=boundaries[hi]
        if right<=left:raise Held('caption_alignment_timing','A word cluster has no usable audio anchors')
        for j in range(lo+1,hi):boundaries[j]=left+(right-left)*(j-lo)/(hi-lo)
        for j in range(lo,hi):result[j]['timing_estimated']=True
        i=hi
    for i,row in enumerate(result):row.update(start=boundaries[i],end=boundaries[i+1])
    return result


def progressive_cues(words):
    """Reveal every original word in small accumulating phrases, with no summaries."""
    groups=[];group=[]
    for word in words:
        if group and (len(group)>=5 or len(' '.join([r['text'] for r in group]+[word['text']]))>42):groups.append(group);group=[]
        group.append(word)
    if group:groups.append(group)
    cues=[]
    for group in groups:
        for i,word in enumerate(group):
            start=word['start'];end=group[i+1]['start'] if i+1<len(group) else word['end']
            if end<=start:raise Held('caption_alignment_timing','Word start times must progress for timed subtitle reveal')
            cues.append({'start':start,'end':end,'text':' '.join(r['text'] for r in group[:i+1])})
    return cues


def align_dialogue(ws,timing,model='tiny.en'):
    try:
        from faster_whisper import WhisperModel
        from faster_whisper.audio import decode_audio,pad_or_trim
        from faster_whisper.tokenizer import Tokenizer
    except ImportError:raise Held('caption_aligner_missing','Install the local faster-whisper source dependencies for complete dialogue subtitles')
    runtime=None;all_words=[];cues=[]
    for unit in timing['units']:
        key=digest(['exact-script-align-v1',model,file_hash(unit['file']),unit['text']])
        path=ws.root/'cache'/('word-alignment-'+key+'.json')
        if path.exists():
            import json
            rows=json.loads(path.read_text(encoding='utf-8'))['words']
        else:
            if runtime is None:
                try:runtime=WhisperModel(model,device='cpu',compute_type='int8',download_root=str(ws.root/'voices'/'asr'),local_files_only=True)
                except Exception as exc:raise Held('caption_model_missing','The local tiny.en alignment model is unavailable. Install the local ASR model before producing dialogue subtitles.') from exc
            audio=decode_audio(unit['file'],sampling_rate=16000)
            if len(audio)>29*16000:raise Held('caption_alignment_length','Split spoken units longer than 29 seconds before alignment')
            features=runtime.feature_extractor(audio);frames=min(features.shape[-1],3000)
            encoded=runtime.encode(pad_or_trim(features))
            tokenizer=Tokenizer(runtime.hf_tokenizer,runtime.model.is_multilingual,task='transcribe',language='en')
            aligned=runtime.find_alignment(tokenizer,[tokenizer.encode(unit['text'])],encoded,frames)[0]
            rows=exact_words(unit['text'],aligned,unit['metrics']['duration'])
            write_json(path,{'words':rows,'model':model,'method':'forced alignment of original script tokens'})
        global_words=[{**r,'start':r['start']+unit['start'],'end':r['end']+unit['start'],'unit_id':unit['id']} for r in rows]
        all_words.extend(global_words);cues.extend(progressive_cues(global_words))
    return {**timing,'word_timings':all_words,'caption_cues':cues,'caption_style':'dialogue_bar',
        'caption_alignment':'Exact supplied dialogue forced-aligned with local faster-whisper; timings remain model estimates, not transcription replacements.'}
