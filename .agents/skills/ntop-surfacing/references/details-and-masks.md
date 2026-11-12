# Details and masks

Once the envelope field E is fair, do not model parts next to it. Cut them out of it.
Every panel, pane and trim piece is a layer of E limited by a mask, so all parts share
one surface and no part can drift from its neighbour.

## Layers

```text
skin(E, lo, hi) = max(E - hi, lo - E)        the shell lo <= E <= hi
```

lo and hi are offsets in field units, negative inward. Recorded values for a car body:

| Part | Layer | Note |
|---|---|---|
| Painted shell | -30 mm to 0 | minus all openings |
| Glass | -7 mm to -2 mm | 2 mm under the paint surface |
| Glass border print | -12 mm to -7.2 mm | behind the glass |
| Seal band | -16 mm to -7.6 mm | dark band behind glass edges |
| Cladding | -20 mm to +2.5 mm | stands proud of the paint |
| Lamp lens | -4.5 mm to +0.5 mm | over a housing at -30 mm to -12 mm |

E is a planar section distance, not a true distance, so a layer of constant field depth
does not have constant thickness. Where thickness matters, measure it along the surface
normal and report it.

## Region masks

A mask is a closed Spline DF in one view plane (side, front or plan), extruded through
the body, negative inside:

```python
window = region('Window outline (side view)', [(0.45, 0.50), (0.62, 0.78), (1.30, 0.80), (1.62, 0.52)], X, Z, r=0.04)
glass  = fmax(skin(E, -0.006, -0.002), window, 0.3 - AY)     # limited to one side of the body
```

`rounded_polygon` turns polygon vertices into control points:

- Three control points per corner: one on each edge at the corner radius, and the
  corner itself. The straight runs between corners stay exactly straight.
- Long edges receive extra collinear points so the parameter speed stays even.
- The loop is ordered clockwise, which is negative inside.
- The loop starts and ends at the midpoint of its longest straight leg, so the clamped
  ends meet without a kink.

Offset a mask by adding to it: `mask - 0.016` grows a region by 16 mm, `mask + 0.020`
shrinks it. Because the mask is a planar distance, the offset is exact in the view plane.

A feature seen in two views is the intersection of two masks, for example a lamp from
its front outline and its side outline: `fmax(front_mask, side_mask)`.

Limit every mask to where it applies. A side-view mask extruded through the body cuts
both sides and anything in between. Add a half-space on the lateral coordinate or along
the length.

## Panel gaps

A gap is a shallow groove in the paint surface, driven by the unsigned distance to a gap
curve. Draw the curve as an open Spline DF in its view plane, take the absolute value,
and limit it to the stretch where the gap runs:

```text
gap     = max(|spline2d(curve points)|, limits...)
gaps    = min(all gap fields)
groove  = (1 - smootherstep(0, 0.0075, gaps)) * 0.0032
outer   = E + groove                         the paint surface, 3.2 mm deep in the gaps
```

Add a dark line inside the groove as a thin rod: `length2(gap, E + 0.0024) - 0.0023`.
Cut gaps only inside finished bodywork. Fill that crosses an opening leaves loose specks.

## Openings and recesses

- Openings (wheel arches, glass apertures, lamp apertures, intakes) are the minimum of
  their masks. Subtract that one field from the shell.
- A recess is a mask intersected with a depth: `smaxq(E, -max(mask, -(E + depth)), k)`
  sets a pocket of that depth into the surface with a rounded rim.
- A proud feature (a bead, a strip, a badge) is a layer above the surface limited by a
  narrow mask, or a bead along a mask edge.

## Rules that kept meshes clean

- Let glass run unbroken under pillar covers and trim the cover. Do not butt two parts
  edge to edge. The meshes never meet exactly and the gap shows the lining behind.
- Put a dark seal band behind every glass edge, so a light interior lining cannot show.
- Blend cut edges of thin layers, or hide them under a bead.
- Give small parts their own tight bounding box and a finer mesh size than the body.
  A box that touches the part clips it.
- Check that every part touches or overlaps a neighbour. Sample each part, split it into
  connected pieces, and report pieces that touch nothing. One recorded check found 54
  loose pieces on a car that looked complete.
- Check the orientation of a local frame before placing a flat feature on it. With
  `w = u x v`, a screen or badge can face into the body.

## Mirrored parts

Build left and right parts from one field with the absolute lateral coordinate where
they are symmetric, and split them with a half-space when they must be separate bodies.
For export, mesh the right-hand part natively and reflect its mesh for the left-hand
twin. Check the reflected mesh against the left part's own field.
