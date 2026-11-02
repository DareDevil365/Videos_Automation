# Validation map

Run the full behavioral suite from the root with `.venv\Scripts\python.exe -m pytest -q`. The editorial update passed 210 tests in 118.40s with two existing Pillow deprecation warnings; the earlier audit passed 183. The [code walkthrough](../docs/CODE_WALKTHROUGH.md#9-tests-tools-and-examples) explains each test file.

| Area | Files |
| --- | --- |
| Hook selection, separate payoff review/holds, speech segments/silence/cache, new graphics/quiz timeline/export | `test_editorial_improvements.py` |
| State, contracts, provider cache/quotas, upload simulations | `test_pipeline.py` |
| Real pipeline exports, original source audio, HTTP controls | `test_pipeline_integration.py` |
| Source/media/music/transcript adapters | `test_agents.py` |
| Creative plans, voices/captions, framing, education/media constraints | `test_playbooks.py` |
| Actual image transport, sampled verdicts, blocks/library | `test_visual_review.py` |
| Unit-bound shots and original story props | `test_storyboard.py` |
| Browser settings and submission/download fixtures | `test_generation_worker.py` |
| Batch leases/recovery/export integrity | `test_batches.py` |
| Native child process/pause command behavior | `test_control.py` |
| Real compositor layouts/effects/audio | `test_composition.py` |
| Legacy editor rendering, HTTP isolation and cancellation | `test_editor.py` |

Controlled renders verify timing/pixels/audio, not audience approval. Fake YouTube transports and local browser pages do not demonstrate real accounts. Keep provider calls/account side effects out of the ordinary test suite. Run `python tools/check_project_docs.py` separately after documentation moves.
