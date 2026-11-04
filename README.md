# YouTube automation project

A local Python application for researching, writing, voicing, editing and checking Shorts for entertainment and education channels. Gemini supplies structured writing/review; local speech, Pillow and FFmpeg produce the video. Publishing is a separate adapter and is currently disabled.

Current editorial additions: twelve playbook presets, including bounded landscape illustrated-story and documentary chapters, including full-screen original server-chat comedy, rewrite reveal, myth/fact and a quiz with real thinking silence/countdown; hook alternatives, exact-payoff review, structured local speech delivery, and source-grounded red animated detail callouts. See the [category guides](docs/categories/README.md), [implementation plan](docs/EDITORIAL_IMPROVEMENT_PLAN.md) and [operating contracts](docs/EDITORIAL_AND_SPEECH.md).

For chat Shorts, open the local panel and choose **New chat**, then **Start batch**. Gemini writes the conversation; the v2 editor controls reading time, portrait message cards and sound without a model director or narrator. See the [chat guide](docs/categories/server-chat/HOW_TO_CREATE.md).

Start reading here:

1. [Project status: done, partial and remaining](docs/PROJECT_STATUS.md)
2. [Whole-code walkthrough: every source module and data flow](docs/CODE_WALKTHROUGH.md)
3. [How to create each content category](docs/categories/README.md)
4. [Agent roles, responsibilities and handoffs](agents/README.md)
5. [Architecture, technology choices and setup](PROJECT_GUIDE.md)
6. [Folder map and organization rules](docs/FILE_ORGANIZATION.md)

## Start locally

Clone [DareDevil365/Videos_Automation](https://github.com/DareDevil365/Videos_Automation) and open its root folder. The repository contains source, tests, guides, research and generated prompt contracts. Private runtime state, credentials, downloaded models/media, machine-specific plans, demonstration exports and the generated PDF stay local. References to those artifacts are labeled local-only; they are not shipped sample outputs.

From the project root in PowerShell:

```powershell
uv sync --extra production --extra dev --extra voices --extra sources --extra browser
.venv\Scripts\python.exe run_pipeline.py --env-file .env doctor
.venv\Scripts\python.exe run_editor.py serve --open
```

Python 3.11+ and FFmpeg/ffprobe are required. The existing local voice models are also needed; a fresh environment must install a voice using `voice-setup` (see [setup](PROJECT_GUIDE.md)). Save credentials only in ignored local configuration. The CLI reads `.env` only when `--env-file .env` is supplied; the production dashboard loads it at startup.

`start_pipeline.cmd` opens native batch controls. `start_editor.cmd` opens the editor; `/production` is the pipeline dashboard, `/` is the supplied-media compositor and `/legacy` keeps older formats. Nothing is scheduled just by reading these guides.

## Where things belong

| Folder | Contents |
| --- | --- |
| `agents/` | One labeled folder per role, with instructions and actual code links |
| `docs/` | Current status, code walkthrough, operating guides and category recipes |
| `research/` | Dated evidence grouped by subject; older findings need rechecking |
| `src/yt_pipeline/` | Production stages, state, integrations and CLI |
| `src/shorts_editor/` | Compositor, FFmpeg renderer, web UI and HTTP server |
| `tests/` | Contracts, recovery checks, fixture integrations and actual renders |
| `examples/` | Small request/config examples; see its index before using them |
| `Resources/` | Production plans, generated prompt contracts, assets and review exports |
| `tools/` | Documentation/preview/demo builders and documentation-link checks |
| `data/` | Private runtime database, credentials, models, caches and job evidence |

Audit on 2 November 2026: 183 tests passed; real local exports exist. YouTube account integration, real browser generation and channel performance remain unverified. Technical completion does not establish owner approval of a story/style. See the status file for exact evidence and blockers.

Current entertainment format: [Phone-screen stories](docs/categories/phone-story/HOW_TO_CREATE.md) combine private chats and phone events with a local reusable editor. [Provider setup](docs/TEXT_PROVIDERS.md) covers Gemini and the optional explicitly enabled OpenAI API route.
