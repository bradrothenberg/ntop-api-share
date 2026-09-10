# Recorded lessons

This is an edited record of prior work. Its native results apply to those recorded revisions.
Local machine paths and omitted artifact links were removed for this public handoff.
Historical tool and artifact names below describe the source work. Use README.md for the runnable commands and files in this checkout.

> Historical source snapshot. Use the local AGENTS.md and README.md for portable setup.

# I6 Astra agent record

## User constraints
- Build from scratch in i6-astra. Read the reference folder to learn the API.
- Produce a highly detailed preliminary inline-six model in nTop.
- Follow the nTop design skill in the final report.
- Record learnings here and finish the work autonomously.
- Use uv for all host Python execution. No emojis or em dashes.
- Added user constraints: real gears, belts, assembly bolts, and custom sections.
  Persisted in the local AGENTS.md and design specification.

## Reference learning
- The GUI Notebook API speaks display units. Recipe literals use explicit SI units.
- A reused output must be a named variable. Plain block fan-out can lose a wire.
- Recipe references resolve within one import. They cannot reference an earlier import.
- Small STL tolerance can increase cost and can drop parts. Check actual mesh bounds.
- The console transport needs desktop access outside the sandbox on this machine.
- Native notebook sections, colors and cameras use saved container data because the
  prototype API has no methods for these settings.

## Provenance
Geometry and the new generator are authored for this task. The neighboring
I6Engine is a reference for measured API behavior, not an engine geometry source.
The console transport and container organizer are reused with attribution.

## Measured findings
- The initial hollow-cylinder STL has zero open edges. Its measured bounds are
  +/-43.0027 mm radially and -0.00468 to 60.00468 mm axially.
- Boolean recipe literals use `{"val": false}`, not bare `false`. A bare Boolean
  caused `Error adding roots` on the native profile-extrusion probe.
- The corrected involute gear probe imports and exports in 2.137 seconds. Its
  STL has 30,576 triangles and zero open edges at 1.5 mm input tolerance.
- The requested AT mesher uses
  `mesh_by_adaptive_tets<implicit,real_field,bool>[5.42.0]`.
  Its inputs are Body, Tolerance and Remesh. Remesh is false in this study.
- Sharpen uses `sharpen_mesh<mesh,implicit,integer,mesh_sharpen_enum>`.
  It receives the AT mesh and the same implicit source. This study uses one
  iteration and enum 0, which is None for remeshing.
- The AT + Sharpen gear probe took 1.709 seconds at 0.658 mm tolerance.
  It has 59,128 triangles and zero open edges. The earlier probe used a different
  tolerance, so these timings do not establish a controlled speed comparison.
- The recipe profile extrusion requires Profile, Distance, Draft Angle,
  Symmetric and Direction. The profile is native, not an imported mesh.

## Geometry and verification learnings
- A positive overlap must connect piston pin bosses to the skirt. A group that
  looks like six pistons can contain eighteen disconnected pieces. Count regions.
- Check bearing-cap and bulkhead extents together. Coplanar casing faces cause
  poor section views and can hide a real overlap in the assembly.
- Closed spring-end coils need to join the active helix. Mesh fragments at a
  clipped helix end are visible through connected-region checks.
- Resolve gear clearance with a finer local mesh. The sampled 24/36T profiles
  have no intersection in 61 positions across a tooth period. The smallest
  two-dimensional gap is 0.112795 mm. This is not a loaded contact analysis.
- A belt backing can use exact native disks joined by external tangent polygons.
  This avoids a large sampled boundary while preserving the circular pulley wraps.
- A lightening hole must cut the pulley flanges as well as its web to remain open.
- The full native graph and the mesh-export graph serve different purposes.
  Save the full native graph first. Export subsystem closures in scratch notebooks
  so a large assembly does not repeat every meshing operation on each edit.
- Render-only mesh simplification must not become the measurement source.
  All reported bounds and topology checks use the original nTop STL exports.

## Intentional preliminary scope
- Dimensions are selected design inputs. The report labels calculated and measured
  quantities separately. No power, mass, stress, temperature or life is claimed.
