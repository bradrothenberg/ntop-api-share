# Findings and learning log

This edited history refers to source-workspace tools. Use [README.md](README.md) for the runnable public commands.
Use [the build 42926 reference](../../docs/API_REFERENCE.md) for new API work. The older skill, display units, and meshing settings below describe recorded cases.

## 2026-09-07: project setup
- The reference directory contains three .ntop notebooks, not analysis or test datasets.
- The user selected an installed flight target. A sea-level static calculation cannot establish that requirement.
- The supplied nTop Notebook API skill documents a prototype API in build 42594. It has unit, fan-out, and bulk-import limitations.
- The HTML report uses the nTop Docs V1 pattern, nTop Design V1 tokens, and nTop writing style.
- A `/spec` skill was not available. Targeted clarification and a persisted SPEC.md provide the project ground truth.

## Notebook API and native authoring

- This project used nTop prototype build 42594. The Python Console owns the `notebook` object. Host Python generates recipes; it does not impersonate that object.
- The user requested Notebook API authoring. `tools/api.ps1` only transports a Python expression to the verified console window. Process and window IDs are session-specific.
- Keep a separate nTop session for this project. Save the complete source notebook before opening export closures in scratch notebooks.
- Recipes encode SI values. A fresh notebook displayed inches and degrees. Length readbacks required multiplication by 25.4 for millimeters. Area readbacks required multiplication by 0.0254 squared for square meters.
- `native_graph.real(v, 'angle')` accepts degrees and stores radians. A dimensionless arc-length/radius calculation already represents radians. Multiply it by an angle literal of ONE RADIAN, not one degree. The first turbine render exposed this error. The corrected recipe uses `real(180/pi, 'angle')`.
- Check the geometry implied by each unit conversion. Graph equality alone cannot detect a consistently encoded but physically wrong formula.
- A reused node must be a named variable with references. Unnamed expression dictionaries require a unique ID for each occurrence. The Jet recipe serializer regenerates those occurrence IDs.
- A separate recipe cannot refer to variables in an earlier recipe. Build each export from the complete dependency closure of its source body.
- Bounding-box properties required aliases in this prototype. The working chain was implicit body, bounding-box variable, point property variable, point alias, scalar multiply by one, then `get_block_input`.
- Compare exported recipes by function, named dependency, and SI literal. nTop can regenerate IDs and refine return types without changing the geometry.
- Sections, colors, visibility, and camera settings were applied to saved notebook metadata. The native model itself was authored through the API. Reopen the presentation file and export its recipe to confirm the graph remains unchanged.
- The P0 source model had 190 named variables, 33 final bodies, eight spline routes, and eight sections. P1 counts appear below. Variable counts include derived fields and checks; they are not counts of independent design inputs.

## Geometry and services

- The engine axis is +Z. The centrifugal compressor precedes an annular combustor and one axial turbine stage.
- Periodic implicit fields create finite-thickness blades. Full and splitter blade families have independent count controls. Keep blade counts integral.
- Turbine camber integrates the meanline inlet and exit tangents along axial chord. Spanwise twist remains a separate native control. These are preliminary cambered solids, not qualified airfoils.
- Cubic spline routes need at least four control points. A three-point route received an interpolated point before construction.
- Offset the spline scalar field for the outer tube. Subtract a smaller offset for the bore. Endpoint spheres from distance fields otherwise close a tube's ends.
- Remove each endpoint cap with a local outward halfspace. Intersect the halfspace with a sphere 1.05 times the outer radius. A global halfspace can remove another bend in the same route.
- The native main fuel pipe has a 3 mm OD and 2 mm ID. These are geometry seeds. Its final refined export has one connected region and open bore centers at both ends.
- Wires are bundle envelopes. The ECU, pump, starter, injectors, igniter, and probe use packaging geometry. Connector ratings, circuit design, metering, and assembly details still require selection.
- Nozzle bore overrun needs a radius correction based on cone slope. Extending a cone with unchanged endpoint radii changes the flow area at the physical exit plane.
- Native nozzle radius feeds the 1D connector. A +5% radius change produced a +10.25% area change and 22.05 lbf in the conditional fixed-area cycle. The baseline was restored to 20.00 lbf.

## Mesh exports: i6-astra workflow and Jet20 findings

- Use `mesh_by_adaptive_tets<implicit,real_field,bool>[5.42.0]` with Remesh false.
- Feed its result to `sharpen_mesh<mesh,implicit,integer,mesh_sharpen_enum>`. Use the identical implicit source, one iteration, and enum 0 for no remeshing.
- Export STL explicitly in millimeters. Measure the original export bounds and topology. Render copies never serve as the measurement source.
- Watertightness is insufficient. The first AT fuel-pipe export at a 0.6 mm mesh scale had 238 closed regions and only 147.25 mm3 total volume. It lost much of the 0.5 mm wall.
- Reducing only the pipe mesh scale to 0.15 mm produced one region and 414.37 mm3. Both bore-center ray tests passed. Keep the rejected topology receipt in `evidence/mesh_verification_coarse_rejected.json`.
- Refining the impeller from 0.4 to 0.2 mm reduced geometric volume error but did not eliminate tiny closed islands. The refined wheel had one 94,679.79 mm3 body and 18 islands. The largest island was below 0.00000418 mm3.
- i6-astra had the same issue on spring seams. Its measured remedy uses native Split Mesh, Filter Mesh List, and Merge after sharpening. Jet20 applies a 0.001 mm3 volume threshold only to the impeller export. This removes numerical islands without deleting a blade. Preserve the pre-cleanup topology receipt.
- The filter threshold is a volume in SI. A threshold of 0.001 mm3 is `1e-12` m3 with units `{'length':3}`. It is not a length tolerance.
- The corrected stator exported at 0.4 mm in about 9.5 seconds. A 0.1 mm run exceeded eight minutes and was stopped in the isolated scratch worker. The saved source model was preserved. A 0.2 mm export was selected for the next measured check. Mesh runtime can grow sharply with refinement; record actual timings instead of extrapolating from another part.
- The 0.2 mm stator export completed in 26.80 seconds. It has one connected region. All ten final rotor/stator camber samples passed; the largest phase error was 0.00105 degrees.
- The nozzle mesh at a 0.6 mm scale had a 0.0284 mm maximum inner-radius error in a section 0.1 mm before the exit. Refining to 0.3 mm reduced that error to 0.00759 mm, below the declared 0.025 mm check tolerance.
- Final export scales are recorded in `build/export_manifest.json`. A curved blade needs a smaller scale than a nearly flat blade with the same circumferential field width. Refining only the scale preserves the geometry while checking this effect.
- Check connected regions, finite coordinates, winding, bounds, and open pipe ends. A closed, consistently oriented surface can still self-intersect. No self-intersection or full assembly clearance claim is made here.
- Measure turbine camber from native STL axial sections at mean radius. Comparing periodic blade intersection angles to the meanline curve catches the radians/degrees failure.
- The camber measurement groups crossings within 0.05 mm on a face before computing the periodic angle. This reduces bias from small mesh wrinkles. It does not prove surface smoothness or absence of self-intersections. The refined rotor's maximum sampled phase error was 0.00105 degrees.

## Cycle interpretation and design basis

- 20 lbf is imposed by sizing airflow at 3048 m and Mach 0.5 with ISA atmosphere. It is not a measured or map-predicted thrust result.
- The baseline derives 0.23644 kg/s air, 0.29496 kg/min fuel, 33.05 kW compressor demand, and a 45.2945 mm equivalent nozzle diameter.
- The nozzle is unchoked at the baseline. The model also handles the choked branch, including pressure thrust. It includes fuel mass and flight ram drag.
- Efficiency, pressure recovery, burner loss, TIT, and kerosene heating value remain declared study inputs. Zero external installation drag is an unresolved lower bound.
- The fixed-nozzle study imposes PR and TIT and closes nozzle continuity. It does not solve an off-design compressor/turbine map match. A different nozzle area does not establish a real-engine thrust gain.
- A 150,000 rpm seed gave a 53.22 mm wheel but a 55.62 mm inlet eye. This geometric failure caused the change to a 100,000 rpm seed and a 79.83 mm wheel. Speed and strength still need validation.
- Compressor slip, transonic eye flow, turbine throat capacity, radial equilibrium, combustion, thermal growth, rotor stress and dynamics, and material life remain open.
- Blade shape cannot improve cycle efficiency while that efficiency is held fixed. Optimization needs calibrated maps or CFD before it can rank aerodynamic blade changes.
- The blade field width is a circumferential seed. It is not a guaranteed constant thickness normal to a curved surface. Follow-on airfoil work must control true normal thickness and leading/trailing edges.

