# Scriptwriter and story reviewer

## Purpose

Write original structured dialogue or factual units, then perform bounded evidence/creative review.

## Inputs and handoff

Inputs: Validated brief, playbook constraints, concept and available media.

Output to the next role: script.json with origin, units, hook, payoff, metadata, reviews and frozen creative plan.

## Implementation

- [writer.py](../../src/yt_pipeline/writer.py)
- [contracts.py](../../src/yt_pipeline/contracts.py)
- [playbooks.py](../../src/yt_pipeline/playbooks.py)
- [creative_plan.py](../../src/yt_pipeline/creative_plan.py)
- [comedy.py](../../src/yt_pipeline/comedy.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

## Validation and current limits

Live Gemini writing works; exact dialogue/speaker/hook and one substantive rewrite limits are tested. Humor and causal story logic remain unreliable.

Next work: Improve coherent setups/payoffs and prove several owner-accepted episodes per category.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