- Crank angle drives the native slider-crank mechanism. The valve, cam and belt
  systems show the source-generated 30 degree review pose.
- Fasteners have modeled shanks, head flats, chamfers, washers and rod-bolt sockets.
  Thread helices and a complete production fastener specification are omitted.
- Production gear roots, belt tooth standards, materials, tolerances, sealing,
  full interference sweeps, flow and durability remain engineering work.

## Final export and numerical audit
- All 52 final export groups have zero open edges. They contain 38,036,616
  triangles before render-only simplification.
- Measured assembly spans are 891.8109 x 571.0074 x 544.0090 mm along X, Y and Z.
- Connectivity checks confirm one crankshaft, six pistons, six liners, twenty-four
  valve springs and two separate oil-pump gears.
- The spring AT mesh had 24 full coils and 32 isolated islands. The islands had
  396 triangles and a total volume of 0.000556208 mm^3. The largest island was
  0.000111883 mm^3. The unfiltered mesh is retained as evidence.
- The final spring export uses native Split Mesh, Filter Mesh List and Merge
  Meshes after Sharpen Mesh. A 0.01 mm^3 volume threshold removes only those
  islands. It retains the complete coils and their original surface triangles.
- Filter Mesh List's Volume Threshold is dimensional. A 1.0 API input exported
  as 1.6387064e-5 m^3, confirming the fresh notebook's cubic-inch display units.
- The native scalar sweep covers 0, 30, 90, 180, 270, 360, 470, 615 and 720 degrees.
  Across 54 pin positions, the largest equation/readback difference is
  7.11e-14 mm. The largest rod-angle difference is 1.95e-14 degrees.
- Native swept volume agrees with the independent 3206.460259 cm^3 calculation
  within 1.37e-12 cm^3. These are numerical agreement checks, not manufacturing
  tolerance or real-engine performance claims.
- The maximum piston-crown Z differs from the analytical review pose by
  0.017827 mm in the original exported mesh.

## Runtime and presentation learning
- The setter can report "was not carried out" after changing the value.
  Read the value back, then retry only if it still differs from the request.
- A busy nTop window can make global UI Automation searches slow. Query a known
  console handle directly and verify its process id. A separate scratch session
  can export independent subsystem closures while the full notebook imports.
- Decimation of the fine gear-pair mesh produced visible shading artifacts on
  large planar faces. The final gear detail renders the original mesh instead.
- The HTML report includes the complete nTop Docs V1 CSS unchanged, with local
  font and figure overrides. The PDF uses the same palette and typography roles.
- Screen-space ambient occlusion caused regular shading bands with the parallel
  camera on the full assembly. The final figures disable that effect. Their
  geometry and measurement meshes do not change.
- The spring Sharpen block retained a native self-intersection warning before
  island filtering. Zero open edges does not establish intersection-free surfaces.
  The report keeps a downstream surface-intersection audit open.

## Native graph packaging
- The 4,259 authored function/variable blocks expand to 13,914 native records,
  including the root and 9,654 literal values. The full recipe import was slow.
- A native packager uses the graph and leaf-table schema measured from this
  project's API-generated empty, gear, kinematic and spring notebooks.
- The gear, 125-node kinematic graph and 448-node spring graph match the API's
  saved graph exactly after excluding anonymous display names and volatile
  evaluation status. Their literal tables match exactly, including units.
- Point lists inherit length units. Implicit-body variables clear field units
  when holding a scalar field. These details were measured against API saves.
- The small packaged gear opened, exported its recipe and saved through the API
  in 2.465 seconds. The full engine completed the same API cycle in 231.626 seconds.
- All 168 full-engine variables match the source after canonical comparison.
  The API refines the return type of rotated/translated primitives from implicit
  to cylinder or box. Only that measured type refinement, generated IDs and display
  names are normalized. Functions, topology, references and values are compared.
- The saved graph has 13,914 records and no stored evaluation error messages.
  Full-assembly pin readbacks match the 30 degree pose within 2.84e-14 mm.
