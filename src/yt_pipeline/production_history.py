"""Safe readout of local production and YouTube upload state for a new editor session."""
import json
from pathlib import Path
import re

from .core import file_hash

QUEUE = Path(__file__).resolve().parents[2] / "docs" / "PRODUCTION_QUEUE.json"
FINISHED = ("ready", "processing", "uploaded_private", "scheduled", "published")


def verified_artifact(record):
    if record:
        path = Path(record["path"])
        if path.is_file() and file_hash(path) == record["sha256"]:
            return json.loads(path.read_text(encoding="utf-8"))
    return {}


def production_history(workspace, limit=8, channel=None):
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Choose a history limit between 1 and 100.")
    where = " WHERE jobs.channel=?" if channel else ""
    args = (channel,) if channel else ()
    with workspace.connect() as db:
        jobs = db.execute("SELECT * FROM jobs" + where + " ORDER BY created_at DESC", args).fetchall()
        uploads = {row["job_id"]: json.loads(row["data"]) for row in db.execute("SELECT * FROM uploads")}
    completed = []
    uploaded = []
    unresolved = []
    pending = []
    for job in jobs:
        request = json.loads(job["request"])
        artifacts = json.loads(job["artifacts"])
        package = artifacts.get("package")
        metadata = verified_artifact(package)
        series = request.get("series") or {}
        item = {
            "job_id": job["id"], "channel": job["channel"], "status": job["status"],
            "title": metadata.get("title") or request.get("topic"),
            "playbook": request.get("playbook"), "series_id": series.get("id"),
            "part": series.get("part"), "total_parts": series.get("total"),
            "production_key": request.get("production_key") or series.get("id"),
            "updated_at": job["updated_at"],
        }
        if metadata and job["status"] in FINISHED:
            visual_plan = verified_artifact(artifacts.get("script")).get("creative_plan") or {}
            shots = visual_plan.get("plan", {}).get("scenes", []) if request.get("playbook") == "comic_lore" else []
            completed.append({**item, "package": package["path"], "video": metadata.get("video"),
                              "description": metadata.get("description"),
                              "publication_ready": metadata.get("qa", {}).get("publication_ready"),
                              "scenes": {shot["unit_id"]:shot["kind"] for shot in shots} or request.get("lore_scenes"),
                              "cameras": {shot["unit_id"]:shot["framing"] for shot in shots} or request.get("lore_cameras"),
                              "top_assets": [row["asset_id"] for rows in (request.get("source_panels") or {}).values()
                                             for row in rows]})
        state = uploads.get(job["id"], {})
        video_id = state.get("video_id") or job["video_id"]
        if isinstance(video_id, str) and re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            uploaded.append({**item, "video_id": video_id, "url": f"https://youtu.be/{video_id}",
                             "upload_state": state.get("phase"), "checked_at": state.get("checked_at")})
        elif state:
            unresolved.append({**item, "upload_state": state.get("phase")})
        elif job["status"] in ("queued", "running", "retry_wait", "held", "failed"):
            pending.append({**item, "stage": job["stage"], "error_code": job["error_code"]})
    for rows in (completed, uploaded, unresolved, pending):
        rows.sort(key=lambda item: item["updated_at"], reverse=True)
    queue = json.loads(QUEUE.read_text(encoding="utf-8")) if QUEUE.is_file() else []

    def completed_idea(idea):
        made = [item for item in completed if item["production_key"] == idea["series_id"]]
        if not made:
            return False
        total = made[0]["total_parts"]
        if not total:
            return True
        return {item["part"] for item in made if item["total_parts"] == total} == set(range(1, total+1))

    next_idea = next((item for item in queue if (not channel or item["channel"] == channel)
                      and not completed_idea(item)), None)
    return {"latest_made": completed[:limit], "uploaded_through_app": uploaded[:limit],
            "upload_needs_reconciliation": unresolved[:limit], "recent_unfinished": pending[:limit],
            "next_to_make": next_idea,
            "scope": "Local workspace records. Studio/manual uploads and later visibility edits need separate verification."}
