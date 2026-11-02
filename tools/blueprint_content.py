# Reader-facing content for build_blueprint_pdf.py. Snapshot: 02 Nov 2026.
start('YouTube automation', 'A DETAILED SYSTEM BLUEPRINT')
Y-=14
text('<b>From research to finished Shorts, publishing and learning.</b>',ParagraphStyle('hero',parent=STYLE,fontSize=24,leading=31),18)
text('Two channels. Several creative formats. One reusable production system.',ParagraphStyle('deck',parent=STYLE,fontSize=15,leading=22),18)
flow([('Discover','Topics, sources and public references','ai'),('Create','Original scripts, voice and visual plans','ai'),('Produce','Assets, timed layouts and MP4 export','code'),('Check','Evidence, media quality and feedback','code'),('Publish','Account-bound upload and scheduling','code'),('Learn','Owned results and new experiments','ai')], 'Purple boxes indicate model-assisted creative work. Other boxes are mostly conventional software.',3)
text('This document explains the intended product and the current implementation separately. It is a practical build and operating guide, not a claim that every route is already live.',gap=14)
callout('CURRENT POSITION','The local research-to-export path has produced real videos. The latest voice was accepted; its script and repeating visuals were rejected. Real Google browser generation and real YouTube publishing remain unverified. The latest full test run passed 78 tests.')
text('Prepared from the repository, prototype records and the latest owner feedback. Technical validation was run on 01 Nov 2026; this document includes the adjustable generation-settings request received on 02 Nov 2026.',SMALL)

start('How to read this plan')
text('The goal is to operate channels through software, with AI doing creative assistance and deterministic code handling timing, files, validation and side effects. The system should assemble videos without the owner editing a timeline by hand.')
sub('The important distinction')
text('A video that exports successfully can still be boring, inaccurate, poorly matched visually, unsuitable for advertising or ineligible for monetization. A successful unit test proves a particular software behavior, not audience demand or platform approval.')
table(['Status','Meaning in this report'],[
('VERIFIED LOCALLY','A real local model, actual media or an actual FFmpeg render was used.'),
('TESTED WITH FIXTURES','An automated test used controlled inputs or a local imitation of an external service.'),
('CODE PRESENT','The adapter or format exists, but its full real-world route has not been demonstrated.'),
('SETUP BLOCKED','An account connection, permission, provider selector or input asset is missing.'),
('PLANNED / REFINE','A required behavior is missing or the current creative result was rejected.')],[1,3])
sub('Three different meanings of script')
text('<b>Video script:</b> the words, hook, payoff and scene intentions in script.json.<br/><b>Automation code:</b> Python modules that run research, downloads, speech, editing and monitoring.<br/><b>Edit recipe:</b> a JSON description of real assets, cuts, positions and audio. FFmpeg executes that recipe; it does not interpret a vague creative prompt.')
callout('WHAT AN AGENT MEANS HERE','An agent is a named responsibility in one Python application, backed by stored jobs and files. We are not deploying a separate independent AI employee for every role. Some roles use Gemini; others are ordinary code.')

start('Document map')
table(['Pages','What they explain'],[
('4-5','Channel strategy and the overall architecture'),('6-7','Roles, AI use and three end-to-end production routes'),('8-9','Google browser generation, direct pages and adjustable settings'),('10-12','Education, entertainment and generated-video formats'),('13-14','Hooks, scripts and matching each visual to a spoken beat'),('15-17','Acquisition, permissions, voice and transcripts'),('18-20','Editor layouts, music, quality checks and prototype evidence'),('21-23','Publishing, supervision and the growth officer'),('24-26','Free-tier operation, revenue and capability limits'),('27-29','Build status, completion order and operating runbook'),('30-31','References, glossary and finished-pilot criteria')],[1,4])
sub('Decisions retained')
text('Use the lightweight FFmpeg compositor rather than require Premiere, After Effects or Resolve. Use local speech to avoid a paid voice API. Keep inspectable JSON checkpoints and SQLite state so failed jobs can resume. Use public or explicitly permitted media rather than treat any available download as licensed.')
sub('Decisions still to prove')
text('Which content pillar holds attention; whether the chosen Google account exposes the expected generation model and included allowance; which permitted creator catalogue is usable; whether the first real upload and Analytics connection work; and which creative changes improve the channel.')
text('The supplied Google page links remove navigation steps. They do not select all sidebar settings, prove the signed-in identity or establish the cost of a generation.',SMALL)

start('The channels we are building')
table(['Channel','Audience promise','Starting approach'],[
('Entertainment','Fast, understandable entertainment with a clear joke, reveal, reaction or visual payoff.','Test a few coherent series first: original chat/storytime, aura edits with permitted media, and short visual payoff loops.'),
('Education / productivity','One useful, believable takeaway viewers can try or understand immediately.','Study/confidence, job-search skills, useful AI demonstrations, practical earning skills and accessible knowledge.')],[1,2,2])
text('The operation is based in India. English content can aim at US viewers, but reach is earned through subject choice, examples, language, timing and audience response. An account setting cannot guarantee US distribution or higher earnings.')
sub('The current creative brief')
text('Use the accepted fast, clear Kokoro male voice. Keep captions smaller. Use relevant footage and frequent meaningful changes in fast educational or aura formats. A small top text strip with two visual blocks is one selected layout, not a compulsory layout for every story.')
text('For fast explained Shorts, a visual change roughly every two to three seconds is a starting hypothesis. ASMR, source dialogue and a satisfying reveal may need longer uninterrupted shots. Pacing should support understanding and payoff rather than become random motion.')
sub('What we are stopping')
text('Do not make another generic procrastination remake or a specialist Python lecture as the next audience prototype. Do not cycle unrelated stock images to fill time. Study successful creators without copying their script, unsupported earnings promise or personal footage without permission.')
callout('NEXT CONTENT DECISION','Research actual references in the agreed niche, write a new original hook and short script, then review the sentence-to-visual storyboard before spending generation allowance or rendering the next prototype.')

