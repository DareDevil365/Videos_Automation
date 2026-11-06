# Editorial checks, exact speech delivery and education graphics

Implemented from the [reviewed improvement plan](EDITORIAL_IMPROVEMENT_PLAN.md). These controls improve inspectability and enforce bounded contracts; they do not establish humor, retention, factual truth or audience approval.

## New request controls

Current source-detail callouts are thick bright red (`#ff3038`, 14 pixels at 720-pixel width) with a dark outline. They animate an entering arrow, a circle drawing on, a short hold and a fade-out. The bounded timeline scales down for short scenes. Frames are composed before camera movement to keep the target anchored to the source. Finished-frame samples cover entry, complete and cleared phases. This animates the overlay, not the depicted eyes/objects, and moving-source tracking remains unsupported.

The [full-screen server-chat preset](categories/server-chat/HOW_TO_CREATE.md) is separate from split-panel tea chat. It uses three comedy concepts/selection, exact-message writing and independent setup/punchline critique, sharing the existing one substantive rewrite. Actual message entry and scrolling are rendered frame by frame, with complete current/past messages and stable distinct speaker colors/voices. Exact-message, participant, length and no-lower-panel contracts are enforced. The latest format pilot demonstrates rendering; model approval still did not establish strong comedy.

New comedy/mystery CLI and batch jobs use `scene_direction_version: 2`; saved requests retain their original setting. The director selects `shot_type: dialogue|two_shot|insert`, `pose: neutral|talk|point|react`, an optional source-detail `callout`, and a specific `reuse_purpose`/`reuse_reason` when stock must repeat. Two-person scenes are preserved rather than forcibly converted into isolated closeups. Character episodes need an early two-shot and two-shots in at least one fifth of the beats. `show_narrator` defaults false; true requires an actual human/animal avatar and outfit for any visible narrator. Actual animals/objects/actions use source-image/video inserts without the talking cast. A still-photo arrow/circle highlights a real located detail, without fabricating motion. Unsupported video tracking holds.

Outfits are stable per character and distinct between characters: shirt/t-shirt, hoodie, jacket or sweater with different colors and trouser variants. Head images receive a complete-head crop and output-pixel check, with one bounded repair; unsuitable group/partial-head sources hold. Source repeats are checked by file hash and require a necessary detail, adjacent continuity or later replay. Reusing a cast location backdrop is allowed. `visuals.json` records compiled outfits, head crops, callout geometry and justified reuse. These are simple collage poses/camera changes, not rigged animation or lip-sync.

Record owner creative feedback with `run_pipeline.py feedback JOB_ID --verdict rejected --reason "Specific criticism"` (accepted and needs_revision are also supported). The private record is bound to an intact saved script hash. Latest applicable examples inform writing; all exact rejections remain binding. A model cannot approve a rejected exact script, and renamed/paraphrased reuse is discouraged but not fully detected. A live model review still passed the rejected Turtle Guard story, so stronger prompts are an improvement attempt, not evidence that comedy quality is solved.

Live generation now supplies measured word/unit counts, counts for each hook alternative and explicit target bounds to the single contract-repair call. Every alternative is checked; dialogue prompts keep the complete spoken hook/caption within twelve words. A still-invalid repair holds instead of being manually trimmed. This does not add another substantive rewrite.

When a literal Commons search finds no eligible match, the media agent can request two simpler search queries from Gemini and try each once. It records successful refinement-to-asset mappings locally. The same license allowlist, registered-asset eligibility and required source/finished-frame review remain; a refined search is not a relevance verdict. Network failures, quota and permission holds propagate without further searching. This adds up to one cached model call and two stock searches per unmatched query, not an unlimited acquisition loop.

Before acceptance, the acquisition route inspects actual source pixels and can reject up to three newly downloaded candidates per query. A migration check also covers previously cached sources. Individual candidate verdicts/cache records are distinct from the per-video source and finished-frame reviews. A video candidate uses three sampled frames, so intervening content can still be missed. Commons JPEG thumbnail MIME is used for decoding even if its original source is a TIFF; license and original MIME remain recorded. Candidate checks add model calls within the shared provider controls; review failure never grants a license exception.

| Field | Values | Behavior |
| --- | --- | --- |
| `hook_options` | boolean | For generated narrated playbooks, request three distinct typed hooks and a selected index inside the existing writer call. The actual first spoken line/caption must match that choice. Supplied scripts and caption-only aura/source clips do not get a fabricated brainstorm record |
| `hook_validation` | `structural`, `strict` | Strict narrated hooks reject greeting/preamble openings and enforce a bounded opening length; there is no universal four-word minimum. Playbook hook/first-unit identity remains checked |
| `editorial_review` | `off`, `required` | Required adds a separate skeptical text review, validates the exact existing final payoff quote/ID, and rejects unresolved issues. Quotas/provider failures remain holds |
| `motion_graphics` | boolean | Enables supported original typography. The three new education presets require this and a full-frame layout |
| `restrict_visuals_to_inventory` | boolean | When true, provide 1-16 registered `visual_asset_ids` and optional `asset_roles`. The writer receives their descriptions; the director must bind every scene to one of those real sources, with no empty search binding. Sources remain subject to eligibility and required review |

