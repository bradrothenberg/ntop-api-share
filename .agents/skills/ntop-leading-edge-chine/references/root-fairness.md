# Tight planform with fair upper and lower skins

Use this construction when a small planform corner radius must meet broad,
smooth wing-body skins. First establish compatible source sections, explicit
twist, and an aligned chine using [construction.md](construction.md).

The accepted aircraft correction retained the compact corner at chine height. It opened
the blend vertically instead of increasing its width with distance aft. This
removed the remaining upper and lower valleys in the verified region.

## Separate the three controls

1. Planform width sets the minimum corner radius at the leading-edge height.
2. Upper and lower recovery heights control how the adjacent skins open out.
3. A longitudinal window returns the corrected geometry to the original body.

These controls are independent design variables. A small planform radius does
not require a short vertical transition. C2 endpoint weights alone do not
prevent a slope overshoot inside the transition.

## Construct the coordinate map

Use SI lengths. These equations use x aft, y span, and z up. Confirm the model's
axes, field sign, symmetry, and source graph before applying them.

For one side, define:

- `b(y)`: body tangent planform, smoothly recovered to the original inboard edge.
- `w(y)`: prescribed straight wing leading-edge planform.
- `e(y)`: original broad leading-edge planform.
- `z_e(y)`: its world height, including section placement and twist.
- `k0 > 0`: compact planform field width.
- `K >= k0`: broad interior field width.
- `h_u, h_l > 0`: upper and lower recovery heights.
- `t > 0`: half-height of the transition between these recovery heights.

For a mirrored aircraft, apply the same side convention on both sides. Retain
the existing BL 0 treatment. Do not replace all coordinates with absolute span
unless the affected geometry is symmetric.

Define the clamped quintic ramp:

    v = clamp(u, 0, 1)
    S(u) = v^3 * (10 - 15*v + 6*v^2)

Open the width with height from the chine:

    dz = z - z_e(y)
    h(dz) = h_l + (h_u - h_l) * S((dz + t)/(2*t))
    k(dz) = k0 + (K - k0) * (1 - exp(-(dz/h(dz))^2))

At the chine height, `k = k0`. Away from it, `k` approaches `K` smoothly. The
case used `t = min(h_u, h_l)/4`. That ratio is a selected control, not a
general rule. Keep `h` positive throughout the transition.

Use this compact quartic smooth minimum for the target leading-edge field:

    q = max(1 - abs(b(y) - w(y))/k, 0)
    T(y,z) = min(b(y), w(y)) - k*q^3*(4-q)/16

The apparent min/abs branches form one smooth operator inside its support.
Implement the full expression with the same positive width and units. Do not
replace it with an unrelated fillet or a sharp clip through the skin.

Retain a separate aft return window, with offset `a` and length `L_aft > 0`:

    R(x,y) = 1 - S((x - e(y) - a)/L_aft)
    X_map = x - (T(y,z) - e(y))*R(x,y)
    F_new(x,y,z) = F_original(X_map, y, z)

This is an inverse coordinate map. Its subtraction sign matters. In the region
where `R = 1`, the prescribed target edge maps back to the original edge. Where
`R = 0`, the original field is recovered exactly. Check that the selected offset
keeps the intended edge in the full-correction region.

Apply the map to the intended geometry branch. Check other features explicitly
if they share that branch. In the case study, the inlet and protected geometry
retained identical field values at the sampled points.

## Calibrate instead of copying dimensions

