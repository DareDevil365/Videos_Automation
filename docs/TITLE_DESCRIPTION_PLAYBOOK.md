# Titles and descriptions that earn the click

Researched 5 November 2026. Optimize for the right viewer understanding and enjoying the actual video. There is no verified magic sentence that makes unrelated videos receive more reach. YouTube describes recommendation performance in terms of viewer choice, watch duration/percentage and satisfaction, alongside personalization and competition. Metadata contributes to search relevance; it cannot substitute for the video delivering its promise. See [YouTube discovery guidance](https://support.google.com/youtube/answer/11914225?co=YOUTUBE._YTVideoType%3Dshorts&hl=en) and [performance FAQ](https://support.google.com/youtube/answer/141805?hl=en).

## Title choices

Start from the strongest honest question or change in the finished script. Offer three distinct angles and choose one for the intended audience. A searchable title names the topic plainly; a curiosity title establishes a specific unresolved situation; an emotional title makes a recognizable human stake clear. This is an editorial choice, not three experimentally proven winners. Put the useful words early, keep the wording readable on mobile, and avoid stuffing creator names, capitalization or repeated punctuation. The API hard limit is 100 characters; a shorter useful title is usually easier to scan, but this is not a fixed optimal length. [YouTube's title tips](https://support.google.com/youtube/answer/12340300?hl=en) distinguish searchable from intriguing titles and recommend checking subsequent Analytics.

| Genre | Useful promise | Example grounded in our script | Avoid |
| --- | --- | --- | --- |
| Chat comedy | Specific social mistake with a consequence | I Added My Boss to the Wrong Group Chat | Funniest Video Ever; revealing every punchline |
| Mystery | Contradiction the story explains | Someone Had My Daughter's Bag. It Wasn't at the Bus Stop. | Fake true-crime framing or a mystery without an answer |
| Emotional chat | A concrete ritual with an unresolved meaning | Dad Kept Buying Two Coffees. I Finally Understood Why. | Unsupported tragedy or a generic motivational claim |
| Cinematic fable | A human act that opens a question | He Painted a Window for a Boy Who Couldn't Go Outside | Calling fictional events a true biography |
| Aura | The supported action/attitude contrast | Let the Shot Answer | Invented achievements, scores or quotes attributed to stock athletes |
| Factual explainer | A real supported question/benefit | How a Footstep Can Generate Electricity | Adding Japan/footstep copy to an unrelated comedy |

The electricity example is a legitimate subject when the video actually explains it with sources. It is not a reusable description for every genre. Do not borrow another successful video's unrelated premise or infer causation from its views. YouTube's [spam/metadata guidance](https://support.google.com/youtube/answer/2801973?hl=en) prohibits misleading manipulation.

## Description construction

The opening one to three sentences describe THIS video's situation and stakes. Use one or two natural subject phrases rather than a keyword wall; keep fiction legible as fiction. Preserve a payoff when that supports the story's viewing experience. Add useful source links, required full music/media credits and appropriate disclosures after the viewer-facing premise. Use hashtags only when relevant; the current automated metadata writer adds none by default. No unrelated trend paragraphs, fake awards, fake testimonials, promises of views or artificial engagement requests.

For The Second Coffee: “Leah thinks she knows why her dad still orders two coffees. A message from the station cafe makes her change her journey home.” This describes the actual plot without explaining the emotional ending. Software adds the licensed soundtrack credit and fictional-content disclosure separately. [YouTube's description guidance](https://support.google.com/youtube/answer/12948449?hl=en) recommends unique descriptions, useful opening lines, and one/two relevant main terms.

## What the program does

`publication_metadata.py` supplies the complete frozen script and genre to one structured packaging call. It requires three different titles, a selected index, a bounded plain-language description, one/two subject phrases, a selection reason and exact quoted script evidence. Invalid evidence, duplicate/oversized titles, bad indices and malformed fields hold. `quality.package` appends deduplicated mandatory credits/sources/disclosure and refuses an oversized full description rather than cutting off a license. Provided packaging uses the same contract with honest `provided` origin; [our three examples](../examples/assistant-five/publication) accompany the revised chat exports. Existing jobs keep their original metadata behavior unless `metadata_version: 2` is requested.

Exact quotes establish traceability, not semantic proof that every title claim follows. The model can still make a poor creative/semantic choice; live quality and audience validation remain open. There is no hidden trending-topic copier or score claiming predicted reach.

## Learn from actual results

Save title/description versions with the job and compare similar genre/length/channel/time cohorts. For Shorts, examine whether people choose to watch, retention/completion and watch time; use available search terms/traffic sources and engagement as context. Do not optimize click-through alone while people leave disappointed. The existing observation/benchmark modules can supply account-authorized measurements once connected. A public view-count comparison is observational; changing a title is not a controlled proof that the title caused a gain. At present this account has no collected channel outcome dataset, so the program must not claim it already knows which title is a winner.
