# Maintenance and demonstration tools

Run tools from the project root. These are separate from normal production commands.

| Tool | Behavior |
| --- | --- |
| [check_project_docs.py](check_project_docs.py) | Offline local Markdown target and move-map validation; JSON output/nonzero on missing targets |
| [build_edit_gallery.py](build_edit_gallery.py) | Builds technical cast/framing previews from local assets |
| [build_motion_block_gallery.py](build_motion_block_gallery.py) | Builds comparison/process/callout example graphics/gallery |
| [create_upgrade_demo.py](create_upgrade_demo.py) | Creates a missing demonstration plan and fetches a source excerpt; does not overwrite an existing initialized plan |
| [create_storytelling_pilot.py](create_storytelling_pilot.py) | Owner-requested assistant-authored fictional story and prepared direction; local speech/render, closed provider, six supplied original art files, zero Gemini calls verified |
| [create_editorial_demo.py](create_editorial_demo.py) | Offline test-only original rewrite pilot; prepared plan, local speech/alignment, no Gemini requests; requires a prepared source brief and installed local models |
| [create_assistant_five.py](create_assistant_five.py) | Five assistant-authored portrait videos through the existing toolbox; requires checked local stock/art/GIF inputs, refuses remote generation and preserves revision state |
| [curate_music_library.py](curate_music_library.py) | Inspect/install the hash-pinned permitted music catalog and choose a registered genre track; downloads only when explicitly requested |
| [curate_sound_library.py](curate_sound_library.py) | List/install/select reusable original effects and permitted ambience; originals install offline |
| [create_source_short_pilots.py](create_source_short_pilots.py) | Resume the two supplied movie and current-affairs Shorts; local motion graphics, no provider calls, no upload |
| [build_blueprint_pdf.py](build_blueprint_pdf.py) | Builds the dated PDF blueprint with ReportLab/system fonts |
| [blueprint_content.py](blueprint_content.py) | Content used by the PDF builder; historical snapshot rather than live current status |

Preview/demo builders write files and some may fetch data; consult their code before treating them as read-only checks. The current [project status](../docs/PROJECT_STATUS.md) and [architecture guide](../PROJECT_GUIDE.md) supersede historical blueprint implementation counts.
