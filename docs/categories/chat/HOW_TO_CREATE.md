# Create: Fictional chat and tea stories

Preset: `tea_chat`. Channel profile: `entertainment`.

## What the format produces

30–45 seconds; 90–140 words; 10–18 units. Consistent brisk character voices.

A clear sender/recipient, planted clue, escalation and an understandable answer. Actual registered ASMR or gameplay lower panel; selected music or explicit music opt-out.

## Prepare the request

Use `fiction: true`, `bottom_kind: "asmr"` or `"gameplay"`, and `bottom_asset_id`. Set `music_id` or `require_music: false`. `top_fraction` can tune the panel split within supported bounds.

Use the [shared batch recipe](../README.md#shared-playbook-batch-recipe). Create a new plan ID, add an item with `kind: "playbook"`, `playbook: "tea_chat"`, `channel: "entertainment"`, a specific topic and your request. Keep `test_only: true` while evaluating the result. `visual_review: "required"` is the default for new playbook batch jobs.

Inspect the actual [writer prompt](../../../Resources/Prompts/tea_chat.writer.json) and [director contract](../../../Resources/Prompts/director-schema.json) rather than inventing unsupported settings. Source and media IDs come from the local registry, not arbitrary paths in model output.

## Execution and outputs

Writer → frozen messages/speakers → per-character TTS → full actual message states → lower-panel composition → review/export.

Run the saved plan from the project root:

```powershell
.venv\Scripts\python.exe run_pipeline.py --env-file .env batch-run --plan Resources/Plans/my-new-plan.json
.venv\Scripts\python.exe run_pipeline.py batch-status --plan Resources/Plans/my-new-plan.json
```

`my-new-plan.json` is a filename you create; it is not a shipped runnable example. Missing essential inputs hold the batch. Outputs go to the plan's `output_root/<plan-id>/<item-id>/`, normally under `Resources/Productions/`, with script, voice, scene plan, captions, metadata, QA and video. Resuming an unchanged completed plan reuses its jobs.

## Review and remaining work

A 35-second multi-voice pilot exported. Story logic still needed improvement; it remains test-only. Chat motion uses discrete states, without smooth scrolling.

Watch the actual whole video and listen to speech/music. Check the opening promise, causal ending, actual media relevance, names, full readable dialogue and timing. Sampled frame review cannot assess the complete audiovisual experience. Technical readiness and creative approval are separate.

Historical/technical example: video (local-only: `Resources/Productions/playbook-refinement/tea-chat/video.mp4`). Its existence is not publishing/style approval.

Read the [dated research](../../../research/formats/entertainment/PLAYBOOK_STORIES.md), [rendering limits](../../../Resources/Templates/README.md), [role index](../../../agents/README.md) and [current status](../../PROJECT_STATUS.md).