New playbook batch jobs default to hook options, strict hook validation and required editorial review, alongside required sampled visual review. Existing saved requests remain unchanged. Direct older preset requests retain their previous review defaults unless enabled. `rewrite_reveal`, `myth_fact` and `quiz_pause` select enhanced defaults even on the direct route; they default to no required music and no lower panel. Explicit modes can disable model review for a clearly labeled offline test; no disabled review should be described as a pass.

Three alternatives share one writing call. The separate editorial pass adds one model call for an ordinary successful script pass and shares the existing single substantive rewrite budget. Structural repairs remain bounded separately. Every call shares the existing provider selection, content cache, local daily budget and cooldown. No swallowed quota, alternate key or paid fallback is introduced.

## Exact script and delivery are separate

The script remains clean immutable dialogue. A director scene can optionally contain:

```json
{
  "speech_segments": [
    {"text": "Use your real experience.", "pause_after": 0.35, "speed": 1.0},
    {"text": "Explain what you personally did.", "pause_after": 0, "speed": 1.05}
  ]
}
```

This is a delivery fragment, not a complete scene. Joining the segment text must preserve every script word, punctuation and order (whitespace is normalized for coverage checking). At most eight segments, speed multipliers 0.9–1.25, internal pauses up to 1.2s each/2.4s total, and zero pause after the final segment. Existing scene `pause_after` handles the unit ending. Effective speech pace must remain within the existing length-scale limits. Empty segments, nonfinite values, changed text and markup tags hold.

Local TTS renders/caches each exact segment and assembles a complete per-unit WAV including its real internal silence. Segment text/speed/model/voice and assembly pause parameters participate in cache identity. Unit timing, complete narration, caption alignment and following scene offsets use the actual assembled file. Accepted preset and cast voices remain selected. `[P]`, `[PP]`, `[PPP]`, `[FAST]` and `[NORMAL]` are not added to dialogue or captions.

## Three education recipes

- [Rewrite reveal](categories/rewrite-reveal/HOW_TO_CREATE.md): weak hypothetical wording → precise explanation → spoken stronger version → truthful takeaway; an actual Before/After comparison is required.
- [Myth versus fact](categories/myth-fact/HOW_TO_CREATE.md): clearly label the misconception, deliver a sourced correction and show Myth/Fact comparison headings. Do not manufacture a popular belief or make a universal claim.
- [Quiz with thinking time](categories/quiz/HOW_TO_CREATE.md): original self-contained question, necessary conditions, one thinking interval, answer and explanation. A claimed unique answer still needs substantive verification.

Every beat in these recipes requires an actual supported original graphic. They do not silently search for stock or invent a product screenshot. Use the existing source-media routes for a real interface/evidence image. Opening graphics show the concrete question/example, without an automatic generic title screen. When a selected hook caption is recorded, an opening education graphic must actually contain it.

## Quiz timing contract

Exactly one scene before the payoff uses `graphic.kind: "timer"`, one exact earlier question phrase in `labels`, and `thinking_seconds` from 2 to 6. The scene first speaks its ordinary clean instruction; the narration then includes real silence for that interval. The frame-counted timer starts at the measured speech boundary. Ordinary end-of-unit pause follows; the next answer unit starts after the full measured duration. Captions cover speech, not an invented spoken countdown.

Timer scenes outside `quiz_pause`, multiple/missing timers, timers after the answer and timers without matching silence hold. Adding only a capability dictionary entry cannot create a timer; schema, plan validation, voice timing and rendered frames are connected.

## Records and review

`script.json` retains hook alternatives/selection and the separate editorial verdict. If the bounded rewrite changes the hook, the old alternatives are marked inactive instead of falsely presented as the current choice. `voice.json` records speech segments, segment timing and thinking duration; exact word alignment remains English/model-estimated. `visuals.json` records timer boundaries and plates. Package metadata includes `creative_experiment` descriptors for later comparisons: actual selected hook type, preset, first-frame intent and an optional question only if present in the final spoken unit. Those descriptors are not performance observations or instructions to post comments.

Independent editorial review still uses the selected model. It is a separate opinion with checked quote identities, not an independent human reviewer or an audiovisual inspection. Existing factual evidence checks and sampled-frame checks remain separate.

## Offline demonstration

`tools/create_editorial_demo.py` renders/resumes a test-only original rewrite exercise using a prepared public-source brief, an explicitly offline prepared scene plan, installed local Kokoro speech and local English alignment. It makes no Gemini call and disables model editorial/frame review explicitly. Its default brief path refers to an existing local historical pilot; a fresh clone must supply a real prepared brief with `--brief` and install the local speech/alignment models. No fresh source fetch or account access is performed.

Default output: local-only `Resources/Productions/editorial-rewrite-demo/`, including `demo-validation.json`. Use a fresh output directory after changing initialized demonstration inputs. Run from the project root:

```powershell
.venv\Scripts\python.exe tools/create_editorial_demo.py
```

Photo-head expressions, chat typing overlays and music beat synchronization remain explicitly deferred in the implementation plan. Changing arbitrary shot lengths is not actual synchronization. Existing source/playbook account and audience-validation gaps remain.
