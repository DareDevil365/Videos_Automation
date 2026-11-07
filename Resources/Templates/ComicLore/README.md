# Geometric comic starter assets

For the new ensemble stories, also reuse the code-native profiles in [lore_screen_cast.py](../../../src/yt_pipeline/lore_screen_cast.py). These preserve Deadpool's mask/swords, Wolverine's mask/claws, the Four's matching suits and individual powers, and the X-Men's identifying features. They are supported drawing profiles, not additional registered PNG files. Use their supplied hand anchor for contact and draw an action through the finite [ensemble scenes](../../../src/yt_pipeline/lore_ensemble.py); a static PNG alone does not animate a claw strike or energy transfer. [Worked examples](../../../examples/screen-recaps/ENSEMBLE_BATCH.md) explain the reuse/variation boundary.

The [catalog](catalog.json) lists transparent actor and prop layers by stable name. The PNGs are ready to place. They are drawn by the local editor's Python helpers. Use the existing actor body and change the head, hair and clothing when appropriate. Happy and Stane share a broad suit silhouette and have different faces, hair and wardrobe. Doom's mask keeps its shape across heat states. The Mark I helmet has its own blocky visor and cheek geometry.

```powershell
.venv\Scripts\python.exe tools/build_comic_asset_starter.py --register
```

This command rebuilds the pack and records registered IDs in `data/pipeline/comic-starter-asset-ids.json`. Running it again can reuse the same IDs when the image and stored copy still match. Use the local ID in the episode's `source_panels` placement. These IDs are for previews. Use a new eligible registration after the publication review if appropriate.

The static layers are useful for first appearances, reveals and background staging. Use the drawing helpers or the [existing editor controls](../../../docs/categories/comic-lore/VISUAL_STYLE.md#editor-controls) for contact, movement and effects. Use the [shot decision guide](../../../docs/categories/comic-lore/SHOT_DECISIONS.md) to choose how a layer contributes to the beat.

For a one-off circular face identifier, start with a registered photo and a verified close crop. The coordinates below are illustrative. They are normalized left, top, right and bottom.

```powershell
.venv\Scripts\python.exe tools/build_comic_asset_starter.py --portrait-asset REGISTERED_PHOTO_ID --portrait-name character-name --portrait-box 0.20 0.10 0.70 0.60
```

Save and reuse the returned local ID. Place the circle through `source_panels` on the actor's head or beside the figure when the viewer needs a label. If the crop has appeared recently, set `repeat_reason` to explain the deliberate identity callback. Inspect the crop and clearances in the finished frame. This preview helper preserves the source reference and usage restrictions. Keep the geometric face as the fallback.


The hunter-arc extension adds reusable `kraven-hunter` and `spider-black-cloth` transparent actors. `lore_hunt.py` reuses those drawing functions for the burial, impostor, escape and confrontation. The black costume is a cloth suit in this story; its appearance does not imply Venom/symbiote powers. Theme/background choices remain independent of costume colors.
