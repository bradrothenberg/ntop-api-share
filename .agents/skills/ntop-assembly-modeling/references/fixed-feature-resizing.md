# Fixed-feature resizing

This contract generalizes the KestrelSAT span-map lessons. It supplies equations and verification requirements, not a full assembly or a native map implementation.

The earlier native resizing sweep used a previous reconstruction on nTop 5.54.2. It does not certify replacement CSG geometry. The bundled [build 42594 pilot](generic-pilot.md) checks a separate width-controlled part; it does not implement this map.

## Select stretch regions

Measure the source in its assembly coordinate frame. Identify the intervals where each coordinate can stretch. Keep intervals sorted, disjoint, and nonzero in length. Protect the complete bounds of features that must move rigidly.

For rails, a constant-section axial span can change while the transverse section stays fixed. For panels, protect the thickness direction. A cylindrical face needs protection on each transverse axis. Oblique and curved features need explicit checks rather than a name-based rule.

The source analysis used measured feature bounds, guards, and minimum gap lengths. Choose those values from the new source and required tolerances. Do not transfer the satellite's dimensions or gap thresholds to an unrelated model.

## Coordinate map

Apply this map independently to each eligible axis. All coordinates and dimensions must use the same length unit. For allowed source intervals `[a_i, b_i]`, define:

```text
l_i = b_i - a_i
L = sum(l_i)
w_i = l_i / L
C_i = sum(l_j for j before i)
delta = APPLIED - nominal_dimension
clamp01(t) = max(0, min(1, t))

forward(x) = x + delta * (sum(w_i * clamp01((x-a_i)/l_i)) - 1/2)
A_i = a_i + delta * (C_i/L - 1/2)
W_i = l_i + delta*w_i
inverse(y) = y + delta/2 - delta*sum(w_i*clamp01((y-A_i)/W_i))
```

Require `L > 0` and `W_i > 0`. An axis without allowed intervals stays rigid; do not divide by a zero span.

The forward slope is `1 + delta/L` inside allowed intervals and 1 outside them. Protected regions translate with constant displacement. The two outer sides move by half the added span, which preserves their bounding-box center.

The recorded design uses `LIMIT = nominal_dimension - L/2` and `APPLIED = max(SIZE, LIMIT)`. At that minimum, allowed intervals retain half their original width. This is a map constraint, not a manufacturing or structural qualification. Read the applied value after an edit, including requests below the minimum.

Compose the original implicit field with the inverse map. Preserve the recorded order: local body, source rotation if needed, source translation, global inverse remap, mapped bounding box. Share the assembly maps across instances. A mapped field is not necessarily a signed-distance field.

## Protect edited features

A feature can distort when its coordinate bounds cross an allowed stretch interval. Constant radius at each corner does not preserve a whole opening, logo, or mounting pattern. Protect its complete bounds when its full shape and spacing must stay fixed.

Before adding, moving, or enlarging geometry, check that displacement stays constant across each protected axis. Rebuild protected intervals when this fails. A source-derived map does not automatically protect later edits.

The recorded design has no upper clamp. Large requests concentrate extension into the available spans. Map monotonicity alone does not prove clearance, fixed cell pitch, assembly fit, or strength.

## Verify the delivered geometry

First check `inverse(forward(x))` and `forward(inverse(y))` at interval endpoints, nearby points, and independent interior and exterior samples. Include nominal, expanded, contracted, one-axis, minimum, and below-minimum cases. Record tolerances and maximum numerical errors.

Then test the final native parts through their actual custom-block boundary. Read applied controls, count bodies, check placements, and measure holes and wall thicknesses on native exports. Bracket both sides of important boundaries with native field probes. Arbitrary field magnitudes do not measure physical distances.

Keep map algebra, earlier native sweeps, current source fidelity, final assembly evaluation, and GUI updates as separate evidence. Bind new results to the delivered family definitions, assembly, inputs, and export settings. Refresh display snapshots after geometry edits.
