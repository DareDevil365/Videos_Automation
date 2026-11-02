# Publisher

## Purpose

Publish only a checked exact version to the verified channel under configured private/scheduled policy.

## Inputs and handoff

Inputs: Ready non-test job, exact-version approval, OAuth and explicit channel publication mode.

Output to the next role: Durable upload session/offset/video ID and reconciled remote state.

## Implementation

- [publishing.py](../../src/yt_pipeline/publishing.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

## Validation and current limits

Simulated resumable upload, lost-response recovery and identity guards pass. Both real profiles remain disabled with no OAuth/upload records.

Next work: Validate owner OAuth, one private upload, recovery and scheduling on the actual channels.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
