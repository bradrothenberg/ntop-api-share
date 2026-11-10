# Curved inlet lips and finite trailing edges

Use these methods only when the adjacent feature is part of the requested edit.
They are engineering constraints around an implicit blend, not results from the
Holder-Minkowski paper.

## Straighten a projection without creating a flat inlet

First identify the requested edge, projection, straight interval, and rounded
returns. A straight side-view lip can still curve laterally in three dimensions.
Do not replace that requirement with a straight spatial edge.

Recover the actual lip crest from the native field. For a regular surface
`F(x,y,z)=0` viewed along y, an apparent contour satisfies `F_y=0`. Track the
intended connected crest through successive sections. Check this condition
against native views: it also finds unrelated apparent contours.

Given measured `x_old(z)` and the prescribed side line `x_target(z)`, use:

    delta(z) = x_old(z) - x_target(z)
    X_map = x + W(x,y,z) * delta(z)
    F_new = F_original(X_map, y, z)

`W` is one on the straightened crest and returns smoothly to zero outside the
mouth. This is an inverse map. At full strength, the new target maps to the old
crest. A linear shear alone does not straighten an already curved source crest.

Preserve the curved cross-section instead of intersecting the inlet with a
plane. The plane repair in the case study created an unwanted flat shelf.
Treat each rounded return separately. Match displacement, first derivative,
and second derivative between the straight interval and the return. Do not
force a rounded terminal contour onto the main straight line.

Check the actual lip at intermediate stations excluded from fitting. Measure
normal changes through the returns, transverse-profile preservation, protected
geometry, and the map Jacobian. Field residuals are not geometric distances.

## Remove an inherited mirror-plane cusp locally

Symmetric points can still have mismatched one-sided normals. If a symmetric
source depends on `abs(y)`, an even replacement can remove the cusp:

    r(y) = a * (3/8 + 3/4*(y/a)^2 - 1/8*(y/a)^4),  abs(y) <= a
    r(y) = abs(y),                               abs(y) > a

This law matches value, slope, and curvature at the band boundary. Its center
derivative is zero, but its center value changes. Select `a` from measured
sections, limit the correction to the affected mouth region, and report the
surface displacement. Apply the radius coordinate only to a symmetric branch.
It is not a globally invertible signed-y transformation.

## Straighten the physical trailing edge

A straight chord guide does not establish a straight surface edge. Finite
thickness, twist, conic shaping, and later cuts can move the aftmost point.
Recover that point from the final section, then move it to the target line.

For a local section angle `theta`, a longitudinal inverse-map correction can
need a corresponding `delta_z = delta_x * tan(theta)`. Derive the sign from the
section frame. Use smooth chord and span envelopes to preserve other features.
Do not extend this map across an exhaust return or fin unless those are in scope.

Separate intended straight panel segments from rounded panel corners, tip caps,
and center returns. Bracket the actual surface on both sides of the target.
Checking the target expression against itself is not sufficient.

## Attach a thin fin and fade its root blend

Use the actual rear body after the exhaust cut as the attachment boundary.
A nominal length or bounding box can extend beyond that shell and cause an
overhang. At a smooth rear extreme in an x/z section, solve `F=0, F_z=0`, then
confirm the selected endpoint and a connected interior witness in native nTop.
Use another boundary method where a sharp intersection invalidates this condition.

If the user asks to match the wing trailing-edge thickness, measure whether it
is a constant thickness or a thickness/chord rule. Do not substitute an arbitrary
small thickness. Taper any broad profile offset to zero at the edge, then add
the required finite thickness term explicitly.

For a forward root blend control `R`, an aft bead control `r`, and measured
stations `x0 < x1`, a useful initial taper is:

    t = clamp((x-x0)/(x1-x0), 0, 1)
    S = t^3 * (10 - 15*t + 6*t^2)
    radius_control = R + (r-R)*S

Require positive controls. Derive `r` from the specified bead or retained edge
thickness when that relationship is intended. Match the start to the existing
fairing and inspect the full runout. A native blend-radius control is not
automatically the resulting surface radius, especially with non-distance fields.

Limit only newly added fin or fillet volume if the original body must remain:

    min(body, max(smooth_union(body, fin, radius_control), aft_limit))

This assumes negative-inside fields and `aft_limit > 0` beyond the permitted
extent. A sharp limit can leave a cut face. Reduce the blend before it reaches
that limit, then inspect the join and bead in native side and oblique views.
Verify no added material beyond the permitted edge and no lost connection.

Identify the component carefully. The wing edge beneath a fin may need its own
correction while the fin trailing line stays fixed. Do not treat a successful
root-radius taper as proof that the adjacent wing edge is straight.