- The superseded direct recipe import was stopped after 3,184.96 seconds. The
  original user notebook was preserved in `evidence/reference_checkpoint.ntop`.
  The verified full native replacement was saved before the process was stopped.
- Fourteen custom sections organize 71 colored final groups. The inspection
  notebook hides covers and manifolds and makes five casing groups transparent.
- Every final PDF page was rendered and visually checked. The final ten-page
  report documents the spring surface warning and preliminary engineering scope.
- Both assembled and inspection notebooks were opened through the API and
  visually inspected in nTop. Their geometry graphs and literal tables remain
  equal to the verified raw save. The assembled GUI save took 98.73 seconds.
- The internal inspection view is left open in nTop. Captures of both views are
  retained in `evidence/`. All ten HTML images loaded, with no horizontal overflow.
- The final package validator checks fourteen sections, 71/61 visible groups,
  the two inventories, all local HTML resources and ten PDF pages. The manifest
  records SHA-256 hashes for the model, source, report, figures and final meshes.

## Revision 2 final record

The native graph now has 254 variables, 16 sections, 80 final groups and 192
modeled fasteners. It contains 14,436 native records. All source
variables match the final API readback. The 60 final exports contain
39,790,656 triangles with zero open edges.

### Spline and routing findings
- A native cubic spline's scalar-field property can be offset directly into a
  solid tube. Subtracting a second offset makes the bore. The direct offset,
  seeded offset and thicken probes produced the same 157,020-triangle mesh hash.
  This corrects the earlier broad assumption based on polycurve offset failures.
- Global endpoint halfspaces can cut distant sections of a hose that doubles
  back. Restrict each outward halfspace to a sphere of 1.05 times the outer radius,
  then subtract that local cap cutter. The corrected result has exactly two
  coolant-hose components and four hard-line components, with zero open edges.
- Keep centerlines and endpoint planes as named variables. Shared references
  remain stable through native packing and API readback.
- Exhaust primaries and collectors now use continuous cubic centerlines.
  Electrical and fluid sections retain wire branches, connectors, supports,
  hollow hoses, hard lines, fittings and bands.

### Native motion findings
- Source mesh import and viewport rendering completed in approximately five
  seconds per frame in the measured three-frame probe. A 72-frame native capture
  succeeded. The final video contains 72 distinct image hashes, four repeated
  720-degree cycles, and 12 seconds at 24 FPS.
- Mesh poses use independent equations that agree with native kinematic
  readbacks. nTop renders the posed native source surfaces. This is not a full
  implicit reevaluation per frame. Thirteen spring shapes were evaluated natively
  at their distinct installed lengths instead of axially scaling a spring mesh.
- Crank rotation is negative about X for increasing review angle. Cams must
  rotate in the same direction at half speed for an open timing belt. Mirror the
  cam phase definition while preserving cosine lift to make the directions agree.
- Belt envelopes are stationary; pulleys rotate. The disengaged starter pinion
  is omitted in the running view. Loads, combustion and dynamics are not solved.

### DOE findings
- Fixed-seed Latin hypercube: 15 cases, PCG64 seed 602026. Chosen bounds are scale
  0.85-1.16, RPM 4500-6500 and BMEP 8.5-12.5 bar. All exact inputs and source hash
  are in doe/study.json. Bounds are assumptions, not validated operating limits.
- Derived sizes span 2.07-4.92 L. Estimated output spans 122-374 hp.
  kW = BMEP_bar * V_L * RPM / 1200. These are BMEP surrogate estimates.
- Evaluate scalar checks as dimensionless labeled values to avoid confusing
  GUI display units with horsepower, liters or RPM.
- nTop import/export removes some duplicate preview facets. Raw triangle counts
  can differ without losing a surface. Map vertices and compare unique facets.
  The audited unique surfaces match. Retain original source and native output
  counts in the evidence instead of forcing an equality that is not required.
- The complete native preview export verifies each geometric scale. Fifteen full
  implicit notebooks preserve the detailed editable graph, but are not remeshed
  independently. Images use the same camera and restore source part colors.

