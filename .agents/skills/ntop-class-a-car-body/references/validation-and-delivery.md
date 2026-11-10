# Validation and delivery

Use separate acceptance records for source fidelity, surface quality, native realization, and display quality.
Do not reduce them to one percentage.

## Frozen silhouette comparison

Preserve the source image, independent mask, trace, and mask rules with hashes.
Record whether dark wheel recesses count as foreground. Keep uncertainty pixels in the stated nominal metric unless the original contract says otherwise.
Do not change mask semantics or omit difficult regions after seeing a candidate.

For the final saved native render, compute:

```text
IoU = intersection(reference_mask, native_mask) / union(reference_mask, native_mask)
missing = reference_mask minus native_mask
excess = native_mask minus reference_mask
```

Record raw counts, image resolution, foreground extraction method, camera, and any exact sensor crop.
The case uses native alpha >= 128. An opaque RGB threshold is not interchangeable with it; validate any alternative extraction.
Do not count construction bodies, floors, shadows, or a viewer background as the car.
Do not apply image registration, nonuniform scaling, contour morphing, or warping before acceptance.
Report local arch and landmark errors separately, in pixels at the recorded resolution.

Use a calibrated mathematical projection to select candidates, then rerender and measure the actual saved native result.
Changing geometry or camera invalidates the previous silhouette receipt.
A layout-only change can retain it only after geometry and camera equivalence are proved.
See compare_native.py (source-project artifact; not bundled).
Its 0.99 target and source paths are case-specific; inspect before applying to another project.

## Surface quality acceptance

Record tolerances and scope before claiming a quality pass. Missing criteria mean acceptance remains open.
These are the inspection categories for this workflow, not numerical Class A standards:

| Category | Evidence to obtain | Limit on the claim |
|---|---|---|
| Position and seams | Gaps and trim consistency at all joins, including mirror seam | A smooth formula does not prove joined boundaries agree |
| Tangency and curvature | Normals, curvature behavior, combs or equivalent diagnostics across joins | Cubic degree and interior C2 spans do not qualify caps or trimmed joins |
| Reflection fairness | Native zebra and shaded views under recorded camera and stripe settings | A pleasing single view can hide local ripples |
| Field regularity | Composite gradient and finite curvature throughout sampled retained regions | Sampled minima do not establish global nonzero gradient |
| Shell geometry | Normal crossings, minimum-thickness search, cavity and opening sections | Field depth is not physical thickness; sampled minimum is not global minimum |
| Topology and intersections | Connected components and explicit surface/offset intersection checks | Basic manifold tests do not prove self-intersection freedom |
| Display fidelity | Source-to-mesh deviation, exported bounds, visible edge quality | A clean preview does not establish manufacturing surface quality |

Inspect the hood, roof, flanks, crowns, wheel lips, underside, and mirror seam.
For numerical curvature, compare more than one differentiation step and report sensitivity.
Compare fairness metrics on identical grids and domains. Identify all excluded caps, trims, offsets, and joins.
Record unsuccessful or excluded witnesses and their reasons; do not count them as passes.

If the supplied source is one photograph, separate image agreement from design choices in unseen regions.
Do not claim those surfaces match an unknown original vehicle.
If a downstream CAD surface format is required, verify that deliverable independently. A native implicit model does not imply a qualified patch network.

## Delivery receipt

Keep a compact manifest with:

- Source image or CAD hash, reference-mask hash, coordinate frame, and units.
- Selected controls, native recipe, output body, native notebook hash, and geometry fingerprint.
- nTop build, native states, independent field witnesses, tolerances, exclusions, and results.
- Native render settings, camera, extraction rule, image and crop hashes, overlap counts, and local feature errors.
- Surface and thickness diagnostics with sample domain, resolution, steps, and unresolved acceptance criteria.
- Mesh settings and source hash if a display mesh exists; explicit failure or cancellation if it does not.
- Presentation checks: sections, collapsed blocks, expanded root, visibility, and unchanged geometry.
- Separate status fields for silhouette target, native checks, display completeness, and Class A acceptance.

Retain the previous delivered revision. Do not transfer its score to a new body.
Deliver native previews with links to the editable model and short quality notes.
Use package_shell.py (source-project artifact; not bundled) as a local example of evidence binding.
It has case-specific paths and assertions; do not run it as a generic packager without inspection.