start('The overall architecture')
flow([('Input brief','Channel, format, topic and constraints','code'),('Research','Dated sources, trends and claims','ai'),('Write','Hook, units, payoff and metadata','ai'),('Acquire','Stock, owner files, permitted clips or generation','code'),('Speak + time','TTS or original source audio','code'),('Direct','Concrete assets and edit JSON','code'),('Render','Crop, cuts, captions and sound','code'),('Check + package','Technical and evidence gates','code'),('Publish + learn','Separate upload, monitoring and experiments','code')], 'Read the numbered nodes in order. Production stages are research -> script -> voice -> visuals -> direct -> render -> quality -> package. Source and generation tasks can supply assets before, or pause, this route.',3)
sub('Why the split matters')
text('Gemini proposes content. Python enforces structure and permitted inputs. FFmpeg produces exact frames and sound. SQLite tracks queued, running, waiting, held, ready and upload states. The model never gets to execute arbitrary code or publish a guessed file path.')
text('A single production worker uses a renewable lease. Each stage writes an artifact and input hash. If voice or source changes, affected outputs must be rebuilt rather than silently reusing an old render. Provider quota can pause the queue without losing completed stages.')
callout('READY IS NOT PUBLISHED','Ready means the local package passed implemented gates. Publishing is a separate, account-bound action. It is currently disabled and no live owner-channel upload has been verified.')

start('Who does what, and where AI fits')
table(['Role','AI work','Code / important modules'],[
('Researcher','Extract topics and source-linked claims; rank possible angles.','research.py / net.py fetch RSS, HTML and public text; store excerpts and dates.'),
('Growth officer','Assist interpretation and propose creative experiments.','benchmarks.py / monitor.py collect allowed metrics and compare cohorts.'),
('Scripter','Produce original hook, words, payoff, captions and metadata as JSON.','writer.py / contracts.py validate schema, references, duplicates and review results.'),
('Media researcher','Propose visual queries or choose a transcript moment.','media_agent.py, source_agent.py and clip_agent.py enforce source and range rules.'),
('Voice performer','Neural speech generation on the local CPU.','voice.py runs Kokoro/Piper, caches lines and measures durations.'),
('Director / editor','Creative intent can come from the model. Semantic storyboarding needs refinement.','director.py / visuals.py / montage.py resolve files; shorts_editor executes layouts.'),
('Generation worker','An image/video model creates a scene from a prompt.','browser_agent.py drives configured controls and imports a download.'),
('Publisher / supervisor','No AI needed to upload bytes or detect a missing file.','publishing.py handles OAuth/sessions; monitor.py handles alerts and checkpoints.')],[1,1.65,2.25])
text('AI evidence review is a second model pass, not an independent guarantee of truth. Public competitor statistics cannot reveal retention, actual revenue, audience geography or private strategy. Missing data must remain unknown instead of becoming an invented number.',SMALL)

start('Three production routes')
sub('A. Narrated education, story or original chat')
flow([('Brief + sources','Original idea with supported facts','ai'),('Script + voice','Words, timing and scene needs','ai'),('Assets + edit','Match units, compose and package','code')], '',3)
text('TTS gives measured unit durations. Captions and layouts follow those timings. Original chat is labelled fiction. Factual education requires evidence. This route has produced real local prototypes; latest script/visual quality still needs improvement.')
sub('B. A permitted source clip')
flow([('Register source','Permission, exact work and episode','code'),('Transcript','Import subtitles or run local ASR','code'),('Select + clip','Valid cue range, context and captions','ai')], '',3)
text('A research lead is not a timestamp. Map it to an approved catalogue item, inspect actual cues and select an in-range segment. Python clips the file, preserves source speech and optionally adds gameplay/music. Do not guess a famous scene or download an arbitrary show.')
sub('C. A generated visual or standalone loop')
flow([('Shot request','Purpose and required duration','ai'),('Browser generation','Verify model/settings/allowance','code'),('Download + use','Register, trim and compose','code')], '',3)
text('An image can fill a storyboard unit; a generated video can become a clip or loop. These adapters exist, but real AI Studio generation and download in the requested Brave session remain unverified. A local browser fixture has been tested.')

start('Google generation: direct-page flow')
text('The owner supplied direct AI Studio image and chat pages. The worker should navigate straight to the appropriate target. It does not need a complicated search through Google menus.')
flow([('Open target','Configured direct URL in Brave','code'),('Check session','Provider origin, model and controls','code'),('Set sidebar','Duration, size, ratio and thinking','code'),('Verify cost','Included allowance and job limit','code'),('Submit once','Save intent before Generate','code'),('Download','Inspect, hash and register result','code')], 'After an interrupted download, reconcile the submitted result. Do not automatically spend allowance again with a second Generate click.',3)
sub('What is already written')
text('browser_agent.py stores jobs, supports explicit selectors, checks origin/model/allowance/cost, prevents blind resubmission, waits for downloads and registers results. A CLI can attach completed generation to production. A local mock exercised submission and file download.')
sub('What the real page still needs')
text('The adapter currently launches its own persistent Chromium profile. Reuse of the already signed-in Brave session is not implemented and verified. Real prompt, sidebar and download selectors need calibration. Setting actions and per-shot profiles are not implemented yet. The strict credit-label parser may need adaptation to the actual page.')
text('<b>Image target:</b><br/><link href="https://aistudio.google.com/prompts/new_chat?model=gemini-3.1-flash-image" color="#ac4d2c">aistudio.google.com/prompts/new_chat?model=gemini-3.1-flash-image</link><br/><b>Video target supplied:</b><br/><link href="https://aistudio.google.com/u/5/prompts/new_chat" color="#ac4d2c">aistudio.google.com/u/5/prompts/new_chat</link>',SMALL)
callout('VERIFY THE ACTUAL MODEL','The second URL is generic new-chat and does not encode a video model. The owner calls the intended option Omni 1.1 Flash. Read the selected model and confirm downloadable video capability. An account-indexed URL is not a durable identity check.')