### Presentation and remaining limits
- The HTML follows the reference showcase structure and nTop Docs V1 grammar.
  It embeds the native video, 15-frame GIF, annotated grid, formulas, source links,
  data downloads and configuration notebooks. A portable media-embedded HTML
  artifact is also supplied. The PDF has 12 pages.
- Preserve the spring intersection caveat, preliminary route-interface scope,
  power assumptions and animation provenance. No strength, flow, thermal,
  combustion or complete interference validation is claimed.



## Revision 3 final record and learnings

- Built 100 configurations using a stratified Latin hypercube, PCG64 seed
  60906100. Bore, stroke, pitch and rod ratio vary independently. RPM and BMEP
  are additional assumed operating factors. The exact input table is preserved.
- Generated 200 native mesh notebooks and captured all 200 views in nTop.
  The 100 exterior captures and 100 section captures are individually unique.
  All native scalar checks pass. Maximum error: 1.137e-13.
- Fit actual transformed crank-journal vertices for all six throws in each case.
  Maximum fitted center error: 0.018396 mm.
  This checks surfaces in addition to the placement equations. Liner radius
  checks use a 0.06 mm tolerance for the simplified source surface.
- Fixed outer width and fixed starter-ring spans distinguish this study from
  uniform scaling. Block length, bore/stroke ratio and deck height vary.
- Mesh view colors must contain four RGBA values. Three-value RGB caused nTop
  to reset the complete view list to gray wireframe without an API exception.
  Rebuilt the pilot with RGBA, then visually verified before running the batch.
- A common camera quaternion, orthographic extent and crop prevent per-case
  auto-fit from hiding dimension changes. The capture crop removes only native
  UI chrome. Image annotations identify the actual case and assumed output.
- A full implicit Scale Object wrapper case did not finish its optional readback
  check in roughly 30 minutes. Its source was preserved. The scratch process was
  stopped after a new nTop instance verified the compact configuration workflow.
  Detailed evidence: evidence/r2/full_case_interrupted.json. Do not report this
  interrupted operation as a successful full implicit configuration solve.
- Shape maps are useful for packaging studies but do not enforce production
  interfaces. The study explicitly keeps belt pitch, fitting alignment and
  complete interference validation open. Editing documentary dimension rows
  does not regenerate imported mesh geometry.
- Kept the original 15-case data, media, implicit models and Revision 2 PDF.
  Archived Revision 2 HTML before replacing the live report. Revision 3 uses
  linked local media to keep a 100-card report responsive.

## Revision 4 workflow learnings

- Keep the exact Revision 3 DOE table and animation order. Hold each case for
  one 720-degree cycle. Use the case's stroke and rod length in the slider-crank
  equations. Move cylinder stations with pitch and piston diameters with bore.
- A live native motion notebook with 267 variables loaded in 51.116 seconds.
  Phase-zero evaluation and capture took 69.74 seconds. The numerical native
  check passed with maximum error 1.421e-14. The next Frame index setter was
  rejected by the API. This probe does not establish a working native sequence.
- Render the complete new sequence with PyVista/VTK using nTop-exported part
  meshes and native spring surfaces. Clearly identify this renderer in the
  report. Do not label this new sequence as nTop viewport capture.
- PyVista clear() removes lights. Restore the light kit after clearing each
  case. Without this step, surface colors look flat despite correct normals.
  Check the first frame visually before starting the complete batch.
- Actor user_matrix transforms avoid rewriting mesh vertices each frame.
  Apply local deformation once per case, then use rigid poses for motion.
  Move each rod's cap bolts with its rod. Audit the actual pose matrix's little
  end against the piston pin on every frame.
- Keep the original thirteen native spring meshes. Select the installed-length
  surface for each valve lift. Use a fixed spring base and move the valve and
  bucket along the mounted valve axis. Retain the earlier spring-contact caveat.
- Camera position, projection and scale stay fixed for all 100 cases. Check
  geometry bounds separately from annotation pixels. Compare cropped geometry
  hashes so changing labels alone cannot pass the motion uniqueness check.
