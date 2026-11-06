# Comic recut audio measurements

Checked 6 November 2026 against actual saved narration and render records. The table immediately below covers the earlier intermediate recut under `Resources/Productions/doom-broken-worlds-tight-20261106/`. The comparison uses `doom-broken-worlds-photo-20261106/`. The final serialized version uses a 1.08 speech speed and longer cliffhanger scripts under `Resources/Productions/doom-broken-worlds-serial-20261106/`; its measurements follow separately.

FFmpeg measured runs below −42 dBFS lasting at least 150 ms. These counts include sentence pauses and the end of the recording. They describe sustained quiet, which can also contain soft breathing. The new scripts differ from the old scripts, so the duration reduction includes both writing changes and PCM trimming.

| Part | Old narration duration | Recut narration duration | Old quiet runs ≥150 ms | Recut quiet runs ≥150 ms | Old runs >300 ms | Recut runs >300 ms | Longest old run | Longest recut run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 42.667s | 31.967s | 19 | 1 | 16 | 0 | 501.5ms | 159.7ms |
| 2 | 41.100s | 30.900s | 20 | 3 | 13 | 0 | 497.5ms | 179.2ms |
| 3 | 38.067s | 31.300s | 18 | 1 | 12 | 0 | 502.6ms | 173.1ms |

The trimming pass removed 3.390s, 3.171s and 3.027s respectively from the newly synthesized unit clips before narration assembly. Their surviving quiet runs above this measurement threshold occur near the final host handoff or inside the closing message. All three recuts have zero runs above 300ms by this measurement.

The trim code preserves 24ms at the start, 40ms at the end, and 60ms on either side of qualifying internal rests. It checks 8ms blocks against a threshold scaled from the clip peak. An independent reconstruction of the edit points in the original cached clips found maximum internal splice amplitude changes of 7, 4 and 9 counts respectively on the 16-bit PCM scale of 32768. These small changes place the joins close to silence. Short consonant or breath timing can still sound different after gap removal, so full subjective listening remains relevant.

Both `compose-job.json` and `render-project.json` contain the selected start and gain values.

| Part | Registered source | Source start | Linear gain | Measured source mean over 38s | Effect in actual narration |
| --- | --- | --- | --- | --- | --- |
| 1 | Fallen (Asper), Eugenio Mininni · `mixkit-565` | 0s | 0.070 | −15.9 dBFS | Impact at 13.380s, gain 0.48 |
| 2 | Echoes, Andrew Ev · `mixkit-188` | 16s | 0.100 | −21.1 dBFS | Reveal at 13.180s, gain 0.48 |
| 3 | Piano Reflections, Ahjay Stelino · `mixkit-22` | 0s | 0.067 | −16.3 dBFS | No effects |

The Part 2 source offset skips Echoes' unusually quiet introduction, which measured −45.2 dBFS in its first five seconds. The selected quiet beds preserve room for the narration. The tracks are installed, their registered hashes passed eligibility checks, and all three proposed excerpts decoded successfully. [Mystery recordings](https://mixkit.co/free-stock-music/tag/mystery/), [Piano Reflections](https://mixkit.co/free-stock-music/instrument/piano/), [recording license](https://mixkit.co/license/modal/musicFree/).
