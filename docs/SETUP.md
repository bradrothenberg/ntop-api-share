# Setup

Run host Python through uv from the repository root. `uv sync --locked` installs pinned dependencies.
`scripts/bootstrap.ps1` sets NTOP_PYSCRIPTS to this checkout's harness/ for the current PowerShell session.
Pass -NTopExe or set NTOP_EXE to the matching licensed custom build. Start nTop from that session.
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
The other names are i6, i6-astra, jet20, b52, and ddgx.

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