start('Generation settings follow the shot')
text('The screenshots demonstrate controls, not fixed presets. Duration, resolution and thinking should change with the requirement. Avoid 4K images or long videos when they add no visible value. These are planned worker refinements, not already-verified live behavior.')
table(['Control','Selection rule to implement'],[
('Aspect ratio','Prefer 9:16 for a full-frame vertical shot. For a panel, choose a supported ratio that preserves the subject after cropping.'),
('Video duration','Use the shortest supported length covering the intended 2-, 3- or 5-second edit plus a small margin. If unavailable, generate the provider minimum and trim.'),
('Image resolution','Choose for the actual panel and planned zoom. Start with the lowest adequate supported size; use 4K only when crop/detail needs justify it.'),
('Video resolution','Match export and panel needs. Compare supported costs; avoid buying detail the final composition discards.'),
('Thinking level','Use a lower available level for a simple literal shot; increase when scene/prompt complexity demonstrably benefits. Verify model support.'),
('Search / grounding','Leave optional tools off unless needed and their allowance/cost is understood. Do not silently enable paid features.'),
('Frame rate / temperature','Record the supported value. A disabled 24 fps field is informational, not something to force. Temperature is model-specific.')],[1,3.5])
sub('The setting contract')
text('A generation request should carry purpose, target slot, usable seconds, crop/zoom needs, supported settings, allowance ceiling and acceptance criteria. Save both requested and observed values. Select and read back relevant controls before submitting; a dropdown click alone is not proof.')
callout('EXAMPLE OF PROPORTIONAL SETTINGS','For a three-second lower-panel insert in a 720p Short, request only enough source detail and time for that panel. Do not default to 10 seconds, 4K and High thinking. If a setting is unsupported or its cost unclear, hold the job rather than silently upgrade.')

start('Education: the format playbook')
table(['Series','Typical structure','Visual requirement'],[
('Useful AI in practice','Visible result -> one precise task -> short demonstration -> comparison.','Original screen recording or accurate illustration. Do not fabricate an interface or free feature.'),
('Study / productivity','Relatable friction -> one actionable method -> example -> small payoff.','Show the action: timer, task breakdown or before/after notes. Avoid a student-photo loop.'),
('Jobs / confidence','Specific mistake -> better wording/action -> side-by-side example -> next step.','A real example answer, resume line or interview scenario. No invented opening or guaranteed placement.'),
('Earning skills','Legitimate task -> requirements/work -> evidence -> realistic limitation.','Demonstrate the skill. A wealth montage does not prove viewers will earn money.'),
('General knowledge','Clear question -> supported explanation -> accurate payoff.','Relevant diagrams, objects, maps or authorized footage. Distinguish facts from illustration.'),
('Value / product reaction','Verified price/limitation -> strong opinion -> useful comparison -> verdict.','Actual source, date and configuration. Do not invent an outrage fact.')],[1,2,2])
text('These are proposed series within the agreed channel. Lesson and stock-footage routes exist, but each series still needs a convincing audience prototype. Test a small number of repeatable audience promises before mixing every subject into one feed.')
sub('Reference research still to complete')
text('Study actual relevant videos, including the kind of short business/skills content associated with Iman Gadzhi and Mark Tilbury. Record opening words, visual promise, beat count, proof, cuts and payoff. Their fame or public view counts alone do not establish which tactic caused success. No completed niche-specific breakdown is being claimed yet.')
callout('BEFORE MAKING A CLAIM','Verify current tool features, job listings and prices. A successful person\'s biography can support a story about that person; it does not prove viewers will reproduce that outcome by copying one tactic. Hypothetical examples must stay labelled.')

start('Entertainment: clips, chats and aura')
table(['Format','What fills the slots','Status and boundary'],[
('Original chat + gameplay','Timed fictional exchange or chat-image sequence above genuine gameplay.','Chat/gameplay slots exist. The basic chat look still needs a convincing style prototype and readable original comedy.'),
('Storytime + gameplay','Original narrated story, subtitles, gameplay or cut-out inserts.','Uses narrated route. Needs a strong story and fiction labels where applicable; no new approved storytime prototype.'),
('Creator / podcast moment','Permitted exact source segment, original speech, captions and optional gameplay.','Ingestion, ASR, selection and caption code exist. Approved catalogue and complete real route still need validation.'),
('Aura / sigma edit','Authorized portrait/clip, short caption, timed zoom/punch and permitted music.','Aura code and supporting assets exist; no approved audience-quality prototype. Never fabricate a creator quote.'),
('Cut-out reaction story','Original characters, poses, stage and narration with punch-ins.','Simple Pillow/FFmpeg motion exists. Full rigging, lip-sync and complex acting do not.'),
('Commentary / controversy','Sourced event, clear opinion, relevant media and bounded conclusion.','Use verified facts. A gossip post or popular repost alone is not sufficient evidence for an allegation.')],[1,2,2])
text('The visual grammar can use fast reveals, contrast, reactions and emphasis at the payoff. Adopting that grammar does not require copying a script or performance. Adding gameplay does not by itself resolve reuse or copyright issues. [R1]')
text('The cut-out animation reference was studied as visual inspiration: photographic/collage reactions, quick changes and emphasis text. The current original-character renderer is simpler. It is not a recreation of a professional animated scene or permission to reuse that reference\'s assets.',SMALL)

start('Movies, theories and visual payoffs')
table(['Format','Workflow','Important limit'],[
('Movie recommendation cards','Theme -> research titles -> order 9 picks -> original reasons -> audience tenth.','Posters/GIFs/excerpts need their own usable basis. A poster list with one-word praise may add little original value. No dedicated finished recommendation module.'),
('Franchise explainer','Question -> canonical sources -> original explanation -> answer.','Comics, anime and film remain copyrighted. The pipeline does not license franchises or authorize arbitrary downloads.'),
('Fan what-if / theory','State hypothetical -> assumptions -> reasoning -> speculative conclusion.','Do not present an invented future plot or leak as confirmed. Check current release details when used.'),
('Clay / sand loop','Generate/record a shape-and-break sequence -> inspect -> choose loop point.','Prompt helpers and bounded looping exist. Requesting a loop does not guarantee physical continuity or a seamless end.'),
('Build-to-payoff / room reveal','Plan scene -> show progress -> reserve final visible reveal.','Needs coherent actions and an actual payoff. Consistent multi-shot builds are harder than isolated short scenes.'),
('Nature / animal mini-story','Usable real footage or clearly synthetic scene -> progression -> payoff.','Do not label synthetic behavior as real evidence or invent the event.')],[1,2,2])
text('ASMR needs convincing synchronized sound and physical continuity. It often benefits from fewer cuts than an educational montage. Captions, CTA animations and music are optional; unnecessary overlays can spoil the audience promise.')
callout('FORMAT SUPPORT IS NOT CONTENT CLEARANCE','The compositor can place valid local media in a slot. Whether that input can be downloaded, edited, monetized or represented as real is a separate question recorded through source and asset evidence.')

