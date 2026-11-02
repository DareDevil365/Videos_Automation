# Media and music librarian

## Purpose

Acquire or reuse registered media and bind real subjects to the intended scene.

## Inputs and handoff

Inputs: Visual queries, unit-to-asset mappings, selected music category and evidence.

Output to the next role: Eligible registered media, source bindings, credits and library candidates.

## Implementation

- [media_agent.py](../../src/yt_pipeline/media_agent.py)
- [media_library.py](../../src/yt_pipeline/media_library.py)
- [music_agent.py](../../src/yt_pipeline/music_agent.py)
- [assets.py](../../src/yt_pipeline/assets.py)
- [source_agent.py](../../src/yt_pipeline/source_agent.py)
- [clip_agent.py](../../src/yt_pipeline/clip_agent.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

## Validation and current limits

Commons acquisition and local metadata search work; Pexels needs an optional key. Metadata matches can be irrelevant and require review.

Next work: Add richer media matching, actual suitable tracks and a validated licensed source library.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
