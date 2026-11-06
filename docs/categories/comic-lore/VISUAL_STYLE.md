# Comic lore visual style

Use the [forge recut recipe](../../../examples/lore-series/books-of-doom/forge-recut.json) as a reference for the channel's look. On this workstation the video is in `Resources/Productions/books-of-doom-forge-recut/part-1/video.mp4`. The approved reference has a dark portrait canvas, a strong short heading, a skewed thin-edged panel, flat faceted shapes, restrained light effects, and captions separated from the lower reaction set.

## Choose what the viewer should see

- Draw the main characters as recognizable geometric silhouettes. Identify each one through a few consistent shapes, colors and signature details. Use a high-resolution cutout when a real object, prop, setting or texture adds clarity. A source character cutout can support a deliberate reveal where the likeness matters. Keep every layer inside the scene's grade.
- Build the composition in layers. Start with a geometric panel and choose where a photo adds recognition, texture, or scale. A drawn performer can interact with a photo prop, or a real cutout can move through a drawn set. Match scale, lighting, and perspective across layers so they feel like one shot.
- Animate what changes the story. In the forge, see two monks work the mask with a hammer and tongs. Cut to the raised hand and worried face. Show the glowing mask move into place. Match-cut to the same shape changing from orange to steel. Then reveal the character with a different shot. The worried monk's expression is illustrative staging.
- Change the setting and visual grammar by story beat. Try a wide terrain view for travel, a close-up for a warning, a profile for contact, and a clean portrait for a reveal. Keep the typography, outlines and color discipline consistent. Reuse the same image when it helps the viewer understand a match cut or callback. Use a different scene or pose when the story moves on.
- Use the lower set like a reaction cutaway. An ensemble story can use a cinema. A character story can use an appropriate workshop, city or living room. Change the cast or camera across episodes. Keep the lower band quieter than the action.

## Editor controls

Supply these fields on a part of the series. Beat IDs come from its exact script. Controls are optional and can be combined.

| Field | Use |
| --- | --- |
| `lore_scenes` | Choose the panel built for the narrated action. Examples include `forge`, `forge_warning`, `mask_fitting`, `mask_cooling`, `street_impact`, and `portrait`. The complete list is in [lore_visuals.py](../../../src/yt_pipeline/lore_visuals.py). |
| `lore_cameras` | Choose `wide`, `push`, `pan_left`, `pan_right`, or `detail` for each beat. |
| `source_panels` | Place a registered image with `asset_id` and a pixel `box`. Transparent cutouts can use a `motion` object with `kind` of `drop`, `arc`, `crush`, or `knock` and an optional pixel `offset`. `repeat_reason` records a deliberate visual callback. |
| `lore_actions` | Pair an action with `actor: symbolic` for a drawn performer or `actor: effect_only` to layer it on a cutout. Choose `optic_blast`, `repulsor`, `hammer_lightning`, `doom_magic`, `sorcerer_rings`, or `ground_impact`. Give the action an `origin` and, for a directed effect, an optional `target` in portrait pixels. |
| `reaction_preset` | Choose an installed lower set. Cinema can use a registered crowd plate. |

Anchor each effect to the hand, tool, or object that causes it. Show anticipation, the moment of contact, and a visible consequence. Keep effects away from the title and captions. Check early, contact, and late frames to ensure motion reads on a phone. The built-in movements are deliberate geometric cues and simple cutout transforms. Plan a different scene if a shot depends on realistic character acting.
