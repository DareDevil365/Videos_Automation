# Content categories: how to create

Each category has a dedicated `HOW_TO_CREATE.md` with prerequisites, request fields, actual pipeline behavior, review steps and current limits. Guides describe supported routes; they do not mean every category has an approved finished episode.

| Category guide | Runtime preset/route | Channel |
| --- | --- | --- |
| [Rewrite reveal](rewrite-reveal/HOW_TO_CREATE.md) | `rewrite_reveal` | education |
| [Myth versus fact](myth-fact/HOW_TO_CREATE.md) | `myth_fact` | education |
| [Quiz with thinking time](quiz/HOW_TO_CREATE.md) | `quiz_pause` | education |
| [Original horror and mystery](horror/HOW_TO_CREATE.md) | `horror_stock` | entertainment |
| [Fictional chat and tea stories](chat/HOW_TO_CREATE.md) | `tea_chat` | entertainment |
| [Phone-screen stories: comedy, mystery, thriller](phone-story/HOW_TO_CREATE.md) | `phone-plan` / `server_chat` v2 + `phone_story` | entertainment |
| [Full-screen original server-chat comedy](server-chat/HOW_TO_CREATE.md) | `server_chat` | entertainment |
| [Landscape illustrated storytelling](illustrated-story/HOW_TO_CREATE.md) | `illustrated_story` | entertainment |
| [Documentary chapter: live route pending](documentary/HOW_TO_CREATE.md) | `documentary_chapter` | education |
| [Character cutout stories and comedy](cutout-comedy/HOW_TO_CREATE.md) | `cutout_ensemble` | entertainment |
| [Aura progression edits](aura/HOW_TO_CREATE.md) | `aura_progression` | entertainment |
| [Useful education and demonstrations](education/HOW_TO_CREATE.md) | `education_demo` | education |
| [Nine-pick movie countdowns](movies/HOW_TO_CREATE.md) | `movie_countdown` | entertainment |
| [Permitted source clips](source-clips/HOW_TO_CREATE.md) | registered source → transcript → clip | entertainment |
| [Generated ASMR](asmr/HOW_TO_CREATE.md) | imported/generated source → legacy ASMR batch | entertainment |

## Shared playbook batch recipe

1. Choose a category, read its guide and gather its actual inputs.
2. Run `run_pipeline.py --env-file .env doctor` from the root. Check actual local quota/cooldown rather than assuming historical audit counts still apply; completed cached jobs can resume.
3. Register the chosen assets with evidence using `asset`/`media-get`/`music-register`, or use existing eligible IDs. Inspect each command's `--help`; do not substitute a path for an expected ID.
4. Save a new version-1 plan in `Resources/Plans/`. Give the plan and each item a unique stable ID. A minimal shape is shown below; replace the category and required request inputs before running.
5. Run the batch commands in the category guide. Missing prerequisites hold before model work where supported.
6. Inspect the resulting files and whole video. Keep evaluation prototypes test-only. Publication requires its separate configured account/policy route.

```json
{
  "version": 1,
  "id": "my-new-plan",
  "output_root": "Resources/Productions",
  "items": [{
    "id": "episode-01",
    "kind": "playbook",
    "playbook": "education_demo",
    "channel": "education",
    "topic": "A specific supported practical demonstration",
    "request": {
      "fiction": false,
      "test_only": true,
      "require_music": false,
      "bottom_kind": "none",
      "visual_review": "required"
    }
  }]
}
```

This is an illustrative plan shape, not a complete ready-to-run factual request: add actual source evidence and appropriate matching media or supported original graphic scenes. Run commands from the project root because relative plan paths resolve there. Do not mutate an initialized plan or manually edit hashed job results. Copy to a new plan ID when changing content. New batches enable hook alternatives/strict checks and separate editorial review; see [editorial and speech controls](../EDITORIAL_AND_SPEECH.md). The three new education presets require an original graphic on every beat, without random stock substitution.

## Researched variants still needing work

The [entertainment catalog](../../research/formats/entertainment/ENTERTAINMENT_FORMATS.md) covers E01–E18, including creator/podcast breakdowns, reaction/sigma clips, alternate show stories, gameplay challenges, simulations, deduction puzzles, choose-a-reply comedy, sound comedy, poster/GIF verdicts and controversy/mystery. Some can use shared primitives; they are not all separately implemented end-to-end playbooks. The fast movie montage, film-specific quiz and aura event/reaction presets remain proposals; the new original education quiz is a separate implemented route.

The [education catalog](../../research/formats/education-and-movies/EDUCATION_FORMATS.md) contains EDU-F01–F15: before/after tasks, prompt repair, free-tool checks, proof-of-skill projects, interview repair, retrieval practice, schedules, if–then plans, task breakdowns, communication, scam checks, earning/journey analysis, job requirement maps, source checking and learning-path choices. They share the education route; each still needs actual topic evidence and demonstration work. They are not fifteen separately completed tools.

For example selection, use the category guides and current owner feedback. The supplied Python request is retained for technical tests, while the rejected generic procrastination and early mystery/aura styles are not approved starting points.
