# I6 Astra

A native assembly with involute gears, nominal fasteners, belts, spline routes, and mechanism checks.

[HTML report](reports/index.html) Â· [Recorded lessons](LEARNINGS.md) Â· [Local agent](AGENTS.md)

## Native models

- [I6_Astra.ntop](models/I6_Astra.ntop)
- [I6_Astra_Inspection.ntop](models/I6_Astra_Inspection.ntop)

Use prepared working copies under `.local/models/i6-astra/` when a notebook has export paths.

## Rebuild

From the repository root:

```powershell
uv run --locked python scripts/build.py i6-astra
uv run --locked python scripts/stage.py i6-astra
```

The first command creates and checks a complete recipe. The second also writes an import script.
Run that script only in an empty, task-owned nTop Python Console. Inspect native readback before accepting the result.
The matching licensed custom build is an external prerequisite. See [setup](../../docs/SETUP.md).

Source code is in scripts/, required data is in inputs/, and generated work is in output/.
The report records earlier native observations. Offline reconstruction does not establish a new native verification.

## Full reference collection

[Complete reference report](../../reports/I6-Astra-Reference.html) includes configuration tables, assembly details, mechanism checks, and the 100-design family. [Summary report](../../reports/I6-Astra.html) provides a shorter introduction. Movies and animated previews remain in the separate downloadable collection.
