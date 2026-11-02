# Browser generation worker

## Purpose

Plan settings, inspect an explicit provider page, submit once and import/download a result.

## Inputs and handoff

Inputs: Prompt, calibrated selectors/capabilities, chosen browser route and proven free/included allowance.

Output to the next role: Generation job record, downloaded asset and dependency resolution.

## Implementation

- [browser_agent.py](../../src/yt_pipeline/browser_agent.py)
- [generation_settings.py](../../src/yt_pipeline/generation_settings.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

## Validation and current limits

Local browser fixtures cover cost/settings read-back and no-duplicate submission. Real Google page/account generation is unverified; owner-imported output is not proof.

Next work: Calibrate real pages/settings and demonstrate one end-to-end generated asset without changing cost policy.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
