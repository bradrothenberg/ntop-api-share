# Primary surfaces

A primary surface is one large face of the shape, described by the simplest section that
can carry it. The whole envelope is a boolean of a handful of them.

## Choosing sections and loft directions

For each face ask in which plane its section is a simple arc, and loft along the
remaining axis:

| Face | Section plane | Loft along | Typical control points |
|---|---|---|---|
| Body side with nose and tail (a plan outline) | plan (x, lateral) | height | 16 to 24, because the outline turns two corners |
| Hood, deck, shoulder shelf | transverse (lateral, z) | length | 6 to 9 |
| Roof with side glass | transverse (lateral, z) | length | 6 to 9 |
| Windscreen, rear glass | side profile (x, z) | lateral, through its square | 4 |
| Underside | a height guide along the length | none | not a section |
| Closed tube: nose cone, pod, cover, spine | superellipse or closed spline | length | 4 guides |

A section does not have to stop where the face stops. An open Spline DF runs on along
its end rays, so make each surface larger than the face it provides and let another
surface trim it. The trimmed edges are then intersections of smooth surfaces, which is
where a designed object has its feature lines.

## Recorded decomposition: five-door body

Six primary surfaces, in the frame X rearward, Y to the right, Z up:

```text
Tub         plan section (x, |y|) lofted along z: front face, body sides, tail
Deck        transverse section (|y|, z) lofted along x: hood, fender tops, shoulder shelf
Canopy      transverse section (|y|, z) lofted along x: roof, cant rail, side glass
Windscreen  profile section (x, z) lofted along |y|
Backlight   profile section (x, z) lofted along |y|
Floor       height guide along x

greenhouse = smaxq(Canopy, Windscreen, 0.060)        A-pillar
upper      = sminq(Deck, greenhouse, 0.014)          belt line and cowl
upper      = smaxq(upper, Backlight, 0.090)          D-pillar
body       = smaxq(upper, Tub, seam(x))              hood edge and shoulder, 26 to 52 mm
body       = smaxq(body, Floor, 0.070)               sill
```

`smaxq` is a smooth intersection and `sminq` a smooth union for negative-inside fields.
Every feature line of the body is one of these five seams. No section contains a
crease.

How each section gets its shape:

- Tub. One fair plan outline gives the base control net. Each control point moves with
  height by a small number of profile guides: a nose profile and a tail profile shift
  the points near the ends in x, and three side profiles (front, doors, rear) scale the
  half width. Weights that fade along the outline decide how much of each profile a
  control point receives. The plan outline keeps one curvature history at every height.
- Deck. Nine control points from five guides: centre height, shoulder height and half
  width, crease height and half width. The points between are fixed fractions of those,
  and the last two continue the shelf in a straight line past the crease so the Tub
  trims it.
- Canopy. A roof crown, a theoretical corner where roof and glass planes would meet,
  and a glass run with a small outward bulge. The glass plane comes from a half width
  at a reference height and a constant lean.
- Windscreen and backlight. A parabola through the measured profile, written as a
  cubic Bezier (four control points). Each control point sweeps back with the square of
  the lateral coordinate, which gives plan curvature and stays smooth on the centreline.

## Recorded decomposition: open-wheel race car

Closed tubular bodies do not need a spline section. The recorded car uses a
superellipse section driven by guides along the length:

```text
a  = |y - yc(x)| / w(x)
bu = max((z - zw(x)) / (zt(x) - zw(x)), 0)       above the widest height
bd = max((zw(x) - z) / (zw(x) - zb(x)), 0)       below it
n  = norm(a, bu, pt(x)) + norm(a, bd, pb(x)) - a
f  = (n - 1) * scale
norm(a, b, p) = m * ((a/m)^p + (b/m)^p)^(1/p),  m = max(a, b) + 1e-12
```

Guides give half width, top, bottom, widest height, and the two exponents. A higher
exponent makes a boxier section. Tub and nose, sidepods, engine cover and airbox spine
are separate lofts joined by smooth unions.

Lessons from that car:

- Factor the larger term out of the power sum, as in `norm` above. A numerical floor
  inside the power function otherwise leaves a groove about 0.3 mm deep along the crown
  line of every loft.
- Close a loft with an elliptic cap factor on width and height over a chosen length.
  Then clip hard at the loft ends, because a smooth union can bulge past the last station.
- Start and end a loft inside its neighbour. A loft that ends on a flat face inside
  another body leaves a knife edge or a step where the face meets the skin.
- Give a swept lip one guide curve for its edge. Lip edges built from separate pieces
  wave.

## Rules that held in both cases

- Few sections, few control points. Add a control point only for a named reason.
- Never let two control rows meet. Where a face narrows to nothing, such as a shelf
  fading into a nose, let the rows converge smoothly and stop the face with a trim.
  Clamping one row against another with a minimum makes a dimple.
- Keep section control polygons convex where the face is convex. An S in the polygon is
  an inflection in every reflection.
- Space control points evenly in arc length, and add points at tight corners by
  reweighting the fit parameter, not by hand.
- Decide what each surface is for before fitting anything. In the recorded case a first
  body made from two large lofts matched the drawing and failed the zebra check. No
  amount of parameter repair fixed it. Rebuilding it from six simple surfaces did.
