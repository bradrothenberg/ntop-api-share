# PyVista figures for high-order (curved) meshes

These notes retain recorded rendering recipes from the local report skill.
They are not new measurements or verification on the current host.

Battle-tested recipe for rendering order-3 gmsh v2.2 meshes (NekMesh
OutputGmsh: tri10=21, tet20=29, prism40=90, pyramid30=118) with pyvista
instead of gmsh. Validated on the AGARD-C run_001 report (2026-07-04).

READY-MADE MODULE: `scripts/ho_mesh_render.py` in this skill implements
everything below (read_msh, build_linear_grid, build_ho_wall,
build_wall_wireframe, build_prism_surfaces, add_wire) - import it into a
case-specific shots script instead of rewriting. Choose cameras and
figure composition from the current report's measured data.

## What renders as true curved geometry, and how

- **Cubic wall triangles (tri10) -> VTK Lagrange triangles.** The gmsh
  tri10 node ordering (corners; 2 edge nodes per edge in edge order 0-1,
  1-2, 2-0; interior) is IDENTICAL to VTK's Lagrange-triangle ordering, so
  all 10 nodes pass through with no permutation. Tessellate with
  `grid.extract_surface(nonlinear_subdivision=3)`.
- **Cubic prisms (prism40) -> self-tessellated faces.** Do NOT map to
  VTK's Lagrange wedge: the gmsh->VTK volume-cell permutations differ and
  VTK's Lagrange wedge/pyramid support is its weakest area - a subtly
  wrong permutation renders plausible-but-wrong geometry. Instead:
  1. Derive the gmsh prism40 node ordering EMPIRICALLY: write ONE linear
     unit prism .msh, run a .geo with `Merge; SetOrder 3;
     Mesh.MshFileVersion=2.2; Save;` (batch Save works; only Print needs
     the GUI), and read the 40 node coordinates back - on a straight unit
     prism, coordinates == parametric coordinates. Hardcode the table.
  2. Classify the 5 faces (2 cubic tris, 3 bicubic quads) and 9 edges by
     coordinate filters on the table (w=0, w=1, v=0, u=0, u+v=1).
  3. Tessellate each face through an exact Vandermonde interpolant:
     complete-cubic monomials for tri faces (10 nodes), bicubic for quad
     faces (16). Precompute `S = M_samples @ inv(M_nodes)` once per face
     type; per face it is one small matmul `xyz = S @ face_node_coords`.
     Emit plain linear sub-triangles - VTK never sees a volume cell.
  Validation: the prism shell must seat seamlessly against the
  independently-rendered Lagrange-triangle wall; a crack or spike means
  the node table is wrong.
- **Element wireframes** are the cubic edge curves (nodes at t = 0, 1/3,
  2/3, 1) sampled by Lagrange interpolation into polylines, deduped by
  corner pair. Never `show_edges=True` on a subdivided surface - it draws
  subdivision-fragment edges, not element boundaries.
- **Tets/pyramids linear** is fine: corner orderings match VTK directly,
  and volume-cell curvature is confined to the wall-adjacent layer
  (sub-pixel at section-figure scale). Say so in the caption.

## Reading and scale (AGARD-C 211 MB msh, 2026-07-05)

- **`pv.read`/meshio cannot read these meshes**: meshio dies with
  `KeyError: 118` on the cubic pyramid caps. Use `read_msh` from
  `scripts/ho_mesh_render.py` (plain ASCII parse), or the gmsh Python API
  (`gmsh.open` reads its own type 118; its `getElementProperties` throws
  "FaceClosureFull not implemented for prisms of order 3" - get
  nodes-per-element from `nodes.size // tags.size` instead).
- **Filter to the display region BEFORE tessellating.**
  `extract_surface(nonlinear_subdivision=3)` turns 56k wall tri10 into
  8.2M faces (144x); clipping/rendering 11M+ tris hung ~36 min. Keep only
  elements whose corners reach the view box / clip side, remap node ids
  compactly, THEN tessellate with `subdivision=2` (plenty for section
  figures) - ~1.7M faces, renders in ~2 min.
- **Cache aggressively**: pickle the filtered (sub_pts, sub_elems) and
  save the clipped/tessellated surfaces as .vtu (clip outputs are
  UnstructuredGrid - .vtp will raise). Camera/color iterations then take
  seconds instead of re-parsing 211 MB.

## Clean cutaway composition (the "gmsh clip but smooth" figure)

Validated recipe for wall + BL + volume section cuts that read cleanly:

- **Never draw the 3D BL prism shell over the wall surface** - two
  coincident curved skins z-fight into a mottled "crocodile" pattern,
  and translucency makes it worse (VTK does not depth-sort). Show the BL
  in the CUT PLANE only.