## Reproducibility and provenance

- Reference notebooks contain nested custom graphs. Scan all embedded function graphs; the first JSON graph may be a small custom function rather than the main model.
- SHA-256 hashes and graph counts are in `evidence/reference_inventory.json`. The original reference files remain unchanged. No measured performance map was found.
- `i6-astra/scripts/native_graph.py`, saved-file organization, camera utilities, and console transport informed the local harness. Jet geometry and analysis are authored for this project.
- The HTML report embeds native images and its interactive study data. Its CSS is stored locally in `assets/ntop-docs-v1.css`; rebuilding does not require the original skill path.
- Use `UV_CACHE_DIR` inside this project. Cached dependency runs can use `--offline`. The report and cycle use the standard library. Mesh checks use NumPy, SciPy, and trimesh. Native renders use PyVista.
- A worker restart changes all process and window handles. The current values are recorded in `_agent/session.json`. The console transport now requires explicit handles and verifies their process owner.
- Qt menu handles are recreated each time a menu opens. Rediscover them. UI Automation Invoke did not activate Python Console reliably in this build; targeted menu key events did. The model itself remains authored and read through the Notebook API.
- Use actual native renders to review geometry. The first compressor image showed the backplate. Looking from the inlet side exposed the full and splitter blades.
- Numerical regression checks, API graph equality, mesh topology, native camber samples, and report browser checks establish separate facts. None establishes safe hardware operation.

## Final evidence index

- `results/native_verification.json`: source/readback graph equality and SI/display-unit checks. The inspection presentation graph also matches the source.
- `results/coupling_verification.json`: native nozzle radius perturbation and restoration, with conditional cycle results.
- `results/mesh_verification_sharp.json`: six final exports, each watertight, consistently oriented, finite, and one connected region.
- `results/blade_camber_verification.json`: ten native mesh sections compared with the intended meanline camber.
- `results/nozzle_geometry_verification.json`: measured native nozzle radius near its exit.
- `results/pipe_opening_verification_sharp.json`: both main-fuel-pipe bore centers remain open.
- `results/report_verification.json`: native image loading, interactive controls, theme switching, mobile width, and browser errors.
- `results/package_manifest.json`: final artifact hashes and confirmation that the source references remain unchanged.

## P1 bolted assembly and documentation

- The user selected bolted metal construction with removable end modules and separate liners and rotors. P0 is preserved under `revisions/P0/`.
- The first joint probe completed in 12.95 seconds through the Notebook API. Its M4 head, washer, nut, and screw extents matched the intended stack. It produced twelve full joint regions and 89 small closed numerical regions. The largest small absolute volume was 0.0233069 mm3.
- P1 fastener exports use a measured 0.05 mm3 native volume filter after AT and Sharpen. Do not reuse this threshold for thin routes, blades, or other components. Keep the raw probe receipt.
- A fastener group is an implicit union of nominal hardware envelopes. Coincident contacting faces can merge in the mesh. The BOM still counts screws, nuts, and washers separately. Manufacturing export requires separation into selected hardware parts.
- Use one joint definition to generate both hole locations and hardware placements. Through-joint checks use grip, two washer thicknesses, nut height, and screw length. Tapped joints use a separate receiver bore and nominal engagement.
- A bolt pattern does not connect a floating module by itself. The P1 interface review added local case attachments for the diffuser, front bearing support, liner pack, and guide-vane frame.
- The first model's offset compressor shroud covered the radial exit. P1 trims the axial caps, opens the radial outlet, and connects an inlet sleeve and diffuser roof. Keep this passage visible in the section review.
- P1 extends the liners to the guide-vane frame and makes the tail cone hollow to clear the rear rotor nut. These are geometry changes, not thermal-clearance qualification.
- The shaft stack uses one central land and four spacer sleeves. Retainers locate the stationary bearing outer-race envelopes. Bearing fit, axial preload, locking, thread hand, and rotor torque transfer remain open.
- Catalog screw, nut, and washer dimensions define envelopes only. They do not select material, coating, strength class, torque, or high-temperature suitability.
- All body groups have dedicated source descriptions. The report must expose unresolved service fittings and sensor glands instead of implying that bundle or pipe envelopes complete those interfaces.
- Documentation meshes reuse a P0 export only when recursive hashes match for functions, references, and SI literals. The impeller, turbine rotor, and main fuel line passed this equality screen. Updated bodies receive new exports.
- Render actual native meshes. Preserve originals for measurement. Report figures record their cut planes and mesh sources. Explanatory flow arrows do not represent computed streamlines or mass-flow splits.
- A small section-render test completed in 9.10 seconds. With a camera normal in the radial plane, choose the positive radial direction as camera up to place engine +Z toward the right.
- A native flange section caught an inlet mounting pad that refilled part of a previously drilled M4 hole. Place all pads before final hole checks. The corrected fifteen-hole sample has a maximum radial error of 0.02704 mm against the 2.25 mm nominal radius.
- Adjacent washers need their full outside diameter in a spacing check. The first tray and fuel-clamp layouts had insufficient washer spacing. A separate bounding-cylinder screen also caught a cable-guide bolt near an inlet bolt. Corrected source geometry passes 5,990 parallel-axis comparisons. This screen excludes cross-axis and hardware-to-body contacts.
- The first six-post diffuser pattern cut one of seventeen thin vanes into two parts. Equal six-fold spacing cannot clear a seventeen-vane row at every location. P1 places six posts in selected vane gaps, using the live camber phase at the bolt radius. The attachment pattern follows the vane geometry instead of drilling through it.
- Rotate manifold saddles between the twelve injector positions. The P1 seats are at 45, 165, and 285 degrees. Place pump-foot bolts away from both the outlet union and the motor envelope.
- The revised NGV export had one full body and two numerical surface regions, with maximum absolute small volume 0.00005513 mm3. The nozzle had one full body and eight small regions below 0.00002309 mm3. A measured 0.001 mm3 native volume filter applies only to these two revised exports.
- Detailing creates references from earlier body entries to later controls. Emit recipes in dependency order and reject cycles before API import. Source hashing ignores entry order but preserves functions, named dependencies, and SI values.
- Avoid full-assembly parameter sweeps in the GUI. The P1 coupling check uses the complete dependency closure of nozzle radius, area, PR, and TIT in a scratch notebook. Presentation files are read back separately and are not overwritten by the scratch sweep.
- A 243-variable expanded recipe contained 5,297 function occurrences and 7,034 literal entries. Variable count alone understated the import workload. A dependency-sorted import remained busy for more than nineteen minutes before the obsolete scratch worker was stopped.
- Repeated function subtrees can become shared native variables. The P1 compactor introduces 164 helpers and reduces repeated function occurrences. Expanded-expression hashing proves that all 243 original expressions are unchanged. Keep parameter references distinct even when their current values match.
- Share only exact expression trees, including function identifiers, types, reference identities, literal values, and units. Never merge separate design inputs merely because they currently have the same number.
- Source recipes and export dependency closures can have different amounts of expression sharing while representing the same geometry. Preserve the semantic-equivalence receipt and compare the actual API readback against the exact recipe used for the native file.
- The shared full model completed through `notebook.import_recipe`, save, and API readback in 1,195.96 seconds. It has 407 native variables. All functions, references, and SI literals matched the generated recipe. This is a measured successful runtime, not proof of a speedup over the abandoned imports.
- A separate four-variable native-container codec probe failed and terminated its isolated test process before readback. It was rejected. The delivered model uses the successful Notebook API import and save path. Rejected files are quarantined in `_agent/rejected_experiments/`; do not reuse them.

