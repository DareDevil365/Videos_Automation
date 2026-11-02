# Reusable production resources

Start with the [category creation guides](../docs/categories/README.md), [current status](../docs/PROJECT_STATUS.md) and [code walkthrough](../docs/CODE_WALKTHROUGH.md). Folder indexes: [plans and input records](Plans/README.md), [writer/director prompts](Prompts/README.md), [templates and limits](Templates/README.md), [review exports](Productions/README.md). Existing plan/media/export paths are preserved for recovery and traceability.

Repository-inspired upgrade: `run_upgrade_demo.cmd` resumes the saved education motion-block pilot. Comparison, process and callout blocks render locally from Gemini's supported JSON. Finished review contact sheets and verdicts are exported beside the video under `visual-review/`. New playbook batch jobs require source/finished-frame checks; legacy exports remain unchanged. The checks share the configured Gemini free-tier call budget and do not assess audio or predict views.

Find reusable registered media with `.venv\Scripts\python.exe run_pipeline.py library-search "dark library" --kind image`. Results are text-matched candidates with current eligibility/integrity checks, not automatic proof of visual relevance.

Double-click `start_pipeline.cmd` in the project root to open the standalone controls. ChatGPT/Codex does not need to be open.

1. **Start batch** runs or resumes the selected saved plan. It reuses completed results rather than generate duplicates.
2. **New plan** creates a horror/chat/aura playbook starter batch. Explicit music and aura visual prerequisites must be configured; missing inputs hold before generation. It does not start generation until you press Start. Review the selected source and scope before large batches.
3. **Pause after this video** finishes the current video, then stops before the next one.
4. **Check status** shows progress. **Open produced videos** opens the output library.

The runtime uses configured Gemini free-tier text requests, local Kokoro/Piper and FFmpeg. It has no ChatGPT/OpenAI runtime dependency. Existing Google browser access is a different integration: real AI Studio generation is still unverified and the current batch imports the owner's downloaded ASMR clip. Nothing is published automatically.

## Folder map

- Root MP4 files: owner-supplied generation downloads. The starter plan captures a specific source; later resumes do not silently select another file.
- `Plans/`: saved production plans. Once started, a plan is immutable; create a new one for changed work.
- `Productions/<batch-id>/<video-id>/`: videos, covers, captions, script/research/voice/edit records and quality results.
- `Prompts/`: exported Gemini writing presets, director schema and editing dictionary.
- `Templates/`: how the editing blocks work, with a local cast-framing demo.
- `Music/Original/`: historical synthesized music tests; rejected as the new-format automatic fallback.

Source media can be reused in meaningful new edits when its recorded terms allow it. Reuse does not make a loop seamless, improve its quality or make duplicate ASMR reposts distinct original content. Keep credits and provenance with each export. Never save API keys, account cookies or login files in this library.

The first completed prototype batch is `Productions/prototype-2026-11-02/`: supplied clay ASMR, a Gemini-written illustrated mystery and a Gemini-captioned portrait/gameplay aura test. These are creative prototypes, not approved final channel style or monetization evidence.

See [PROJECT_GUIDE.md](../PROJECT_GUIDE.md) for setup, architecture, limitations and validation.

The new-format detailed operating guide is [Templates/README.md](Templates/README.md). Productions/playbook-refinement/tea-chat/video.mp4 (local-only: `Resources/Productions/playbook-refinement/tea-chat/video.mp4`) is a 35-second standalone-generated technical chat pilot with three local voices. It remains test-only because the story logic needs improvement; it is not approved publishing content.

The control panel and CLI now default to `Resources/Plans/playbook-starter.json`; legacy `prototype-batch.json` remains selectable for inspecting/resuming historical exports. Starter IDs use `playbooks-` to avoid colliding with completed legacy batch folders.
