# YouTube automation: project guide

Updated: 2026-11-01. **Implemented:** a supplied-media Shorts compositor with three new layouts, reusable layout/JSON-job binding, borders/glow, timed effects/CTA, selected clip audio/music, real exports, saved projects and an export queue. The previous six card/chat recipes are preserved as legacy behavior. **Still proposed:** automated research, script/voice generation, source clearance, publishing, supervision and growth analytics. No external accounts, keys, source-video downloads, uploads or recurring automations were activated. Start with [usage](../README.md), [reference audit](../references/COMPOSITION_REFERENCE_AUDIT.md), and the broader [implementation plan](../../docs/archive/IMPLEMENTATION_STATUS_EARLIER.md).

## Current production-module work order

The [implementation plan](../../docs/archive/IMPLEMENTATION_STATUS_EARLIER.md) is now a current status inventory plus the P0–P9 work order, adapted from the user's framework. It explains each role's input, work, output and completion check. The owner is not the routine editor: the production program must operate the existing compositor through its JSON/Python interface. A separate automatic chat/visual builder must supply the prepared foreground, and a director must compute actual timing/audio routing before export. These modules are not yet implemented.

This update adds **machine-readable CLI results**: `compose --json` and `render --json` emit a single versioned result on stdout, with complete output paths/duration/dimensions, while progress uses stderr. Ordinary failures return a structured error and nonzero exit code; a hard process kill can leave no result. Output existence is checked before job import, and the renderer still protects existing finished MP4s. The controller must inspect exit status/result/artifacts; AI prose alone is not a completion signal.

Reason for this addition: the program needs a stable handoff without interpreting browser UI or human progress strings. The existing same-process Python API remains preferable when the production modules share a process. New end-to-end tests submit a two-shot JSON job through the actual CLI, verify returned files, reject an overwrite and check missing-media failure. No Gemini key, TTS model or source service was installed or activated in this update.

Validation for this update: the full suite passed **23 tests in 48.32 seconds**. The two added CLI integration tests passed independently as well; local links in the revised plan, guide and README were verified. Earlier 21-test results below describe the preceding compositor milestone.

Next implementation priorities: durable profiles/job records and contracts; an actual eligible voice proof; the validated scripter; supported live research/source adapters; reference-style chat/caption/visual preparation; the automatic director and two local channel samples. Publishing/supervision/analytics follow those proofs. The earlier generic Streamlit/scaffold plan is not an instruction to rebuild the working editor.

## Implemented editor: architecture and flow

The user clarified that the first editor missed the intended format: the program supplies actual clips/screenshots/music to a 9:16 composition, rather than accepting generated gameplay and large invented chat/headline cards. The user supplied a Dozzek Short as a direct style reference and rejected the repeated green/charcoal UI. The current default is a neutral light media-slot inspector with no automatic demo generation. No matching palette directive was found in the inspected local custom skills, memories and global AGENTS instructions, so no unrelated skill was deleted. These are recorded corrections, not audience-performance conclusions.

The user has Premiere Pro, After Effects and Resolve Studio available, but clarified that using them is optional; output quality and automation suitability determine the backend. The first corrected renderer uses FFmpeg for fixed slots/basic effects. Adobe/Resolve scripting/render bridges are researched options, not implemented dependencies. No native application project or preferences were changed. See the [direct observations and app capability notes](../references/COMPOSITION_REFERENCE_AUDIT.md).

```text
Browser controls -> loopback HTTP API -> validate version-1 project JSON
                         |                         |
                    imported asset Store      saved projects
                         |                         |
                  Pillow overlays + FFmpeg <- single export worker
                         |
                  MP4 / cover / SRT / recipe / technical manifest

Automation JSON + local media -> jobspec.materialize_job -> validated project
                                                        -> render_project -> same files
```

