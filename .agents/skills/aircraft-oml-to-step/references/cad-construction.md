# CAD construction choices and failure modes

## Fair surfaces and exact boundaries

Use analytic planes and lines where they express the design. For smooth skins,
fit a compact camber/thickness representation or controlled spline surfaces.
Regularize interior coefficients while enforcing known boundary positions and
slopes. Check that thickness stays nonnegative and that extra extrema do not
appear between fitted stations. A single thickness maximum is useful for a
conventional airfoil, but is not a rule for every profile.

Straightness must be a geometric constraint. Collinear spline poles, an explicit
line edge, or a suitable ruled boundary can impose it. Smoothing noisy points does
not guarantee a straight edge. Preserve intentional sweep corners as separate
segments. Do not straighten a nose, curved tip or twisted edge without evidence.

For finite trailing edges, define upper/lower endpoints in the specified direction.
Wing vertical separation, section-normal separation and fin side-to-side thickness
are different measurements. Construct closing faces with shared boundaries.
Measure the actual exported edges, including the final station. A root blend can
widen into the body; state where the specified exposed-edge thickness applies.

## Oblique wing tips

Continue the valid wing loft beyond the intended tip. Intersect it with the
measured tip cutting plane or surface. Close the resulting airfoil section.

Do not collapse the outer loft's chord or station mapping into an oblique tip
corner. Compression can create a transverse ridge or distorted tip. A natural
planform corner and a surface defect are not interchangeable.
Inspect tip upper/lower surfaces, the cap, and the last trailing-edge segment.

## Normal fins and local root blends

Construct the unblended fin from its source root, leading edge, trailing edge,
tip line and profile/taper rule. Determine its intersection with the body before
selecting a blend footprint. Keep the fairing local to that intersection.
Leading-edge, root and aft blend radii may differ. Derive their variation from
the source and requested changes; measure both the transition and the aft limit.

Prove automatic fillets on a small candidate before relying on them. A failed
fillet is a reason to inspect topology and geometry, not to increase its radius.
If necessary, construct a controlled patch between the exact body trim curve
and a curve on the fin. Match tangent directions at both ends.

For a cubic Bezier cross-section with endpoints P0, P3 and endpoint derivatives
d0, d1 in the same normalized parameter:

    P1 = P0 + d0/3
    P2 = P3 - d1/3

A quartic section has five poles. Its endpoint derivatives set P1=P0+d0/4
and P3=P4-d1/4. Use the remaining P2 to control the interior fairly. A quartic
does not provide two independently prescribed second derivatives as well.
When the constraints do not fit the degree contract, revise the physical patch
layout or use compatible joined spans. Do not silently raise the degree.

Derive derivatives from the adjoining surfaces and actual parameter scaling.
Check the patch for foldovers, local bulges, self-intersections and excessive
normal/curvature changes. Matching endpoint tangents alone does not make the
interior fair. Do not add an unexplained curvature offset merely to pass a check.

Use boundary conditions in their physical parameter scale. A tangent direction
must also have a useful magnitude and a positive transverse ordering. Check
finite-width strips, including the end of each correction's support. A compact
blend with zero value outside its support can still produce a local curvature peak.

Coordinate the fin's aft termination with the body closeout. Avoid a rounded fin
corner ending above a remaining body shelf. A shared trailing plane or compatible
cap can solve this, but preserve the source planform and record body changes.
Do not expand the fairing to conceal the mismatch.

Scope body trimming tools to the intended component and region. A cutter used
on the complete assembly can remove unrelated surfaces. Recheck the complete
silhouette after booleans, not only the local junction.

## Face layout and symmetry

Fit the smooth surface first, then imprint useful CAD boundaries along measured
shoulders, construction transitions, blend limits and sweep changes. A surface
split should not introduce a gap or a ridge. Preserve sharp design edges.

When symmetry is required, build and split one half and mirror its exact topology.
Check boundary geometry as well as surface points. Independent left/right fits
can look symmetric while their face layouts differ.

