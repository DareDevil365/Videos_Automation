# Animation repositories and free API boundaries

Checked 5 November 2026 at the owner's request. These are primary README/documentation checks, not installations, code audits or benchmarked integrations. The requested one-off storytelling pilot uses assistant-authored text/direction, built-in imagegen artwork, local Kokoro and our existing renderer; no Gemini generation calls are required for it.

## Useful candidates

| Repository | What it actually offers | Meaning of free and fit here |
| --- | --- | --- |
| [Frame Studio](https://github.com/programmersd21/frame_studio) | Gemini plans/generates React/Remotion code, TypeScript validation with bounded repair, browser MP4 rendering | Closest reference for animated editorial graphics. Rendering runs on the client; a Gemini key and Supabase setup are documented. A free model/tier is not an unlimited API or free access to every selectable model. Not installed. |
| [Manim Community](https://github.com/ManimCommunity/manim) | Local Python animation framework for graphs, geometry, diagrams and explanatory scenes | Free local renderer, not a hosted generation API. Useful for reusable chart/timeline templates. Model code generation is optional; assistant-authored scenes need no text API. Retaining our current renderer avoids adding its dependency/toolchain for this pilot. |
| [Manim Generator](https://github.com/BinyamMamo/manim_generator) | Documents prompt-to-Manim code through Gemini and MP4 rendering | A small natural-language wrapper worth examining for diagram workflows. Its README's free-Gemini claim still depends on current model access/quotas. Not installed or execution-tested; generated Python would require a bounded isolated rendering design. |
| [eduvids](https://github.com/namanbnsl/eduvids) | Lesson/narration planning and Manim scenes rendered in an E2B sandbox, with timed voice | Useful chapter/scene architecture. Self-host setup needs Gemini, E2B, Convex, Upstash and UploadThing configuration; the public free demo does not establish indefinitely free self-host operation. Not a zero-setup local replacement. |
| [Showrunner](https://github.com/scrollmark/showrunner) | Pluggable Remotion, Manim and AI-clip formats, resume/refine commands and local Kokoro | Useful reference for checkpoints and per-scene refinement. Default text providers require paid-service credentials; its video providers are separate dependencies. Repository availability and local TTS do not make its whole default pipeline a free API. Not installed. |

Frame Studio's [primary README](https://raw.githubusercontent.com/programmersd21/frame_studio/main/README.md) describes its actual client/server flow. Showrunner's [primary README](https://raw.githubusercontent.com/scrollmark/showrunner/main/README.md) separates text, TTS, render and video providers. eduvids' [setup section](https://github.com/namanbnsl/eduvids#run-it-yourself) lists its hosted dependencies. These workflows are inspiration; none has been silently added to this project.

## Provider and renderer costs are separate

[Google's current pricing](https://ai.google.dev/gemini-api/docs/pricing) lists free input/output for Gemini 3.5 Flash-Lite, with model/tier limits. That supports text-to-animation-plan/code as a possible free-tier route; it does not grant unlimited requests, guaranteed availability or a free synthetic-video API. This project's existing free-only controls and cooldowns continue to apply. No provider/key rotation is proposed.

[Remotion's license page](https://www.remotion.dev/docs/license/pricing) describes free eligibility for individuals and companies of up to three people, and paid licensing for ineligible organizations. Do not inherit a repository's simplified licensing summary instead of checking the renderer's current terms. Browser/local rendering also uses local compute even when there is no hosted render charge.

## Project choice

For the immediate pilot, retain Python/Pillow/FFmpeg and local speech, and use the assistant as the script/director only because the owner explicitly requested this exception. It gives a concrete visual result without introducing another model provider, account, hosting stack or generated-code execution path.

For future explanatory animation, evaluate Frame Studio's approach and Manim first. A small set of locally rendered, validated graphic templates is the first integration candidate; adopting an entire SaaS-style repository is not necessary to obtain animated bars, relationships and timelines. Full character animation or realistic generated motion is a different requirement from animating diagrams or still artwork and remains unimplemented here.
