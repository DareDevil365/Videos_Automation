# Generated writer/director contracts

Each `<playbook>.writer.json` contains the actual exported writer rules for one of the six presets. `director-schema.json` defines scene/cast output; `director-capabilities.json` and `edit-blocks.json` describe supported operations.

Source of truth: [playbooks.py](../../src/yt_pipeline/playbooks.py), [creative_plan.py](../../src/yt_pipeline/creative_plan.py), [edit_blocks.py](../../src/yt_pipeline/edit_blocks.py) and [scene_blocks.py](../../src/yt_pipeline/scene_blocks.py). Regenerate from the root with:

```powershell
.venv\Scripts\python.exe run_pipeline.py playbooks --export Resources/Prompts
```

Do not maintain divergent manual prompt copies. Unsupported operations are not implemented simply by adding them to a prompt. Read the relevant [creation guide](../../docs/categories/README.md) and [template limits](../Templates/README.md).
