# Deadpool's real target

The [script](SCRIPT.md), [selection review](SELECTION_REVIEW.md), `brief.json` and `series.json` record the original connected narration, checked claims and per-shot reasons. This is *Deadpool Kills the Marvel Universe* #1–4 (2012), an alternate comic reality, not the MCU. The source collection cover is retained at near-native display size instead of heavily enlarging it.

```powershell
.venv\Scripts\python.exe tools/create_screen_recaps.py --only deadpool --measure-only
.venv\Scripts\python.exe tools/create_screen_recaps.py --only deadpool --build-suffix polished-20261107
.venv\Scripts\python.exe tools/create_screen_recaps.py --only deadpool --build-suffix polished-20261107 --render
```

The shared builder supplies the local editor with the exact script and validated cuts. It uses installed local voices, alignment, curated music, registered theater assets and FFmpeg, with no Gemini text or image generation. Setup is the same as [the screen recap workflow](../../screen-recaps/README.md). Download and inspect the cover first; its URL is recorded in the builder. The current output is under `Resources/Productions/deadpool-fourth-wall-polished-20261107/part-1/`. A changed script requires a new build ID.

The actual full issues and referenced competition video were not watched/read. Sources are a creator interview, publisher metadata and a bounded secondary plot recap. Source artwork is for local review; technical QA does not establish audience engagement or voice acting quality. Finished checks are recorded after export.


Completed local review: **51.366s**, 720×1280, **16 directed shots**. All 14 package hashes matched and technical QA passed. Every exported cut was sampled, with the source image, main action, lower audience, captions and final card inspected. The spoken/visible subscribe request starts at **49.373s** after the story consequence. No narration silence of at least 0.3s was detected at −42 dB; mixed clipping was zero. Local review evidence is beside the video. Voice acting, music preference and real audience response remain matters for human review and actual channel data.
