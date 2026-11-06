import json

from shorts_editor.store import write_json
from yt_pipeline.core import Workspace, file_hash
from yt_pipeline.production_history import production_history
from yt_pipeline.publishing import save_upload


def test_history_separates_local_outputs_uploads_and_incomplete_transfers(tmp_path, monkeypatch):
    ws = Workspace(tmp_path/"workspace")
    queue = tmp_path/"queue.json"
    write_json(queue, [
        {"series_id":"arc","channel":"entertainment"},
        {"series_id":"followup","channel":"entertainment"},
    ])
    monkeypatch.setattr("yt_pipeline.production_history.QUEUE", queue)

    def make(part):
        job = ws.create("entertainment", {"topic":f"Part {part}", "series":{"id":"arc","part":part,"total":2}})
        package = ws.job_dir(job["id"])/"package.json"
        write_json(package, {"title":f"Story {part} → preview","description":"Local package"})
        ws.update(job["id"], status="ready", artifacts={"package":{"path":str(package),"sha256":file_hash(package)}})
        return job["id"]

    first = make(1)
    save_upload(ws, first, {"video_id":"abcdefghijk", "phase":"published", "session":"secret-session-url"})
    unfinished = ws.create("entertainment", {"topic":"Interrupted upload"})["id"]
    save_upload(ws, unfinished, {"phase":"uploading", "session":"other-secret-session"})
    result = production_history(ws)
    assert result["next_to_make"]["series_id"] == "arc"
    assert result["uploaded_through_app"][0]["url"] == "https://youtu.be/abcdefghijk"
    assert result["upload_needs_reconciliation"][0]["job_id"] == unfinished
    assert "secret-session" not in json.dumps(result)
    make(2)
    result = production_history(ws)
    assert result["next_to_make"]["series_id"] == "followup"
    assert [item["part"] for item in result["latest_made"]] == [2,1]
