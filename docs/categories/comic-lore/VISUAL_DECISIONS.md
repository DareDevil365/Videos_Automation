# Choose the representation from the script

Choose a medium for each shot and layer, rather than assigning one medium to an entire character. The assistant reads the exact sentence and records its important element, physical action, people and prop state. The program applies [lore_style.py](../../../src/yt_pipeline/lore_style.py), saves its reasons, and checks registered assets and renderer support before execution.

## Decision order

1. **Find the important element.** Is the shot about identity, emotion, action, an object, a mechanism or a location? Doom fitting a hot mask is an object/contact shot. Introducing Doom is an identity shot.
2. **Find the action and consequence.** Contact, transformation and combat need controllable poses, attachment points and a visible changed state. Prefer geometry when the silhouette stays clear. A difficult likeness needs prepared cutout limbs or a different framing. Moving a rigid photo across the screen does not provide complex acting.
3. **Check recognition.** Detailed faces, armor and similar costumes favor cutouts for introductions. Thor and Beta Ray Bill need distinct faces. Hellboy and Spider-Man have stronger simple silhouettes for action. The profile ratings are editable editorial estimates, not recognition probabilities.
4. **Choose props independently.** A heating mask, moving beam or ship with replaced planks favors geometry. An inscription or exact texture favors a source image. Do not force all non-living things into one treatment.
5. **Choose the environment independently.** Atmosphere or scale can favor a photograph. A mechanism, exchange or comparison often benefits from a quiet geometric stage. Keep the palette, grade, outlines and typography consistent.
6. **Check feasibility.** Verify registered rights, transparency, resolution and the required pose. Generic cutout placement rejects enlargement above 1.25×. Get a better asset, reframe or add the missing recipe when the selected treatment cannot be executed.
7. **Review the result.** Inspect early, contact and late frames at phone size. Switch medium at meaningful cuts while keeping costume, colors and identifying details consistent. Rules guide the first choice; they do not certify visual taste.

| Purpose | Character treatment | Other layers |
| --- | --- | --- |
| Doom fits the hot mask | Geometric Doom with connected hands | Geometric mask changing temperature |
| Introduce Doom | Clean character cutout | Restrained drawn setting |
| Compare Thor and Beta Ray Bill | Cutouts showing distinct faces and costumes | Geometric hammers |
| A hero lifts wreckage | Recognizable geometric actor or anchored rig | Geometric moving wreckage |
| Compare Vision and White Vision | Cutouts for likeness | Quiet geometric library |
| Restore memories or phase through an object | Geometric action with contact points | Effects or a mechanism diagram |
| Explain the Ship of Theseus | Characters can leave frame | Planks move and form two ships |
| Reveal an inscription | Supporting actor only if useful | A sharp source photograph |

## Inputs and execution

Supply `visual_selection` on a series part, with `mode: auto` and a `shots` map keyed by script beat ID. Each shot names `focus`, `motion`, `characters` and `props`. Known profiles live in the module. New profiles require integer `detail` and `geometric_clarity` ratings from 0 to 3 based on the intended costume and phone-size silhouette.

```json
{
  "visual_selection": {
    "mode": "auto",
    "shots": {
      "u1": {"focus":"identity", "motion":"hold", "characters":["doom"], "props":[]},
      "u2": {"focus":"object", "motion":"contact", "characters":["doom"],
             "props":[{"id":"mask", "changes_state":true}]}
    }
  },
  "character_cutouts": {"doom":"REGISTERED_ASSET_ID"}
}
```

The exact script stays unchanged. `creative_plan.plan.visual_selection` records representations, reasons and continuity. Directed scenes receive `visual_style`. Source registration, pose and scale checks are separate. Thor can mix a geometric actor and a rigged cutout in one supported scene. A `portrait` can place a registered cutout. The Vision/Spider-Man recipes consume scene choices. Existing forge recipes execute geometric material/contact shots.

New series plans enable selection. Known forge and Thor recipes have initial semantic defaults. Other existing recipes keep their authored treatment unless a direction is supplied; the report labels this `authored`. The system does not infer every arbitrary sentence's purpose by itself. Antigravity supplies that interpretation using this playbook. Unsupported combinations stop with an asset or recipe message. `mode: authored` retains deliberate existing direction.

## Voices

[lore_voices.py](../../../src/yt_pipeline/lore_voices.py) rotates across distinct male and female Host/Narrator pairs. It considers recent completed comic series, avoids repeated pairs and narrators where possible, and freezes a seeded choice in the new plan. A continuing series keeps its pair. Voice selection is independent of character gender.

An optional top-level `source_voices` in `series.json`, such as `{"Host":"am_michael","Narrator":"af_bella"}`, overrides rotation. Supported local Kokoro IDs are `am_adam`, `am_michael`, `bm_george`, `af_heart` and `af_bella`. Keep the host at the opening and closing and the narrator through the body. Check a spoken sample for pace and tone; rotation alone does not establish acting quality. A female character entering does not trigger a narrator change.


## Photographic objects and locations

A photograph is useful when exact appearance, texture, lettering or the atmosphere of the place is the information. Geometry is useful when a material must heat, cool, bend or break, when the layout or mechanism needs explaining, or when a quieter setting helps the foreground read. Preserve the important prop's shape, colors and meaning across a change of representation. Compare perspective, lighting and clutter before accepting a photo.

For a simple `portrait` stage or exact-detail insert, the selected photographic layers can be supplied directly:

```json
{
  "visual_selection": {
    "mode": "auto",
    "shots": {
      "u1": {"focus":"location", "motion":"hold", "characters":["hellboy"],
             "props":[{"id":"inscription", "readable_detail":true}]}
    },
    "layers": {
      "u1": {
        "setting":"REGISTERED_BACKGROUND_ID",
        "props": {
          "inscription":{"asset_id":"REGISTERED_DETAIL_ID", "box":[70,640,210,880]}
        }
      }
    }
  }
}
```

The background is checked, cropped, graded and placed behind the actor. Named prop inserts use the existing source-image compositor and caption boundaries. The stage supports geometric Doom, Hellboy or Spider-Man silhouettes, as well as registered character cutouts. Generic props that need original geometry require a drawing recipe; the insert stage does not invent an object.

The selected source layer must exist and agree with the selected treatment. Missing images, excess enlargement or an incompatible action recipe stop with a specific message. Use a photo-aware action recipe or author its layer adapter when native opaque scenery cannot be replaced safely. Existing Hellboy photographic scenes remain an authored example of that approach.

These setting and prop assets participate in the recent-image reuse check. To return deliberately to the same photo setting, add `setting_repeat_reason` beside its ID. Prop placements use `repeat_reason`. Character identity assets can stay consistent, while composition, action and camera still need variety.


For objects, `appearance_matters: true` covers recognizable design or surface detail beyond readable lettering. `changes_state: true` takes priority for a material transformation. For settings, optional `setting` flags `appearance_matters` and `atmosphere` can select a photograph even when the foreground is an action. `needs_layout: true` takes priority when the viewer must understand geography or a changing structure. All three flags are booleans on the shot direction. The resulting photo layer still needs a compatible recipe and an actual registered source.
