# BetterWay reference: visual sampling with watch-video

Reviewed 5 November 2026. Reference: [What Happened To Devin?](https://www.youtube.com/watch?v=_f7UAsanEBk), BetterWay. This supplements the [long-form implementation plan](../../../docs/LONG_FORM_IMPLEMENTATION_PLAN.md). It is reference analysis, not a generated episode or approval of the video's factual claims.

## Tool and actual evidence

Installed [KishoreVetha/watch-video-skill](https://github.com/KishoreVetha/watch-video-skill), skill folder `watch-video`, through the standard skill-installer. Read its instructions and extraction script before running. This is a user-level analysis tool, not a production dependency, model service or change to our runtime presets.

The existing yt-dlp 2026.07.04 received HTTP 403. A current `yt-dlp[default]` in an isolated `uv run --no-project --with` environment succeeded. No keys, account cookies, browser session, paid transcription API or publishing action were used. FFmpeg, ffprobe, Node and Python were already present. The project dependency/lock files were not changed.

The downloaded reference measures **571.834 seconds, 1280 x 720, with audio**. The skill extracted 80 overview frames in seven sheets and 60 opening frames at two per second for 0-30 seconds in five more sheets. All twelve sheets were visually inspected. Available English automatic captions were read; another requested English track received HTTP 429, so the usable original track was retained without retrying that rate limit.

Local-only evidence is under `data/reference-analysis/betterway-devin-20261105/` and `data/reference-analysis/betterway-devin-opening-20261105/`: manifests, frames, sheets, captions and run records. These files are ignored by Git and are reference material, not reusable production assets.

Limitations: sampling is not continuous playback. The script uses a fixed sampling grid, not scene-change detection. Its burned labels reflect that grid, so overview timestamps are approximate within several seconds; they should not be used as frame-exact edit points. The opening's denser sample shows changes at roughly half-second intervals. Captions can mistranscribe names. The audio track was present but not listened to; voice acting, music, mix and sound-effect quality remain unassessed. Screenshots and narration are not independent verification of a claim.

## Observations

- **Opening, about 0:00-0:30:** a date/logo introduction develops into a growing valuation graphic, then contrasting product cards and a visual question. The diagram changes with the argument rather than remaining one background card.
- **About 0:45-1:05:** bars build a benchmark comparison, followed by qualification panels.
- **About 2:00-2:45:** request-versus-delivery cards, highlighted reporting and a task-result grid explain criticism visually.
- **About 3:30-4:30:** logos, connecting lines and staff icons communicate changing company relationships.
- **About 8:14 onward:** the documentary gives way to a sponsor/product demonstration. The entire 9:32 should not be treated as documentary-story duration.

Across the sampled documentary frames, a dark canvas, restrained accent colors, whitespace and consistent cards support charts, diagrams and source excerpts. The sampled opening confirms progressive reveals and repositioning. Intermediate animation counters are not necessarily final reported values. No shot-frequency average or retention benefit was measured.

## What this changes for our implementation

These are proposed engineering choices based on the observations, not capabilities added by installing the skill:

1. Prioritize a small landscape graphic vocabulary: metric comparison, growing chart, date timeline, highlighted source excerpt, relationship map and outcome grid. Use original layout/art and verified data, not recreated reference screenshots or dialogue.
2. Give each graphic a measured scene clock and explicit reveal/hold/transition states tied to narration. Current source-camera motion and callout animation are useful foundations but do not already supply this documentary renderer.
3. Record each chart's final values and claim/source IDs separately from its animation state. Review settled frames as well as entry/exit so a halfway counter is not mistaken for the final statistic.
4. Keep screenshots, diagrams and supporting media semantically related to the current explanation. A longer stock-image sequence would not address the missing explanatory motion.
5. Retain the staged milestone: episode/canvas contract, one program-written 60-90 second landscape chapter, then a full episode after actual viewing/listening checks. Chapters, landscape plumbing and long-form review remain unimplemented.

The skill is demonstrated for this reference on this PC. It extracts evidence for the assistant to inspect; it does not autonomously rate or repair our finished videos. No general reliability claim follows from one successful run.
