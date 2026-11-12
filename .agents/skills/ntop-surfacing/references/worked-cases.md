# Worked cases

Two models built in November 2026 with prototype build 42926, both authored as native
implicit fields through the Notebook API. Their measurements explain the method. They
are not defaults for another shape.

## Case A: open-wheel race car concept

156 named bodies in eight notebook sections. No mesh or CAD was imported.

Method:

- Bodywork from guide-driven superellipse lofts along the length: tub and nose,
  sidepods, engine cover, airbox spine. Guides give half width, top, bottom, widest
  height and two section exponents.
- Guides fitted to shape-preserving curves through hand-chosen stations.
- Lofts joined by smooth unions with widths from 36 to 140 mm.
- Inlet lips as single swept guide curves. Paint zones and lettering as partitions of
  the body field.

What went wrong and what fixed it:

| Review comment or finding | Cause | Fix |
|---|---|---|
| Inlet wobbly, then bumpy in side view | Lip edges and outer wall built from separate trims | Each lip edge from one guide curve. Outer wall removed. The inlet floor rises to meet the roof at the corner |
| Jagged ridge at the upper lip root | Pod loft hard clipped in the visible skin, leaving a step and a blunt root | Loft carried on inside the chassis. Edge curve continued into the chassis. Compact C2 blend with a width that opens with height. Root stations calibrated to a power law |
| Dashed crease along loft crown lines | Numerical floor in the superellipse norm, a groove 0.3 mm deep | Larger term factored out of the power sum |
| Wavy underside between tub and pod | Pod section stopped at the tub side | Pod section carried into the tub |
| Knife edge on the engine cover flank | Tub loft ended on a flat face | Loft extended and capped inside the cover |
| Small detached blobs at loft tips | Tip of a secondary loft poked through its neighbour | Tip lowered and buried |
| Bulge past loft ends | Smooth union beyond the end cap | Hard clip at the loft ends |
| NaN normals | Power with base zero, square root of zero | Base clamp and a small offset under roots |

Measured results:

- Lip root outline within 0.30 mm of one power law over 420 mm.
- Section curvature at the root bounded on the sampled cuts after the repair.
- All 156 parts built with state OK. 40 native field probes agreed with the host field
  within 1e-9 m. A design control changed through the API moved a probe to the value of
  the host rebuild.
- All parts exported natively. Worst native vertex 0.98 mm from the host field, most
  parts within 0.1 mm.
- A later attachment check found 54 loose pieces on the finished car and all were fixed.

Limits: an exterior concept with design-input dimensions. Fairness was sampled on
chosen cuts. No aerodynamic or structural validation is implied.

## Case B: five-door body from a dimension drawing

185 bodies. The body envelope is built from Spline DF surfaces, and every exterior part
is a layer of that envelope cut by region masks.

First attempt, abandoned:

- Two lofts. A plan section with 20 control points lofted over 24 height levels, and a
  transverse section with 17 rows lofted along the length through guides with 46
  control values. One smooth intersection joined them.
- The silhouettes matched the drawing. The previews showed dimples at the front upper
  corners where rows converged, a pinched ridge up the rear pillar, and ripples.
- Several rounds of parameter repair did not cure it. The zebra check showed the cause:
  surfaces fitted through many traced keys.

Rebuild:

- Six primary surfaces (tub, deck, canopy, windscreen, backlight, floor) and five seams
  with chosen widths from 14 to 90 mm. See the primary surfaces reference.
- 16 guides with 4 to 24 control values. Deviations from the keys 0.5 to 5.7 mm, all
  recorded.
- The plan outline replaced by a designed curvature history of 15 numbers, 17.7 mm from
  the trace at most, mainly at details it was meant to ignore.
- Windscreen and backlight as parabolas with four control points each.
- Analytic nose and tail profiles.

Measured results:

- Zebra stripes even on roof, glass, hood, sides and pillars. Remaining stripe movement
  on the front and rear faces follows designed features.
- Silhouette close to the drawing in all four views after separate calibration of each
  view.
- Host preview of the envelope: about one million triangles at 8 mm cells in under ten
  seconds on a GPU.
- Section pilots on this build: native mesh vertices within 0.02 mm of the host field
  for lofted and open sections.
- All 185 parts exported natively, 129 meshed and 56 reflected twins. Painted body 6.5
  million triangles, 0.94 mm from the host field at a 6 mm tolerance. One lamp part
  reached 4.2 mm against a tolerance of 1.5 mm and was flagged.

Limits: the full notebook import of the body section is not recorded as complete in the
files reviewed for this skill. The wheels section imported with all 36 parts OK. The
zebra check is a visual inspection of a host mesh, not a Class A acceptance. Hidden
surfaces are design choices.

## What transfers

- Decide the primary surfaces before fitting anything.
- Few control values and a recorded deviation beat a close fit.
- Put feature lines at intersections and give each seam its own width.
- Check reflections early, on the envelope alone.
- Calibrate against the finished surface, after all blends.
- Prove semantics with a pilot, freeze the geometry, then pay for the native build once.
