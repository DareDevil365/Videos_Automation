# Create: a source-backed comic lore series

The `comic_lore` preset is a narrated portrait recap of a specific comics canon. The [first three scripts](../../../examples/lore-series/secret-wars-2015/README.md) explain the 2015 Secret Wars version of Doom and Battleworld; it is not the 1984 event or a prediction of the MCU. See [the research packet](../../../research/content-lore/README.md) for official sources and the full-issue access limitation.

For style continuity, start with the [forge recut and visual playbook](VISUAL_STYLE.md). Use the [research and reach workflow](RESEARCH_AND_REACH.md) to choose the angle and plan the opening and payoff. For a new Antigravity session, start with the [assistant handoff](../../ASSISTANT_PRODUCTION.md).

Use the same writing rhythm as the current cut. Start with the action or choice that makes the viewer curious. Give only the setup they need to understand that choice. Each line should move the event forward or change what the viewer thinks happened. Keep multiword names together in speech. Save extra space for a consequence that earns it. Finish an independent episode with its answer. For a serial, carry the question forward at the point where the story actually turns.

1. Pick one arc and record publisher evidence, issue IDs and small atomic claim IDs. Use a factual brief about the fictional canon. Mark plot interpretation as interpretation; do not invent quotations or use secondary summaries as if you had read complete issues.
2. Divide one continuing story at natural turns. Earlier parts end on a specific unresolved event or question, then the next part continues from it. The final part concludes the arc. New plans default to `structure: "serial_cliffhanger"` and support measured 25–179 second Shorts with 7–24 beats and 75–420 words. Use the host to announce the series and part after the opening hook, with a storyteller for the body and the host returning at the end. Every factual line carries its supporting claim IDs.
3. Prepare `series.json` with consecutive part numbers, a local script filename or a focused writing topic for each part, and null publication URLs. Optionally select an allowed `lore_scenes` kind per actual unit ID. A provided source review must hash the exact brief and all supplied scripts. Otherwise the text API performs evidence review. The critic is separate from that review.
4. Run the commands below. Register eligible music first with `music-library --install`, and install the existing Kokoro voice pack. Each local batch checkpoint retains its script, claim-linked art, timed speech, captions and QA. Preview jobs cannot be published.

```powershell
.venv\Scripts\python.exe run_pipeline.py lore-plan --series examples/lore-series/secret-wars-2015/series.json --brief research/content-lore/SECRET_WARS_2015_BRIEF.json --source-review examples/lore-series/secret-wars-2015/source-review.json --output Resources/Plans/my-doom-series.json --build-id my-doom-series
.venv\Scripts\python.exe run_pipeline.py batch-run --plan Resources/Plans/my-doom-series.json
```

`lore-plan --build-id NEW_ID --revise-batch PATH_TO_OLD_BATCH_JSON` can build a deliberate test-only revision of the same series in a new folder while preserving older jobs. A script change needs a new source review and new plan. An actual publication link should be added only after that video exists.

The editor uses local Pillow drawing and FFmpeg. It combines original geometric panels, registered source cutouts, anchored animation and an optional reaction set. Existing visual families cover the forge origin, cosmic events, confrontations and quieter character moments. Choose a specific image or action for the line and keep it tied to the source claim. Use the [audience critic](../../../agents/audience-critique/README.md) for actual attention and clarity issues before rendering and on sampled frames afterward.

The latest [script recipe](../../../examples/lore-series/secret-wars-2015/recut-scripts.json) and [music plan](../../../examples/lore-series/secret-wars-2015/recut-music.json) feed the [recut tool](../../../tools/create_comic_lore_recut.py). It combines registered photo panels with the original art and the theater set. Tight speech removes sustained quiet sections before word alignment, while the measured frame timeline retains short breathing room and a slightly longer host handoff. The chosen series length can change with the story.

For independent answers in a series, explicitly choose `structure: "chapter_answers"` in the series file. Older initialized jobs keep their saved requests. A local episode's `description.md` links to the actual next MP4. When preparing a YouTube release, attach the next episode through Related video and use the corresponding release outro in the script recipe. [YouTube Related video setup](https://support.google.com/youtube/answer/14075157)


The owner’s latest writing requirements are in [NARRATIVE_WRITING.md](NARRATIVE_WRITING.md). Begin with the [cached source library](../../../research/content-lore/SOURCE_LIBRARY.md), extract the causal chain, identify the issue/show during the opening and show its cover/artwork. Current standalone revisions request `source_duration: [42, 50]` and aim near 50s with fuller writing and brisk measured delivery. Preserve the connective reasoning before optimizing word count.
