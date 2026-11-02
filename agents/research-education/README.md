# Education researcher

## Purpose

Build a small supported lesson/demo about useful AI, study, confidence or jobs/skills.

## Inputs and handoff

Inputs: Question, accessible primary source URLs and actual demonstration artifacts.

Output to the next role: Source-linked claims, a bounded learning takeaway and factual brief.

## Implementation

- [research.py](../../src/yt_pipeline/research.py)
- [editorial.py](../../src/yt_pipeline/editorial.py)
- [contracts.py](../../src/yt_pipeline/contracts.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

The preserved [detailed research brief](RESEARCH_BRIEF.md) records the original research workflow and its boundaries.

## Validation and current limits

Dated excerpts and claim IDs are checked. Real factual writing/export ran; source truth and useful teaching still need review.

Next work: Collect actual tool demonstrations and researched real journeys; do not treat the historical Python fixture as an approved channel topic.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
