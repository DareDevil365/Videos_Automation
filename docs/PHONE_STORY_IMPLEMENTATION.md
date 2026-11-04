# Phone-screen channel format: implementation and next work

Updated 5 November 2026. Owner direction: the program is the editor. It should combine reusable layouts, screens, themes, symbols and effects to tell different stories entirely through a phone screen. A threatening unknown sender, spouse/daughter chats, different wallpapers, a dying phone, silence and a later notification are examples of capabilities, not a mandatory script template.

## Architecture and implemented work

Retain Python/Pillow/FFmpeg and the durable eight-stage pipeline. This is a bounded extension of `server_chat` v2, selected through `phone_story: true` and the `phone-plan`/native **New phone story** entry point. It avoids adding a browser or hosted render service and preserves asset provenance, checkpoint validation and local exports. A browser-based compositor could offer richer typography, emoji and interactive UI, but adds rendering/dependency management; that alternative is not implemented.

| Module | Responsibility |
| --- | --- |
| `src/yt_pipeline/phone_editor/contract.py` | Finite contact/thread/beat schema, private-chat chronology checks, code-selected event durations |
| `themes.py` | Immutable app palettes, original patterned wallpapers, quiet optional registered-photo treatment |
| `chrome.py` | Fixed status bar, contact identity, call/video/menu symbols and composer |
| `messenger.py` | Measured bubbles, exact text, continuous scroll, typing, entry and bounded camera emphasis |
| `screens.py` | Reusable navigation slide, notification/lock screen, battery warning, glitch and black screen |
| `story.py` | Resolve story clock and current thread; isolate history; compose selected screen with no future-message leak |
| `writing.py` | Research-informed comedy brief and writing-only critique with exact evidence and at most one revision |
| `src/yt_pipeline/chat_editing.py` | Compile immutable dialogue, allocate complete reading/event holds, synthesize quiet original sound and encode/register message clips |
| `src/yt_pipeline/gemini_projects.py` | Fair scheduling across explicitly declared independent free-tier projects, separate durable cooldown/usage, bounded attempts and private key-file import |
| `src/yt_pipeline/text_provider.py` | Explicit Gemini/OpenAI provider factory, environment-key selection and optional Responses API adapter |

Flow: topic -> fictional brief -> selected text provider's structured story -> local contract checks/optional one repair -> bounded writing critique/revision -> frozen script -> event/reading timeline -> composable phone frames and sound -> existing portrait composition -> technical QA -> local export. The model describes story occurrences, not camera/timing. Optional writing review stays within script work; it does not restore the old model director/visual reviewers.

The schema separates story facts from presentation: message/thread/time and phone occurrence are data; screen styling, sound, effect duration and camera behavior are local rules. This permits adding another app skin without rewriting stories. Only one original messenger-inspired skin currently exists, with four palettes; exact selectable WhatsApp and iMessage replicas are not implemented.

## Quality and limits

Implemented: exact message identity, finite enums, participant/thread validation, chronological same-day timestamps, no narration, no future messages, isolated restored histories, preserved reading holds, silent blackouts, fixed navigation during camera moves, bounded writing revision and refusal of fabricated review quotations. Existing owner rejection and duplicate-script controls remain in force.

New app visuals remove decorative fiction/channel labels from current and legacy render paths, while preserving useful contact and source information. Sound uses one quiet rounded pop rather than per-letter chirps or stacked sharp pings. These aesthetic changes still require owner feedback.

Proposed, **not implemented**: a general phone home screen, incoming/missed-call screens, photo/video/voice-note messages, independently selectable branded app skins, broad emoji fallback assets, multi-day timestamps, automatic licensed avatar/wallpaper search and a reliable audience-calibrated quality scorer. No claim of pristine autonomous results follows from adding API keys or a favorable writing critique. Script quality must be evaluated on actual exported examples.

## Validation record

Targeted tests exercise a normal end-to-end job using only a writer and writing-review fixture, with TTS/model editing forbidden; ready jobs resume without extra calls. Separate assertions inspect private-chat isolation, correct phone-owner direction when Unknown speaks first, fixed chrome, exact review evidence, revision limits, black pixels and zero audio samples through the blackout. Provider transport fixtures cover explicit OpenAI enablement, selected environment key, schema adaptation and cache reuse without credentials in payloads.

Live validation and final test counts are recorded in the root [project guide](../PROJECT_GUIDE.md). The first live Gemini request exposed a complex schema rejection; the wire adapter omits combinatorial array-count bounds while the local contracts retain and enforce them. The supported 3.8 Flash writing comparison also exercised separate project labels in actual cached responses; a later generation timed out, then received HTTP 503, and remains queued. A failed writer/repair remains held and is not presented as a completed video. This distinction matters because fixtures establish the editor's behavior, not model writing quality or live account access.

Final checks: 287 full-suite tests passed (two existing Pillow warnings), then 56 relevant tests passed after final changes. Documentation validation covers 86 managed files, 558 local links and all 39 moved-file destinations. Both completed live prototypes have intact eight-stage hashes; neither is approved writing. The full-event Gemini 3.8 comparison remains retry-wait at script after provider timeout/503; its partial files are not a finished episode.
