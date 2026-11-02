# Project status and remaining work

Latest implementation update, 2 November 2026: **nine playbooks** now include original-graphics rewrite reveal, myth/fact and quiz with real thinking silence/countdown. New batches enable same-call hook alternatives and separate exact-payoff review; structured speech segments add internal silence/speed without changing dialogue. **210 tests passed in 118.40s** with two existing warnings. An actual local rewrite fixture exported at 25.333 seconds with 77/77 aligned words and zero Gemini calls. See the [completed improvement plan](EDITORIAL_IMPROVEMENT_PLAN.md) and [operating contracts](EDITORIAL_AND_SPEECH.md). Live validation of the new model prompts and owner creative approval remain pending. Earlier counts below describe the pre-improvement audit snapshot.

Audit date: 2 November 2026. Checked source modules, documentation, current local configuration, SQLite records, saved outputs/checkpoint hashes and the complete test suite. No new model generation, account login, publishing or external research was performed. Documentation organization is implemented; the feature gaps below were assessed rather than silently changed.

At the time of the audit this directory was not a Git checkout; the assessment used on-disk code/state and saved run evidence, rather than commit history or a Git diff. A subsequent source-only GitHub publication is recorded in the root project guide.

## Overall assessment

The local production engine works and has produced real videos. The project is still a prototype channel operation: creative quality is inconsistent, daily source/input setup is incomplete, and live publishing/Analytics/browser generation need validation. A single percentage would conceal those differences.

Evidence vocabulary: **demonstrated** means an actual saved local/live run exists; **fixture-tested** means behavior was checked with controlled media/pages or fake services; **pending activation** means code exists but real inputs/accounts are absent; **proposed** means the dedicated feature is not implemented. Technical passage does not mean owner-approved creative quality.

## Initial workspace audit snapshot

| Item | Observed state |
| --- | --- |
| Jobs | 21 total: 16 ready, 2 held, 3 cancelled |
| Ready requests | 10 explicitly test-only; 6 older requests without the test-only flag |
| QA readiness | 6 ready records say `publication_ready: true`; these flags do not constitute current owner/style approval or account readiness |
| Saved integrity | 493 checkpoint/file references across ready jobs checked; no missing files or hash mismatches |
| Registered assets | 128 records, including 78 explicitly test-only video assets; this is not 128 independently reviewed reusable production inputs |
| Review exports | 7 `video.mp4` copies under `Resources/Productions/`; other pipeline-ready outputs stay in private job storage |
| Visual review evidence | 1 ready job has a passing live finished-frame review; 15 older ready QA records predate these report fields |
| Uploads/Analytics | 0 upload records, 0 video IDs, 0 observations, 0 public snapshot records |
| Source catalog | No registered source profile files |
| Channel activation | Both publication modes disabled; no OAuth files or verified channel identities; auto-private upload off |
| Recurring inputs | Both profiles have zero configured feeds, source URLs, research queries or footage IDs; no profile music selected. Per-job assets exist separately |
| Optional keys | YouTube discovery and Pexels keys absent. Commons/local supplied inputs do not require these keys |
| Runtime | FFmpeg/ffprobe, Kokoro/Piper runtimes and current local voice model found |
| Gemini | Key present when `.env` is explicitly loaded; local free-tier confirmation recorded; 36 calls used against the restored 30-call local cap on the audit UTC date, so 0 local calls remain |

The separate local daily budget resets at 00:00 UTC, or 05:30 IST on 3 November for this recorded day. That is local accounting, not a claim about provider allowance. Do not increase the cap merely to force the backlog through. The plain CLI does not implicitly load `.env`; use `--env-file .env`.

The two held jobs report `background_missing` at directing and `model_experiment_network` at scripting. Inspect/retry deliberately after supplying the actual fix. Cancelled development attempts remain for traceability; they are not unfinished production commitments.

## Implemented and demonstrated locally

