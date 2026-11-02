# Coordinator and queue

## Purpose

Turn the selected topic/category into an inspectable request or immutable batch; own handoffs and current status.

## Inputs and handoff

Inputs: Topic, channel, category prerequisites, current guide and recorded choices.

Output to the next role: Stable job IDs, batch manifest, held reasons and review exports.

## Implementation

- [core.py](../../src/yt_pipeline/core.py)
- [pipeline.py](../../src/yt_pipeline/pipeline.py)
- [batches.py](../../src/yt_pipeline/batches.py)
- [control.py](../../src/yt_pipeline/control.py)
- [cli.py](../../src/yt_pipeline/cli.py)
- [dashboard.py](../../src/yt_pipeline/dashboard.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

The preserved [detailed research brief](RESEARCH_BRIEF.md) records the original research workflow and its boundaries.

## Validation and current limits

Batch leases, job leases, restart recovery and changed-artifact checks are tested. PC must remain awake; no distributed/cloud scheduler is installed.

Next work: Configure recurring sources and validate a realistic daily production cadence.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
