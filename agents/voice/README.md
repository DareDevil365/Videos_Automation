# Voice and captions

## Purpose

Turn exact script units into measured local speech and readable full-dialogue captions.

## Inputs and handoff

Inputs: Frozen units, speaker IDs, selected voice and delivery/pause plan.

Output to the next role: Per-unit WAVs, assembled narration, voice.json, SRT and optional word timings.

## Implementation

- [voice.py](../../src/yt_pipeline/voice.py)
- [dialogue_captions.py](../../src/yt_pipeline/dialogue_captions.py)
- [transcripts.py](../../src/yt_pipeline/transcripts.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

## Validation and current limits

Kokoro/Piper and local English alignment were exercised. Every word is preserved on the tested dialogue route; estimated timing repairs are marked.

Next work: Review pronunciation/emotion and test other languages; frame review does not assess audio.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
