# Explain and execute the visual choices

The owner wants deliberate, lively art direction. The repeated navy/teal look came from hard-coded defaults in `_background` and `_room`, compounded by reused recipes. The missing lower audience came from omitting `reaction_preset` in the builder, not a renderer limitation. Neither omission was a necessary style choice.

Use the established flat geometric/cutout language while changing locations, lighting and compositions to serve the story. Consistency means recognizable characters, deliberate outlines and a coherent visual hierarchy; it does not mean every room is blue. See [representation decisions](VISUAL_DECISIONS.md), [shot staging](SHOT_DECISIONS.md) and [topic research](TOPIC_SELECTION.md).

## Questions the assistant must answer

| Decision | Question | Basis for the choice | Saved evidence/review |
| --- | --- | --- | --- |
| Topic | Why would someone want this story now? | Concrete conflict, recognizable stakes, escalation, surprising supported consequence, comparison with rejected alternatives | `SELECTION_REVIEW.md`, source links and owner feedback |
| Beat | What changes during this sentence? | New information, decision, action, reaction or result | Script/claim IDs and shot purpose |
| Elements | Why is each character, prop or symbol present? | It establishes identity/location, shows a cause, carries a clue or makes a result legible | Per-shot `elements` descriptions; remove decorative items competing with the cause |
| Medium | Why a cutout or geometry? | Likeness/complex costume versus controlled contact, transformation or mechanism; props/settings decided independently | `visual-decisions.json` or explicit authored direction; do not claim automatic choice when authored |
| Palette | Why these colors in this location? | Material, light source, time/weather, genre and current emotional turn; retain character costume colors | Named palette and per-shot rationale in `design-decisions.json` |
| Color change | Why change palette here? | Location/time transition, a new subjective state or a significant turn; a returning location usually retains its palette | Before/after relationship in the shot rationale; no random rainbow cuts |
| Background | Why this space? | Story geography or atmosphere; clear separation from cast and captions | Source provenance for a photo or named geometric recipe; atmosphere is illustration, not an extra canon fact |
| Motion | Why does this move? | It depicts the spoken verb, a reaction or motivated environmental motion | Anchors/contact/state change; atmosphere behind the subject, never an unrelated barrage of particles |
| Atmosphere | Why particles, energy or weather? | Fire → rising warm embers; Hex/magic → shifting multicolor energy; graveyard storm → slanting rain; dry interior/underground → sparse dust | Named bounded effect with timing; do not add fire because a palette is orange |
| Camera | Why this size/angle? | Wide for geography/relationships; medium for interaction; close detail for a clue or reaction; payoff changes the composition | `lore_camera` and beat rationale; check framing after audience resize |
| Type family | Why this font? | Readable familiar shapes, mood and hierarchy, actual installed availability | `lore_design.font`; same selected family for heading and captions |
| Type weight/size | Why bold and this size? | Fast phone reading; heading must fit its reserved band; captions remain readable at final export size | Bounded heading fit, measured caption layout, actual frame inspection |
| Contrast | Can the viewer read it immediately? | Dark text on paper/daylight, light text on dark palettes; a dark caption band isolates white narration from changing scenes | Contrast tests for palette text, sampled final captions; never color-grade the text into the scene |
| Labels | Why display this text as well as speech? | Identify source, explain identity or reinforce the decisive object/action | Exact labels, no decorative channel/fiction banners; avoid long blocks of narration |
| Audience | Why this lower set/cast? | Reusable channel format: a quiet Marvel theater for ensemble comic stories; topic-specific workshop/city/home where appropriate | Explicit registered set, asset provenance, `audience_required`; no unrelated franchise masquerading as canon |
| Sound | Why this track/cue/level? | Genre and emotional arc, narration intelligibility, avoid an overused bed; one relevant impact can mark a physical turn | Registered music/evidence and bounded mix fields; listen to the whole export |
| Timing | Why this hold or pause? | Actual complete speech, readable detail, a decision or reveal that needs time | Measured voice/caption times; no empty padding or clipped lines |
| Ending | Why leave this final image? | It shows the changed situation or consequence promised at the start | Final frame and exact last line; no unrelated moral or automatic CTA |

## Implemented controls

`lore_design` is optional so initialized historical plans retain their look. For new productions use it explicitly:

```json
{
  "reaction_preset": "crossover-theater",
  "lore_design": {
    "palette": "paper",
    "font": "Trebuchet MS",
    "atmosphere": "none",
    "audience_required": true,
    "reason": "Warm paper separates the explanatory diagram from the storm outside; the theater retains the channel format.",
    "shots": {
      "u1": {
        "palette": "ember",
        "atmosphere": "embers",
        "reason": "This beat is inside a lit forge; heat and rising embers make the environment respond to the action.",
        "elements": ["The hot mask is the object changing state; tools establish who changes it."]
      },
      "u2": {
        "palette": "hex",
        "atmosphere": "hex",
        "reason": "Use only for a supported magical/subjective context such as the Hex, not an arbitrary location change.",
        "elements": ["Multicolor moving energy establishes the magical environment behind the focal character."]
      }
    }
  }
}
```

Seven named palettes: `paper`, `ember`, `plum`, `concrete`, `daylight`, `crimson`, `hex`. Five effects: `none`, `embers`, `dust`, `hex`, `rain`. Fonts: Arial for neutral narration, Trebuchet MS for open, slightly more expressive comic lettering, Georgia for a restrained archival heading only when it remains readable. Default fallback uses the existing local font resolver if the selected font is absent; check the actual export, not just the requested family. No new font download or license assumption is made.

`compile_design` validates IDs/options, records the palette colors and rationale on each scene, and rejects an audience-required plan without a set. It does not prove that a written rationale is sensible: the assistant must compare the stated purpose with the actual frame. The new background renderer animates atmosphere within the story viewport. The Vision/Spider-Man room recipe accepts palette colors instead of always painting teal. The lower-set compositor transforms the entire scene—including photo inserts and effects—together, then reserves a dark caption band above the theater. Caption fonts follow the request and participate in the render cache key. Legacy plans without these fields keep their existing controls; arbitrary recipes are not automatically recolored or newly rigged.

## Before making the final video

1. Finish source/story selection, exact script, scene direction, assets and editor extensions first. Prepare a storyboard and measure narration before freezing a new build.
2. Inspect each frame for the promised element, costume/prop continuity, legible source artwork, color purpose and audience presence. Check the two extremes of important motion, not only a midpoint. An illustrated coffin cross-section is explanatory staging, not evidence that the comic used that angle.
3. Run relevant editor tests and resolve failures. Render a short atmosphere sample if adding an unfamiliar effect. Do not use a successful MP4 encode as a design verdict.
4. Render the full video. Inspect opening, transitions, action contact, final consequence, captions and the lower band from the actual MP4; listen to full narration/music. Check duration, hashes, clipping and awkward gaps.
5. Save completed checks, unresolved limitations, metadata and design rationale with the export. No finite checklist makes a video foolproof or guarantees views. Record the actual result and the next improvement.

Randomness is limited to small nonsemantic variation after the meaningful choices are fixed: dust positions, subtle ambient motion, or rotation among already suitable tracks/voices. It does not choose the story's cause, payoff, setting, palette, important prop, shot purpose or evidence. The current atmospheric paths are deterministic for repeatable review.