| Area | What is done | Remaining boundary |
| --- | --- | --- |
| Orchestration | Durable stages/checkpoints, job/global leases, cache, retry/hold/cancel, disk guards, quota cooldown and resume | Single-PC runtime; no unattended uptime or throughput proof |
| Research/writing | Public page/feed collection, dated source-linked claims, Gemini scripts/evidence review, explicit supplied-script origin, bounded rewrites and duplicates | Real topic/source curation and reliable creative results still needed |
| Voice/captions | Local Piper/Kokoro speech, stable character voices, measured durations, pauses, audio checks; English exact-script alignment and full-dialogue phrase captions | Acting, pronunciation and timing need actual listening; other languages unvalidated |
| Editing/export | Supplied-media overlay/stack/focus/multiblock layouts, crop/contain/blur, motion/effects/CTA, H.264/AAC MP4, cover, SRT, project and manifest | No arbitrary timeline, full animation or native-editor adapter |
| Creative plans | Nine presets, frozen dialogue/cast plan, per-unit visual mapping, one substantive rewrite, comedy concept/punchline checks, new-batch hook alternatives and separate exact-payoff review | A model pass has missed weak logic/jokes; not a dependable autonomous creative director |
| Motion graphics | Trusted comparison/process/callout scenes using exact script text, local animated typography | No general generated-code animation or fabricated screenshots |
| Media/provenance | Registered copied inputs, recorded evidence, expiry/hash checks, Commons acquisition, optional Pexels adapter and SQLite metadata search | Search can return irrelevant subjects; matching/permission records need review |
| Technical QA/package | Full audio/video decode, dimensions/timing/clipping, freshness/asset checks, credits, disclosure and metadata | Limited claim phrase checks and sampled images do not establish complete editorial/audio quality |
| Batch/native controls | Saved plans, stable jobs, renewable leases, checked copies, restart recovery, Start/Pause/Status/New plan | Cooperative pause; current default starter intentionally has missing media/music inputs |
| UI | Local dashboard and compositor with tested HTTP/session controls | Newer generation/source/music/playbook setup mostly CLI-driven; current visual/responsive QA pending |

## Content categories: how finished are they?

| Category | What exists | What is partial or missing |
| --- | --- | --- |
| [Rewrite reveal](categories/rewrite-reveal/HOW_TO_CREATE.md) | Full original-graphics recipe; actual local 25.333s speech/alignment/export fixture | New model hook/editorial prompts live-unverified; fixture is not style/audience approval |
| [Myth/fact](categories/myth-fact/HOW_TO_CREATE.md) | Original-graphics preset, correct comparison headings and source/plan contracts | Real sourced episode and creative validation pending |
| [Quiz](categories/quiz/HOW_TO_CREATE.md) | Required question/answer structure, one measured silent thinking interval, real rendered countdown and full synthetic-speech pipeline test | Generated puzzle correctness and real human-speech quiz pilot still require validation |
| [Horror/mystery](categories/horror/HOW_TO_CREATE.md) | Stock-story preset and older procedural illustration route; exported legacy mystery | Earlier short pilot rejected; approve a coherent full-length stock story with relevant scenes |
| [Chat/tea](categories/chat/HOW_TO_CREATE.md) | Timed full messages, cast voices, ASMR/gameplay layout; 35-second pilot | Story/payoff reliability, approved episodes and smooth chat scrolling |
| [Cutout comedy](categories/cutout-comedy/HOW_TO_CREATE.md) | Human-shaped silhouettes, stable shirts, active-speaker closeups, aligned full dialogue; 30.2s revision | Strong owner-approved comedy; detailed acting/emotions/rigging/lip-sync absent |
| [Aura](categories/aura/HOW_TO_CREATE.md) | Old export and new four-distinct-asset progression contract | Old single-image style rejected; demonstrate rich real progression/music timing |
| [Education](categories/education/HOW_TO_CREATE.md) | Live factual pipeline and 27.8s interview typography pilot with 85/85 words and passing sampled frames | Actual current-tool demos/source visuals and approved repeatable series; no external-media relevance proved by typography pilot |
| [Movie countdown](categories/movies/HOW_TO_CREATE.md) | Nine-pick preset, rank layouts and matching-media prerequisites | Real verified nine-film asset/source set and complete approved pilot |
| [Source clips](categories/source-clips/HOW_TO_CREATE.md) | Permission profiles, ingestion/subtitles/ASR, cue-based selection, original speech/caption fixtures | Populate a real source catalog and validate the entire acquisition-to-export route |
| [ASMR](categories/asmr/HOW_TO_CREATE.md) | Owner-imported clip packaged/exported | Real automatic provider generation unverified; source quality and seamless ending need improvement |

The [category index](categories/README.md) also maps the broader research catalogs. Those catalogs contain more ideas than the nine executable playbooks; their entries are not all completed content generators.

