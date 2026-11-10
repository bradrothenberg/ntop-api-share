# Shorter recovery without a root valley

Use this after the compatible-section and height-opening construction in
[root-fairness.md](root-fairness.md). It addresses the later failure where
shortening only the aft recovery created a lower-skin curvature reversal.

## Treat the correction as three coupled controls

Keep the target planform and the exposed edge constraints fixed. Vary:

1. The axial recovery length `L`.
2. A positive scale `s_h` on the upper/lower height-opening law.
3. A nonnegative addition `epsilon_peak` to local section-nose regularization.

The paper's HM parameter does not replace these controls. HM averages compatible
candidate fields; it does not determine the target edge or skin recovery.

For height `dz` from the chine, the tested shifted-conic opening is:

```text
h = s_h * h_base(dz)
k_raw = k0 + (K-k0) * (sqrt(1 + 2*(dz/h)^2) - 1)
```

At `dz=0`, the uncapped width is `k0`. Its actual planform radius must be calibrated
from the target curve. Increasing `s_h` slows the width opening at a given height.
The cap must remain inactive here to retain the chine-height guide.

The retained construction caps this width with a compact smooth minimum:

```text
k_cap = L * (0.5/1.875) * (16/3)
k_soft = 0.1 * k_cap
q = max(1 - abs(k_raw-k_cap)/k_soft, 0)
k = min(k_raw,k_cap) - k_soft*q^3*(4-q)/16
```

Require `k_cap-k0 >= k_soft` to keep the final width exactly `k0` at chine height.
With the documented fraction this is `k_cap >= k0/0.9`. Check this after every
length change. Also check that the cap transition avoids the intended skin.

These cap fractions are case choices. They came from a derivative budget, not
a universal bound for arbitrary geometry. The maximum quintic-return slope is
`1.875/L`, and the compact quartic rounding correction is at most `3*k/16`.
Include the complete target/source displacement when checking the Jacobian.
Changing `L` also changes this cap, so it is not only a longitudinal change.

Retain the inverse map:

```text
R = 1 - S((x - e(y) - a)/L)
X_map = x - (T(y,z)-e(y))*R
```

Use the original source skin beyond recovery. `L` is the coordinate window,
not the measured length of a visible crease or a guaranteed fillet radius.

## Round the local section nose inside its field

The compatible section law contains a positive regularization length epsilon:

```text
d = h_local - M
N = d^2 + 2*R_conic*(sqrt(d^2+epsilon^2)-epsilon) - B
```

`R_conic` is the section conic parameter. It is different from the aft return
weight `R`. Increase epsilon locally with compact span support:

```text
t = (s - s_intersection)/w_span
b = max(1-t^2, 0)^3
epsilon = epsilon_base + epsilon_peak * b * R
```

Require `w_span>0`, `epsilon_base>0`, and finite inputs. The addition vanishes
with zero first and second span derivatives at its support boundary. The aft
weight also removes it as the section returns to the unmodified geometry.

Use a smooth symmetry coordinate where needed. In the measured case the support
is away from BL 0 and uses the existing symmetric branch. Do not introduce an
absolute-value cusp at an active centerline merely to mirror this correction.

**Keep the operation in the same coordinate composition.** The outer x remap
feeds the body field, which also contains the centerline remap. The epsilon
expression is evaluated inside that body branch. Evaluating its return weight
in world coordinates and applying a later surface offset changes the result.
Mirror the native graph order in the independent evaluator.

The peak coefficient is a section regularization setting. It is not the
planform radius, maximum surface motion or a measured rolling-ball radius.
Increasing it changes local skin fullness. Check the physical nose and material
ahead of the edge even if the nominal chord endpoint is fixed algebraically.

## Select by geometry, not by the shortest parameter

Start with a small coupled sweep around the previous smooth result. Compare
signed displacement from that result, positive thickness, and slope progression
on both skins. Do not force the upper/lower curvature sign used in this case
onto geometry with intended inflections.

For the selected candidate:

- Densify the longitudinal stations, including stations between the first cuts.
- Check transverse and oblique cuts through the complete support band. Detect
  local minima and inspect curvature concentrations; these are different tests.
- Halve the sampling interval near joins and high-curvature regions. Compare
  paired surface normals, with invalid roots excluded and coverage reported.
- Check `dX_map/dx` over the affected volume, including near the width cap.
- Measure actual edge position, guide radius and material ahead of the nose.
- Recheck native fields, not only the independent candidate evaluator.
- Compare protected inlet, tail and outboard samples with the prior model.
- Inspect matched native upper, lower and grazing views before promotion.

In the observed case, factors `0.65` and `0.35` were relative to the same earlier
recovery length. Thus the latter was `1-0.35/0.65 = 46.15%` shorter than the
immediate predecessor. Report the reference for every percentage. That result
still had some inward skin motion and did not verify a strict one-inch visible
crease limit. Do not reuse its dimensions as defaults.

Smooth support functions, positive sampled Jacobians, finite normal convergence
and clean renders are distinct evidence. Together they support a candidate;
they do not establish global C2 continuity, exact source preservation or aero
performance. Separate user visual acceptance from numerical pass results.

## Preserve evidence during iteration

Encode all varied controls in output names or use an isolated directory per
candidate. A filename containing only recovery length can silently mix different
height-opening and rounding settings. Bind native probes and screenshots to the
selected file hash. Check the saved model again after cleanup and publication.

For existing notebooks, identify graph controls by name, units and dependency
context before editing. Fixed node IDs from one aircraft are not a reusable API.
For a new aircraft, author with verified native block definitions, then run a
small native pilot before broad numerical sweeps or model promotion.
