# Channel workspace: production pipeline and Shorts renderer

This preserves the earlier compositor user/API guide. Use the [current status](../PROJECT_STATUS.md) for present readiness and the [main README](../../README.md) for project navigation. Older test counts and pending-feature notes below are historical; the compositor usage/API remains useful.

The local production pipeline is now implemented alongside the reusable format editor. Open **http://127.0.0.1:8765/production** after starting the server to create jobs, inspect research/script/voice stages, resume holds and download exports. See [PROJECT_GUIDE.md](../../PROJECT_GUIDE.md) for the complete architecture/setup and [IMPLEMENTATION_PLAN.md](../archive/IMPLEMENTATION_STATUS_EARLIER.md) for tested status and remaining extensions.

```powershell
uv sync --extra production --extra dev
.venv\Scripts\python.exe run_pipeline.py doctor
.venv\Scripts\python.exe run_editor.py serve --open
```

Gemini is connected using the selected complete key in ignored `.env`, with free-tier/billing-disabled use confirmed by the owner. Live research, scripting, evidence review, real local Piper narration and a 28.421-second education export passed. YouTube OAuth and actual entertainment footage remain pending; publication stays disabled. Imported examples in `examples/` also work without Gemini. Commands return JSON; `run_pipeline.py --help` lists job, asset, voice, worker, publishing, supervisor and growth controls.

A local compositor for the planned YouTube automation system: choose a reusable 9:16 layout, supply clips/screenshots/music, and export. It does not generate gameplay or invent chat bubbles. No API key, login or paid service is needed for rendering once dependencies are installed. The new default follows the [reference audit](../../research/references/COMPOSITION_REFERENCE_AUDIT.md), including the user's Dozzek example.

## Start on this PC

Double-click **`start_editor.cmd`**, or run from this folder:

```powershell
python run_editor.py serve --open
```

Open **http://127.0.0.1:8765**. Keep the terminal running; Ctrl+C stops the editor. If the port is busy, use `serve --port 8766 --open`. Python, Pillow and FFmpeg were available and tested on this PC during implementation.

