import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import uuid

from PIL import Image

from .models import ValidationError, validate_project

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
MEDIA_EXT = IMAGE_EXT | {".gif", ".mp4", ".mov", ".mkv", ".webm", ".avi", ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus"}
IDENTIFIER = re.compile(r"^[a-zA-Z0-9_-]{1,80}$")


def checked_id(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValidationError("Invalid record identifier.")
    return value


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def probe(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    if result.returncode:
        raise ValidationError("This file could not be read as media. Try another export.")
    return json.loads(result.stdout)


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.lock = threading.RLock()
        for folder in ("assets", "projects", "previews", "jobs"):
            (self.root / folder).mkdir(parents=True, exist_ok=True)

    def asset(self, asset_id):
        asset_id = checked_id(asset_id)
        meta_path = self.root / "assets" / (asset_id + ".json")
        if not meta_path.is_file():
            raise ValidationError(f"Asset {asset_id} is missing. Import its media first.")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        path = (self.root / "assets" / meta["file"]).resolve()
        if path.parent != (self.root / "assets").resolve() or not path.is_file():
            raise ValidationError("Imported media is missing or outside its asset directory.")
        return {**meta, "path": path}

    def list_assets(self):
        items = []
        for path in sorted((self.root / "assets").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            item = json.loads(path.read_text(encoding="utf-8"))
            items.append(item)
        return items

    def register(self, path, name=None, asset_id=None, demo=False):
        path = Path(path)
        suffix = path.suffix.lower()
        if suffix not in MEDIA_EXT:
            raise ValidationError("Import an image, video, GIF, or audio file.")
        asset_id = checked_id(asset_id or uuid.uuid4().hex)
        target = self.root / "assets" / (asset_id + suffix)
        if suffix in IMAGE_EXT:
            with Image.open(path) as img:
                img.verify()
            with Image.open(path) as img:
                width, height = img.size
            kind, seconds, has_audio = "image", 0, False
        else:
            info = probe(path)
            video = next((s for s in info.get("streams", []) if s["codec_type"] == "video" and not s.get("disposition", {}).get("attached_pic")), None)
            has_audio = any(s["codec_type"] == "audio" for s in info.get("streams", []))
            if not video and not has_audio:
                raise ValidationError("No usable video or audio stream was found.")
            kind = "video" if video else "audio"
            width, height = (video.get("width", 0), video.get("height", 0)) if video else (0, 0)
            seconds = float(info.get("format", {}).get("duration") or (video or {}).get("duration") or 0)
            if not seconds > 0:
                raise ValidationError("Media duration could not be determined.")
        if width * height > 100_000_000:
            raise ValidationError("Image or video dimensions are too large.")
        if path.resolve() != target.resolve():
            shutil.copyfile(path, target)
        meta = {"id": asset_id, "name": (name or path.name)[:200], "file": target.name,
                "kind": kind, "duration": seconds, "width": width, "height": height,
                "has_audio": has_audio, "demo": demo}
        write_json(self.root / "assets" / (asset_id + ".json"), meta)
        return meta

    def resolve_project_assets(self, project):
        ids = {s[k] for s in project["scenes"] for k in ("media", "secondary_media") if s[k]}
        ids.update(project[k] for k in ("narration", "music") if project[k])
        result = {asset_id: self.asset(asset_id) for asset_id in ids}
        for scene in project["scenes"]:
            for key, offset_key in (("media", "media_start"), ("secondary_media", "secondary_start")):
                if not scene[key]: continue
                asset = result[scene[key]]
                if asset["kind"] == "audio":
                    raise ValidationError("Choose an image or video for a visual panel.")
                if asset["kind"] == "video" and scene[offset_key] >= asset["duration"]:
                    raise ValidationError(f"Start time must be shorter than {asset['name']}'s {asset['duration']:.1f}s duration.")
        for key in ("narration", "music"):
            if project[key] and not result[project[key]]["has_audio"]:
                raise ValidationError(f"Choose a file with audio for {key}.")
        return result

    def save_project(self, data, project_id=None):
        p = validate_project(data)
        project_id = checked_id(project_id or uuid.uuid4().hex)
        with self.lock:
            write_json(self.root / "projects" / (project_id + ".json"), {"id": project_id, "project": p})
        return {"id": project_id, "project": p}

    def project(self, project_id):
        path = self.root / "projects" / (checked_id(project_id) + ".json")
        if not path.is_file(): raise ValidationError("Saved project not found.")
        return json.loads(path.read_text(encoding="utf-8"))

    def list_projects(self):
        return [{"id": p.stem, "name": json.loads(p.read_text(encoding="utf-8"))["project"]["name"]}
                for p in sorted((self.root / "projects").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)]
