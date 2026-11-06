# Screen-story Shorts

Two assistant-authored original recaps use the existing local comic-style editor. Doctor Strange is What If…? season 1 episode 4 (2021); Civil War is the 2016 film, not the comic event. The owner prioritizes connected explanation, iconic scenes and a late payoff over a forced runtime. YouTube’s [current portrait/square Shorts limit](https://support.google.com/youtube/answer/15424877) is three minutes. These drafts measure about 55 and 95 seconds with their subscribe lines.

Read each SCRIPT.md, source brief, selection/coverage record and series.json. The series keeps per-beat palette/element reasons and speech-anchored visual cuts. The lower Marvel theater is present throughout. The spoken and graphic subscribe card comes after the ending under the owner’s latest preference.

```powershell
.venv\Scripts\python.exe tools/create_screen_recaps.py --measure-only
.venv\Scripts\python.exe tools/create_screen_recaps.py
.venv\Scripts\python.exe tools/create_screen_recaps.py --render
```

Use `--only strange` or `--only civil` for one production. Preparation freezes a plan and creates a storyboard without rendering the final video. Changed inputs need a new `--build-suffix`. Setup uses the project environment, installed local voice/alignment models, curated music and reaction presets. Posters must be downloaded and inspected first; exact source URLs are in the builder. Publicity artwork/audience photos remain local-review assets. No upload is requested here.

The assistant supplies writing and direction; the build asserts unchanged text-provider usage. Pillow draws geometric actions; Kokoro voices, local forced alignment and FFmpeg complete the export. No Gemini writing or visual-generation service is used. The software validates source IDs, scenes, anchors, measured timing and assets. It cannot certify that a story will get views or recreate the film’s full emotional experience.
