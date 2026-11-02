# Implementation plan: AI-operated two-channel production

Updated: 2026-11-01. This is the current build plan, adapted from the user's framework and the code that actually exists. It replaces the earlier editor-first work order. The owner is not the routine editor: software must research, write, prepare voice/media, compose, export and eventually publish. The browser is an optional inspection/control screen.

**Current boundary:** the compositor works with supplied local media and JSON jobs. Automated research, Gemini scripting, TTS, reference-style chat generation, production orchestration, publishing and analytics are still to build. Research markdown and agent role briefs are not running services.

Validation of the existing editor and new machine-result contract: **23 tests passed in 48.32 seconds** on 2026-11-01, including a real two-shot headless export, returned output-file verification, overwrite protection and structured missing-media failure. These checks do not certify the unbuilt modules below.

## 1. What is done and what is left

| Component | Actual status | What it already does / what remains |
| --- | --- | --- |
| Reference research and role briefs | Documents completed | Catalogs, sources, risks and inspected examples exist. No continuous researcher is installed. |
| Compositor | Implemented | Three supplied-media layouts, geometry/fit, borders/glow, timed effects/CTA, clip audio/music, 720p/1080p MP4, cover and technical manifest. |
| Programmatic editing interface | Implemented | JSON job plus local media paths can render through compose without browser clicks. The Python API is also available. |
| Machine-readable result | Implemented in this update | compose/render --json returns one JSON result on stdout; progress goes to stderr; ordinary failures exit nonzero with a structured error. |
| Editor persistence | Implemented, narrow scope | Saved projects and a single-worker export history use atomic JSON. This is not the full production database or scheduler. |
| Production foundation | Not implemented | Two channel profiles, SQLite records/events, stage scheduling, recovery, content hashes, provider settings and budgets. |
| Researcher | Not implemented | Collect and refresh topic evidence and candidate media/source leads. |
| Scripter / Gemini writer | Not implemented | Produce validated scripts, dialogue, edit intent and metadata from a brief. |
| Voiceover | Not implemented | Select a commercially usable voice, synthesize audio, measure timing and cache clips. |
| Chat/caption/visual preparation | Partial / not implemented | Older card recipes exist; the reference-style phone/chat generator, speech-timed captions and automatic visual preparation do not. |
| Asset/source manager | Basic import only | The Store copies/probes local files. Acquisition, eligibility records, attribution and expiry checks remain. |
| Production director | Not implemented | Bind actual files and measured timings into compositor jobs automatically. |
| Editorial/source/technical QA | Partial | Technical export checks exist. Full audio, factual, source, duplication and publication checks remain. |
| Packaging | Partial | Cover extraction exists. Automatic titles/descriptions, disclosure/attribution and optional designed thumbnails remain. |
| Publisher / supervisor / growth officer | Not implemented | No OAuth channel connection, uploads, incident notification integration or analytics loop is active. |

The six previous card/chat formats are preserved as legacy behavior. The default editor now uses actual supplied media and does not generate gameplay on startup. See [usage](../README.md), [architecture](../../PROJECT_GUIDE.md) and [the corrected visual reference audit](../references/COMPOSITION_REFERENCE_AUDIT.md).

## 2. What each module does

These are logical roles implemented as ordinary Python modules, saved artifacts and bounded AI calls. A multi-agent framework is not a prerequisite.

