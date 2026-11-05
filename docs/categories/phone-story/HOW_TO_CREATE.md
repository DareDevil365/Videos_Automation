# Create: phone-screen stories

Latest sound/publishing update: new plans use [stable character voices and ducked genre music](../../CHAT_AUDIO.md), retaining actual silence during blackouts. A notification that previews a message speaks it once at first visibility and stays through the complete line. [Make + upload](../../AUTOMATIC_PRODUCTION.md) supplies the separate opted-in production/public publishing route; YouTube account connection can be deferred while rendering and metadata finish. The ordinary batch workflow below remains a test-only preview. [Genre writing/timing guidance](../../../src/yt_pipeline/skills/short-video-writing/SKILL.md) is loaded by the program, not only installed for an assistant.

This is the channel's reusable phone-screen storytelling format. Comedy, mystery and thriller stories happen entirely inside private message conversations and phone events. It extends the existing durable `server_chat` v2 pipeline with `phone_story: true`; it is not a separate application or a collection of manually edited videos.

## Start a video

Open `start_pipeline.cmd`, choose **New phone story**, enter a premise and press **Start batch**. The native shortcut creates a thriller plan. Change `chat_tone` in a fresh, uninitialized plan to `comedy` or `mystery`, or use the CLI:

```powershell
.venv\Scripts\python.exe run_pipeline.py phone-plan --tone mystery --topic "An original mystery told through private messages with a fair final answer" --output Resources/Plans/new-phone-story.json
.venv\Scripts\python.exe run_pipeline.py --env-file .env batch-run --plan Resources/Plans/new-phone-story.json
.venv\Scripts\python.exe run_pipeline.py batch-status --plan Resources/Plans/new-phone-story.json
```

Plans and outputs stay local under `Resources`. Choose a new filename and ID for changed initialized plans; jobs keep immutable request/checkpoint hashes. Publishing stays disabled/test-only. The standalone program requires the configured text API and FFmpeg, not an interactive ChatGPT or Codex session. The optional OpenAI API adapter is described in [provider setup](../../TEXT_PROVIDERS.md).

## Story content versus editing

The model writes the original messages and story facts: phone owner, contacts, which private conversation each message belongs to, fictional same-day timestamps and relevant phone occurrences. It never supplies Python, JavaScript, arbitrary layouts, file paths, image URLs, camera motion or sound instructions.

Software validates that content, compiles a fixed event timeline, measures reading holds and draws the video at 720x1280, 30 fps. The phone owner consistently sends right-hand bubbles even if the first message is from an unknown sender. Returning to a conversation restores only its own already revealed messages. Navigation, header/contact actions, colors, bubble geometry, scroll, camera emphasis and sound remain program decisions.

| Component | Implemented behavior |
| --- | --- |
| Contact header | Stable name/initial avatar or registered photo; back, voice-call, video-call and menu symbols |
| Private conversations | One phone owner plus 1-5 contacts, separate histories, automatic slide on a thread change |
| Themes | Light, dark, rose and sage app palettes; original code-drawn quiet wallpaper patterns |
| Optional photo wallpaper | Explicit `phone_wallpaper_ids` mapping thread IDs to eligible registered image IDs; no automatic download or generated photo |
| Story timestamps | 24-hour HH:MM in status/header context and individual message bubbles; chronological same-day validation |
| Message animation | Entry, scrolling, typing dots, bounded emphasis and viewport camera motion; navigation/composer stay fixed |
| Phone occurrences | Low-battery alert, bounded glitch, 1.5-second black screen, elapsed-time lock screen and incoming notification |
| Sound | Stable distinct character voices, one soft pop per arrival, quiet ducked genre music; a notification is voiced once and blackouts remain silent |
| Completion | Existing local MP4, SRT, cover, QA, provenance and resumable stage records |

Call/menu symbols are visual app controls in a rendered video, not actual telephony integration. Registered GIF/still message attachments are supported through `chat_attachment_ids`. No calling screen, live typing text, home-screen app launcher, charging/unlock interaction, group phone conversation or arbitrary app recreation is implemented. Normal chat supports 2-3 participants; this private-thread mode supports up to six total participants. Pattern/initial fallbacks make it work without stock assets. A hacker photograph is supported only after registering a permitted source and explicitly assigning it as a wallpaper; a hoodie is not silently downloaded or invented.