## P1 final checks, 2026-09-07

- Both presentation notebooks reopened through the Notebook API. Their 407-variable readbacks matched the source graph. The native nozzle perturbation returned 20.00, 22.05, and 20.00 lbf in the conditional cycle, then restored the radius.
- All 71 original component exports have finite coordinates, zero open edges, and zero nonmanifold edges. Multiple connected regions are intentional for vane, injector, sleeve, and hardware groups. Closed topology does not establish surface quality or assembly clearance.
- The revised diffuser has seventeen vane regions. Its six post sections have a minimum measured clearance of 5.43291 mm to the vane mesh. Their maximum radius error is 0.01185 mm. This samples cold geometry at Z = 52 mm.
- Fifteen flange-hole samples passed with a maximum radius error of 0.0270314 mm. The nozzle exit-near section has a maximum inner-radius error of 0.00554815 mm.
- The revised NGV camber sample at 70% chord produced forty raw circle crossings, rather than thirty-eight. Two extra crossings lie inside one blade's outer boundaries, separated by about 0.00268 mm. Do not increase the grouping tolerance to conceal them.
- The camber checker now separates blade sectors by air gaps, measures their outer faces, and retains every internal crossing. Ten rotor/stator sections pass within 0.00276263 degrees. This establishes camber mapping only. The internal contour anomaly remains documented for later surface refinement and intersection checks.
- Ten final figures use actual native meshes without decimation. Their provenance records both recursive source hashes and original STL hashes. `tools/verify_documentation.py` checks those hashes and complete component and joint coverage.
- The final report browser check loaded twelve embedded images, found 71 inventory groups and ten selectable views, and passed search, theme, study controls, and 390-pixel mobile layout checks. No browser script errors were observed.
- Final evidence: `results/native_verification.json`, `results/coupling_verification.json`, `results/documentation_mesh_summary.json`, `results/diffuser_passage_verification.json`, `results/joint_hole_verification.json`, `results/hardware_spacing_verification.json`, `results/blade_camber_verification.json`, `results/documentation_verification.json`, and `results/report_verification.json`. Earlier six-mesh receipts describe P0 and do not replace the current P1 audit.

## Offline actual-model browser viewer, 2026-09-07

- The user wanted to understand the engine in the report without opening nTop. Existing static sections were insufficiently prominent. Section 01 now starts with an interactive actual-model viewer and includes full-resolution normal, exploded, and longitudinal images.
- Use original native STL exports as the source. Preserve the 71 group identities, native source hashes, native dimensions, descriptions, and joint references in the browser metadata.
- A three-part display trial used the impeller, front barrel, and inlet hardware group. Measured simplification times were 26.48, 14.42, and 5.06 seconds. Validate the reduction on representative thin and repeated features before scaling to all groups.
- PyVista `decimate_pro` with topology preservation, splitting disabled, and boundary deletion disabled does not always reach the requested triangle count. The NGV and hardware groups retained more triangles. Record actual output counts rather than claiming the requested limit.
- All display copies contain 1,416,960 triangles, from 28,441,556 source triangles. The encoded geometry is 15,278,684 compressed bytes. Normals use signed eight-bit coordinates; positions use local unsigned sixteen-bit coordinates; indices use sixteen or thirty-two bits as required. Every packed attribute starts at a four-byte boundary.
- The largest measured display-bounds change is 0.246891 mm. Half of the largest position quantization step is 0.00160755 mm. These are not complete surface-distance error bounds. Do not substitute browser geometry for original mesh measurements.
- Native XYZ maps to browser coordinates as (Z - 135, X, Y). Exploded translations map as (dZ, dX, dY). This preserves handedness and places the engine axis horizontally in the default view.
- Local-file module and asset fetches can fail browser origin checks. Bundle Three.js and OrbitControls into an inline script. Embed compressed geometry as base64 and inflate it with DecompressionStream. The final offline test observed no external requests.
- Three.js clipping keeps points with nonnegative signed distance to a material plane. Select the retained half deliberately. For an axial cut viewed from the inlet, keep the downstream half to expose the cut face.
- Live cut lines intersect the displayed triangle geometry. They do not cap the resulting openings or imply a solid-section tessellation. The full-resolution original-mesh sections remain available alongside the viewer.
- Module labels overlap in end-on views because stations project onto the same point. Hide those labels for axial views. Apply screen-space spacing in other views. Use the station caption and selectable parts to identify an end section.
- Show guide-vane and compressor modules from opposite axial sides to expose the blade faces. The module tour still permits free rotation.
- The report links all 71 inventory names back to their corresponding 3D objects. Hardware descriptions include scheduled counts and nominal screw sizes. Part dimensions come from original mesh bounds, not the reduced display meshes.
- Browser tests passed offline loading, mouse orbit, wheel zoom, part ray picking, isolation, exploded transforms, axial/longitudinal cuts, all eight module tours, visibility controls, inventory links, enlarged images, theme, and 390-pixel mobile width. The test receipt records the measured load time for that machine; do not generalize it to other devices.
- Normal and exploded still images use original meshes without decimation. Each exploded image records one rigid display translation per source group. These offsets illustrate relationships, not validated assembly motions.
- `tools/verify_documentation.py` checks display source hashes, original mesh hashes, native notebook hashes, packed data spans, and normal/exploded image provenance. Both native notebooks and all original meshes remained unchanged during this report revision.

## Historical P1 rear-bearing feed routing defect

- The user identified the diagonal orange pipe through the combustor in the longitudinal browser view. It is `F03 Rear bearing feed`, defined in `nTopScripts/build_jet.py`.
- Axial sections of the original F03 and liner meshes at Z = 145, 150, and 160 mm confirm that the pipe occupies the annular combustion space. At Z = 150 mm, its radial extent is 38.0391-40.2915 mm. The combustion-space radial limits there are 26.3477-48.4948 mm. This is not a projection artifact.
- Endpoint routing alone missed the full path through the combustor. The model has no engineered protective passage for that crossing. General notes about unfinished fittings were insufficient; the report now identifies this specific routing defect.
- Watertight pipes, open bores, and valid spline geometry do not establish usable routing. Future checks must classify the complete pipe against combustion spaces, stationary walls, rotating envelopes, and required feed-throughs.
- `tools/inspect_rear_feed_route.py` produced the three native-section measurements now preserved in `revisions/P1/results/rear_feed_route_finding.json`. The P1 route had not changed at the time of this audit. P2 and P3 supersede that geometry. Thermal, support, and interface qualification remain open.
## P2 correction evidence, 2026-09-07

- The full P2 Notebook API import, save, and readback completed in 1,528.93 seconds with 435 native variables. The source has 258 base variables and 177 exact-expression helpers. Do not estimate import completion from variable count alone.
- Both P2 saved notebooks reopened and matched all 435 source variables with no graph differences. A +0.5 mm feed-radius perturbation reduced the native straight-wall clearance by 0.5 mm. A +1 mm case-radius perturbation increased the diffuser outlet gap by 1 mm. Both parameters were restored. The independent nozzle/1D check returned 20.00 and 22.05 lbf under its imposed cycle assumptions, then restored the radius.
- The P2 report checks pass for 71 groups, 23 joints, ten refreshed section views, four new correction close-ups, offline 3D interactions, and 390-pixel mobile layout. No browser script errors or external network requests were observed. The browser geometry contains 1,418,018 display triangles from 29,690,826 native triangles.
- The nominal 9.247099 mm radial feed clearance applies to the straight inner wall. The forward liner lip is closer, with a sampled native clearance of 2.10065 mm. State the measured surface and station scope whenever reporting a clearance.

