# Gemini video generators: deeper repository audit

Research snapshot: 2 November 2026. This extends [the earlier 35-repository review](AUTOMATION_REPOSITORY_REVIEW.md) with **14 new repository leads**, including projects with 0–2 stars. Selected implementation files were read in ten of them. The [structured inventory](gemini_video_repository_candidates.json) records inspected paths, licenses, provider dependencies, dated metadata and unresolved claims. No third-party project was installed or executed; no personal browser, paid generation, credentials or external account was used.

The useful discovery is that Gemini can create an edited video **without being a video diffusion model**: it can write scene JSON, select existing media, or author animation code that a local renderer turns into frames. Several repos implement these routes. However, “uses a Gemini key” does not establish that the whole program is Gemini-only, independent of a coding assistant, or free to run. Some polished demos depend on paid image/video/voice services or a host coding agent.

## Recommended additions

Keep our local voices, state/recovery, evidence records, FFmpeg exports and standalone controls. Add one bounded advanced scene renderer and actual visual review rather than replace the entire project.

1. **Pre-authored motion scenes driven by Gemini JSON.** Start with a before/after comparison, labelled diagram, readable evidence insert and small animated chart. Bind existing spoken-unit IDs and measured timings. Our model should choose validated parameters in trusted templates first. Free-form generated Python/TSX would be a separate sandboxed experiment.
2. **A preview gate that sees actual frames.** Give Gemini representative scene frames, narration and intended action. Record concrete mismatches, not just a confidence score. A text-only script critic cannot claim it inspected bodies, subtitle readability or what footage shows. Retain deterministic complete-dialogue, active-speaker, timing and integrity checks.
3. **Broader media acquisition with relevance and license evidence.** Study YAAS provider adapters, but keep our hold when an essential screenshot/poster is missing. More irrelevant images do not solve the rejected random-photo problem. Prefer a bounded query-reformulation/verification loop over random selection.
4. **Only then test code-authored animation.** A short education diagram is a useful comparison. Comedy still needs good premise, escalation and payoff before elaborate motion. The parent implementation's new exact-script subtitles and consistent speaker framing should be retained.

These are pitches, not installed features. Model judgements about humor/retention are opinions, not proof.

## Shortlist

