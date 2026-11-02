# Quality reviewer and packager

## Purpose

Check exported bytes and sampled images, then package exact outputs with evidence.

## Inputs and handoff

Inputs: Render, source/script/voice/director evidence and requested review mode.

Output to the next role: quality.json, metadata/package JSON, visual-review reports and contact sheets.

## Implementation

- [quality.py](../../src/yt_pipeline/quality.py)
- [visual_review.py](../../src/yt_pipeline/visual_review.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

## Validation and current limits

Full decode/dimensions/audio and sampled Gemini-frame checks exist. Only the latest typography pilot demonstrates live finished-frame review; it has no external-media bindings.

Next work: Validate real source relevance and audio delivery; visual repair and complete audiovisual review are not implemented.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