- The user correctly identified two geometric failures. The P1 rear feed crossed the combustion annulus. The P1 backplate also extended to the case bore and blocked the diffuser outlet. Earlier vane/post clearance checks did not test this flow connection.
- Preserve rejected geometry and measurements before a correction. P1 is archived under `revisions/P1/`. Use explicit before/after evidence rather than deleting the failed checks.
- The corrected backplate ends at radius 56.681832 mm inside the 59.875175 mm case bore. Its nominal radial turn gap is 3.193343 mm. The six axial joints moved to radius 52 mm; the three local mounting lugs remain. Native post-to-vane clearance is at least 5.077388 mm.
- A six-face-connected flood of original native meshes uses 0.5 mm voxels. It excludes the shaft cavity and the impeller running-clearance leak. P1 connects zero of seventeen vane-gap seeds to the liner-port target. P2 connects all seventeen. The sampled axial open area at Z = 56.5 mm is 1,039 mm2. This is geometric evidence, not a diffuser loss or flow-capacity result.
- Trace the air beyond the diffuser. It turns around the backplate, moves inward past the front support ring between its three webs, then moves outward around the dome into the liner air space. Outer-liner holes admit air into the combustion annulus. Do not draw an axial route through the solid dome.
- A long, unconstrained spline can cross the combustor. F03 now uses separate cubic spans for a radial entry, a local bend, and a straight axial run. The case port, front support passage, guide bores, and receiver share the live route coordinates.
- The initial probe completed in 17.87 seconds and produced one closed mesh region. A -30 degree route position approached a front-retainer washer. The final -10 degree azimuth clears that stack and the case fuel clamps. Always include hardware in the route screen.
- The final F03 export has 443,976 vertices and face-center samples in the routing screen. In the combustor length, its radial extent is 14.100137 to 15.900475 mm. The straight inner-liner inner surface is at least 9.247099 mm farther out. All six bore-center rays are open. No sampled penetration exceeds the 0.03 mm numerical contact tolerance.
- Nearest-face pseudonormal signs can give false collisions. One point near a guide end returned a negative signed distance while independent ray containment classified it outside. A retainer query returned a negative sign well beyond its axial bounds. Use independent containment, then unsigned distance for depth. The final screen classifies every pipe vertex and triangle center against each overlapping solid, and samples unsigned clearance separately.
- Integral guide and receiver geometry does not complete a lubricant system. The case sleeve, tube seat, housing cross bore, seals, retention, metering, fabrication access, and thermal growth still need engineering definition and qualification.
- Cache exports by recursive source hash, including parameters and dependencies. Seven P2 component groups changed; 64 retained identical geometry and reused their native exports. Refresh every affected figure and browser mesh. Display simplification is not dimensional evidence.
- Host Python remains `uv run`. The i6-astra virtual environment contains PyVista but not SciPy. `uv run --offline --python <i6-astra interpreter> --with scipy python ...` supplies the cached SciPy dependency without editing that environment.

## P2 case pass-through audit, 2026-09-07

- The complete F03 route screen did not establish that every service has a valid case penetration. A new original-mesh audit confirms casing interference on seven of eight routes: F01, F02, P01, and E01-E04. These defects remain open in P2.
- Independent containment of native mesh vertices finds F01 surface points inside case metal at Z = 94.472641 to 97.570793 mm. Its independently defined hole is centered at Z = 99 mm. P01 interference spans Z = 49.438412 to 51.415985 mm; its hole center is Z = 48.535183 mm.
- Spline control points do not force the curve through an intermediate station. Share interface coordinates between each route, wall hole, and fitting. Use a constrained straight crossing and local bends. Do not drill a hole from a nominal endpoint while allowing a long spline to cross the wall elsewhere.
- F02 and E04 lack matched case holes. E01 crosses both inlet-flange bodies. E02 crosses the front flange and barrel. E03 crosses the front barrel, split flanges, and rear barrel. Check flange envelopes along exterior bundles as well as wall crossings.
- The igniter boss itself clears its case hole, but its E02 lead intersects metal elsewhere. The exhaust probe stops inside the case. A zero collision count for an object that never reaches the wall cannot establish a valid pass-through.
- The screen checks original service vertices against casing bounds and radial envelopes, then uses independent ray containment. Unsigned distance measures penetration depth. The 0.03 mm threshold is a numerical contact threshold, not an export mesh size or manufacturing tolerance.
- The initial P2 audit completed in 34.16 seconds. The final extended P2 receipt is preserved in revisions/P2/results/case_pass_through_audit.json with source and STL hashes. Sampled positive intersections establish defects; vertex sampling does not prove the absence of every possible contact. Sealing, retention, thermal growth, and fitting internals remain separate requirements.
- Extending the screen to the pump outlet union confirms another defect. Its hexagonal body intersects the mating front-barrel flange to a sampled depth of 1.466166 mm. Its stem clears the inlet-piece bore within the 0.03 mm threshold. Drilling one member of a joint does not establish clearance through the whole stack. The final eleven-object audit took 53.36 seconds and supersedes the initial ten-object receipt.

## P3 repair and flow-study evidence, 2026-09-07

- P2 files and evidence are preserved in `revisions/P2/`. P3 trial geometry and failed measurements are preserved in `revisions/P3_probe/`. Trial native exports remain under `exports/P3/`; refinements use `exports/P3b/` and `exports/P3c/`. The current manifest, not a directory name, defines the final meshes.
- Shared route, hole, and fitting coordinates replace independent case-port definitions. F01 is clocked to -15 degrees at Z = 99 mm to clear both injectors and liner fasteners. F02 uses a straight +15 degree entry at Z = 86 mm and an open receiver behind the front bearing. P01 uses the midpoint of the shroud and backplate stations, Z = 51.767591 mm.
- The final cable routing radius is separate from the fuel-service radius: 84 mm versus 69.075175 mm. The 80 mm P3c trial is superseded. Move the tray, ECU, guide bores, connector stubs, and attachment joints together. Connector stubs are at Z = 24 mm; attachment screws are at Z = 35 mm. Check all four leads against guides and fasteners as well as the case.
- E01 terminates ahead of the inlet in a motor pocket. E02 terminates outside the case at the igniter. E03 terminates in a probe head at Z = 211.689949 mm. The probe stem now crosses the pressure wall, and its head clears the exhaust flange. E04 crosses a matched sleeve at Z = 68 mm into the cool front plenum; the pickup itself remains undefined.
- The pump union needs clearance in three bodies: pump foot, inlet piece, and front-barrel flange. The last trial found a 1.001 mm pump-foot overlap after the two flange members were clear. The final counterbore removes that collision.
- The final full screen tests 1,403,643 native vertices and triangle centers across eight routes and three fitting envelopes against all other component and hardware groups. No penetration exceeds the 0.03 mm numerical contact threshold. The screen completed in 259.44 seconds. Thirteen center rays and four hollow cubic centerlines pass separate bore checks. This does not establish full bore area, sealing, retention, temperature rating, or an operating lubricant system.
- Independent ray containment can still give rare false inside classifications. Two F02 candidates lay below every projected casing triangle. Use an exact projected-triangle radial lower bound, including edge interiors, to reject these geometrically impossible case classifications. Preserve the rejected receipt and method change. Do not simply whitelist a collision.
- All 71 native exports have finite coordinates, zero open edges, and zero nonmanifold edges. Use AT meshing, then Sharpen against the same source. A closed surface is not evidence of aerodynamic function or manufacture readiness.
- The final 0.5 mm full-engine six-face flood connects all six stations and all seventeen diffuser passage seeds. The inlet-connected diffuser-turn area is 1037.75 mm2 at Z = 56.5 mm. This is a finite-grid connectivity/area check, not CFD pressure recovery. The shaft cavity, outside-shroud route, and backplate running-clearance bypass before Z = 59 mm are excluded from the principal flow domain.
- Measure the NGV throat on cylindrical cuts of the original vane mesh. Fourteen radial bands with 0.01 mm edge sampling give 1114.085070 mm2; the edge-sampling lower value is 1110.905623 mm2. The seven-to-fourteen-band difference is 0.137959 mm2. The lower value only bounds edge-point spacing, not mesh, radial quadrature, or aerodynamic losses.
- The original nominal liner-hole area was 793.0 mm2. At the five-percent burner-loss budget, even unity Cd admits only 0.174647 kg/s in the lumped model, below the required 0.236436 kg/s. Use a common radius scale of 1.4799762962, giving 1736.933352 mm2. All 42 centers are open; the maximum measured axial-radius error is 0.007584 mm.
- Cd = 0.75 for primary holes and 0.60 for the other rows are uncalibrated assumptions transferred from NASA TN D-5570, Appendix A. They are not Jet20 measurements. Solve hole admission against combustion-zone static pressure with compressible mass flow. Do not use total-to-total pressure loss directly in an incompressible orifice formula.
- An 81-case pilot precedes the 10,201-case bounded search and constrained local refinement. The stated objective minimizes conditional fuel flow for 20 lbf within the retained case, impeller, 100,000 rpm, 2.9 PR, and 1100 K study limits. Only one grid point meets all stated constraints. No lower-fuel solution was found.
- The pressure-loss-aware fixed-nozzle prediction changes from 11.997557 to 20.000000 lbf after the hole change. Conditional fuel flow is 0.294964 kg/min. The reference compressor-delivery bound is active with zero modeled margin and uses unmeasured flow-coefficient/blockage seeds. These numbers do not prove physical performance.
- A 0.8 multiplier on the assumed hole coefficients reduces predicted thrust to 18.540179 lbf. The 1.2 multiplier retains 20 lbf because the five-percent loss budget remains. This is sensitivity, not a confidence interval. Off-design points impose PR and TIT and need component maps before operating-line claims.
- Read native nozzle radius, PR, TIT, and liner-hole scale into the external flow model. Verify that a native scale perturbation changes computed hole area and conditional thrust, then restore it. Do not optimize blade shape against imposed efficiencies.

