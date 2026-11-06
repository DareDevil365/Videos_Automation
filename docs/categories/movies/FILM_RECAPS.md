# Film and episode recaps

Start with an interesting conflict and a specific ending, then check the original continuity. A film, comic and alternate-universe episode are different sources. Name the actual source early and show its identifying cover/poster during narration. Record whether evidence was watched directly or read in a cited recap; do not imply full viewing from a synopsis.

For a whole-film request, make a coverage table before compressing the writing. Track the inciting incident, each faction's reason, causal bridges, iconic actions, deception, late revelation, confrontation and consequences. Preserve the film's order of discovery: Civil War's parents recording belongs in the final act, after the Siberian trap, rather than in the opening hook. Compression can remove secondary exchanges; disclose that a short recap cannot reproduce every detail of a feature film. Never remove the cause that makes the next decision intelligible.

Measure complete local speech before setting the runtime. The current platform guidance allows qualifying vertical/square Shorts up to three minutes ([YouTube Help](https://support.google.com/youtube/answer/15424877), checked November 2026). The supplied Civil War recipe explicitly uses a 75–115 second window to retain the main story; Doctor Strange uses 45–60. This is an authored exception to the shorter standalone comic target, not permission to pad speech with silence. Recheck platform rules before future publication.

## Direct the actual words

One complete narrated unit can contain several shots. Use `lore_cuts` in the series part, keyed by unit ID. Each row declares `on`, `kind`, `camera`, and `reason`. The first row has an empty `on` and the unit's base scene kind. Later anchors must occur once, in order, in that unit's exact words. The current renderer accepts two to six cuts and rejects shots shorter than half a second. Final timing comes from aligned audio words; only draft storyboards use proportional estimates.

Choose a shot because it explains the current verb, changes the situation or makes a consequence visible. Use an anchored rig for contact, scale and material change; a checked image for source identification or exact likeness. Keep costume and injury continuity. Change setting, angle and scale between distinct events rather than repeating a throne or portrait. Use the existing [art direction](../comic-lore/ART_DIRECTION.md) and [representation decisions](../comic-lore/VISUAL_DECISIONS.md). Lower audience framing remains required for these recipes and does not add those spectators to story continuity.

Choose music from the installed catalog by the story's emotional direction, not genre tags alone. A happy ending track is unsuitable under Civil War's escalating rupture. Record the exact track, credit and reason. Mix under narration and verify the final export. Technical QA and an assistant's fit judgment do not establish audience retention.

## Endings and calls to action

The latest owner request restores a short spoken and visible subscription request. Finish the consequence or cliffhanger first, then say “For more stories like this, subscribe.” Put an `end_subscribe` cut on that phrase and set `edit.cta: true`. Do not insert a CTA over the revelation or invent an unavailable next-part link. Older examples with `edit.cta: false` document an earlier preference; they do not override the current request. Changed exports get a new build ID so previous review copies remain available.

Inspect actual exported frames for every cut, the source poster, lower audience, captions, action contact and the final CTA. Check actual duration, narration gaps, package hashes and provider-call history. Save the script, coverage table, exact decisions, source review, metadata, credits and local review beside the production record. Follow the separate publishing workflow only when the channel and authorization are ready.

Worked recipes: [Civil War](../../../examples/screen-recaps/civil-war-complete/README.md) and [Doctor Strange](../../../examples/screen-recaps/strange-supreme-heart/README.md).

`tools/review_lore_export.py Resources/Productions/<build>/part-1` verifies completed package hashes, reconstructs cuts from aligned speech, samples each cut from the exported MP4, checks the closing subscribe anchor and measures narration silence. Inspect its contact sheet before replacing the pending visual-inspection note with actual observations. It does not listen for acting quality or certify creative success.