- Video playback is slowed to 120 RPM at 24 FPS. Case-specific RPM and BMEP
  only set the output estimate. Explain this distinction beside the media.
- Preserve prior animations and archive Revision 3 HTML before adding R4.
  Keep the running section extension in the report generator, so rebuilding
  the 100-case grid does not remove the new animation.

- Keep the requested start-case selection separate from playback progress.
  Updating the selector on timeupdate can overwrite a chosen case when the
  user changes speed before pressing Play from case.
- Browser video seeking requires byte-range responses. The basic Python HTTP
  preview reported a seekable range of 0-0 and reset seeks to zero. The scoped
  range-aware preview reports 0-100 seconds and correctly starts at 77 seconds.
- Automatic approval review rejected serving the entire project folder. Use
  an isolated preview with HTML and display assets only. No notebooks, source
  scripts or evidence directories need to be exposed for playback testing.

### Revision 4 completion measurements

- 100 cases, 24 frames each, 2,400 unique full frames. Each case also has
  24 unique geometry-only crops.
- 14,400 slider-crank checks pass. Maximum rod-to-pin alignment error:
  5.729e-14 mm. Maximum full-stroke error:
  1.421e-14 mm. All twelve valve positions open and close.
- The MP4 decodes to 2,400 frames over 100 seconds. The GIF has 1,200 frames
  and a measured duration of 100.01 seconds.
- No geometry touches the frame boundary. The extreme-case review sheet uses
  bore, stroke, pitch and rod-length extremes at four crank phases.
- Summed measured case rendering time: 426.89 seconds,
  excluding startup and encoding. Complete checks are in doe100_running.

## Revision 5 split-screen learnings

- Added 2,400 exterior frames using the existing scene motion calculations.
  Restore static exterior groups and disable casing clips. Keep identical
  camera position, orthographic scale, case order and crank phases.
- Include fixed fasteners with their component anchors. Connectivity region
  labels map each complete fastener to a rigid placement offset. Do not stretch
  fastener heads when the cylinder spacing changes.
- Reuse section JPEGs directly with ffmpeg hstack. Both inputs use 24 FPS and
  the same zero-based frame names. No scaling, interpolation or section rendering
  is needed. Encoded video compression is separate from source-frame preservation.
- Exact phase dictionaries match for all 2,400 exterior frames. Original section
  hashes match before and after rendering and encoding. Minimum unique exterior
  geometry frames per case: 24.
- The 2880 x 960 video decodes without errors and contains 2,400 paired frames.
  Measured exterior rendering time: 622.28 seconds, excluding
  startup and encoding. Video size: 28020966 bytes.
- Keep the split-screen report extension in the generator. Preserve the R4
  section-only media, earlier sweeps and 100-case grid.
- Browser playback passed case seeking, quarter-speed playback and pause checks.
  The complete 100-second video is seekable. The report fits a 1280-pixel viewport.

## Cancelled exhaust-side view

- The user cancelled the exterior camera change. R5 video and report stay unchanged.
  One separate pilot case was rendered; no full sweep or report update was made.
- The bronze circles on the block are the twelve recessed core plugs, six per side.
  The source definition is in scripts/build_engine.py under Cylinder block.

## Revision 7 overview film learnings

- Keep individual source parts addressable when making exploded views. A merged
  material actor cannot independently separate the cover, head, block and sump.
- Apply display translations after the verified moving-part matrices. Restore
  each spring's original mount before applying a new frame's display offset.
  Otherwise spring offsets accumulate across frames.
- Group whole fixed fasteners by nearest authored fastener location and its
  assembly metadata. Do not stretch a fastener or separate its constituent faces.
- Use a fixed orthographic scale during configuration comparisons. A scripted
  pointer and selected card communicate the case change. Label these presentation
  graphics honestly; they are not native nTop UI captures.
- Track annotation leaders from projected actor-group bounds. Keep labels outside
  the center mechanism. Check all chapter layouts before the full render.
- A sub-minute pilot rendered 42 frames and storyboard samples in 42.12 seconds.
  The crank close-up initially clipped the flywheel; increasing its scale and
  centering on the complete moving group corrected the issue before full rendering.
