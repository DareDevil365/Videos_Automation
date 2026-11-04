# Create: landscape illustrated storytelling

Preset: `illustrated_story`, entertainment channel, 75-130 seconds, 180-270 spoken words and 12-18 units. This is an implemented chapter-length landscape route, not a 6-10 minute episode orchestrator. It uses original registered illustrations, one local voice-only narrator, source-camera moves, optional bounded rain/light effects and optional source-coordinate callouts. It does not rig bodies or produce lip-sync.

## Owner-requested one-off assistant direction

For **The Last Light**, the owner explicitly asked the assistant to write/direct instead of Gemini. [The script](../../../examples/storytelling-last-light.json) is labelled original provided fiction, and [the local builder](../../../tools/create_storytelling_pilot.py) supplies its direction through a closed provider that accepts only the prepared director operation. Any other model-generation request raises an error. The builder never loads API credentials, compares Gemini usage before/after and keeps publishing disabled/test-only. Its prepared review flags are assistant assertions, not independent model review or owner approval.

Six selected built-in imagegen files and `prompts.json` must exist in the art directory. The project-local originals are `Resources/Drafts/the-last-light-art/01.png` through `06.png`; the prompt record includes the costume correction. Generated media is ignored by Git, so a fresh clone must supply/generate those inputs rather than expect them to be in the repository.

```powershell
.venv\Scripts\python.exe tools/create_storytelling_pilot.py --art Resources/Drafts/the-last-light-art
```

The default export is `Resources/Productions/the-last-light-20261105/`. The state binds the exact script/art/prompts; use a fresh output directory after changing them. Resume uses normal pipeline checkpoints for research, script, local speech/alignment, visuals, direction, render, technical QA and packaging. Do not edit hashed job records. Inspect the whole output and the actual art before accepting it.

## Renderer/data flow

Prepared script and immutable direction -> local Kokoro -> exact-script word alignment -> one measured landscape shot per unit -> full-frame composition -> landscape ASS captions -> decode/dimension/audio checks -> checked export copies and origin/usage record. A narrator never receives a face or costume. Shared rescue scenes actually include the keeper, Mara and Pip.

`src/yt_pipeline/illustrated_story.py` requires original-graphic image assets and ordered unit coverage. A repeated image needs an explicit continuity/detail/payoff reason. `illustration_effects` maps actual unit IDs to normalized `crop_start`/`crop_end`, optional `flash_box`, optional `callout_box`/`target`, and `rain`. Boxes use [left, top, right, bottom] coordinates in the source image and remain inside [0,1]. Crop and callout share the source transformation; overlays are frame-timed rather than a frozen graphic on top of a moving camera. The supplied window/paw closeups are intentional returns to planted clues.

The underlying compositor's explicit `documentary` profile provides a 1280x720 or 1920x1080 canvas for full-frame `focus` composition. The name describes the landscape chapter profile and is also used by this fictional pilot. Existing short profiles retain portrait dimensions and the 180-second project limit; chapter profiles retain that limit too. Longer episode assembly remains a separate milestone.

The preset also exposes normal program writing/directing when an explicit API-enabled request supplies matching original illustration IDs. That autonomous route is not what generated this one-off demonstration and is not live-validated by it. There is no automatic story-art acquisition in the standalone runtime.
