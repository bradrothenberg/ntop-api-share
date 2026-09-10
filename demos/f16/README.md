# F-16

R6 fair airfoils and finite trailing edges. The R6 report records revised aft-fuselage guides, finite trailing edges, and native section checks. Onshape and Fusion comparisons use the earlier nTop R3 baseline. Do not treat those comparisons as measurements of R6.

[Primary HTML report](../../reports/F-16.html) | [Recorded lessons](LEARNINGS.md) | [Local agent](AGENTS.md)

- [Onshape comparison](../../reports/F-16-Onshape-Comparison.html)
- [Fusion comparison](../../reports/F-16-Fusion-Comparison.html)

## Native snapshots

- [F16_Parametric.ntop](models/F16_Parametric.ntop)

Run `scripts/prepare.py --models` from the repository root to create separate working copies under `.local/models/f16/models/`. Edit those copies and preserve the published snapshots.

## Replay the saved construction graph

From the repository root:

```powershell
uv run --locked python scripts/build.py f16
uv run --locked python scripts/stage.py f16
```

The first command copies and checks `inputs/recipe.json`. The second prepares an import script for an empty nTop notebook. The complete recipe contains the saved construction operations and controls. Edit that graph or the native controls to explore a new variant. The original reference-fitting and solver pipelines are not included in this replay.

Use the matching licensed Notebook API build for native execution. See [setup](../../docs/SETUP.md). Offline graph checks and saved results do not establish a new native evaluation.

Download the complete repository to view reports with their local assets. Reference photographs remain only in the separate downloadable collection.
