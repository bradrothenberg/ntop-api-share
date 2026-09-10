# Original inline-six

An API recorder, slider-crank mechanism, cam motion, and analytic helical springs.

[HTML report](reports/index.html) · [Recorded lessons](LEARNINGS.md) · [Local agent](AGENTS.md)

## Native models

- [I6_Engine.ntop](models/I6_Engine.ntop)

Use prepared working copies under `.local/models/i6/` when a notebook has export paths.

## Rebuild

From the repository root:

```powershell
uv run --locked python scripts/build.py i6
uv run --locked python scripts/stage.py i6
```

The first command creates and checks a complete recipe. The second also writes an import script.
Run that script only in an empty, task-owned nTop Python Console. Inspect native readback before accepting the result.
The matching licensed custom build is an external prerequisite. See [setup](../../docs/SETUP.md).

Source code is in scripts/, required data is in inputs/, and generated work is in output/.
The report records earlier native observations. Offline reconstruction does not establish a new native verification.
