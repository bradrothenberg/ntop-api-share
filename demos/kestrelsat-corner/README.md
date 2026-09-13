# KestrelSAT corner: native CSG versus STEP

This example rebuilds one corner block from the original STEP with continuous native nTop geometry.
It includes one editable `.ntop` part, the extracted source STEP solid, complete source recipes, and recorded accuracy evidence.

[Open the comparison report](reports/index.html).
The report includes matched host views of the original STEP tessellation and the actual recorded native mesh.
Select the recess view or the negative-X view of a rounded pocket and bore.
A separate recorded native nTop image shows the implicit body.
A [description-only portability edit](evidence/native-portability.json) preserves its complete native geometry, camera, and display state.

## Open the example

- [Modeled corner notebook](models/Corner_block.ntop)
- [Original STEP corner](inputs/Corner_block_source.step)
- [Shared CSG modeling skill](../../.agents/skills/ntop-csg-modeling/SKILL.md)
- [Measured CSG feature tree](inputs/corner.csg.json)
- [Complete native recipe](inputs/corner.recipe.json)
- [Separate mesh validation recipe](inputs/mesh.recipe.json)

The recorded native build is **nTop 6.0.0-rc build 42594**.
The model output is a native implicit body. Construction is saved collapsed.
This fixed corner has **no exposed notebook inputs**. It does not provide assembly resizing.
The example contains no assembly model.

The part spans 22 x 22 x 22 mm and remains in the original STEP world coordinate frame.
The extracted source is solid 0 from the original 28-solid assembly. It has no new placement transform.
Read [the source extraction and reimport audit](evidence/source-extraction.json).

## Construction

The feature tree contains 24 solid features: seven boxes, eight plane half-spaces, six cylinders, and three hexagonal recess profiles.
Boolean operations combine these features. The three profile extrusions form real recesses.
They replace an earlier rejected construction with 106 thin slice extrusions; continuous plane cuts now form the slopes.

The full native output does not import the STEP or a mesh as its geometry source.
The STEP is the comparison reference. Meshing remains in the separate validation recipe.

## Recorded result

| Measure | Recorded value |
|---|---:|
| Volume intersection-over-union | 99.973930% |
| STEP to native sampled maximum | 0.0464267 mm |
| Native to STEP sampled maximum | 0.0221227 mm |
| Missing material | 1.170529 mm³ |
| Excess material | 0.619736 mm³ |

The source comparison uses 0.005 mm STEP tessellation deflection.
The actual native mesh uses AT at 0.05 mm, Remesh enabled, then one Sharpen iteration.
Both compared meshes are closed. Sampled surface extrema are not certified Hausdorff bounds.

- [Complete recorded values and scope](evidence/validation.json)
- [Native expression, source, mesh and settings binding](evidence/geometry-binding.json)
- [Image provenance, camera and hashes](reports/assets/provenance.json)
- [New host comparison with the included extracted STEP](evidence/reference-recheck.json)

These are recorded native results, not a new native run in this checkout.
The new comparison images are host renders with identical camera, scale, lighting, and material.
The original native capture records no elapsed time or process exit code, so it supports no timing claim.
Live Notebook API import and live GUI update timing remain unverified for this handoff.

## Files and generated work

Keep `reports/index.html` beside `reports/assets/` for offline viewing.
Raw STL files, regenerated outputs, browser captures, and solver data belong in ignored `output/`.
No raw meshes or embedded mesh payloads are included in the report.

## Replay and verify

Run each command from the repository root.
The build and stage steps replay the saved native graph. They do not rerun the original feature measurement or fitting.

```powershell
uv run --locked python scripts/build.py kestrelsat-corner
uv run --locked python scripts/stage.py kestrelsat-corner
```

Follow the staging instructions to import the generated recipe through a separate, authorized nTop session.
Do not use an existing user-controlled session for automated testing.

Prepare the separate meshing recipe when a fresh native comparison is required:

```powershell
uv run --locked python demos/kestrelsat-corner/scripts/replay.py --mesh
```

This writes `output/mesh/import_model.py`. The staged native run targets `output/native.stl`.
After nTop has completed the export, compare that actual mesh with the included STEP:

```powershell
uv run --script demos/kestrelsat-corner/scripts/verify.py --native demos/kestrelsat-corner/output/native.stl
```

The verification script pins its CAD and mesh dependencies through PEP 723 metadata.
Check the included files and graph without starting nTop:

```powershell
uv run --locked python demos/kestrelsat-corner/scripts/check_example.py
```

Offline checks and saved graph replay do not establish a new native geometry pass.
