# Chat comedy playbook

Research and production guidance, updated 2026-11-05. This is an editorial playbook for original, reading-led chat Shorts. Gemini writes the conversation; the application owns layout, timing, motion and sound. It is not a claim that a model or a structural validator can certify humor.

Start with the [server-chat creation guide](../../../docs/categories/server-chat/HOW_TO_CREATE.md) for commands, schema and implemented behavior. The [project guide](../../../PROJECT_GUIDE.md) explains the wider architecture. This document records the writing decisions and research behind stronger scripts; recommendations below are not all automatically enforced.

## What the owner wants

- The first actual message can create suspicion, surprise or anticipation. Treat this as a flexible craft idea, not a compulsory contradiction or fixed first-line formula. The ending should fairly resolve the specific curiosity the story creates.
- A clean messaging-app cutout, familiar like iMessage or WhatsApp, with the story told through messages. No decorative series banners or labels such as “original fiction,” “after hours,” or “common room.”
- Short natural replies, believable conflicting personalities, an escalation with comic turns, and a final payoff that adds something.
- Purposeful zooms, highlights, occasional emojis and restrained sound. Softer cues are preferred; harsh repeated typing and pings are distracting. Effects cannot substitute for a joke.
- An original Gemini-generated script through the normal application route, rather than a hand-authored demonstration that the normal workflow cannot reproduce.

These are recorded owner preferences, not findings about what every audience prefers.

## What was actually inspected in Beluga

