# Entertainment researcher

## Purpose

Find source-backed reference premises and original fiction opportunities with a complete payoff.

## Inputs and handoff

Inputs: Entertainment catalog, current topic, dated references and any registered source catalog.

Output to the next role: Research brief with dated sources/claims, or an explicitly fictional premise.

## Implementation

- [research.py](../../src/yt_pipeline/research.py)
- [editorial.py](../../src/yt_pipeline/editorial.py)
- [benchmarks.py](../../src/yt_pipeline/benchmarks.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

The preserved [detailed research brief](RESEARCH_BRIEF.md) records the original research workflow and its boundaries.

## Validation and current limits

Public-source and live Gemini paths exist. Public discovery key and recurring feeds are not configured; search metrics do not prove audience fit.

Next work: Curate repeatable sources and validate real channel topics; generic trend-to-playbook planning is incomplete.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