- Close-up exhaust tubes use the complete native source surfaces. The reduced
  motion templates made their curvature look faceted. The original headers have
  1,772,166 triangles and the collectors have 415,144. A 17.17-second detail probe
  verified the corrected shot before replacing that chapter's 192 frames.
- Final movie: 1,728 decoded frames, 24 FPS, 72 seconds, 1920 x 1080 pixels.
  Measured rendering time, including the close-up revision: 415.61
  seconds. Maximum assembled
  rod-to-pin error: 5.684e-14 mm. All nine chapters contain
  geometry motion. Existing R5 video and poster hashes are unchanged.
- The four-stroke display is a phase guide, not a combustion simulation. Exploded
  movement is illustrative. The source spring-contact and belt-envelope limits
  remain. Source geometry is from nTop; the film renderer is PyVista/VTK.
- Browser playback confirmed the 72-second seekable duration and nine chapter
  controls. Chapter jumps to 14 and 52 seconds started playback without errors.

## Revision 8 presentation-style learnings

- The nTop Design V1.1 presentation grammar differs from the document grammar.
  Use cream content backgrounds, blue working accents, open layouts and fixed
  footer chrome for this film. Remove the orange card-based visual treatment.
- Use Aeonik Fono for labels and numeric chrome, and installed Aeonik Regular/Bold
  for body text and headings, per the user's preference. This overrides the skill's
  current IBM Plex Mono pairing. Check the per-user Windows Fonts
  The footer uses a text wordmark, not a claimed official logo asset.
- Aeonik Fono has mono-style forms but varying glyph advances. Measure each
  glyph when applying letter spacing; do not assume a fixed character width.
- Keep the existing scene, cameras and pose equations. All 1,728 R8 motion
  receipts match R7. The original R7 movie hash is unchanged.
- On cream backgrounds, dark belt geometry becomes easier to see. The valve
  close-up needed a 25-pixel upward placement shift to clear the fixed footer.
  The camera and engine geometry remain unchanged.
- User requirement: no mouse pointer. Show a brief blue press highlight followed
  by the selected row's persistent blue type and square indicator. Verify the
  transient highlight and its return to open styling with actual frame pixels.
- Final film: 1,728 frames, 72 seconds, 24 FPS, 1920 x 1080 pixels. Measured
  rendering time: 321.03 seconds. Full decoding and source-frame
  comparisons passed. The report retains nine chapter buttons and prior media.

- Browser delivery check passed: architecture and configuration chapter buttons seek
  and play the new MP4. Duration and seekable range are 72 seconds. No media
  error or horizontal overflow was observed. Close the isolated preview afterward.

## Revision 9 fixed callout and section learnings

- Supersede the R7 tracked-bound annotation advice for this film. The user wants
  leaders and text fixed on screen while the internal mechanism operates.
- Use a dedicated geometry viewport and a separate label column. Match a numbered
  marker on each component region to its label. Route leaders in vertical order.
- Fixed world datums and fixed inspection cameras give identical screen endpoints.
  Rasterize the annotation overlay once per chapter at three times resolution.
  Downsample with Lanczos and reuse the exact overlay. Use two-pixel blue lines
  with a cream clearance line. Do not use changing group bounds or integer-only
  one-pixel leaders. All 768 annotated frames retain identical label pixels.
- Omit leaders during large assembly transitions. Fixed leaders cannot accurately
  identify parts that are moving to separate display locations.
- A narrower engine viewport needs independent camera-margin checks. Increase
  the close-up orthographic scale enough to retain the flywheel and timing drive.
- A clipping plane that clears the assembled engine may still clip an exploded
  manifold. Move the disabled plane well outside all exploded geometry.
- The opening display plane is parallel to XZ, the engine-length direction, and
  traverses Y from -500 to +180 mm before returning. Static surfaces are clipped;
  the complete moving mechanism is retained. The plane outline appears only when
  it crosses the package. Source implicit geometry remains unchanged.
