# Section construction

Use SI lengths and radians internally. These formulas use x aft, y span, and z up.
Verify the source convention before applying them.

## Explicit twist and placement

Let a(y) = (a_x(y), y, a_z(y)) be the leading-edge anchor. Let theta(y) be the
section twist, c(y) its chord, and u its chord coordinate. A local point (q,h),
where q=c*u, maps into world coordinates as:

    x = a_x + cos(theta)*q - sin(theta)*h
    z = a_z + sin(theta)*q + cos(theta)*h

An implicit field evaluates the inverse map:

    q =  cos(theta)*(x-a_x) + sin(theta)*(z-a_z)
    h = -sin(theta)*(x-a_x) + cos(theta)*(z-a_z)

This positive angle raises the trailing chord relative to the leading chord.
Do not call it washout until the aircraft's axis and incidence conventions agree.

For a straight exposed edge, prescribe a linear a_x and a_z over that span.
Fair the anchor into the body-side chine inside the selected root interval.
One possible weight is S(t)=6t^5-15t^4+10t^3, with t clamped to [0,1]. Its first
two derivatives vanish at the endpoints. It can still create excess curvature
inside a short transition. Inspect derivatives and lengthen or refit as needed.

If the source rotates about a fixed pivot, recover its physical edge first.
Do not fit a straight line to a distorted screen image. Keep the original angle
law and report the translation needed to put sections on the new line.

## Shared section law

For a mirrored centerline, a function of |y| has a cusp if its one-sided first
derivative is nonzero. Tying the first two body shape coefficients is insufficient
when planform, chord, or placement still have nonzero first derivatives.

A compact even span coordinate is q_s=w*Q(t), for |y|<w, with t=|y|/w and:

    Q(t) = (15/8)*t^2 - (5/4)*t^4 + (3/8)*t^6

For |y|>=w use q_s=|y|. This preserves the center value, gives zero center slope,
and matches value, slope, and second derivative at w. Apply it consistently to
the active section guides and placement laws. Verify the width with measured
surface displacement and curvature. This eases a linear absolute-span twist near
the center; retain its original schedule outside the band and report the change.
It does not repair a separate sharp Boolean intersection or singular field.

The center-preserving Q above reaches a span derivative of approximately 1.347.
It must compensate for zero slope at the center while retaining the original
center height and outer location. That overshoot can leave a narrow shoulder.
Do not accept it solely because the BL 0 slope check passes.

If the crown and keel can move, one monotone alternative inside the width is:

    Q_f(t) = 5/16 + (15/16)*t^2 - (5/16)*t^4 + (1/16)*t^6

Use q_s=w*Q_f(t) inside and q_s=|y| outside. Q_f' increases from zero to one;
Q_f''=(15/8)*(1-t^2)^2 is nonnegative. Value and the first three derivatives
match absolute span at the boundary. The positive center value deliberately
moves the crown and keel. It does not preserve the original side silhouette.

A longitudinal width such as w=4*w_max*s*(1-s), with normalized body coordinate
s, tapers this correction toward the nose and tail. This is a selected design
law. Measure its displacement and source-fit error. Keep division finite at the
ends without moving the geometric closure. Verify the full field outside the
correction region, not just the leading-edge anchor. Compare boundary derivatives
with the underlying unrounded loft, since an earlier correction can have different
support. C3 here describes the correction map; it does not upgrade the continuity
of its input guides or certify the whole aircraft.

If the complete wing-body field is even in y, this correction can be applied once:
`H_corrected(x,y,z)=H_original(x,q_s(y),z)`. That is equivalent to substituting the
coordinate into all its active shape laws. Verify equivalence before simplifying
the native graph. Do not use a nonnegative remap for an asymmetric body or apply
it to unrelated components. A separate vertical tail can remain in world space.

For 0 <= u <= 1, construct:

    M = c*u*(1-u)*[(1-t)*C_body(u,y) + t*C_wing(u,y)]
    A = (1-t)*A_body(u,y) + t*A_wing(u,y)
    B = c^2 * [u*(1-u)^2*A^2 + delta^2*u^2]
    d = h-M
    N = d^2 + 2*R*(sqrt(d^2+epsilon^2)-epsilon) - B

M is camber, A is a positive dimensionless thickness amplitude, delta is a
dimensionless trailing half-thickness ratio, R is a nonnegative conic length,
and epsilon is a positive rounding length. R can decrease from the body value
to zero on the wing. A and C can be low-order Bernstein or other smooth lofts.

The zero surface N=0 defines both skins. For B>0 and R>=0 it has two symmetric
height roots about M. The squared amplitude prevents a negative thickness target
inside the chord. Zero endpoint camber fixes the chord anchors; it does not force
a finite-thickness trailing edge to a single point.

A useful dimensional field normalization is:

    f = N / [2*sqrt(max(B,0)+R^2+ell^2)]

where ell>0 is an explicit conditioning length. This is not a signed distance.
Changing its normalization can change a subsequent blend.

With rounded noses and nonzero twist, the minimum world x can differ from the
nominal q=0 point. Measure both if straightness of the visible silhouette matters.
Likewise, a tip cap can truncate the nominal chord before u=1.

## Nearby candidates and HM

Use compatible candidates f_i, for example from nearby positive A_i. Preserve
their common chord anchors and edge bounds. For two equal-weight candidates:

    H = (L/p) * [log(exp(p*f_1/L)+exp(p*f_2/L)) - log(2)]

L>0 is a reference length. Use shifted log-sum-exp for stability and the explicit
p=0 limit H=(f_1+f_2)/2. Do not evaluate division by zero in an unused native
branch. Keep field signs and scales consistent.

H is between the two candidate field values at each point. If both vanish at a
point, H vanishes there. Neither property guarantees small curvature or an
unchanged spatial volume. Smooth zero surfaces also require a nonzero gradient.

For more general weights and the paper's exact conventions, use the HM skill.
The section construction, endpoint constraints, and straight-edge frame here are
engineering additions. Do not attribute their guarantees to the paper.

## Fitting and validation distinctions

Untwist individual sample points before fitting. Global vertical upper/lower ray
hits do not become pairs at identical local q after rotation. Either interpolate
onto shared local coordinates or fit each transformed skin point directly. If
paired coordinates are averaged as an approximation, measure the resulting error.

Keep these quantities separate in reports:

1. Source sampling error and interpolation uncertainty.
2. Reconstructed section-shape residual in the source placement.
3. Intentional section translation to satisfy the straight-edge constraint.
4. Total deviation of the delivered model from the reference.

A small edge residual cannot establish whole-aircraft accuracy. A good render
cannot establish C2 continuity or aerodynamic performance.
