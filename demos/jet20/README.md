# 20 lbf jet

A native compressor, combustor, turbine, housing joints, fasteners, and service routes. The 20 lbf value is a conditional sizing target.

[HTML report](reports/index.html) · [Recorded lessons](LEARNINGS.md) · [Local agent](AGENTS.md)

## Native models

- [Jet20.ntop](models/Jet20.ntop)
- [Jet20_Inspection.ntop](models/Jet20_Inspection.ntop)
- [Jet20_Assembled.ntop](models/Jet20_Assembled.ntop)
- [Jet20_Exploded_Implicits.ntop](models/Jet20_Exploded_Implicits.ntop)

Use prepared working copies under `.local/models/jet20/` when a notebook has export paths.

## Rebuild

From the repository root:

```powershell
uv run --locked python scripts/build.py jet20
uv run --locked python scripts/stage.py jet20
```

The first command creates and checks a complete recipe. The second also writes an import script.
Run that script only in an empty, task-owned nTop Python Console. Inspect native readback before accepting the result.
The matching licensed custom build is an external prerequisite. See [setup](../../docs/SETUP.md).

Source code is in scripts/, required data is in inputs/, and generated work is in output/.
The report records earlier native observations. Offline reconstruction does not establish a new native verification.

[Native nTop assembled and exploded screenshots](screenshots/README.md). These later presentation snapshots are included in models/.