| Module | Its job in plain language | Input → saved output |
| --- | --- | --- |
| Channel head / growth officer | Chooses the next topics and series, keeps both channels coherent, and later uses actual results to propose changes. Initially uses the content catalog and experiment brief. | Channel profile, topic evidence, experiment history and available reports → editorial plan and candidate jobs |
| Researcher | Finds interesting topics, public reference examples and supporting facts. Records where each observation came from and when it was checked. | Search/feed seeds and channel brief → brief.json, sources.json and candidate-media leads |
| Source/asset manager | Separates a fact source from a file we may actually use; acquires eligible visuals/music and keeps provenance. Can select a segment from the owner's reusable gameplay batch. | Source profiles, candidate assets, local library → assets.json and local files, or a held reason |
| Scripter | Turns a selected brief into a hook, setup, progression and payoff. Writes spoken lines, fictional dialogue when relevant, visual requirements and packaging options. | Brief, supporting claims, format and channel voice → script.json |
| Voiceover | Reads the narration/dialogue through the selected TTS voice and measures the real duration of the result. Skips synthesis when a clip already supplies the intended speech. | Spoken units, pronunciation hints and voice profile → WAV clips, assembled narration.wav and timing.json |
| Chat/caption/visual builder | Converts approved dialogue into the compact phone/chat presentation, reveals/scrolls messages at the correct times, and prepares captions or original explanatory graphics as needed. | Script, timing, visual rules and eligible assets → chat.mp4, captions.srt, images/demonstrations and visual manifest |
| Production director | Makes concrete editing decisions: which file occupies each slot, which source range to use, where the crop goes, when the payoff effect fires and how audio is routed. | Real files, measured timing, template and edit intent → compose-job.json |
| Compositor | Executes the edit deterministically and exports files. It does not decide whether a factual claim is true or a song is licensed. | compose-job.json + local media → video.mp4, cover, project and technical manifest |
| Quality reviewer | Checks the actual result and its records. Finds technical errors, unsupported claims, unresolved sources, excessive similarity and missing disclosures. | Render + script + source/asset records → qa.json with pass, hold or failure reasons |
| Packaging | Selects an accurate title, description and cover; includes required attribution and disclosure information. | Finished video, script and channel style → metadata.json + cover/thumbnail |
| Publisher | Uploads the fixed approved version to the correct channel, checks processing and applies the allowed schedule/visibility policy. | Approved render/metadata and authorized channel identity → upload/session/video records |
| Production supervisor | Tracks stuck/failed jobs, disk/quota problems and available incident signals; pauses the affected work and alerts on meaningful changes. | Job events, expiry/status signals → incidents, retries/holds and notifications |
| Performance monitor | Collects supported owned-channel reports after publication and feeds observations back to the channel head. | Authorized reports at comparable observation windows → observations and experiment review |

The growth officer does not have competitors' private retention, impressions or earnings. Public examples generate hypotheses. The ordinary API is not a complete copyright-strike feed; supervision still needs the actual supported notices/Studio workflow described in the [supervision research](../sources-and-safety/STRIKE_PREVENTION_AND_SUPERVISION.md).

## 3. Two production routes, not one forced voiceover recipe

### Entertainment / brainrot

- **Chat over footage:** researcher identifies a premise/format; scripter writes an original fictional conversation; voice module optionally provides speakers; chat builder prepares the compact blue/gray phone presentation; director places it over an eligible footage segment; compositor adds selected music/effects.
- **Creator/podcast moment or aura-style edit:** source manager identifies eligible exact footage/time ranges. The original speech can remain; TTS is optional. Scripter proposes context, captions or a separate fictional chat setup where appropriate. The director keeps both layers readable and coordinates the payoff.
- **Movie/recommendation cards:** researcher supplies the selection criterion and facts; source manager resolves actual image/media eligibility; scripter writes concise reasons. Nine supplied picks plus a viewer-tenth prompt remains a supported concept, not a promise of ten supplied recommendations.

Generated gameplay is not the production default. The owner may supply a reusable gameplay batch; later automation selects segments from the stored library. Unknown media is not made eligible merely by adding a gameplay layer.

### Education / productivity

- Researcher finds a dated useful topic and primary evidence: study methods, practical AI use, confidence, jobs/skills or a real documented success journey.
- Scripter gives it one concrete angle, short spoken units and a real takeaway, with claim references.
- Voice module narrates it; visual builder prepares actual diagrams/screenshots or recordings of demonstrated tasks.
- Director selects an appropriate layout and resolves timing; compositor renders it.
- Job/earning claims require current geography/eligibility details; success examples do not become fabricated testimonials or universal earnings promises.

Both routes are shared infrastructure with separate channel profiles, assets, editorial history and later account identities. Start US-first English as the existing experiment; additional languages follow voice/font/pronunciation and localization checks.

## 4. How the AI controls editing

~~~text
Natural-language brief
        ↓
Research evidence + selected format
        ↓
AI script and structured edit intent
        ↓
