# Agent roles

One folder per responsibility. The executable implementation is a single Python application with stage functions, adapters and a local worker. Role guides and the four preserved research briefs do not launch services or recurring assistants.

| Role guide | Responsibility |
| --- | --- |
| [Coordinator and queue](coordinator/README.md) | Turn the selected topic/category into an inspectable request or immutable batch; own handoffs and current status. |
| [Entertainment researcher](research-entertainment/README.md) | Find source-backed reference premises and original fiction opportunities with a complete payoff. |
| [Education researcher](research-education/README.md) | Build a small supported lesson/demo about useful AI, study, confidence or jobs/skills. |
| [Source and rights reviewer](source-and-rights/README.md) | Record exact source/asset conditions and keep provenance attached to production. |
| [Scriptwriter and story reviewer](writer/README.md) | Write original structured dialogue or factual units, then perform bounded evidence/creative review. |
| [Voice and captions](voice/README.md) | Turn exact script units into measured local speech and readable full-dialogue captions. |
| [Media and music librarian](media/README.md) | Acquire or reuse registered media and bind real subjects to the intended scene. |
| [Browser generation worker](generation/README.md) | Plan settings, inspect an explicit provider page, submit once and import/download a result. |
| [Director and visual editor](director/README.md) | Convert frozen dialogue and actual media into supported timed scenes and a compositor recipe. |
| [Quality reviewer and packager](quality/README.md) | Check exported bytes and sampled images, then package exact outputs with evidence. |
| [Publisher](publisher/README.md) | Publish only a checked exact version to the verified channel under configured private/scheduled policy. |
| [Supervisor and growth analyst](supervisor/README.md) | Surface operational incidents and collect honest owned-channel performance observations. |

## Handoffs

Coordinator → researcher/source reviewer → writer and bounded director critique → voice/captions → media and visual builder → director → renderer → quality/package → separately enabled publisher → supervisor/observations.

Some steps share a model call or overlap in implementation; [the code walkthrough](../docs/CODE_WALKTHROUGH.md) gives the exact execution order. Rendering lives in [shorts_editor](../src/shorts_editor), and [tests](../tests) validate the roles together.

For a new video, choose a [category recipe](../docs/categories/README.md), then inspect the owning role guide. Check [status](../docs/PROJECT_STATUS.md) for what is implemented versus still awaiting activation or creative validation. Delegation to additional assistants requires authorization; these folders are not that authorization.
