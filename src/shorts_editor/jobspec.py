"""Bind a reusable layout to actual local media files for headless automation."""
import json
from pathlib import Path

from .models import COMPOSITION_IDS, ValidationError, template_project, validate_project


def materialize_job(job, store, base):
    if not isinstance(job, dict): raise ValidationError("Composition job must be an object.")
    base = Path(base).resolve()
    layout = job.get("template", "overlay")
    if isinstance(layout, str) and layout in COMPOSITION_IDS:
        p = template_project(layout)
    elif isinstance(layout, str):
        path = Path(layout)
        if not path.is_absolute(): path = base/path
        raw = json.loads(path.read_text(encoding="utf-8"))
        p = validate_project(raw.get("project",raw))
    elif isinstance(layout, dict):
        p = validate_project(layout)
    else: raise ValidationError("Template must be a preset name, a layout JSON path or an object.")
    if p["format"] not in COMPOSITION_IDS: raise ValidationError("Choose a media-slot composition template.")
    for key in ("name","resolution","fps","profile","music_volume","source_volume"):
        if key in job: p[key] = job[key]
    if "composition" in job:
        if not isinstance(job["composition"],dict): raise ValidationError("Composition settings must be an object.")
        p["composition"].update(job["composition"])
    imported = {}
    def media(value):
        if not isinstance(value,str) or not value: raise ValidationError("Input media needs a local file path.")
        if "://" in value: raise ValidationError("Use local input files; this command does not download videos.")
        path = Path(value)
        if not path.is_absolute(): path = base/path
        path = path.resolve()
        if not path.is_file(): raise ValidationError(f"Input file does not exist: {path.name}")
        if path not in imported: imported[path] = store.register(path)["id"]
        return imported[path]
    inputs = job.get("inputs",{})
    if not isinstance(inputs,dict): raise ValidationError("Inputs must be an object.")
    for key in ("music","narration"):
        p[key] = media(inputs[key]) if inputs.get(key) else ""
    if "shots" in job:
        rows = job["shots"]
        if not isinstance(rows,list) or not 1<=len(rows)<=30: raise ValidationError("Use one to thirty shots.")
    else: rows = [job]
    original = p["scenes"]
    scenes = []
    for i,row in enumerate(rows):
        if not isinstance(row,dict): raise ValidationError("Each shot must be an object.")
        if not isinstance(row.get("inputs",{}),dict): raise ValidationError("Shot inputs must be an object.")
        s = dict(original[min(i,len(original)-1)])
        shot_inputs = {**inputs,**row.get("inputs",{})}
        s["media"] = media(shot_inputs["background"]) if shot_inputs.get("background") else ""
        s["secondary_media"] = media(shot_inputs["foreground"]) if shot_inputs.get("foreground") else ""
        for key in ("duration","media_start","secondary_start","effect_at","source_audio","fit","focus_x","focus_y"):
            if key in row: s[key] = row[key]
        scenes.append(s)
    p["scenes"] = scenes
    p = validate_project(p)
    store.resolve_project_assets(p)
    from .composition import require_inputs
    require_inputs(p)
    return p