If a whole-solid half-space operation creates large tolerances near a degenerate
junction, diagnose that junction. Extracting and splitting individual positive
faces, then mirroring and sewing them, is one possible fallback. This is
not a reason to ignore poor topology or to loosen tolerances blindly.

## Runtime and reconstruction

Use `uv` and retain exact dependency versions for the delivered rebuild. The
CAD bindings vary between versions. Inspect array types, topology casts, and
bounding-box methods in the installed API before copying calls.

Default fast mass-property integration can give visibly different areas for
mirrored spline faces. Use adaptive integration for reported area/volume results.
Do not interpret numerical quadrature error as geometric asymmetry.

## Fairness integration and finite boundary ownership

Integrate derivative penalties in every knot span. A sparse uniform sample can
skip short spans and leave rapid oscillations almost unpenalized. Select the
quadrature order for the degree of the squared derivative. For a tensor-product
penalty, account for both parameter directions. Recheck the result with denser,
independent witnesses, especially near clustered knots.

Assign a neighbor to each finite boundary segment. Do not let a shared endpoint
classify the whole edge. A nearest-point search can select a nearby corner or an
unrelated branch. Require finite correspondence and record excluded vertices.
At a multiple-face corner, incompatible jets require a common construction or a
revised partition. A small positional gap does not prove a tangent contract.

A straight physical boundary can have a curved pcurve in a nonlinear chart.
Map the complete physical boundary through the chart before fitting its pcurve.
Do not replace it with the chord between its UV endpoints. Measure the resulting
physical path after STEP readback.

## Physical tangent data across charts

Transfer physical tangent planes, not coefficient rows, between different charts.
Even two regular charts can have different shear or parameter scales. An unchanged
coefficient row can then change the physical normal and move another boundary.

For the chart `X=C(Y)-R, Z=H(R,Y)`, the physical slopes are:

```text
Z_X = -H_R
Z_Y = H_Y + H_R C'(Y)
H_R = -Z_X
H_Y = Z_Y + Z_X C'(Y)
```

Apply the chain rule before setting the derivative control row. For a general
chart, use its Jacobian and the physical tangent-plane constraint. Check the
normal after the complete solve, including all endpoint and boundary operations.

At a corner, value rows and derivative rows can share poles. A later side-row
overwrite can move a previously fixed front rail. Fit compatible corner data
together. Measure both rails after export. If mixed endpoint derivatives conflict,
revise the local construction instead of adding a small patch over the defect.

Sample source data in the chosen surface chart. A point grid from an earlier
chart can poorly cover a steep return even when its overall sample count is high.
Check spatial coverage and normals at the return, lip foot, and divider junction.

## Local end slopes and simple lofts

A change to one terminal pole row can affect a much larger region than expected.
Inspect the complete basis support first. Exact knot insertion can localize the
allowed correction without changing the initial geometry or increasing degree.
Tie the centerline height rows when zero transverse slope is required.

Check section height and section slope separately. A positive chart Jacobian
does not exclude a shallow trough or a curvature wave. Compare every new height
extremum with the implicit. Do not conceal an unconfirmed trough with shading.

For a narrow region between compatible rails, test a cubic Hermite loft before
adding more interior fit poles. Use physical derivatives at each rail. Where a
longitudinal split is needed, share the position row and scaled derivative row.
Measure source deviations; the simpler loft can be fairer but less accurate.

## Preserve analytic planes after a configuration map

A nonlinear aircraft map can leave some cap or tip surfaces planar. Test the
mapped support instead of keeping every converted surface as a spline. For a
nonrational spline, bound the distance of every control point from the candidate
plane. The convex-hull property then bounds the complete support. A sample of
surface points alone does not provide that bound.

Keep the existing XYZ boundary curves and vertices. Project their pcurves onto
the analytic support. Check retained trims, validity, and physical normals after
STEP readback. Plane parameters and topological face sense can change on export.
Do not infer an inward normal from an unchanged geometric plane.

Fair only the retained surface region. Large derivatives on unused rectangular
support extensions can dominate a global smoothing penalty. Keep the objective
sampling mask separate from the exact trim-domain checks used for acceptance.
