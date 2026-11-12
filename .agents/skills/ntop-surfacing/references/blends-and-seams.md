# Blends and seams

## The compact quartic blend

For two fields a and b and a width k in field units:

```text
q     = max(1 - |a - b| / k, 0)
sminq = min(a, b) - k * q^3 * (4 - q) / 16
smaxq = -sminq(-a, -b, k)
```

Inside the support, with s = (a - b) / k and |s| < 1, this is the even polynomial

```text
sminq = (a + b) / 2 - k * (3/16 + 3 s^2 / 8 - s^4 / 16)
```

Properties:

- Outside |a - b| >= k the result is exactly min(a, b). Surfaces away from the seam are
  not moved at all. A plain polynomial or exponential smooth minimum moves them slightly
  everywhere.
- Value, first and second derivatives match min(a, b) at the edge of the support, so
  the blend is C2 there when a and b are smooth.
- Where a = b the result lies 3k/16 below both. A smooth union therefore adds material
  along the seam and a smooth intersection removes it.
- k may be a field.

The width is not a fillet radius. The size of the visible fillet depends on k and on the
angle at which the two surfaces cross: a shallow crossing spreads the same k over a
wide band. The result is also only as smooth as the inputs. A C2 formula does not make
a regular surface where the inputs have a crease or the combined gradient vanishes.

For negative-inside fields `sminq` is a smooth union and `smaxq` a smooth intersection.
Subtract with `smaxq(a, -b, k)`.

## Choosing widths

Widths recorded for a body about 4.7 m long:

| Seam | Width | Character |
|---|---|---|
| Belt line and cowl (deck to greenhouse) | 14 mm | crisp line |
| Hood edge and shoulder (upper body to side) | 26 mm | defined edge |
| Same seam over the rear wheel | 52 mm | soft haunch |
| A-pillar (windscreen to roof and side glass) | 60 mm | rounded pillar |
| Sill (body to floor) | 70 mm | soft turn-under |
| D-pillar (rear glass to roof and side glass) | 90 mm | broad rounded corner |

Start from the character the seam should have, set the width, then inspect the section
across the seam and the zebra stripes along it.

## Widths that vary

One seam often needs to be crisp in one place and soft in another. Make k a smooth
field:

```text
seam(x) = 0.026 + 0.026 * smootherstep(2.0, 2.9, x)
```

Recorded uses:

- Along the length: crisp shoulder at the front doors, soft over the rear wheel.
- With height above an edge: a sidepod lip blend that stays compact at lip height, so
  the planform corner stays tight, and opens above the lip so the lip top fairs into the
  body side over a broad fillet. It returns to the compact width further aft.

Drive the width by a coordinate that separates the two needs. Width growth driven only
by distance along the seam left valleys in a related aircraft case even though the
weights were C2. A varying width must itself be smooth, including across a symmetry
plane, and it must stay positive.

## Order of operations

Nested blends are not associative. Decide the order from the design and keep it:

1. Join the surfaces that form one visual volume first (roof with windscreen).
2. Join volumes next (greenhouse onto deck).
3. Apply the trims that should cut everything last (body sides, floor).

Changing the order moves the seams by a fraction of the widths involved. If two seams
meet at a corner, the wider blend decides the corner. Inspect corners where three
surfaces meet from at least two views.

## When a seam pinches, waves or bulges

| Symptom | Usual cause | Repair |
|---|---|---|
| Pinched ridge along a seam | Surfaces cross at a very shallow or reversing angle | Reshape one surface so it crosses the other steadily, then blend |
| Wavy seam line | One surface ripples, or the crossing angle varies | Fix the guide of the rippling surface. The seam is the intersection curve and shows every wave |
| Lump at a three-surface corner | Blend supports overlap with different widths | Reorder the blends, or change the surfaces so only two meet there |
| Bulge past the end of a loft | Smooth union reaches beyond the end cap | Hard clip the loft at its ends before the union |
| Blunt, stepped root of a lip | A hard clip passes through the visible skin | Carry the surface on inside the neighbour and blend. No hard clip through a visible skin |
| Groove along a seam after a smooth intersection | Width too large for a thin part | Reduce k below the local thickness |

## Cut edges of thin parts

A sharp maximum that cuts a thin skin meshes with a ragged edge. Blend the cut with
`smaxq` and a radius of at least two mesh cells, or cover the edge with a bead:

```text
bead = length2(mask, E + offset) - r
```

where mask is the region field whose zero is the cut line and E the envelope field. The
bead is a round rod that follows the cut line at a set depth under the surface.
