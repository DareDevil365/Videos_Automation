# Stronger chat writing: implementation and evidence

Updated 5 November 2026. This changes the program's writing workflow; it does not certify that a model is funny or that the owner will like a video.

## What failed

The dishwasher script disclosed the donation early and then repeated it. The key-search comedy cycled through locations and introduced a toaster late, without an earned comic mechanism. The coach/key thriller named its sender but did not explain his threatening behavior. Another draft invented SMS control over an electrical gate. A favorable broad model verdict missed these problems.

Code inspection also found actual prompt conflicts: chat writing inherited generic stock-search/visual-query instructions, narration-oriented guidance and unrelated hook-selection descriptions. The old revision call omitted the original creative brief and format rules. A twelve-message minimum encouraged padding even when the idea needed fewer exchanges.

## What changed

New `chat-plan` / `phone-plan` requests select **`chat_writing_version: 2`**. Existing requests without that field keep version 1. Both use the local chat editor; this writing version does not restore a model director.

1. **Develop the ending before the dialogue.** One writing request returns three compact story sketches, selects one, and writes its conversation. Sketches record the situation, competing wants, opening, early plant, ending, cause and mechanism. Software checks that the selected opening/ending and early plant actually appear. This is writer selection, not an independent quality vote. No three full scripts or extra concept-selection call is required.
2. **Use a focused chat brief.** The new writer receives the topic, genre, owner constraints/feedback, message/word/time bounds and supported story contract. It receives no stock-search, narration, music, camera or generic visual-brief tasks. Private contact/thread/time/occurrence fields remain story data, not editing instructions.
3. **Use fewer messages when appropriate.** Normal chat allows 8-20 messages, 35-105 words and 12-55 seconds. Phone stories allow 10-26 messages, 50-145 words and 18-90 seconds. The existing three-word counting tolerance remains. Complete reading holds and at most twelve words per message are retained. Old saved version-1 bounds remain unchanged.
4. **Read the actual conversation without the writer's pitch.** A fresh text request sees messages and necessary private-thread context, but no title, claimed hook/payoff, self-explanation or favorable prior verdict. It reconstructs the viewer's question/answer and missing assumptions. All seven criteria—opening, cause, knowledge, progression, voice, payoff and genre—require an explicit judgment and a real quoted message. Missing assumptions or substantive failure block acceptance. A repeated final message is also detected locally.
5. **Revise the cause, not just the wording.** One revision receives the original owner brief, bounds, genre and concrete critique. It may rebuild a broken premise. The new text gets the same cold-reader check; another failure holds the job. Development records mark changed anchors as rebuilt rather than pretending the old sketch still describes the ending.

At most five writing operations are available in a completed pass: draft/development, one structural repair, reading critique, one revision and one recheck. Project failover/network resumption can create additional counted HTTP attempts. A malformed development envelope cannot silently bypass sketch planning. Provided scripts remain explicitly provided, and do not make these writing requests.

## Genre choices

Comedy needs a coherent mechanism, distinct wants and changing consequences; random absurdity or repeated disbelief is insufficient. Mystery needs a fair planted explanation and plausible character knowledge/motivation. A gentle `story` needs an earned emotional choice and fulfillment; it should not be forced into a danger hook or surprise punchline. The opening may create curiosity, surprise or anticipation naturally, without one compulsory first-line formula.

The [humor playbook](../research/formats/entertainment/CHAT_HUMOR_PLAYBOOK.md) supplies the craft background and reference observations. Our application choices are hypotheses for this format, not research-established retention rules. The original [Self-Refine paper](https://arxiv.org/abs/2303.17651) supports testing feedback/revision as an approach across its evaluated tasks, not a guarantee for these videos. [MT-Bench's judge study](https://arxiv.org/abs/2306.05685) documents judge limitations and biases; a separate request from the same provider remains a model opinion, not an independent human verdict. Removing metadata reduces one source of priming but cannot eliminate self-preference or reasoning errors.

## Tests versus creative evidence

Fixtures verify focused prompt routing, exact sketch anchors, all seven criteria, invented-quote refusal, missing-assumption/repeated-ending rejection, original-brief preservation and bounded revision. They establish software behavior, not semantic judgment accuracy. No live Gemini writing comparison was run in this pass: the owner explicitly requested assistant authorship for the five new videos.

The [five original scripts](../examples/assistant-five/README.md) demonstrate the intended craft choices through assistant-authored examples. Their local exports use the normal toolbox with a closed provider that refuses remote generation. They are not relabeled Gemini successes or owner-approved content. The remaining evaluation task is a blinded live comparison on held-out stories and eventual owner/audience feedback; reliable excellent unattended model writing remains unproved.

Validation: 295 tests passed in the full suite, followed by 24 affected tests after final changes. Actual five-video output hashes and saved inputs verify; sample inspection led to real presentation fixes. These checks establish the toolbox and data flow. The new API writing route was exercised with closed fixtures only, honoring the owner's assistant-authorship instruction for this pass.
