# Create: Useful education and demonstrations

Preset: `education_demo`. Channel profile: `education`.

## What the format produces

25–45 seconds; concrete problem → demonstrated change → useful result.

Accessible supporting sources, a practical takeaway and real matching demonstration media for specific tool screens or factual visuals. Original explanatory typography can use the supported motion blocks.

## Prepare the request

Use `fiction: false`, `source_urls` or a validated `brief`; bind essential media with `media_assets`. Non-test factual media requires unit-ID `visual_approvals`. Optional `motion_graphics: true` enables comparison/process/callout using exact script phrases. Music can be explicitly omitted with `require_music: false`.

Use the [shared batch recipe](../README.md#shared-playbook-batch-recipe). Create a new plan ID, add an item with `kind: "playbook"`, `playbook: "education_demo"`, `channel: "education"`, a specific topic and your request. Keep `test_only: true` while evaluating the result. `visual_review: "required"` is the default for new playbook batch jobs.

Inspect the actual [writer prompt](../../../Resources/Prompts/education_demo.writer.json) and [director contract](../../../Resources/Prompts/director-schema.json) rather than inventing unsupported settings. Source and media IDs come from the local registry, not arbitrary paths in model output.

## Execution and outputs

Sources → claim brief → writer → combined evidence/director review → local voice/alignment → matching demo or trusted graphics → frame/technical checks → package.

Run the saved plan from the project root:

```powershell
.venv\Scripts\python.exe run_pipeline.py --env-file .env batch-run --plan Resources/Plans/my-new-plan.json
.venv\Scripts\python.exe run_pipeline.py batch-status --plan Resources/Plans/my-new-plan.json
```

`my-new-plan.json` is a filename you create; it is not a shipped runnable example. Missing essential inputs hold the batch. Outputs go to the plan's `output_root/<plan-id>/<item-id>/`, normally under `Resources/Productions/`, with script, voice, scene plan, captions, metadata, QA and video. Resuming an unchanged completed plan reuses its jobs.

## Review and remaining work

Live factual writing, voice and export work. The latest interview typography pilot is 27.8 seconds with 85/85 spoken words and a live finished-frame pass. This does not prove current-tool screen recording, external-media matching or audience appeal. The old Python sample is a technical fixture; use the agreed practical channel topics.

Watch the actual whole video and listen to speech/music. Check the opening promise, causal ending, actual media relevance, names, full readable dialogue and timing. Sampled frame review cannot assess the complete audiovisual experience. Technical readiness and creative approval are separate.

Historical/technical example: video (local-only: `Resources/Productions/repo-upgrade-final-2026-11-02/interview-before-after/video.mp4`). Its existence is not publishing/style approval.

Read the [dated research](../../../research/formats/education-and-movies/PLAYBOOK_COUNTDOWNS_EDUCATION.md), [rendering limits](../../../Resources/Templates/README.md), [role index](../../../agents/README.md) and [current status](../../PROJECT_STATUS.md).
