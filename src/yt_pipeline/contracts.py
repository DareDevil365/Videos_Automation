import re
from .core import Held


SCRIPT_SCHEMA = {"type":"object", "properties":{
    "version":{"type":"integer"}, "title":{"type":"string"}, "description":{"type":"string"},
    "format":{"type":"string","enum":["chat","lesson","clip","aura","cutout"]}, "fiction":{"type":"boolean"},
    "hook":{"type":"string"}, "payoff":{"type":"string"},
    "units":{"type":"array","items":{"type":"object","properties":{
        "id":{"type":"string"},"speaker":{"type":"string"},"text":{"type":"string"},
        "kind":{"type":"string","enum":["fact","instruction","fiction","transition"]},
        "claim_ids":{"type":"array","items":{"type":"string"}},"onscreen":{"type":"string"},
        "visual_query":{"type":"string"},"visual_kind":{"type":"string","enum":["image","video"]}},
        "required":["id","speaker","text","kind","claim_ids","onscreen"],"additionalProperties":False}},
    "edit":{"type":"object","properties":{"effect":{"type":"string","enum":["none","punch","flash","shake"]},
             "payoff_unit_id":{"type":"string"},"cta":{"type":"boolean"}},
             "required":["effect","payoff_unit_id","cta"],"additionalProperties":False}},
    "required":["version","title","description","format","fiction","hook","payoff","units","edit"],"additionalProperties":False}


def string(value, name, maximum):
    if not isinstance(value,str) or not value.strip() or len(value)>maximum:
        raise Held("invalid_contract",f"{name} needs nonempty text of at most {maximum} characters.")
    return value.strip()


def brief_contract(value):
    if not isinstance(value,dict): raise Held("invalid_brief","Brief must be a JSON object.")
    title=string(value.get("title"),"Brief title",180)
    question=string(value.get("question"),"Viewer question",500)
    kind=value.get("kind","fact")
    if kind not in ("fact","fiction"): raise Held("invalid_brief","Brief kind must be fact or fiction.")
    sources=value.get("sources",[]);claims=value.get("claims",[])
    if not isinstance(sources,list) or len(sources)>20 or not isinstance(claims,list) or len(claims)>40:
        raise Held("invalid_brief","Brief source/claim list is invalid.")
    source_ids=set();checked_sources=[]
    for source in sources:
        if not isinstance(source,dict):raise Held("invalid_brief","Each source must be an object.")
        source_id=string(source.get("id"),"Source ID",60)
        if source_id in source_ids: raise Held("invalid_brief","Source IDs must be unique.")
        source_ids.add(source_id)
        url=string(source.get("url"),"Source URL",2000)
        if not url.startswith(("https://","http://")) and not re.fullmatch(r'asset://[a-f0-9]{32}',url): raise Held("invalid_brief","A source needs its actual web URL or registered recording asset ID.")
        checked_sources.append({"id":source_id,"url":url,"title":string(source.get("title"),"Source title",250),
                                "excerpt":string(source.get("excerpt"),"Evidence excerpt",18000),
                                "checked_at":string(source.get("checked_at"),"Evidence date",100)})
    claim_ids=set();checked_claims=[]
    for claim in claims:
        if not isinstance(claim,dict):raise Held("invalid_brief","Each claim must be an object.")
        claim_id=string(claim.get("id"),"Claim ID",60)
        if claim_id in claim_ids or claim.get("source_id") not in source_ids:
            raise Held("invalid_brief","Claim references are missing or duplicated.")
        claim_ids.add(claim_id)
        checked_claims.append({"id":claim_id,"text":string(claim.get("text"),"Claim",700),"source_id":claim["source_id"]})
    if kind=="fact" and not checked_sources: raise Held("missing_evidence","Factual briefs require actual source evidence.")
    return {"version":1,"title":title,"question":question,"kind":kind,"sources":checked_sources,"claims":checked_claims,
            "notes":str(value.get("notes",""))[:2500],"editorial_verified":value.get("editorial_verified") is True}


def script_contract(value, brief, expected_format=None):
    if not isinstance(value,dict): raise Held("invalid_script","Script must be a JSON object.")
    if set(value)-set(SCRIPT_SCHEMA["properties"]): raise Held("invalid_script","Script contains unsupported fields; no arbitrary code or tool paths are accepted.")
    if value.get("version")!=1: raise Held("invalid_script","Unsupported script version.")
    fmt=value.get("format")
    if fmt not in ("chat","lesson","clip","aura","cutout") or (expected_format and fmt!=expected_format):
        raise Held("invalid_script","Script format does not match the channel job.")
    fiction=value.get("fiction")
    if not isinstance(fiction,bool) or fiction!=(brief["kind"]=="fiction"):
        raise Held("invalid_script","Fiction/fact labels must match the brief.")
    rows=value.get("units")
    if not isinstance(rows,list) or not 1<=len(rows)<=28: raise Held("invalid_script","Use 1–28 spoken units.")
    ids=set();units=[];claim_ids={c["id"] for c in brief["claims"]}
    for row in rows:
        if not isinstance(row,dict): raise Held("invalid_script","Each spoken unit must be an object.")
        uid=string(row.get("id"),"Unit ID",50)
        if not re.fullmatch(r"[A-Za-z0-9_-]+",uid) or uid in ids: raise Held("invalid_script","Spoken-unit IDs must be safe and unique.")
        ids.add(uid)
        refs=row.get("claim_ids",[])
        if not isinstance(refs,list) or not all(isinstance(r,str) and r in claim_ids for r in refs):
            raise Held("unsupported_claim","Script refers to an unknown factual claim.")
        kind=row.get("kind")
        if kind not in ("fact","instruction","fiction","transition"): raise Held("invalid_script","Unknown spoken-unit kind.")
        if kind=="fact" and not refs: raise Held("unsupported_claim","Every factual unit needs an evidence claim reference.")
        if kind=="fiction" and not fiction: raise Held("invalid_script","Fictional dialogue must not be labelled factual.")
        units.append({"id":uid,"speaker":string(row.get("speaker","Narrator"),"Speaker",40),
                      "text":string(row.get("text"),"Spoken text",350),"kind":kind,"claim_ids":refs,
                      "onscreen":string(row.get("onscreen",row.get("text")),"Onscreen text",220),
                      "visual_query":str(row.get('visual_query',''))[:160],
                      "visual_kind":row.get('visual_kind') if row.get('visual_kind') in ('image','video') else 'image'})
    edit=value.get("edit",{})
    if not isinstance(edit,dict) or edit.get("effect") not in ("none","punch","flash","shake") or edit.get("payoff_unit_id") not in ids or not isinstance(edit.get("cta"),bool):
        raise Held("invalid_script","Edit intent must refer to an existing payoff unit and supported effect.")
    return {"version":1,"title":string(value.get("title"),"Video title",100),
            "description":string(value.get("description"),"Description",2500),"format":fmt,"fiction":fiction,
            "hook":string(value.get("hook"),"Hook",350),"payoff":string(value.get("payoff"),"Payoff",350),
            "units":units,"edit":{"effect":edit["effect"],"payoff_unit_id":edit["payoff_unit_id"],"cta":edit["cta"]}}