## Final P3 geometry refinements

- The 80 mm cable-radius trial caused actual J14/J20 hardware overlap. The two-direction native mesh screen measured up to 0.87758 mm penetration. Preserve that rejected result in `revisions/P3c/`.
- A separate native cable-radius control now sets 84 mm. The ECU, tray, guides, routes, and related joints follow it. Final original meshes have no sampled J14/J20 intersection. The conservative parallel hardware screen checks 5,987 profile pairs with no overlap candidates. These checks do not establish full assembly motion, tool access, preload, or hot clearance.
- Thirteen cable-dependent groups were exported through the Notebook API into `exports/P3d/`. The other 58 groups retain identical recursive source hashes. The manifest identifies all final meshes. The final full service screen has 1,403,643 route and fitting samples and took 259.44 seconds.
- Removing the backplate running-clearance bypass from the gas domain still leaves all seventeen diffuser seeds connected to the inlet and liner passage. Reuse the voxel cache only after every source and mesh hash matches. Reclassification only removes cells; it must repeat the six-face flood and retain the original voxelization time.
- The final browser geometry contains 1,433,194 display triangles from 29,820,088 original triangles. The compressed geometry is 15,464,264 bytes. The maximum display-bounds change is 0.250637 mm. This is not a complete surface-error bound.
- Nine P3 close-ups document case interfaces, liner openings, and the corrected guide fasteners. Ten principal views, two normal/exploded stills, and four retained correction close-ups use original native meshes. Source hashes control reuse of every figure.
- A small live API probe verified that setting a calculated variable's Input replaces its expression with a literal. Use this only when the intended source control is an independent scalar. Match the complete exported graph to the source after the edit.

## P3 saved-file and report delivery verification

- The full Notebook API import, save, and initial readback took 3186.66 seconds. The source has 314 base variables and 218 shared-expression helpers, for 532 variables. Exact expression sharing preserves the expanded graph.
- The earlier import used the 80 mm cable-radius trial. A small API setter probe, including two dependent scalar consumers, accepted replacing its calculated Input. The same replacement failed in the full notebook after long evaluation. Small scalar success does not prove that a large-model transaction will complete.
- Complete route, fitting, and hardware interference checks before freezing the recipe for a full import. A later cable-guide correction changed the first import's source. The source-hash guard correctly prevented delivery of that stale graph. Compare the completed import hash with the current source before applying presentation or generating the final report.
- The user restarted the computer during the first patch attempt. The completed raw notebook and all export/analysis receipts survived. A fresh session reopened and exported the raw notebook in 47.66 seconds, but a second full-model replacement also failed. The final delivery therefore uses a complete Notebook API import of the final source, with the independent 84 mm scalar present from the start. Preserve the failed attempts in `revisions/P3c/`.
- Both `Jet20.ntop` and `Jet20_Inspection.ntop` reopened through the Notebook API and matched all 532 source variables. Display metadata and camera bounds do not alter the source graph. The original P2 delivery and P3c trial remain preserved.
- A native 10 percent reduction in liner-hole radius scale produces 19 percent less nominal opening area. The connected loss-aware flow model returned 20.000000, 18.636694, and 20.000000 lbf before, during, and after that perturbation. All test values were restored. This validates the software connection, not physical thrust.
- Final browser checks pass against the delivered HTML hash: all images load, 71 groups remain selectable, assembled/exploded and movable section views work, all eight tours work, and the page fits a 390-pixel width. Offline checks observe no external requests or script errors.
- Do not infer absence of a bypass from inlet-to-nozzle connectivity alone. Separate virtual caps at Z = 182 and 206 mm, radius 39.974373 mm, disconnect inlet and nozzle in the restricted 0.5 mm gas domain. No connected turbine bypass is resolved there. The check uses copies of the voxel array and preserves hashes of the original geometry receipt and volume. It does not predict leakage below the grid scale.
- The optimization plot reads the recorded CSV: 2,905 cases have no valid cycle result, 7,295 violate constraints, and one passes. Fuel contours include infeasible geometry candidates. The guide-vane throat requires at least 81.3 percent of ideal sonic capacity under the imposed inlet state. This is a necessary capacity bound, not a measured discharge coefficient or operating map.
- `tools/verify_documentation.py` requires current source hashes, native file hashes, original mesh hashes, native flow inputs, and browser report hashes. The final report generator rejects stale saved-file verification. Regenerate all dependent evidence when geometry changes.
- Geometry repairs and the bounded conditional optimization are complete for this preliminary scope. Component maps, surge margin, combustion behavior, rotor mechanics, hot clearances, sealing, and hardware tests remain unresolved. Do not describe these receipts as qualification of a working engine.

## A1 component matching and manufacturing handoff

- One temperature, speed, fuel flow or thrust command closes the steady control degree of freedom. Five residuals solve the remaining operating quantities together. P3 normalization reproduces its duty by construction and is not physical validation.
- A burner-loss root on a least-squares bound stopped near a scaled residual of 2e-6. Place the root inside numerical bounds and enforce the loss floor through the admission complementarity residual. Accepted residuals are below 1e-7.
- Corrected quantities use each component's inlet total state. Reference compressor duty is 0.292450 kg/s at 101,129 corrected rpm. Turbine duty is 0.214105 kg/s at 51,181 corrected rpm. Correction references are 288.15 K and 101325 Pa.
- A 5 percent relative compressor-efficiency reduction gives 17.673 lbf. A 20 percent hole-Cd reduction gives 18.416 lbf after rematching. The old imposed-cycle result differs because it did not solve speed and turbine capacity.
- A 5 percent larger nozzle gives 21.886 lbf and 104,393 rpm at 1100 K. Speed and PR exceed retained limits. The 41-area trade finds one passing target case at the native area. This is a sampled, bounded result.
- Of 54 flight cases, 43 match and 11 fail numerically. Some low-temperature failures approach numerical flow bounds. Do not infer a physical idle or stability boundary from these failures.
- Reference shaft torque is 3.156 N m. Nominal solid-shaft torsion is 31.394 MPa. The case membrane screen gives 8.244 MPa from 165.230 kPa pressure difference. These calculations exclude detailed features, thermal gradients, fatigue and material allowables.
- The 0.300 mm cold tip gap is the closing-growth budget before tolerances, runout, distortion and required running clearance. The thermal helper requires metal temperatures and explicit expansion coefficients and displacements.
- Ten numerical tests cover balances, command equivalence, losses, accessory load, drag, choking, map interpolation, data reduction, stale geometry and thermal-clearance arithmetic. Temporary synthetic maps never represent measured Jet20 data.
- An authorized PyPI sync supplied missing registry metadata and created the local dependency lock. Subsequent locked analysis runs work offline without the i6-astra environment.
- Current Browser controls cannot reload file URLs. A temporary loopback server supports A1 UI testing. Exact comparison confirms all 31 original image payloads and five original inline scripts are unchanged. P3 offline receipts stay associated with their preserved HTML; A1 has separate current receipts.