The field widths `k0` and `K` are not geometric radii. At `z = z_e(y)`, use the
target planform curve to measure curvature and solve for the required width.
For a graph `x = T0(y)`, its local radius is:

    radius = (1 + T0'(y)^2)^(3/2) / abs(T0''(y))

Exclude straight segments from a finite minimum-radius calculation. For a
general parametric boundary, use its full planar curvature instead. Verify the
actual native outline after calibration; twist or rounded noses can shift it.

Measure each skin's distance from the chine at representative root stations.
Use those distances to define a small sweep of upper and lower recovery heights.
Prefer the smallest tested candidate that meets the shape constraints and dense
fairness checks. Recheck the transition scale and aft window when the section,
twist, corner angle, or requested radius changes.

## Check the interior, not just the joins

The rejected construction increased width with distance aft of the edge.
Its skin slope accelerated and then recovered. This produced a valley despite
C2 joins. A sparse four-section check also missed a later lower-skin valley.

For each candidate:

1. Solve both skin roots along longitudinal cuts across the whole root band.
   Include stations between the initial test cuts and around the planform corner.
2. Inspect slope and second derivative along each cut. For the case nose-to-skin
   transition, the intended slope progression was monotone. The upper check used
   `d2z/dx2`; the lower check used `-d2z/dx2`. Both stayed negative in the accepted
   region. Do not impose that sign on surfaces with intentional inflections.
3. Check normals, transverse sections, and support boundaries. Repeat with finer
   spacing where a derivative margin is small or a grazing view shows a feature.
4. Check the map Jacobian throughout the affected volume. With y and z unchanged,
   its determinant is `dX_map/dx`. Require it to remain positive to avoid local
   folds. Positive sampled values do not prove global invertibility.
5. Measure leading-edge position, planform radius, twist, positive thickness,
   unwanted material ahead of the edge, and maximum displacement from the source.
6. Compare native field and map evaluations with the independent implementation.
   Check the final saved model, including inlet and other protected features.
7. Inspect native upper, lower, planform, and grazing views with matched cameras
   before and after the change. Hide intermediate bodies to avoid false seams.

Keep the independent dense sampling results separate from the smaller native
sample set. Field residuals are numerical agreement checks, not manufacturing
tolerances. Neither sampled fairness nor a clean render establishes global C2
continuity or aerodynamic qualification.

## Rejected short-runout example

The following construction passed sampled longitudinal and native agreement
checks, but the user rejected its dented appearance. It is a failure example,
not an approved shortcut for a strict aft crease limit. A geometry check must
include the accepted reference skin, crosswise shape, and native grazing views.

The short map changed local skin fullness and created a concentrated shoulder.
Positive map Jacobians and smooth endpoint derivatives did not prevent this.
Nor does zero correction beyond a station establish visual fairness there.

When the user limits how far the crease can extend aft, compressing the delayed
C2 ramp above can create a new valley. Reducing the recovery heights can also
cause slope reversal. Test a recovery that starts at the tight edge itself.
This changes the local sections. In the reviewed case it did not preserve the
accepted surface appearance, despite native numerical agreement.

Let `E(y)` be the tight planform evaluated at chine height and `e(y)` the original
edge. Use a positive recovery length `L(y)` and the inverse map:

    q = max(1 - (x-E(y))/L(y), 0)
    X_map = x - (E(y)-e(y))*q^3

The correction starts immediately. It becomes zero with zero first and second
derivatives at `x=E+L`. Retain the original curved body field behind that station.
Do not add a second height-dependent width law without checking both skins.

For an inboard completion station `x_goal` and minimum local length `L_min`,
use a C2 smooth maximum of `x_goal-E` and `L_min`. For the compact quartic
operator in this reference, smooth-max rounding adds at most `3*k/16` to the
larger input. Include that increment in the requested aft-distance limit.
A hard maximum in `L(y)` can create a crosswise seam inside the fairing.

Check the map derivative `1 + 3*(E-e)*q^2/L` where the cubic is active.
A negative displacement needs enough recovery length to keep it positive.
The cubic grows ahead of the edge. If bounding that continuation, put its
transition in verified empty space. A hard cap is not globally C2, even when
it does not intersect the delivered surface.

Keep the local wing-side runout distinct from the fuselage-side completion
station. Verify the actual edge, normal progression, and both skin curvatures
between test stations. Show matched native views. Exact zero correction aft
proves recovery to the source field; it does not certify that source's fairness.

For a repair, retain the last accepted full skin as the comparison baseline.
Measure inward and outward displacement on both skins. A one-sided envelope can
prevent inward movement yet still introduce a local shoulder, so it is also
insufficient by itself. Test transverse and oblique normal progression. If the
requested runout conflicts with a tight planform corner in the tested family,
resolve that design constraint before changing the corner radius. Restore the
accepted shape when a short-return candidate fails visual review.

## Broader corner with a gradual conic opening

When the user allows a larger planform corner, recalibrate its actual curvature
and retain the last smooth axial return as a comparison. One tested alternative
to the Gaussian height law was a shifted conic:

    h = scale * h(dz)
    k_raw = k0 + (K-k0) * (sqrt(1 + 2*(dz/h)^2) - 1)

Unlike placing `k0` inside the square root, this law does not make its initial
second derivative inversely proportional to the small planform width. It still
needs a measured scale sweep. Faster opening can cause a local curvature reversal.

Bound the remote width with a compact C2 smooth minimum. Choose its cap from
the map derivative budget, then check that the cap transition avoids the intended
skin. For a quintic return of length `L`, the maximum absolute ramp derivative
is `1.875/L`. Include the full target/source displacement in the Jacobian bound;
do not assume the tangent separation is positive without checking it.

The earlier broader-corner candidate had no inward skin displacement over its
dense checked root band and passed native edge, surface, and protected-feature
checks. Its separate strict aft visible-crease limit remained unverified. Treat
this as a tested alternative, not a guarantee of a one-inch fade or visual
acceptance. Corner radius and longitudinal crease distance are distinct measures.
Later compact-recovery candidates did have some inward displacement. Do not
carry this earlier no-inward-motion result into those revisions.

## Native authoring and provenance

For the later coupled correction that shortened recovery without the tested
lower-skin reversal, read [compact-recovery.md](compact-recovery.md). It adds
local section-nose regularization and preserves its coordinate composition.

Use block identifiers and units verified from the active nTop catalog. Implement
the selected height law with scalar fields and the existing coordinate-remap
branch. The Gaussian option uses an exponential. The later shifted-conic option
uses a square root and a compact width cap. Both retain the smooth return ramp.
Do not copy example node IDs into another notebook.
Keep named upper and lower recovery controls. Preserve the source during iteration.

Save a separate version. Collapse authored blocks and sections, retain only the
intended final body's visibility, and associate measurements and native captures
with its file hash. See [aircraft-case.md](aircraft-case.md) for measured outcomes
and validation limits. Remove obsolete branches only during an authorized,
verified cleanup of the selected result.

This coordinate-map correction is an engineering addition to the HM workflow.
Do not attribute its fairness checks or planform constraints to the paper.
