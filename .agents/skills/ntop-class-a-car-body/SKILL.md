---
name: ntop-class-a-car-body
description: Build and refine editable car bodies and hollow shells in nTop with the Notebook API. Use for photo-based car reconstruction, silhouette fitting, surface fairing, wheel openings, and Class A surface-quality work. Keep measured silhouette agreement separate from continuity and reflection acceptance.
---

# Class A car body construction in nTop

Build a continuous, editable native body with fair surfaces and a documented quality result.
Class A is an acceptance target. The recorded CarShell example is not a completed Class A result.

Use the installed `ntop-notebook-api` skill for the current authoring transport and block catalog.
This skill adds car geometry, fitting, shell, and verification decisions.
Read the [measured case](references/measured-case.md) when continuing CarSurface or reusing its tools.

## Establish the model and acceptance contract

Read the task's existing specification and evidence before asking questions. Reuse answers already supplied.
Record these items in the project specification as they become known:

- Source images or CAD, their hashes, coordinate frame, and measured dimensions.
- Required editable output: exterior body, hollow shell, or a particular CAD surface format.
- Fidelity metric, reference view, wheel-opening semantics, and local feature limits.
- Surface acceptance: position, tangent, curvature, and reflection criteria, with units and inspection conditions.
- Known dimensions, unresolved dimensions, and design choices for unseen surfaces.

Ask only for missing information that changes the next work. Continue independent modeling when possible.
In the recorded case, 99% meant silhouette overlap in the supplied view. Define the metric for each new task.
Use normalized design length when no physical dimension exists; label it explicitly.
Do not infer a production wall thickness or vehicle size from a single photograph.
An implicit body or display mesh does not by itself satisfy a requested CAD patch-surface deliverable.

Freeze the reference mask before fitting. Trace the outer body and wheel lips independently of the candidate.
Record how recesses, occlusions, and uncertain dark pixels count. Keep those rules fixed for all candidates.
Zebra bands in this reference are reflections, not edges to reproduce as ribs or panel seams.

## Construct and fair the shape

Read [modeling and fitting](references/modeling-and-fitting.md) for the measured field construction and sensitivity method.

Choose the surface architecture before fitting. One control net fitted through many traced keys can
match every silhouette and still ripple in reflections. A later body built that way showed dimples
where control rows converged and a pinched ridge up the rear pillar, and parameter repair did not cure it.
The repair was a rebuild from a few primary surfaces, each lofted in the plane where it is simple,
with guides of few control values and seams of chosen width. Use the `ntop-surfacing` skill for that
method, its zebra and section-curvature checks, and its native Spline DF pilot. Run the zebra check on
the bare envelope before fitting details or scoring the silhouette.

Start with a small native pilot of the longitudinal guides and transverse cubic sections.
Confirm section orientation, field sign, symmetry, units, and varying-section behavior against independent points.
Then build the broad hood, cabin, shoulders, flanks, and rear as a coherent control net.
Keep shape controls, physical camera controls, and shell controls distinct.

Fair the full net under topology and symmetry constraints. Preserve transverse order and shared-height groups.
Do not clip individual controls after a constrained solve; that can invalidate the solved constraints.
Use crowned ends and smooth field transitions when they suit the reference.
Keep wheel aperture depth and lip treatment explicit.

Fit the boundary of the complete trimmed body, including caps, wheel cuts, and underside opening.
The raw loft boundary is not the visible boundary where a trim dominates.
Check new derivative code with nonzero finite-difference witnesses before optimizing the full model.
Keep fairness and feature gates fixed to a recorded baseline. Do not weaken them after each accepted step.

## Make a shell that stays open

Choose wheel pockets or through openings from the geometry contract.
For thin wheel-house returns, the measured route bands the already wheel-trimmed exterior field.
Open the underside after banding, then check sections, cavity points, lips, and retained material.

The native spline field measures planar section distance, not true three-dimensional signed distance.
A field band therefore has a field depth, not guaranteed constant normal thickness.
Measure actual surface crossings. State sample coverage and failed or excluded probes.
Do not close an opening or add material merely to hide a preview defect.

## Verify silhouette and surface quality separately

Read [validation and delivery](references/validation-and-delivery.md) before choosing a final candidate.

Use mathematical projection for iteration. Calibrate its rasterization against a saved native render.
The acceptance score must use the saved native model, its recorded camera, and the frozen reference mask.
Report intersection over union, missing pixels, excess pixels, resolution, and local arch errors.
Do not register, stretch, or warp the rendered image to improve its score.

Inspect native shaded and zebra views from the reference, rear, sides, top, and underside as relevant.
Check seams, mirror joins, caps, wheel lips, and underside transitions, not only the untrimmed skin.
Combine reflection inspection with continuity, curvature, nonzero-gradient, thickness, and intersection checks.
Use stated tolerances. If they are absent, report diagnostics and unresolved acceptance instead of inventing a pass.

A high silhouette score, cubic spline degree, C2 blend formula, or successful API state is insufficient for Class A acceptance.
A finite set of regularity samples does not establish whole-surface regularity.

## Author and deliver the native result

For inset glazing, retained pillars, and shallow body lines, read
[smooth detail deformation](references/detail-deformation.md).

Read [native authoring and meshing](references/native-workflow.md) before live API calls or display builds.
Author geometry through the Notebook API using verified native blocks.
Preserve the previous deliverable and save each accepted revision with its controls and recipe.
Verify native field values against an independent mathematical model.

Keep expensive display meshing in a separate notebook that references the selected source dependency graph.
Pilot it within a measured time and memory budget. A successful strip does not qualify the full shell.
If display work cannot finish, retain the editable source and report the missing display result.

Organize native construction into named sections. Collapse all authored and nested blocks and all custom sections.
Keep only the notebook root expanded. Reapply this after the last API or GUI save.
Use verified presentation-only changes; prove geometry and input contracts did not change.

Deliver the editable `.ntop`, controls, API recipe, native previews, and a compact evidence manifest.
Bind results to source, geometry, camera, mask, and image hashes.
State separately whether silhouette, sampled geometry, display quality, and Class A acceptance passed.
