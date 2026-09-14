# Recent modeling lessons: September 12-13, 2026

This review extracts reusable lessons from the bulkhead, marine propeller, ski, KestrelSAT, and DDG(X) work. The [source snapshot](evidence/recent-modeling-sources.json) records the reviewed file hashes. The [recorded results](evidence/recent-modeling-results.json) retain selected measurements without private paths or geometry files.

These are lessons from existing work. This update performs source comparison and offline package checks. It does not rerun native geometry, import complete models, or refresh the bundled demo snapshots. Some source tasks remain active; the hashes identify this review's scope.

Use [build 42926 API guidance](API_REFERENCE.md) for new API work. Bulkhead and marine notes identify build 42926. Ski and KestrelSAT results retain their recorded build 42594 context. DDG(X) meshing notes also record build 42594. A method observed on one build needs a new check before claiming compatibility with another.

| Work | Reusable lesson | Evidence boundary |
|---|---|---|
| Bulkheads | Independent pocket imports, explicit control wiring, and separate export acceptance | 286 native body samples passed; direct full-field meshing failed |
| Marine prop | Preserve physical edge identity and finish mechanical interfaces after blending | Saved-graph orientation and native shoulder checks are separate |
| Skis | Distinguish field blends, physical rolling-ball geometry, and display meshes | Full-ski continuous fields and local canal pilots have different scopes |
| KestrelSAT | Audit complete input-driven expressions when changing assembly presentation | 28 native body expressions match; a render cannot reveal every hidden part |
| DDG(X) | Drive attachments from their supports and check them across variants | 4,650 recorded native contact samples across ten versions |

## Bulkheads: complete modules and separate acceptance checks

Large imports stalled even though a small pocket pilot succeeded. The recorded recovery imports the perimeter first, then independent pocket groups. Each group contains its local controls and full dependency closure. Live API calls then clear and connect those controls to the shared variables.

This does not establish automatic reference resolution between separate imports. Inspect each connection, reject recorded connection errors, check block states, and save a checkpoint after each completed group. Resume from verified saved progress and command receipts, not a guessed loop index.

The final Boolean can cost much more than an individual pocket. Measure the final dependency closure separately. Keep meshing and export blocks out of the authoring pilot when they are unnecessary. The marine work also shows that importing a small graph can reevaluate existing expensive exports.

For a simple planar pocket, the source uses an exact sphere-offset construction from a planar core and a half-space. Validate radius contacts and retained material in a small coupon before generalizing it. A successful general smooth Boolean does not prove a constant physical fillet radius.

The finished-body receipt passes 286 native field samples. Two later full-field mesh attempts ended without completion receipts. Their STL files still contained the placeholder body used to prepare the export graph. File existence was therefore insufficient evidence of a successful export.

Check completion, source identity, actual extents, topology, and sampled geometry before accepting a mesh. Preserve failed outputs and their receipts. A separate STEP-derived display mesh was accepted for presentation, while the detailed notebook retained editable native pocket fields. Label that display route explicitly.

The independent STEP and native-field comparisons also retain a failed earlier CAD volume assertion. Preserve conflicting evidence and explain the independent check. Do not silently replace a failed comparison with a different metric.

## Marine propeller: frame continuity is not edge identity

A forced positive angle wrap added almost a full turn to the frame. Choosing the shorter rotation removed a visible peak. However, that change alone did not preserve the physical leading edge through the return.

The R3 saved-graph check found reversed nose/tail orientation at 40 of 81 nominal stations. Smooth rails, unsigned endpoint angles, and a watertight mesh missed the error. Define foil nose and tail consistently, with an explicit shaft axis, rotation sense, and inflow direction.

Check signed nose-to-tail separation in each local station frame. Inspect the saved profile and point expressions, then sample the continuous law between construction stations. The R5 record contains seven trim cases with 121 stations each and no reversed stations. These are saved-graph checks, not a hydrodynamic result.

Rotate the starting profile with the forward frame trim. Keep endpoint weighting and tangent-frame construction consistent. Use colored native edge traces and section probes when orientation is difficult to see in the surface.

Blending can also damage a previously correct interface. The smooth blade/barrel union added material above the cap seat. The accepted R5 operation applies a bounded annular finishing envelope after the blend. It preserves the seating plane and locating spigot while retaining the rail geometry and separate hardware.

The shoulder record includes 72 native samples. Its mesh still has finite deviations from the nominal seat and spigot. Inspect those deviations and the mating clearance separately. A nominally flat field boundary does not make a tessellated mesh exact.

The later R6 blend-taper candidate remains unverified in the reviewed source. A smooth scalar taper does not prove a smooth final surface, valid clearance, or a successful native build. Do not promote that candidate's proposed settings as accepted practice.

Two API details are useful beyond propellers. A computed rotated-point property was not readable through the attempted scalar wrapper. Evaluating coordinate-plane fields at that point provided a measured workaround. Read the returned units. The recorded `polyline<list<point>>[5.20.0]` block returns `polycurve`; query the output type instead of inferring it from the name.

## Skis: measure geometry in physical coordinates

A circular blend in field coordinates can have a different radius after a nonlinear map. General rounded combinations of non-distance fields do not establish an exact rolling-ball surface. Use the actual mapped parent surfaces and unit normals when physical radius is the requirement.

For a radius R, a rolling-ball center lies on both parent surfaces offset by R along their unit normals. The canal field measures distance to that center curve and subtracts R. Retain the valid contact sector and handle finite endpoints explicitly. An unrestricted tube or endpoint cap can add the wrong material.

