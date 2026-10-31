---
name: aircraft-oml-to-step
description: Reconstruct aircraft outer mold lines as smooth, low-degree STEP surfaces from nTop construction logic and measured implicit geometry. Use for new CAD skins, inlet lips, wing panels, symmetry, and tangent joins. This is not a direct export of existing CAD.
---

# Aircraft OML to STEP

Build new analytic or constrained spline supports from the source design and
measurements. Use nTop to inspect and query the implicit. A mesh can supply
measurements; its triangles are not the delivered CAD faces.

## Establish the contract

Read the project instructions and preserve the source and previous revisions.
Record axes, units, selected native output, component identities, intended sharp
edges, smooth joins, symmetry, and required output type. A surface assembly and
a watertight solid have different acceptance conditions.

Record the requested fit tolerance and its measurement definition. If none is
specified, report measured deviations without inventing an acceptance threshold.
Separate approximation error from an intentional change that improves fairness.

Prefer analytic surfaces where they express the measured design. Start freeform
supports with cubic splines. Use quartic splines when needed for compatible
boundary constraints. Keep supports at degree four or below unless the user
sets another contract. Boundary and trim curve degree limits are separate.

For reconstruction, generate new supports. Reference CAD can explain a useful
face layout when authorized. Do not copy its surfaces, poles, or hidden payloads
into a reconstruction that must come from the implicit.

## Measure the source

Read [source-measurement.md](references/source-measurement.md). Trace profiles,
rails, transforms, blends, passages, and clipping operations upstream of the
final body. Query important components separately when a union hides their roles.

Honor command-only and no-computer-use constraints. Use a verified API bridge,
saved-file query, or command-line runtime. Keyboard shortcuts still control the
application. For live API work, consult the available `ntop-notebook-api` skill
and verify the intended process before editing. Do not replace unrelated work.

Keep native query receipts, source hashes, units, and failures in the private
project workspace. Cache results only when all geometry and query inputs match.
An unknown or timed-out run is not a successful query.

## Construct fair surfaces

Read [cad-construction.md](references/cad-construction.md) for edges, tips,
blends, physical tangent transfer, and analytic recovery. Read
[fair-surface-workflow.md](references/fair-surface-workflow.md) for inlet bands,
constraint feasibility, periodic seams, and finite trim ownership.

Prove a small difficult junction before scaling the pipeline. Choose a regular
physical chart and confirm section order, branch identity, and finite normals.
Do not force a height chart across a return or overhang.

Solve shared position and tangent data together. Matching boundary normals alone
does not establish a fair interior. Integrate fairness penalties in every knot
span. Inspect sections and highlights in both surface directions.

Give the inlet lip a finite band with useful boundaries. Join it to the hood,
passage, and surrounding skin. If a narrow patch has incompatible rails, revise
the common construction or partition before adding poles or local blends.

Build fair supports before adding semantic splits. Keep wings, control surfaces,
glazing, lips, and passages identifiable. For a symmetric design, construct and
split one half, then mirror the complete geometry and face layout.

## Verify the actual STEP

Read [validation.md](references/validation.md). Reopen each exported file and
check topology, design geometry, source fit, and appearance separately.

```powershell
uv run --with cadquery-ocp python "<skill>/scripts/audit_step.py" "<model.step>" --output "<topology.json>"
uv run --with cadquery-ocp python "<skill>/scripts/audit_surface_contract.py" "<model.step>" --max-degree 4 --output "<surfaces.json>"
uv run --with numpy python "<skill>/scripts/compare_points.py" "<paired-points.csv>" --output "<fit.json>"
```

Use the task's pinned environment when available. The scripts inspect stored
geometry or summarize supplied measurements. They do not reconstruct a model,
discover every neighbor, prove global fairness, or certify closest distances.

Check actual pcurves, finite domains, physical normals, and shared boundaries.
Keep raw kernel warnings and resolve their retained-domain meaning. Do not call
an unexamined warning harmless or a skipped check a pass.

Compare the implicit and CAD in identical physical section planes. Inspect
plain shaded views and views with actual CAD edges. Include the full repaired
neighborhood, not only the original marked corner.

## Deliver and share

Deliver versioned STEP files, useful views, measured limits, and portable rebuild
inputs. Test the packaged command in a separate output directory. Distinguish a
cached configuration rebuild from a general converter for a changed implicit.

Keep source-fit distances, field residuals, seam gaps, and intentional design
changes distinct. Report unresolved projections and the worst sampled regions.
This workflow does not establish aerodynamic performance or structural strength.

For public reuse, share generic instructions and synthetic test code only.
Exclude customer names, models, measurements, source hashes, paths, images,
logs, identifiers, and case narratives. Keep private evidence with its project.
Audit an explicit publication file list before pushing it.
