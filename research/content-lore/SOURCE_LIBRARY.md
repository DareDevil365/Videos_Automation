# Reusable comic story sources

Use [source-library.json](source-library.json) before starting topic discovery again. It contains **14 reading/source routes and 17 story records**. Eleven records reuse reviewed project evidence; six are reading leads whose full causal story has not yet been extracted. The research agent hit its usage limit; the main assistant completed this library. This is a source index and a cache of bounded facts, not an archive of copied narration or complete copyrighted issues.

```powershell
.venv\Scripts\python.exe tools/query_comic_library.py doom --ready-only
.venv\Scripts\python.exe tools/query_comic_library.py "Spider Man"
.venv\Scripts\python.exe tools/query_comic_library.py
```

The lookup checks each saved packet against its provided source-review hash. `reviewed_claim_scope` means those facts have a recorded review. It does not mean the earlier video's writing was accepted or that every scene in the comic was read. Changed packets are labeled `review_needed`. Reading leads remain `discovery_only`.

## Where to find material

| Route | Useful material | Boundary |
| --- | --- | --- |
| [Marvel official guides](https://www.marvel.com/comics/guides) and character histories | Arcs, roles, verified events and issue references | Marketing blurbs often omit the decisive choice or ending. |
| [Marvel's free-issue collection](https://www.marvel.com/comics/guides/2421/free_issues) | Selected publisher-offered issues | Verify what is actually free and readable. |
| [Marvel reading-service help](https://help.marvel.com/article/marvel-whats-happening-to-marvel-unlimited) | Current account/app access | November 2026 search results describe a service transition. Recheck the current reader and terms before recommending a subscription. |
| [DC editorial explainers](https://www.dc.com/blog/2016/02/08/the-dctv-secrets-of-supergirl-ep-13-for-the-girl-who-has-everything) and [official timelines](https://www.dc.com/blog/2025-09-24/a-complete-timeline-of-the-new-history-of-the-dc-universe) | Context, story connections and exact issues | Bibliographic copy can conflict. Verify the issue and continuity. |
| [DC Universe Infinite information](https://www.dc.com/blog/2021/01/21/welcome-to-dc-universe-infinite) | Licensed full-reading route | Subscription, catalog and territory conditions need a current check. |
| [Hellboy publisher timeline](https://images.darkhorse.com/darkhorse/index_images/blog/hellboy_timeline.pdf) and [Dark Horse Digital](https://digital.darkhorse.com/) | Chronology and official issue/preview routes | Timeline entries do not supply every motive. Main publisher pages blocked this browser; full reading was not claimed. |
| [Image first-issue readers](https://imagecomics.com/comics/read-first-issues) | Publisher-hosted openings, including [Invincible #1](https://imagecomics.com/comics/releases/invincible-1) | A free opening does not verify a later plot twist. |
| [Radiant Black publisher recap](https://imagecomics.com/comics/releases/radiant-black-the-story-so-far) | A focused recap starting point | Read the exact scene when the recap skips a causal link. |
| [Comic Book Plus](https://comicbookplus.com/?cbplus=about) and [Digital Comic Museum](https://digitalcomicmuseum.com/) | Complete stories in public-domain-oriented archives | Check the specific issue, jurisdiction and rights. A free download does not establish worldwide reuse permission. |
| [Grand Comics Database](https://www.comics.org/) | Credits, editions and issue bibliography | It is a volunteer index, not a complete story source. |
| Creator interviews and accessible transcripts | Why a scene works and precise event order | Separate creator interpretation, third-party transcription and the actual issue/episode. Write original narration. |

## Reuse a story without researching everything again

1. Search the library for the character or premise. Keep the exact run, year and issue range. WandaVision is a television record, not a comic record.
2. Reuse reviewed claims and their source IDs when they cover the intended story. Do not use the old short script as the factual source or a style template.
3. Write a causal ledger: protagonist's want, opposing pressure, consequential choice, action and resulting state. Explain why each beat leads to the next. A sequence of teaser blurbs is insufficient.
4. If a connection is missing, read that specific scene once and add a bounded, attributed claim. Record uncertainty rather than inventing motives. A bibliography can locate the issue; it cannot supply the missing decision.
5. Write a new original script from the ledger. Keep necessary transitions, not just plot highlights. Identify the actual publication/episode near the opening and show matching cover/artwork when available.
6. Save the new brief, review hashes and cover provenance. The next episode can use that updated packet offline.

Refresh changing reading-service access, releases, URLs, licensing and uncached decisive details. Stable already-reviewed plot facts do not need a fresh broad web search for every video.

## Starter coverage

Reviewed project packets cover the Spider-Man machinery rescue, WandaVision's identity exchange, Beta Ray Bill, Doom/Strange's rescue, Hellboy's refusal and Secret Wars (2015). The remaining leads cover Superman's Black Mercy story, Mister Miracle (2017), Invincible #1, Radiant Black's recap, Seed of Destruction and a Golden Age mystery selection. Their JSON states what is known and what still needs reading. None implies that every Marvel or DC story is ready to script.

For “For the Man Who Has Everything,” preserve **Superman Annual #11** and resolve year/collection metadata before an exact bibliographic announcement. The research found inconsistent publisher wording. This is why publisher status alone does not remove the need to check a specific conflicting fact.


The latest reviewed packet adds Kraven’s Last Hunt (1987): burial, impersonation, emergence, the final test and consequence. Its [selection review](../../examples/lore-series/kraven-last-hunt/SELECTION_REVIEW.md) separates why the story was chosen from the factual claim review.


The offline lookup accepts an exact reviewed hash or a hash differing only by LF/CRLF line endings after a Git checkout, and records `packet_hash_match`. Changed fact text still requires a new review. Immutable production-plan input hashes remain exact; this portability allowance applies only to the reading cache.


The ensemble batch adds the original 2012 Deadpool creator/reader story, the original 1975 Krakoa rescue, and the two 2024/2025 movie recap packets. Film and comic records are labeled separately. Reuse their bounded source facts without conflating variants, later retcons or adaptations. The actual narration and sampled exports remain separate creative work.
