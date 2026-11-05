# Background music library and editing playbook

Checked 5 November 2026. This library serves the software editor: spoken chat comedy, unknown-sender mystery/thriller, emotional family stories, cinematic narration and action/aura edits. It contains **14 downloaded, registered recordings** with source/license evidence. No new music was generated.

The versioned [machine-readable catalog](../src/yt_pipeline/music_catalog.json), [selection/installation module](../src/yt_pipeline/curated_music.py) and [command-line tool](../tools/curate_music_library.py) are the reproducible definitions. Audio and downloaded evidence live locally in ignored `Resources/Music/curated-20261105/`; registered asset IDs live in ignored `data/pipeline/curated-music-library.json`. IDs are local to a workspace and must never be copied as portable catalog identifiers.

## What the editor needs

Music should supply a missing feeling while the script and acting supply the story. It should not compete with character voices or tell the audience the punchline before the message arrives. These are editorial choices to test, not proven reach rules.

| Genre | Desired sound and timing | Avoid |
| --- | --- | --- |
| Chat comedy | Light pizzicato/plucked rhythm, dry curiosity, small rise when consequences escalate. Leave a short gap before the final reply and let the line land. | A loud laugh track, constant cartoon hits, a drop on every message, music louder than the joke |
| Mystery | Sparse, low atmospheric tension with an uncertain pulse. Let clues remain intelligible; a sudden absence of sound can mark real danger. | Playful detective music under a credible threat, nonstop risers, false jump scares, hiding a clue under a loud hit |
| Thriller | Controlled dark tension that intensifies only when the character's risk changes. Preserve an intentional blackout's silence. | Trailer-scale intensity from the first message, distorted dialogue, a musical release before the reveal |
| Emotional chat/story | Quiet piano or warm restrained texture. Stay neutral during the misunderstanding and support the character's choice when it arrives. | Automatically treating every family story as grief, sentimental swells before the audience understands why |
| Cinematic narration | Uncluttered instrumental bed, phrase-length changes, modest rise toward the earned resolution. | Busy lead melodies in the speech range, a different track on every sentence |
| Aura/action | Confident rhythmic bass/percussion, build through actual preparation, place the strongest musical event on the real athletic/action payoff. | Fabricated performance scores, empty footage after the action, assuming a beat drop exists at an unchecked timestamp |

Start dialogue beds around **0.06–0.10 linear gain** after sensible source loudness handling; the catalog records a starting suggestion per track. Aura without dialogue can start around 0.45–0.50. These numbers are mix inputs, not LUFS targets or auditioned final levels. Duck music during speech, use short fades, and check intelligibility on a phone speaker. The music must yield to a deliberate silence. Do not play a voice twice because its text is previewed in a notification and later shown in a chat bubble.

Do not speed up or pitch-shift a famous recording merely to imitate another creator. Do not call a suggested source offset a verified beat marker. Inspect/listen to the actual excerpt before claiming a cut lands on a beat. This initial library has technical decoding/provenance checks; no subjective listening approval is claimed.

## Installed recordings