| Repository | Actual route | Fit and decision |
| --- | --- | --- |
| [XredaX/Code2Video-AI](https://github.com/XredaX/Code2Video-AI) | Gemini → Remotion TSX → frame preview/review → local MP4 | Strong small-project reference; no repository license found, so no direct code copying |
| [showlab/Code2Video](https://github.com/showlab/Code2Video) | Teaching outline → storyboard → Manim code → render/layout/video feedback | MIT; strong education pattern, but inspected Gemini calls use configured AzureOpenAI endpoints, not a plain Google key |
| [Scenerio](https://github.com/chengenli9/BeaverHacks2026) | Measured footage → Gemini plan → manifest → FFmpeg/Remotion → critics | Verified hackathon lead; good QA design; no license found |
| [YAAS](https://github.com/raunakpatil/youtube-agentic-ai-studio) | Topic research/script → stock → Edge TTS → MoviePy → review/upload | MIT; closest whole free-stack comparison, but weak media/provider fallbacks need changing |
| [Automated Video Generator](https://github.com/itsPremkumar/Automated-Video-Generator) | Script/stock/Remotion toolkit, JSON operations and host-agent integrations | MIT; useful examples, but “agent/no-key” mode may consume the host model allowance |
| [Showrunner](https://github.com/scrollmark/showrunner) | Pluggable faceless/Manim/Veo formats, resumable scene refinements | MIT; default planner is Anthropic, while its Gemini provider means Veo generation |

Stars at inspection: respectively 1, 2,214, 2, 205, 121 and 18. These are discovery context, not quality scores. A recent `pushed_at` can describe a different branch; it is not a successful test or the date of every inspected file. Four key audits have pinned default-branch commit links in the inventory.

## XredaX/Code2Video-AI: the most useful small-project visual loop

The [agent runner](https://github.com/XredaX/Code2Video-AI/blob/14b7cf53a76eb2ed0103bf2017b423e17f0b7c99/src/lib/agent-runner.ts) renders a representative contact sheet, sends it back to Gemini and tracks the hash of reviewed code. The final render must use that reviewed code. Its instructions distinguish preview from a finished output. This is directly relevant to our “valid JSON, bad-looking video” problem.

The [render runner](https://github.com/XredaX/Code2Video-AI/blob/14b7cf53a76eb2ed0103bf2017b423e17f0b7c99/src/lib/render-runner.ts) uses Docker with no network, read-only base filesystem, capability drops, controlled mounts, CPU/RAM/process limits and timeout. The [CLI](https://github.com/XredaX/Code2Video-AI/blob/14b7cf53a76eb2ed0103bf2017b423e17f0b7c99/renderer/render-cli.js) renders actual stills/video. The basic validators check input/path properties; they do not make arbitrary TSX safe by themselves.

This produces programmatic motion graphics, not live-action footage. README-linked MP4/GIF examples exist; none was executed or quality-certified locally. No root license was found in metadata/tree inspection. Independently implement its preview→critique→bounded revision pattern with our renderer, or establish reuse permission before copying code.

## ShowLab Code2Video: a real education animation design

The MIT [agent](https://github.com/showlab/Code2Video/blob/1142d8e14cdc2806df85aedb0fbb5dca474caa0f/src/agent.py) separates outline, sections, code generation, real Manim rendering, layout analysis and multimodal review. Failures can trigger section repairs. This is useful where objects must express a relationship: quantities, chronology, flows, before/after or a concept demonstration.

The integration catch is [gpt_request.py](https://github.com/showlab/Code2Video/blob/1142d8e14cdc2806df85aedb0fbb5dca474caa0f/src/gpt_request.py): functions named for Gemini instantiate `openai.AzureOpenAI` using endpoint configuration. An OpenAI client library does not itself imply an OpenAI account, but this configuration is **not a direct Google AI Studio API-key adapter**. We would need to port it to our Gemini client and update supported model/request details.

[Dependencies](https://github.com/showlab/Code2Video/blob/1142d8e14cdc2806df85aedb0fbb5dca474caa0f/src/requirements.txt) include Manim, Cairo/Pango/OpenGL components, MoviePy and API clients. The agent permits repair limits of ten and concurrent sections; do not copy those budgets into a free-tier runtime. Start with trusted templates or an isolated one-scene renderer, at most two repairs and a clear failure. Generated Python must not run with unrestricted workspace/account access. The local codegen/layout strategy is useful without adopting the repository wholesale.

## Scenerio: a hackathon clue with organizer evidence

The [BeaverHacks judging page](https://judge.beaverhacks.org/cmlfqho300000kv04wi9199a5) explicitly lists Scenerio as first in Google's Best Use of Gemini track. [Oregon State University's event article](https://today.oregonstate.edu/all-stories/beaver-hackathon-brings-crowd-student-programmers-osu) corroborates its Google-track award. This establishes that result, not that it is necessarily the user's remembered event or an overall worldwide Google competition.

Its [Gemini service](https://github.com/chengenli9/BeaverHacks2026/blob/b6fd82531951434c47710f1ab512094c07df7151/backend/app/integrations/gemini/service.py) constrains plans/indexes using measured probes and shot indexes, validates structured results, measures narration and writes artifacts. A [bridge](https://github.com/chengenli9/BeaverHacks2026/blob/b6fd82531951434c47710f1ab512094c07df7151/backend/app/rendering/remotion_bridge.py) creates Remotion graphic blocks and FFmpeg composes them. A sample render exists in the tree; it was not executed or quality-reviewed here.

The useful distinction is between the [blind manifest critic](https://github.com/chengenli9/BeaverHacks2026/blob/b6fd82531951434c47710f1ab512094c07df7151/backend/app/prompts/blind_manifest_critic.md), which expressly cannot judge visuals/audio, and the [render critic](https://github.com/chengenli9/BeaverHacks2026/blob/b6fd82531951434c47710f1ab512094c07df7151/backend/app/prompts/render_review_critic.md), which receives actual media and goals. We should preserve that distinction: a coherent description is different from a video communicating it.

Its model policy distinguishes text/TTS/images and limits expensive retries, but demo fallbacks can use placeholders or omit narration. Our requested production should hold instead of calling a silent/placeholder result complete. No repository license was found; study the design pending reuse permission.

## YAAS: closest complete Python comparison, with media weaknesses

[pipeline.py](https://github.com/raunakpatil/youtube-agentic-ai-studio/blob/main/pipeline.py) connects actual research, script, stock, narration, render and review/upload stages. [Requirements](https://github.com/raunakpatil/youtube-agentic-ai-studio/blob/main/requirements.txt) use Google GenAI, network Edge TTS and pinned MoviePy1/NumPy1. The MIT [license](https://github.com/raunakpatil/youtube-agentic-ai-studio/blob/main/LICENSE) was read. This is a real single-PC pipeline comparison, not merely a coding-agent skill.

But [stock.py](https://github.com/raunakpatil/youtube-agentic-ai-studio/blob/main/video/stock.py) randomizes candidates and can broaden failed scene queries to generic fallback queries. That risks the irrelevant-photo problem already rejected. [creator.py](https://github.com/raunakpatil/youtube-agentic-ai-studio/blob/main/video/creator.py) has actual pans, section graphics and SRT overlays; decorative motion does not verify meaning.

[The scriptwriter](https://github.com/raunakpatil/youtube-agentic-ai-studio/blob/main/agents/scriptwriter.py) includes hook/open-loop/re-hook instructions and multiple visual queries. Test these as prompts; do not treat generic hype phrases as proven writing. [The Gemini client](https://github.com/raunakpatil/youtube-agentic-ai-studio/blob/main/agents/gemini_client.py) switches through models on errors/quotas and then other providers, with old hardcoded quota comments. Keep our explicit selected model, budget/cooldown and no-paid-fallback policy. Selectively adapt provider/UI ideas rather than migrate state/rendering.

## Automated Video Generator: a toolkit, not free intelligence

This MIT repo has many example operation/scene JSON files, caption styles, media providers and small independent operations. That can inform our reusable editing vocabulary. Its [Gemini instructions](https://github.com/itsPremkumar/Automated-Video-Generator/blob/main/docs/GEMINI.md) and [driver bridge](https://github.com/itsPremkumar/Automated-Video-Generator/blob/main/src/adapters/mcp/driver-llm.ts) explain that a host agent can drive the agent backend. No extra key does not mean no inference cost: a ChatGPT/Claude host consumes that allowance, which the user excluded.

[AI verification](https://github.com/itsPremkumar/Automated-Video-Generator/blob/main/src/agentic/ai/ai-verify.ts) can return no semantic judgement and fall back to signal checks. Its audio judgement can use transcript text rather than hearing the recording; that cannot establish music suitability or clipping.

[beat-sync.ts](https://github.com/itsPremkumar/Automated-Video-Generator/blob/main/src/agentic/plugins/audio/beat-sync.ts) contains an aubio loader returning dummy zero-valued audio; another path uses FFmpeg statistics, and several verification/render hooks remain partial. Do not copy that as proven beat-synced aura. Implement a real onset detector on an actual registered track, then test known transients. Read the code behind features rather than inheriting blanket guarantees from a verification document.

## Showrunner: its Gemini provider is Veo

[Package registrations](https://github.com/scrollmark/showrunner/blob/d9f01063d9dc103766757a4ceeb5a67537f788b1/pyproject.toml) make Anthropic the default planner, with OpenAI as an alternative. Gemini is registered under video, and [that provider](https://github.com/scrollmark/showrunner/blob/d9f01063d9dc103766757a4ceeb5a67537f788b1/src/showrunner/providers/video/gemini.py) invokes Veo. This is not a Gemini text-only stack.

Its [pipeline](https://github.com/scrollmark/showrunner/blob/d9f01063d9dc103766757a4ceeb5a67537f788b1/src/showrunner/pipeline.py) has checkpoints and bounded repair; its [Manim renderer](https://github.com/scrollmark/showrunner/blob/d9f01063d9dc103766757a4ceeb5a67537f788b1/src/showrunner/formats/manim_explainer/renderer.py) returns stderr for repair and checks an actual output exists. Scene refinement/export is useful. Replacing our queue just for equivalent checkpoints would duplicate working code.

## Other small or easily confused leads

- [NIMA](https://github.com/khozhaniyazov/nima_model): zero stars, Apache-2.0 read. Manim-focused project with narrated sample and documented scene streaming/layout checks. [Config](https://github.com/khozhaniyazov/nima_model/blob/main/config.py) defaults to OpenAI-compatible paid routes/fallbacks; direct free Gemini use was not established. Study layout risk checks and Windows render serialization. A generic successful fallback MP4 is not the requested explanation. Readme/config audited; no render execution.
- [LLM Video Maker](https://github.com/GoldLegendW80/llm-video-maker): 35 stars, MIT read. HTML/HyperFrames skill bundle, example videos/briefs, local Kokoro option and transcript-locked workflows. A coding host authors the creative project; an independent Gemini API orchestrator was not established. Useful brief/source/shot organization. README/tree/license inspected, underlying engine not benchmarked.
- [AI Video Factory](https://github.com/ersinkoc/AI-Video-Factory): 107 stars, MIT metadata. [Actual agent runner](https://github.com/ersinkoc/AI-Video-Factory/blob/main/packages/agents/src/runner.ts) uses Claude Agent SDK and documents subscription/API consumption. Gemini media support does not make its creative runtime Gemini-only. Useful state/media ideas, not our free runtime replacement.
- [NorthStar video solution generation](https://github.com/yashmote/Northstar-video-solution-generation): related BITS Goa repo found by the focused search. [Actual module](https://github.com/yashmote/Northstar-video-solution-generation/blob/main/eduvision_laptop.py) implements Gemini JSON→HTML/Playwright PNG→audio→FFmpeg. It imports `google.generativeai`, while [requirements](https://github.com/yashmote/Northstar-video-solution-generation/blob/main/Requirements.txt) list `google-genai`, a setup mismatch. Voice falls from ElevenLabs to flite to silence. Author/campus is public, but this is **not identified as the remembered Pokémon/resumed-work demo**. License not established.
- [Pokémon Natural Geographic](https://github.com/bhancockio/pokemon-ai-video-generator): 48 stars, no repository license found. Documented stack uses Claude Code, Gemini images, KIE/Kling video and ElevenLabs voice/SFX. Not free Gemini-only. Asset bibles, composition-before-motion and clear action prompts are useful ideas. Documentation only, no paid calls/code execution.
- [Gemini-Powered-Video-Generator](https://github.com/auzzton/Gemini-Powered-Video-Generator): zero stars. Package includes ElevenLabs, fal and OpenAI. README-linked `antoinekllee/VideoGen-gemini-hack` returned404. No top-level license found; app sub-license needs review. Some deeper requests timed out, so discovery lead only.
- [Pokémon sprites evolution timeline](https://github.com/ketanvelip/pokemon-sprites-evolution-timeline): one star. A particular Remotion animation and agent-skill folders, not proof of a generic independent generator. No source license found; artwork rights are separate. Metadata/tree discovery only.

## Other Google hackathon clues

[Felix Peng's project page](https://www.felixpeng.com/projects/youtube-ai-studio) and [launch post](https://www.linkedin.com/posts/felixpeng24_we-won-the-google-deepmind-hackathon-ucla-activity-7444556073358954496-6ZeG) describe a UCLA Google DeepMind winner using Gemini/Lyria. The project links [aarontzhang/yt-ai-studio](https://github.com/aarontzhang/yt-ai-studio) directly: an exact source linkage, not a similar-name guess.

Current source differs: [README](https://github.com/aarontzhang/yt-ai-studio/blob/main/README.md) requires OpenAI, Anthropic and Supabase; [package](https://github.com/aarontzhang/yt-ai-studio/blob/main/package.json) contains those clients. [geminiClient.ts](https://github.com/aarontzhang/yt-ai-studio/blob/main/lib/server/geminiClient.ts) exists for mood classification, so saying Gemini is absent would also be wrong. This is an editor for footage with Gemini as one component, not free Gemini-only topic-to-video. Its YouTube-style publishing screens include mock UI, not proof of official native integration. No repository license found. An independent organizer result for this team was not located; winning status here is attributed to creator materials.

[Official Kaggle Gemini3 winners](https://www.kaggle.com/competitions/gemini-3/hackathon-winners) are search-indexed with FlameEdit, by Muhammad Yousuf Noor. Readable page body, verified public source repo and an ordinal first-place claim were not established. Keep it as another lead, not the proven remembered winner. Exact BITS Goa identity is owned by the parallel focused search/report.

## Costs, licenses and a concrete experiment

[Google's API pricing](https://ai.google.dev/gemini-api/docs/pricing) separates text, image, speech and video models. Free text access does not imply free Veo/video. Google Pro browser allowance must not be treated as billing credit for an API repository. Use our confirmed unbilled project/allowed model/local budget; unavailable routes hold. Free code and no additional key do not guarantee free inference.

[Remotion's own license/pricing](https://www.remotion.dev/docs/license/pricing) and [terms](https://www.remotion.dev/docs/terms) govern its use, not a wrapper's MIT label. Individuals and qualifying small companies have a free license; company automation has separate terms. Check exact version/use before adding it. We do not need to buy Adobe or a video API to test a local parameterized scene.

Retain notices when adapting permissive code. For no-license repos, public visibility is not permission to copy implementation. Independently implement the patterns, choose licensed code, or establish permission; no author was contacted.

The next experiment should compare **one education scene adapter** against our existing renderer:

1. Supply a short factual script, actual evidence and one narrow visible result, such as a resume before/after or process explanation.
2. Keep the same accepted voice, narration and subtitles in both outputs so the comparison tests visuals.
3. Gemini chooses validated labels, positions, arrows/callouts and entrance times in trusted blocks; no arbitrary subprocesses/network/code.
4. Render frames and a scene; inspect whether visible objects communicate the narration and all text remains readable.
5. One bounded actual-frame critique/revision; preserve versions/timings and hold missing sources/unsupported edits.
6. Reuse the result as a normal asset in our FFmpeg pipeline. Try sandboxed codegen only if trusted blocks demonstrably cannot express the required scene.

Engineering estimate: 1–2 focused working days for one local scene/comparison, another 1–3 for a reliable visual-review loop/failure tests. Generated-code isolation, native dependencies and model adaptation are a separate larger spike. These are planning estimates, not measured delivery promises.

Acceptance: a saved request runs without ChatGPT; free-budget constraints hold; spoken words/unit/source identities survive; actual frames match the visual goal; invalid outputs/timeouts stop; repeat runs reuse verified artifacts. A compile, MP4, model score or star count is insufficient.

## Search and validation limits

Search families: exact BITS Goa/Gemini/Pokémon/LinkedIn, prompt-to-video/Manim/Remotion, official hackathon winners and small-repo discovery. Public metadata/trees, source modules, dependencies, license files and four default-branch commit records were inspected. The anonymous GitHub API limit was reached; no credentials, alternate accounts or quota evasion used. Known public code/raw pages supported later reads. 404/timeouts remain explicit rather than guessed away.

This is deeper code-backed discovery, not proof all14 repos run here or make audience-ready videos. No third-party example entered production. The most useful gains are bounded scene expressiveness, actual-frame review and better media matching.
