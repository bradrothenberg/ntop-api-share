# Setup

Current authoring baseline: **nTop 6.1.0-rc build 42926**. Read [the current API reference](API_REFERENCE.md).
Build 42594 remains the recorded source of older demo results. Opening those files on another build is not a new verification.

Run host Python through uv from the repository root. `uv sync --locked` installs pinned dependencies.
`scripts/bootstrap.ps1` sets NTOP_PYSCRIPTS to this checkout's harness/ for the current PowerShell session.
Pass -NTopExe or set NTOP_EXE to the exact matching licensed custom-build executable.
Launch a separate task-owned nTop process directly from that PowerShell session with `Start-Process`, then author through the Notebook API.
Follow [launch and attachment checks](BACKGROUND_CONSOLE.md#launch-a-separate-task-owned-process) before editing; opening a second window alone does not select its TCP session. Computer Use is not required.
An already-running nTop instance does not inherit new environment variables; restart a task-owned session or
add this checkout's harness folder to sys.path manually in its Python Console.

Read [the build 42926 update](API_42926.md) for current capabilities and the optional owned-session TCP tool.
`ntop_api.check_api(notebook, require_42926=True)` checks feature presence without changing the graph.
Use the tiny `ntop_api.hello(notebook)` check in an empty notebook before a large build.
`ntop_api.use("jet20")` selects one demo and clears cached modules from other demo folders.
Then `import agent` exposes run, dump, recipe, blocks, properties, and api helpers.
These helpers write receipts beneath the selected demo's output/_agent directory.

## Build and import

```powershell
uv run --locked python scripts/build.py fury
uv run --locked python scripts/stage.py fury
```

The staged script requires an empty notebook. It imports the complete recipe, saves a working .ntop,
and exports a recipe readback. It does not certify geometric validity merely because import succeeded.
Registered demos are i6, i6-astra, jet20, fury, b52, ddgx, f16, a12, fcat, propellers, and kestrelsat-corner.
The last five use saved-graph replay. See each demo README for revision and native-build scope.

## Inspect the current build

`agent.api(notebook)` records live method docstrings. `agent.properties(notebook, block_id)` records inputs and output property names.
Use `block_catalog.lookup(notebook, mask)` for bounded identifier discovery.
`agent.dump` records readable values, display units, build states, and read errors for connected or unsupported inputs.
These helpers do not convert an unreadable property into a literal or prove geometry correctness.

The optional [value probe](../examples/probe_42926.py) checks real, integer, bool, and text in an empty task-owned notebook.
It does not cover all six types, movement, clearing, list processing, or recipe input/output behavior.
Method presence and offline tests do not replace those native checks.

For external commands on build 42926, use [owned-session TCP dispatch](BACKGROUND_CONSOLE.md).
For an older build without that listener, use the window-message bridge described on the same page.

## Notebook paths

`scripts/prepare.py --models` writes separate working copies beneath .local/models.
Tracked notebooks use repo:// path references where export filenames are required.
Preparation resolves those paths into the recipient's checkout. nTop itself does not resolve repo://.
Use a working copy, retain the tracked source, and keep generated exports in ignored output folders.
Preparation preserves an existing working file; choose a new working path when intentionally refreshing it.

## Saved presentation

```powershell
uv run --locked python scripts/collapse_saved_notebook.py .local/staged/fury/Model-working.ntop -o .local/staged/fury/Model.ntop
```

This is a file-format workaround, not a Notebook API call. It changes only block and section expansion state.
Use a separate output path after the final save. Reopen and inspect the deliverable when the GUI is available.

Native API imports can exceed an offline smoke-test duration. Monitor the command receipt and process progress.
Do not queue another mutation until the previous command has completed.