- Composition: (1) curved Lagrange wall, opaque, smooth_shading, NO
  edges; (2) `build_wall_wireframe` curved edges via `add_wire` at
  line_width ~1.1 - element boundaries read on the smooth skin; (3) BL
  cross-section from `build_prism_cut` (below); (4) tet section from the
  linear grid slice with `show_edges=True`.
- **`build_prism_cut(pts, elems, origin, normal)`** (in
  ho_mesh_render.py) renders the BL cut as ONE smooth curved face per
  prism: it evaluates each cut prism's exact 40-node cubic volume
  interpolant (complete-cubic (u,v) x cubic w) on a sub-wedge grid,
  slices that, and returns the true curved element-boundary lines
  separately (from slicing the curved prism-face tessellation). Draw the
  band WITHOUT show_edges + the boundary lines via `add_wire` - no
  linear-slice triangle diagonals.
- A pure section-normal camera (e.g. view_vector (0,-1,0)) on an opaque
  clipped half shows a side ELEVATION (the BL shell occludes the wall
  from outside). For "look at the cut" either fill the slice plane (the
  composition above) or make the shell translucent.

## Locked framing for a MULTI-MESH movie (no border jitter)

Rendering one frame per DOE run into an MP4: `camera.tight` fits each
mesh individually, so the ragged clip-box perimeter lands in a different
place every frame and the border visibly jitters. Fix, both parts:

- LOCK the camera: identical focal point + `parallel_scale` for every
  run (fixed world window). Do NOT per-frame auto-fit.
- OVERSCAN the clip: clip the section to a box ~1.5x the visible
  half-window so its ragged edge is always OFF-screen; the frame border
  is then a clean straight image edge cutting through full mesh.
- Orientation gotcha: an explicit `+y` camera with `up=+z` renders the
  body NOSE-RIGHT (wrong x-handedness). `camera.tight(view="xz")` has
  the correct nose-left handedness. So to lock framing while keeping the
  right orientation: call `camera.tight(view="xz")` first, then override
  ONLY focal_point + parallel_scale, repositioning the camera ALONG the
  tight-chosen direction (`pos = focal - direction*dist`) so the roll is
  preserved. Constants (CX, CZ, PZ) must be hardcoded/env, not per-mesh,
  since fleet workers render independently. Validated on agardb_v4
  (500-run curved-section movie, 2026-07-05).

## Rendering gotchas (each cost a probe-fix cycle)

- **`pv.PolyData(points)` auto-creates VERTEX cells** that render as
  square dots over any lines you add afterward - the classic
  "dashed/beaded wireframe". Setting `.lines` later does NOT remove them.
  Construct with `pv.PolyData(points, lines=lines)`. Tubes only mask this.
- **Surface-coincident wireframes**: set the wire actor's
  `mapper.SetRelativeCoincidentTopologyLineOffsetParameters(-4, -4)` (the
  depth-offset mechanism show_edges uses internally). Do NOT displace the
  wire geometrically toward the camera - it produces a halo at the
  silhouette. Polygon offset on the surface does not fix curved-wire vs
  chordal-face coincidence either (patchy blending).
- **Hairline wireframes on dense meshes** (user preference: thin AND
  opaque, no opacity tricks): render 2x oversampled with line_width ~1.3;
  the GL 1px line minimum then reads as a hairline. At 1x, opaque lines on
  a ~24k-face body silhouette-fill the surface.
- **Coincident-face z-fighting between two meshes sharing nodes but not
  geometry** (curved wall vs chordal prism inner faces): delete the
  coincident faces from one mesh. After `extract_surface()`, filter cells
  whose points (via `vtkOriginalPointIds`) all lie in the other mesh's
  corner-node set.
- **Slab extraction must bound ALL axes** to a near-body box; a thin
  one-axis band drags in any huge farfield tet that touches it with a
  single vertex.
- **Camera handedness for sections**: looking down -y puts +x screen-left
  (nose reads backwards); look down +y (camera at -y, up=+z) for the
  conventional nose-left section view.
- **uv on Windows/OneDrive trees**: `UV_LINK_MODE=copy` or
  `--with pyvista` installs fail with hardlink os error 396.
- Off-screen: `pv.Plotter(off_screen=True, window_size=...)` +
  `enable_anti_aliasing("msaa")` works on a desktop Windows box, no xvfb.

## When to prefer this over gmsh batch screenshots

- You want smooth-shaded, anti-aliased, publication-look surfaces and
  precise camera control from Python (no .geo-per-image dance, no GUI
  flash, no silent Print failures).
- You need composition (multiple meshes, per-actor colors, selective face
  removal) - much easier than gmsh visibility tricks.
- Stick with gmsh when you need its clip-plane volume cuts of a WHOLE
  huge mesh interactively, or a quick look with zero scripting.
