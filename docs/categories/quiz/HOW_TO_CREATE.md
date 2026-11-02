# Create: quiz with real thinking time

Preset `quiz_pause`, education channel, 20–40 seconds including its actual silent thinking interval, 45–90 spoken words and 5–9 units. It uses original graphics, the accepted education voice and no lower panel; music is optional.

1. Prepare an original self-contained puzzle/question and a checked explanation. Give all necessary conditions, distinguish it from a subjective dilemma, and verify that the claimed correct answer follows.
2. Use a new [playbook batch plan](../README.md#shared-playbook-batch-recipe) with `playbook: "quiz_pause"`, `channel: "education"`, real source/brief inputs and initial `test_only: true`.
3. Keep the question/conditions readable. Add one short spoken thinking instruction before the answer. The director gives that scene `graphic: {"kind":"timer", "title":"Question", "labels":["exact earlier question phrase"]}` and `thinking_seconds: 3` (allowed 2–6).
4. The narrator speaks the instruction, then actual silence plays while the visible countdown runs. The answer is a later unit; other beats use callout/process/comparison graphics. A timer without matching silence, multiple timers or a timer after the payoff is rejected.
5. Run the plan and inspect `voice.json` thinking duration, `visuals.json` countdown boundaries, actual exported silence, question, answer/explanation and readable captions. Comment questions are optional after the explanation.

See [timing and editorial contracts](../../EDITORIAL_AND_SPEECH.md), [writer rules](../../../Resources/Prompts/quiz_pause.writer.json) and [new regression tests](../../../tests/test_editorial_improvements.py). The tests include synthetic local speech and an actual FFmpeg export; they do not establish that a generated puzzle is clever or that viewers will engage.