- The final study retains all 100 exact DOE cases and their prior sequence.
  Each receives 48 frames with 15-degree crank steps, two seconds at 24 FPS.
  This displays 60 RPM. Specs use the exact study inputs and surrogate outputs.
- The original spring library samples 10-degree crank poses. The 15-degree
  display sequence needs additional lengths. Axially map the nearest native
  spring surface to 36 minus lift mm and recompute normals. Keep coil diameter.
  This slightly changes axial wire section and is display geometry. Record each
  source lift and scale in overview_clear/intermediate_springs.json.
- Use the requested closing text: A very early preliminary design model for reference.
- Final rendering took 1525.30 seconds. All 6,528 frames decoded.
  R8 movie hashes remain unchanged. Source meshes are from nTop; the film is
  rendered in PyVista/VTK. Aeonik and Aeonik Fono remain the project font pairing.

- Match the opening camera endpoint to the next chapter to avoid an angular jump.
  The refresh-opening command updates only those 144 frames and their receipts.
- Browser checks passed at 14, 67 and 267 seconds. The full 272-second timeline
  is seekable with no video error or horizontal overflow. The final report links
  to the R9 storyboard with all ten chapters and 100 exact case specifications.

## Revision 10 pacing and paired-view learnings

- The user found the six-second section sweep too fast. Slow the section motion
  independently of mechanism motion. Use an eighteen-second opening with a
  three-second centerline hold. Crank motion remains ten degrees per 24 FPS frame.
- Spend most sweep time inside the package, not crossing empty space. The moving
  housing plane traverses Y, parallel to the XZ engine-length plane. Keep moving
  mechanisms complete and match camera and crank phase at the next chapter.
- The R9 two-pixel blue leaders were too prominent. Supersede that setting with
  one-pixel muted gray-blue leaders and smaller ten-pixel-radius numbered markers.
  Keep the three-times-resolution overlay and fixed annotation positions.
- Combine the selected-variant and full-family chapters into one synchronized
  comparison. Use section left, exterior right and a shared spec strip below.
  Preserve all 100 IDs, exact study inputs, estimated outputs and case order.
- Reuse the 4,800 R9 section images with a verified source hash and matching
  crank receipt. Crop above the baked slide rule and footer before recomposition.
  Render matching exterior poses with the same camera and fifteen-degree steps.
- Each case receives 48 frames, one 720-degree cycle, two seconds at 24 FPS.
  Output estimates retain the study's RPM and assumed BMEP. They are not tests.
- The pilot rendered 22 sample frames in 33.78 seconds. The complete render took
  1633.29 seconds. All 6,456 encoded frames decoded successfully.
  All 768 label-column frames retained identical pixels within each chapter.
- Preserve R9 video bytes and archived reports. Update chapter links when timeline
  durations change. This edition has nine chapters and lasts 269 seconds.
- Source surfaces remain nTop-authored. Rendering is PyVista/VTK. Do not describe
  the movie as a native nTop viewport capture. Aeonik and Aeonik Fono remain in use.
- The encoded label columns had zero change at the 99th percentile between
  adjacent frames. Mean gray-level change stayed below 0.00001 on a 0-255 scale.
- Browser playback passed at the opening, architecture, paired family and closing
  chapters. The 269-second video is fully seekable. All 718 local links resolve.

## Collapse-on-save skill update

- User default: deliver saved notebooks with all authored blocks and custom
  sections collapsed. This is now part of the local ntop-notebook-api skill.
- Block records use `open[].collapsed`; sections use
  `sections.decorations[].collapse`. Preserve the `100_` root notebook group.
- The skill helper rewrites only those flags and container lengths/offsets.
  Geometry, caches, visibility, colors, cameras and other UI fields remain intact.
- A separate I6 test copy collapsed 14,991 block records and 16 sections.
  Non-UI chunks remained byte-identical. Repeated collapse was byte-idempotent.
  This was a file-level check, without a live GUI reopen. The source was unchanged.
- Retain the API-saved working file and write a separate collapsed deliverable.
  Apply the helper after the last save; later GUI saves can replace this UI state.
  Evidence: evidence/collapse_skill/verification.json.
