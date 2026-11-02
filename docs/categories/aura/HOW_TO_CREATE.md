# Create: Aura progression edits

Preset: `aura_progression`. Channel profile: `entertainment`.

## What the format produces

12–24 seconds; short original editorial captions; no default TTS.

At least four genuinely different permitted visual files, an actual progression/payoff and selected suitable music. Gameplay can be optional; ASMR is rejected.

## Prepare the request

Supply at least four `visual_asset_ids` with distinct content hashes, `music_id`, and `bottom_kind: "none"` or `"gameplay"`. Describe only what the supplied assets support; do not invent quotes/achievements about the depicted person.

Use the [shared batch recipe](../README.md#shared-playbook-batch-recipe). Create a new plan ID, add an item with `kind: "playbook"`, `playbook: "aura_progression"`, `channel: "entertainment"`, a specific topic and your request. Keep `test_only: true` while evaluating the result. `visual_review: "required"` is the default for new playbook batch jobs.

Inspect the actual [writer prompt](../../../Resources/Prompts/aura_progression.writer.json) and [director contract](../../../Resources/Prompts/director-schema.json) rather than inventing unsupported settings. Source and media IDs come from the local registry, not arbitrary paths in model output.

## Execution and outputs

Caption writing → source-aware progression plan → measured edit timing → actual clips/stills/gauge → effects at payoff → review/export.

Run the saved plan from the project root:

```powershell
.venv\Scripts\python.exe run_pipeline.py --env-file .env batch-run --plan Resources/Plans/my-new-plan.json
.venv\Scripts\python.exe run_pipeline.py batch-status --plan Resources/Plans/my-new-plan.json
```

`my-new-plan.json` is a filename you create; it is not a shipped runnable example. Missing essential inputs hold the batch. Outputs go to the plan's `output_root/<plan-id>/<item-id>/`, normally under `Resources/Productions/`, with script, voice, scene plan, captions, metadata, QA and video. Resuming an unchanged completed plan reuses its jobs.

## Review and remaining work

The old single-portrait aura exported but was creatively rejected. The new four-asset progression contract exists and is tested; its approved real-content pilot is pending. Beat synchronization is not implemented.

Watch the actual whole video and listen to speech/music. Check the opening promise, causal ending, actual media relevance, names, full readable dialogue and timing. Sampled frame review cannot assess the complete audiovisual experience. Technical readiness and creative approval are separate.

Historical/technical example: video (local-only: `Resources/Productions/prototype-2026-11-02/aura-composure/video.mp4`). Its existence is not publishing/style approval.

Read the [dated research](../../../research/formats/entertainment/PLAYBOOK_AURA.md), [rendering limits](../../../Resources/Templates/README.md), [role index](../../../agents/README.md) and [current status](../../PROJECT_STATUS.md).
