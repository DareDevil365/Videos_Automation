"""Real media integration tests; FFmpeg is required for this project."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from PIL import Image
import pytest

from shorts_editor.demo import create_demo
from shorts_editor.models import LEGACY_FORMATS, ValidationError, template_project, validate_project, duration
from shorts_editor.render import RenderCancelled, preview, render_project
from shorts_editor.server import Jobs, make_server
from shorts_editor.store import Store, probe, write_json


@pytest.fixture(scope="module")
def media(tmp_path_factory):
    store = Store(tmp_path_factory.mktemp("editor"))
    return store, create_demo(store)


@pytest.mark.parametrize("format_id", [f["id"] for f in LEGACY_FORMATS])
def test_each_format_exports_playable_media_and_companions(media, tmp_path, format_id):
    store, demo = media
    project = template_project(format_id, demo)
    output = tmp_path / (format_id + ".mp4")
    manifest = render_project(project, store, output)
    info = probe(output)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    assert (video["width"], video["height"], video["codec_name"]) == (720, 1280, "h264")
    assert any(s["codec_type"] == "audio" for s in info["streams"])
    assert abs(float(info["format"]["duration"]) - duration(project)) < .25
    assert manifest["audio"]
    assert output.with_suffix(".srt").read_text(encoding="utf-8").count(" --> ") >= len(project["scenes"])
    assert json.loads(output.with_suffix(".project.json").read_text(encoding="utf-8")) == project
    with Image.open(output.with_suffix(".png")) as cover:
        assert cover.size == (720, 1280)
    # Decode the entire MP4, rather than trusting headers alone.
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"], check=True, capture_output=True)
    with pytest.raises(ValidationError, match="already exists"):
        render_project(project, store, output)


def test_preview_changes_with_chat_reveal_and_is_cached(media):
    store, demo = media
    project = template_project("chat", demo)
    early = preview(project, store, at=.1)
    late = preview(project, store, at=7.9)
    assert early.read_bytes() != late.read_bytes()
    assert preview(project, store, at=.1) == early
    with Image.open(late) as frame:
        assert frame.size == (360, 640)


def test_1080p_audio_offsets_contain_and_panel_swap(media, tmp_path):
    store, demo = media
    clip = tmp_path / "clip with sound.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(store.asset(demo["motion"])["path"]),
                    "-i", str(store.asset(demo["music"])["path"]), "-map", "0:v", "-map", "1:a",
                    "-t", "3", "-c:v", "copy", "-c:a", "aac", str(clip)], check=True)
    source = store.register(clip)
    voice = tmp_path / "voice.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(store.asset(demo["music"])["path"]),
                    "-t", "1", str(voice)], check=True)
    narration = store.register(voice)
    project = template_project("split", demo)
    project.update(resolution="1080p", fps=24, swap_panels=True, split_ratio=.35,
                   music=demo["music"], narration=narration["id"])
    project["scenes"][0].update(media=source["id"], media_start=.5, secondary_start=.7,
                                  fit="contain", source_audio=True, duration=2)
    output = tmp_path / "mixed.mp4"
    render_project(project, store, output)
    info = probe(output)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    assert (video["width"], video["height"], video["r_frame_rate"]) == (1080, 1920, "24/1")
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(output), "-vn", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    assert len(set(pcm)) > 100  # Mixed output contains an actual audible signal.
    project["narration"] = demo["music"]
    with pytest.raises(ValidationError, match="Narration is longer"):
        render_project(project, store, tmp_path / "too-short.mp4")


def test_rejects_unsafe_asset_paths_invalid_offsets_and_unbounded_work(media):
    store, demo = media
    project = template_project("story", demo)
    project["scenes"][0]["media"] = "../outside.mp4"
    with pytest.raises(ValidationError, match="not a path"):
        validate_project(project)
    project = template_project("story", demo)
    project["scenes"][0]["media_start"] = 999
    with pytest.raises(ValidationError, match="Start time"):
        store.resolve_project_assets(project)
    project["scenes"] = [deepcopy(project["scenes"][0]) for _ in range(30)]
    for scene in project["scenes"]: scene["duration"] = 60
    with pytest.raises(ValidationError, match="180 seconds"):
        validate_project(project)


def test_cancellation_and_restart_preserve_truthful_job_state(media, tmp_path):
    store, demo = media
    cancelled = threading.Event(); cancelled.set()
    output = tmp_path / "cancelled.mp4"
    with pytest.raises(RenderCancelled):
        render_project(template_project("story", demo), store, output, cancel=cancelled)
    assert not output.exists()
    isolated = Store(tmp_path / "restart")
    record = {"id": "a" * 32, "status": "running", "created_at": "2026-11-01T00:00:00Z"}
    write_json(isolated.root / "jobs" / record["id"] / "job.json", record)
    jobs = Jobs(isolated)
    try:
        assert jobs.get(record["id"])["status"] == "interrupted"
    finally:
        jobs.close()


def test_local_http_save_preview_export_range_and_request_isolation(media, tmp_path):
    store, demo = media
    server = make_server(store, 0)
    worker = threading.Thread(target=server.serve_forever, daemon=True); worker.start()
    base = f"http://127.0.0.1:{server.server_port}"
    def request(route, data=None, headers=None):
        payload = None if data is None else json.dumps(data).encode()
        return urlopen(Request(base + route, payload, headers or {}), timeout=30)
    try:
        bootstrap = json.load(request("/api/bootstrap"))
        token = {"X-Editor-Token": bootstrap["token"], "Content-Type": "application/json"}
        project = template_project("punchline", demo)
        project["scenes"][0]["duration"] = 1
        saved = json.load(request("/api/projects", {"project": project}, token))
        assert json.load(request("/api/projects/" + saved["id"]))["project"]["name"] == project["name"]
        assert json.load(request("/api/preview", {"project": project}, token))["url"].endswith(".png")
        job = json.load(request("/api/renders", {"project": project}, token))
        deadline = time.monotonic() + 45
        while job["status"] in ("queued", "running") and time.monotonic() < deadline:
            time.sleep(.15)
            job = json.load(request("/api/jobs/" + job["id"]))
        assert job["status"] == "complete", job
        part = request(job["url"], headers={"Range": "bytes=0-31"})
        assert part.status == 206 and len(part.read()) == 32
        for headers in ({}, {**token, "Origin": "https://unrelated.example"}):
            with pytest.raises(HTTPError) as error:
                request("/api/projects", {"project": project}, headers)
            assert error.value.code == 403
        with pytest.raises(HTTPError) as error:
            request("/api/bootstrap", headers={"Host": "unrelated.example"})
        assert error.value.code == 403
    finally:
        server.shutdown(); server.server_close(); server.jobs.close(); worker.join(timeout=5)
