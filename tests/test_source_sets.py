from PIL import Image, ImageChops, ImageDraw
import pytest

from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset
from yt_pipeline.core import Held, Workspace
from yt_pipeline.dialogue_captions import progressive_cues
from yt_pipeline.source_delivery import connected_text
from yt_pipeline.source_sets import SETTINGS, draw_reaction_set, resolve_source_set


def test_set_cast_and_props_are_reusable_and_remain_preview_only(tmp_path):
    workspace = Workspace(tmp_path / "pipeline")
    path = tmp_path / "cutout.png"
    cutout = Image.new("RGBA", (60, 90))
    ImageDraw.Draw(cutout).ellipse((4, 4, 55, 85), fill="#d7af84")
    cutout.save(path)
    record = register_asset(workspace, path, "test", {"license": "review only"}, commercial=False, editing=False)
    asset_id = record["id"]
    request = {"reaction_set": {"setting": "cinema", "cast": [asset_id], "props": [asset_id]}}
    script = {"units": [{"id": "u1"}]}
    with pytest.raises(Held, match="commercial edited use"):
        resolve_source_set(workspace, request, script)

    stills = set()
    for setting in SETTINGS:
        request["reaction_set"]["setting"] = setting
        _, resolved, assets = resolve_source_set(workspace, {**request, "test_only": True}, script)
        assert [asset["id"] for asset in assets] == [asset_id]
        first = Image.new("RGB", (720, 1280))
        second = first.copy()
        draw_reaction_set(first, resolved, 0)
        draw_reaction_set(second, resolved, .75)
        box = ImageChops.difference(first, second).getbbox()
        assert box and box[1] >= 992
        stills.add(first.crop((0, 992, 720, 1280)).tobytes())
    assert len(stills) == len(SETTINGS)

    backdrop_path = tmp_path / "backdrop.png"
    Image.new("RGB", (760, 320), "#31444f").save(backdrop_path)
    backdrop = register_asset(workspace, backdrop_path, "original_graphic", {"source": "fixture"})
    request["reaction_set"] = {"setting": "workshop", "cast": [asset_id], "backdrop": backdrop["id"]}
    _, resolved, assets = resolve_source_set(workspace, {**request, "test_only": True}, script)
    frame = Image.new("RGB", (720, 1280))
    draw_reaction_set(frame, resolved, 0)
    assert {asset["id"] for asset in assets} == {asset_id, backdrop["id"]}
    assert frame.getpixel((20, 991)) == (0, 0, 0)
    assert frame.getpixel((20, 992)) == (49, 68, 79)


def test_linked_title_stays_whole_in_speech_and_captions():
    title = "The Fantastic Four: First Steps"
    line = f"Watch {title} first."
    assert connected_text(line, [title]) == "Watch The Fantastic Four First Steps first."
    words = [{"text": word, "start": index / 4, "end": (index + 1) / 4}
             for index, word in enumerate(line.split())]
    assert [cue["text"] for cue in progressive_cues(words, [title])] == ["Watch", title, "first."]


def test_named_preset_is_frozen_at_job_creation(tmp_path):
    workspace = Workspace(tmp_path / "pipeline")
    path = workspace.root / "reaction-presets.json"
    recipe = {"setting": "city", "cast": ["example-id"]}
    write_json(path, {"spider-man-city": recipe})
    request = {"playbook": "movie_brief", "reaction_preset": "spider-man-city", "test_only": True}
    job = workspace.create("entertainment", request)
    write_json(path, {})
    assert workspace.get(job["id"])["request"]["reaction_set"] == recipe
    with pytest.raises(Held, match="not installed"):
        workspace.create("entertainment", request)
