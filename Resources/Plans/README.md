# Production plans and recorded inputs

These files retain their original names/paths because initialized production plans and job evidence are version/hash-bound. Use a new plan ID/file for changed content. [Category guides](../../docs/categories/README.md) explain how to create a new plan.

| Group | Files and meaning |
| --- | --- |
| Original three-format batch | `prototype-batch.json`: legacy ASMR/mystery/aura technical prototypes; exported but creatively rejected |
| Chat pilots | `tea-playbook-pilot.json`, `tea-playbook-quality-pilot.json`, `tea-playbook-refined.json`: successive recorded test inputs; not interchangeable current defaults |
| Cutout/comedy work | `human-cast-episode.json`, `human-cast-final-episode.json`, `roommate-comedy-episode.json`, `couch-fee-comedy-episode.json`: recorded production requests/plans; inspect their shape before passing to a command |
| Script revision | `human-cast-revised-script.json`: script material, not a generic batch definition |
| Registered input records | `cast-preview-assets.json`, `stock-pilot-assets.json`, `comedy-room-asset.json`: asset records/mappings, not all executable batch plans |
| Motion-block demos | `repo-upgrade-demo.json`: earlier development attempt; `repo-upgrade-final.json`: completed final typography pilot/resume input |
| On-demand starter | `playbook-starter.json` is created by the control panel/default batch path when absent. It may not exist until then; its missing music/media are intentional prerequisites |

Some `.json` files are requests, scripts or asset records despite sharing this folder. Read the top-level keys and the [data contracts](../../docs/CODE_WALKTHROUGH.md#6-files-and-data-contracts). A version-1 batch requires `id`, `items` and each item's supported `kind`; a raw script/request is used through its corresponding CLI interface.
