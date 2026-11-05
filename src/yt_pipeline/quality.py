from array import array
import json
from pathlib import Path
import subprocess

from shorts_editor.store import probe, write_json
from .assets import asset_record
from .core import Held, file_hash, digest, now
from .research import source_freshness


def inspect_render(workspace, job, brief, written, timing, directed, rendered):
    output=Path(rendered["video"])
    info=probe(output)
    video=next(s for s in info["streams"] if s["codec_type"]=="video")
    expected=json.loads(Path(directed["project"]).read_text(encoding="utf-8"))
    from shorts_editor.models import dimensions
    size=dimensions(expected)
    if (video["width"],video["height"])!=size:raise Held("qa_dimensions","Output size does not match its edit recipe.")
    duration=float(info["format"]["duration"])
    if abs(duration-timing["duration"])>.20:raise Held("qa_timing","The finished video does not match measured narration timing.")
    if not any(s["codec_type"]=="audio" for s in info["streams"]):raise Held("qa_audio","The render contains no audio stream.")
    decoded=subprocess.run(["ffmpeg","-v","error","-i",str(output),"-vn","-ac","1","-ar","16000","-f","s16le","-"],capture_output=True,timeout=90)
    if decoded.returncode:raise Held("qa_decode","The final audio could not be decoded.")
    samples=array("h");samples.frombytes(decoded.stdout)
    if not samples or max(abs(x) for x in samples)<100:raise Held("qa_silent","The exported audio is empty or effectively silent.")
    clips=sum(abs(x)>=32760 for x in samples)/len(samples)
    if clips>.001:raise Held("qa_clipping","Final audio contains excessive clipped samples.")
    checked=subprocess.run(["ffmpeg","-v","error","-i",str(output),"-an","-f","null","-"],capture_output=True,timeout=120)
    if checked.returncode:raise Held("qa_decode","The final video could not be fully decoded.")
    stale=source_freshness(brief,int(job["request"].get("max_source_age_days",30)))
    if stale:raise Held("stale_sources"," ".join(stale))
    if not written["review"].get("supported"):raise Held("editorial_review","The script has not passed its evidence review.")
    assets=[asset_record(workspace,a["id"]) for a in directed["provenance"]]
    test_only=bool(job["request"].get("test_only")) or any(a.get("test_only") for a in assets)
    full_text=" ".join(unit["text"] for unit in written["script"]["units"]).lower()
    flags=[]
    if any(term in full_text for term in ("guaranteed income","guaranteed job","risk-free profit","earn $1000 a day")):
        flags.append("Potentially deceptive outcome claim requires review.")
    if flags:raise Held("editorial_claim"," ".join(flags))
    visual_reports=[rendered.get(k,{}) for k in ('visual_review','asset_review')]
    visual_unresolved=any(r.get('status') in ('fail','unknown','needs_review') for r in visual_reports)
    report={"version":1,"checked_at":now(),"technical_pass":True,"editorial_review":written["review"],
            "visual_review":rendered.get('visual_review',{'status':'not_requested'}),
            "asset_review":rendered.get('asset_review',{'status':'not_requested'}),
            "publication_ready":not test_only and not visual_unresolved,"test_only":test_only,"duration":duration,"width":video["width"],"height":video["height"],
            "audio":{"clipped_fraction":clips,"decoded_samples":len(samples)},"video_sha256":file_hash(output),
            "source_conditions_recorded":True,"notes":["Recorded evidence and automated checks are not a legal/YPP certification.",
                 "No speech word alignment or subjective naturalness claim is inferred from technical checks."]}
    if rendered.get('chat_editing'):
        report['chat_editing']=rendered['chat_editing']
    write_json(workspace.job_dir(job['id'])/'qa.json',report)
    return report


def package(workspace, job, brief, written, timing, directed, rendered, qa,provider=None):
    script=written["script"]
    strategy=None
    if job['request'].get('metadata_version')==2:
        from .publication_metadata import make_metadata,validate_metadata
        supplied=job['request'].get('publication_metadata')
        strategy=validate_metadata(supplied,script) if supplied is not None else make_metadata(provider,script,job['request'])
        if supplied is not None:strategy['origin']='provided_content_packaging_v1'
    description=(strategy['description'] if strategy else script["description"]).strip()
    if script["fiction"]:description+="\n\nOriginal fictional entertainment/edit captions; not a real conversation, creator quote or endorsement."
    series=job['request'].get('series')
    if series:
        if (not isinstance(series,dict) or type(series.get('part')) is not int or type(series.get('total')) is not int
                or not 1<=series['part']<=series['total']<=12 or series.get('next_part')!=(series['part']+1 if series['part']<series['total'] else None)):
            raise Held('series_contract','Series metadata needs sequential real parts and a concluding final part.')
        description+=f"\n\nPart {series['part']} of {series['total']}. "+str(series.get('canon',''))
    if brief["sources"]:
        description+="\n\nSources checked:\n"+"\n".join(source["url"] for source in brief["sources"])
    credits=list(dict.fromkeys(asset["attribution"] for asset in directed["provenance"] if asset.get("attribution")))
    if credits:description+="\n\n"+"\n".join(credits)
    if len(description.encode('utf-8'))>5000:raise Held('metadata_description','Description and required credits exceed 5000 UTF-8 bytes; shorten the premise without cutting credits.')
    metadata={"version":1,"channel_profile":job["channel"],"title":strategy['title'] if strategy else script["title"],"description":description,
              "category_id":"27" if job["channel"]=="education" else "23", "made_for_kids":False,
              "contains_synthetic_media":timing.get("source")!="original_clip" or script["fiction"] or any(a.get('evidence',{}).get('synthetic') for a in directed['provenance']),"disclosure":{"decision":"Conservative disclosure for synthesized narration or fictional presentation; original-source clip route retains source audio.",
                  "voice":timing["voice"],"fiction":script["fiction"],"impersonation":False},
              "video":rendered["video"],"cover":rendered["cover"],"captions":rendered["captions"],
              "qa":qa,"source_urls":[s["url"] for s in brief["sources"]],"attribution":credits,
              "publication_mode":job['request'].get('publish_visibility','disabled'),"created_at":now(),
              'packaging_strategy':strategy,'series':series}
    hook=written.get('hook_options') or {}
    plan=(written.get('creative_plan') or {}).get('plan',{})
    question=plan.get('comment_question','')
    metadata['creative_experiment']={'playbook':job['request'].get('playbook'),
        'hook_type':hook.get('selected',{}).get('type') if hook.get('active') else None,
        'hook_options_recorded':bool(hook),'hook_selection_active':hook.get('active',False),
        'first_frame_intent':hook.get('selected',{}).get('first_frame') if hook.get('active') else None,
        'editorial_review':'passed' if written.get('editorial_review') else 'not_requested',
        'spoken_comment_question':question if question and question in script['units'][-1]['text'] else None,
        'limits':'Experiment descriptors, not measured engagement or an instruction to post comments.'}
    metadata["approval_fingerprint"]=digest([qa["video_sha256"],metadata["title"],metadata["description"],job["channel"],metadata["contains_synthetic_media"]])
    write_json(workspace.job_dir(job["id"])/"metadata.json",metadata)
    return metadata
