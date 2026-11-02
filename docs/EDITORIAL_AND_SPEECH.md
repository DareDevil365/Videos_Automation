# Editorial checks, exact speech delivery and education graphics

Implemented from the [reviewed improvement plan](EDITORIAL_IMPROVEMENT_PLAN.md). These controls improve inspectability and enforce bounded contracts; they do not establish humor, retention, factual truth or audience approval.

## New request controls

| Field | Values | Behavior |
| --- | --- | --- |
| `hook_options` | boolean | For generated narrated playbooks, request three distinct typed hooks and a selected index inside the existing writer call. The actual first spoken line/caption must match that choice. Supplied scripts and caption-only aura/source clips do not get a fabricated brainstorm record |
| `hook_validation` | `structural`, `strict` | Strict narrated hooks reject greeting/preamble openings and enforce a bounded opening length; there is no universal four-word minimum. Playbook hook/first-unit identity remains checked |
| `editorial_review` | `off`, `required` | Required adds a separate skeptical text review, validates the exact existing final payoff quote/ID, and rejects unresolved issues. Quotas/provider failures remain holds |
| `motion_graphics` | boolean | Enables supported original typography. The three new education presets require this and a full-frame layout |

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

This is a delivery fragment, not a complete scene. Joining the segment text must preserve every script word, punctuation and order (whitespace is normalized for coverage checking). At most eight segments, speed multipliers 0.9–1.15, internal pauses up to 1.2s each/2.4s total, and zero pause after the final segment. Existing scene `pause_after` handles the unit ending. Effective speech pace must remain within the existing length-scale limits. Empty segments, nonfinite values, changed text and markup tags hold.

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
