# Spider-Man Could See the Cure. He Couldn’t Reach It.

The owner rated the earlier scripts 2/10 for disconnected summarization. This is the new story revision, not an owner-approved quality claim. Its current local export is `Resources/Productions/spider-man-last-lift-story-revision-final-20261107/part-1/video.mp4`.

This original recap covers Stan Lee and Steve Ditko's If This Be My Destiny arc, The Amazing Spider-Man #31–33, culminating in issue #33 (1966). The opening names that issue while showing its matching publisher-hosted cover. Earlier events from the arc provide the causal setup; they are not all claimed to occur in issue #33.

The rewrite makes the emergency personal: Peter's radioactive transfusion harms Aunt May. The stolen serum leads him to the underwater base and trap; remembering Ben changes his decision to persist. The lift gives him access to the remedy, and Connors helps prepare the treatment. The final bottle now carries a consequence that the opening established. The [writing review](../../../docs/reviews/comic-lore-script-revision/WRITING_REVIEW.md) contains the exact narration.

The source cover is followed by geometric blood/radiation and hospital diagrams, Doc Ock's mechanical arms, the visible but unreachable cure, a masked close-up for the decision, a connected lift and the treatment outcome. The vial retains its signature appearance across scenes. A desk insert closes on the recovered object. Physical staging is illustrative; these are not reproduced comic panels. The prepared modern Spider-Man likeness remains in the asset packet but is not used as the 1966 cover art.

Marvel's official decade guide, greatest-moments recap, Doctor Octopus history and issue catalog support the claim packet. The catalog page blocked direct access; indexed publisher metadata and the official cover were available. Full issues were not read in this pass. `brief.json` records that scope, and `source-review.json` hashes the exact revised brief and script.

The series file records each beat's important element, movement, characters and props. The local rules choose supported representations and save the reasons in `visual-decisions.json`. Voice pairing is fixed for the episode: male host (`am_adam`) and female narrator (`af_bella`), independent of character gender. `source_duration: [42, 50]` enforces the measured target. Delivery is 1.15× with tight speech and linked names. These are explicit editor settings, not timing tags in dialogue.

```powershell
.venv\Scripts\python.exe tools/create_adaptive_hero_shorts.py --only spider --measure-only
.venv\Scripts\python.exe tools/create_adaptive_hero_shorts.py --only spider --prepare-only
.venv\Scripts\python.exe tools/create_adaptive_hero_shorts.py --only spider
```

The builder resumes the initialized plan. Changed input requires another build ID; existing plans and exports preserve their frozen words. Draft measurement occurs before initialization. The supplied writing and local renderer use no Gemini text generation or image generation. The build checks unchanged text-provider usage.

Validation: **49.966 seconds**, 720×1280, passing technical QA and 14 matching package hashes. Actual role voice IDs were checked in the unit records. Narration silence detection at −42 dB found no interval of 0.3 seconds or longer. Sampled exported frames were inspected. Technical checks do not establish expressive acting, writing quality or audience results.

The packet retains title, description, sources, speech, captions, technical report and video. The cover/poster and sourced character assets are local-preview inputs with attribution in `media-sources.json`; publication readiness is false. Earlier adaptive exports remain historical versions with rejected writing. Reuse [reviewed source facts](../../../research/content-lore/SOURCE_LIBRARY.md), not those earlier scripts, when writing another episode.


The saved recipe now includes a required lower theater and contextual art direction. Existing frozen videos/plans are unchanged. To preview the new direction without replacing history, use `--build-suffix context-review-20261107 --prepare-only`; omit `--prepare-only` only when requesting that new render. The owner rejected these prior topic choices; they are visual fixtures, not default next releases.