| Implemented component | Responsibility and reason |
| --- | --- |
| `models.py` | Three composition presets plus six legacy definitions, editable geometry/effect settings and bounded validation. |
| `composition.py` | Supplied-media placement, aspect-preserving foregrounds, blurred fill, borders/glow, timed punch/flash/shake and an optional sliding CTA. No chat or footage generation. |
| `jobspec.py` | Binds a preset/saved layout to local input paths and shot timing, imports those files into the Store and validates them. This is the program-facing JSON adapter. |
| `store.py` | Copies imported media into an asset registry, probes it and saves projects atomically. Asset IDs avoid arbitrary browser-supplied filesystem paths. |
| `graphics.py` | Legacy card/chat drawing and shared text fitting; the new compositor does not add its chat bubbles or headline cards. |
| `render.py` | Shared FFmpeg layout, crop/fit, looping, optional source/voice/music mix, encoding, technical checks and export companions. Its Python API and CLI work without a browser. |
| `server.py` | Loopback HTTP API, media streaming, preview serialization and one export worker. Job JSON persists progress and completion; an unfinished job becomes interrupted after restart. |
| `web/studio.*` | Default media-slot inspector, layout controls, still preview, saved projects and playable exports. `index.html`/`app.js`/`style.css` remain the legacy UI at `/legacy`. Neither requires a frontend build system. |
| `demo.py` | Synthetic test/demo generation remains available only through explicit commands; startup does not invoke it. Prior generated assets remain on disk and are hidden from normal new-slot choices. |
| `cli.py`, `run_editor.py`, `start_editor.cmd` | Launch the UI or render headlessly. `compose`/`render --json` return a machine-readable result with separate progress/error handling. The Windows launcher prefers a local virtual environment when present. |

Important technology decisions:

- **Python + FFmpeg + Pillow:** CPU rendering and compositing with one Python package dependency. Compared with MoviePy, direct FFmpeg commands expose encoding/filter behavior and retain useful failure logs, at the cost of more explicit filter construction. GPU acceleration is not required or configured.
- **Plain browser UI + Python standard-library server:** chosen for this separate narrow editor instead of the earlier proposed Streamlit dashboard. It gives direct control over media import, scene controls and export playback without adding a dashboard framework. This is a single-user localhost server, not authenticated cloud hosting or a production internet server.
- **Atomic JSON + local files:** adequate for this standalone single-worker export queue and easy to inspect. This does not implement the planned transactional SQLite production queue, multi-machine leases, automatic resume or publication approval history. Interrupted renders are restarted as new jobs.
- **Shared slot/filter logic:** previews and exports use the same media geometry and effects. A 360×640 still preview is cheaper than real-time full-resolution playback. The new compositor preserves a supplied foreground's aspect ratio without an opaque padded card. CTA graphics and legacy cards use PNGs; foreground dialogue is not generated or transcribed.
- **H.264/AAC MP4:** conventional playable output at 720p or 1080p, 24/30 fps. Each scene renders separately, then joins and mixes audio. This retains intermediate files for diagnosis and uses more disk space than a cleanup-first pipeline.

Request/data flow: importing a file copies it into `data/editor/assets`, verifies it with Pillow/ffprobe and returns an ID. Scene controls assemble a project referencing those IDs. Saving writes normalized JSON. Preview requests render/cache one still. Export submission snapshots the project into a durable job record; one worker renders its scenes, joins them, mixes audio, verifies dimensions/duration, and exposes successful files for download. Failed or cancelled jobs retain their reason/logs; incomplete output is not offered as complete. A browser session token plus Host/Origin checks restrict mutations; the service binds only to `127.0.0.1`. There is no outgoing network activity in this editor.

Current presets: **chat over footage** (compact supplied chat/screenshot over a full-frame clip), **two blocks** (top/bottom supplied clips), and **clip on blurred fill** (a sharp copy over blurred full-frame media). Optional borders/glow and timed punch/flash/shake/CTA are controls, not claims that effects improve views. The direct Dozzek reference starts with effects/CTA off. Legacy story, split, chat, list, explainer and punchline recipes remain available at `/legacy` and through the API/CLI, but are not the default style.

Browser layout export clears media references; project export preserves workspace asset IDs. The `compose` CLI accepts a preset name or layout file, actual local input paths, audio and optional shot sequence, then calls the same renderer as the UI. Paths resolve relative to the job JSON. No downloader is implied. Changing static screenshot states uses separate shots; a supplied chat recording carries its own reveal timing. Entire projects remain limited to 180 seconds and 30 shots. New composition shots can use the full 180 seconds. Preserve the full data folder when moving saved projects.

Validation now includes the three new compositions and six legacy formats, full MP4 decoding, pixel checks for slot placement and non-opaque contain behavior, timed effects/CTA, selected audio-track frequency, layout rebinding, invalid/missing inputs, restart/cancellation and local HTTP isolation. The browser imported two explicit technical test clips and exported a 1080p composition with a border, punch effect and CTA; the headless `compose` CLI also exported a real MP4. Solid-color fixtures check mechanics, not convincing gameplay or production aesthetics. Final visual tuning still needs actual supplied source media.

