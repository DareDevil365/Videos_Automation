# Long-form documentary implementation plan

Reviewed 5 November 2026. Status: **proposed, not implemented**. No full-length documentary was generated in this review.

## Reference evidence

The owner supplied [BetterWay: What Happened To Devin?](https://www.youtube.com/watch?v=_f7UAsanEBk). YouTube's public oEmbed and player metadata identify BetterWay and a duration of 572 seconds (9:32). Its description outlines Devin's launch, criticism, product changes and subsequent company developments, and credits/promotes Kinetic for motion design and ElevenCreative. These are creator-provided descriptions, not independently verified historical claims or proof of a complete production workflow.

Playback was unavailable. No reference audio, captions or video was inspected. Shot timing, typography, sound and animation quality have not been assessed. The choices below propose an original researched explainer; they are not claims about observed editing in this video. No paid service or copied footage is required by this plan.

## Current capability and gaps

| Area | Reusable implementation | Required work |
| --- | --- | --- |
| Research | Source briefs and linked claims | Chapter-level dated evidence and attribution for disputed/reported claims |
| Writing | Gemini scripts, hooks and bounded review | Episode outline, chapter writing, global continuity and repetition review |
| Narration | Local TTS, measured timing, pauses and captions | Chapter timing, pronunciation and whole-episode listening checks |
| Visuals | Typography, comparisons, process blocks, callouts and media inserts | Landscape templates, timelines, sourced charts and document/screen closeups |
| Assembly | FFmpeg exports and durable checkpoints | Independent chapter rendering and final landscape assembly |
| QA | Decode, timing, hashes and sampled frames | Chapter joins, evidence completeness and landscape readability throughout |

Concrete blockers: `src/shorts_editor/models.py` rejects projects over 180 seconds and returns portrait dimensions. `src/yt_pipeline/director.py`, `pipeline.py` and visual renderers also contain portrait assumptions. Existing playbooks impose short word/unit/duration bounds. Increasing one duration cap would not create a validated documentary route.

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

Next milestone: the episode/canvas contract and one generated landscape chapter. Reference playback analysis and a finished full-length demonstration remain outstanding.
