# Create: original chat Shorts

New plans now enable [distinct character speech and background music](../../CHAT_AUDIO.md). The registered [genre library](../../MUSIC_LIBRARY_PLAYBOOK.md) supplies an offline track; install it with `music-library --install` on a new setup. Each message is spoken in its character's voice when first shown, with measured full-line holds, quiet cues and music ducking. Saved reading-led jobs remain unchanged. For a topic → titles/description → public-upload flow use [Make + upload / produce](../../AUTOMATIC_PRODUCTION.md); the preview steps below remain test-only.

For multi-conversation phone fiction, see the new [phone-screen channel format](../phone-story/HOW_TO_CREATE.md). It shares the local editor and adds private histories, wallpapers, timestamps and phone events.

Current route: `server_chat` with `chat_editing_version: 2`. Gemini writes the conversation; Python/Pillow/FFmpeg handles every edit. Output is **720x1280 (9:16)** by default, with two or three recurring fictional participants, a clean messenger-inspired app crop, measured scrolling bubbles, fixed contact/call/menu chrome, selected camera emphasis and soft local message sounds. New plans add local character TTS and genre music. No separate narrator character, model director, generated photos, body/costume layer or lower panel is required.

## Use without Codex/ChatGPT

Open `start_pipeline.cmd`, click **New chat**, enter a short topic (or leave blank for a roommate comedy), then click **Start batch**. The saved plan is selected automatically. Local Gemini credentials/free-tier configuration are read by the existing CLI child process; Codex/ChatGPT does not need to be running. **Open produced videos** opens the local export directory. The new button is wired and its plan/preflight paths are tested; extensive interactive GUI QA is not claimed.

CLI equivalent:

```powershell
.venv\Scripts\python.exe run_pipeline.py chat-plan --topic "A petty household rule backfires" --output Resources/Plans/my-new-chat.json
.venv\Scripts\python.exe run_pipeline.py --env-file .env batch-run --plan Resources/Plans/my-new-chat.json
.venv\Scripts\python.exe run_pipeline.py batch-status --plan Resources/Plans/my-new-chat.json
```

Choose a fresh plan filename/ID after changing an initialized plan. Missing keys, free-tier confirmation, provider quota/cooldown, invalid scripts and unusable assets remain holds; there is no paid fallback. Explicitly configured independent-project pools can distribute requests while respecting each project's cooldown; see provider setup. The existing authorized development local-budget override does not grant provider quota. Publishing remains disabled/test-only.

## Model versus software responsibilities

| Responsibility | Owner |
| --- | --- |
| Write original conversation from the topic, exact message text and content metadata | Selected text provider: one writing call, at most one structural repair; new plans enable bounded writing review |
| Validate 2-3 participants, no narrator, exact onscreen/message identity, hook, word/unit bounds and final answer identity | Software |
| Map stable speaker identities/colors and optional registered photo avatar slots | Software |
| Set complete-message reading holds and typing gaps on the 30 fps clock | Software |
| Draw current/past messages only, limit visible history, preserve font sizes, animate entry and reaction emphasis | Software |
| Generate original cue audio locally and assemble MP4/captions/cover | Software |
| Technical dimensions/timing/audio/decode/hash checks and resumable checkpoints | Software |
| Decide whether the writing is funny, natural and satisfying | Owner/editorial judgment; not certified by structural QA |

The model does not supply a storyboard, camera instructions or audio plan. Normal chat timestamps are local defaults; phone stories can supply explicit fictional story times. V2 rejects legacy hook-alternative, director editorial-review and visual-review settings. New plans separately enable `chat_script_review`: writing-only critique, at most one revision and one recheck, without model editing calls. See [provider setup](../../TEXT_PROVIDERS.md). It also rejects factual-source requests: original fiction is the supported script-only route. No claim is made that these rules constitute an intelligent autonomous comedy critic.

Contract: 12-22 complete messages, 40-100 words total (existing three-word tokenization tolerance), mostly 2-7 words and at most 12 words each. Actual complete reading duration must fit 18-55 seconds; excessive content holds instead of truncating a message or shrinking fonts. Current timing uses a bounded word/character reading estimate plus typing and payoff holds; it is not measured audience comprehension. `voice.json` retains the common timing-stage filename. Reading-only requests record `narration: false`; voiced requests record the actual cast, complete speech boundaries, mixed music provenance and `narration: true`. New writing-v2 bounds are 8-20 messages, 35-105 words and 12-55 seconds; this paragraph's older 12-message/18-second bounds describe writing v1.

## Optional real-photo avatars

`chat_avatar_ids` accepts up to six registered image IDs in first-speaker appearance order. `chat_avatar_crops` optionally gives matching normalized [left, top, right, bottom] crops. Eligibility/hash checks run before rendering; actual source metadata stays with the asset. Missing optional photos fall back to stable initial avatars. The software does not download arbitrary Google images or infer their rights. The live demonstration used a CC0 black-cat photo and a public-domain raccoon photo, with attribution/source records retained, and no generated image. Fresh plans work with initials and need no image-search account.

## Live evidence and limits

The normal `chat-plan` / `batch-run` route produced **The Dishwasher Decree**, 29.0 seconds, 13 messages, two stock-photo avatars and original local cue audio. Script origin is `gemini`; edit-plan origin is `compiled_chat_rules_v2`; no script was manually supplied. Gemini performed the writing and one structural repair. All subsequent edit/timing/render operations were local, with zero editing-model calls. The exported video passed technical checks and sampled frames were inspected. Its closing message repeats the preceding reply, so it is a working format demonstration with a weak ending, not owner-approved comedy.

Local export: `Resources/Productions/chat-20261105-2b77addc/chat-short/`. The exact script, compiled plan, measured reading timeline, visual records and QA accompany the video. These are ignored local outputs rather than media shipped with the repository. Re-running an unchanged ready job uses intact checkpoints without another model call.

## Legacy behavior

Already-created requests without `chat_editing_version` retain v1: the older full-interface renderer, Gemini concept/director/review workflow and local character voices, 16-18 messages, 85-125 words and 30-55 seconds. Explicit version 1 can reproduce that route. New CLI/batch `server_chat` requests default to version 2; direct Python callers select the version explicitly. V1 exported prompts remain historical/reference contracts; `Resources/Prompts/server_chat.v2.writer.json` and `.v2.editor.json` describe the new path.

The separate [tea/chat preset](../chat/HOW_TO_CREATE.md) still uses split-panel chat. The [Beluga reference study](../../../research/formats/entertainment/BELUGA_CHAT_REFERENCE_2026-11-03.md) records the initial access limitation and subsequent actual frame sampling. Original names/dialogue/art/sound are used; no reference creator footage or characters are copied.

Current writing update: fresh plans select `chat_writing_version: 2`, with 8-20 messages, 35-105 words and 12-55 seconds. The [writing-quality guide](../../CHAT_WRITING_QUALITY.md) explains three compact sketches in one call, an unprimed seven-criterion reader and bounded contextual revision. Earlier counts above describe writing version 1. Provided scripts remain provided and skip model writing. Optional `chat_group_name` and registered `chat_attachment_ids` supply an actual header and animated GIF/still messages through the local editor.
