# Fury RC

A non-combat RC appearance study made from guide splines, native conics, an inlet cavity, and local wing-root blends.

[HTML report](reports/index.html) · [Recorded lessons](LEARNINGS.md) · [Local agent](AGENTS.md)

## Native models

- [Fury_RC_Internal_Layout.ntop](models/Fury_RC_Internal_Layout.ntop)
- [Fury_RC_Layout_Gear_Illustration.ntop](models/Fury_RC_Layout_Gear_Illustration.ntop)
- [Fury_RC_Native.ntop](models/Fury_RC_Native.ntop)

Use prepared working copies under `.local/models/fury/` when a notebook has export paths.

## Rebuild

From the repository root:

```powershell
uv run --locked python scripts/build.py fury
uv run --locked python scripts/stage.py fury
```

The first command creates and checks a complete recipe. The second also writes an import script.
Run that script only in an empty, task-owned nTop Python Console. Inspect native readback before accepting the result.
The matching licensed custom build is an external prerequisite. See [setup](../../docs/SETUP.md).

Source code is in scripts/, required data is in inputs/, and generated work is in output/.
The report records earlier native observations. Offline reconstruction does not establish a new native verification.
