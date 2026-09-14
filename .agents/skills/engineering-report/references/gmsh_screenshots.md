# Gmsh batch screenshots for mesh reports

These notes retain recorded rendering recipes from the local report skill.
They are not new measurements or verification on the current host.

Battle-tested recipe for rendering mesh figures (linear and high-order,
surface and volume section cuts) with gmsh in batch mode on Windows.
Everything here was learned the hard way; trust the gotchas.

## The basic unit: one .geo per image

```
Merge "mesh.msh";
General.GraphicsWidth = 1600;
General.GraphicsHeight = 1000;
General.SmallAxes = 0;
Mesh.SurfaceFaces = 1;          // filled surface triangles
Mesh.SurfaceEdges = 1;          // wireframe on surfaces
Mesh.VolumeFaces = 0;           // set 1 for volume-element views
Mesh.VolumeEdges = 0;
Mesh.ColorCarousel = 2;         // color by physical group
Mesh.NumSubEdges = 6;           // curved-element rendering smoothness
General.Trackball = 0;          // use explicit Euler-angle camera
General.RotationX = 270; General.RotationY = 0; General.RotationZ = 0;
General.ScaleX = 6; General.ScaleY = 6; General.ScaleZ = 6;
General.TranslationX = 1.35; General.TranslationY = 0;
Draw;
Print "output.png";
Exit;
```

Run: `gmsh script.geo` (a GUI window flashes briefly; batch `-` mode
cannot Print on Windows builds without OSMesa).

**GOTCHA (silent):** a `Print` that follows a `General.RotationY` change
in the same script writes nothing, with no error. One gmsh invocation
per screenshot - drive it from a small Python loop that writes each
.geo from a template and checks the PNG exists afterward.

## Camera math

- The scene is auto-fitted; `Scale = 1` shows the full bounding box of
  the WHOLE mesh (including any farfield!). Visible width is roughly
  `scene_extent / Scale`.
- `TranslationX/Y` are in model units, applied to the model relative to
  the scene center. To center feature at model x = x0 when the scene
  center is xc: TranslationX starts near `xc - x0`; expect one probe
  iteration to land it.
- Useful base orientations: side view `Rotation (270, 0, 0)` (x right,
  z up); axial view down the x-axis `Rotation (0, 90, 0)`; 3/4 view
  `(290, 0, 340)`.
- ALWAYS probe: render at 1400x900, Read the image, adjust, then final.

## Section cuts through volume meshes

Clip planes: `General.Clip0A..D` define plane a*x+b*y+c*z+d, applied to
the mesh with `Mesh.Clip = <bitmask>` (1 = plane0, 3 = planes 0+1).

- **Slab cut** (classic mesh figure): two opposing planes, e.g. keep
  0 <= y <= 0.04: Clip0 = (0,1,0,0), Clip1 = (0,-1,0,0.04), Mesh.Clip=3,
  `General.ClipWholeElements = 1`, VolumeFaces/Edges = 1.
- **Hide the enclosing surface** (farfield spheres etc.): huge boundary
  triangles crossing the slab are kept whole and block everything -
  set `Mesh.SurfaceFaces = 0; Mesh.SurfaceEdges = 0` for volume-cut
  views; the body then reads as a clean white hole.
- The white region boundary = wall faces of the volume elements - ideal
  for showing chordal (linear) vs curved (high-order) wall geometry in
  comparison pairs.

## High-order (curved) meshes

- `Mesh.NumSubEdges = N` renders each curved edge with N subdivisions
  (default 2 looks straight; 6-10 is smooth).
- **Artifact:** clipping curved elements clips their subdivided
  fragments, producing "shattered glass" shards at glancing angles.
  Mitigate with `General.ClipOnlyDrawIntersectingVolume = 1` (draw only
  the single element layer the plane cuts - the big win),
  `General.PolygonOffsetAlwaysOn = 1` (z-fighting), and lower
  NumSubEdges (3-4). If shards remain, keep them and state in the
  caption that it is a visualization artifact, citing the mesh's
  Jacobian check.
- Wireframe-only volume rendering of curved meshes is a hairball - do
  not bother.
- `Mesh.Explode` on curved elements explodes the subdivision fragments,
  not elements - useless.
- **Gmsh cannot read the 29-node cubic pyramid (type 125)** - it
  crashes with std::bad_array_new_length. Exporters must write the
  30-node type 118. If a mixed HO mesh crashes gmsh on load, check the
  element types in the file (`awk` the $Elements section) and downgrade
  or fix the offending type.
- To discover gmsh's node-ordering/position conventions empirically: write a
  single linear element .msh, then a .geo with
  `Merge "one.msh"; SetOrder 3; Mesh.MshFileVersion = 2.2;
  Save "one_o3.msh";` and inspect the coordinates.

## Pair discipline

For every linear-vs-HO (or before/after) pair: identical .geo except the
Merge path, identical camera, then crop BOTH images with the SAME
union-content bounding box (scripts/crop_pairs.py in the skill). Never
autocrop each image independently.

## Interactive handoff

When giving the user a command to explore themselves, pass the options
via `-string`:

```
gmsh mesh.msh -string "Mesh.SurfaceFaces=0; Mesh.VolumeFaces=1; ... Mesh.Clip=1;"
```

and mention Tools > Clipping (drag plane live) and Tools > Visibility >
Physical groups (isolate a group, e.g. just the prism BL).
