# Source and rights reviewer

## Purpose

Record exact source/asset conditions and keep provenance attached to production.

## Inputs and handoff

Inputs: Source URLs/files, actual reuse evidence, expiry and permitted operations.

Output to the next role: Registered asset/source profile, attribution, transcript identity and explicit held reasons.

## Implementation

- [assets.py](../../src/yt_pipeline/assets.py)
- [source_agent.py](../../src/yt_pipeline/source_agent.py)
- [net.py](../../src/yt_pipeline/net.py)
- [contracts.py](../../src/yt_pipeline/contracts.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

The preserved [detailed research brief](RESEARCH_BRIEF.md) records the original research workflow and its boundaries.

## Validation and current limits

Hash/expiry/eligibility and source-profile tests pass. No registered live source profiles currently exist. Records do not independently certify rights.

Next work: Populate a permitted source catalog and validate one complete real creator/source route.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
