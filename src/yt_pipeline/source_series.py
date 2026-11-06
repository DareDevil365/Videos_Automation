"""Source-aware multipart plans executed by the existing durable batch runner."""
import json
from pathlib import Path
import re

from shorts_editor.store import write_json
from .contracts import brief_contract,script_contract
from .core import Held,file_hash,now
from .playbooks import validate_playbook_script
from .lore_voices import choose_series_voices


def create_series_plan(workspace,series_file,brief_file,output_file,source_review=None,*,build_id=None,revise_batch=None,
                       assistant_authored=False):
    series_file=Path(series_file).resolve();brief_file=Path(brief_file).resolve();output_file=Path(output_file).resolve()
    if output_file.exists():raise Held('series_exists','Choose a new plan filename; initialized series plans are immutable.')
    series=json.loads(series_file.read_text(encoding='utf-8'));brief=brief_contract(json.loads(brief_file.read_text(encoding='utf-8')))
    identifier=series.get('series_id','');parts=series.get('parts',[])
    structure = series.get('structure','serial_cliffhanger')
    if structure not in ('serial_cliffhanger','chapter_answers'):
        raise Held('series_contract','Choose serialized cliffhangers or chapters with individual answers.')
    if not isinstance(identifier,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',identifier):raise Held('series_contract','A series needs a safe unique ID.')
    if not isinstance(parts,list) or not 1<=len(parts)<=12 or not all(isinstance(p,dict) for p in parts) or [p.get('part') for p in parts]!=list(range(1,len(parts)+1)):raise Held('series_contract','Use one to twelve sequential parts, starting at one.')
    if brief['kind']!='fact':raise Held('series_evidence','Comic recaps need factual evidence about the chosen canon.')
    if assistant_authored and not source_review:
        raise Held('series_evidence','Assistant-authored production requires an exact source review and a supplied script for every part.')
    review=None
    if source_review:
        review=json.loads(Path(source_review).read_text(encoding='utf-8'))
        if (not isinstance(review,dict) or review.get('brief_sha256')!=file_hash(brief_file) or review.get('supported') is not True
                or not isinstance(review.get('reviewer'),str) or not review['reviewer'].strip() or not review.get('limitations')
                or not isinstance(review.get('script_sha256'),dict) or any(not p.get('script') for p in parts)):
            raise Held('series_evidence','Source review must bind this exact brief and record reviewer, outcome and limitations.')
        brief['editorial_verified']=True
        brief['notes']+='\nProvided source review: '+review['reviewer']+'. Limitations: '+str(review['limitations'])
    from .curated_music import select_genre_music
    music=select_genre_music(workspace,'mystery',selection_key=identifier)
    build_id=build_id or identifier
    if not isinstance(build_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',build_id):raise Held('series_contract','Use a safe build ID.')
    ancestors={}
    if revise_batch:
        previous=json.loads(Path(revise_batch).read_text(encoding='utf-8'))
        if previous.get('id')==build_id:raise Held('series_contract','A revision needs a distinct build ID and output folder.')
        for item in previous.get('items',[]):
            if item.get('job_id'):
                old=workspace.get(item['job_id'])
                if old['request'].get('series',{}).get('id')!=identifier or old['request'].get('test_only') is not True:
                    raise Held('series_contract','Revision ancestors must be test-only jobs from this same series.')
                ancestors[item['id']]=old['id']
    items=[]
    voices=choose_series_voices(workspace,identifier,series.get('source_voices'))
    for index,part in enumerate(parts):
        if part.get('next_part')!=(index+2 if index+1<len(parts) else None):raise Held('series_contract','Each part must lead to the actual next part; the final part concludes.')
        if part.get('publication_url'):raise Held('series_contract','New local series plans do not invent or import publication links.')
        request={'playbook':'comic_lore','fiction':False,'test_only':True,'auto_publish':False,'brief':brief,
            'hook_options':False,'editorial_review':'off','visual_review':'off','bottom_kind':'none','require_music':True,
            'music_id':music['id'],'motion_graphics':True,'source_voices':voices,
            'visual_selection':{'mode':'auto'},
            'series':{'id':identifier,'structure':structure,'part':part['part'],'total':len(parts),'next_part':part.get('next_part'),'canon':str(series.get('canon',''))[:240]},
            'source_review':review,'creative_brief':('Build one continuing story. End earlier parts on a concrete cliffhanger and conclude the arc in the final part. ' if structure == 'serial_cliffhanger' else 'Deliver the chapter answer before its next-part lead. ')+'Preserve the supplied canon/source distinction.'}
        for key in ('lore_scenes','lore_cameras','lore_actions','source_panels','reaction_preset','source_delivery',
                    'source_cues','source_music','music_id','thunder_cast','pact_cast','hellboy_media','visual_selection','character_cutouts','source_duration','lore_design','reaction_set'):
            if key in part:
                request[key]=part[key]
        if assistant_authored:
            request['lore_fresh_visuals']=True
        if f'part-{index+1}' in ancestors:request['prototype_revision_of']=ancestors[f'part-{index+1}']
        if part.get('script'):
            if not isinstance(part['script'],str):raise Held('series_contract','Script paths must be filenames within the series folder.')
            path=(series_file.parent/part['script']).resolve()
            if not path.is_file() or not path.is_relative_to(series_file.parent):raise Held('series_contract','Each script must be a real file within this series folder.')
            script=script_contract(json.loads(path.read_text(encoding='utf-8')),brief,'lesson')
            if review and review.get('script_sha256',{}).get(part['script'])!=file_hash(path):
                raise Held('series_evidence','Source review must bind each exact supplied script; revised words need a new review record.')
            validate_playbook_script(script,'comic_lore',request);request['script']=script;topic=script['title']
            from .lore_visuals import plan_lore
            from .lore_actions import resolve_actions
            plan_lore(script,request,brief)
            resolve_actions(request,script)
            if 'publication_metadata' in part:
                from .publication_metadata import validate_metadata
                validate_metadata(part['publication_metadata'],script)
                request.update(metadata_version=2,publication_metadata=part['publication_metadata'])
        else:
            topic=part.get('topic','')
            if not isinstance(topic,str) or not 1<=len(topic)<=180:raise Held('series_contract','Each part needs its supplied script or a specific writing topic.')
        items.append({'id':f'part-{index+1}','kind':'playbook','playbook':'comic_lore','channel':'entertainment','topic':topic,'request':request})
    plan={'version':1,'id':build_id,'created_at':now(),'output_root':str(output_file.parent.parent/'Productions'),
        'note':'Source-linked original comic recap series. Local review previews with actual next-part relations and the supplied story structure.',
        'series_file_sha256':file_hash(series_file),'brief_file_sha256':file_hash(brief_file),'items':items}
    output_file.parent.mkdir(parents=True,exist_ok=True);write_json(output_file,plan)
    return {'plan':str(output_file),'id':build_id,'parts':len(items),'source_review':'provided' if review else 'model evidence review required',
        'creative_origin':'assistant_supplied' if assistant_authored else 'standard',
        'next':'batch-run --plan '+str(output_file)}
