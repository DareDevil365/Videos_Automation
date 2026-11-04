# Text APIs and local key selection

The standalone app defaults to its existing Gemini route. Phone-screen editing is local; either supported text provider receives the same structured story contract. This does not require Codex/ChatGPT to run alongside the app. Configuration and `.env` remain local/ignored. Never put credentials in plans, prompts, guides or Git.

## Gemini

Existing `GEMINI_API_KEY` (or legacy `GOOGLE_API_KEY`) and free-tier confirmation continue to work. To keep several keys locally, give each an environment variable and select one explicitly:

```dotenv
GEMINI_API_KEY_STORY=your-local-key
GEMINI_API_KEY_OTHER=another-local-key
```

```powershell
.venv\Scripts\python.exe run_pipeline.py config gemini.key_env '"GEMINI_API_KEY_STORY"'
```

The values above are placeholders, never real keys. A `key_env` config field stores only the environment variable's name. That single-key selection remains available. For the owner's explicitly separate projects, use the new project pool:

```powershell
.venv\Scripts\python.exe run_pipeline.py gemini-projects-import --file "C:/path/to/private-keys.txt" --env-output .env --distinct-projects --free-tier-confirmed
```

This explicit import copies recognized key tokens into private local environment slots and stores only environment variable names plus project labels in local config. It never uploads the key file, prints keys or overwrites the source file. It is idempotent for the same ordered input and accepts only private `.env`/`.env.*` targets, never `.env.example`. Identical credentials cannot be registered as separate project profiles. The flags confirm that keys actually belong to distinct free-tier projects; different keys alone do not establish different projects. For several keys from one project, use one project profile so its limit is not counted twice.

The scheduler distributes requests among available declared projects by their local usage. A 429 cools only its project; another independent project may complete the request. A single generation attempts at most three projects, then leaves work queued. Access failures cool that profile, while malformed requests, content failures and model-contract problems are not retried across keys. Cooldowns and usage persist in SQLite across restarts, cached completed writing remains reusable even when all projects cool down, and the selected free model never silently changes. No paid provider fallback occurs. Aggregate local budgets remain in force in production; the owner's development budget override preserves counts while disabling local caps. Actual provider quota/balance is not inferred from the local count. Google states that [limits apply per project, not per API key](https://ai.google.dev/gemini-api/docs/rate-limits); multiple keys from one project do not multiply quota.

## Optional OpenAI API

The optional adapter uses the [Responses API with structured JSON output](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses), `store: false`, bounded output, a local cache and no hosted tools. It is intended for script writing and writing-only review; image review is explicitly unsupported. No claim is made that OpenAI API use is free or included in any subscription. Actual model access/billing depends on the selected account. This implementation was transport-fixture tested; no live OpenAI call was made during implementation.

Set `OPENAI_API_KEY` locally, then choose an API model available to your account and enable it explicitly:

```powershell
.venv\Scripts\python.exe run_pipeline.py config openai.model '"YOUR_API_MODEL_ID"'
.venv\Scripts\python.exe run_pipeline.py config openai.api_usage_enabled true
.venv\Scripts\python.exe run_pipeline.py config text_provider '"openai"'
```

The model placeholder must be replaced. No OpenAI model is silently selected, and no live paid request is made merely by opening the app. Use `openai.key_env` to select an alternate locally defined variable such as `OPENAI_API_KEY_STORY`. Run production commands with `--env-file .env` to load the local variables. Run `doctor` to check selected-key presence without printing it.

Strict OpenAI schemas require all properties; optional fields are sent as nullable, then null fields are omitted before the shared local contract checks. Refusal/incomplete output, missing keys, provider errors and exhausted budgets hold the job instead of accepting partial scripts. Selecting another key/model does not improve an existing ready export; create a fresh plan to request another story. Provider/model selection is workspace configuration rather than an immutable per-job binding. Keep it stable while an active batch runs; create a fresh plan for a comparison. Each cached response records its actual model and Gemini project label. The current development comparison explicitly selects the existing supported `gemini-3.8-flash` option; the default configuration remains `gemini-3.5-flash-lite`. Set `gemini.model` and optional `gemini.thinking_level` with the same `config` command; only the existing free-model allowlist is accepted.

To return to Gemini:

```powershell
.venv\Scripts\python.exe run_pipeline.py config text_provider '"gemini"'
```

## Quality expectations

New chat/phone plans enable a bounded writing critique. It can reject a script with missing causes, repeated endings or implausible private-chat knowledge. This adds model writing calls, not a model video editor. A valid JSON response or positive critique does not establish excellent humor, suspense or audience retention. Source research and local validation improve the process; rendered examples and owner feedback determine readiness.
