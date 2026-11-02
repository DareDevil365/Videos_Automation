# Create: Character cutout stories and comedy

Preset: `cutout_ensemble`. Channel profile: `entertainment`.

## What the format produces

30–50 seconds; recurring cast; measured per-character speech.

Two to four stable characters, permitted head images/backgrounds and a causal setup/payoff. New CLI/batch jobs select scene direction v2: early two-person shots, interaction/reaction views, selective closeups and actual animal/object/action inserts. Distinct clothes stay consistent for each person; a narrator is voice-only unless `show_narrator: true` is selected.

## Prepare the request

Use `fiction: true`, optional `story_tone: "comedy"`, `cast_assets` keyed by cast ID and eligible background/media inputs. Choose `bottom_kind` and music explicitly. The comedy path adds concept selection and exact-punchline critique.

Use the [shared batch recipe](../README.md#shared-playbook-batch-recipe). Create a new plan ID, add an item with `kind: "playbook"`, `playbook: "cutout_ensemble"`, `channel: "entertainment"`, a specific topic and your request. Keep `test_only: true` while evaluating the result. `visual_review: "required"` is the default for new playbook batch jobs.

Inspect the actual [writer prompt](../../../Resources/Prompts/cutout_ensemble.writer.json) and [director contract](../../../Resources/Prompts/director-schema.json) rather than inventing unsupported settings. Source and media IDs come from the local registry, not arbitrary paths in model output.

## Execution and outputs

Concepts/selector with visible beats when enabled → writer with owner feedback → bounded comedy/creative critique → frozen cast/scene plan → voices → verified individual head crops, distinct outfits, shared scenes and inserts → exact-script aligned subtitles → render. Necessary stock repeats require a reason; the same cast location can continue naturally.

Run the saved plan from the project root:

```powershell
.venv\Scripts\python.exe run_pipeline.py --env-file .env batch-run --plan Resources/Plans/my-new-plan.json
.venv\Scripts\python.exe run_pipeline.py batch-status --plan Resources/Plans/my-new-plan.json
```

`my-new-plan.json` is a filename you create; it is not a shipped runnable example. Missing essential inputs hold the batch. Outputs go to the plan's `output_root/<plan-id>/<item-id>/`, normally under `Resources/Productions/`, with script, voice, scene plan, captions, metadata, QA and video. Resuming an unchanged completed plan reuses its jobs.

## Review and remaining work

The owner rejected **The Turtle Guard** script after viewing it. Its saved video remains technical history. The exact script is now blocked by owner feedback, even though a stricter live model critique still passed it. Do not recycle it by renaming characters. Scene/outfit/insert improvements have controlled FFmpeg tests and local previews; a complete new owner-approved comedy is still pending. These are simple collage poses, not full acting, rigs or lip-sync.

Fresh live review: local-only `Resources/Productions/fresh-funny-mystery-20261102/fresh-funny/` contains **The Turtle Guard**, 36.066 seconds and 114 words. Gemini generated the script, concept/critique and director plan from the starting brief; local speech/FFmpeg and required source/finished-frame/technical checks completed. `SCRIPT.md` is a readable copy of the actual generated dialogue. This is a new review candidate, not owner creative approval.

A 30.2-second revision exported with 90/90 subtitle words. Body shapes were accepted, while earlier stories/framing/caption choices were rejected. Current comedy approval remains unresolved. Bodies are silhouettes without rigs, facial acting or lip sync.

Watch the actual whole video and listen to speech/music. Check the opening promise, causal ending, actual media relevance, names, full readable dialogue and timing. Sampled frame review cannot assess the complete audiovisual experience. Technical readiness and creative approval are separate.

Historical/technical example: video (local-only: `Resources/Productions/speaker-subtitle-revision/video.mp4`). Its existence is not publishing/style approval.

Read the [dated research](../../../research/formats/entertainment/COMEDY_REFERENCE_2026-11-02.md), [rendering limits](../../../Resources/Templates/README.md), [role index](../../../agents/README.md) and [current status](../../PROJECT_STATUS.md).
