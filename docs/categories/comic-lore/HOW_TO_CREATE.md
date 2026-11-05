# Create: a source-backed comic lore series

The `comic_lore` preset is a narrated portrait recap of a specific comics canon. The [first three scripts](../../../examples/lore-series/secret-wars-2015/README.md) explain the 2015 Secret Wars version of Doom and Battleworld; it is not the 1984 event or a prediction of the MCU. See [the research packet](../../../research/content-lore/README.md) for official sources and the full-issue access limitation.

1. Pick one arc and record publisher evidence, issue IDs and small atomic claim IDs. Use a factual brief about the fictional canon. Mark plot interpretation as interpretation; do not invent quotations or use secondary summaries as if you had read complete issues.
2. Divide the arc into chapters that have independent meaning: a specific opening promise, escalation, a concrete answer, then at most one genuine next-part lead. Use one narrator, roughly 75–175 words in 7–12 units and a measured 25–80 seconds. A final chapter ends. Every factual line carries its supporting claim IDs.
3. Prepare `series.json` with consecutive part numbers, a local script filename or a focused writing topic for each part, and null publication URLs. Optionally select an allowed `lore_scenes` kind per actual unit ID. A provided source review must hash the exact brief and all supplied scripts. Otherwise the text API performs evidence review. The critic is separate from that review.
4. Run the commands below. Register eligible music first with `music-library --install`, and install the existing Kokoro voice pack. Each local batch checkpoint retains its script, claim-linked art, timed speech, captions and QA. Preview jobs cannot be published.

```powershell
.venv\Scripts\python.exe run_pipeline.py lore-plan --series examples/lore-series/secret-wars-2015/series.json --brief research/content-lore/SECRET_WARS_2015_BRIEF.json --source-review examples/lore-series/secret-wars-2015/source-review.json --output Resources/Plans/my-doom-series.json --build-id my-doom-series
.venv\Scripts\python.exe run_pipeline.py batch-run --plan Resources/Plans/my-doom-series.json
```

`lore-plan --build-id NEW_ID --revise-batch PATH_TO_OLD_BATCH_JSON` can build a deliberate test-only revision of the same series in a new folder while preserving older jobs. A script change needs a new source review and new plan. An actual publication link should be added only after that video exists.

The editor uses local Pillow drawing and FFmpeg to create original symbolic comic panels, not downloaded publisher pages, official art or a visual-generation service. Supported scenes include world collapse, survival craft, Battleworld, throne/control, hidden source, meal, confrontation, rebuilding and family return, with cutaway/detail variants. Pictures illustrate the exact line and source claims; they do not add factual evidence. Use the [audience critic](../../../agents/audience-critique/README.md) for actual attention/clarity issues before rendering and on sampled frames afterward.
