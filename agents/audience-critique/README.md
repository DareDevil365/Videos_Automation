# Audience critique agents

These are separate reusable reviewer roles in the local application. Invoke an audience pass after the writing stage, then optionally ask for a sampled-frame pass on the finished file. A critic receives the exact words/labels, relevant source claims and context, not the writer's title, self-grade or promised quality. The same configured text provider may be used in a fresh request; this is a simulated viewer perspective, not measured human attention.

| Role | Viewer test |
| --- | --- |
| `comic-lore` | Can a newcomer follow the cause, and does a comics fan see accurate canon and a real chapter payoff? |
| `movie` | Is there a usable recommendation or verified update, with actor, character, dates and speculation clearly separated? |
| `current-affairs` | Does an India/UPSC learner leave with the dated change and understand the scope, direction and terms? |
| `comedy` | Which exact reply first stops being funny, and does the last line change the situation? |
| `mystery` | Does anticipation have a fair clue, and is the reveal an answer instead of another unexplained question? |
| `story` | Is there a specific choice and earned emotional consequence? |
| `aura` | Does the action actually land, or do empty footage, repeated cuts and invented claims take over? |
| `ai-tools` | Can the viewer actually use the described feature under the stated price, location and eligibility limits? |
| `education` | Does the video explain and show the promised answer or step? |

```powershell
.venv\Scripts\python.exe run_pipeline.py --env-file .env audience-critique JOB_ID --role comic-lore --phase script
.venv\Scripts\python.exe run_pipeline.py --env-file .env audience-critique JOB_ID --role comic-lore --phase frames
```

Omit `--role` for automatic selection from the saved request/format. Each call uses the configured API and its existing quota rules. Frame mode samples up to ten actual frames after QA and needs a provider that supports images. The current OpenAI text-only adapter does not. No full video or audio is sent. A frame finding names a supplied frame ID, from which software attaches the real timestamp and hash. Script-only findings have no timestamps.

Every finding needs an exact spoken unit, severity, viewer consequence and concrete fix. If a critic says it would leave, it must identify the first unit and explain why. Changed checkpoints, fabricated quotes and unsupported frame references hold. The report saves separately under the job's `audience-critique` folder; it never rewrites or uploads the job. Start a deliberate revision after deciding which critique is valid. Its outcome is neither publication approval nor an audience metric.

Actual comic pilot records: [first critique](../../docs/reviews/comic-lore-pilot/SCRIPT_CRITIQUE.md) and [revision recheck](../../docs/reviews/comic-lore-pilot/REVISION_RECHECK.md). The [movie](../../docs/reviews/movie-pilot/SCRIPT_CRITIQUE.md) and [current-affairs](../../docs/reviews/current-affairs-pilot/SCRIPT_CRITIQUE.md) reviews are labelled main-assistant passes, because the separate runs hit a usage limit. The app's structured critic contract is tested independently of live provider availability.
