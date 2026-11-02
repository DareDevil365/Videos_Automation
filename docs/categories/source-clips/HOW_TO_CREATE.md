# Create: permitted source clips

This route preserves the exact source audio instead of synthesizing narration. It is separate from the six playbook presets.

## Inputs

An exact local recording or bounded list of episode URLs, recorded commercial/edit/download permission as applicable, attribution/expiry, and actual VTT/SRT subtitles or local transcription. A series name alone is insufficient. The local source catalog currently has no registered profiles.

## Workflow

1. Use `run_pipeline.py source-register --help` to prepare/register a source JSON. Required profile fields include a title, `local_media` or `urls`/`episodes`, and `permission.evidence`, `permission.commercial: true`, `permission.editing: true`. URL download additionally needs `permission.download_allowed: true`. Add `owner_recording: true` only when accurate, and `test_only: true` for fixtures.
2. Use `source-ingest` with that source ID. It registers the media, records profile/transcript hashes and imports subtitles or runs local faster-whisper.
3. Use `clip-agent` with the source ID and a concrete selection hint. Gemini selects actual cue indices; invalid/invented indices hold. The route creates bounded 5–60 second clip jobs and deduplicates exact source ranges.
4. Run the resulting job IDs through `run`. Original speech, actual subtitle ranges, cover, video and packaging use the normal pipeline. Optional gameplay needs its own eligible background.
5. Review the whole source context, selected start/end, transcript names, audible meaning and subtitles. No model selection establishes source truth or permission independently.

Inspect each command's `--help` for exact arguments before invoking it. [source_agent.py](../../../src/yt_pipeline/source_agent.py), [clip_agent.py](../../../src/yt_pipeline/clip_agent.py), [clips.py](../../../src/yt_pipeline/clips.py) and [transcripts.py](../../../src/yt_pipeline/transcripts.py) implement this route. `source-handoff` can map dated references to an existing permitted catalog; it does not build that catalog automatically.

## Current evidence and gaps

Technical fixtures exercise source audio, cue ranges and caption burn-in; local transcription has been used. A complete real permitted-source → download → selection → export pilot remains unverified. No arbitrary movie/source library, automatic permission discovery or account upload is established. Start with a small known source and keep evaluation output test-only.

Read [source-role instructions](../../../agents/source-and-rights/README.md), [media-role instructions](../../../agents/media/README.md) and [status](../../PROJECT_STATUS.md).
