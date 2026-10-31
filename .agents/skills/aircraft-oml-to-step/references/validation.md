# Validation and delivery evidence

Keep topology, design intent and source fidelity as separate results.
A closed, valid STEP can still contain a large lump or a bad wingtip.

## STEP readback

Use the delivered STEP, not only the in-memory BREP. Check expected roots/bodies,
validity, closed shell flags, unmatched or nonmanifold edges, loose faces, topology
tolerances and the kernel's self-intersection result. Record the STEP hash.

`scripts/audit_step.py` imports STEP in millimeters and reports unique topology,
shell flags, nondegenerate edge uses, loose vertices, adaptive closed-solid volume, bounds,
maximum topology tolerances and the kernel check. It returns nonzero for failed
explicit requirements, an invalid shape, or a failed kernel check. A skipped
kernel check is recorded as skipped. A topology pass does not certify appearance,
source fit, edge thickness, symmetry, manifold geometry under every downstream
kernel, or an aircraft design's suitability.

Run with the project's pinned dependency environment where possible:

    uv run python "<skill>/scripts/audit_step.py" "<file.step>" --output "<audit.json>" --expected-solids 1 --require-closed

`--max-topology-tolerance-mm` is optional. Supply a project-specific acceptance
limit when one exists. Sewing/healing tolerances are not source-fit tolerances.
`--skip-kernel` is for a quick pilot, not final release evidence.

## Design checks

Measure actual trimmed edges and faces after STEP readback:

- Straight segments: distance to the specified design line, with endpoints and
  parameter coverage recorded. Do not merely fit a new line to the wrong edge.
- Thickness: upper/lower or left/right separation at corresponding stations in
  the specified measurement direction. Check the transition into each cap.
- Symmetry: reflected surface and boundary geometry, body counts, matching face
  domains and any explicitly asymmetric exceptions.
- Smooth joins: both sides of a shared edge, sampled through their pcurves, plus
  positional residual. Skip intentional sharp edges. Report G1 tangent checks
  separately from any G2 curvature check.
- Closeouts: both adjacent surfaces share the intended edge; no residual shelf,
  gap, overlap, collapsed cap or unintended local protrusion remains.
- Fairness: section thickness/camber, cross-sections near tips and blends,
  derivative/curvature trends and shaded inspection. Use geometric evidence
  before deciding whether a highlight is a shape defect or coarse tessellation.

Render views with and without CAD edges. Inspect an overall plan view, a side
silhouette and local close-ups of the changed regions. Do not infer shape quality
from a single isometric image. A tessellated preview is inspection evidence,
not the geometry delivered in the STEP.

## Fit and reproducibility

Keep the paired CAD/source points and the measurement method. Report regional
and global statistics, failed projections, field residuals, sampling density and
known limitations. Read `source-measurement.md` before generating these data.

At an implicit union corner, a fixed normal ray can miss a nearby zero even when
both ray ends have the same sign. Search bounded coordinate rays or refine local
sign intervals. Keep the unresolved witness until a fresh native query confirms
the proposed root. Preserve the bracket, residual, source hash, and search method.

If a STEP writer omits a semantic face name, do not recover it from list order.
Use a unique geometric correspondence. A metadata-only probe can temporarily
name blank entities, reopen them, and match exact face fingerprints to the prior
readback. Prove that only name bytes changed. Keep name recovery separate from
orientation repair and from geometry acceptance.
`compare_points.py` summarizes pairs; it neither locates nor verifies the source.

Rebuild from the packaged inputs in a separate directory. Compare topology and
geometry to the validated candidate. An identical BREP hash is useful when
serialization is deterministic. If bytes differ, measure geometry; do not claim
equivalence from matching face counts and volume alone. STEP timestamps can
change a file hash without changing the geometry.

Deliver the new STEP and concise notes. Include changes, measured checks, useful
views, units, source provenance, dependencies and rebuild inputs. Name the worst
retained approximation and avoid hiding it behind a favorable median.

## Helper regression checks

Run `scripts/smoke_test.py` with `uv run --with cadquery-ocp --with numpy python`.
It uses temporary synthetic geometry and known point pairs. It checks a box,
a cylinder seam, an open face, solids with loose edges or vertices, region statistics and
nonfinite source projections. These tests do not replace aircraft validation.

## Explicit smooth-join plans

`audit_surface_contract.py` inventories actual stored surface, edge, and pcurve
types. It recognizes analytic types and nested spline supports. A surface-degree
limit does not also limit boundary curves. Supply `--max-curve-degree` separately
when the contract requires it. The helper does not detect analytic reducibility.

For a smooth-join check, pass `--joins` with a JSON file such as:

```json
{
  "step_sha256": "SHA-256 of the actual file being checked",
  "joins": [{
    "name": "lip to hood",
    "left": {"face": 0, "edge": 1},
    "right": {"face": 2, "edge": 3}
  }]
}
```

Indices are zero-based actual face and local-edge indices. The values illustrate
the schema; discover the indices from the current file. Optional per-join limits
are `max_position_mm`, `max_tangent_deg`, and `max_oriented_normal_deg`. Use the
project's acceptance values. Intentional sharp edges are not smooth-join entries.

The helper samples both directions with bounded projection. It reports edge-to-
support discrepancy, position gap, tangent-plane angle, and oriented-normal angle.
The last two are different: tangent planes can agree while normals are reversed.
This is a finite sampled check, not proof of G2 or a continuous maximum.

Keep source-fit evidence private to the project. Public skill tests must use
synthetic geometry and synthetic point pairs, with no customer data or identifiers.