Earlier milestone checks on 2026-11-01 passed 11 legacy integration tests. Final compositor verification passed **21 tests in 41.37 seconds**, JavaScript syntax, Python compilation and a wheel build including the new UI/adapter. Browser checks included two imports, clip-length timing, a 1080p export with a border/punch/CTA, draft recovery and a clean New action. Legacy samples remain under `data/editor/examples`; explicit compositor QA fixtures/CLI output and `compositor-ready.jpg` are under `data/editor/qa`. These artifacts are ignored. Tests used Python 3.14.3, Pillow 12.3.0 and FFmpeg/ffprobe 8.1.1 on Windows; other OS/version combinations are untested.

Current limitations: no script/voice/chat-recording generation, footage discovery/downloading, rights certification, publishing, analytics, arbitrary layer timelines/keyframes, beat detection/cross-shot transitions, automatic voice ducking, speech alignment, automatic disk cleanup, native-editor bridge or verified multilingual font coverage. Basic timed slot effects and a CTA entrance are implemented; they are not full motion-design tooling. A technical render does not certify rights or monetization. The next integration should bind real eligible inputs to these layouts rather than duplicate the renderer.

## Purpose and recorded requirements

Build a system that researches video opportunities, prepares scripts and visuals, edits videos, prepares packaging, publishes, monitors production and channel performance, and proposes improvements. Use free software, genuinely free API tiers, and existing hardware. Agents handle permission research, scripts and editing. The user later offered a reusable gameplay recording batch; ongoing filming is not required.

Start with Shorts and support two independently managed channels:

1. Entertainment: the user's “brainrot” channel, potentially featuring authorized creator, podcast, streamer, and show clips, humorous editing, or system-generated original comedy.
2. Education/productivity: research earning money, confidence, procrastination, effective study, good jobs, AI usage, free AI, AI tools, and related useful topics. The user requested this broader catalog; a narrower initial series is a recommendation to test, not a settled restriction.

The latest audience preference is US-first English, with comparison against other English-speaking audiences as a proposed experiment. Program/payout research uses an India-operated scenario; target audience and creator eligibility are different. Multiple languages are a future capability, not an initial requirement to publish each video many times. Revenue, growth, monetization approval, and unlimited free service availability are not guaranteed. See the [US-first revenue plan](../strategy/US_FIRST_REVENUE_PLAN.md).

The broader production architecture and rollout decisions below are proposals except for the implemented editor above. Rationale is design judgment unless explicitly identified as a recorded user requirement. The user explicitly requested research agents, and three researchers were delegated independent workstreams. Saved role briefs describe repeatable responsibilities; they are not an installed agent runtime or a recurring service.

The user wants material risks disclosed and will decide which risks to accept. Keep high-risk formats visible, separate platform rules from project recommendations, and record later explicit choices with their actual scope in the [decision ledger](../strategy/DECISIONS.md). Welcome-clipping sourcing and incident supervision are now selected directions, with game/music permissions still unresolved. Interest in a format or a proposed mitigation is not blanket risk acceptance or third-party permission.

## Latest operating choices and researched corrections

The user is willing to supply gameplay recordings; routine writing/editing and permission research remain system responsibilities. The provisional visual recommendation is clean parkour/obby-style footage, compared with an endless-runner or simple obstacle/racing background, after exact publisher/experience checks. No evidence establishes a universally highest-view game. User-recording avoids copying another recorder but does not remove publisher or soundtrack rights.

Selected direction: Gemini free API, potential free-cloud operation, incident notifications, periodic owner checks and an eventual target of four to five videos per channel per day, possibly nine to ten later. These targets supersede the earlier low-cadence suggestion as the user's capacity goal, not as a validated starting commitment. Keep a small production/measurement pilot before scaling. The free-cloud option is unimplemented; sleep, persistent storage, render capacity, account/payout access and quotas need testing. The local renderer remains the proposed baseline until a suitable alternative is demonstrated.

Gemini quotas are per project, not per key. Use retry/backoff, caching/batching, queued jobs or a verified local fallback; do not rotate projects/accounts to circumvent limits. Native Shorts music selection is a separate creation/licensing route from burning an arbitrary downloaded song into an API-uploaded video. Genre labels such as phonk do not establish a license.

