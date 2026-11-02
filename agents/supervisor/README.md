# Supervisor and growth analyst

## Purpose

Surface operational incidents and collect honest owned-channel performance observations.

## Inputs and handoff

Inputs: Local job/asset state; authorized published video IDs for remote checks.

Output to the next role: Local alerts, paused-channel incident state, 24h/72h/7d observations and growth hypotheses.

## Implementation

- [monitor.py](../../src/yt_pipeline/monitor.py)
- [benchmarks.py](../../src/yt_pipeline/benchmarks.py)
- [cli.py](../../src/yt_pipeline/cli.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

## Validation and current limits

Local supervision and mocked analytics work; no real observations exist. Alerts are local. Growth grouping currently uses checkpoint/channel, not format and duration cohorts.

Next work: Connect remote observations/notifications and improve matched-cohort analysis after real publishing.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
