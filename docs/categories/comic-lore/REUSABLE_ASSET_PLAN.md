# Reusable asset plan for comic lore

Keep the episode's decisions in the shot list. Give Antigravity a small menu of characters, objects, actions and sets so it can spend its time on the story. The editor should assemble familiar pieces from stable IDs and accept a new asset only when the current scene needs it.

The first [starter pack](../../../Resources/Templates/ComicLore/README.md) is installed locally. It has 12 generated transparent layers, stable catalog names and idempotent local registration by asset hash. Happy and Stane share a broad body shape. Tony and Pepper have individual face and wardrobe details. The same runtime hammer primitive supplies the standalone Thor prop and the editor's lightning action. A general pose catalog and automatic face placement are later extensions.

## What the project already has

| Existing piece | What it saves | Where to extend it |
| --- | --- | --- |
| Comic-lore frames and cameras | The local Pillow renderer draws geometric art and keeps pans, pushes and detail shots inside the visual panel. | [Lore renderer](../../../src/yt_pipeline/lore_visuals.py) |
| Forge and reactor recipes | Doom's mask already has separate geometry, heat and scale. Tony's reactor already keeps its shape across build, theft and return shots. The reactor cast adds authored body, face and arm geometry for Tony, Pepper and Stane. | [Forge](../../../src/yt_pipeline/lore_forge.py), [reactor](../../../src/yt_pipeline/lore_reactor.py), [reactor cast](../../../src/yt_pipeline/lore_reactor_cast.py) |
| Effects and cutout motion | Named power effects already accept explicit origin and target coordinates. Registered cutouts can drop, arc, crush or knock. The hammer silhouette in the lightning effect is the seed for a prop. | [Actions](../../../src/yt_pipeline/lore_actions.py), [placements and motion](../../../src/yt_pipeline/source_sets.py) |
| Reusable sets | Cinema, workshop, city, living room and sanctum already have local presets. The workshop can stack a backdrop, actor and foreground. | [Set library](../../../examples/lore-series/MARVEL_REACTION_SETS.md) |
| Circular photo heads | An older storytelling renderer already clips a head photo into a circle on a reusable body, with configurable wardrobe and pose. Comic lore would need its own way to select and anchor that layer. The phone renderer also demonstrates deterministic circular masking. | [Storytelling cast](../../../src/yt_pipeline/planned_visuals.py), [phone avatar](../../../src/yt_pipeline/phone_editor/chrome.py) |
| Registered local media | The workspace already verifies asset hashes and usage evidence. Search indexes registered metadata in SQLite. A saved photo can be reused without repeating acquisition or classification. | [Registry](../../../src/yt_pipeline/assets.py), [media search](../../../src/yt_pipeline/media_library.py) |

## Proposed asset inventory

| Priority | Prepare once | Variants and uses |
| --- | --- | --- |
| First pack | Shared actor anchors | Define head, chest, shoulder, elbow, hand, ground and seat attachment points. Start with busts and waist-up actors for the existing 9:16 compositions. Support slim, medium and broad silhouettes with different shoulder lines and stance. |
| First pack | Civilian head and wardrobe layers | Hair outline, hair color, jaw, beard, glasses, collar, jacket, shirt and sleeves. Build Pepper with her own hair silhouette and wardrobe. Give Tony a distinct hairline, goatee and workshop clothing. Give Stane a broad suit silhouette, bald head and gray beard. Aim for recognition in silhouette and full color. |
| First pack | Metal faceplate drawing pieces | Share cheek facets, material shading, eye cutouts, optional seams and placement anchors. Give Doom a hood and a distinct iron mask, with red-hot, cooling and cold variants. Give Tony his own outline, brow, faceplate seams and palette. Keep the cave-built Mark I distinct from red-and-gold armor. |
| First pack | Reactor and keepsake props | Reuse the authored reactor ring, sockets, battery, wires, case and gift wrap. Provide lit, dim, cased and loose variants. Keep the registered replica photograph as a separate optional object insert for the inscription. |
| First pack | Story actions with named attachment points | Neutral, look, reach, hold, set down, pick up, remove and recoil. Let the editor attach an object to a hand, a surface or a socket at an authored point in the beat. |
| Next pack | Thor's hammer | Separate head, handle and strap. Expose `grip`, `head` and `impact` anchors. Support carried, raised, launched and landed poses with the existing lightning, arc and impact effects. Add Thor's silhouette when his episode is scheduled. |
| Next pack | Common props and textures | Phone, shield, wrench, table, box, book, tools, rubble, doors, glass and floor pieces. Start with props the next scripts actually use. Real objects can enter as registered transparent cutouts using the same placement controls. |
| Next pack | A few useful stage layouts | Single actor close-up, two-person exchange, workshop bench, forge, seated confrontation, chase profile and object insert. For each, define camera clearance, foreground occlusion and caption clearance. |
| Selective | Circular photo identity | Use an eligible photo when a geometric profile needs help at first appearance or after a long absence. Save one normalized square crop per identity, reuse it as a clipped face or small marker, and keep the regular geometric face available. |
| Later | Costume and effect extensions | Add capes, gauntlets, visors, magic rings, color palettes and special poses only as stories call for them. Build more realistic motion after simpler blocking shows its limits in an actual episode. |

