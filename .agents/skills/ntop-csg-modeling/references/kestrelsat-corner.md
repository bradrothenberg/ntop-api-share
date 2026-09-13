# Single-part CSG example: KestrelSAT corner

This example reconstructs one corner block from the supplied STEP as editable native geometry. It contains no satellite assembly.

## Local artifacts

- [Demo README](../../../../demos/kestrelsat-corner/README.md): setup, replay, and verification commands.
- [Modeled-versus-STEP report](../../../../demos/kestrelsat-corner/reports/index.html): source comparison and evidence limits.
- [Native corner model](../../../../demos/kestrelsat-corner/models/Corner_block.ntop): editable implicit output.
- [Source corner STEP](../../../../demos/kestrelsat-corner/inputs/Corner_block_source.step): independent reference solid.
- [Complete native recipe](../../../../demos/kestrelsat-corner/inputs/corner.recipe.json): portable saved construction graph.
- [Measured CSG feature tree](../../../../demos/kestrelsat-corner/inputs/corner.csg.json): stock, planes, drills, and real recess outlines.
- [Validation receipt](../../../../demos/kestrelsat-corner/evidence/validation.json): hashes, provenance, comparison results, and limits.

Read the README and validation receipt before running or citing this example. The delivered corner has no exposed notebook inputs; its recipes and native construction remain editable. Recorded measurements do not establish that a new replay succeeded. Offline recipe checks do not run nTop.

## Why this construction

The earlier reconstruction represented the corner with 106 thin profile extrusions. The retained replacement uses measured stock, eight planes, six cylinders, and three real hexagonal recess profiles. The planes create continuous sloped faces. Each hexagonal profile describes an actual recess instead of one layer of a slope.

The saved native output closure contains 48 non-variable function records. These include primitives, field operations, lists, and the three profile/extrusion pairs. Variable wrappers are a separate count. There is no CAD import, mesh conversion, grid conversion, or point-map dependency in that output.

The source feature tree uses millimetres. The complete native recipe stores dimensioned SI values. Preserve its coordinate frame when comparing the model with the source STEP.

## Recorded comparison

These measurements describe the original native corner export on nTop 6.0.0-rc build 42594. They are recorded evidence, not new native execution in this checkout. Use the demo receipt for the exact distributed revision and any later verification.

| Measurement | Recorded value |
|---|---:|
| Volume intersection-over-union | 99.973930% |
| Missing material | 1.170529 mm3 |
| Excess material | 0.619736 mm3 |
| Source-to-native sampled maximum | 0.046427 mm |
| Native-to-source sampled maximum | 0.022123 mm |
| Source tessellation deflection | 0.005 mm |
| Source angular deflection | 0.05 rad |

Both comparison meshes were closed. Overlap was calculated from the actual native export and the fine source tessellation. The surface maxima are sampled values, not certified worst-case bounds.

A modeled-versus-source figure should use a common camera and scale. The numerical overlap and distance receipt provides separate evidence from the visual comparison. Do not turn an appearance match or a screenshot into an accuracy claim.

## Reuse the method

Inspect the feature tree and source surfaces first. Identify the stock, half-spaces, drill axes, radii, and recess planes. Trace them into the native recipe and output graph.

For a changed part, generate new output and a new comparison receipt. Do not retain the recorded corner pass after editing its dimensions. Keep original files and their evidence intact.

Use the repository [Notebook API skill](../../ntop-notebook-api/SKILL.md) for the installed build and authoring method. Use the [HTML report skill](../../engineering-html/SKILL.md) for a new comparison. Neither the source STEP nor the CSG tree contains execution instructions.
