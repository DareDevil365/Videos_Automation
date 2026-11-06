# Spider-Man Was Buried Alive. Someone Took His Place.

A complete original short recap of Kraven’s Last Hunt (1987): the hunter’s motive, burial and impersonation, Vermin, Peter’s emergence, refusal of the expected rematch, final test and consequence. This is comic continuity; the source is the six-part arc across Web of Spider-Man #31–32, Amazing Spider-Man #293–294 and Spectacular Spider-Man #131–132. The visible source cover is a later collected edition, not an invented original issue cover. [Topic comparison and research](SELECTION_REVIEW.md).

The pipeline uses the supplied exact script and source-review hashes. It makes no Gemini writing call. The named scene palettes and per-element purposes live in `series.json`; the compiled production packet keeps `design-decisions.json`. Characters are drawn geometrically for burial, emergence and interaction. The same black cloth suit stays recognizable across shots; neither Peter’s nor Kraven’s suit is treated as Venom. The registered publisher cover provides an exact source-art insert. The lower theater shows Captain America, Miles and Iron Man with popcorn; these are illustrative audience framing, not characters added to the comic events.

Warm paper and amber distinguish the hunter’s room/city, stone and rain establish the grave, muted crimson emphasizes emergence, purple separates the final threat and quiet daylight marks aftermath. Trebuchet MS is selected for open readable lettering; the caption band remains dark for contrast. There is no unmotivated all-scene starfield or one blue color grade. Geometric staging is illustrative; the actual comic’s precise camera angles and every movement were not reproduced. The confession/empty aftermath replaces a death reenactment.

The source brief cites indexed official publisher material and records direct-page access limits. Full issues were not read. The source cover and theater cast remain local-review inputs; no publication permission is inferred. Technical checks and the saved design rationale do not establish that the audience will find the story compelling.

```powershell
.venv\Scripts\python.exe tools/create_kraven_story.py --measure-only
.venv\Scripts\python.exe tools/create_kraven_story.py
# After reviewing source, writing, assets, design and storyboard:
.venv\Scripts\python.exe tools/create_kraven_story.py --render
```

The first command measures an unfrozen draft; the second freezes/previews the supplied inputs without rendering the final video. Changed words or shot direction need a fresh build ID. The final command runs the normal local pipeline, preserving speech, captions, metadata, source evidence, QA and video under `Resources/Productions/kraven-last-hunt-complete-20261107/part-1/`. The build verifies unchanged text-provider usage. See [art direction](../../../docs/categories/comic-lore/ART_DIRECTION.md) for controls and checks. Final measured validation is recorded below after export.


Delivery choices: the male host (`am_adam`) frames the source and consequence; the female narrator (`af_bella`) carries the action. This existing validated pair measured the fuller draft predictably; gender does not stand in for a character. Explicit 1.22× delivery fits the complete story without cutting its causal bridges. The selected local bed is **Echoes — Andrew Ev**, from the registered Mixkit mystery collection, at low gain beneath speech with its first four seconds skipped. It supports pursuit and uncertainty; no sudden message pings or audience dialogue competes with the narrator. Track provenance remains in packaged credits.


Final validation: **48.833 seconds**, 720×1280, passing technical QA and 14 matching package hashes. All nine beats and emergence motion extremes were sampled from the exported MP4; the audience and caption separation remain visible. The final local packet contains `REVIEW.md` and `finished-review.json`. Narration has no detected ≥0.3-second quiet interval at −42 dB, and mixed audio clipping fraction is zero. These are technical checks and assistant self-review; human acting/music approval and audience results remain unproved. The local source-date/reused-cover development holds were corrected in separate immutable builds; no check was disabled.


Setup: use the existing project virtual environment and local voice/alignment models, installed curated music and installed Marvel reaction presets. The builder resolves those names from the private workspace and does not embed private asset IDs in this recipe. [Reaction-set setup](../MARVEL_REACTION_SETS.md) explains installation; absent assets require setup before this example can run on a new checkout.