Reference: [Beluga video xobNmldbWpo](https://www.youtube.com/watch?v=xobNmldbWpo). Analysis uses 48 timestamped frames covering approximately 0:00–2:12 of a 2:14 video, extracted using the installed `watch-video` skill. Four contact sheets were inspected. The captions mostly describe music and do not provide a reliable dialogue transcript. This was visual sampling, not a claim of continuous audiovisual viewing or measured retention.

| Approximate point | Visible observation | Transferable writing/editing inference |
| --- | --- | --- |
| 0:00–0:28 | A mundane greeting meets disproportionate moderation; short apologetic replies are met with more restrictions. The crop repeatedly isolates a speaker or reply. | Establish conflicting attitudes through behavior. A tiny goal can support a large comic overreaction. Alternate the absurd claim with a concise audience-like reaction. |
| 0:33–1:07 | Permission to participate becomes an enormous reading task. A file-size close-up makes the disproportion concrete; the document keeps expanding. | Escalate the same comic logic through a new cost or condition. One precise number or object can be funnier than adjectives such as “ridiculous.” |
| 1:10–1:38 | Time jumps and an extended form show the growing effort, yet the person still cannot obtain the original permission. | A sequence needs changing stakes, not synonyms for the same disagreement. Compress repetitive labor while keeping its consequence visible. |
| 1:41–2:06 | Another condition appears near the supposed finish; the final exchange reverses who controls the situation, followed by an abrupt reaction. | A payoff changes the relationship or meaning of earlier behavior. Stop while the audience can make the connection. |

The observed ending involves a tracking-link gag. Its useful abstraction is a change in leverage; reproducing that action is unnecessary. Use original fictional consequences. Do not reuse the creator's characters, distinctive lines, file-size premise, verification plot, footage, or sounds.

The reference does **not** open with the specific suspicious first-message design the owner now requests. That hook is a project adaptation. Its landscape framing and long runtime are also not our output contract. Borrow mechanisms, then make a readable portrait Short.

## External research and its limits

**A surprise needs an understandable setup.** BBC Maestro's comedy-writing guidance describes conflict and an expectation-changing resolution. It recommends beginning with the punchline, constructing its setup, adding smaller jokes where useful, removing unnecessary material, and testing the result on people. Applied here: decide what the final message newly reveals, then plant only the information required to understand it. A closer crop cannot repair a redundant ending. [BBC Maestro: How to write a joke](https://www.bbcmaestro.com/blog/how-to-write-a-joke).

**A broken expectation alone is insufficient.** McGraw and Warren's original 2010 study tested moral violations across five experiments. Their account links amusement to a violation that is also perceived as benign; psychological distance and alternative norms can affect that appraisal. Applied here: familiar low-stakes friction, outsized confidence and self-inflicted embarrassment are useful starting points. A genuinely distressing consequence can change the scene from playful to unpleasant. The study does not establish a recipe for chat-video success or guarantee the same reaction across audiences. [McGraw and Warren, Benign Violations: Making Immoral Behavior Funny](https://leeds-faculty.colorado.edu/mcgrawp/pdf/mcgraw.warren.inpress.pdf).

**Pattern can make a turn legible.** In his own course notes, David Walliams describes two examples that establish an expectation and a third that surprises. This is a craft option, not a mandatory three-message formula or an empirical rule for retention. A short chat can establish a pattern in two compact exchanges, then change the category on the next attempt. Avoid three identical threats with bigger numbers. [David Walliams, BBC Maestro course notes, “Finding the Funny,” printed page 39](https://assets.cdn.bbcmaestro.com/david-walliams-lesson-0-notes.pdf?version=1697111682).

The production recipes below are our adaptation of these sources and the sampled reference. Their effectiveness needs actual viewer/editor feedback; neither citations nor schema compliance make a script funny.

## The writing recipe

1. **Choose a small, specific desire.** Somebody wants a delivery, a quiet room, a refund, a game win, a borrowed object, or a favor. Give the other person a competing priority. Two participants are usually enough. Their different reactions establish character without biographies.
2. **Choose one comic mechanism and a final turn.** Identify what the audience is likely to assume, and what the final message will make them reinterpret. The payoff should be surprising but caused by earlier information. Do not rely on a random third person, secret superpower, or new object arriving in the last line.
3. **Open inside the problem.** The first visible message can contain a concrete contradiction, surprising action, specific desire or another natural source of curiosity appropriate to this story. It creates a clear question the chat can answer. Avoid greetings, a title card, generic danger, “you won't believe this,” or concealing so much that the premise is incomprehensible.
4. **Plant a fair clue early.** A detail in the first few messages should serve an immediate conversational purpose and become relevant again at the payoff. The hook's question must be resolved, even when the ending adds another implication.
5. **Escalate through different consequences.** Each exchange changes the situation: a new condition, a mistaken interpretation, an attempted fix that worsens the original problem, or evidence that changes who has leverage. Cut an exchange if deleting it changes nothing.
6. **Let reactions breathe.** Small replies can be the comic contrast to the other person's confidence. Every line need not be a joke. Avoid padded reaction loops and repeated “are you serious?” exchanges. Include at least two smaller turns before the final payoff when the premise supports them.
7. **Put the decisive information last.** The final message resolves the planted question while adding a new implication, consequence or interpretation. End there. No recap, moral, audience question, explanation, or extra reaction that repeats what just happened.
8. **Read as a real chat.** Prefer contractions, fragments, concrete words and one intention per message. Do not distribute essay sentences between two speakers. Slang and emojis should fit the person and the moment; adding “bro” or a skull emoji does not create a punchline.

Within the current v2 contract, use 12–22 messages and 40–100 total words, usually 2–7 words each, never more than 12 words in a message. There are 2–3 participants and no narrator. The same exact text goes in the message and onscreen fields. These are application constraints; the current creation guide is authoritative if the contract changes.

## Vary the mechanism between videos

| Mechanism | Useful engine | Common failure |
| --- | --- | --- |
| Literal interpretation | A normal request is interpreted exactly, with a logically connected absurd consequence. | A pun that the chat spends four messages explaining. |
| Conflicting priorities | Each person solves a different problem while believing they agree. | Characters deliberately refusing to understand a plain sentence. |
| Wrong metric | A character optimizes the visible score while defeating the real goal. | Arbitrary numbers with no change in consequence. |
| Escalating commitment | An attempted fix commits the character further to the original mistake. | Repeating the mistake without a new cost. |
| Callback with changed meaning | An early ordinary detail becomes decisive under a second interpretation. | Introducing the crucial fact only at the end. |
| Self-own/status change | A confident claim exposes the claimant through planted evidence. | The familiar “your rule also applies to you” ending with no additional turn. |

A default brief of “a petty household rule backfires” repeatedly selects the last mechanism and makes the ending easy to predict. Broaden the brief to an ordinary goal, two conflicting priorities, a suspicious first message and a planted payoff. These are writing choices, not a requirement to add a model selector or extra API calls.

## Why the previous dishwasher example feels weak

The premise announces a punishment, the other person applies it to the rule-maker's mug, and the final message repeats the already disclosed donation. The viewer can predict the reversal well before the ending. Several replies express disbelief or explain the rule without changing the situation. Formal declarations also sound written for the audience instead of sent to a roommate.

The remedy is not more camera motion or a stronger sound sting. Change the comic mechanism or give the reversal a second, planted implication; cut duplicate reactions; make the final message the first delivery of decisive information. Preserve Gemini authorship by improving the brief and regenerating, not silently rewriting the accepted output by hand.

## A compact brief for the script-only writer

This block is recommended prompt content. Adapt it to the existing JSON schema; it does not add fields, a director, model review stages, or extra writing calls.

> Write an original chat comedy for two people with conflicting ordinary priorities. The FIRST actual message should create a specific curiosity naturally, through a surprise, contradiction, desire or unresolved situation as appropriate; no greeting, title or generic warning. Plant a fair clue in the opening exchanges. Use one clear comic mechanism; vary it beyond a household rule turning on its maker. Every exchange must change the situation, evidence or leverage. Include smaller unexpected turns on the way to the ending. Use casual short messages with distinct reactions, not explanatory speeches or repeated disbelief. Choose the final payoff before constructing its setup: the LAST message must answer the opening question and add a surprising but causally planted interpretation or consequence. It must not repeat an earlier reveal, explain the joke, add a moral or ask the audience a question. No arbitrary new character/object in the ending. Return only the existing script JSON; software supplies all timing, camera, UI and sound. Follow the supplied message/word/speaker limits.

The model should output only the requested artifact. A long visible rationale, self-awarded humor score or assertion that the ending is “hilarious” supplies no useful evidence.

## Editorial review before calling an example good

- Can a viewer understand the first message and state the specific unanswered question?
- Does the ending answer that question using information planted earlier?
- Does the last message add information? If removing it changes nothing, it is a recap.
- Is the main ending already obvious halfway through? If so, add a different earned implication or choose another mechanism.
- Can each middle exchange be described as a different change rather than another reaction to the same claim?
- Can the two speakers be distinguished by wants and reactions without relying on their names?
- Is the absurdity coherent under the character's logic, and playful enough for the intended audience?
- Does the raw text produce an amusing turn before effects are added? Can a person read it comfortably at the rendered pace?

These are human editorial questions. Automated checks can enforce counts, role consistency and exact text identity; they cannot certify surprise, naturalness or amusement. Keep a technically ready video labeled as a demonstration until the owner has approved its writing and presentation.

## Editing serves the conversation

Reveal messages in order and preserve enough recent context to read the response. Keep a stable app identity and speaker identity. Use a brief emphasis or gentle zoom on the message that changes meaning; restore the context afterward. Do not have every message bounce, zoom or flash. Hold the setup long enough to read, allow a small gap before the final reveal, and leave the payoff readable before ending. Avoid arbitrary numerical timing claims: use the existing reading-time compiler and inspect the actual render.

Use restrained soft entry/send cues and an occasional distinct payoff cue; a cue on every letter or an equally loud ping for every message becomes clutter. The editor determines these choices locally. Gemini supplies conversation text, not camera directions, effect labels, stage directions or sound commands.

The latest UI and sound implementation should be checked in the root guide and server-chat guide. This playbook does not assert that an app skin, softer sound design or a specific zoom behavior has already shipped.