start('How the scripter earns attention')
text('Begin with a specific visible tension or result, make a narrow promise, then deliver it. YouTube\'s interview with Jenny Hoyos emphasizes the first second and a compact shock/intrigue/satisfaction approach. Treat this as inspiration, not a universal formula or guarantee of views. [R6]')
table(['Framework','Original hook example','Required payoff'],[
('Visible contrast','“Same experience. Two resume lines. One is much clearer.”','Show both and explain the difference; no guaranteed hiring claim.'),
('Small live test','“Can this free tool do this without a card? Let\'s test it.”','Test the current free route and show the outcome, including a limit if encountered.'),
('Mistake -> correction','“This interview answer hides your best example.”','Show weak wording, a stronger truthful rewrite and why it is clearer.'),
('Story reversal','“He sent the confident reply. Then the next message arrived.”','An original readable exchange with a real reversal.'),
('Satisfying promise','Show the unfinished object and the final action about to happen.','Complete the build, break or reveal before the loop restarts.')],[1,2,2])
sub('The script contract')
text('Each unit needs a purpose, spoken text, on-screen text, factual claim references and a precise visual requirement. Avoid a long preamble, repeated setup or a CTA before the payoff. Title, opening and ending should describe and satisfy the same promise.')
sub('Implementation today and next')
text('editorial.py contains hook frameworks and agreed scope. writer.py requests JSON and can run one bounded repair plus evidence review. Rejected prototypes show that schema validity is not creative quality. A real-reference breakdown and stronger original script review remain unfinished.')
callout('SCRIPT APPROVAL TEST','Read it aloud with the selected voice pace. Can a viewer understand the promise immediately? Does each sentence advance it? Is the answer shown rather than merely asserted? Remove words that delay the payoff.')

start('The storyboard must control visuals')
text('This is the largest creative gap. montage.py can cut two panels quickly, but it cycles an asset pool. The result repeats footage unrelated to the sentence. The owner rejected this behavior. Increasing cut frequency alone will not fix it.')
table(['Beat / intention','Exact visual action','Acceptance test'],[
('Hook: two resume lines','Original fictional example: weak and revised, side by side.','Both readable on a phone; match the opening words.'),
('Explain weak wording','Highlight the vague phrase in the first line.','Highlight the phrase being discussed, not a random keyboard.'),
('Demonstrate rewrite','Replace it with a specific truthful description.','Animation follows narration; invent no achievement or metric.'),
('Show result','Return to the comparison and emphasize the change.','Ending delivers the promised contrast, with no unrelated photo.'),
('Optional next step','Show one action viewers can apply to their own wording.','Practical step without a hiring guarantee.')],[1.5,2,2])
text('This is an illustrative, unapproved concept, not a finished next script or a claim that the advice has already been validated. It demonstrates sentence-to-action matching.')
sub('The change to build')
text('Introduce a unit-to-shot plan: unit ID, exact asset/acquisition need, semantic purpose, crop, motion, timing, transition and fallback. Acquire only missing assets. Validate the visual meaning before render. A purposeful diagram or original screen demonstration is better than unrelated stock when a suitable image is unavailable.')
callout('AI VS CODE','AI proposes the visual meaning and search/generation prompt. Code checks files, dimensions, duration, reuse count and timing. A semantic review still matters: a hash cannot prove that an image depicts the narration.')

start('Where images and clips come from')
flow([('Storyboard need','Subject, action, slot and duration','ai'),('Choose route','Owner / stock / source / generation','code'),('Acquire + inspect','License and media properties','code'),('Register asset','Hash, credit, evidence and expiry','code'),('Bind unit','Exact file and visible action','code'),('Recheck at export','Evidence and state unchanged','code')], '',3)
table(['Route','Implemented behavior','Limit'],[
('Owner recording','Gameplay/footage registration with evidence and hash.','Review game policy, in-game music and third-party material.'),
('Commons','Keyless bounded download, license metadata and credits.','Basic filename ranking. Automatic allowlist excludes unknown/NC/ND/SA; this is a conservative choice, not a claim all SA use is unlawful.'),
('Pexels','Optional keyed stock-video acquisition.','No key configured; current API and license terms apply.'),
('Source catalogue','Permitted local file/URL, subtitles or local ASR.','No blanket creator/movie approval; some sources inaccessible or unsuitable.'),
('Generation','Import/registration and a tested local browser fixture.','Real Google, Brave and allowance need proof.')],[1,2,2])
text('Google Images results are discovery leads, not licenses. Permission from a creator may not cover a song, guest or TV insert. Save actual scope and date instead of a vague “does not strike” label. [R2, R9, R10]',SMALL)

