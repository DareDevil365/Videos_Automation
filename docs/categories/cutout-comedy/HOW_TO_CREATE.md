# Create: Character cutout stories and comedy

Preset: `cutout_ensemble`. Channel profile: `entertainment`.

## What the format produces

30–50 seconds; recurring cast; measured per-character speech.

Two to four stable characters, permitted head images/backgrounds and a causal setup/payoff. Clothing identity remains stable; spoken turns focus the actual speaker.

## Prepare the request

Use `fiction: true`, optional `story_tone: "comedy"`, `cast_assets` keyed by cast ID and eligible background/media inputs. Choose `bottom_kind` and music explicitly. The comedy path adds concept selection and exact-punchline critique.

Use the [shared batch recipe](../README.md#shared-playbook-batch-recipe). Create a new plan ID, add an item with `kind: "playbook"`, `playbook: "cutout_ensemble"`, `channel: "entertainment"`, a specific topic and your request. Keep `test_only: true` while evaluating the result. `visual_review: "required"` is the default for new playbook batch jobs.

Inspect the actual [writer prompt](../../../Resources/Prompts/cutout_ensemble.writer.json) and [director contract](../../../Resources/Prompts/director-schema.json) rather than inventing unsupported settings. Source and media IDs come from the local registry, not arbitrary paths in model output.

## Execution and outputs

Concepts/selector when enabled → writer → bounded comedy/creative critique → frozen cast plan → voices → active-speaker closeups → exact-script aligned subtitles → render.

Run the saved plan from the project root:

```powershell
.venv\Scripts\python.exe run_pipeline.py --env-file .env batch-run --plan Resources/Plans/my-new-plan.json
.venv\Scripts\python.exe run_pipeline.py batch-status --plan Resources/Plans/my-new-plan.json
```

`my-new-plan.json` is a filename you create; it is not a shipped runnable example. Missing essential inputs hold the batch. Outputs go to the plan's `output_root/<plan-id>/<item-id>/`, normally under `Resources/Productions/`, with script, voice, scene plan, captions, metadata, QA and video. Resuming an unchanged completed plan reuses its jobs.

## Review and remaining work

A 30.2-second revision exported with 90/90 subtitle words. Body shapes were accepted, while earlier stories/framing/caption choices were rejected. Current comedy approval remains unresolved. Bodies are silhouettes without rigs, facial acting or lip sync.

Watch the actual whole video and listen to speech/music. Check the opening promise, causal ending, actual media relevance, names, full readable dialogue and timing. Sampled frame review cannot assess the complete audiovisual experience. Technical readiness and creative approval are separate.

Historical/technical example: video (local-only: `Resources/Productions/speaker-subtitle-revision/video.mp4`). Its existence is not publishing/style approval.

Read the [dated research](../../../research/formats/entertainment/COMEDY_REFERENCE_2026-11-02.md), [rendering limits](../../../Resources/Templates/README.md), [role index](../../../agents/README.md) and [current status](../../PROJECT_STATUS.md).
