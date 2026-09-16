# Draft and conservative release envelopes

Draft and tool separation are different checks. The recorded revision uses a
user-selected 3-degree provisional draft on formerly vertical formed straight
walls and closed-bead flanks. Existing 30/45-degree ramps and corrugation walls
remain unchanged. Cut faces and the varying tangent angles in bend radii are
outside that straight-wall draft criterion. Do not promote 3 degrees to a
universal manufacturing rule.

For a wall between horizontal levels separated by H, set beta = 90 - draft.
With midsurface radius Rm = Ri + t/2:

```
wall tangent length = (H - 2*Rm*(1 - cos(beta))) / sin(beta)
wall radial advance = 2*Rm*sin(beta) + tangent_length*cos(beta)
```

Keep both sheet faces at exact normal offsets +/- t/2. Recompute mounting
holes from the new ledge datum. Preserve an outside housing envelope by
reducing its radial-mapping rectangular core, rather than scaling the sheet.
For the neck opening toward +Z, the neck radius grows upward; the cover skirt
opens toward -Z. State the release direction for each feature. Returns and
two-ended bridge interiors still require separate tool access.

## Native signed-field regression

Build 42926's CAD Revolve returned incorrect cavity and far-field signs for
the tested bead with t=1.5 mm, Rm=2.25 mm, height=6 mm and 87-degree bends.
The block state was e_OK. Moving that revolution to Z0 did not cure it; an
outer-minus-inner pair also retained a bad far field. These are recorded
findings for that construction, not a blanket claim about all revolutions.

An extruded exact meridian provides a reliable 2D section field for this case.
Map X to radial distance, Y to the extrusion midplane, and Z to the local bead
height. In the known flat crown region, clamp the mapped radius to half the
crown tangent width to avoid the artificial cap on the meridian's axis.
This clamp does not change the crown zero surface. Test the face, interior,
cavity and far-field signs, then the full mesh topology and analytic volume.
Keep rejected evidence and distinguish the successful construction from an
unverified attempt to fix the same failure.

## Conservative envelope construction

The helper operates on an accepted native triangular mesh, not a raster depth
snapshot. Each triangle contributes its maximum/minimum Z to every 1 mm XY
cell overlapped by its projected AABB. Expand maxima/minima by one cell, then
set each grid vertex to the extrema of its adjacent cells. Every triangulated
tool cell remains conservatively outside the contributing sheet triangles.

The recorded envelopes add 0.75 mm vertical allowance. One-cell expansion
covers every projected point within 0.5 mm of each triangle AABB; other points
are already at least 0.5 mm away laterally. These bounds establish at least
0.5 mm spatial separation relative to the native tessellation. Check every
facet/cell assignment, not only mesh vertices or a few depth pixels. Closed
upper/lower shells open along +Z/-Z. The recorded offsets are 0, 2, 5 and
10 mm; further travel along those axes monotonically increases separation.

Nearest filling of holes produces forming envelopes, not piercing punches.
The envelopes avoid inaccessible undercut interiors, so this result does not
establish usable contact dies or a feasible forming sequence. The intermediate
sheet motion remains prescribed. A mesher setting is not an independently
verified error bound to exact CAD. Keep these distinctions in the GIF, report
and share caption.

```
uv run --locked python .agents/skills/ntop-sheet-metal/scripts/build_drafted_sheet_metal.py --case all --out WORK/drafted
# Import, save, evaluate, export and validate matching native meshes first.
uv run --locked --group render python .agents/skills/ntop-sheet-metal/scripts/animate_drafted.py --root WORK/drafted
```

The referenced supplier guidance is [JUMAI TECH's deep drawing design tips](https://www.deepdrawtech.com/deep-drawn-metal-stamping-design-tips/).
It describes 1-3 degree taper as potentially helpful while noting that straight
walls are possible. Material, surface finish, draw depth and tooling sequence
remain process-specific decisions. All dimensions in this revision are
authored study choices.