start('Rights, claims and monetization')
text('Track source performance, images, gameplay and music separately. Record commercial/editing permission, credits, restrictions, expiry and provenance. A record aids traceability; it cannot guarantee a dispute-free upload.')
table(['Issue','Meaning','Response'],[
('Content ID claim','A rights match may affect availability or revenue; not automatically a strike.','Preserve evidence and inspect the exact claim. Pause affected work if appropriate. [R3]'),
('Copyright strike','A removal request led to a strike. Deletion generally does not clear it.','Alert and hold similar pending jobs; no automatic legal counter-notification. [R2]'),
('Reused / inauthentic','A monetization issue separate from copyright permission.','Improve original contribution and substance. Resizing/rearranging a repetitive template is not a reliable cure. [R1]'),
('Misleading claim','Fabricated job, quote, opening or outcome.','Require evidence or rewrite as a clearly labelled hypothetical/opinion; never fake proof.'),
('Identifiable person','Copyright terms may not settle endorsement, publicity or privacy.','Use neutral context; do not imply the stock person endorsed a method, failed or earned a stated sum. [R9, R10]')],[1,2,2])
text('No creator list or download source can promise zero claims or strikes. The operational goal is documented usable inputs, substantial original value, accurate presentation and a controlled response to incidents.')
sub('Why template changes are insufficient')
text('A layout can repeat as part of a recognizable series. The substance must still vary and contribute something meaningful. Cosmetic changes to size, position, border or music do not establish originality. Likewise, permission to repost does not automatically establish channel eligibility. [R1]')
callout('RISK ACCEPTANCE HAS LIMITS','The owner can choose a strategy and tolerate uncertainty. The program should still not invent permission, fake an income outcome or treat a tolerated repost as an approved monetization business.')

start('Voice, speech and captions')
sub('The accepted voice path')
text('Kokoro ONNX works locally on CPU. The latest prototype uses male am_adam, faster length scale 0.78 and loudness normalization. The owner accepted this voice. Retain it while improving the script and visuals. Piper remains an alternative, not the only available option.')
table(['Component','What it does','Distinction'],[
('Kokoro + ONNX','Local neural speech using installed weights and voices.','Weights and runtime have separate licenses; Kokoro weights are Apache 2.0. Language/voice quality varies. [R11, R12]'),
('Piper fallback','CPU speech from a different model/voice package.','Check each voice model license; one model\'s terms do not cover all Piper voices. [R13]'),
('TTS timing','Measure/cache units, pad to frames and assemble narration.','Unit timing is not perfect per-word forced alignment.'),
('Subtitles / ASR','Parse VTT/SRT or run faster-whisper on registered media.','ASR can mishear names/numbers. Inspect selected context and captions. [R14]'),
('Caption output','SRT plus actual timed burn-in for source clips.','Keep clean render and caption manifest. Inspect placement at phone size.')],[1,2,2])
text('Audio checks detect silence/clipping. Current normalization targets -14 LUFS integrated and -1.5 dB true peak. This is an engineering preset, not a guarantee of equal perceived volume on every device. Background music must stay below clear speech.')
text('Commanding delivery also depends on short phrases, emphasis and useful pauses. Multilingual production needs per-language voice and script validation. Installed English speech does not prove natural output in every market.')
callout('ORIGINAL SPEECH IS A DIFFERENT ROUTE','For a selected source moment, preserve its speech and skip TTS. Captions follow the actual source transcript; do not voice-clone the speaker or fabricate a quote.')

start('The editor is a format engine')
layout()
text('The program supplies real assets and JSON. The compositor crops/scales into slots, applies borders/effects, mixes sound, places captions and exports MP4. The owner should not have to drag clips around a timeline.')
table(['Layer','Decision'],[
('Script / beat plan','What is said, what viewers must see and when payoff occurs.'),('Director JSON','Asset, source offset, duration, crop, panel, effect and audio.'),('FFmpeg render','Exact frames/pixels, trims, encoding and sound mix.'),('Outputs','H.264/AAC MP4, SRT, PNG cover, project JSON and hashed manifest.')],[1,3])
text('The current renderer supports 720p/1080p, 24/30 fps, bounded shots, crop/contain, punch/flash/shake, borders/glow and CTA overlays. Pipeline duration stays below 180 seconds. These are templates, not arbitrary After Effects compositions.')
callout('WHY KEEP FFMPEG','It is scriptable, reproducible and works without opening a desktop editor. Premiere, After Effects and Resolve can remain future options for advanced templates. No completed native-project bridge is claimed.')

start('Music and sound by format')
table(['Format','Starting direction','Avoid'],[
('Aura / reaction','Permitted rhythm with a timed reveal hit.','Assuming popular phonk is copyright-free.'),('Chat / cringe comedy','Light tension, short comic cue or silence before the final line.','Drowning out text/voice or default copyrighted meme sounds.'),('Education / demo','Quiet bed or no music; a small result cue.','Wealth music replacing evidence.'),('Storytime','Low-volume mood, clear speech hierarchy.','Loud continuous loop or unrelated stings.'),('Gameplay','Usable game audio or permitted track.','Assuming in-game radio belongs to the publisher.'),('ASMR','Convincing synchronized material/tool sound.','Music obscuring the sound being promised.')],[1,2,2])
sub('What the agent does today')
text('music_agent.py has six mood categories, Commons acquisition and a tagged library. Optional public video observations can inform candidates. It does not reliably prove that a track is trending in a country, nor that a tagged sound fits the actual edit.')
sub('What the next version needs')
text('Store tempo/energy, useful segment, intro length, speech-safe volume and credits. Match sound to beats and audition the real mix. Keep a small usable library. A popular reference and an acquired licensed asset are separate things.')
text('Music offered inside YouTube creation tools follows the applicable platform workflow. Do not assume that permission transfers to an externally rendered MP4, another platform or every upload type. There is no licensed catalogue of all viral songs in this project. [R4]')
callout('NO AUTOMATIC POPULAR-SONG DOWNLOADER','Trend research can record a reference. Download/assembly should use the separately verified usable track, original sound or silence. Similar mood does not require the identical copyrighted recording.')

