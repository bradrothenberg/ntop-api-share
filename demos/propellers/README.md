# Propeller and two-rail blade studies

An eight-inch propeller, separate retained spinner, ten original blade forms, and ten airfoil candidates.
The folder contains 22 complete construction recipes, two native assembly notebooks, recorded measurements, and native nTop screenshots.
The large cached blade notebooks and mesh exports can be regenerated locally from the recipes.

[Open the shared report](reports/index.html) | [Case manifest](manifest.json) | [Lessons](LEARNINGS.md) | [CFD plan](CFD_PLAN.md)

## What is included

- `models/assembly.ntop`: propeller, motor reference, separate spinner, and nominal retention hardware.
- `models/spinner.ntop`: separate spinner notebook.
- `inputs/assembly.json` and `inputs/spinner.json`: complete saved construction recipes.
- `inputs/elliptical_*.json`: the ten original shape studies, including corrected three-petal and folded-loop tips.
- `inputs/airfoil_*.json`: the ten later airfoil candidates. Modified Mobius sections are explicitly labeled.
- `evidence/`: selected recorded measurements, source identities, and public dimension references.
- `reports/`: the offline gallery and native screenshot assets. No supplied reference photos are bundled.
- `scripts/replay.py`: portable recipe staging with an empty-notebook guard.

## Use a blade study

From the repository root:

```powershell
uv run --locked python demos/propellers/scripts/replay.py --case airfoil_07_three_petal
```

Read the generated import script under `demos/propellers/output/airfoil_07_three_petal/`.
Dispatch it to an empty, task-owned nTop build 42926 notebook using the root background or TCP helper.
No current notebook is cleared automatically. The script saves `Model-working.ntop` and a recipe readback locally.
Exports can take minutes for complex loops. Wait for the dispatch receipt before opening files or retrying.

After the save completes, prepare a separate collapsed deliverable:

```powershell
uv run --locked python scripts/collapse_saved_notebook.py demos/propellers/output/airfoil_07_three_petal/Model-working.ntop -o demos/propellers/output/airfoil_07_three_petal/Model.ntop
```

Replay preserves the native construction graph. It does not preserve the original viewport arrangement or repeat the source measurements.
Use the root setup to prepare the two tracked native snapshots into separate `.local/models/propellers/models/` working copies.
Do not open a tracked snapshot directly: its portable `repo://` export paths must be resolved first.

## Evidence limits

The source models were evaluated in nTop build 42926. The public packaging checks are offline and do not constitute another native run.
The original section studies are shape experiments. The NACA candidates are not accepted aerodynamic optima.
The CFD pilot established solver startup and rotating-wall velocity. It did not establish converged performance, wake animations, or noise.
The nominal retention geometry is not a released manufacturing drawing or a safe-speed qualification.
