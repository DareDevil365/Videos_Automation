# Why Hellboy Breaks His Own Horns

An assistant-written, standalone portrait comic-lore Short. It uses geometric characters with photographic scenery and a real book cutout. It ends on the story's answer, with no subscribe, follow or next-part line.

## Research and writing

The chosen angle connects a recognizable visual feature to a consequential choice. The opening promises an explanation of the broken horns. The middle establishes the human upbringing, reveals the hand's purpose, and presents the unwanted destiny. The refusal supplies the answer before the host's closing line. This is an editorial engagement hypothesis. No audience test or view outcome is claimed.

- [Dark Horse's official timeline](https://images.darkhorse.com/darkhorse/index_images/blog/hellboy_timeline.pdf) supports the summoning, adoptive father and Hecate encounter.
- [The official licensed RPG introduction](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/353222-sample.pdf) supports the paranormal investigator premise and the apocalyptic hand.
- [The horn discussion](https://scifi.stackexchange.com/questions/215873/why-does-hellboy-file-down-his-horns/215896) identifies the horn-breaking sequence in *Wake the Devil* #5. It distinguishes this from filing scenes in the films. This is secondary corroboration, not a claim to have read the complete issue.

The short covers the classic premise and that particular refusal. It does not claim to summarize or resolve the entire later saga. The last line is original commentary, not a quotation from Hellboy. The source review binds the exact brief and script hashes.

## Shots and style

| Beat | Viewer takeaway | Visual decision |
| --- | --- | --- |
| u1 | A demon rejects his intended role | Adult geometric Hellboy against photographed lava, with a slow push. |
| u2 | A human raised him | Small red child reaches toward Professor Broom's hand. Both figures use shapes. Photographed architecture sets the scene. |
| u3 | He protects people | Trench-coated investigator beside an isolated photographed book on a quiet graphic background, with a gentle scanning accent. |
| u4 | His fist can unlock destruction | Large segmented stone fist, an abstract release diagram and a lava inset. The diagram is an analogy, not a literal comic mechanism. |
| u5 | His destiny is invoked | Horns grow while a distant geometric Hecate silhouette watches. |
| u6 | The choice has a human cost | Full horns remain visible. The hand is isolated in the foreground while the lava fades. |
| u7 | He refuses | Arms rise, hands reach the horns, fragments fall away, hands lower, and the broken stubs remain. A restrained sound accent marks the cut. |
| u8 | The investigator wins over the destined king | The coat returns and the story closes on the monster hunter. No call to subscribe. |

The palette retains the existing dark panel, cream frame and flat faceted actors. Photographs are desaturated and darkened to fit that palette. Hellboy's horn stubs, red face, heavy brow, goatee, coat and oversized stone right hand identify the same character throughout. Lava returns within this episode to connect the threat and refusal. The ruins return at the end as a callback to his human life. These are newly sourced settings for this episode, not inherited Doom panels.

The backgrounds are illustrative real-world photographs, not canonical locations. Tintern Abbey is cropped to exclude photographed visitors. The historical binding is an illustrative book, not a claimed artifact from the comics. All living characters remain drawn geometry.

## Media and rebuild

[media-sources.json](media-sources.json) records source pages, download URLs, creators and licenses. Lava is credited to Janice Wei / Hawai‘i Volcanoes NPS under the recorded public-domain status. Michael Gwyther-Jones's ruins photograph uses CC BY 2.0. Godfried Croenen's binding photograph uses CC0. Packaged metadata retains credits and modification notes.

```powershell
.venv\Scripts\python.exe tools/create_hellboy_short.py --prepare-only
.venv\Scripts\python.exe tools/create_hellboy_short.py
```

The tool downloads missing source files, prepares the crop/matte, registers image evidence, and creates a supplied-script plan. `hellboy_media` passes the three registered IDs to `lore_hellboy.py`. The scene recipes draw the actors after the photographic layer. The existing camera, local speech, music, captions, QA and packaging stages finish the video. The initialized plan resumes when rerun. Use a new `--build-id` when changing an already rendered script or plan.

The script and shot direction come from the assistant. There are no Gemini writing or image-generation calls. The episode remains a local test preview. Run `production-history` to distinguish the finished local copy from any recorded upload.

## Validation

The final export is `Resources/Productions/hellboy-horns-geometric-final-20261106/part-1/video.mp4`, 40.53 seconds at 720×1280. Local technical QA passed with no clipped audio samples detected. Its saved SHA-256 matches the exported file. Sampled MP4 frames were inspected, including the hand-to-horn contact and settled lowered hands. Silence detection on the narration at −42 dB found no gap of 0.3 seconds or more. Fourteen focused lore and series tests passed. The builder's provider-usage assertion passed. No audience response, full-issue reading or subjective listening approval is inferred from those checks.
