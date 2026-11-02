# Director and visual editor

## Purpose

Convert frozen dialogue and actual media into supported timed scenes and a compositor recipe.

## Inputs and handoff

Inputs: Script/creative plan, measured voice timing, registered visual inputs.

Output to the next role: visuals.json, direct.json, compose-job.json and versioned project.

## Implementation

- [director.py](../../src/yt_pipeline/director.py)
- [creative_plan.py](../../src/yt_pipeline/creative_plan.py)
- [planned_visuals.py](../../src/yt_pipeline/planned_visuals.py)
- [visuals.py](../../src/yt_pipeline/visuals.py)
- [storyboard.py](../../src/yt_pipeline/storyboard.py)
- [montage.py](../../src/yt_pipeline/montage.py)
- [entertainment.py](../../src/yt_pipeline/entertainment.py)
- [scene_blocks.py](../../src/yt_pipeline/scene_blocks.py)
- [edit_blocks.py](../../src/yt_pipeline/edit_blocks.py)
- [cast_body.py](../../src/yt_pipeline/cast_body.py)

These are modules inside one local application. This folder describes a role; it does not create an independently running agent.

## Validation and current limits

Local effects, blocks, framing, captions and real renders are tested. Silhouette bodies have no facial acting, rigs or lip sync.

Next work: Improve relevant footage, richer storytelling, music timing and animation; avoid unsupported generated code.

## Operating rule

Preserve upstream evidence and checkpoint hashes. Report missing inputs as holds; do not invent media, permission, observations or successful account actions. Use the selected Gemini budget and local tools. Changes to content need a new request/plan version rather than rewriting completed job artifacts.

Read the [category recipes](../../docs/categories/README.md), [current status](../../docs/PROJECT_STATUS.md) and [code walkthrough](../../docs/CODE_WALKTHROUGH.md) before changing this role.
