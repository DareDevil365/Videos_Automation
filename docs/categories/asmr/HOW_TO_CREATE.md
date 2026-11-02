# Create: generated ASMR

This route packages an actual generated clip, preserving its source audio. An owner-imported download already exported; automatic provider generation has not been demonstrated on the real Google interface.

## Inputs and workflow

1. Prepare an original visual action with a clear payoff. Use an actual generated download with provenance, or the browser-worker route after real selector/model/allowance calibration.
2. The browser route uses `generation-create`, `generation-plan`, `generation-run`, `generation-import` and `generation-use`; inspect `--help` before invoking each. Create/preview actions do not prove generation. Real submission needs proven free/included cost and explicit calibrated controls.
3. To package an existing supplied clip, create a new legacy batch item with `kind: "asmr"`, safe unique `id`, and an actual `source_file`. Use the version-1 batch shape from the [category index](../README.md), replacing the playbook item with this legacy item. Keep a new plan ID; an initialized source is hash-bound.
4. Run `batch-run --plan Resources/Plans/my-asmr-plan.json` with `--env-file .env` as in the shared guide. The current legacy route imports the provided file and creates a test-only source-clip job. It does not regenerate the file in Google.
5. Watch/listen for subject cropping, source quality, action/payoff, loop discontinuity and original sound. Exported files include source provenance and ordinary QA/package records.

The original ASMR prototype (local-only: `Resources/Productions/prototype-2026-11-02/asmr-flower/video.mp4`) is about 10 seconds. Its source is landscape 640×360, uses blurred fill and has a nonseamless ending. Do not treat that clip as proof of native vertical HD, a perfect loop, approved creative quality or a live browser generation integration.

Implementation: [browser_agent.py](../../../src/yt_pipeline/browser_agent.py), [generation_settings.py](../../../src/yt_pipeline/generation_settings.py), [batches.py](../../../src/yt_pipeline/batches.py) and [clips.py](../../../src/yt_pipeline/clips.py). Review the [generation role](../../../agents/generation/README.md) and [current status](../../PROJECT_STATUS.md).
