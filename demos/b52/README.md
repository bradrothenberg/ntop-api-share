# B52 fuselage

The R7 fair nose blend and accepted cockpit loft. Geometry is derived from a GPL-2.0 artist model, not production aircraft data.

[HTML report](reports/index.html) Â· [Recorded lessons](LEARNINGS.md) Â· [Local agent](AGENTS.md)

## Native models

- [B52F_Fair_Nose_Blend.ntop](models/B52F_Fair_Nose_Blend.ntop)

Use prepared working copies under `.local/models/b52/` when a notebook has export paths.

## Rebuild

From the repository root:

```powershell
uv run --locked python scripts/build.py b52
uv run --locked python scripts/stage.py b52
```

The first command creates and checks a complete recipe. The second also writes an import script.
Run that script only in an empty, task-owned nTop Python Console. Inspect native readback before accepting the result.
The matching licensed custom build is an external prerequisite. See [setup](../../docs/SETUP.md).

Source code is in scripts/, required data is in inputs/, and generated work is in output/.
The report records earlier native observations. Offline reconstruction does not establish a new native verification.

This demo and its upstream artist model are [GPL-2.0](LICENSE). The upstream source and authors are documented in [upstream/README.md](upstream/README.md).

## Earlier loft studies

[R2](../../reports/B52-R2-Loft-Study.html) | [R3](../../reports/B52-R3-Loft-Study.html) | [R4](../../reports/B52-R4-Loft-Study.html) | [R5](../../reports/B52-R5-Loft-Study.html) | [R6](../../reports/B52-R6-Loft-Study.html)

[Historical editable source](history-source/README.md) preserves the corresponding saved graphs and guide data under GPL-2.0. The primary demo remains R7.
