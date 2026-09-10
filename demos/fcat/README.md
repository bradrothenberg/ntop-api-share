# F-Cat

Continuous tail and cargo-pod geometry. The geometry report covers the continuous bent tail, pod fairing, chine, wheels, and wing sections. The separate aero report retains AVL, XFoil, CFD, mesh-resolution concerns, and conditional range calculations. A saved native model does not reproduce those solver studies.

[Primary HTML report](../../reports/F-Cat-Engineering.html) | [Recorded lessons](LEARNINGS.md) | [Local agent](AGENTS.md)

- [Aerodynamic study](../../reports/F-Cat-Aero.html)

## Native snapshots

- [F-Cat_Parametric.ntop](models/F-Cat_Parametric.ntop)
- [F-Cat_Meshing.ntop](models/F-Cat_Meshing.ntop): separate meshing snapshot with portable export destinations.

Run `scripts/prepare.py --models` from the repository root to create separate working copies under `.local/models/fcat/models/`. Edit those copies and preserve the published snapshots.

## Replay the saved construction graph

From the repository root:

```powershell
uv run --locked python scripts/build.py fcat
uv run --locked python scripts/stage.py fcat
```

The first command copies and checks `inputs/recipe.json`. The second prepares an import script for an empty nTop notebook. The complete recipe contains the saved construction operations and controls. Edit that graph or the native controls to explore a new variant. The original reference-fitting and solver pipelines are not included in this replay.

Use the matching licensed Notebook API build for native execution. See [setup](../../docs/SETUP.md). Offline graph checks and saved results do not establish a new native evaluation.

Download the complete repository to view reports with their local assets. Reference photographs remain only in the separate downloadable collection.