For a fresh environment, install Python 3.11+ and FFmpeg (including ffprobe) on PATH, then:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python run_editor.py serve --open
```

The launcher prefers `.venv` when present. The required Python dependency is Pillow; pytest is only for development. No Node build step is needed. FFmpeg must include the `libx264` encoder. This Windows build uses Arial; another local font can be selected with the `SHORTS_EDITOR_FONT` environment variable.

## Make a video

1. Choose **Chat over footage**, **Two blocks**, or **Clip on blurred fill**. Layout switching keeps selected input files and shot timing. **New** saves the current project and opens a fresh empty layout.
2. Import slot **A** (background/main footage), slot **B** (prepared chat screenshot or other clip), and optional music. The blurred-fill preset uses the main clip for both its sharp and blurred layers. Startup creates no media. Old synthetic test media is hidden unless explicitly enabled.
3. Adjust the foreground's position, width/maximum height, fit and border. For stacked blocks, height controls the top/bottom split. Set clip offsets and shot duration; **Use clip length** follows the selected foreground video, or the background when no foreground is selected.
4. Select which clip supplies sound and set music/clip volumes. Optional glow, punch zoom, short flash, micro shake and a timed like/subscribe label are off by default. The effect time is local to each shot; CTA time is measured from the start of the whole video.
5. Scrub a **still-frame preview**, then export to watch/hear the actual MP4. Preview scrubbing does not play real-time motion or audio. Required empty slots block export.
6. Save a project, or download **Layout JSON** to reuse placement/effects with different media. Layout export clears input file references; project export preserves them. **Add shot** supports a change of screenshot or clip state without writing a whole new format.

Projects are saved on this computer. The browser also keeps the current draft. Export jobs have progress, cancellation and a saved history. A stopped export is marked interrupted when the server restarts; starting a new export is required.

| Format | What to plug in | Behavior |
| --- | --- | --- |
| Chat over footage (`overlay`) | Background plus prepared screenshot/chat clip | Full-frame background; compact foreground near the top, with aspect ratio preserved |
| Two blocks (`stack`) | Two clips/images | Top/bottom blocks with adjustable split and border |
| Clip on blurred fill (`focus`) | One clip | A sharp, aspect-preserved copy over a blurred full-frame copy |

The previous six card/chat recipes and saved projects are preserved at **http://127.0.0.1:8765/legacy** and through the existing API/CLI. They are not the default production style. Their generated artwork/animation is synthetic demo material, not convincing gameplay or finished episodes. Explicit `demo` / `serve --with-demo` commands still create test media; ordinary startup does not. This compositor does not find, download or clear media rights.

## Export files and storage

Default workspace: `data/editor/` (excluded from source control).

```text
assets/             Imported copies and their metadata
projects/           Saved version-1 JSON projects
previews/           Cached PNG frames and preview logs
jobs/<job-id>/      Job state and completed export files
demo-projects/      Optional synthetic examples from the explicit demo command
```

Every successful export produces:

- `video.mp4`: H.264/AAC, 9:16, 720×1280 or 1080×1920, 24 or 30 fps.
- `video.png`: a cover frame. Selecting a YouTube Shorts cover is a later publishing concern.
- `video.srt`: scene-caption output; empty for compositions with no supplied caption text. The compositor does not transcribe a screenshot/chat clip or invent its dialogue.
- `video.project.json`: the normalized reusable recipe.
- `video.manifest.json`: dimensions, duration, audio presence and asset references; not a rights approval.

Compositions support 1–30 shots and at most 180 seconds total. A single composition shot can be up to 180 seconds; legacy recipes retain their 60-second scene limit. Images hold for a shot; short clips and music loop. Foreground contain preserves the whole screenshot and leaves the remaining background visible; it does not add an opaque padded card. Source audio comes from the chosen background or foreground clip, plus optional music. Music has simple fades and a limiter, without automatic speech ducking or loudness mastering. Timed effects are not beat detection or crossfades between shots.

Project JSON references asset IDs. Moving a JSON file alone does **not** move its media; preserve the whole workspace when moving projects. Imported files, preview caches, export intermediates and logs accumulate; there is no automatic cleanup yet. Do not expose the local server to the internet: it is a loopback-only, single-user tool.

## Use without the editor

The program can supply a JSON job and actual local file paths. Start from [the example job](../../examples/composition-job.example.json), replace its paths, and run:

```powershell
python run_editor.py formats
python run_editor.py compose examples/composition-job.example.json --output data/editor/exports/my-video.mp4
python run_editor.py render saved-project.json --output data/editor/exports/another-video.mp4
```

The example intentionally references missing user-supplied files and cannot export until they are supplied. Paths in a composition job resolve relative to the job JSON. Its `template` may be `overlay`, `stack`, `focus`, or a saved layout JSON path. `inputs` binds `background`, `foreground`, optional `music` and optional `narration`. Use `shots` for multiple shot objects with their own `duration`, offsets, `effect_at` and optional `inputs`; shared inputs remain available. A prepared foreground recording supplies its own message timing. Static screenshots can change between shots but are not automatically turned into a scrolling conversation.

For an AI/program caller, add **`--json`** to `compose` or `render`. It returns one JSON object on stdout with `schema_version: 1`, `status: "complete"`, an `outputs` map (video, cover, captions, project, manifest), duration and dimensions. Progress text goes to stderr. Ordinary validation/render failures return `status: "failed"`, an error type/message and a nonzero exit code. Invalid command-line syntax uses argparse's normal nonzero error; a forcibly terminated process may return no JSON. Check the exit code and actual complete artifacts before treating a job as successful. No browser interaction is required.

```powershell
python run_editor.py compose job.json --output data/editor/exports/job-001.mp4 --json
```

This is the **execution interface**, not a completed natural-language-to-video agent. The future scripter/director must translate creative instructions into supported fields and supply real media paths. See the [current module plan and status](../archive/IMPLEMENTATION_STATUS_EARLIER.md) for the researcher, scripter, voiceover and production director.

Choose a new output filename; existing MP4 files are protected from overwrite. To use another workspace, put the global option first: `python run_editor.py --data D:\ShortsWorkspace serve`.

With the package installed, the Python interface is:

```python
from shorts_editor.jobspec import materialize_job
from shorts_editor.render import render_project
from shorts_editor.store import Store

store = Store("data/editor")
project = materialize_job({
    "template": "overlay",
    "duration": 20,
    "inputs": {"background": "gameplay.mp4", "foreground": "chat.mp4"}
}, store, base="my-input-folder")
render_project(project, store, "data/editor/examples/new-video.mp4")
```

`render_project` has optional progress and cancellation callbacks/events. It makes no network requests. The browser uses the same renderer, so there is no separate browser-only export implementation.

## Validation and remaining work

```powershell
python -m pytest -q
node --check src/shorts_editor/web/studio.js
```

Integration tests render the new and legacy formats, decode actual MP4s, inspect media-slot pixels, check transparent contain behavior, timed effects/CTA, selected audio frequency, reusable layouts, bounds/missing-input rejection, cancellation, restart state and HTTP export/download isolation. Solid-color fixtures test technical behavior; they do not establish production aesthetics or audience response. Node is optional and used only for this syntax check.

The compositor remains independently usable. The production package adds source research, Gemini scripting, local Piper speech, timed chat/lesson graphics, an original-source-audio clip route, durable orchestration, export QA/packaging, OAuth/resumable publication adapters, local supervision and owned Analytics/growth reporting. Current automated verification covers 59 tests, including actual FFmpeg pipeline exports and simulated upload recovery. The new dashboard's HTTP controls and JavaScript syntax were checked; visual browser QA is pending because browser use is disabled in Work settings.

Arbitrary multitrack timelines, beat cuts, forced word alignment, fully automated movie-list/clip discovery, multilingual quality checks and native After Effects/Resolve bridges remain extensions. Supplied media, voice quality, sources and publication policy still need real-content/account validation. A successful export is not a rights, monetization or growth guarantee.

See [PROJECT_GUIDE.md](../../PROJECT_GUIDE.md) for architecture and design tradeoffs, and [IMPLEMENTATION_PLAN.md](../archive/IMPLEMENTATION_STATUS_EARLIER.md) for the larger automation roadmap.
