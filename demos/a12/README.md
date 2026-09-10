# A-12

R33 cockpit and continuous loft snapshot. The report preserves the R33 cockpit study, planform and side agreement, and the unresolved front-view target. It records an appearance reconstruction from public references. It does not establish production dimensions or aerodynamic performance.

[Primary HTML report](../../reports/A-12.html) | [Recorded lessons](LEARNINGS.md) | [Local agent](AGENTS.md)


## Native snapshots

- [A12_R33.ntop](models/A12_R33.ntop)

Run `scripts/prepare.py --models` from the repository root to create separate working copies under `.local/models/a12/models/`. Edit those copies and preserve the published snapshots.

## Replay the saved construction graph

From the repository root:

```powershell
uv run --locked python scripts/build.py a12
uv run --locked python scripts/stage.py a12
```

The first command copies and checks `inputs/recipe.json`. The second prepares an import script for an empty nTop notebook. The complete recipe contains the saved construction operations and controls. Edit that graph or the native controls to explore a new variant. The original reference-fitting and solver pipelines are not included in this replay.

Use the matching licensed Notebook API build for native execution. See [setup](../../docs/SETUP.md). Offline graph checks and saved results do not establish a new native evaluation.

Download the complete repository to view reports with their local assets. Reference photographs remain only in the separate downloadable collection.
