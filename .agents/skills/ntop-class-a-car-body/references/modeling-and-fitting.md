# Modeling and fitting

Use these mechanisms when building a guide-driven implicit car body or refining the measured CarSurface model.
They describe a tested construction, not a universal automotive surface standard.

## Native skin and shape controls

The case uses longitudinal `curve_axis_distance` guides and a cubic `spline_implicit` tensor skin.
Its coordinates run from front at x=0 to rear at x=1, with mirror symmetry about y=0 and z upward.
One notebook metre represents one normalized design length, L.
These are case conventions; record the frame and scale for each new model.

The transverse field is signed distance to the planar cubic section at the current x.
It is not a true three-dimensional distance to the loft.
Verify a constant-section pilot, then a varying-section pilot with exact mathematical surface points.
Use conservative control-hull bounds that contain the retained skin.
Check that a bounding guard never becomes an unintended exterior face.

Maintain a consistent transverse control-polygon order. An early reversed polygon produced the wrong body.
Enforce mirror and endpoint conditions in the control basis. Check derivative behavior across the mirror seam.
Keep equal-height groups and longitudinal/transverse order constraints inside the fairing solve.
Compare fairness on the same domain, grid, and units before and after fitting.
Repeat at twice the grid density before interpreting small candidate differences.

Relevant implementations:
car_recipe.py (source-project artifact; not bundled),
shell_fairing.py (source-project artifact; not bundled),
fairness_diagnostic_v2.py (source-project artifact; not bundled).
Inspect these local helpers before reuse. Their paths, data layouts, and model dimensions are case-specific.

## Crowned ends and compact C2 transitions

For a negative-inside body field, the case trims the loft with front and rear crown fields:

```text
front = -x + cy*y^2 + cz*(z-zc)^2
rear  = x-1 + cy*y^2 + cz*(z-zc)^2
```

Each cap has its own coefficients and centre. Apply the actual model's ordered nested smooth maxima.
For d=a-b and positive width w, the measured compact maximum is:

```text
if abs(d) >= w: max(a,b)
otherwise: (a+b)/2 + w/6 + d^2/(2*w) - abs(d)^3/(6*w^2)
```

Width is a field blending parameter, not a physical fillet radius.
The formula's C2 continuity does not prove a regular zero surface: inputs must be smooth and the composite gradient must stay nonzero.
Inspect the full blend footprint. A fixed x-distance from an end does not identify all crown-influenced points.

See cap_blend.py (source-project artifact; not bundled) and
rounded_caps.py (source-project artifact; not bundled).

## Shell order and open edges

For a negative-inside exterior field F and positive field depth d, use:

```text
shell_band = max(F, -F-d)
opening_field = bottom_guide(x) + opening_rise - z
final_shell = smooth_max(shell_band, opening_field, underside_width)
```

Decide whether wheel cuts belong before or after banding:

- Band after wheel trimming to retain a thin wall around finite wheel recesses.
- Band first when the intended design is a different aperture or lip construction; verify the resulting section explicitly.
- Choose through cuts or finite pockets from the requested geometry. They are not interchangeable defaults.

The case helper requires `opening_rise > field_depth + underside_blend_width`.
It limits blends applied after banding to at most `field_depth/4`.
These guards keep the branch switch inside material and preserve the intended opening for this field construction.
Re-derive and recheck them if the field scaling or topology changes.
Wider wheel blends applied before banding do not use that same limit.

The case's attempted depth increase from 0.004 L to 0.008 L closed the underside when its opening rise stayed 0.006 L.
It was not an acceptable preview repair.
Field depth must not be reported as constant physical thickness. Measure along independent surface normals and retain unsuccessful crossings in the coverage report.

See shell_native.py (source-project artifact; not bundled) and
prepare_shell_checks.py (source-project artifact; not bundled).

## Fit the true composite boundary

First establish a plausible three-dimensional body and physical camera. A single silhouette underdetermines unseen shape.
Fit important arch and landmark contours separately so global overlap cannot hide malformed openings.
Preserve the reference mask, topology, and accepted feature limits throughout optimization.

Where a cap dominates, moving raw loft control points may not move the final boundary.
Use the exact closest point on each cubic span and the chain rule through all active smooth maxima.
Include span endpoints and all real stationary candidates when choosing the closest section point.
Reject ambiguous closest branches from derivative fitting, and report the omitted coverage.

For a fixed-x radial boundary q=c+rho*r and composite field H(q,C)=0:

```text
d(rho)/dC = -(partial H/partial C) / (gradient_yz(H) dot r)
```

For a section control coordinate, its partial includes the cubic tensor basis, outward section normal, and nested blend weight.
The pure-cap region has zero sensitivity to loft controls.
Apply the physical camera Jacobian after the field-boundary derivative.
Reject near-zero ray denominators. Confirm the boundary root residual after refinement.

Before the full solve, check finite differences at nonzero transition witnesses using more than one step size.
A collection of zero derivatives is a vacuous test of the active blend logic.
Keep original fairness gates fixed and report which comparisons use the original versus immediate baseline.
The selected case improved relative to V1 while some curvature measures worsened relative to its immediately preceding candidate.

See shell_candidate_cap_boundary.py (source-project artifact; not bundled).

## Calibrate projection before trusting a percentage

The fast proxy must include the actual underside and wheel trims.
Single-pixel polygon fill overfilled the case boundary by approximately one pixel.
It produced a misleading score until area coverage and pixel phase were calibrated against native pixels.
Section sampling also changed the score; a coarse longitudinal grid was not a valid final proxy.

The case used 700 by 200 section samples, 4x area coverage while fitting, and 8x for final proxy checks, with pixel phase -0.5.
These are measured case settings, not defaults for another car, camera, or image size.
Measure sampling convergence and proxy-to-native disagreement for the current model.
Use native rendering for final acceptance even when the calibrated proxy exceeds the target.

See shell_projection.py (source-project artifact; not bundled),
shell_raster_calibration.py (source-project artifact; not bundled), and
shell_camera_coverage.py (source-project artifact; not bundled).
