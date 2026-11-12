# Fair guides

A guide is a function of the loft coordinate that drives one coordinate of one control
point. The surface is only as fair as its guides.

## Why fitted keys ripple

Stations read from a drawing or a photograph carry scatter of a millimetre or more. A
guide with many control values follows that scatter. The deviation report looks better
and the surface looks the same in a shaded view, but its curvature now changes sign
every few hundred millimetres and reflections ripple.

`python scripts/example_body.py report` shows this on the same 41 keys with about one
millimetre of scatter:

| Crown guide | Control values | Largest deviation | Inflections | Curvature extrema |
|---|---|---|---|---|
| Fair | 7, penalty 0.02 | 1.95 mm | 1 | 1 |
| Traced | 24, no penalty | 1.10 mm | 6 | 13 |

The traced guide is closer to the keys and is the worse surface. `example_body.py zebra`
renders both.

## Fit with few control values

`Guide.fit(name, us, vs, n, u0, u1, lam)` solves a least squares problem for n control
values of a clamped uniform cubic B-spline:

```text
minimize  sum (g(u_k) - v_k)^2  +  lam^2 * sum (third difference of control values)^2
```

- Start with n between 5 and 9. Raise n only when the deviation exceeds the tolerance
  in a region where the reference is trusted.
- The third-difference penalty favours slowly changing curvature. Values around 0.01
  to 0.02 worked for guides in metres over spans of one to five metres. Scale it with
  the data.
- Record n and the largest deviation for every guide. The recorded five-door body has
  16 guides with 4 to 24 control values and deviations from 0.5 to 5.7 mm.
- Read the fairness with `Guide.fairness()`: the number of inflections and of curvature
  extrema. Compare them with what the design needs. A hood profile needs no inflection.
  A profile over a wheel arch may need two.
- Guide names must be unique. Each becomes a named spline in the notebook.

Use a low-degree polynomial where the face is that simple. A roof centre height is well
described by a cubic, a glass width by a quadratic. Fit the polynomial to the keys, then
represent it exactly as a guide.

Use an analytic profile where the shape has a clear description. The recorded nose
profile is a sum of two soft ramps: foremost at bumper height, leaning back above it,
swept back below it. Such a profile is fair by construction and has a few numbers to tune.

## Shape-preserving guides

The race car fitted each guide to a shape-preserving (PCHIP) curve through its stations,
sampled densely, with about 1.6 control values per station. This never overshoots
between stations and suits hand-chosen stations that are already smooth. It follows the
stations closely, so it also follows their errors. Use it for stations that are design
inputs. Use the penalised fit for stations that are measurements.

## Design the curvature when the outline matters

A plan outline is seen in every reflection of the body side, so its curvature history
must be simple. For the recorded body the traced outline, fitted with 24 control
points, oscillated in curvature and put visible drips into the front face. The repair
did not smooth the fit. It replaced the outline:

1. Write the curvature along arc length as a short sum: a light crown across the front,
   one bump for the front corner, a nearly straight side, one bump for the rear corner,
   a light crown across the back. Fifteen numbers in the recorded case.
2. Integrate curvature to heading and heading to position.
3. Fit those numbers to the traced outline by least squares on the normal distance,
   with end conditions for closure and heading.
4. Remove the remaining closure error with a smooth correction and store the points.

The result deviated from the trace by up to 17.7 mm, mostly at details the outline was
meant to ignore, and it is fair by construction. Then fit the section control net to
this outline, with:

- Mirror conditions built into the unknowns: the first two control points share their
  x, as do the last two, and the end points lie on the centreline.
- A fit parameter weighted toward the corners, so the corners receive more control
  points without hand placement.
- Deviation measured as geometric distance to the curve. Deviation at equal parameter
  values is misleading.

## Calibrating an edge to a law

Where a feature must grow out of another surface, state the law and solve for the
stations that produce it. The race car's sidepod lip root is the recorded example:

- Measure the finished outline at lip height and the outline of the chassis alone. The
  difference is how far the lip stands proud.
- Fit one power law to the established part of the lip: `proud = A * ((x - x0) / L)^n`.
- Move the root edge stations by the error against that law, keep them in order, and
  repeat. In the recorded case this brought the outline within 0.30 mm of the law over 420 mm.

The measured quantity is the finished surface, after all blends. Moving guide stations
until the guide looks right does not make the surface right.

## Checklist for one guide

- Few control values, deviation recorded, inflections counted.
- No kink at a symmetry plane: an even function of the lateral coordinate, or zero slope.
- Argument clamped to the guide range.
- End behaviour chosen on purpose. A clamped guide is constant beyond its range.
- Checked at stations between the keys, not only at the keys.
