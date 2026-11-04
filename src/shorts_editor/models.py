from copy import deepcopy
import math
import re

LEGACY_FORMATS = [
    {"id": "story", "name": "Story + gameplay", "tag": "Narrative", "description": "A clear story over a moving background.", "icon": "story"},
    {"id": "split", "name": "Split screen", "tag": "Clips", "description": "Two media panels, one hook, timed captions.", "icon": "split"},
    {"id": "chat", "name": "Chat story", "tag": "Dialogue", "description": "Messages appear one by one. Finish with a comeback.", "icon": "chat"},
    {"id": "list", "name": "Movie / list cards", "tag": "Collections", "description": "A series of picks with a reason for each.", "icon": "list"},
    {"id": "explainer", "name": "Educational cards", "tag": "Ideas", "description": "A headline, a visual, and one useful takeaway.", "icon": "explainer"},
    {"id": "punchline", "name": "Punchline edit", "tag": "Moments", "description": "Full-screen footage with a timed reveal.", "icon": "punchline"},
]
COMPOSITION_FORMATS = [
    {"id":"overlay", "name":"Chat over footage", "tag":"Composition", "description":"A supplied screenshot or chat clip over full-frame footage.", "icon":"overlay", "slots":2},
    {"id":"stack", "name":"Two blocks", "tag":"Composition", "description":"Two supplied clips in bordered top and bottom blocks.", "icon":"stack", "slots":2},
    {"id":"focus", "name":"Clip on blurred fill", "tag":"Composition", "description":"Preserve a wide clip with a blurred copy filling the canvas.", "icon":"focus", "slots":1},
]
COMPOSITION_IDS = {f["id"] for f in COMPOSITION_FORMATS}
FORMATS = COMPOSITION_FORMATS + LEGACY_FORMATS
FORMAT_IDS = {f["id"] for f in FORMATS}


class ValidationError(ValueError):
    pass


