# Make, package and upload

Implemented 5 November 2026. The owner selected **public publication** and explicitly deferred YouTube account connection. The native panel's **Make + upload** flow and CLI `produce` create a new opted-in production, generate/review its script, synthesize character voices, select licensed genre music, render, check it, create titles/description, and attempt the existing resumable YouTube uploader. No assistant session is required. These commands use the configured text API; they do not generate photos or videos with a visual-generation service.

## Start a production

In `start_pipeline.cmd`, enter a topic in the production row, choose genre, chat/phone format and visibility, then **Make + upload**. `public` is the default for this new flow. The old **Start batch** / **New chat** / **New phone story** flows remain test-only previews. **Resume production** uses the selected saved production request; **Choose** can select an earlier request. Repeating a saved request resumes its existing job instead of creating another.

```powershell
.venv\Scripts\python.exe run_pipeline.py music-library --install
.venv\Scripts\python.exe run_pipeline.py --env-file .env produce --topic "A boss is invited into the wrong group chat" --genre comedy --format chat --visibility public
.venv\Scripts\python.exe run_pipeline.py --env-file .env produce --resume JOB_ID
.venv\Scripts\python.exe run_pipeline.py finish-production JOB_ID
```

`music-library --install` explicitly downloads the hash-pinned permitted catalog. After installation, genre selection is offline. `music-pick mystery` inspects a suitable registered track. A chosen `music_id` is frozen in the job request before execution, so retries do not switch music. Explicit asset/voice assignments can be supplied in a saved production request:

```json
{
  "topic": "A family discovers why an unknown sender has a missing bag",
  "genre": "mystery",
  "format": "phone",
  "visibility": "public",
  "request": {
    "chat_voice_ids": {"Unknown": "am_onyx", "Ari": "am_adam"},
    "creative_brief": "Use a fair early clue, plausible private knowledge and a concrete causal reveal."
  }
}
```

Use `produce --request path/to/request.json`. Speaker-name overrides must match the final script. For fully automatic character names, omit `chat_voice_ids`; the installed distinct-voice pool assigns one voice per speaker. Other playbook jobs can use the same package/upload stages by setting `metadata_version: 2`, `auto_publish: true`, the intended `publish_visibility`, and the matching channel policy in their creation request. They still need their own permitted visual prerequisites. The new one-topic creator currently supplies chat and phone stories, not a universal asset-planning UI for every format.

## State and recovery

`production.py` orchestrates the existing eight-stage pipeline. Script/voice/visual/render/QA/package artifacts keep their original hashes. Packaging version 2 uses `publication_metadata.py`: three title choices, one selected title, a unique content description, exact supporting script quotations and one/two subject phrases. The [metadata playbook](TITLE_DESCRIPTION_PLAYBOOK.md) explains selection and evidence limits. Required credits, sources and disclosures are appended by software; they are never silently truncated to fit the API description limit.

`finish_production` verifies the completed artifacts. A missing account returns `awaiting_youtube_connection` and saves `publication.json` beside the job. Rendering remains ready. Connection later only needs this exact job's publishing step. A worker tick also considers explicitly opted-in ready/processing jobs; it does not sweep old test previews into publication. The publisher persists the resumable session and confirmed byte offset, reconciles ambiguous completion, checks the OAuth channel identity, and reports the returned remote visibility. A public request is not called published until YouTube actually reports it public and processed. An unresolved session is not replaced with a duplicate upload.

Publication approval binds the video, title, complete description, category, kids/disclosure fields, schedule and channel publication mode. The opted-in flow records that exact approval automatically under the owner's standing request. Changed policy/content needs a new matching approval; per-job visibility and channel policy must agree. Existing explicit private and scheduled publishing remain supported. Test-only media, changed/expired source evidence, failed QA, paused channels and identity mismatches still hold.

## Connect YouTube later

No credentials or OAuth window were requested during this implementation. When ready, supply an installed-app OAuth client JSON and use:

```powershell
.venv\Scripts\python.exe run_pipeline.py authorize entertainment path/to/desktop-client.json
.venv\Scripts\python.exe run_pipeline.py config channels.entertainment.publication_mode '"public"'
.venv\Scripts\python.exe run_pipeline.py finish-production JOB_ID
```

`authorize` performs explicit browser consent, saves the credential only in ignored local storage and records the authorized channel ID. An API key alone cannot authorize uploads. Scope and API behavior follow the [official upload reference](https://developers.google.com/youtube/data/reference/rest/v3/videos/insert). Real account connection, live upload, post-upload Analytics and audience response remain untested here; transport fixtures verify public/private policy, metadata, partial-upload recovery and duplicate prevention. The three new voiced exports remain local test-only review candidates and are not queued for public release.
