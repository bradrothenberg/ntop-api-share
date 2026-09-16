# Compound sheet forms

The study-03 builder combines independent parent sections and local formed features in six authored designs. Public sources in `complex-sources.json` establish feature families, without supplier CAD or copied dimensions.

| Case | Parent geometry | Local details | Expected surface handles |
| --- | --- | --- | --- |
| vent_chassis | Six-bend symmetric return-flange section | Six 30° louvers, four mounting holes | 10 |
| beaded_crossmember | Eight-bend crown and 45° joggled feet | Two closed hollow beads, four slots, two holes | 6 |
| stepped_housing | Two-level meridian mapped around a rectangular core | Three hollow floor beads, six flange slots | 6 |
| annular_cover | Revolved neck, decks, 45° cone and flange | Central bore and twelve bolt holes | 13 |
| corrugated_shield | Five waves with twenty signed 60° bends | Six foot slots, five crest holes | 11 |
| cable_panel | Two edge bends | Four two-ended bridges, three pierced dimples, four holes | 15 |

Each closed orientable mesh should have Euler characteristic `2 - 2*handles`. A two-ended bridge adds two handles because its tongue is attached across an opened sheet window. Topology is checked independently of volume and local thickness samples.

## Exact construction

Use the signed arbitrary-angle strip helper from the advanced builder. Its faces are exact normal offsets of line and arc midsurface segments. Extrude one continuous profile for constant sections. The annular part revolves a meridian whose initial tangent is vertical; do not assume every chain starts horizontally.

For a rounded rectangular body, compute `rho = sqrt(max(abs(x)-A,0)^2 + max(abs(y)-B,0)^2)` outside a rectangular core, and map the full normal-offset meridian through `(rho,z)`. This retains continuous rounded corners at each wall level. Account separately for the flat core, straight side regions and rounded ends in the analytic volume.

Closed beads use distance to a line segment. Dimples use radial distance to a center. Remove underlying flat stock and rejoin through a retained flat overlap ring. The formed volume contribution subtracts the displaced parent sheet footprint; retained overlap is counted once. Keep hole/slot footprints on flat stock when applying analytic `area * thickness` deductions.

Compound features must share native coordinate fields. The initial housing and cable-panel import exposed duplicate X-plane variable IDs when separate cutter helpers each constructed coordinates. Cache the X/Y/Z field set on the recipe and make all helpers reuse it. Audit top-level ID uniqueness before native import.

Dimensions are named native real inputs where exposed. Counts, angles, layout ratios and some feature-center coordinates remain source choices. Keep positive thickness, inside radii and straight tangents. Closed bead rise exceeds twice its midsurface radius. A 45° offset leg requires `rise > 2*Rm*(1-cos(45°))`. Maintain clearance between patches, slots, perimeter bends and neighboring features; preserve bridge root overlap. The supplied dimensions are a nominal study domain, not a generally valid optimization range.

## Verification

Check source profile closure and planarity, then explicit native signed-field samples at both sheet faces, retained stock, hollow regions, openings and roots. Export the full native mesh and require watertightness, consistent winding, one component, expected topology, outside extents within 0.02 mm, and volume within 0.25% of exact independent section integrals. Those limits are study checks, not manufacturing tolerances.

The nominal check closures contain 337 probes across the six designs. Changed-input studies add 12 chassis probes at 250 mm length and 35 mm flange rise, and 12 annular-cover probes at 12 mm neck tangent and 26 mm deck tangent. Re-run these checks when adopting a changed recipe; a previous recording does not qualify new values. Preserve recipe/mesh hashes, API e_OK evidence, CLI receipts and geometry-unchanged presentation comparisons in the study directory.

## Motion and translucent tools

The tooling helper uses evaluated native meshes. Bind vertices to their closest analytic midsurface segments with local tangent and normal offsets. Scale signed angles while retaining arc length; scale an initial tangent angle when a neck starts vertically. For local features, keep the parent mapping direction separate from the feature direction in closures. Use floating-point center arrays even for integer-valued centers. Assert that the computed endpoint agrees with every original vertex before rendering.

Start local forms before completing parent flanges. Radial motion at closed beads and drawn corners changes circumferential lengths. Two-ended bridges use an explicit longitudinal mapping to keep both roots attached while unforming; this introduces prescribed in-plane deformation. These are geometric preforms, not inextensible developments or cutting blanks.

Sample two opposing orthographic depth buffers at 1 mm spacing for top and bottom vertical tool envelopes. Each view has its own silhouette mask; fill missing samples from nearby valid heights independently and assert finite values. Using the upper-view mask for both fields can leave lower-view NaNs and produce a blank renderer. Close the sampled surfaces into upper/lower shells with 0.6 mm nominal vertical display clearance and an outer display thickness. This sampling cannot represent every undercut or vertical tool-access requirement.

Use an opaque sheet and low-opacity nTop-blue shells, fixed camera, prescribed closing translations and an opening end hold. The final sheet state uses unmodified native triangles. The helper emits 960 × 720, 7.04-second infinite loops. Decode each actual GIF to verify its size, frame count, durations, changing intermediate images and final hold; provide a poster and accessible play/stop control in the report.

Every animation must identify its scope inside the image: concept tools and prescribed geometry motion, without a material-forming solver. The shells are not qualified die designs and do not include piercing punches. Contact, friction, draw-in, thinning, wrinkling, force, tool release, split tooling and springback remain unsolved. Keep generated media and notebooks outside the shared source skill and Git.


## Embed animations in a portable report

Embed each delivered GIF as a `data:image/gif;base64,...` entry in a JSON payload inside the HTML. Embed the static posters and native figures too, and use the same embedded figure map for the native viewer's image fallback. Set individual GIF download links to the embedded bytes. Native notebooks, source files and optional ZIP bundles may remain separate linked downloads; identify that boundary in the report.

Use an IntersectionObserver to play visible GIF cards and pause offscreen cards, with an explicit stop/play control. Honor `prefers-reduced-motion` by starting paused, while allowing a deliberate play action. Verify each embedded GIF's decoded bytes against the accepted source hash. Test an isolated copy of the HTML without adjacent asset folders, checking all figures, animation playback, download links, mobile layout, fallback and reduced-motion behavior. Large HTML files containing GIFs are generated media and stay out of the shared source repository and Git.
