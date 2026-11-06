# Continue making videos in Antigravity

Open this project folder in Antigravity. Its workspace instructions are in [AGENTS.md](../AGENTS.md). Start the session with **“Use yourself as the writer and shot planner. Read the comic lore playbook, check production history, and make the next local preview.”** The assistant writes the creative files. The program handles registered assets, local voices, timing, motion, rendering, captions, and the finished title and description package.

## Start with what happened last

```powershell
.venv\Scripts\python.exe run_pipeline.py production-history --limit 5
```

- `latest_made` lists completed previews with their title, package, video, and recent visual choices. `uploaded_through_app` uses the YouTube IDs already saved by the upload workflow. An unfinished transfer is tracked separately so it can be reconciled. Studio uploads made outside the app need a separate Studio check.
- `recent_unfinished` shows the stage and failure code for work that may be resumable. If the user meant a particular job, use the original plan and `batch-status --plan ...` to verify it. Batch plans are immutable once initialized. Use a new build ID for a changed script or shot list.
- `next_to_make` is a starting idea from [the production queue](PRODUCTION_QUEUE.json). Check the latest request and current evidence. As of the forge recut, the suggested comic is **How Doctor Doom took Latveria**. Comic lore comes first, then movie coverage and current affairs.

## Make one reviewable result

1. Start with the [full AI task list and scene decision matrix](categories/comic-lore/SHOT_DECISIONS.md). It covers research, writing, visual blocking, render review, metadata, logging and upload handoff. Watch a current reference and check the last three comic cuts for reused images, settings, angles, and openings. Record why this angle is worth making and how the opening, action and payoff will work on a phone.
2. Make a short source brief, script and shot list. Use the [forge script recipe](../examples/lore-series/books-of-doom/forge-recut.json) for the writing and visual rhythm and the [Secret Wars example](../examples/lore-series/secret-wars-2015/README.md) for multipart structure. The script contract takes a viewer-facing title and a short description. Write both with the script, using the actual hook. The package step adds sources and credits. If there are useful alternate titles, the optional `publication_metadata` field takes the format in [publication_metadata.py](../src/yt_pipeline/publication_metadata.py).
3. Save a source review with `reviewer`, `supported: true`, `limitations`, `brief_sha256`, and a `script_sha256` object keyed by each script filename. Only mark claims supported after reviewing the cited material. `Get-FileHash -Algorithm SHA256` can supply the hashes. Use lowercase hex.
4. Build the plan and render it. Use your current Antigravity model to produce the input files. This route supplies all text and leaves the local editor to execute it without a separate text API generation call.

```powershell
.venv\Scripts\python.exe run_pipeline.py lore-plan --assistant-authored --series path/to/series.json --brief path/to/brief.json --source-review path/to/review.json --output Resources/Plans/new-build.json
.venv\Scripts\python.exe run_pipeline.py batch-run --plan Resources/Plans/new-build.json
```

5. Open the actual MP4 under `Resources/Productions/<build>/part-1/`. Check the opening, action contact, speaking gaps, any cliffhanger, and the portrait caption space. Check `metadata.json` for the final title, description and credits. Confirm a passing local preview in the history. When the request includes publishing, follow the existing [upload workflow](AUTOMATIC_PRODUCTION.md) and verify the saved YouTube result.

Use the example pacing and art direction as a starting point. A slow reveal can earn a pause. A good callback can reuse a visual on purpose. If a new composition needs a new scene, add the smallest renderer extension and make a short review clip before building the whole episode.

For **geometric characters with photographic environments and object cutouts**, use the [Hellboy episode](../examples/lore-series/hellboy-horns/README.md). It records the research, hook, eight shot decisions, continuity and media sources. Its `hellboy_media` field resolves registered lava, ruins and book images. The recipe draws characters over the photographs, then applies the normal camera and captions. This is a story-specific implementation of the style. A new story still needs its own source review and blocking. Follow the owner's current ending preference; the Hellboy example finishes on its answer with `edit.cta: false`, no subscription request and no invented next part.

Before searching for images or drawing a new layer, check the [starter catalog](../Resources/Templates/ComicLore/README.md) and [asset reuse plan](categories/comic-lore/REUSABLE_ASSET_PLAN.md). Ready assets have stable names and local IDs. A geometric actor can wear a different jacket while retaining their identifying features. Use motion where the viewer needs to see an exchange, a theft, a strike or its consequence. When a circular face crop helps, prepare it once from a registered source and verify the actual portrait. For a first production pass, use geometry whenever the source photo or exact action cannot be checked.
