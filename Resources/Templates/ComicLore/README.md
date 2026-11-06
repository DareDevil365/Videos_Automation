# Geometric comic starter assets

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
