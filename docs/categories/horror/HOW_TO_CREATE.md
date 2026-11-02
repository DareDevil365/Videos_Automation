# Create: Original horror and mystery

Preset: `horror_stock`. Channel profile: `entertainment`.

## What the format produces

30–45 seconds; 75–95 words; 8–13 units. Female local narrator, slower delivery and restrained pauses.

A specific opening anomaly, two or three clues and a concrete final explanation/reversal. Relevant permitted location/prop stills or clips; quiet selected music. Optional ASMR lower panel.

## Prepare the request

Use `fiction: true`; select `music_id`, `visual_asset_ids` and/or `media_assets`. `bottom_kind` is `none` or `asmr`; a lower panel needs `bottom_asset_id`. Stock acquisition can fill eligible fictional scenes, but its matches still require review.

Use the [shared batch recipe](../README.md#shared-playbook-batch-recipe). Create a new plan ID, add an item with `kind: "playbook"`, `playbook: "horror_stock"`, `channel: "entertainment"`, a specific topic and your request. Keep `test_only: true` while evaluating the result. `visual_review: "required"` is the default for new playbook batch jobs.

Inspect the actual [writer prompt](../../../Resources/Prompts/horror_stock.writer.json) and [director contract](../../../Resources/Prompts/director-schema.json) rather than inventing unsupported settings. Source and media IDs come from the local registry, not arbitrary paths in model output.

## Execution and outputs

Research → fictional script → frozen scene plan → timed speech → matched stock/captions → FFmpeg → sampled-frame and technical review.

Run the saved plan from the project root:

```powershell
.venv\Scripts\python.exe run_pipeline.py --env-file .env batch-run --plan Resources/Plans/my-new-plan.json
.venv\Scripts\python.exe run_pipeline.py batch-status --plan Resources/Plans/my-new-plan.json
```

`my-new-plan.json` is a filename you create; it is not a shipped runnable example. Missing essential inputs hold the batch. Outputs go to the plan's `output_root/<plan-id>/<item-id>/`, normally under `Resources/Productions/`, with script, voice, scene plan, captions, metadata, QA and video. Resuming an unchanged completed plan reuses its jobs.

## Review and remaining work

A shorter legacy illustrated mystery exported and was creatively rejected. The newer stock preset and contracts exist; a strong approved 30–45s stock episode remains to be demonstrated.

Watch the actual whole video and listen to speech/music. Check the opening promise, causal ending, actual media relevance, names, full readable dialogue and timing. Sampled frame review cannot assess the complete audiovisual experience. Technical readiness and creative approval are separate.

Historical/technical example: video (local-only: `Resources/Productions/prototype-2026-11-02/mystery-last-floor/video.mp4`). Its existence is not publishing/style approval.

Read the [dated research](../../../research/formats/entertainment/PLAYBOOK_STORIES.md), [rendering limits](../../../Resources/Templates/README.md), [role index](../../../agents/README.md) and [current status](../../PROJECT_STATUS.md).
