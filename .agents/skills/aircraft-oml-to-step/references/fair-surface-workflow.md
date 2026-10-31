# Fair supports and finite joins

## Choose the chart before fitting

A dense fit cannot repair a folded or poorly ordered parameterization. Start
with physical sections, arc length, or a regular local chart. Check the signed
Jacobian and normals across the retained region. A positive Jacobian alone does
not prove global injectivity, correct branch selection, or source fidelity.

A height chart is useful only when the chosen projection is single-valued.
Use a roll chart or compatible charts around an overhang. Do not clamp an inverse
map to a nearby branch. Track complete section contours and their physical order.
Same-XY height differences can be misleading around a turned surface. State
whether a measurement compares corresponding sections or nearest surface points.

## Check boundary feasibility

Use one common authority for the position and tangent plane at a shared corner.
The incident rail tangents must lie in that plane. Fixed incompatible tangent
curves cannot satisfy an exact common tangent plane, regardless of pole count.
Adjust the permitted rail or partition and measure the resulting source change.

Check whether a requested fair section can exist before solving its control net.
For a graph z(x) over x0..x1, let L=x1-x0, with L positive. This is the horizontal
interval, not arc length. Nonnegative second derivative makes slope nondecreasing.
If the endpoint slopes dz/dx are m0 and m1, necessary conditions are:

```text
m0 <= m1
m0 * L <= z1 - z0 <= m1 * L
```

These are necessary moment conditions, not a complete existence proof for all
other constraints. Releasing endpoint second derivatives cannot fix incompatible
positions and first derivatives. Do not constrain curvature to one sign unless
the design requires it; legitimate profiles can contain inflections.

Treat value and derivative rows as one coupled system. A later corner overwrite
can change a rail that appeared fixed earlier. Transfer physical derivatives
with the chart Jacobian and check all adjoining rails after the final solve.

## Make the lip a finite band

Separate three concerns: geometric support, semantic face layout, and join quality.
Several semantic faces can share a common fair support. Separate names do not
require independent fits that produce unrelated boundaries.

Measure finite lip width around the complete perimeter, including the lower
corners. Do not let the exterior band collapse to a point while the inner return
continues. Give the surrounding body skin its own attachment rail. Where the
upper band turns back, use a suitable roll chart rather than an XY graph.

Use analytic conic segments where they fit the measured sections. Otherwise,
start with a compact cubic or quartic cross-roll profile. Match the mouth,
outer shoulder, and passage rails with compatible derivatives. Preserve intended
sharp edges and any physical divider separately.

Do not stretch a faulty old chart into a rectangular extension. Test the new
band's finite ordering and normals before attaching the body skirt. If a fixed
guide contains an unwanted rise, fall, and rise, repair that guide first.
Interior smoothing cannot remove a feature imposed by the boundary itself.

## Regularize the complete region

Integrate the derivative penalty in every nonzero knot span. Choose quadrature
for the polynomial degree of the squared derivative in both parameter directions.
For rational geometry, use suitable numerical integration with refinement checks.
A uniform sample can miss short spans and leave rapid oscillations unpenalized.

Penalize the interior as well as boundary residuals. A boundary-only least-squares
fit can have a large interior null space. Small seam errors can coexist with
large control motion, waves, and normal changes inside the trimmed face.

Bound control displacement where appropriate and measure actual retained motion.
Use independent section and normal witnesses in every active span. Record solver
convergence separately from geometry acceptance. A stopped solver is not an
optimum; a converged solver is not proof of a fair shape.

Check both longitudinal and transverse behavior. Independent smooth section
solutions can introduce waves between sections. Inspect full-mouth and broad
glancing views, the ends of each correction, and the adjoining skin.

Source gradients can be noisy even near a well-converged scalar root. Compare
gradient targets with finite section secants and nearby root brackets. Fit a
regular physical normal field when justified by those measurements. Preserve
the raw samples and report the approximation.

## Preserve finite ownership and orientation

A surface, its face pcurve, and the stored 3D edge are separate representations.
Map the complete physical boundary through a nonlinear chart. A UV chord between
the endpoints usually does not preserve the physical curve.

Reopen the STEP and inspect pcurve domains, short knot spans, endpoint continuation,
micro-loops, and duplicate finite footprints. Perform ownership cuts in a verified
chart. Test known inside and outside witnesses after each boolean. Successful
kernel completion alone does not prove that an overlapping region was removed.

Preserve face orientation when rebuilding trims. Check physical outward normals
after export, including mirror operations. An unoriented tangent-plane angle
cannot detect an inverted face. Near a thin fold, identify the correct implicit
branch before comparing a CAD normal with a projected source gradient.

When only orientation changes, compare the actual readback geometry and trims.
A translator can alter edge ranges or tolerances during the same operation.
If exact identity fails, measure and bound the difference. Do not replace a
failed byte-identity assertion with a claim based on appearance.

## Periodic parts and internal geometry

After a nonlinear configuration map, test periodic position and derivative
closure. Coincident seam positions do not establish tangent continuity. Enforce
compatible scaled first derivatives and verify each seam knot span after export.
Higher continuity is useful only when it is required and remains source-faithful.

Inventory internal parts as well as exterior skins. Recover analytic planes or
cylinders when the transformed geometry supports them. Keep nominal structural
sheets separate from thick visualization bodies. Do not imply strength validation.
Combine redundant coplanar profiles before mirroring when exact symmetry is
required, and report any intentional change from an asymmetric source.

## Group parts without losing evidence

Re-exporting imported parts through an assembly writer can change pcurves or
topology even when basic solid validity passes. Audit actual grouped members
against their qualified source members before reusing prior checks.

A specialized composer can join compatible STEP DATA streams by renumbering
entity references outside quoted strings. This requires schema, section, unit,
context, name, and presentation handling. It is not general text concatenation.
Reopen the result and verify every member. Matching text alone is insufficient.

For deterministic kernel serialization, complete BREP identity can establish
unchanged geometry and topology. If bytes differ, inspect the actual differences.
Matching face counts, volume, or a render is not equivalent evidence.
