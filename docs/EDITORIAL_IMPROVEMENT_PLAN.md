# Editorial improvements: implementation plan

Prepared 2 November 2026 after reviewing the supplied implementation recommendations and script playbook against the current source. This plan selects their useful ideas and corrects incompatible snippets. It is the work plan for this change, not a claim of measured retention or completed live account integration.

## Scope and sequence

1. **Hook and editorial contracts.** Add format-aware hook checks for newly initialized playbook batches. Generate three typed hook alternatives inside the existing writing call, validate the selected line/caption, and record the choice. Source clips and short caption-only aura edits keep their own contracts. Add an optional separate skeptical editorial call that must identify the exact existing payoff unit/text, preserve factual review, propagate provider holds and share the existing single-rewrite budget. New batches enable these checks; existing immutable requests remain reproducible.
2. **Structured speech delivery.** Keep exact clean dialogue as the source of truth. Optional director speech segments select bounded speed and real internal silence without embedding control tags in captions. Validate complete ordered text coverage, write a complete per-unit audio file, and include timing/delivery changes in cache identity. Preserve preset/cast voices, measured durations, word alignment and mono/sample-rate/audio checks.
3. **Reusable education recipes.** Add `rewrite_reveal`, `myth_fact` and `quiz_pause` using the existing education scene renderer. Original typography is explicit; a named tool/interface or external evidence still needs actual matching media. Required graphics must cover every beat. Myth/fact gets honest headings, rather than mislabeling the cards before/after. A quiz has exactly one bounded thinking interval after its spoken question/instruction and before its answer.
4. **Visible quiz timing.** Extend the actual graphic schema, validation, renderer and measured audio timeline together. Render a countdown during real silence, keep captions out of that silence, and preserve downstream voice/shot/QA timing. A dictionary entry alone is not an executable feature.
5. **Verification and documentation.** Add meaningful contract/provider-hold/audio/timing/render regressions; run the full suite. Export current prompt contracts and update role/category guides, code walkthrough, status and root architecture guide. Produce a clearly labeled offline technical example where local inputs permit; do not spend provider allowance merely to validate code.

## Design choices

- Hook options share the writing call; the additional editorial pass is explicit and budgeted. Successful content-bound caches and upstream checkpoints remain reusable.
- Structural rules are enforced in code. The model's judgement about humor, comprehension and payoff is fallible and is saved as an opinion with exact supporting text.
- Spoken text and presentation metadata remain separate. No `[P]`/`[FAST]` tags may leak into new playbook speech/captions. A structured segment changes delivery, not the script's words or speaker.
- Existing playbook voices and the selected female horror narrator are retained. No new global voice/profile table is needed.
- Timing is measured from actual assembled audio. A countdown consumes actual thinking time; changing a picture alone cannot create a pause.
- Comment questions are optional, appear only after the delivered answer, and create no promise of automated pinned comments or replies.
- New playbook batch requests enable hook alternatives, strict hook review and the separate editorial check. Direct older requests retain their prior defaults unless explicitly enabled. The three new education presets select their own complete graphic/request defaults.

## Deliberately deferred

Photo-head expression changes, chat typing overlays and actual music beat synchronization require separate asset/timeline contracts and accepted creative tests. They are not implemented by editing the unused legacy cartoon renderer, encoding a transparent overlay as opaque H.264, or choosing arbitrary short shots. The existing explicit `shot_durations` remains usable. No automatic external commenting, paid fallback, account activation, copied third-party implementation or audience-performance claim is added.

## Completion evidence

All five implementation phases above are complete. The new runtime modules are `script_quality.py` and `speech_delivery.py`; writer/director, voice, batch defaults, trusted graphics, packaging and prompt export are integrated. Nine presets and eleven category creation guides are available. The retained voice/profile system is extended rather than replaced.

The full suite passed **210 tests in 118.40s**, with two pre-existing Pillow deprecation warnings. Coverage includes invalid hook choice/caption, provider quota/budget propagation, exact payoff/issue rejection, at most one substantive rewrite, graphic requirements, timer positioning/count, exact speech coverage, finite speed/pause bounds, cached audio reuse, real inserted silence, real timer frames and a complete synthetic-speech quiz export. Controlled provider verdicts and synthetic speech are explicitly fixtures.

A separate actual local Kokoro/English-alignment rewrite example completed at local-only `Resources/Productions/editorial-rewrite-demo/`: **25.333 seconds**, **77/77 aligned words**, full video/audio decode and technical QA pass, 0.35 seconds of actual internal zero-valued audio (8,400 samples at 24 kHz), and zero Gemini calls. Four sampled frames were visually checked for readable opening/comparison/dialogue. Script origin is provided original content; plan origin is `offline_prepared_fixture`. Model editorial and frame review are explicitly off for this test-only example. No new live Gemini prompt result, subjective listening verdict, source recheck, owner approval or audience measurement is claimed.

The run is reproducible/resumable with [the offline tool](../tools/create_editorial_demo.py); a fresh clone supplies a prepared source brief and local speech/alignment models. Deferred expression/typing/beat work remains listed above. Final documentation/navigation and unchanged-artifact checks are recorded in the root project guide.

Final verification: 74 documents/480 local links pass; all 53 runtime source modules are mapped; prompt JSON/Python syntax and diff whitespace checks pass. All 523 saved references across the original sixteen ready jobs and new demonstration retain their hashes. The source/guide update uses the existing authorized GitHub repository, excluding local demo/runtime artifacts.
