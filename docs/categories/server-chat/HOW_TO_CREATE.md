# Create: Original server-chat comedy

Preset: `server_chat`. Channel: `entertainment`. Output: a full-screen fictional server conversation, with original usernames/initial avatars, complete message text, smooth entry/scroll and distinct local character voices. No stock, character bodies, real-service screenshot or lower panel is required.

Use the [shared batch recipe](../README.md#shared-playbook-batch-recipe) with `playbook: "server_chat"`, `fiction: true`, `test_only: true`, `bottom_kind: "none"` and `require_music: false` (or an actual eligible music ID). Supply only a creative brief/topic if the program should invent the story; do not supply `script`/`script_file` or a manually prepared storyboard. New requests enable hook alternatives, strict hooks and separate exact-payoff review. Keep `visual_review: "required"` while evaluating actual output.

Target: 16-18 short messages, 85-125 total spoken words, measured duration 30-55 seconds, 2-3 actual participants and no narrator. Each message is at most 15 words; mostly 3-8 words is preferable. Every onscreen message must equal its exact spoken line. The hook is the first actual message. The final message should enact the planted consequence/reversal, without an explanatory postscript.

The program compares three original comedy concepts, selects one, writes the messages, validates the contract, separately critiques the exact setup/payoff, and directs consistent local voices without changing the script. It permits one structural repair and one substantive rewrite; quotas, malformed outputs and unresolved critique remain holds. The editor reveals only current/past messages, scrolls to keep the latest message readable, and retains stable distinct participant colors. Message arrival lasts about 0.18 seconds; the remainder stays readable for measured speech. Sound remains local character speech and optional explicitly selected music; this does not implement notification sound design or silent reading-only timing.

Run from the root:

```powershell
.venv\Scripts\python.exe run_pipeline.py --env-file .env batch-run --plan Resources/Plans/my-server-chat.json
.venv\Scripts\python.exe run_pipeline.py batch-status --plan Resources/Plans/my-server-chat.json
```

Use a new stable plan ID after changing an initialized brief. Inspect `script.json`, the concept/critique and director records, `voice.json`, frame states, the actual complete video and its quality report. Passing model checks is not humor or audience approval. Do not copy reference creator names, characters, plots, screenshots, sounds or dialogue. The [reference study](../../../research/formats/entertainment/BELUGA_CHAT_REFERENCE_2026-11-03.md) distinguishes accessible page evidence from design inferences; browser playback was unavailable during the study.

The older [tea/chat preset](../chat/HOW_TO_CREATE.md) remains a separate split-panel option.