start('Quality checks and prototype review')
flow([('Technical gates','Decode, timing, sound and files','code'),('Evidence gates','Claims, permissions and freshness','code'),('Creative review','Hook, relevance, pace and payoff','ai'),('Prototype feedback','Watch the real phone-sized export','code'),('Revise upstream','Fix words/shot plan before render','code'),('Release candidate','Freeze approved package version','code')], 'Technical/evidence checks exist. Richer semantic/editorial review remains a planned improvement. A model pass does not replace watching the export.',3)
table(['Prototype','What worked','Feedback / limit'],[
('Technical education exports','Real Gemini JSON, local speech and MP4.','Topics too technical for the channel.'),('13.6-second stock version','Sourced photo in a real render.','Generic script and repeating visual rejected.'),('21.3-second moving version','Footage and Kokoro route.','Pace/delivery needed revision.'),('15.45-second three blocks','Fast accepted voice, two panels and cuts.','Script rejected; pool repeated and did not follow narration.')],[1.5,2,2])
text('The full suite passed 78 tests, including real FFmpeg subtitle-burn checks and a local browser download fixture. Two Pillow deprecation warnings remain. This does not prove real Google access, monetization or retention.',SMALL)
callout('NEXT PROTOTYPE EXIT CRITERIA','New original concept; word and visual hook; sentence-matched shots; accepted voice; no arbitrary repeating pool; a delivered payoff; clean phone-size playback. Prove this before scaling daily volume.')

start('Publishing is a separate workflow')
flow([('Connect owner','OAuth and verify channel identity','code'),('Preview package','Exact MP4, metadata and credits','code'),('Approve version','Bind hashes and intended account','code'),('Persist session','Save upload intent and offset','code'),('Upload / reconcile','Resume known session; no duplicates','code'),('Observe result','Remote ID and available status','code')], '',3)
text('publishing.py implements disabled/private/scheduled modes, dry runs, account binding, version approval and resumable sessions. It stores intent before upload and probes an existing session after uncertain completion instead of blindly creating another video.')
sub('Current live status')
text('OAuth is not connected. No real owner-channel upload, schedule, copyright-check result or thumbnail application has been verified. Default publication remains disabled. Packaged titles/descriptions come from the script and credits; this is not yet a mature title-testing or thumbnail-strategy system.')
sub('Enabling automation')
text('First verify one private upload against the correct channel and package. Check response, playback, metadata and available platform checks. Exact-version approval is enforced. An optional auto_private_upload policy can approve eligible versions and upload privately; it is off. Its real account route must be tested before unattended use.')
text('A PNG cover is exported, but this is not a full thumbnail-maker workflow. Shorts thumbnail selection and API support must be checked for the actual surface. A successful upload response does not establish ad eligibility or that every check has finished. [R7, R8]')
callout('NO AUTOMATIC LEGAL ACTION','Do not automatically dispute a claim, file a counter-notification or assume deletion fixes a strike. Preserve incident evidence for owner review. [R2]')

start('Supervisor, incidents and recovery')
table(['Signal','Implemented response','Missing / limited'],[
('Stalled local job','Leases, timestamps, held reasons and checkpoint retry.','Cause still needs resolution; retries cannot create missing rights.'),('Disk / expired asset','Local checks, alerts and pause controls.','External phone/chat notification not configured.'),('Provider quota','Durable shared cooldown, cached results and waiting.','Local counts are not provider balance.'),('Remote upload status','Optional authorized reconciliation and observations.','No complete copyright-strike feed or full platform-health guarantee.'),('Reported incident','Record and pause affected production/publication.','Learning the correct new rule from every incident is not fully automatic.')],[1,2,2])
sub('Intended incident loop')
flow([('Detect / report','Save exact platform message','code'),('Contain','Pause affected queue; preserve files','code'),('Diagnose','Identify source and actual restriction','ai'),('Owner decision','Resolve the specific incident','code'),('Update rule','Add verified correction','code'),('Regression check','Test before re-enabling','code')], '',3)
text('Do not delete unrelated uploads after an uncertain alert. Keep evidence, hashes and the exact package. Rules should be narrow and justified, such as blocking an expired source profile, rather than guessed restrictions for an entire genre.')
text('Local dashboard alerts and owner inspection remain practical today. Add external notifications only after choosing and authorizing a service. No message, email or platform dispute is sent simply because this report describes a future feature.',SMALL)

start('The growth officer and feedback loop')
flow([('Publish a test','One clear audience promise','code'),('Observe','Owned metrics at checkpoints','code'),('Compare','Age, format and topic cohorts','code'),('Hypothesize','Possible explanation, not certainty','ai'),('Experiment','Change one meaningful variable','ai'),('Review again','Keep/reject using new results','code')], '',3)
table(['Data','Can tell us','Cannot establish'],[
('Owned Analytics','Available authorized video/channel metrics after reporting delay.','Precise causation from a small sample; revenue without metric access.'),('Public competitors','Public views, age, titles and later observed growth.','Private retention, RPM, geography or exact earnings.'),('Prototype feedback','Readability, repetition, mismatched shots and payoff.','Guaranteed wider-audience response.')],[1,2,2])
text('benchmarks.py saves snapshots and later observed deltas. monitor.py schedules owned checks around 24 hours, 72 hours and seven days using calendar-date reports with lag. Missing data is not zero. A basic growth rule needs three comparable observations before proposing an experiment.')
text('Keep differences in length, topic and format visible. A rise in views does not prove the music or hook caused it. Transferring a successful format from another market is a testable idea, not guaranteed demand.')
callout('CURRENT GAP','Public YouTube API credentials and owner Analytics are not connected for a full live loop. No actual channel results or RPM values currently justify growth or income promises.')

start('Free operation and resource limits')
table(['Resource','Choice','Practical limit'],[
('Text model','Gemini free text route, billing disabled, structured output; no paid fallback.','Quotas/availability change. Rotating keys does not expand a project quota. [R5, R15]'),('Speech / ASR','Local Kokoro/Piper and faster-whisper.','CPU time, storage, electricity and model downloads remain.'),('Editing','Python, Pillow and FFmpeg on existing PC.','Keep PC awake; rendering competes for CPU/RAM/disk.'),('Stock','Eligible Commons; optional free Pexels API.','Relevant free media is not unlimited.'),('Browser generation','Only verified included account access.','Subscription UI access differs from API billing. Model/allowance still need proof.'),('Cloud','Local first; no paid deployment.','Free cloud is not a guaranteed always-on renderer; sleep, storage and runtime limits apply.')],[1,2,2])
sub('Quota controls already written')
text('HTTP 429 handling honors Retry-After/RetryInfo. Without a longer hint, repeated quota responses back off from one minute to one hour. An explicit daily violation conservatively holds for 24 hours, or longer if instructed. Cached successes remain usable. Local daily accounting resets at UTC midnight; provider daily reset is Pacific time. [R5]')
text('The goal is no additional software/API spend using existing resources. It is not unlimited output without resource use. Four or ten videos daily per channel is an unproven proposed pace. Measure render time, quality and quotas before choosing a cap.')
callout('BROWSER ALLOWANCE IS ALSO A BUDGET','Use the shortest adequate clip and appropriate image size, save results for reuse where meaningful and do not regenerate after ambiguous submission. No automatic purchase, billing enablement or paid fallback is authorized.')

