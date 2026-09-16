---
name: ntop-sheet-metal
description: Build editable nTop sheet-metal studies from analytic profiles, bends, reliefs, draft, and radial fields; assemble reusable parts and produce clearly scoped forming and release-envelope illustrations. Use for sheet-metal geometry studies, not material-forming predictions.
---

# nTop sheet metal

Use the adjacent [Notebook API skill](../ntop-notebook-api/SKILL.md) for direct process launch, owned-session API transport, SI recipes, and saved notebook presentation. Use [engineering HTML](../engineering-html/SKILL.md) for report structure and the current nTop blue design tokens. Work in the user's requested development folder; keep generated models outside this skill directory.

Before selecting a builder, identify the intended process: press-brake bends, local punch forms, drawing, or a sequence of operations. Read [manufacturing scope and claims](references/manufacturing-scope.md) when choosing blank development, describing tools, or preparing reports and share captions. Embed selected geometric constraints with their assumptions; an implicit field is a geometry representation, not a material-forming solver.

Start with a small circular bend and verify it natively before adding a full enclosure. A native model made from exact line and circular-arc profiles is preferable to a stack of sliced approximations. See [the method and measured lessons](references/method.md) for the dimensional convention, solid joins, flat patterns, and stamping boundary.

The included [basic builder](scripts/build_sheet_metal.py), with its adjacent [miter field helper](scripts/miter_geometry.py), creates five complete Notebook API recipes: an L bracket, U cover, four-wall enclosure, return-flange channel, and idealized cup. It authors native dimension-driven math and analytic curves, not imported meshes. Its bend chain supports signed 90-degree bends. The cup is a revolution of a constant-thickness meridian, not a sheet-forming solver.

The [advanced builder](scripts/build_advanced_sheet_metal.py) adds a slotted hat rail, open-ended louver panel, closed bead panel, pierced dimple plate, and continuous rounded tray. It supports fixed signed bend angles below 180 degrees, including 30- and 45-degree bends. Read [the advanced method](references/advanced.md) before using radial mappings, replacing planar stock beneath formed patches, or creating forming animations. Public sources establish the feature families; all advanced dimensions are authored choices.

```powershell
uv run python .agents/skills/ntop-sheet-metal/scripts/build_sheet_metal.py --case enclosure --out .local/sheet-metal-study
uv run python .agents/skills/ntop-sheet-metal/scripts/build_advanced_sheet_metal.py --case all --out .local/advanced-sheet-metal
```

Read the generated `evidence/enclosure.design.json`, import the complete `models/enclosure.recipe.json` into an identified empty task notebook through the Notebook API, and save a working native file. The `.checks.recipe.json` variant outputs signed field probes for explicit native evaluation. Recipe generation alone does not establish evaluation or geometric correctness.

The [compound builder](scripts/build_complex_sheet_metal.py) adds six study-03 designs: a return-flange ventilation chassis, beaded joggle crossmember, stepped drawn housing, collared annular cover, corrugated mounting shield and bridge-lance cable panel. Read [the compound method](references/complex.md) before combining parent sections with local formed patches. [Public manufacturer sources](references/complex-sources.json) establish feature families; all dimensions and tool shells are authored.

```powershell
uv run python .agents/skills/ntop-sheet-metal/scripts/build_complex_sheet_metal.py --case all --out .local/compound-sheet-metal
uv run --locked --group render python .agents/skills/ntop-sheet-metal/scripts/animate_with_tools.py --study complex --root .local/compound-sheet-metal
```

Defaults write under `.local/sheet-metal-study` in the current working directory, with sibling `advanced`, `complex`, `drafted`, and `assemblies` folders. Use `--out` for builders and `--root` for animations to choose another development folder. Assembly builders require the matching saved native contracts; these are generated locally and are not bundled. Run from the repository root with `uv run --locked --group render python` when using animation helpers.

The animation command requires accepted native meshes and matching evidence in the output directory. Generation alone does not create or verify those exports.

For drafted revisions and release-envelope illustrations, read [draft and release](references/draft-release.md). The [drafted builder](scripts/build_drafted_sheet_metal.py) preserves exact normal thickness while recalculating wall lengths and mounting datums. The [release-envelope helper](scripts/release_tools.py) checks conservative separation from every native triangle; [the revised animator](scripts/animate_drafted.py) labels this limited scope in the GIF. Do not describe these envelopes as contact dies or the prescribed forming stroke as solved contact.

For reusable sheet-metal assemblies, read [assembly methods](references/assemblies.md) and the adjacent [native assembly skill](../ntop-assembly-modeling/SKILL.md). The [family builder](scripts/build_assembly_families.py) and [assembly builder](scripts/build_sheet_assemblies.py) demonstrate separate sheets and hardware, shared evaluations, and mounting datums derived from the drafted parts. They require the saved native family contracts described in that reference.

## Modeling contract

Record each process constraint's value, units, source, applicability, and status as an assumption or calibrated value. Separate constraints enforced by the native graph from offline checks and descriptive notes. Do not claim a rule is embedded because it appears only in the report.