def number(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValidationError(f"{name} must be a finite number.")
    if not low <= value <= high:
        raise ValidationError(f"{name} must be between {low} and {high}.")
    return float(value)


def text(value, name, limit):
    if not isinstance(value, str) or len(value) > limit:
        raise ValidationError(f"{name} must be text of at most {limit} characters.")
    if any(ord(c) < 32 and c not in "\n\t" for c in value):
        raise ValidationError(f"{name} contains an unsupported control character.")
    return value


def asset_ref(value, name):
    value = text(value, name, 80)
    if value and not re.fullmatch(r"[a-zA-Z0-9_-]+", value):
        raise ValidationError(f"{name} must refer to an imported asset, not a path or URL.")
    return value


def new_scene(index=0):
    return {"title": "Your next idea", "text": "Add a clear setup and a satisfying payoff.",
            "duration": 4, "media": "", "secondary_media": "", "media_start": 0,
            "secondary_start": 0, "fit": "cover", "focus_x": 0.5, "focus_y": 0.5,
            "source_audio": False, "messages": [{"name": "Alex", "text": "Wait. What happened?", "side": "left"},
                                                 {"name": "Sam", "text": "That's the interesting part.", "side": "right"}]}


def new_project(format_id="story"):
    return {"version": 1, "name": "Untitled video", "format": format_id,
            "resolution": "720p", "fps": 30, "profile": "short", "accent": "#b5f36c", "background": "#101516",
            "split_ratio": 0.5, "swap_panels": False, "font_scale": 1,
            "narration": "", "music": "", "music_volume": 0.12, "source_volume": 1,
            "composition": {"x":.10,"y":.12,"width":.80,"height":.44,"foreground_fit":"contain",
                            "border_width":0,"border_color":"#ffffff","glow":0,
                            "effect":"none","effect_duration":.45,"cta":False,"cta_text":"LIKE + SUBSCRIBE",
                            "cta_at":5,"cta_duration":2,"audio_source":"foreground"},
            "scenes": [new_scene()]}


def validate_project(data):
    if not isinstance(data, dict):
        raise ValidationError("Project must be a JSON object.")
    if data.get("version", 1) != 1:
        raise ValidationError("Only project version 1 is supported.")
    p = new_project()
    p.update({k: deepcopy(v) for k, v in data.items() if k in p})
    p["name"] = text(p["name"], "Project name", 120)
    if p["format"] not in FORMAT_IDS:
        raise ValidationError("Choose a supported format.")
    if p['profile'] not in ('short','documentary'):
        raise ValidationError('Choose short or documentary profile.')
    if p['profile']=='documentary' and p['format']!='focus':
        raise ValidationError('Documentary profile requires the full-frame focus composition.')
    if p["resolution"] not in ("720p", "1080p") or p["fps"] not in (24, 30):
        raise ValidationError("Choose 720p or 1080p, at 24 or 30 fps.")
    for key in ("accent", "background"):
        if not isinstance(p[key], str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", p[key]):
            raise ValidationError(f"{key} must be a six-digit hex color.")
    for key in ("swap_panels",):
        if not isinstance(p[key], bool):
            raise ValidationError(f"{key} must be true or false.")
    for key, low, high in (("split_ratio", .25, .75), ("font_scale", .7, 1.4),
                           ("music_volume", 0, 1), ("source_volume", 0, 2)):
        p[key] = number(p[key], key, low, high)
    for key in ("music", "narration"):
        p[key] = asset_ref(p[key], key)
    defaults = new_project()["composition"]
    if not isinstance(p["composition"], dict): raise ValidationError("Composition must be an object.")
    c = {**defaults, **{k:v for k,v in p["composition"].items() if k in defaults}}
    for key,low,high in (("x",0,.95),("y",0,.95),("width",.1,1),("height",.1,1),
                         ("border_width",0,16),("glow",0,30),("effect_duration",.15,2),
                         ("cta_at",0,180),("cta_duration",.5,6)):
        c[key] = number(c[key],key,low,high)
    if c["x"]+c["width"]>1.001 or c["y"]+c["height"]>1.001:
        raise ValidationError("The foreground box must stay inside the canvas.")
    if c["foreground_fit"] not in ("contain","cover"): raise ValidationError("Choose contain or cover for the foreground.")
    if c["effect"] not in ("none","punch","flash","shake"): raise ValidationError("Unsupported effect.")
    if c["audio_source"] not in ("none","background","foreground"): raise ValidationError("Choose which clip supplies audio.")
    if not isinstance(c["cta"],bool): raise ValidationError("CTA must be true or false.")
    c["cta_text"] = text(c["cta_text"],"CTA text",60)
    if not isinstance(c["border_color"],str) or not re.fullmatch(r"#[0-9a-fA-F]{6}",c["border_color"]):
        raise ValidationError("Border color must be a six-digit hex color.")
    p["composition"] = c
    if not isinstance(p["scenes"], list) or not 1 <= len(p["scenes"]) <= 30:
        raise ValidationError("Use between 1 and 30 scenes.")
    scenes = []
    for i, item in enumerate(p["scenes"]):
        if not isinstance(item, dict):
            raise ValidationError(f"Scene {i+1} must be an object.")
        s = new_scene(i)
        s.update({k: deepcopy(v) for k, v in item.items() if k in s})
        for key, limit in (("title", 180), ("text", 700)):
            s[key] = text(s[key], f"Scene {i+1} {key}", limit)
        if p["format"] in ("story", "split") and len([line for line in s["text"].splitlines() if line.strip()]) > 12:
            raise ValidationError("Use at most twelve caption cues per scene. Add another scene for more text.")
        for key in ("media", "secondary_media"):
            s[key] = asset_ref(s[key], key)
        s.setdefault("effect_at",max(0,float(s["duration"])*.75) if isinstance(s["duration"],(int,float)) else 0)
        s["effect_at"] = number(item.get("effect_at",s["effect_at"]),"Effect time",0,180)
        for key, low, high in (("duration", 1, 180 if p["format"] in COMPOSITION_IDS else 60), ("media_start", 0, 86400),
                               ("secondary_start", 0, 86400), ("focus_x", 0, 1), ("focus_y", 0, 1)):
            s[key] = number(s[key], key, low, high)
        if s["fit"] not in ("cover", "contain"):
            raise ValidationError("Media fit must be cover or contain.")
        if not isinstance(s["source_audio"], bool):
            raise ValidationError("Source audio must be true or false.")
        if not isinstance(s["messages"], list) or len(s["messages"]) > 8:
            raise ValidationError("Use at most eight messages per scene.")
        messages = []
        for msg in s["messages"]:
            if not isinstance(msg, dict) or msg.get("side", "left") not in ("left", "right"):
                raise ValidationError("Each message needs text, a name and a left/right side.")
            messages.append({"name": text(msg.get("name", ""), "Message name", 35),
                             "text": text(msg.get("text", ""), "Message", 180),
                             "side": msg.get("side", "left")})
        s["messages"] = messages
        scenes.append(s)
    if sum(s["duration"] for s in scenes) > 180:
        raise ValidationError("This Shorts editor supports projects up to 180 seconds.")
    p["scenes"] = scenes
    return p


def dimensions(project):
    if project.get('profile','short')=='documentary':
        return (1920,1080) if project['resolution']=='1080p' else (1280,720)
    return (1080, 1920) if project["resolution"] == "1080p" else (720, 1280)


def duration(project):
    return sum(s["duration"] for s in project["scenes"])


def template_project(format_id, demo_assets=None):
    if format_id not in FORMAT_IDS:
        raise ValidationError("Choose a supported format.")
    p = new_project(format_id)
    p["name"] = next(f["name"] for f in FORMATS if f["id"] == format_id)
    if format_id in COMPOSITION_IDS:
        s = new_scene()
        s.update(title="",text="",messages=[],duration=8,effect_at=5,source_audio=True)
        p.update(scenes=[s],background="#000000",accent="#ffffff")
        if format_id=="stack": p["composition"].update(x=0,y=0,width=1,height=.5,border_width=3,foreground_fit="cover")
        if format_id=="focus": p["composition"].update(x=.04,y=.30,width=.92,height=.38,audio_source="background")
        return validate_project(p)
    demo_assets = demo_assets or {}
    a = demo_assets.get("art", [])
    motion = demo_assets.get("motion", "")
    def scene(title, caption, index=0, seconds=4):
        s = new_scene(index)
        s.update(title=title, text=caption, duration=seconds, media=a[index % len(a)] if a else "",
                 secondary_media=motion)
        return s
    if format_id == "story":
        p["scenes"] = [scene("THE GROUP CHAT", "The printer was accidentally invited to lunch.", 0),
                       scene("ONE NEW MESSAGE", 'Its only reply? “Out of office.”', 1)]
        for s in p["scenes"]: s["media"] = motion
    elif format_id == "split":
        p["scenes"] = [scene("ONE MOMENT. TWO ANGLES.", "Drop a clip above and gameplay below.", 0, 6)]
    elif format_id == "chat":
        p["scenes"] = [scene("THE PERFECT REPLY", "A fictional chat", 0, 8)]
        p["scenes"][0]["messages"] = [{"name":"Alex", "text":"You can't come without a car.", "side":"left"},
                                              {"name":"Sam", "text":"I'm already here.", "side":"right"},
                                              {"name":"Alex", "text":"How?", "side":"left"},
                                              {"name":"Sam", "text":"I live upstairs.", "side":"right"}]
    elif format_id == "list":
        titles = ["A world worth exploring", "A mystery in one room", "One impossible choice", "A quieter kind of adventure",
                  "The unexpected friendship", "A different tomorrow", "A very strange journey", "The final clue", "A beautiful detour"]
        p["scenes"] = [scene(f"{i+1:02d} / YOUR WATCHLIST", title, i, 3) for i,title in enumerate(titles)]
        p["scenes"].append(scene("YOU PICK NUMBER 10", "What belongs on this list?", 0, 3))
    elif format_id == "explainer":
        p["scenes"] = [scene("ONE USEFUL IDEA", "Turn a big goal into one visible next action.", 0),
                       scene("MAKE IT CONCRETE", 'Instead of “finish project,” try “open the draft.”', 1)]
    else:
        p["scenes"] = [scene("HE PREPARED THE PERFECT COMEBACK", "Nobody was arguing.", 2, 5)]
    if format_id in ("list", "explainer"):
        for s in p["scenes"]: s["fit"] = "contain"
    return validate_project(p)
