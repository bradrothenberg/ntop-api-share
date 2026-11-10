# Smooth detail deformation

Use this route for inset glazing and shallow lines on an accepted native shell.
Keep the baseline unchanged. Treat feature locations and depths as selected
styling controls unless actual dimensions or landmarks establish them.

## Measured construction

The car generator (source-project artifact; not bundled)
uses two successive coordinate maps of the complete shell:

1. `Y = y + Dy(x,z) * sg(y)`.
2. `Z = z + Dz(x,Y) * gate(z)`.
3. Evaluate the source field at `(x,Y,Z)` with the native Remap Field block.

`Dy` and `Dz` are nonnegative. The signed transverse gate and upper gate are
monotone C2 ramps. Each stage is strictly increasing and onto along its own
coordinate. Their composition is globally invertible under these conditions.
Its determinant is `(1+Dy*sg'(y))*(1+Dz(x,Y)*gate'(z))`, which is at least one.

Evaluate the second amplitude at mapped `Y`. Evaluating it at original `y`
invalidates this proof. Negative depths or zero transition widths also require
a new audit. This proof does not establish source-shell regularity or Class A.

Use the clamped quintic `S(t)=t^3*(10-15*t+6*t^2)` for C2 support transitions.
Form rounded convex window fields with stable log-sum-exp of plane fields:
`m+w*log(sum(exp((p_i-m)/w)))`, where `m=max(p_i)` and `w>0`.
This expression is smooth, symmetric, permutation-invariant, and avoids overflow.
Nested compact smooth maxima were slower and introduced an order-dependent
symmetry error in this case. A C2 function alone does not ensure fair highlights.

Retain undeformed bridges between glazing regions for the pillars. Deform both
faces of the existing shell together. Coordinate depth is not normal recess
depth or physical wall thickness. Material masks can partition the transformed
shell into paint, glass, seals, and lines. They do not create a glazing assembly.
Inspect the whole shell as one visible body for a clean reflection diagnosis.

## Repair panel-line joins

Separate open panel curves produced a pointed hood join and disconnected door
lines in the first detailed car, despite passing field and silhouette checks.
For a closed panel perimeter, prefer one rounded closed contour over independently
fitted edges. The V03 candidate (source-project artifact; not bundled)
uses positive-width log-sum-exp of polynomial boundary fields. A C2 groove mask
follows that contour. A separate door divider uses a C2 clip to the perimeter.

Trace the complete zero contour. Check closure, planar gradients, mirror joins,
and divider intersections. These checks establish construction coherence, not
acceptable highlights. Field-based bands can vary in normal width. Overlapping
perimeter and divider displacements also deepen their T-junctions.

Before accepting a repair, inspect the saved native hood centerline, corners,
and door T-junctions in shaded and zebra views. Include top, side, and reference
views. Require this visual review separately from silhouette and numerical checks.
The V03 contour audit (source-project artifact; not bundled)
passes its planar checks; final native visual acceptance remains open.

## Verification and performance

Run the map audit (source-project artifact; not bundled)
after changing controls or generator code. Check dependencies, finite-difference
Jacobians, symmetry, inverse residuals, support, and bounds.
Then compare native field witnesses with independent values. Include surface
samples for surface acceptance; off-surface field values only prove wiring.
Remeasure the frozen native silhouette and inspect shaded and zebra views.

The 8 October 2026 detailed car passed 46 native witnesses and all 259 variables.
Its fixed-view IoU was 99.124606%. Class A and wall thickness remained unverified.
See the delivery record (source-project artifact; not bundled)
and quality limits (source-project artifact; not bundled).

The sphere pilot took 21.16 seconds. The full spline-shell import took 745.00
seconds. Use representative shell geometry in performance pilots, then change
only feature count. The sphere pilot did not predict full-model evaluation cost.
After import, delete QA consumers in the same verified task-owned session.
Avoid reopening the just-saved model before cleanup. Compare all output geometry
fingerprints, then apply collapsed sections and saved views on the clean file.