Voice/visual tools produce actual files and measured timings
        ↓
Director resolves intent into a supported compose-job.json
        ↓
Compositor validates inputs and exports automatically
        ↓
Machine result + technical/editorial/source checks
        ↓
Approved packaging → later publishing → observations
~~~

The AI can request a layout, crop, border, music level, shot sequence and an effect on a particular reply. It cannot invent an input file, an unsupported editing operation or exact speech timing. For example, it may request a punch on reply_05; the director resolves that to the measured end/start of the corresponding audio unit. The renderer never executes AI-written shell commands or arbitrary editor code.

**Already runnable machine interface:**

~~~powershell
python run_editor.py --data data/editor compose job.json --output data/editor/exports/job-001.mp4 --json
~~~

The caller receives a JSON result with status, dimensions/duration and absolute paths for video, cover, captions, project and manifest. Progress uses stderr. On ordinary input/render failures, status is failed and exit code is nonzero. The caller must check both exit code and result. Invalid command-line syntax still uses argparse's standard error/exit code; hard process termination may yield no result.

Use the [example composition job](../../examples/composition-job.example.json). It references intentionally missing user files until a producer supplies them. A saved layout JSON can replace the preset name. Multiple shots may override their input paths and timing. The existing Python materialize_job and render_project interfaces avoid subprocess parsing entirely when called by the same application.

## 5. Contracts between the modules

All contracts are versioned, tied to a channel/job ID and written atomically. Their proposed fields are not an implemented production database.

- **brief.json:** topic/viewer question, discovery timestamp, language/audience hypothesis, reference URLs, evidence locations, factual claims, uncertainty, source freshness and proposed angle.
- **script.json:** hook/payoff, spoken-unit IDs/text/speaker, dialogue IDs and fiction status, claim/source references, visual requirements, optional clip ranges and edit intent. Separate factual assertions from jokes, opinions and fiction.
- **assets.json:** actual file ID/path/checksum, owner/source URL, acquisition route, evidence date, allowed use, attribution, expiry and eligibility state. A URL or manifest row alone is not proof of permission.
- **timing.json:** voice-model/version/license reference, spoken text hash, sample rate, measured unit duration, timeline start/end and pronunciation notes.
- **visuals.json:** generated/imported file references and which timed units or message states they represent.
- **compose-job.json:** one concrete supported layout, existing input paths, source offsets, measured shot durations, audio selection and exact effect/CTA times.
- **qa.json / metadata.json:** separate technical/editorial/source outcomes, title/description/cover, attribution, disclosure decision and unresolved items.
- **upload / observations:** resumable session/video ID, authorized channel, fixed content version, visibility/processing state; later official metric definitions/windows and missing-data markers.

Changing script/voice/media invalidates the corresponding downstream files and approval. Cache keys include input hashes, model/prompt/voice/template versions and relevant settings. The production database stores state/artifact references; large media stays on disk.

## 6. Technology and changes to the supplied framework

| Choice | Reason and tradeoff |
| --- | --- |
| Existing Python compositor and plain browser inspector | Reuse the working media engine. Do not rebuild it in another dashboard framework. Browser interaction is optional. |
| SQLite for production records, JSON for artifacts | The future pipeline needs transactional stages/events and recovery. The current editor's atomic JSON export history remains a narrow component; it is not silently treated as the full queue. |
| Gemini free-tier writer adapter | Structured generation is suitable for scripts/edit intent. Exact free model/tool combination and access are checked at setup; a valid JSON response is not necessarily factually correct. |
| Local Piper voice adapter, conditional on a usable model | Avoids per-video API charges and owner recording. Exact voice license, naturalness and installation compatibility must be established; Piper being available does not clear every voice. |
| FFmpeg + Pillow | Existing media rendering/probing, simple graphics and chat-frame preparation. More elaborate motion design may later use a native editor backend. |
| One heavy media stage at a time | Fits the observed roughly 16 GB RAM machine. Network/provider waiting should release the worker slot rather than freeze unrelated jobs. Benchmark before enabling heavier parallel tasks. |
| Optional Adobe/Resolve adapter | Only if a proven visual requirement needs it. The user owns these tools but does not require their use; no bridge is implemented. |

