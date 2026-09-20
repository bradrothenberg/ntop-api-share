---
name: open-ntop-gui
description: "Open a prepared nTop notebook interactively with a selected Automate input JSON, including review of a saved DOE point."
---

# Open nTop with selected inputs

Use this when the user requests an interactive notebook window with a known parameter set.
For native geometry images, use the [Notebook API skill](../ntop-notebook-api/SKILL.md) and [rendering guidance](../../../docs/VERIFICATION.md).

The source workflow observed `ntop.exe -j` on Windows with nTop 5.51.3.
Confirm support in the selected executable's help and preserve the notebook's version requirements.

```powershell
& "C:\path\to\ntop.exe" -j "input.json" "model.ntop"
```

1. Resolve the notebook and input paths. Record their hashes and the selected executable.
2. Generate a template with the matching `ntopcl` and compare input names, types, and units.
3. Make a separate GUI input JSON. Remap only declared output paths into a task-owned directory.
4. Preserve imported file paths, filenames, and required assets. A missing input is not an output directory.
5. Launch the selected notebook in a task-owned session. Record its PID, executable, and creation time.
6. Verify the intended notebook, applied values, and completed evaluation. A window title or dirty marker alone is insufficient.

Do not pass `--save` for a read-only inspection. Use a working copy when evaluation can write into the notebook or adjacent assets.
Do not attach to or replace another project's open notebook.
For API attachment, follow the repository's [owned-process procedure](../../../docs/BACKGROUND_CONSOLE.md).
This portable version uses the explicit CLI command instead of the old launcher that automatically rewrote every missing path.