## R1 requirements, executable acceptance, and SysML v2

- Keep requirement authority and verification status independent. User intent can be confirmed while its acceptance details and physical evidence remain open. Retained analysis seeds do not become hardware allowables.
- One canonical register generates the readable specification, SysML definitions, and trace table. The acceptance runner emits JSON, CSV, and JUnit results. Missing values and evidence stay blocked/skipped and prevent release.
- Twenty-one new guard tests exercise corrupted evidence, blocked passages, missing fittings/joints, mesh defects, fabricated validation labels, and empty or unrun checks. They complement the ten existing performance tests.
- The R1 evidence lock pins 100 original P3/A1 artifacts. Check those hashes and each receipt's source/mesh hashes before reading its numerical result. This verifies evidence currency; it does not repeat the underlying geometric measurement.
- The retained NGV receipt actually contains four sampled blade-sector entries with internal crossings: one at axial fraction 0.7 and three at 0.9. They may sample related geometry. The previous single-sector summary was incomplete; retain the exact finding until inspected and resolved.
- An official reference parser is available in conda-forge's `jupyter-sysml-kernel` distribution. Version 0.61.0 is named by the official 2026-07 release. Extract its JAR and standard library locally; Java 21 runs the parser without installing Jupyter or altering system configuration. Keep metadata, checksums, and upstream licenses.
- `SysMLInteractive.process()` reports syntax and semantic issues. Validate a correct fixture, an invalid syntax fixture, and an undefined-type fixture before accepting a generated engine model. The final model has zero errors and warnings under that implementation.
- On Windows, use an absolute standard-library path. A relative path caused EMF to seek literal percent-encoded directory names. `analysis` is reserved; dependency paths use `::`; a requirement usage with an added input needs an explicit inherited-subject redefinition before the input.
- The SysML model represents logical architecture and external evidence predicates. Unbound Boolean evidence inputs and verification verdicts prevent a generated exchange model from asserting hardware satisfaction. Python remains the executable analysis and verification implementation.
- Long SHA256 strings overflowed the first 390-pixel report layout. `overflow-wrap:anywhere` on source notes fixed the page overflow. Scrollable tables and code blocks retain their own horizontal scrolling.

## R2 NGV mesh diagnosis

- The rejected NGV was watertight and winding-consistent, yet its Euler number was -5470. Closure alone missed its excess surface handles. The original four failed blade-sector samples became 73 failed circles in a broader 440-circle diagnostic.
- AT refinement from 0.2 to 0.1 mm cleared those sampled vane crossings but left Euler number -1778. Enabling the native AT Remesh control gave -1650. A coincident-interface overlap trial gave -1780 and was rejected.
- Standard Mesh from Implicit at 0.2 mm followed by Sharpen gave the expected Euler number -64 and one connected surface. Its topology accounts for 19 gas passages, one center bore, six shroud-carrier holes, three web vents, and four bearing-support holes. The source readback is unchanged.
- The accepted mesh passes 1,485 section circles: 99 axial fractions and 15 radii. Each has two crossings per vane. Preserve this broader screen and the bad R1 mesh as negative evidence.
- A slice exactly at the flat frame end can create many small loops. Their radial locations matter. All extra loops in the cap sweep lie outside the gas annulus; +/-0.01 mm cuts give the expected upstream/downstream contours. Do not call this only float32 error: measure cap deviations and edge effects. Manufacturing surface tolerances remain open.
- Use the standard-mesher exception only for this measured NGV case. Other parts retain AT then Sharpen. Mesh settings belong in cache eligibility, so a changed mesher cannot reuse an old mesh merely because its implicit source hash matches.
- Notebook API export is `export_as_recipe`. `add_block` returns a dictionary, while `list_block_inputs` takes its `id`. The measured AT Boolean input is named Remesh.
- The graph builder writes the main recipe, layout, parts, routes, and joints as side effects. A probe builder briefly wrote trial build outputs. Regenerating the default source restored all 100 R1 lock hashes before adoption. Preserve/restore generated files around future experiments.


## R2 delivery results, 2026-09-08

- J20-GEO-012 passes with the original R1 acceptance criterion. All 36 software tests pass. The matrix has 28 passes, no failures, and 26 blocked hardware requirements. Normal acceptance exits 0; manufacturing release exits 2.
- The native recipe and both saved notebooks keep their original hashes. Only the NGV original mesh changed. All 71 meshes pass the repeated edge audit. Ten camber cuts, 1,485 broad vane circles, all 11 route/fitting screens, 13 interface rays, and four hollow centerlines pass.
- Fresh 0.5 mm voxelization took 624.735 seconds. All six station seeds and seventeen diffuser passages connect. Both independent virtual turbine caps disconnect inlet and nozzle.
- Corrected 14-band throat: 1107.169728 mm2; edge-sampling lower value: 1103.990281 mm2. Seven-to-fourteen difference: 0.024317 mm2. This replaces the earlier 1114.085070 mm2 estimate. Mesh accuracy, radial quadrature, and aerodynamic losses are not bounded by the edge-sampling value.
- The 81-case pilot and 10,201-case conditional search retain 20 lbf and 0.294964 kg/min at the reference condition. Only one sampled grid point passes retained limits. The normalized matched model again closes 43 of 54 flight cases; eleven numerical failures remain recorded. Only one of 41 sampled nozzle areas meets the retained target/limit combination.
- Current browser payload: 1,399,626 display triangles from 36,152,420 original triangles. All 71 groups, eight tours, normal/exploded views and section controls pass current browser checks. All 32 embedded figures load and enlarge.
- R2 renews 97 performance-lock artifacts and 131 requirement-lock artifacts after actual measurement refresh. Historical P3/A1/R1 receipts stay associated with their original report hashes. Never relabel historical image receipts after a mesh changes. Include the early blade-detail figure in the dependency review.
- SysML reference implementation 0.61.0 accepts the unchanged model with zero syntax or semantic errors. Invalid syntax and undefined-type controls fail as expected. Hardware evidence inputs remain unbound.
- Windows Python defaults can decode UTF-8 source as cp1252. Always specify encoding='utf8' for report and harness text reads and writes. Inspect punctuation in the actual browser.
- PowerShell can report a failing native command as shell exit 1. Check the child process return code to distinguish acceptance failure from the intentional release exit 2.

- Browser review measured that fill('') retained the previous search query. Keyboard selection and Backspace cleared it. A capture immediately after viewport reset could use a stale bitmap size; a fresh observation gave the correct desktop frame.

## C1 blocked-requirement audit and preparation

- All 26 current blocks concern hardware acceptance. Several require manufacturing documents or demonstrations, so do not describe every block as an engine-test requirement.
- Decision dependency counts are derived from the canonical register: qualified operating limits affect nine blocked requirements; duty/life affects eight; materials affect six. These counts describe dependencies, not a schedule or a risk ranking.
- The component and engine measurement templates contain no measured data. Reference-normalized performance cannot close independent correlation, thrust, or stability requirements. Empty decision values remain null.
- Generated production worksheets cover 71 native groups and 23 joints. Groups include combined hardware and multi-piece geometry. Split them into real made and purchased part numbers before claiming a complete production BOM.
- The bearing prefix selects four groups: two cartridges and two retainers. Select the cartridge names explicitly for the bearing packaging handoff. Bounds do not establish rolling-element geometry, fit, or supplier compatibility.
- Joint records use different geometric fields for different patterns. CSV fieldnames must include the union of those fields. Keep the nominal model separate from undefined production thread, preload, seal, locking, and inspection definitions.
- Forty-three current steady cases provide conditional load ranges with exact source indices. Eleven failed solves provide no accepted loads. Neither the maximum steady torque nor the reference shaft stress is a complete qualification load case.
- Source-linked preparation can advance without changing locked acceptance evidence. Do not add a Boolean approval shortcut or relabel missing hardware evidence as a pass.