Specific corrections to the framework:

1. **Keep the current editor and JSON adapter.** Its source structure is the starting point; there is no need to recreate an editor folder tree or a second Streamlit interface.
2. **Validate timing from audio.** Initial captions follow measured sentence/phrase clips. Splitting a longer spoken clip into several text phrases does not reveal their true timings. Word highlighting needs alignment or genuinely separately generated phrases.
3. **Generate natural spoken units.** Avoid forcing every few words into an independent TTS call merely to obtain timings; this can damage prosody. Compare full sentences and short dialogue turns in the voice proof.
4. **Use each voice track once.** Chat can carry its own speech, or use global narration; do not mix the same voice in both. Creator clips can keep their own speech without synthesized replacement.
5. **Do not loop speech accidentally.** The current compositor loops short video inputs. The director must ensure foreground speech covers its assigned shot, or an explicit future freeze/mute policy is required. Looping background gameplay/music is separate.
6. **Publication checks sit above the renderer.** The renderer verifies technical inputs; the production workflow checks source/editorial conditions and authorization before outbound use. A local test export does not become a publication approval.
7. **Uncertain uploads are reconciled.** Persist the resumable session URL before bytes, then recover its status after a lost response. A returned video ID alone cannot handle a response that never arrived.

Current primary references: [Gemini structured output](https://ai.google.dev/gemini-api/docs/structured-output), [free/paid model and tool pricing](https://ai.google.dev/gemini-api/docs/pricing), [project-level limits](https://ai.google.dev/gemini-api/docs/rate-limits), [Piper Python API](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md), [voice model licenses](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md), [YouTube resumable upload protocol](https://developers.google.com/youtube/data/guides/using_resumable_upload_protocol).

## 7. Implementation order and completion checks

This is the next work order, not a claim that the modules below already run. Milestones have observable outputs instead of a guaranteed completion date.

| Order | Work | Done when |
| --- | --- | --- |
| P0 — machine editor | Existing compositor plus a structured CLI response | Completed: a program submits a two-shot job, receives valid output paths, and gets a structured failure for missing files/overwrite attempts. |
| P1 — production records/contracts | Two profiles, versioned brief/script/timing contracts, SQLite migrations/events, fake providers, restart handling and explicit publication mode | Jobs can persist/resume local stages; profiles remain separate; no credentials are required for the fixture path. |
| P2 — voice proof | Select eligible English voice, isolate compatible runtime if needed, synthesize a known script, cache units and measure WAV timing | A real audible sample has acceptable pronunciation/prosody, license evidence and duration records; missing model/silence/clipping are handled. |
| P3 — scripter | Gemini adapter, prompts, structured output, evidence references, limits/retry/cache and duplicate checks | A saved sourced brief produces a validated original script; malformed response/unknown claim IDs/quota exhaustion cannot move it forward incorrectly. |
| P4 — live researcher/source records | Supported public YouTube API observations, permitted feeds/pages and source refresh; use existing catalogs as first-run leads | Finds actual dated briefs and media leads with evidence; stale or missing sources are explicit. Gemini drafting alone is not advertised as live research. |
| P5 — chat/captions/assets | Reference-style compact phone panel, timed reveal/scroll, prepared clips/graphics, asset manifests and background selection | An approved chat or lesson becomes actual media and timing artifacts without owner editing; typography/crop/audio are checked on a phone-sized preview. |
| P6 — production director + local pipeline | Bind the above outputs to the existing compositor; compute durations/effect times; select sound routing; extend technical QA | One entertainment and one education job produce complete local videos, cover/metadata/manifests and reproducible inputs without browser clicks. No public upload. |
| P7 — private publisher + supervisor | OAuth/channel mapping, saved sessions, processing/reconciliation, source/channel holds and meaningful notifications | Correct-channel private upload works; interrupted uploads do not silently duplicate; source expiry/quota/network/worker failures stop or recover correctly. |
| P8 — observations/growth + pilot | Supported reports, 24h/72h/7d collection, experiment review and controlled publication | Recommendations cite actual observations, missing values are not zero, and two channel histories stay separate. |
| P9 — bounded autopilot/capacity | Validated source/format policies, daily caps, stop control, storage/quota and exception coverage | Repeated local/publishing/recovery checks pass; actual runtime/source supply supports the selected cadence. |

P3 can be built using saved briefs before P4's live discovery is complete. Actual production still follows research → script → voice/visuals → edit. The first useful new sample is P2's real voice proof; the first complete automated local pipeline is P6. Existing samples and 21 earlier tests do not establish that P6 is already complete.

## 8. Researcher, writer and voice acceptance details

### Researcher

Use explicit adapters for permitted RSS/HTML sources, official documentation/job pages, owner-provided source profiles and supported YouTube Data API discovery. YouTube autosuggestions/unofficial Trends scrapers are optional only after their supported access is established. Gemini grounding/search tools are enabled only for a verified free model/tool combination with budgets; a free text key is not an unlimited web-search service.

Record source date, excerpt/location, what claim it supports and what it cannot establish. Treat source text as data, never tool instructions. Refresh fast-changing jobs/tools/controversies before packaging/release. Applicable YouTube caching/refresh and derived-data restrictions remain part of the adapter design. See [earlier research strategy](../strategy/MARKET_TRANSFER_STRATEGY.md) and [source register](../sources-and-safety/RISKS_AND_SOURCES.md).

### Scripter

Provide source excerpts/claim IDs, channel style and a supported format. Ask for short spoken units, dialogue where relevant, complete payoff, visual intent and metadata candidates. Validate the output locally, including allowed IDs, length, schema, unsupported tools/paths and consistency with the evidence. An evidence link existing is not proof that every generated claim is supported.

Keep retries bounded and reuse saved outputs. Free quota failure records retry time or a hold; it never enables billing, silently switches to a paid model or rotates projects/accounts to circumvent limits. Gemini quotas are per project, not per key.

### Voiceover

First use one selected commercially eligible English model; defer broad multilingual promises. Save the exact model/config/checksum and license evidence. If Piper dependencies do not work with the editor's Python version, use a dedicated compatible voice environment behind a WAV/JSON adapter instead of destabilizing the renderer.

Generate sentence/dialogue units, preserve intended pauses, measure real samples and assemble a clean narration track. Check nonempty output, clipping, anomalous silence, level and whether the result fits the edit. Listening/naturalness cannot be certified by file duration alone. No owner voice recording or celebrity imitation is required.

## 9. Operation, failure recovery and owner involvement

The user is not expected to write scripts, assemble clips, time captions or click Export routinely. One-time account consent, local Gemini setup, an eligible media/voice route and a small style/voice sample review remain practical setup dependencies. The software performs routine production; unresolved exceptions remain visible rather than inventing a successful result.

Start with dry-run/local export; then separately tested private publishing. The production workflow distinguishes proposed, researched, scripted, media-ready, rendering, checked, review-ready and approved publication versions. A local render success cannot set published. Keep stage-specific bounded retries, artifact hashes, a durable event log and an upload reconciliation state.

A running job can fail or be interrupted. The controller checks exit code, complete manifests and actual output files; missing/partial results are not success. Reuse saved research/voice/media after a downstream failure. Keep original evidence before storage cleanup. No complete claim/strike API feed or automatic legal dispute handling is promised.

The owner's target of four to five videos per channel per day is a capacity goal after pilots, not a starting throughput guarantee. Benchmark actual generation, media preparation, rendering, upload, storage, free quota and exception load before increasing volume. Local work stops when the PC sleeps; already scheduled uploads have separate YouTube-side behavior. A verified free always-on cloud renderer has not been established.

## 10. Immediate deliverables

1. Produce a durable local job with a saved brief/script contract and two separate channel profiles.
2. Establish a real licensed voice proof and measured timing.
3. Connect a validated Gemini script from a saved brief.
4. Automate the reference-style chat/visual layer and direct its real files into the compositor.
5. Add live discovery, quality/packaging, then private publishing/supervision and the learning loop.

No API keys or OAuth credentials were requested or used while updating this plan. The researcher, scripter and voiceover are explicitly still proposed; this update implements the machine-result interface and documents their concrete responsibilities and completion checks.