start('Revenue and realistic milestones')
table(['Route','Best format fit','Required first'],[
('YouTube ads','Original Shorts / longer videos with repeat viewers.','Eligibility, accepted YPP review, suitable videos and measured performance.'),('Affiliate','Truthful tool demos and useful workflows.','Suitable approved program, disclosure and real conversions.'),('Sponsors','Coherent education audience or recognizable entertainment series.','Relevant stable reach, audience evidence and actual agreement.'),('Clipping campaigns','Permitted campaign deliverables.','An actual accepting campaign, rules and payment terms; reposting alone does not earn.'),('Products / services','Useful templates or services tied to demonstrated skill.','A worthwhile offer, support and honest claims. A paid course is not required.'),('Other platforms','Adapted versions with compatible rights.','Separate accounts, exports and rules. No finished cross-posting adapter.')],[1,2,2])
text('Current YPP guidance gives the main ad routes as 1,000 subscribers plus either 4,000 qualified watch hours in 12 months or 10 million qualified Shorts views in 90 days. Review is still required; Shorts-feed hours do not count toward that watch-hour route. Recheck Studio eligibility before relying on a threshold. [R16]')
sub('Milestones instead of invented income dates')
text('<b>First:</b> one convincing prototype and private upload.<br/><b>Then:</b> a small coherent series and comparable results.<br/><b>After evidence:</b> refine the winning promise; assess eligibility or affiliate fit.<br/><b>With repeatable audience proof:</b> evaluate sponsors or other offers.')
text('There is no basis yet for “X weeks = Y income.” Later estimates must use actual eligible views, RPM or conversions and net costs. US geography alone does not establish payout. No channel earnings, sponsor rates or affiliate income are validated.')
text('The current Shorts policy also announces a new monthly revenue condition from 01 Feb 2027 involving 10 million qualified Shorts views in the preceding 90-day measurement window. Recheck the published terms and Studio before modelling future income. [R4]',SMALL)

start('Possible, conditional or absent')
table(['Request','Assessment today'],[
('JSON -> finished video','Possible locally with valid registered media. Good content still needs strong scripting and relevant visuals.'),('Fast voice / multiple panels','Verified in real export. Latest voice accepted; content not approved.'),('Find/download stock','Restricted Commons route implemented; optional Pexels. Relevance remains imperfect.'),('Creator/movie clipping','Conditional on usable exact sources and rights. No blanket approved catalogue or completed live route.'),('AI Studio in signed-in Brave','Target design; session, selectors and settings unverified. A direct URL alone does not complete it.'),('Every clip free','Not guaranteed; allowances/models/wait times vary. No paid fallback.'),('All strikes by API','Not a complete current capability. Owner Studio inspection remains necessary.'),('Guaranteed monetization','Not possible. Permissions, technical checks and originality do not determine external decisions.'),('Automatically go viral','Not guaranteed. Growth loop needs real data and experiments.'),('All languages / niches','Future expansion; validate speech, culture, scripts, rights and audience per market.'),('Heavy desktop editor','No native bridge implemented; present scope is a format engine.')],[1.5,3.5])
text('These limits do not prevent useful automation. Prove a narrow route, then expand. A larger multi-agent diagram does not substitute for missing rights, account access or creative quality.')

start('Implementation inventory')
table(['Area','Evidence / state','Remaining acceptance check'],[
('Orchestration','SQLite, leases, hashes, cache and recovery tests.','Long unattended run on operating PC.'),('Live text generation','Real research, JSON script and evidence review.','Better original niche-specific writing.'),('Voice / export','Real local voices and MP4s; latest voice accepted.','Retain voice in a genuinely new concept.'),('Three-block montage','Real fast-cut two-panel render.','Replace round-robin pool with semantic storyboard.'),('Acquisition','Actual Commons downloads and evidence.','Better semantic search and contextual use.'),('Source / clip chain','Catalogue/transcript/range/caption tests; local ASR.','Complete route with actual permitted source.'),('Aura / cut-out','Code and supporting assets.','Convincing approved prototypes.'),('Browser generation','Local mock submit/download; duplicate protection.','Real Brave, target page, model, settings and result.'),('Publish / growth','Adapters and fixture recovery tests.','OAuth, private upload and real checkpoint metrics.'),('Dashboard','Queue and operational controls.','Expose newer features; restart/retest current UI.')],[1.3,2,2])
text('Latest suite: 78 passed in 75.03 seconds; two Pillow deprecation warnings. This is not evidence of a real Google generation, source-series publication or income. External pages and local services can change after this snapshot.')

start('Completion order and release gates')
table(['Order','Deliverable','Done means'],[
('1. Creative','Reference breakdown, new original script and storyboard.','Every beat has a relevant visual; promised payoff delivered. No rejected procrastination remake.'),('2. Editor','Unit-to-shot binding, reuse limits and pacing.','No arbitrary carousel; captions/assets follow speech.'),('3. Google','Direct targets, Brave access, settings and budgets.','Real included-access output generated once, downloaded and registered; observed settings saved.'),('4. Prototypes','Education, one entertainment series and generated payoff.','Usable exports watched and refined with owner feedback.'),('5. Sources','Approved catalogue and real source clip.','Scope covers use; transcript in range; credits/audio correct.'),('6. Publishing','OAuth and one exact-version private upload.','Correct channel/playback/metadata/remote ID/recovery.'),('7. Learn / scale','Metrics, alerts and small experiments.','Real checkpoint loop; raise output only with quality/quota/audience evidence.')],[1,2,2.5])
sub('A gate-based schedule')
text('Creative feedback may need iterations. Browser/account behavior is external. Set dates after measuring the first working pilot, rather than promise income by a particular week. Count actual render time, allowance usage and manual exceptions before deciding daily volume.')
callout('FIRST NEXT ACTION','Improve the new script/storyboard while independently calibrating Google. Reuse the accepted voice and compositor. A convincing next prototype is more valuable than adding infrastructure without validating content.')