- Identify dimensions as outside, inside, or tangent-to-tangent. Set material thickness and inside radius independently. Use explicit SI literals, including angles; an Extrude block's third scalar is Draft Angle, not an offset distance.
- Keep geometric midsurface radius `Ri + t/2` separate from development radius `Ri + K*t`. K-factor changes the flat pattern, not the formed geometry.
- Derive coordinates and dimensions from named native inputs. Wrap reused expressions in variables before fan-out. Memoize exact subexpressions to keep the graph compact.
- Build each continuous constant section as one closed profile with true arcs, then extrude once. Offset each side of the midsurface analytically. For signed bends, the inner/outer offset radius switches with turn sign.
- Give adjoining sheets positive overlap only inside already retained stock. Avoid an internal zero sheet at a face-only union. Keep corner gaps and bend reliefs explicit; do not silently bridge them with smooth blending.
- Distinguish a floor-to-wall bend radius from the radius at a relief cutout's root. For round-ended reliefs, keep the cap and slot dimensions explicit. The rounded corner option reuses cutters in the shared planar floor. The default miter45 enclosure clips four bent flanges with paired 45-degree planes and circular roots. Its developed solid evaluates the same formed fields under an explicit fold map, retaining the through-thickness bevels. Do not substitute an unrelated 2D outline.
- Distinguish a 45-degree wall seam from a chamfer on a relief slot. The default diagonal seam has a 0.5 mm normal gap and 0.5 mm root radius. It requires bevel cutting or other edge preparation. Document that manufacturing consequence and the valid gap range; do not describe this solid as a conventional perpendicular-cut blank.
- Extend cutters through the full sheet thickness. Preserve fixed thickness, radii, hole diameters, and intended hole datums when resizing the envelope.
- For lanced flaps, keep the opening dimensions independent of K-factor. Use geometric midsurface length plus clearance for the formed opening, and the development radius only for the flat flap length. Check a changed K value natively to catch hidden dependencies.
- For closed beads and dimples, remove the original floor underneath the formed patch. Rejoin only in a retained planar annulus. A raised solid rib above an intact floor is not a sheet emboss.
- For constant-section mapping, use distance to a segment for capsule beads and distance outside a rectangle for continuous rounded trays. Preserve exact meridian offsets and check the hollow underside. Closed feature ends require in-plane deformation in manufacture.
- Reuse a single native coordinate-field set across compound feature systems. Check every top-level variable ID is unique before import. Distinguish the parent radial mapping direction from each local feature direction in animation closures; numeric feature-center arrays must use floating-point coordinates.
- Carry a public-source ledger that separates copied dimensions, derived dimensions, and study assumptions. A familiar product envelope does not establish replica fidelity or load capacity.

## Verification and delivery

Check profile closure and planarity, bend surface locations, thickness, hole centers, open corners, and overlapping joins. Test changed inputs as well as nominal geometry. Treat `e_DIRTY`, `None` readbacks, and transport completion as incomplete evaluation. A native export or explicit native check output is needed to establish evaluated geometry.

Inspect an actual native mesh for bounds, connected components, watertightness, winding, and volume. Use analytic volume as a cross-check, not a substitute for topology and local features. Signed compound fields need not equal physical distance in overlapping regions. Record the mesh settings, source recipe hash, and evidence scope.

For perforated single-body sheets, also compare the mesh Euler characteristic with the intended through-opening count: chi = 2 - 2h. In the advanced examples, native meshes must agree with exact profile-integral volumes within 0.25 percent and expected outside extents within 0.02 mm. These are study acceptance thresholds, not manufacturing tolerances.

Do not force equality between constant-thickness formed volume and a K-factor flat blank when K differs from 0.5. This simple geometric/development pair does not model through-thickness strain. Report the difference and calibrate K with a bend coupon and the intended material/tooling.

Keep editable source recipes, working native saves, collapsed final notebooks, numerical evidence, and an offline HTML report together. Show only the final formed body in the default native view, with the flat blank available separately. Verify the presentation copy preserves the native graph.

The five examples are grounded in [public sources](references/sources.json). They progress from simple bends toward a stamped-part geometry study. Before claiming stamping predictions, add a forming model with material plasticity and anisotropy, contact, friction, blank holder, thinning, wrinkling, springback, and experimentally checked results.

For shareable GIFs, the [animation source](scripts/animate_advanced.py) uses verified native meshes and prescribed analytic unforming. Pass `--root` pointing to the generated advanced study, which must contain `.local/<part>.stl` and matching `evidence/<part>.mesh-validation.json`. The script requires NumPy, SciPy, trimesh, PyVista and Pillow; its Windows text rendering uses installed Segoe UI fonts. The last state uses unmodified native triangles. Label every animation as illustrative geometry motion, including the scope inside the GIF so it survives sharing. Do not call the starting geometric preforms released cutting blanks or the stroke inset production tooling. Keep generated GIFs, meshes and ZIPs in the study output, outside the shared source skill and Git.


For translucent tools, use [the tooling animation helper](scripts/animate_with_tools.py) with `--study advanced` or `--study complex` and `--root` pointing to the accepted study. Keep its adjacent builders and `animate_advanced.py` available. The helper samples native upper/lower vertical surface envelopes at 1 mm spacing and uses 0.6 mm display clearance. Its 7.04-second loops retain an opaque sheet and translucent nTop-blue tools. These shells and their closing motion are concept illustrations; no contact, die release, material flow or piercing process is solved. Record these limits inside the GIF and in the report. Keep final native triangles unchanged and decode the delivered GIFs to verify timing, loop, moving frames and the final hold.