## C2 user basis capture

- The user confirmed three hours of continuous operation and three hours of total service life. Store both separately, even when they have the same value. Neither statement demonstrates endurance.
- One-time use does not define a factory acceptance run allowance, a relight requirement, a count of starts, or whether the vehicle is recovered. Ask about the application before applying a vehicle-specific design basis.
- Normal jet fuel does not identify an exact grade or lubricant. Preserve the user's words and the existing kerosene-class intent without inventing a qualified fluid specification.
- Casting and sheet metal are user preferences. Printing of the compressor and turbine is a permitted substitution, not a material or process qualification.
- The C2 input addendum supersedes corresponding unanswered questions in the C1 planning snapshot. Historical acceptance results retain their original configuration and evidence identity.

## C3 SAR mission and production proposals

- The user confirms the expendable vehicle is a search-and-rescue drone. Its intended application is defined; do not repeat that question. Aircraft mass, fuel capacity and detailed schedule remain unknown.
- Three hours of reference fuel flow gives 53.093568 kg. Producer density bounds at 15 C give 63.206628-68.507829 L of liquid. Neither value is an actual mission prediction or total tank requirement. Keep reserves, start/shutdown, unusable fuel and ullage separate.
- Equal three-hour mission and total service-life values leave zero extra mission-only life. Any additional ground-running time consumes life. Keep the inclusive margin unresolved until that allowance is defined.
- `analysis/mission.py` integrates explicitly supplied steady segments and rejects invalid/unconverged states or missing duration. Eight tests cover unit conversion, segment invariance, density inversion, absent allocations, extra fuel and ground-running life consumption. Tests do not demonstrate endurance.
- C3 adds J20-ANA-012 and updates confirmed SAR duration and production preferences in the canonical register. Four decisions are partly defined. Status is 29 pass and 26 blocked; the new pass is software accounting. No physical requirement was closed.
- Producer references support candidate routes, not engine qualification. Wrought Haynes 282 creep data are not AM rotor allowables. Printed patterns for investment casting are distinct from printed metal rotors. IN718 coupon tensile properties cannot establish turbine metal-temperature capability.
- The proposed production register explicitly maps 48 nonhardware groups and 23 hardware groups. Casting, sheet forming, machining, welding, tubing, bought components and additive substitutes require different evidence. Native integral lips, lugs, flanges and bosses are not already defined as fabrication pieces or weld seams.
- Nominal M3/M4/M8 geometry cannot set torque without load, friction, grade, temperature and preload requirements. C3 leaves joint preload and torque null.
- The updated SysML model uses ISQ::DurationValue with SI::s. The official 0.61.0 implementation accepts the mission targets and the duration verification constraint. Hardware evidence and verdicts remain unbound.
- Long unit-test identifiers overflowed the requirements report at 390 pixels. Applying overflow-wrap:anywhere to each requirement card corrected the measured page overflow. Recheck current HTML hashes after any renderer change.

## C4 finalization with authorized assumptions

- The user confirms approximately 200 kg total takeoff mass including fuel and payload. The user explicitly authorizes documented assumptions for unanswered inputs. Do not repeat optional questions after a documented basis exists.
- Separate confirmed intent, engineering assumptions, derived budgets, sourced properties and physical evidence. All 18 decisions now have planning bases. This removes missing user preferences as a planning dependency, but does not qualify materials, bearings, limits, controls or endurance.
- Preserve the original service-life requirement when adding contingency and ground duty. C4 assumes 15 minutes powered contingency, five minutes factory running and five minutes preflight running. Its 12300-second design provision exceeds the original 10800-second life by 1500 seconds. Both physical-life verdicts remain false.
- When unusable fuel is a fraction of total start load, divide burnable demand by one minus that fraction. Do not simply add the fraction to burnable demand. For ullage defined as a fraction of gross tank volume, divide liquid volume by one minus ullage.
- Track factory fuel, aircraft start load and takeoff fuel separately. C4 uses a separate factory supply. Its aircraft start load includes preflight fuel; takeoff mass follows that consumption. No engine-running refuel is assumed or instructed.
- C4 reference-flow accounting gives 60.196789 kg start fuel, 58.721967 kg takeoff fuel and 141.278033 kg residual nonfuel mass budget. Using the sourced 775 kg/m3 density at 15 C and assumed 3% ullage gives 80.075542 L gross tank provision. Actual thermal expansion, slosh, pickup, tank fit, CG and model uncertainty remain unverified.
- Weight/thrust is the required lift-to-drag ratio for steady level balance when lift equals weight and thrust equals drag. At 200 kg and 20 lbf this is 22.046226. It leaves no excess thrust at equality. Hypothetical L/D values must remain sensitivity inputs, not measured aircraft performance.
- Seven additional tests cover aircraft mass/fuel conservation, tank denominators, life-deviation preservation, force balance, invalid inputs, impossible fuel allocation and false hardware acceptance. The complete 51-test suite passes. SysML reference 0.61.0 accepts the SI mass and separate assumed time targets with no warnings or errors.
- Retain prior baselines before requirement revisions. C4 lives under `results/sar_C4/`; `revisions/C3_before_finalization/` preserves prior source and results. Do not regenerate an old receipt under a new revision label.

## C5 aircraft mass and approximate L/D target

- The user revises aircraft mass toward 110 kg and targets L/D approximately 12. Preserve the established total takeoff mass scope, including fuel and payload. The new input supersedes 200 kg; it does not change the engine geometry or thrust target.
- At 110 kg and 20 lbf, steady-level force balance requires L/D 12.125424. At exactly L/D 12, required thrust is 20.209041 lbf and the 20 lbf target has a 0.929859 N deficit. The mass at force equality is 108.862169 kg. Never turn that deficit into a pass by rounding the approximate target.
- Keep the requested aircraft L/D target separate from actual aerodynamic performance. `confirmed.aircraft_lift_to_drag_target` stores 12; `planning.adopted_aircraft_lift_to_drag` stays null. The SysML model records a target, while physical thrust/drag acceptance remains unverified.
- Mass reduction alone does not reduce fuel flow in the retained reference-hold study. Takeoff fuel remains 58.721967 kg, now 53.383607% of 110 kg. The remaining nonfuel mass budget is 51.278033 kg. Recompute a real duty only after the aircraft and engine evidence supports it.
- C5 reuses the tested force-balance functions. Document guards independently check the target drag, required thrust conversion, maximum mass, negative margin and remaining mass. Browser checks verify the L/D-12 default, displayed exact conditions, controls and mobile layout. All 51 software tests and official SysML validation pass.
- `revisions/C4_before_mass_update/` preserves the old source and reports. Use `results/sar_C5/` for current budgets and the C5 assumption register for current planning. Actual native geometry evidence and the 26 hardware acceptance blocks are unchanged.

## Assumptions table formatting

- Combining automatic column sizing with `overflow-wrap:anywhere` compressed the Topic column and split normal words into fragments. Scope normal wrapping to the assumptions table and assign explicit column proportions.
- The five-column table uses fixed layout, an 840 px minimum width and a focusable horizontal-scroll wrapper. Headers can wrap. The Topic column receives 18% of the width; IDs remain on one line.
- At a 940 px viewport, the complete table fits its 871 px container and the Topic column measures about 157 px. At 390 px, scrolling stays inside the table and the page does not overflow. The formatting change does not require repeating engine analysis tests.


## nTop UI screenshot preparation, 2026-09-09

