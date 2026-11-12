# Spline DF sections

Recorded on prototype build 42926 for a cubic curve. Run the pilot again on any other
build, and treat anything outside the pilot as unverified.

## Blocks

| Purpose | Block identifier | Inputs, in recipe order |
|---|---|---|
| Section field | `spline_implicit<list<vector_field_2d>,integer,vector_field_2d>[5.53.0]` | control points, degree, query point |
| Control or query point | `vector_field_2d_from_components<real_field,real_field>[5.31.0]` | first and second section coordinate |
| Guide curve | `spline_by_control_points<list<point>,integer>[5.20.0]` | control points, degree |
| Guide value field | `curve_axis_distance<curve_interface,axis,vector>[5.30.0]` | curve, axis, direction |
| Guide at another coordinate | `remap<real_field,real_field,real_field,real_field>` | field, new X, new Y, new Z |

The input order is what the recorded recipes use. Read the live input names from the
installed build with the Notebook API skill instead of assuming them.

## What the block returns

The Spline DF output is an implicit body. Dividing it by one metre gives a plain number
field, which is easier to combine with other fields:

```text
f(u, v) = signed distance in the section plane from (u, v) to the curve
```

- Knots are clamped and uniform. With K control points a cubic curve has K - 3 spans. It
  starts at the first control point and ends at the last, tangent to the first and last
  legs of the control polygon.
- The sign is positive on the left of the direction of travel. Clockwise travel around a
  body, seen with the first section coordinate to the right and the second up, keeps the
  inside on the right and gives a negative-inside field.
- An open curve does not stop. It continues as straight rays along the end tangents, so
  an open section divides the whole plane. Use this on purpose: let a roof section run
  on past the side wall and trim it with the wall. Keep the rays from crossing each other
  or the curve inside the region you use.
- The curve is closed when the first and last control points coincide. Put the seam in
  the middle of a straight run so the clamped ends meet without a kink.
- The value is a planar distance at the current loft coordinate. It is not the 3D
  distance to the lofted surface. A layer of constant field depth is thinner where the
  section changes quickly along the loft. Measure thickness where it matters.

The recorded cases noted the opposite sign convention for the Conic DF block
(`conic_implicit`) and did not verify it natively. Pilot it before use.

## Units

The recorded graphs keep every field dimensionless in metres and convert at the block
boundary:

```text
coordinate   = plane scalar field / 1 m
control point = vector_field_2d(a * 1 m, b * 1 m)      a, b are dimensionless fields
constant     = a length literal directly
section      = Spline DF / 1 m
body         = set bounding box(field * 1 m, box)
```

Give every body an explicit bounding box that contains it with a margin of a few cells.
A box that touches the body clips it, and the cap face it leaves is not part of the design.

## Guides as native fields

A guide g(u) on [u0, u1] is a cubic B-spline function. Natively it is a spline curve
drawn as the graph of g, read back with the axis distance:

1. Control points at the Greville abscissae: `(u_i, g_i + offset, 0)` with
   `u_i = u0 + (u1 - u0) * (t[i+1] + t[i+2] + t[i+3]) / 3` for the knot vector t. With
   these abscissae the curve is exactly the graph of g.
2. Distance of that curve from the X axis, measured in the Y direction, minus the
   offset. The offset keeps the curve on one side of the axis, because the distance is
   unsigned.
3. The result is g as a field of the world X coordinate. To use g along another
   coordinate or an expression, remap it: new X is the argument times one metre, new Y
   and Z are zero.

Clamp the argument to [u0, u1] before the remap. The checked build asserted when a guide
spline was sampled far outside its range.

`surfacing.py` writes exactly this construction (`Guide`, `Recipe.emit`).

## Half sections and symmetry

For a symmetric body evaluate the section with the absolute lateral coordinate and draw
only one half of the curve. The half curve must meet the centreline at a right angle:
give the first two control points the same height, and the last two as well if the
curve returns to the centreline. The mirrored surface then has no crease on the
centreline. Check the curvature across the centreline as well, since equal height of
two control points fixes the tangent and not the curvature.

Every other field that depends on the lateral coordinate needs the same care. A blend
width or a sweep that is linear in the absolute coordinate has a kink at the centreline.
Use the square of the coordinate for such terms.

## Host evaluation

`surfacing.spline_distance` reproduces the block: a dense sample of the curve, then a
safeguarded Newton search for the closest parameter, the sign from the left normal, and
the end rays for open curves. Lessons from making it reliable:

- Use about eight samples per span and switch to a Gauss-Newton step where the second
  derivative term is not safely positive. Uneven control spacing makes plain Newton
  jump to the wrong span.
- On a closed curve the seam is one point with two parameters. When the search stops at
  one end, repeat it from the other end and keep the nearer result.
- Long straight edges of a region need extra collinear control points. Without them
  the parameter speed varies strongly and the search fails. In the recorded case a mask
  had errors of 53 mm without subdivision and about 1 mm with it.

## Pilot results

`loft_pilot.py native` on build 42926, 12 November 2026, 20 000 sampled native mesh
vertices per body against the host field:

| Pilot body | Native conversion | Largest distance | Mean distance |
|---|---|---|---|
| Lofted half section with two guides | 55 s | 0.022 mm | 0.003 mm |
| Open arc with end rays | 15 s | 0.022 mm | 0.002 mm |
| Closed region plate | 6 s | 0.075 mm | 0.001 mm |
| Two surfaces with a compact C2 blend | 17 s | 0.020 mm | 0.002 mm |

The host evaluator in this skill agrees with a separate GPU implementation of the same
graph to within 1e-14 m on the three bodies with field-valued or open sections.
The pilot proves the sign, the rays, the closed case, the guide construction and the
blend on these bodies. It does not prove a different degree, the Conic DF block, or the
accuracy of a much larger graph.
