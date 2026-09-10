# Verification and exports

A successful API call is not a verified graph.
Separate source topology, native readback, dimensions, meshes, and visual checks.

1. Inspect recipe connections, literals, units, and named dependencies.
2. Compare a native measurement with an independent equation or known input.
3. Perturb one control. Check the dependent output, restore, and check again.
4. Export a small subsystem before the full assembly.
5. Measure actual mesh bounds, connected regions, open edges, and bore openings.
6. Inspect native views and source-linked figures.

The measured meshing route uses Mesh from Implicit by AT with Remesh false,
then Sharpen Mesh against the same implicit source.
Its identifier is mesh_by_adaptive_tets<implicit,real_field,bool>[5.42.0].
The examples use one Sharpen iteration and enum 0.

Jet's coarse fuel-pipe export fragmented a thin wall into many closed regions.
Refinement restored one route with open bores. Watertightness alone missed the failure.

Native split/filter/merge removes measured numerical islands.
Filter thresholds are dimensional volumes.
Springs, impellers, fasteners, and guide vanes use different recorded thresholds.
Do not remove small geometry using one global threshold.

Rotated-body bounding boxes can be conservative.
A mesh block can report a complete box while its STL loses a thin feature.
Measure the exported file.

Repository checks establish copy fidelity, relocation, and offline generation.
Historical receipts preserve earlier native checks. They are not new nTop runs on this machine.

## Finite-edge and aerodynamic report evidence

The later Fury report separates native section thickness, raw surface topology, sharpened topology, and volume-mesh checks. A visually smoother edge can coexist with fragments or invalid cells. Preserve failed cases and measure the exported artifact at the requested tolerance.

The F-Cat aero report separates inviscid loading, section polars, viscous CFD, and conditional mission calculations. Read wall-resolution, prism, pressure-peak, convergence, and refinement findings before using a coefficient. Geometry replay does not rerun those studies.

The [report catalogue](../reports/index.html) retains these distinctions. The public edition removes reference photos and large outputs but preserves source credits, compact measurements, and unresolved findings.