The supervisor proposal uses available authenticated API signals plus Studio/official notices; the ordinary API does not establish a complete claims/strikes feed. Pause affected jobs/sources, notify the owner, preserve evidence and update actual source/asset rules. Do not assume deletion resolves an issued strike, or automate legal counter-notifications. A normal API key is not private-channel/OAuth authorization. No monitoring or messaging integration is active. [Detailed source matrix, incident flow and primary sources](../sources-and-safety/STRIKE_PREVENTION_AND_SUPERVISION.md).

Educational content now explicitly includes real success journeys researched from interviews, posts and reporting (EDU-F12 variant). Label self-reported claims, separate takeaways from universal promises, and treat the person as a case-study subject rather than an ambassador. Preserve strong truthful hooks and distinct episode substance. No fabricated vacancies, income outcomes, testimonials or first-person experiments are part of production. Cosmetic panel rearrangement alone does not establish originality/monetization eligibility; R4 and R8 are explained in the update.

## Content strategy

### Entertainment channel

Treat this as a coherent entertainment brand. The latest editor direction is supplied-media composites, anchored to the user's Dozzek chat-over-footage reference. Original storytime and other catalog formats remain content possibilities, rather than requirements that the editor invent gameplay or dialogue. Fictional material should be identified as fiction; a technically rendered phone panel is not evidence of a real private exchange.

An earlier feasibility prototype generated a procedural obstacle animation. The user rejected that as the intended production background; it is now explicit test/demo material only. Production compositions consume actual supplied footage. For recorded gameplay, verify the particular publisher's commercial video permissions and acquisition method. A public story or narration is not automatically licensed for adaptation.

Other possible series are creator-moment explanations, podcast claim breakdowns, comedy edits of specifically licensed footage, and original absurd mini-stories generated by the system. Test a coherent series before mixing all these formats. Do not assume an unrelated gameplay layer, subtitles, zooms, famous music, or a humorous caption supplies sufficient originality or rights. Each story needs distinct substance and a complete payoff; template-driven mass production still presents monetization risk.

The user also requested movie-poster/GIF verdict edits and a nine-movie list with the tenth invited from comments. These remain distinct research formats, including the minimal-caption and reasoned-curation variants. A proposed list Short supplies nine complete picks and accurately invites the final one; it must not promise ten supplied recommendations or invent viewer comments. All movie/poster/GIF/music and commercial data-source rights remain separate research questions. See [E15/E16 in the entertainment catalog](../formats/entertainment/ENTERTAINMENT_FORMATS.md).

Mystery/conspiracy and controversy/gossip are also requested research formats (E17/E18), including higher-risk speculation and rumor variants. Agents can use news/chitchat feeds as discovery leads and produce original scripts/graphics; source research does not necessarily require acquiring creator footage. Keep confirmed events, allegations, rumors, opinions and fiction distinct. The user has not accepted specific risk exposures. [Supplement](../formats/entertainment/CONTROVERSY_AND_MYSTERY.md).

Cross-market adaptation is a requested channel-head strategy: find observable format traction, check destination competition, then produce an original localized episode. Region/language labels are not proof of viewer geography and an English example is not automatically a US opportunity. [Market-transfer research](../strategy/MARKET_TRANSFER_STRATEGY.md).

Clipping is a possible business model, but two income paths must remain separate: campaign compensation for approved promotional clips, and YouTube Partner Program earnings. Success in one does not establish eligibility for the other. A campaign may also require a particular channel niche, geography, disclosure, or editing style; do not mix incompatible campaigns just because their footage is entertaining.

### Education channel

Recommended pilot: short demonstrations and researched explanations about useful digital skills, portfolio projects, and misleading job/earning claims. Examples are a real before/after spreadsheet task, a small portfolio artifact, or an explanation of an officially documented job-scam pattern. These are episode ideas, not completed tests or evidence of audience demand.

