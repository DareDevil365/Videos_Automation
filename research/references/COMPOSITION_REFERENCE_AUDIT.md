# Reference audit: supplied-media Shorts compositions

Checked 2026-11-01. This supersedes the earlier recommendation to make generated gameplay and large headline/chat cards the editor's default. The user clarified that the program should supply clips/screenshots/music to reusable 9:16 compositions. The user's direct reference is the primary style anchor; high public views help select examples, but do not establish earnings or the cause of their performance.

## Directly inspected references

Counts were read from the native YouTube Shorts Description panel; runtimes were read from the loaded video element. Visual observations come from sampled playback and screenshots, not an exhaustive frame/audio audit. Dates are the native UI dates, which can differ from earlier search-indexed dates.

| Reference | Native public views | Runtime / publication | Direct visual findings |
| --- | ---: | --- | --- |
| [User's Dozzek example](https://www.youtube.com/shorts/h6pcngherRs) | 1,810,945 | 63.361 s; 2026-08-18 | Full-frame moving footage; a compact dark phone-message panel near the upper center. Blue/gray message bubbles and the contact header belong to that panel. Its visible content/height changes as the conversation progresses. Sampled approximately 9.5, 57.0 and 62.2 seconds. Background samples include real-world rooftop/parkour/water footage, rather than a generated game. |
| [ViraL Trend celebrity-reply edit](https://www.youtube.com/shorts/5FzNT-oyDEk) | 66,627,975 | 53.681 s; 2023-12-10 | Full-frame portrait footage, compact center/lower text with a highlighted word, watermark, cuts between people and a later reaction shot. It is not a gameplay split screen or phone-chat design. Paid promotion and a betting brand are visible; those branding assets are not template features to reproduce. |
| [Christina Kingston text-message example](https://www.youtube.com/shorts/9_e6Y9iiB-E) | 14,004,475 | 51.981 s; 2026-06-25 | Black background, large phone-message crops, a persistent compact hook at the top. At the opening, later messages are blurred; later sampled frames show different revealed messages and a changed crop. No gameplay was visible in the sampled frames. |
| [Rizzo texts example](https://www.youtube.com/shorts/K0TbExFL4P4) | 3,255,094 | 54.781 s; 2024-09-04 | A narrow phone-header/message crop near the top over full-frame satisfying footage. Sampled backgrounds change from metal machining to fruit preparation. This is not evidence that Minecraft itself caused its views, despite game-related description tags. |

The 66.6-million-view reference is the largest count among these inspected examples, not a verified global maximum. Search results are not an exhaustive ranking. A native Shorts + Popularity filter returned no results for the sigma query in this session; it was not treated as a reliable ranking. Search thumbnails also supplied leads with approximately 7M and 496K views, but their full videos were not inspected and they are not implementation evidence above.

Native public view counts do not establish gross revenue, monetization status, US audience share, retention, music permissions, or the right to reuse the source. These are format references, not production media. No source video or music file was downloaded. Limited research screenshots are local artifacts in `data/reference-audit/`, excluded from source control; only the sigma and user-reference capture were saved successfully. Other frames were inspected in the browser.

## What the editor should do

1. **Primary preset: chat over footage.** Background clip fills the canvas. A supplied screenshot or prepared chat video is placed near the upper center, preserving its aspect ratio. Initial editable box: left 10%, top 12%, width 80%, maximum height 44%. These numbers are approximate design measurements, not the original project's parameters.
2. **Two-block preset.** Two supplied clips occupy top and bottom regions with an adjustable split and border. This is a requested supported layout, not a finding that every inspected high-view example uses it.
3. **Wide clip on blurred fill.** A sharp, aspect-preserved clip sits over a blurred copy that fills 9:16. This is a useful preservation option suggested by search-thumbnail observations, not a fully audited high-view reference in the table.
4. **No automatic card over the content.** The compositor does not invent headlines, chat bubbles, fake phone conversations or gameplay. If chat needs progressive reveals, provide a prepared recording, or change supplied screenshot states using separate shots. Building a chat authoring system is a separate task.
5. **Effects are optional.** Border/glow, timed punch zoom, short flash, micro shake and a timed like/subscribe label are production controls. These were requested by the user; this audit does not establish that adding them improves views. The direct reference should start clean, with effects and CTA off.
6. **Reusable layout, separate inputs.** The same placement/effects recipe can accept different local files through a JSON job. Readability, cropping, audio and effect timing should be checked with actual supplied media; solid-color QA fixtures certify geometry/audio behavior only.

## UI preference audit and native editor options

The user rejected the previous green/charcoal style and asked to delete a saved rule if one required it. Inspected the available local custom skills, local memories folder and global AGENTS instructions. No directive requiring that palette or dashboard style was found, so no unrelated skill was removed. The previous palette was an implementation choice. The new default UI is a neutral light media-slot inspector; its colors do not set the colors of imported chat/media.

The user also has access to Premiere Pro, After Effects and Resolve Studio and clarified that these are optional if the result works well without them. Locally detected Premiere Pro 2022 and Resolve 21.0.4; no After Effects executable was found in the standard Adobe install directory inspected. This does not establish that AE is unavailable elsewhere.

After Effects supports script-driven preparation and `aerender` command-line rendering; Resolve's installed Studio scripting SDK supports Python/Lua, media/timeline operations and render jobs. These could become alternate backends after a real template is tested. No native application preferences were changed, no project was opened/modified, and no Adobe/Resolve integration is implemented. The current FFmpeg compositor is appropriate for the requested fixed media slots and basic effects, with no new paid dependency. See [Adobe scripting](https://helpx.adobe.com/after-effects/desktop/automate-in-after-effects/automate-animation/scripts.html) and [Adobe automated rendering](https://helpx.adobe.com/after-effects/desktop/render-and-export/automate-rendering/automated-rendering-network-rendering.html).

## Implemented versus remaining

Implemented: three media-slot presets, adjustable foreground geometry/fit, borders/glow, timed effects/CTA, selected clip audio plus music, browser import/preview/save/export, reusable layout JSON and headless JSON-job materialization. Startup does not generate demo footage, and export rejects missing required media.

Remaining: automatic clip sourcing, chat authoring/reveal generation from text, beat detection, arbitrary multitrack/keyframe editing, native-editor bridges, script/voice generation and channel automation. Actual source-media samples are still required for final aesthetic/readability tuning. Do not describe synthetic test renders as convincing gameplay or finished channel episodes.