- The user requests authentic nTop UI captures of the whole assembled and exploded engine. Keep the application interface visible. Match the report's exploded spacing. Screenshots must be actual captures, not rendered engine images composited into a fabricated interface.
- An assembled capture is saved under screenshots/. Its presentation copy enables all 71 component groups. A saved notebook can retain an active section tool independently of visibility; close that tool before an assembled capture.
- The raw API translation pilot read back the correct -85 mm impeller offset after conversion to native inch display units. Full per-call translation authoring became slow and stopped after 22 of 71 groups. A partial status is not completion.
- The report's existing quantized display payload can be decoded into 71 STL display copies without repeating simplification. It contains 1,399,626 triangles. A native import of these 71 display groups completed in 5.92 seconds, and recipe readback matched. The user subsequently requested actual implicit bodies, so this display-mesh fallback is not the requested deliverable.
- Save the original screenshot bytes with their actual file format. The computer-use tool returned JPEG. Do not label it PNG or alter the screenshot to fabricate missing geometry or UI.
- Desktop capture can return a black screen when the Windows session is unavailable. Activation then failed with "failed to activate captured window". Stop app input and restore the desktop session before another capture.
- For native implicit presentation authoring, first hide all source bodies in a separate saved copy. Keep every non-view chunk byte-identical. In the measured retry, adding the first ten Translate variables took approximately 3.02 to 3.35 seconds per group, substantially faster than the visible-source attempt. Retain checkpoints and verify the complete source graph after authoring.
- The native implicit retry completed all 71 groups in 533.17 seconds, including opening, four checkpoints, final save and recipe readback. The readback preserves all 532 original variables and expressions. Every added body has type `implicit`, references its original component, and has the specified SI translation. Both original engine notebook hashes match their existing verification receipt.
- `Jet20_Implicit_Exploded.ntop` is the requested native presentation. Camera, visibility, colors and collapse state are separate saved UI metadata. The preparation helper verifies that all other serialized chunks remain byte-identical to the API working notebook. All 71 translated groups are visible.
- The final delivery copy is `screenshots/Jet20_Exploded_Implicits.ntop`. Its screenshot uses actual implicit geometry in nTop 6.0.3, with all 71 groups enabled and the log panel collapsed. `screenshots/capture_manifest.json` records both assembled and exploded captures and native file hashes.
- With several nTop instances open, activation can time out while a different nTop window or Python Console remains in front. A capture can then show the occluding window. In this session, minimizing the observed foreground presentation or completed console exposed the correct target. Verify the title and actual image before saving. Do not treat an activation timeout alone as proof of a locked desktop or unfinished geometry.
- The small chevron at the far right of the nTop 6.0.3 status bar collapses the log panel. This removes file paths from the screenshot without clearing or deleting log data. Wait for the viewport to resize before capture.

## P4 inlet and outer nacelle, 2026-09-09

- The user explicitly included the outer casing profile. The unscaled reference photo supplies styling intent only. P4 adds an external fairing around the retained pressure casing. It does not establish better inlet recovery, lower drag, thermal acceptability, or manufacturing release.
- Keep revision outputs separate. P4 retains all 532 baseline variable expressions and eight locked baseline file hashes. Its final native model has 624 variables and 75 visible groups. Five current native exports cover the serviced inlet, two panels, new hardware, and two grommet envelopes.
- Recipe occurrence IDs require independent object instances. A Python deepcopy preserves shared references within its source graph. Assigning fresh IDs through shared nodes can create duplicate expression IDs. A JSON serialization round trip breaks that shared identity before the ID pass.
- Notebook API import references resolve inside the imported recipe. Import tool variables first, then connect existing and new variables through native API blocks. The Offset Distance input is a real_field. Connecting a native length variable succeeds where direct numeric assignment does not.
- Build hidden native source copies before large implicit operations. Preserve the API readback before organizing UI sections, visibility, colors, and camera. Compare native definitions again after presentation changes.
- Check the new nose as well as the outer panels. The first P4 nose crossed the retained starter lead twice. Preserve that rejected evidence. The correction cuts two passages and adds two flanged grommet envelopes without changing the lead route.
- The corrected nose screen finds zero sampled lead intersections. The grommet export contains two closed connected bodies. Among 1,654 nearby lead samples, none lie inside a grommet; the minimum sampled gap is 0.060859 mm. These results do not qualify bore tolerance, sealing, retention, or insulation.
- Separate pre-existing attachment contacts from new collisions. Compare front-service candidates with the original inlet surface. The 0.05 mm mesh classification threshold identifies retained contact; it is not a manufacturing allowance.
- The panel screen covers 116 comparisons and 589,058 sampled surface points with zero detected intersections. Reuse it only after verifying unchanged panel mesh hashes and confirming that changed parts occupy a separate axial region. Finite samples do not prove a global minimum clearance.
- All five current exports use Adaptive Mesh followed by one Sharpen iteration and have zero open or nonmanifold edges. Keep the separate standard-mesher exception for the unchanged baseline NGV.
- Keep full source meshes for critical sections. Simplifying the new large curved parts to 45,000 triangles produced visible artifacts. The browser now uses approximately 150,000 triangles per large P4 part. New-part still images and all critical sections use original native STL exports.
- A section exactly on a tessellation plane can show coplanar edge artifacts. Use a documented 10-degree meridional plane for full-engine sections and X = 0.2 mm for the starter detail. Never make the camera up vector parallel to its viewing direction.
- When replacing a visible component, update label anchors as well as tours and inventory. A stale CASE Inlet bell anchor caused repeated explode_mm errors. Browser verification now selects the new inlet label and exercises all view modes. Axial section limits derive from the expanded model bounds.
- The final geometry and browser checks do not change baseline hardware requirement status. Mount compliance, fastener preload and locking, normal wall thickness, thermal gaps, fabrication splits, and aerodynamic losses remain open.
- Associate an authentic nTop UI image with both its image hash and the native notebook hash. Do not embed an earlier capture as evidence for a later geometry correction. The report builder includes such a capture only when its receipt matches the current notebook.

## P5 spline/revolve and attachment preparation, 2026-09-09

- The user requests a larger bell, fuller compressor-side proportions, smoother flowpath and explicit casing attachment logic. Keep P5 separate from P4. Treat larger housing proportions separately from rotor redesign and engine rematching. The rotor-scope clarification is still unanswered.
- Measured native identifiers are `spline_by_control_points<list<point>,integer>[5.20.0]`, `profile_from_curves<list<curve_interface>,vector>[5.20.0]`, and `revolve<new_profile,axis,real>[5.20.0]`. Profile from Curves accepts native spline and line-segment variables in a curve_interface list. The profile normal is native Y; the revolution axis is native Z.
- Four control points and degree three produce a cubic Bezier segment. A closed chain of six cubic splines and two straight closures produced the P5 bell wall. The curve directions join tangentially at the bell, rounded lip and outer return. The complete 42-variable pilot imported and saved in 2.04 seconds.
- The 20-variable dependency-closure pilot export used 0.5 mm Adaptive Mesh followed by Sharpen. It completed in 14.02 seconds and contains 1,507,034 triangles with zero open or nonmanifold edges. All 36 radial profile rays pass the 0.12 mm geometric screen. Meridional sampled wall spacing is 1.48793-1.50041 mm. This is not a production thickness tolerance or aerodynamic validation.
- Set PyVista camera parallel_scale explicitly after enabling parallel projection. Leaving its default produced an unusable extreme close-up. When retaining the negative-Y half of a meridional cut, place the camera on positive Y to see the cut and inlet interior.
- A circumferential screw pattern must respect access windows. Two front positions fell inside the proposed electrical opening. The staged recipe now uses six front panel screws and eight at each other support station. Washer-seat and tool-access checks still require actual full-assembly exports.
- A support ring added to an existing flange changes the clamped grip and required screw length. The proposed 6 mm rings give total grips of 12, 12.5 and 12 mm at J01/J02/J03. M4 x 20 with the retained washers and nuts gives nominal protrusions of 3.2, 2.7 and 3.2 mm. These arithmetic results do not establish preload, strength or clearance.
- Do not expose unused scalar controls for discrete standard hardware. P5 hardware sizes and pattern selections are recipe-level configuration values; rebuild after changing them. Continuous shape, wall and ring dimensions remain native scalar parameters.
- Windows locked before the complete native P5 launch. The observed console input failed with `failed to activate captured window`; a fresh capture showed the lock screen. Stop UI input. P5's full recipe, native runner, verification/export preparation and presentation scripts are staged, but the full engine revision is not executed or verified.
- `P5_Inlet/run_pipeline.py` can run the native assembly and then wait for host verification. Exports start only when readiness hashes match the current native readback and export manifest. Launch it once from the unlocked dedicated API console; do not inject new UI commands while locked.