Regenerate the center curve when the radius, lean, or parent geometry changes. Changing the tube radius alone breaks parent tangency. Test contact position, normal alignment, available clearance, and nearby blend interactions. A larger requested radius can fail to fit even when its mathematical construction is valid.

The local native curve pilot passed 168 checks. A separate closed-pocket pilot passed 126 sampled contact checks. Reducing the continuation step resolved that local pocket case. Neither result certifies the full ski's rolling-ball conversion, which still had unresolved contact transitions in the reviewed source.

Keep three representations distinct:

- The editable normal-rib model uses local construction radii and mapped fields.
- The corrected rolling-ball preview uses a generated mesh and native implicit conversion. Radius or lean changes require regeneration.
- The full continuous-field ski uses native fields without a mesh dependency. Its saved-file CLI reopen passed 32 checks, but its general blends are not globally constant-radius rolling-ball surfaces.

Binary voxel offsets produced repeated ridges in an earlier preview. Continuous parent-distance evaluation and explicit offset-surface intersection removed that artifact in the corrected workflow. Mesh smoothing was not the correction. A source kernel checkout can help explain behavior, but its commit must match the executable before claiming implementation identity.

Touching bounded patches also left internal zero sheets. Add overlap only within retained material, then test both the old interface and the exterior. The source's sampled exterior comparison supports its tested change; it is not a global equivalence certificate.

Keep analysis attached to its exact geometry and controls. The ski's local beam and section calculations are not nTop's 3D FEA solver. A displacement proxy is not the same observable as a target 3D displacement magnitude. Geometry replacement requires new affected analyses before carrying results forward.

## KestrelSAT: preserve computations through presentation changes

The earlier [skill audit](KESTRELSAT_SKILL_AUDIT.md) already captures the custom-block and fixed-feature resizing contracts. The recent colored native assembly provides a stronger example of presentation verification.

Compare complete default and symbolic body expressions, input defaults, custom definitions, and output contracts. This catches a disconnected control that a default-state picture can hide. The recorded audit compares all 28 native outputs and confirms unchanged computation and input contracts.

A whole-file hash can change because of display order, colors, or saved layout. Preserve the old receipt and establish exact computation identity before inheriting its geometry evidence. Do not rewrite earlier native results to fit the new file hash.

Audit dependencies reachable from the active outputs separately from dormant preview branches. The colored assembly has no active external geometry dependency, but retains five hidden preview dependencies. Those branches still matter if they become visible or are delivered for later use.

Closed, manifold, oriented preview meshes can still report self-intersection. Exact STL-to-indexed-OBJ conversion preserved every triangle and coordinate and removed the vertex-merging warning. The self-intersection warning remained. This does not prove welding caused the problem or that the warning is a false positive.

Use stable family colors and separate native output bodies. Check visibility records and internal groups as well as the exterior image. The recorded render does not independently verify all occluded components or measure a live GUI update time.

## DDG(X): attachments must follow the geometry they meet

The recent construction study found gaps where details used fixed elevations while the deck shape changed. Drive attachment bases from the same deck guide or support geometry. When preserving a shared graph, repair the existing variable so its consumers receive the change.

Define each attachment's intended support. A bridge overhang can connect to its deckhouse without touching the weather deck across its entire footprint. A failed sample at a proposed contact location is not automatically a count of detached components.

The source checks 465 attachment/support intersections per version across ten versions, for 4,650 recorded native checks. This establishes sampled geometric contact. It does not establish joint strength or construction readiness.

Test dependent members after shape changes. The study scans a native loft crossing, then checks rib and longeron membership at the new location and the old reference. Moving guide curves alone does not prove the structure followed them.

Keep hull and upper-assembly controls independent when that is the design contract. Check the applied inputs, transformed feature coordinates, support contacts, and sampled map Jacobian across parameter states. A positive sampled Jacobian is not a global no-folding proof.

Construction-stage files should retain exactly the required source dependencies. Audit that only declared design literals change between variants. Distinguish promoted notebook inputs, named variables, and source recipe values in instructions and captions.

For visualization, the measured default is AT with Remesh enabled, then one Sharpen pass using the same source body. AT Remesh and Sharpen's Remeshing enum are separate settings. Check native warnings, thin-feature coverage, and actual mesh extents. Better median triangle quality does not guarantee better worst-case angles or a simulation-quality mesh.

Use matching camera, scale, clipping, visibility, and lighting when comparing variants. Bind captures to their native source and selected controls. An ordered sequence of evaluated states is not a recording of live interactive recomputation. Display caps and older mesh viewers must retain their separate geometry scope.

## Apply the lessons

Use the [CSG skill](../.agents/skills/ntop-csg-modeling/SKILL.md) for physical feature reconstruction and the [assembly skill](../.agents/skills/ntop-assembly-modeling/SKILL.md) for dependencies, placements, and support checks. The [verification guide](VERIFICATION.md) distinguishes native evaluation, saved graphs, geometry comparisons, and presentation evidence.

The common sequence is a small complete pilot, explicit invariants, saved native readback, targeted geometry checks, and a separate export or presentation check. Preserve rejected attempts. Reuse prior evidence only when its geometry, controls, representation, and measured scope still apply.

## Review checks

All 33 captured source hashes and the referenced result records were checked offline. All four bundled skills validate. The isolated proposed checkout passes all eleven demo smoke checks and all 104 tests without skips. The public-content audit finds no issues in the 15 changed files and their 96 local links. No native model or new native execution is part of this update.
