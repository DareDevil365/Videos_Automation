# Long-form documentary implementation plan

Reviewed 5 November 2026. Status: **chapter foundation implemented; full episode workflow pending**. No full-length documentary was generated in this review.

## Reference evidence

The owner supplied [BetterWay: What Happened To Devin?](https://www.youtube.com/watch?v=_f7UAsanEBk). YouTube's public oEmbed and player metadata identify BetterWay and a duration of 572 seconds (9:32). Its description outlines Devin's launch, criticism, product changes and subsequent company developments, and credits/promotes Kinetic for motion design and ElevenCreative. These are creator-provided descriptions, not independently verified historical claims or proof of a complete production workflow.

The initial metadata review lacked playback. A subsequent [watch-video analysis](../research/formats/education-and-movies/BETTERWAY_VIDEO_ANALYSIS_2026-11-05.md) inspected 80 overview frames, 60 opening frames and available captions. It confirms progressive explanatory graphics and identifies the sponsor segment separately. Sampling does not establish continuous shot timing; actual audio quality remains unassessed. The implementation choices below remain proposals. No paid service or copied footage is required by this plan.

## Current capability and gaps

| Area | Reusable implementation | Required work |
| --- | --- | --- |
| Research | Source briefs and linked claims | Chapter-level dated evidence and attribution for disputed/reported claims |
| Writing | Gemini scripts, hooks and bounded review | Episode outline, chapter writing, global continuity and repetition review |
| Narration | Local TTS, measured timing, pauses and captions | Chapter timing, pronunciation and whole-episode listening checks |
| Visuals | Typography, comparisons, process blocks, callouts and media inserts | Landscape templates, timelines, sourced charts and document/screen closeups |
| Assembly | FFmpeg exports and durable checkpoints | Independent chapter rendering and final landscape assembly |
| QA | Decode, timing, hashes and sampled frames | Chapter joins, evidence completeness and landscape readability throughout |

The new explicit `documentary` profile now supports landscape focus composition, preview, QA and caption dimensions. Existing shorts retain their portrait defaults; every individual project still rejects durations over 180 seconds. New `documentary_chapter` and `illustrated_story` presets have their own bounded word/unit/duration contracts and visual builders. Factual diagram/grounding contracts are fixture-tested; no live documentary model run is claimed. The owner explicitly redirected this production to a one-off assistant-authored fictional story with no Gemini calls. Full episode planning, chapter revision/invalidation and assembly remain outstanding.

## Implementation sequence

1. **Episode/canvas contract.** Add an explicit long-form profile with ordered chapter IDs, target duration and landscape dimensions. Pass dimensions through graphics, captions, compositor, covers and QA. Preserve existing portrait defaults and short-job bounds. Reject unsupported combinations before generation.
2. **Research and outline.** Let the program produce a sourced central question, chapter objectives and ending from the brief. Store dated claims separately, distinguishing confirmed facts, attributed company claims and interpretation. Missing evidence holds the chapter rather than prompting invented details.
3. **Chapter writing.** Generate chapters using the accepted outline, evidence and shared continuity notes. Review the whole script for contradictions, repeated explanations and unresolved questions. Use bounded repair and per-chapter checkpoints so revisions avoid regenerating unrelated work. The program supplies the script and direction, rather than an assistant-authored script disguised as generation.
4. **Visual grammar.** Begin with code-owned date timelines, comparisons, sourced quotation/document highlights, charts using real values, process diagrams and relevant eligible media. Share one theme and map each scene to its claim/media. Avoid repeated stock carousels, fabricated product screens and invented chart values.
5. **Sound and assembly.** Synthesize/align narration and render each chapter before final assembly. Optional registered music/effects need real timing and voice-aware levels. Retain Python/Pillow/FFmpeg initially because it fits the existing local runtime and checkpoints. This limits arbitrary motion design; evaluate a browser/vector renderer later if the small template set proves insufficient. This is an inferred engineering tradeoff, not a recorded decision to purchase a tool.
6. **Pilot and full episode.** First generate and inspect/listen to a 60-90 second landscape chapter through the new route. Then produce a coherent 6-10 minute test episode. This is a proposed target, not a measured throughput, quality or model-budget promise. Publishing remains disabled.

## Acceptance and tests

- Export matches declared landscape dimensions, decodes fully, preserves readable captions and has no clipped narration or unintended chapter-boundary gaps.
- Every factual claim resolves to evidence or explicit attribution. Missing evidence holds predictably; no invented dates, quotations, statistics or product screenshots appear.
- Restart reuses intact chapter checkpoints. A chapter revision invalidates its dependent render/final assembly without repeating unrelated chapters.
- Existing short jobs retain their dimensions and constraints. A dedicated long-form route does not silently relax the general shorts editor limits.
- Full viewing/listening checks continuity, pacing, pronunciation and visual relevance. Technical and model passes alone do not establish documentary quality or audience retention.

Current milestone: landscape chapter/caption plumbing and trusted comparison, process, timeline, source-highlight, relationship and bar graphics are implemented. An owner-requested assistant-authored fictional pilot exercises the illustration route separately. Outcome grids, full episode outlines, chapter-level revision orchestration/assembly and a complete factual demonstration remain outstanding. See the [illustrated-story guide](categories/illustrated-story/HOW_TO_CREATE.md) and [documentary guide](categories/documentary/HOW_TO_CREATE.md).
