# Fury RC

A non-combat RC appearance study made from guide splines, native conics, an inlet cavity, and local wing-root blends.

[HTML report](reports/index.html) Â· [Recorded lessons](LEARNINGS.md) Â· [Local agent](AGENTS.md)

## Current finite-edge snapshot

Start with [Fury_RC_TE_0p5in.ntop](models/Fury_RC_TE_0p5in.ntop). This is the saved revision with 0.5 inch full trailing-edge thickness on the wing, horizontal tail, and fin. It addresses the earlier knife edges. Meshing and export operations remain paused.

[Finite-edge and mesh report](../../reports/Fury-RC.html) | [Earlier surface report](../../reports/Fury-RC-Earlier-Surface.html) | [Alternatives](../../reports/Fury-Alternatives.html) | [CFD readiness](../../reports/Fury-CFD-Readiness.html)

Smooth native edges do not establish a valid CFD mesh. The report retains mesh defects and failed checks. Use a prepared working copy to inspect or change the model.

## Earlier native models

- [Fury_RC_Internal_Layout.ntop](models/Fury_RC_Internal_Layout.ntop)
- [Fury_RC_Layout_Gear_Illustration.ntop](models/Fury_RC_Layout_Gear_Illustration.ntop)
- [Fury_RC_Native.ntop](models/Fury_RC_Native.ntop)

Use prepared working copies under `.local/models/fury/` when a notebook has export paths.

## Rebuild the earlier appearance baseline

From the repository root:

```powershell
uv run --locked python scripts/build.py fury
uv run --locked python scripts/stage.py fury
```

These commands reconstruct the earlier appearance baseline, not the finite-edge snapshot. The first command creates and checks a complete recipe. The second also writes an import script.
Run that script only in an empty, task-owned nTop Python Console. Inspect native readback before accepting the result.
The matching licensed custom build is an external prerequisite. See [setup](../../docs/SETUP.md).

Source code is in scripts/, required data is in inputs/, and generated work is in output/.
The report records earlier native observations. Offline reconstruction does not establish a new native verification.