## Implemented adapters awaiting real validation

- **Browser media generation:** supported-setting planner, explicit selector/cost preflight, dedicated Brave or configured CDP, one submission and download-only reconciliation are fixture-tested. A saved downloaded/imported job is not proof of an automated real-page generation; the demonstrated ASMR source was owner supplied. Actual selectors/account/model allowance need calibration.
- **YouTube publishing:** OAuth, verified identity, exact-version approval, network-free preview, private/scheduled resumable upload and ambiguous-response recovery are implemented and simulated. Connect each intended channel, validate one private upload/recovery and then scheduling. No immediate-public mode is offered.
- **Analytics/growth:** owned calendar-date reports at 24h/72h/7d checkpoints and basic hypotheses exist, but no real observations. Current growth grouping filters by channel/checkpoint; it does not rigorously match format, duration or experiment conditions. Geography, retention curves, revenue collection and mature optimization are not implemented here.
- **Public comparisons:** optional YouTube discovery/public count snapshots exist but are not configured/observed in this workspace. Age-normalized lifetime counts are not live trends; later snapshots are needed for observed deltas.
- **Supervision:** local disk/asset/lease alerts, incident pause and optional remote reconciliation exist. External notifications and a complete claims/strikes feed do not.

## Highest-value remaining work

1. **Finish one repeatable creative route.** Choose the next category from current owner steering, improve the actual setup/payoff and relevant visuals, and produce several distinct owner-accepted episodes. Preserve the accepted voice/body work. Do not revive rejected topics/styles by default.
2. **Supply the prerequisites.** Curate reusable eligible backgrounds/music and any literal demo/movie media; populate source profiles/feeds/queries where needed. Existing assets are not configured channel defaults. New default plans are starter templates, not a ready daily schedule.
3. **Close the actual review gap.** Demonstrate source-frame relevance on real selected external media; listen to complete speech/music and inspect real pacing/caption timing. Current frame checks have no audio and can miss unsampled action. No autonomous visual repair loop exists.
4. **Validate the required integration route.** If generated footage is needed, calibrate one real browser/provider route. If source clipping is needed, prove one real permitted source ingestion/selection/export. These can be pursued independently; neither is required for a purely original typography pilot.
5. **Activate publication deliberately.** Owner OAuth/identity, exact eligible finished version, first private upload, remote processing/recovery and schedule validation. Publishing remains disabled during this audit/organization.
6. **Run a measured small pilot.** Capture actual publication/production times and owned observations. Improve matched-format/duration comparisons before using automated growth suggestions to choose a winner.
7. **Reduce operating friction.** Surface playbook/media/generation setup in the UI, verify current responsive behavior, connect a chosen external notification route and document backup/storage management.

## Further engineering, currently proposals or limited primitives

Smooth chat scrolling; beat-aware cuts/stings/ducking; richer character animation and emotional voice direction; multilingual quality/alignment; advanced thumbnail alternatives/testing; semantic media matching and bounded automatic repair; fast movie montage/film quiz/event-reaction playbooks; richer success-journey/source-aware demos; fully integrated discovery-to-new-playbook scheduling; sustainable daily capacity measurement; automatic storage lifecycle/cleanup; cloud deployment and native Adobe/Resolve bridges. Some have reusable lower-level building blocks, but the dedicated complete features are not established.

Public audience results, monetization access, campaigns and income are not demonstrated. Repository studies and campus-project investigations are research records; no audited third-party application was installed/integrated by this organization task.

## Documentation/organization completed in this pass

39 existing documents/research records moved to labeled subject/role folders; 12 role guides and 8 category creation guides added; whole-code walkthrough, status report, folder map, examples/tools/tests/Resources subfolder indexes added. The old implementation status is archived. Root README is the entry point, and root PROJECT_GUIDE remains maintained architecture/setup. Runtime package/media/plan/checkpoint paths are preserved. [FILE_MOVES.json](FILE_MOVES.json) records moves.

Validation before organization: **183 tests passed in 87.24s**, two existing Pillow `Image.getdata` deprecation warnings. These checks include real FFmpeg outputs plus controlled external-service/browser fixtures. After organization: **493 saved references still match**, **453 local links across 69 documents pass**, all **51 source modules are mapped**, moved research JSON parses and both CLI help entry points load. The root project guide records the exact scope/limitations. No production behavior was changed to close the gaps listed above.
