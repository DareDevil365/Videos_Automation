# Create: movie content

## Confirmed movie context and recommendations

The `movie_brief` route makes one source-backed question or recommendation into a narrated portrait Short. Start with the viewer's question, distinguish announcement from rumor, and give a concrete viewing reason. Use studio/distributor evidence for the actual market/date or omit the claim. A cast announcement is not a confirmed plot; a comic recap is not a film spoiler. A trailer or publisher page does not grant permission to re-upload its images.

The [Doomsday research packet](../../../research/content-movies/README.md) and [reviewed source pilot tool](../../../tools/create_source_short_pilots.py) demonstrate an optional viewing recommendation without assumed movie footage rights. The program uses a factual brief, one narrator, 7–12 source-linked units, exact graphics labels and the existing local motion-block compositor. Keep rumor, release timing, region, box-office estimate and reporting date distinct. Use the [movie audience critic](../../../agents/audience-critique/README.md) to flag empty hype, weak reasons and actor/character confusion. The older countdown route below remains available.

## Nine-pick movie countdowns

Preset: `movie_countdown`. Channel profile: `entertainment`.

## What the format produces

35–55 seconds; nine complete picks at ranks 10 through 2, with number one explicitly invited from viewers.

A clear theme, nine verified films, distinct original reasons and matching permitted posters/clips. The opening must accurately promise nine picks plus an optional audience choice.

## Prepare the request

Provide factual source evidence and matching `media_assets`; non-test jobs need unit-ID `visual_approvals`. Select permitted music or the supported explicit opt-out. No random stock replacement for a named film.

Use the [shared batch recipe](../README.md#shared-playbook-batch-recipe). Create a new plan ID, add an item with `kind: "playbook"`, `playbook: "movie_countdown"`, `channel: "entertainment"`, a specific topic and your request. Keep `test_only: true` while evaluating the result. `visual_review: "required"` is the default for new playbook batch jobs.

Inspect the actual [writer prompt](../../../Resources/Prompts/movie_countdown.writer.json) and [director contract](../../../Resources/Prompts/director-schema.json) rather than inventing unsupported settings. Source and media IDs come from the local registry, not arbitrary paths in model output.

## Execution and outputs

Film/theme research → source-backed original reasons → frozen rank plan → narration → matching named cards/clips → readability/relevance and technical review.

Run the saved plan from the project root:

```powershell
.venv\Scripts\python.exe run_pipeline.py --env-file .env batch-run --plan Resources/Plans/my-new-plan.json
.venv\Scripts\python.exe run_pipeline.py batch-status --plan Resources/Plans/my-new-plan.json
```

`my-new-plan.json` is a filename you create; it is not a shipped runnable example. Missing essential inputs hold the batch. Outputs go to the plan's `output_root/<plan-id>/<item-id>/`, normally under `Resources/Productions/`, with script, voice, scene plan, captions, metadata, QA and video. Resuming an unchanged completed plan reuses its jobs.

## Review and remaining work

The preset, rank rendering and input holds are implemented/tested. A complete approved real nine-film episode and its usable asset set have not been demonstrated. Fast montage, film quiz and poster/GIF verdict variants are separate proposals.

Watch the actual whole video and listen to speech/music. Check the opening promise, causal ending, actual media relevance, names, full readable dialogue and timing. Sampled frame review cannot assess the complete audiovisual experience. Technical readiness and creative approval are separate.

No completed real-content pilot is established for this category.

Read the [dated research](../../../research/formats/education-and-movies/PLAYBOOK_COUNTDOWNS_EDUCATION.md), [rendering limits](../../../Resources/Templates/README.md), [role index](../../../agents/README.md) and [current status](../../PROJECT_STATUS.md).