The system can create diagrams, motion graphics, and recordings of workflows it actually executes with synthetic demonstration data. The user need not film anything. Never fabricate first-person experiments, earnings, employers, vacancies, hiring outcomes, credentials, or testimonials. Date job sources and verify geography and eligibility before mentioning an opportunity. [FTC job-scam guidance](https://consumer.ftc.gov/articles/job-scams).

### Retention and languages

Proposed Shorts structure: establish a clear question immediately, advance the story through meaningful visual changes, then deliver the promised answer or joke. Duration should follow the material; start with roughly 20–50 seconds as a production experiment. Avoid filler and false cliffhangers.

Initially use one language that can be quality-checked. Localize successful formats only after testing pronunciation, translation, and cultural context. Where available, multilingual audio can keep versions on one video; regional stories may justify separate language channels. Studio steps remain necessary unless a supported integration is verified. [YouTube multilingual features](https://support.google.com/youtube/answer/13338784?hl=en).

Assess actual audience geography and creator earnings after monetization; language alone does not establish revenue. CPM concerns advertiser spend, while RPM concerns creator revenue per thousand views, with different view bases for Shorts and regular videos. [YouTube revenue metrics](https://support.google.com/youtube/answer/9314357?hl=en).

## Source research and permission register

Public pages checked on 2026-11-01. These findings are leads, not a blanket license or confirmation of account eligibility. Recheck before each use.

| Candidate | Evidence found | Present limitation / next verification |
| --- | --- | --- |
| MrBeast | Vyro's own homepage lists a MrBeast campaign | Homepage marks it locked for new posts; full brief was not readable through the public app page. Do not activate. |
| Hulu: The Mob | Public Vyro campaign listing | Need specific brief, allowed episodes/assets, eligibility, disclosures, and automation permission. |
| Hulu: Phony | Public Vyro campaign listing | Same verification; listing does not authorize other Hulu shows. |
| iHeartPodcasts: Joy 101 | Public Vyro campaign listing | Podcast lead only; obtain the exact campaign brief before using any footage. |
| IShowSpeed × Expedia | Organizer's detailed brief plus Content Rewards listing | Rewards listing shows paused and exhausted budget; do not treat as an open earning opportunity. |

Sources: [Vyro homepage](https://vyro.com/), [campaign directory](https://vyro.com/campaigns), [Speed campaign requirements](https://reachclipping.com/Expedia-Speed), [rewards campaign status](https://contentrewards.com/c/campaigns/03bda4fd-3474-4b1e-a914-88aaf3ac8372).

Speed's documented campaign covers a specific segment, specifies an English-speaking audience and minimum views, and disallows AI-generated videos. This is evidence of a limited campaign, not permission for his entire archive. The organizer's general page says live while the rewards listing says paused; use the restrictive status until reconciled.

Vyro permits campaign participation subject to its terms and briefs; eligibility, content rights, compensation, and persistence obligations need review. Its content rules restrict unauthorized automation and automated promotional posting. No supported automation API was verified. Do not scrape the service, automate participation, or imply an integration exists. [Creator terms](https://vyro.com/clipper-terms), [content requirements](https://vyro.com/content-requirements).

MrBeast's historical encouragement of reposting was reported publicly, but a current universal license covering every video, commercial reuse, and embedded third-party material was not established. No universal IShowSpeed permission was established either. For each podcast or creator, research owner-controlled terms rather than relying on fan accounts or “no copyright” compilations.

The proposed rights register records owner, exact asset, permission evidence and date, allowed platforms, commercial use, editing/translation rights, music coverage, attribution/disclosure, expiry, acquisition route, campaign eligibility, and automation permission. Unknown permissions block that asset. Keep these records separate from temporary YouTube research caches.

## Monetization and publishing safeguards

YouTube distinguishes reused-content monetization rules from copyright. Permission alone does not qualify minimally changed clips; repetitive or mass-produced material is also a concern. Meaningful original narration, analysis, storytelling, or substantial editing must be assessed in context. No numerical “safe clip length” is assumed. [Monetization policies](https://support.google.com/youtube/answer/1311392?hl=en).

Check community rules, advertiser suitability, audience designation, rights, claims, and accurate packaging separately. Reject deceptive earnings claims, impersonation, artificial engagement, and mass uploads of near-duplicates. [Spam policy](https://support.google.com/youtube/answer/2801973?hl=en), [advertiser guidelines](https://support.google.com/youtube/answer/6162278?hl=en).

Keep a record of the AI disclosure decision. Realistic synthetic scenes, people, events, and relevant generated audio may require disclosure; drafting assistance has different treatment. [AI disclosure rules](https://support.google.com/youtube/answer/14328491?hl=en).

Default music source: a small pre-cleared library acquired through YouTube Audio Library, with required attribution retained. Optional stock visuals: Pexels, respecting license restrictions and API attribution. Famous music is not automatically cleared by a creator's permission. [Audio Library](https://support.google.com/youtube/answer/3376882?hl=en), [Pexels license](https://www.pexels.com/legal-pages/license/), [API guidelines](https://www.pexels.com/api/documentation/).

Initial uploads should be private review copies. Automated technical checks cannot determine every rights or editorial issue. Proposed unattended mode is restricted to validated formats and sources; unresolved rights, policy changes, factual uncertainty, and service failures pause the affected job. If no human review is wanted, held jobs stay unpublished. This is a system design choice, not a claim that YouTube requires preapproval of every upload.

## Research agents and proposed production architecture

The implemented research layer consists of [reusable markdown role briefs](../../agents/README.md): entertainment researcher, education/productivity researcher, source/risk reviewer, and a coordinating research lead. The three research workstreams were run by delegated assistants during this chat. Separate files avoid competing edits and let the lead reconcile findings. Markdown retains visible reasoning and evidence without requiring API keys or a paid hosting service. The tradeoff is that these are instructions and research artifacts, not a standalone program that continuously runs agents.

For the later production system, the proposal remains one local Python application with separate modules and saved jobs. This makes failures, cost limits, and publishing decisions easier to trace. The modules below are broader planned responsibilities; the editor now implements media assembly and technical export checks only.

| Module | Input → output |
| --- | --- |
| Channel head | Channel brief, approved observations, experiment history → weekly editorial proposals and production allocation |
| Researcher | Search seeds, permitted feeds, primary sources → dated evidence-backed topic briefs |
| Rights/source manager | Candidate assets and terms → eligible asset manifest or blocked reason |
| Writer | Approved brief → original script, factual claim references, scene plan, title options |
| Producer/editor | Scene plan, cleared clips/graphics, voice, music → vertical render and captions |
| Packaging | Finished story → accurate title/description, cover frame, optional thumbnail |
| Quality checker | Render, sources, rights manifest → technical results and unresolved issues |
| Publisher | Approved render and correct channel identity → private upload, then authorized schedule/publication |
| Production monitor | Jobs and heartbeats → progress, failures, retries, quota/storage warnings |
| Performance monitor | Official reports and observations → channel-specific performance views and next hypotheses |

Flow: research → source verification → script → scenes/voice → render → checks → publication approval → upload/process/schedule → monitoring → next editorial proposal. A source or script change invalidates downstream approval. A render failure resumes at rendering; it must not rerun a completed upload.

Proposed job states: `idea`, `researching`, `rights_pending`, `script_ready`, `rendering`, `quality_check`, `review_ready`, `approved`, `uploading`, `processing`, `scheduled`, `published`, `monitoring`, plus `blocked`, `failed`, and `cancelled`.

## Technology choices and tradeoffs

| Technology | Purpose and reason | Alternative / limitation |
| --- | --- | --- |
| Python | Shared orchestration, API access, media tooling | TypeScript is viable but would add little to this first local media pipeline |
| Streamlit (earlier proposal) | Potential broader dashboard for jobs, sources and decisions | The implemented standalone editor uses plain HTML/CSS/JavaScript and a local standard-library Python server; reassess the full dashboard after testing |
| SQLite (production proposal) and local files | Future transactional pipeline jobs; media stays on disk | The editor currently uses atomic JSON job/project files and one worker; no distributed leases or automatic render resumption |
| FFmpeg | Deterministic assembly, cropping, audio mixing, captions, encoding | More complex motion design needs additional tooling; templates alone do not create original substance |
| Pillow / generated vector graphics | Thumbnails, diagrams, title cards | Generative image/video services are optional, not a guaranteed free dependency |
| Free-tier Gemini adapter | Script drafts and creative assistance | Only explicitly free model/tool combinations; model access and limits must be checked at setup |
| Local Ollama adapter | Continue text work without cloud quota | Choose a commercially usable model and benchmark memory, speed, and quality before promising throughput |
| Voice adapter | Free API TTS where available, or licensed local TTS such as Piper | Voice-model licenses and target-language quality need separate validation; no unlicensed celebrity imitation |
| YouTube Data API and Analytics/Reporting APIs | Official discovery, upload, and owned-channel reports | Account authorization and endpoint-specific report availability apply |
| Windows Task Scheduler + persistent worker | Start jobs without paid hosting | Offline/sleeping PC pauses work; future scheduled YouTube publication can proceed after successful upload |

Official references: [Streamlit](https://docs.streamlit.io/), [FFmpeg](https://ffmpeg.org/about.html), [Ollama](https://docs.ollama.com/), [Piper](https://github.com/OHF-Voice/piper1-gpl).

Structured generation outputs should be schema-validated. Treat web pages and creator descriptions as untrusted source material, not executable instructions. Restrict downloads to permitted asset locations. Do not send credentials or private analytics to free AI services.

Revenue research identified an important free-service limitation: ElevenLabs' free-generated output is not commercially licensed under its checked terms, so it is not a default zero-cost production voice source. Also, TMDB's free noncommercial API access is not a verified commercial poster feed. These are provider-specific limits, not a claim that all free AI or movie-data sources are unsuitable. Alternatives remain local/commercially permitted voices and individually eligible assets. [Provider findings](../revenue/REVENUE_EDUCATION.md), [movie source findings](../formats/entertainment/ENTERTAINMENT_FORMATS.md).

## Free-only operation

No subscription, paid trial, paid model, premium clipping feature, or cloud hosting is part of the baseline. Existing electricity, hardware, storage, and internet still have real costs. Free APIs do not guarantee continuous access or high output volume.

Use a free-only provider allowlist, request/token limits, bounded retries, and a durable queue. On quota exhaustion, wait, use an approved local fallback, or block; never enable billing automatically, rotate projects to evade quotas, or silently switch to a paid model. Keep keys outside source control and redact logs. Setup requires user-controlled account sign-in/consent; no passwords belong in this guide.

Gemini's pricing currently includes free text options, but not every tool/model is free. Free-tier content may be used to improve Google's products, subject to applicable terms. Verify active project limits rather than hard-coding a generic allowance. [Pricing](https://ai.google.dev/gemini-api/docs/pricing), [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

The currently checked YouTube quota page lists separate daily search and upload buckets of 100 calls each, plus 10,000 units for other endpoints. The upload reference now states unverified projects are not automatically private-only; do not rely on old tutorials. Verify actual project access with a private test. [Quota reference](https://developers.google.com/youtube/data/determine_quota_cost), [upload reference](https://developers.google.com/youtube/data/reference/rest/v3/videos/insert).

## Revenue research and financial planning

The research now separates platform ads/Premium, paid clipping campaigns, direct sponsors, affiliates/referrals, digital products, services, memberships/tips and other-platform rewards. Each requires different content, eligibility and remaining operator work. Free production is separate from fees deducted after earning, refunds, tax and foreign-exchange costs. No program or payout account has been activated.

The [timed revenue model](../strategy/US_FIRST_REVENUE_PLAN.md) uses published rates and explicit conditional arithmetic, with zero income possible at every horizon. Sponsor survey quotes are benchmarks, not secured offers. Campaign approval, YouTube monetization, settled balance and bank cash are distinct. Do not extrapolate a total channel view count into all revenue streams.

Official YPP changes announced for February 1, 2027 materially affect a six-month plan beginning in late 2026. Current and future entry/ongoing requirements are separated in the [YouTube/campaign report](../revenue/REVENUE_CAMPAIGNS_AND_YOUTUBE.md). Ad income is not the launch-budget assumption. [Official changes](https://support.google.com/youtube/answer/12843009).

## Growth officer: available evidence and limits

For owned channels, use authorized reports for views/engaged views, viewing duration, retention, traffic, subscribers, and available geography/revenue metrics. Metric support varies by report and format. Use Studio export for gaps; missing/delayed data must not become zero. Competitor retention, impressions, and earnings are not available merely because their videos are public. [Channel reports](https://developers.google.com/youtube/analytics/channel_reports), [reporting overview](https://developers.google.com/youtube/reporting).

Use displayed official metrics and editorial observations initially. Custom API-based viral scores, engagement ratios, inferred earnings, and similar derived analytics require the applicable YouTube permission. Extended competitor-history retention must also be checked. Apply refresh/deletion rules to public research caches; owned authorized statistical history has separate conditions. [Developer policies](https://developers.google.com/youtube/terms/developer-policies), [additional analytics policies](https://developers.google.com/youtube/terms/derived-metrics-policy).

Proposed review cadence: once daily for job health and new publications, with 24-hour, 72-hour, and 7-day content reviews as data becomes available. Compare similar formats, durations, and observation windows. A better result suggests a hypothesis; it does not establish causation. Do not promise a universally best posting time or infer revenue from raw views.

## Build stages and acceptance criteria

The broader build order, approximate effort, dependencies, data/file design and failure tests are specified in [IMPLEMENTATION_PLAN.md](../../docs/archive/IMPLEMENTATION_STATUS_EARLIER.md). The editor-first slice now supplies a shared scene model and six renderable formats, with synthetic sample content. Researched stories, verified voice production and eligible real sources still need integrating before the proposed full production slice is complete.

Keep the dashboard and persistent worker separate, use transactional SQLite job leases/events and version-bound approvals, and route AI output through validated contracts. The first runtime does not need a distributed agent framework: deterministic application code controls assets, rendering and accounts; logical AI roles produce reviewable proposals. A future cloud controller must have durable storage/authenticated job handoffs instead of sharing a live SQLite file between machines. This retains the local/free baseline while making a later migration explicit.

The plan's rough 4–6 active-development-week estimate covers a supervised operating version if tool/source/account dependencies are available; it is not a guaranteed date or an income forecast. The public pilot and its full observation windows are a separate stage. No external setup or publishing is authorized merely by a planning milestone.

1. **Source and feasibility proof.** Establish one usable entertainment source or a generated-original fallback, one education format, one voice, and a local render benchmark. Exit: two playable sample Shorts with evidence/rights manifests and no paid dependency. A public listing alone is insufficient.
2. **Local production pipeline.** Add the dashboard, job persistence, script/scene schemas, captions, covers, duplicate detection, and resume behavior. Exit: one job per channel survives a deliberate render failure/restart without losing approvals or duplicating work.
3. **Publishing.** Connect each channel separately through OAuth. Use resumable uploads and stored upload/video IDs; verify channel identity, visibility, metadata, and processing status. Exit: private test upload and approved scheduled publication work without duplicate uploads. Studio-only features and unsupported campaign actions remain explicitly outside automation.
4. **Monitoring and learning.** Add official owned-channel reports, production alerts, source expiry checks, and a weekly evidence-linked editorial proposal. Exit: two channels remain separate, missing data is explicit, and recommendations cite observations rather than invent results.
5. **Limited unattended operation.** Only after repeated pilot reviews, enable eligible sources/formats with a queue cap, stop control, and fail-closed rules. Exit: simulated expired permission, exhausted quota, and ambiguous upload outcome all stop safely. Additional languages and longer videos are later experiments.

The earlier three-per-channel-per-week plan is a proposed initial validation cadence, not the user's eventual target. The pilot protocol's first cycle is three formats × three distinct episodes per channel (18 total). After source, runtime and observation gates pass, benchmark the later requested four to five per channel per day, with nine to ten a possible further capacity experiment. No cadence is a guaranteed growth tactic; publish only within actual source supply, quality, quotas and incident coverage.

## Setup and validation status

Runnable editor setup: `python run_editor.py serve --open`, or double-click `start_editor.cmd`. See [README.md](../README.md) for fresh-environment installation, versioned dependency details, commands and export behavior. No credentials or local model are needed for this component. Future service adapters/database/account setup are separate work. Publishing and campaign enrollment have not been performed.

Earlier research validation inspected the initially empty workspace, relevant official policy/API/tool documentation and public clipping-program pages. Editor runtime/media tests are now implemented as described above. No model benchmarks, license clearance for individual external media, account eligibility checks, campaign participation or uploads were performed. No supported Vyro/Reach automation integration was established. Source availability, permissions, free quotas and terms still need checking when those integrations are built.

Later research validation inspected three examples in YouTube's native Shorts browser interface, sampled their visuals and read Description counters; the findings and limits are in [direct reference checks](../references/DIRECT_REFERENCE_CHECKS.md). Public counters are time-sensitive observations, not competitor private analytics or proof of earnings. Local documentation links and catalog ID counts were checked; the new executable test suite covers the editor rather than the future end-to-end production system.

Current deliverables: reusable research-agent briefs, format catalogs (33 formats and 43 episode concepts), source/risk research, an updated decision ledger, revenue-route research, a US-first conditional financial model, public performance references, three direct Shorts checks, a market-transfer method, pilot measurement plan and source/strike-supervision update. Real success journeys are an EDU-F12 variant, not an extra counted ID. No owned-channel performance has been measured or production/alerts activated. See the [research index](../README.md) and [consolidated report](../strategy/INITIAL_RESEARCH_REPORT.md).

Current implementation deliverable: standalone format editor, reusable render API/CLI, sample videos, export manifests and integration tests. Next, test the formats with actual eligible clips/gameplay and narration, then connect research/writing/voice and the full production queue. A technical export manifest does not yet provide source/claim approval. Account setup and publication have not begun.
