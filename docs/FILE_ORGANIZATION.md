# File organization

Organized on 2 November 2026. This is a navigation/documentation change; Python package paths, launchers, examples, media, immutable production plans and runtime checkpoints retain their locations.

## Why the layout looks like this

Agent work is separated into role folders under `agents/`. Each role README names its inputs, output, implementation modules, validation and unfinished work. The older four research briefs are preserved inside their corresponding role folders. These folders do not install or launch independent services: one Python application currently implements the roles. Moving its modules into agent folders would add import and packaging changes without making the roles more autonomous.

`docs/categories/<category>/HOW_TO_CREATE.md` explains each implemented creation route. The category index also points to researched variants that still need implementation. `docs/CODE_WALKTHROUGH.md` covers the whole source tree. `docs/PROJECT_STATUS.md` is the current readiness/backlog reference. The root `PROJECT_GUIDE.md` remains the architecture and decision record.

The editorial update adds three education guides (eleven category guides total), two runtime modules (`script_quality.py`, `speech_delivery.py`), an implementation plan/operating contract and an offline demo tool. Existing data/plan/export locations remain stable; generated demo media is still private/local-only.

Research is grouped into `strategy`, `formats`, `sources-and-safety`, `references`, `revenue`, `repositories`, `investigations` and `archive`. Original research filenames are retained so they remain recognizable. [FILE_MOVES.json](FILE_MOVES.json) records every moved file and its destination. Relative Markdown links were updated with the moves.

## Stable data locations

- `Resources/Plans/`: saved production inputs; do not rearrange initialized plans casually.
- `Resources/Prompts/`: generated writer/director contracts; regenerate from code rather than edit competing copies.
- `Resources/Templates/`: rendering capability guide and visual previews.
- `Resources/Productions/`: review exports grouped by production/batch. Their old names are retained for traceability.
- `data/pipeline/`: SQLite state, credentials, copied inputs, voice models, caches and hashed job artifacts. Keep private and back up as a unit.
- `data/editor/`: compositor projects, imported media, previews and render history.
- `.venv/`, `build/`, `output/`, `tmp/`: environment/build/generated/working material. No bulk cleanup or deletion was performed.

Checkpoint JSON contains absolute file paths and hashes. Moving a job or source asset can break recovery or approval, so this organization keeps those files intact. A future migration would need to update and validate the saved state deliberately.

## Adding future work

1. Add or update the category recipe and the owning agent README.
2. Keep executable Python in the appropriate package; use the walkthrough to find it.
3. Store dated evidence in the relevant research folder and link it from the research index.
4. Update current status and affected architecture sections when behavior changes.
5. Save new production content under a new plan ID instead of changing an initialized plan.
6. Run `python tools/check_project_docs.py` after moving documentation. Run behavioral checks when implementation changes.

Recorded design choice: retain the existing single-PC Python/Pillow/FFmpeg/SQLite system. The organization favors readable entry points over a large runtime refactor. The research archive preserves past decisions without treating past status as present capability.

## GitHub source distribution

The GitHub repository publishes the source packages, tests, examples, guides, role briefs, research, prompt contracts and tools. `.gitignore` excludes runtime data/credentials, the virtual environment, build/temp outputs, machine-specific plan JSON, generated production/preview media, music and the generated PDF. Folder README files remain available so a fresh clone explains where local inputs/outputs belong. Generated contracts can be rebuilt; actual source media and voice models must be supplied or installed locally.

The source distribution deliberately does not move or rewrite saved private production files. Its documentation labels references to those files as local-only rather than publishing broken download links. The dated job counts/acceptance records describe the audited local workspace, not artifacts included in a fresh clone.