start('Operating the current project')
text('Install production/development dependencies; optional browser features need Playwright and a runtime. Keep secrets in ignored local configuration. The PC must remain awake. The local dashboard uses loopback port 8765; Adobe/Resolve is not required.')
text('<b>Typical commands (replace JOB_ID and input files):</b><br/>.venv\\Scripts\\python.exe run_pipeline.py doctor<br/>.venv\\Scripts\\python.exe run_editor.py serve --open<br/>.venv\\Scripts\\python.exe run_pipeline.py status<br/>.venv\\Scripts\\python.exe run_pipeline.py run JOB_ID<br/>.venv\\Scripts\\python.exe run_pipeline.py retry JOB_ID --from-stage direct<br/>.venv\\Scripts\\python.exe run_pipeline.py alerts',SMALL)
table(['Location','Purpose'],[
('src/yt_pipeline/','Roles, contracts, state, adapters and CLI.'),('src/shorts_editor/','Compositor, FFmpeg rendering, project store and local server.'),('examples/','Request examples; review before using as audience content.'),('data/pipeline/','Private jobs, database, assets, models, reports and credentials. Back up privately.'),('PROJECT_GUIDE.md','Maintained architecture/setup and current limitations.'),('docs/PROJECT_STATUS.md','Current audit, readiness and remaining work; earlier tracking is archived.'),('tools/build_blueprint_pdf.py','Reproducible PDF layout; blueprint_content.py holds the dated content.'),('output/pdf/','Reader-facing system blueprint.')],[1.5,3])
text('Job artifacts include research, script, timing, visuals, director/render and quality/package JSON. Render folders hold MP4, SRT, PNG and manifest. Inspect recorded paths rather than assume a render hash.')
text('For a hold: read its code/message, resolve the cause and retry the affected stage. Respect cooldowns. Reconcile uncertain uploads/generations before starting replacements. Never print secrets or copy private browser profiles into a shared report.')

start('Sources and evidence')
text('Repository and prototype records support implementation status. These primary sources support external rules, limits and technology behavior. Consulted 01-02 Nov 2026; recheck before release. Links are clickable.',SMALL)
refs=[
('R1','YouTube monetization policies','https://support.google.com/youtube/answer/1311392?hl=en'),
('R2','YouTube copyright strikes','https://support.google.com/youtube/answer/2814000?hl=en'),
('R3','YouTube Content ID claims','https://support.google.com/youtube/answer/6013276?hl=en'),
('R4','YouTube Shorts monetization','https://support.google.com/youtube/answer/12504220?hl=en'),
('R5','Gemini API rate limits','https://ai.google.dev/gemini-api/docs/rate-limits'),
('R6','YouTube Shorts deep dive - creator hooks','https://blog.youtube/creator-and-artist-stories/youtube-shorts-deep-dive/'),
('R7','YouTube resumable uploads','https://developers.google.com/youtube/data/guides/using_resumable_upload_protocol'),
('R8','YouTube videos.insert','https://developers.google.com/youtube/data/reference/rest/v3/videos/insert'),
('R9','Creative Commons Attribution 2.0','https://creativecommons.org/licenses/by/2.0/'),
('R10','Commons: identifiable people','https://commons.wikimedia.org/wiki/Commons:Photographs_of_identifiable_people'),
('R11','Kokoro model and license','https://huggingface.co/hexgrad/Kokoro-82M'),
('R12','Kokoro ONNX runtime','https://github.com/thewh1teagle/kokoro-onnx'),
('R13','Piper runtime / voice-model context','https://github.com/OHF-Voice/piper1-gpl'),
('R14','faster-whisper transcription','https://github.com/SYSTRAN/faster-whisper'),
('R15','Gemini pricing / model tiers','https://ai.google.dev/gemini-api/docs/pricing'),
('R16','YouTube Partner Program eligibility','https://support.google.com/youtube/answer/72851?hl=en')]
for rid,title,url in refs:
    text(f'<b>{rid}</b> &nbsp; <link href="{url.replace("&","&amp;")}" color="#ac4d2c">{title}</link><br/><font color="#65645f">{url.replace("&","&amp;")}</font>',SMALL,5)

start('Definitions and the finished target')
table(['Term','Plain-language meaning'],[
('Brief','Task: audience, topic, format, source and constraints.'),('Unit / beat','Small part of the script with purpose, words, timing and visual need.'),('Storyboard','Map from each beat to a visible action or exact asset.'),('Asset','Local media file with properties, hash and evidence.'),('Source profile','Versioned permitted work/episode and scope of use.'),('Manifest / hash','Input/output record and change detection; not legal/creative proof.'),('Held / retry-wait','Work needs an input fixed or a bounded waiting period to expire.'),('OAuth','Owner grants scoped access to the actual channel.'),('Publication-ready','Implemented local gates passed; external outcomes remain separate.'),('RPM / experiment','Measured revenue metric / test of a creative hypothesis against comparable results.')],[1.3,3.5])
sub('What a finished pilot demonstrates')
text('An original engaging script comes from real research; each spoken beat has a relevant visual; accepted speech stays clear; export needs no manual timeline editing; claims/inputs are traceable; one version reaches the correct channel under a verified policy; and results inform a recorded next experiment.')
sub('What this document establishes')
text('Architecture, responsibilities, format families, current evidence, missing connections and order of work are explicit. Next work should improve relevance and prove external integrations, rather than describe untested adapters as an autonomous channel business.')
callout('THE DESIGN PRINCIPLE','Spend effort and allowance on the promised viewer payoff. Reuse reliable code, keep settings proportional to the shot and make every output inspectable.')