## Story contract

The outer script keeps `version: 1`, exact `text`/`onscreen`, `hook` equal to the first actual message and a real final payoff unit. `phone_story` contains:

```json
{
  "pov": "Ari",
  "contacts": [{"id": "c1", "name": "Unknown"}],
  "threads": [{"id": "unknown", "contact_id": "c1", "theme": "dark"}],
  "beats": [{"unit_id": "u1", "thread_id": "unknown", "time": "18:31", "events": ["notification"]}]
}
```

This is a field illustration, not a complete valid episode. Writing v2 uses 10-26 messages, 50-145 words and 18-90 seconds; retained writing v1 uses 12-28 messages, 55-150 words and 22-90 seconds. Both allow at most 12 words per message and must fit complete reading/speech/event time. Every beat references one actual unit in order. Private messages must come from the phone owner or that thread's contact. No separate Narrator character; actual message speakers can have local voices. Contacts cannot duplicate the owner. Timestamps cannot move backward or cross midnight in this first version.

Events occur **before** their associated message. Supported names: `switch`, `low_battery`, `glitch`, `blackout`, `time_jump`, `notification`; software inserts navigation on thread changes even when the writer omits `switch`. Battery/glitch must precede blackout in that beat or an earlier beat; a time jump must advance the actual story clock. Incoming notifications preview that beat's contact message. Do not put every event into every story. A three-hour jump is computed from the actual story timestamps, not a decorative label. Full reading holds are added after events, never stolen to squeeze the story into its time limit.

## Writing quality

New phone plans enable `chat_script_review: true`. The selected text provider writes once, may repair one structural failure, then critiques the **writing only** using exact quotations of the actual opening, planted clue and designated payoff. Software also requires that quoted clue to occur in the first third of the conversation; a last-minute hint cannot be mislabeled an early plant. A failed critique allows one full revision and one recheck; a second failure holds the job. At most five writing operations in one completed pass: writer, structural repair, critique, revision, recheck. Bounded project failover and later resumption after network errors can require more HTTP attempts; every sent attempt is counted in usage. There is no model editor, timing director or visual review hidden in this path. A supplied script remains explicitly `provided_script`; it is not relabeled model-written.

The [humor playbook](../../../research/formats/entertainment/CHAT_HUMOR_PLAYBOOK.md) records actual Beluga frame observations, external research and a reusable writing checklist. Curiosity, surprise, anticipation and an earned payoff are flexible craft choices, not one compulsory first-line formula. New comedy briefs vary the mechanism instead of always making a household rule backfire. A thriller needs causally planted answers; an unplanted prank or dream cannot replace its resolution.

Counts, exact quote checks, timeline consistency and technical QA are automatic. Humor, emotional impact, originality and audience response are not certified by those checks or a model's favorable judgment. Treat the output as a candidate until the owner approves it. Technical tests deliberately use synthetic stories and do not demonstrate excellent writing.

## How to extend the editor

See [the implementation plan and current scope](../../PHONE_STORY_IMPLEMENTATION.md). Add a trusted screen/event renderer, its finite story-data fields, local timing and meaningful tests; register it through the compiler. Do not ask the model to generate executable rendering code. This keeps layouts, symbols, screens, effects and sound reusable independently of the story while retaining deterministic recovery.

## Writing v2, GIFs and gentle stories

New plans also select `chat_writing_version: 2`; [the writing-quality guide](../../CHAT_WRITING_QUALITY.md) explains the focused development/read/revision process and limits. Current v2 bounds are 10-26 messages, 50-145 words and 18-90 seconds; version-1 saved requests keep their older bounds. `phone-plan --tone story` supports gentle emotional narratives without a compulsory threat/twist.

`chat_attachment_ids` maps up to eight existing message IDs to registered GIF/still-image asset IDs. GIFs retain their source/license record, animate on the frame clock and get at least a three-second reading/view hold. The loader accepts at most 240 frames; MP4/voice-note attachments are not implemented. `chat_group_name` gives normal group chats their actual short header. A private-thread phone story still uses its contact headers. The [assistant-authored examples](../../../examples/assistant-five/README.md) demonstrate a GIF, private chats and a fifteen-minute jump without remote generation.
