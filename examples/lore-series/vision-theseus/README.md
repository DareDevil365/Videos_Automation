# Vision Beat Himself With a Question

A standalone MCU recap of the WandaVision (2021) finale. This is separate from later VisionQuest events and from the comic story that inspired the Ship of Theseus conversation.

The hook connects the unexpected boat question to the fight's resolution. The body distinguishes the rebuilt original body from Wanda's magically created Vision, demonstrates the two-ship puzzle, then resolves the fight through restored memories. The script avoids claiming that restored data makes White Vision the same emotional partner Wanda says goodbye to. It finishes on the result without a subscription or continuation line. The engagement argument is an editorial hypothesis, not a view guarantee.

The research brief uses [Jac Schaeffer's creator interview](https://www.etonline.com/wandavision-series-finale-interview-jac-schaeffer-161951), [GamesRadar's scene discussion](https://www.gamesradar.com/wandavision-the-comic-book-roots-of-the-finales-ship-of-theseus-scene/) and [Marvel's goodbye article](https://www.marvel.com/articles/tv-shows/wandavision-paul-bettany-vision-goodbye?linkId=112916480). The exact source review hashes the supplied script and brief.

Cutouts carry the identity comparison in u1/u2, White Vision's memory portrait in u6, and the closing portrait in u8. The geometric figures in u3 explain the different origins. The u4/u5 ship diagrams use a separate quiet grid and moving planks. In u7 a geometric hand reaches the forehead before the memory effect, followed by White Vision leaving. Those movements are illustrative blocking. The cutout crops are prepared at comparable facial scale and share a scene grade.

The series file contains script-focus annotations. The local rules choose each character, prop and setting representation and record the reasons. The compiled `visual-decisions.json` is retained with the final package. Voice pairing comes from the normal series rotation, independent of character gender, and is fixed before narration is synthesized.

```powershell
.venv\Scripts\python.exe tools/create_adaptive_hero_shorts.py --only vision --prepare-only
.venv\Scripts\python.exe tools/create_adaptive_hero_shorts.py --only vision
```

The local production folder is `Resources/Productions/vision-theseus-adaptive-20261106/part-1/`. The supplied writing and local renderer use no Gemini text generation or image generation. MCU character images and the fan-prepared White Vision cutout remain local-preview inputs; no publication rights are inferred. Source pages and credits are in `media-sources.json` and packaged metadata. The title, description, source brief, voices, captions, quality report and video remain together in the production packet.


Validation: the final 42.17-second portrait export passed local technical QA, all saved package hashes matched, and the actual role voices were checked in the measured unit records. Narration silence detection at −42 dB found no run of 0.3 seconds or more. Sampled MP4 frames were inspected. The builder’s unchanged text-provider usage check passed.