## How to build the first version

1. **Make a versioned menu of available pieces.** Give each checked-in geometric asset a stable name, a category, supported profiles and a reference image or contact-sheet cell. Keep visual primitives in Pillow so the editor can recolor and position them locally. Keep registered photo IDs, prepared alpha crops and their evidence in the workspace. An asset can have a stable catalog name and resolve to a different local registry ID on another machine.
2. **Reuse the current renderer and request flow.** Extend the beat staging with a small set of typed choices for cast, pose, prop and layout. Freeze resolved IDs and versions when creating the job. Add named anchors to character and prop layers so a handoff can resolve to Pepper's hand, the workbench or Tony's hand without prompting for pixel coordinates every time. Use the existing effect and camera paths. Keep the current freeform coordinates for a special composition.
3. **Make changes in the frame match changes in the story.** Plan the giver, object, recipient and visible outcome before rendering. For the reactor gift, show Pepper placing the case and Tony discovering it, then show the object paying off later. If the exact blocking is uncertain, label the staging as illustrative and preserve the source-supported action. A familiar asset can return while the room, angle, blocking and emotion change.
4. **Add portraits only where the viewer benefits.** Crop once from a registered image with a local fixed crop box and save the result or crop coordinates. Reuse the mask logic from the older cast or phone renderer. Let the planner choose `geometry`, `portrait_intro` or `portrait_face` after seeing a preview. The geometry path should render offline from the same script when the optional photo is unavailable or unsuitable.
5. **Optimize after measuring.** Prepare transparent props and portrait crops once. Cache static layers by asset version, palette, facing and scale when a measured bottleneck justifies it. Keep movement and camera composition on the existing beat timeline. A geometry or source change should invalidate only the affected rendered beats when a safe cache is added. Use pose keyframes and draw order before considering full rigs or a separate animation engine.

### Usage records and verification

- Use the existing registry for actual media, with source, usage evidence, edit and commercial eligibility, attribution and a checksum. Keep a link to the original asset and crop when a derived portrait or object is registered. A crop, mask or palette change inherits its source restrictions.
- Treat preview-only material as a local review choice. For a publication candidate, validate the final resolved assets through the existing provenance checks and use independently cleared replacements where required. A drawn likeness still needs an appropriate publication review.
- Reuse named bodies and props freely for character and object continuity. Reuse an identical hero shot only for a deliberate callback. Check the first appearance at phone size, then check silhouette, hands, attachment, occlusion, and the effect of the scene on mute. [Visual style and editor controls](VISUAL_STYLE.md)

### Proposed acceptance targets

These are trial targets. Capture the current baseline on the same machine and the same locked set of six to eight beats first.

| Measure | First comparison |
| --- | --- |
| Creative drafting effort | Track active shot-planning minutes and new manual asset preparations per approved Short. Aim for at least 70% of comparable beats to use already prepared pieces. |
| Model and acquisition work | Count separate image-generation, crop and asset search calls. Aim for zero such calls on beats fully covered by the installed pack. Track external research separately. |
| Editor rebuild cost | Time first render and a one-beat visual correction. Compare cold and warm runs at the same resolution. If per-beat caching is added, changing one beat should reuse intact earlier renders and refresh the changed beat and final assembly. |
| Creative quality | Check three frames per action for setup, contact and consequence. On mute, a fresh viewer should be able to identify who gives, takes or reacts and which object changed hands. Fix flat or repetitive staging before claiming a time saving. |

The current files already support many of these pieces separately. The versioned character and prop menu, named-attachment shot contract, optional comic portrait mode and comparative performance targets are proposed work. [Antigravity handoff](../../ASSISTANT_PRODUCTION.md)