All Mixkit rows use the [Stock Music Free License](https://mixkit.co/license/modal/musicFree/), which permits online video use, including commercial YouTube projects. It excludes music-only distribution/remixes, rights-management registration, games and TV/radio use. A claim is still possible; Mixkit provides a support process. Full source credits are stored even where attribution is optional.

| Catalog key | Recording and artist | Intended use | Evidence |
| --- | --- | --- | --- |
| `incompetech-usuan1400011` | Monkeys Spinning Monkeys — Kevin MacLeod | Recognizable, bouncy comedy | [Original track/license](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400011) |
| `incompetech-usuan1100772` | Sneaky Snitch — Kevin MacLeod | Low-stakes plotting, mischievous comedy | [Original track/license](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100772) |
| `incompetech-usuan1100646` | Investigations — Kevin MacLeod | Dry, awkward comic investigation | [Original track/license](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100646) |
| `mixkit-595` | Secret Garden — Eugenio Mininni | Light comic dialogue alternative | [Comedy collection](https://mixkit.co/free-stock-music/tag/comedy/) |
| `mixkit-2` | Comical — Ahjay Stelino | Broader playful reactions | [Comedy collection](https://mixkit.co/free-stock-music/tag/comedy/) |
| `mixkit-188` | Echoes — Andrew Ev | Sparse mystery/unknown-sender tension | [Mystery collection](https://mixkit.co/free-stock-music/tag/mystery/) |
| `mixkit-671` | Piano Horror — Francisco Alvear | Actual danger and darker suspense | [Mystery collection](https://mixkit.co/free-stock-music/tag/mystery/) |
| `mixkit-565` | Fallen (Asper) — Eugenio Mininni | Longer cinematic tension alternative | [Mystery collection](https://mixkit.co/free-stock-music/tag/mystery/) |
| `mixkit-493` | Beautiful Dream — Diego Nava | Warm reflective stories | [Piano collection](https://mixkit.co/free-stock-music/piano/) |
| `mixkit-22` | Piano Reflections — Ahjay Stelino | Quiet introspection | [Piano collection](https://mixkit.co/free-stock-music/piano/) |
| `mixkit-839` | Tears of Joy — Michael Ramir C. | Positive emotional resolution | [Piano collection](https://mixkit.co/free-stock-music/piano/) |
| `mixkit-400` | C.B.P.D — Arulo | Confident practice-to-payoff action | [Trap collection](https://mixkit.co/free-stock-music/trap/) |
| `mixkit-357` | Head Bang — Arulo | More forceful aura/action alternative | [Trap collection](https://mixkit.co/free-stock-music/trap/) |
| `mixkit-370` | Sparta — Arulo | High-energy athletic finish | [Trap collection](https://mixkit.co/free-stock-music/trap/) |

The three Kevin MacLeod **original recordings** use CC BY 4.0, with visible full attribution required. The [composer's FAQ](https://incompetech.com/music/royalty-free/faq.html) permits monetized YouTube videos with credit. Packaging must retain title, composer, source and license link. The license does not apply automatically to later covers or orchestral versions.

## Famous versus permitted versus effective

We found primary evidence for the familiarity of **Monkeys Spinning Monkeys**: [TikTok's April 2021 report](https://newsroom.tiktok.com/trending-on-tiktok-endless-inspirationalquotes?lang=en) associates it with comedic videos, and [TikTok's June 2022 Classics announcement](https://newsroom.tiktok.com/tiktok-classics-memes-and-viral-hits?lang=en-GB) includes the composition among viral hits. These dates establish historical familiarity, not a current November 2026 ranking or a promise of more views. The downloaded Incompetech original is used under its own license; the Warner orchestral version is a different recording.

Other installed tracks have **no verified track-specific popularity result** in this pass. They are genre candidates, not claimed winners. `Oh No` and `Spooky, Scary Skeletons` appear only as historical platform reference titles in the catalog; no recording was downloaded or made selectable.

[YouTube's safe-music guidance](https://support.google.com/youtube/answer/15577610?hl=en) says that calling music free or adding a credit does not itself resolve rights. [YouTube's Shorts guidance](https://support.google.com/youtube/answer/15424877?hl=en) distinguishes music added through its own tools from royalty-free Audio Library options and notes restrictions for claimed longer Shorts. A song in a platform music picker is not automatically licensed for baking into an MP4 uploaded through our API. The software therefore selects only separately permitted downloadable recordings. It does not rip popular sounds from other videos.

## How software selects and expands the library

```powershell
python tools/curate_music_library.py list
python tools/curate_music_library.py install
python tools/curate_music_library.py select comedy --selection-key episode-42
```

Installation explicitly fetches checked recordings and source/license snapshots, verifies pinned SHA-256 values and registers provenance. Selection is offline by default. `select_genre_music(workspace, genre, selection_key='', avoid_recent=3, download_missing=False)` returns an eligible asset with catalog metadata. It checks media integrity and permission eligibility again; test-only, missing or modified tracks cannot silently enter a public production. It avoids the music IDs from recent ready/uploaded/published jobs when another eligible choice exists, then rotates deterministically from the selection key. The caller should persist the chosen `music_id` with the job, so subsequent history changes do not alter a resumed edit. An explicit soundtrack choice stays with its caller.

The existing broad `choose_music` route remains backward compatible; it is not silently rewritten for older saved jobs. The curated selector adds fine genre control without another model, subscription or generated-audio dependency. Official downloadable sources were retained so the editor can keep exact permission evidence; platform-only popular music would require a separate platform publishing workflow or direct rights agreement.

To add a track, inspect the original rights-holder page and exact recording license; add its source, SHA-256, credits, genres, fit note and honest popularity status to the packaged catalog. Reinstall only after reviewing a changed source hash. Add measured musical timestamps only after checking that recording. Record a dated primary popularity observation rather than a permanent “viral” flag. Do not bulk label source collection order or view counts as audience preference.

Once the channel is connected, compare similar episodes using different genre candidates and keep the chosen track ID/version with the video's analytics. Evaluate retention, viewers choosing to watch, completion and feedback alongside script/topic differences. An uncontrolled view-count difference is an association, not evidence that the soundtrack caused reach. No channel-performance experiment or public upload was run to build this library.

Validation for this addition: **six focused tests passed** for offline selection, recent-use rotation, least-recent fallback, test-only/tampered asset exclusion, changed-download refusal and rights/popularity separation. All fourteen actual downloaded recordings fully decode with FFmpeg, all fourteen installed registrations pass current integrity/eligibility checks, and all six supported genre selections resolve. The ignored local `VALIDATION.json` preserves those technical results. These checks do not constitute a listening verdict or an audience-performance test.

## Effects and environment coverage

The [sound catalog](../src/yt_pipeline/sound_catalog.json), [sound library module](../src/yt_pipeline/sound_library.py) and [sound tool](../tools/curate_sound_library.py) add **16 reusable assets** alongside the fourteen music recordings. Twelve are original deterministic software signals with bounded peaks/durations; they use no sampled app audio, voice imitation, generation service or third-party recording. Four are downloaded ambience items from their original permitted source. The existing generic `original_graphic` source bucket labels software-made assets; each original signal's evidence explicitly identifies its media type as audio and retains its synthesis recipe.

| Categories | Available assets | Intended use |
| --- | --- | --- |
| `message_incoming`, `message_outgoing` | Two restrained variations each | One cue at an actual message arrival, with stable direction and subtle variation |
| `notification` | One soft notification | Use instead of a second bubble cue when the same incoming message is already previewed |
| `transition` | Two short air movements | A meaningful conversation/screen switch, not every camera move |
| `error`, `low_battery` | One quiet cue each | A real compiled error or battery event |
| `glitch` | One bounded 0.21-second interruption | A planted phone interruption; not constant distortion |
| `reveal`, `impact` | One restrained reveal and one low athletic impact | Explicit story/action accents; never automatically add a loud sting to every ending |
| `ambience_rain` | Mixkit “Light rain loop” | Established rainy setting; source is 15 seconds, no seamless-loop claim |
| `ambience_office` | Mixkit “Office ambience” | Established office setting; approximately 42 seconds |
| `ambience_cafe` | Mixkit “Restaurant crowd talking ambience” | Established café/restaurant setting; 120 seconds; keep crowd below character speech |
| `ambience_station` | Mixkit “Train waiting at station” | Established station setting; approximately 42 seconds |

The original source pages are [rain](https://mixkit.co/free-sound-effects/rain/), [ambience](https://mixkit.co/free-sound-effects/ambience/) and [train](https://mixkit.co/free-sound-effects/train/). These exact ambience recordings use the **[Mixkit Sound Effects Free License](https://mixkit.co/license/modal/sfxFree/)**, a different license from the music license. It permits incorporation into larger edited projects, including commercial YouTube videos. It does not permit redistribution as standalone stock/source files or rights-management registration. Only source metadata and the installer are committed; each installation downloads its own recordings. Source titles describe the atmosphere, not a verified real-world recording location or recording method.

```powershell
python tools/curate_sound_library.py list
python tools/curate_sound_library.py install --originals-only
python tools/curate_sound_library.py install
python tools/curate_sound_library.py select message_incoming --selection-key episode-42
```

`install_sound_library(workspace, include_ambience=True, keys=None)` prepares/registers selected items with definitions, source/license snapshots and hashes. Original cues install without network calls. `select_sound(workspace, category, selection_key='', genre=None, avoid_asset_ids=())` chooses an eligible installed variant offline and returns its asset plus mix guidance. `mix_sound_events(workspace, samples, rate, events, silence=(), speech_ranges=())` mixes explicit events into a mono 16-bit PCM timeline and returns resolved asset IDs, source hashes and credits for the caller's checkpoint/provenance.

An event supplies `category` and absolute `start`, with optional `selection_key`, `genre` and bounded `gain`. Ambience may specify a shorter `duration`; effects must fit in full and cannot be silently truncated. Longer ambience is not invented by assuming an unverified seamless loop. The mixer fades source edges, ducks ambience during supplied speech intervals and hard-mutes every supplied blackout interval **after** effects are added. The calling editor must supply those intervals and keep returned source records with the exported video. No source is chosen for an unmentioned environment, and no API is called to invent a missing sound.

New chat plans resolve one notification-or-message cue, compiled switch/battery/glitch cues, and any explicitly directed atmosphere/accent. A message has one speech occurrence even if it appears in both a notification and bubble. There is deliberately no repeated typing sound and no hard horror jump-scare preset. An explicitly opted-in job calls the mixer after voice and music so silence wins; older completed videos are not retroactively changed. Other genres can call the library with deliberate scene-event choices.

This is **core audio coverage**, not all possible audio. Footsteps, doors, dogs, mail delivery, crowds beyond the selected setting, specific sports Foley, custom musical builds and natural expressive character acting may still require a separately licensed source or a new deliberate sound decision. No waveform/decode check can establish that a sound is pleasing, that an ambience loop is seamless or that an audience will prefer it.

Sound-library validation: **six focused tests passed**, covering network-free original installation and reuse, deterministic bounded signals, variation/integrity checks, genre/category holds, complete-effect timing and gain limits, speech-ducked ambience and exact blackout silence. Actual source recordings and registered assets are audited locally under `Resources/Music/sound-effects-20261105/`. No subjective listening or owner approval is inferred.
