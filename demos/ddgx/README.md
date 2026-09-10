# DDGX concept

A normalized public-concept exterior with a native hull loft, superstructure, and editable display features. Dimensions are inferred.

[HTML report](reports/index.html) · [Recorded lessons](LEARNINGS.md) · [Local agent](AGENTS.md)

## Native models

- [DDGX_Concept.ntop](models/DDGX_Concept.ntop)

Use prepared working copies under `.local/models/ddgx/` when a notebook has export paths.

## Rebuild

From the repository root:

```powershell
uv run --locked python scripts/build.py ddgx
uv run --locked python scripts/stage.py ddgx
```

The first command creates and checks a complete recipe. The second also writes an import script.
Run that script only in an empty, task-owned nTop Python Console. Inspect native readback before accepting the result.
The matching licensed custom build is an external prerequisite. See [setup](../../docs/SETUP.md).

Source code is in scripts/, required data is in inputs/, and generated work is in output/.
The report records earlier native observations. Offline reconstruction does not establish a new native verification.
