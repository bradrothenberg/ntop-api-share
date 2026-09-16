# Advanced sheet metal construction

The advanced builder extends the first five examples with a mounting rail, louver panel, closed bead panel, pierced dimple plate and continuous rounded tray. All dimensions in this set are authored. [Public manufacturer sources](advanced-sources.json) establish the feature families, not exact commercial replicas or tooling approval.

## Exact signed bends

`build_advanced_sheet_metal.py` uses the adjacent core builder and field helper. Its `strip` function supports fixed signed turn angles with magnitude below 180 degrees. The worked models use 30, 45 and 90 degrees. Bend angle and feature count are structural builder choices; dimensions, radii, thickness, locations and relevant K-factors are native inputs.

Given midsurface position p, unit tangent u and left normal n, a bend of sign s and radius Rm has center c = p+s*Rm*n. Rotate the tangent by theta. Rotate the initial radius by theta/2 for the arc midpoint, then theta for the endpoint. For a side at normal offset d = +/-t/2, use radius Rm-s*d. Each side is built with exact line and Three Point Arc blocks; join their ends to obtain a closed profile.

Keep positive tangent lengths and Ri > 0. This guarantees positive inner offset radius. Zero-length straights should be removed from the chain rather than emitted as degenerate lines. The offline audit checks closure and planarity; native surface probes check the evaluated bend geometry.

## Four-bend mounting rail

The example uses t = 1.5 mm, Ri = 2 mm, length 180 mm, crown rise 25 mm, tangent feet 16 mm and crown tangent width 34 mm. Starting on a foot, use +90, -90, -90 and +90 degree turns. The wall tangent length is rise-2Rm. Outside width is 2*foot+crown+4Rm; outside height is rise+t.

Extrude the complete profile once. Cut four 18 x 5 mm capsule slots in the feet and four 8 mm crown holes through the appropriate height. In the flat blank, use tangent lengths plus four bend allowances. Map slots to the corresponding flat foot datums; retain crown holes in the middle strip. K changes the blank only.

Require rise > 2Rm and positive foot/crown lengths. Check hole and slot ligaments against the tangent regions when inputs change. Do not infer hardware strength from the geometry.

## Open-ended louver panel

The 180 x 120 mm panel has t = 1 mm, Ri = 1.5 mm, 12 mm high edge flanges and six louver flaps. Each flap has 56 mm span, a 30-degree root bend and a 12 mm tangent leg. The 0.3 mm side clearance and layout are study choices, not catalog values.

Cut each rectangular opening from the panel and replace its material with an exact bent flap. Its 2t-long foot overlaps retained stock behind the root. A native max-of-axis-fields box expresses the rectangular cuts without redundant CAD rectangle profiles. All three coordinate fields are reused.

Separate two lengths:

- Formed opening O = leg + Rm*theta + clearance. It is independent of K.
- Developed flap D = leg + (Ri+K*t)*theta.

In the blank, cut a U-shaped clearance around the sides and front of each flap. Side slots have the chosen clearance and extend to O. The front slot extends from D to O, so its width is clearance+(0.5-K)*t*theta. This preserves the fixed formed opening while K changes the developed material length. Require O > D, clear separation between lances, and all flaps/roots inside the planar region between edge bends. K in the demonstrated 0.25-0.5 range keeps the front clearance positive.

An initial version used D in the formed opening and coupled K to the formed geometry. The accepted model removes that dependency. Recursively tracing the formed output reaches no K input; tracing the blank does. A native K-change check verifies fixed formed faces and moving developed edges. Do not use a whole-recipe input list as evidence of output dependency.

These are open-ended lanced flaps. Closed-end louvers require additional end forming and deformation. No tooling draft, burr direction, shear fracture or die clearance is simulated.

## Closed beads and dimples

Create a radial section containing the desired surface transitions, offset its two sides by +/-t/2 and revolve the closed section. The radial section is the meridian of a forming target.

For a closed bead, start on the raised flat crown, add a -90-degree crown transition, a downward tangent, a +90-degree root transition and a short flat foot. The example uses 5 mm rise, t = 1 mm, Ri = 1.5 mm, 4 mm crown half-width and 70 mm straight bead length. Require rise > 2Rm.

For a capsule bead with straight length ell, evaluate the round master at:

```
rho = sqrt(max(abs(x)-ell/2,0)^2 + y^2)
F_bead(x,y,z) = F_round(rho,0,z)
```

Translate the distance field for repeated beads. This gives circular closed ends and a straight middle sharing the same section. Remove the original floor under each feature; overlap its patch with the retained panel only in the outer flat foot. Leaving the original plate under a closed bead would add material and trap an unintended cavity. Check the underside, volume and connected topology.

For the dimple, start at the pierced hole radius and a depressed inner lip. Use a +45-degree transition, a conical tangent and a -45-degree transition to the outer sheet, then a flat foot. For total depth H, the cone tangent rise is H-2Rm*(1-cos(45 degrees)); divide by sin(45 degrees) for its tangent length. Require this rise to be positive. Revolve the section and place it using circular distance from each hole center.

The example has six 8 mm holes with 1.5 mm inner lips, 3 mm depth, t = 1.2 mm and Ri = 1 mm. Its outer panel is 150 x 110 mm. These are pierced dimples, not qualified screw countersinks. Keep feature footprints and mounting-hole ligaments separate as dimensions change.

The fields use distance to a line segment or point in the sheet plane. Away from their axes, its gradient has unit magnitude; the meridian's normal offsets retain their geometric thickness. At the bead axis the section is a horizontal plateau. These are normal-offset geometric targets, not a variable-thickness forming result.

## Continuous rounded tray

The example uses a 160 x 120 mm outer envelope, t = 1.2 mm, Ri = 2 mm, 18 mm flange rise, 12 mm floor plan radius and 10 mm flange tangent width. Its meridian begins on the floor, turns +90 degrees to the wall, then -90 degrees into the outward flange. Wall tangent height is H-2Rm.

Let r_end be the outer flange radius of this meridian. Set A = L/2-r_end and B = W/2-r_end. Replace circular radius by distance outside the rectangle with half dimensions A and B:

```
dx = max(abs(x)-A,0)
dy = max(abs(y)-B,0)
rho = sqrt(dx*dx+dy*dy)
F_tray(x,y,z) = F_round(rho,0,z)
```

This creates continuous rounded corners with exact meridian bends. The rectangular core maps to the flat center of the round master. Require A,B > 0 and H > 2Rm. Four mounting slots lie in the straight outer flange regions; keep them clear of the upper bends and plan corner transitions.

The tray is a drawn-shape target with continuous corner material. The 45-degree miter cuts from the press-brake enclosure do not belong here. A controlled flange shape may require a separate trimming operation in manufacture. No developed cutting pattern is asserted for this target.

## Independent checks

For a closed meridian with radial coordinate r and height z, use Green integrals A_s = integral(r dz) and M_s = 0.5*integral(r^2 dz), correcting for wire orientation. Integrate exact line and circle segments, rather than mesh triangles.

- An extruded section has volume A_s*length.
- A revolved section has volume 2*pi*M_s.
- A capsule extension adds 2*A_s*ell to the revolved volume.
- A rounded-rectangle tray has volume core_area*t + core_perimeter*A_s + 2*pi*M_s.

For local formed patches, subtract the original planar footprint and add the formed patch volume. Count retained overlap only once. Subtract holes and slots only where they cut flat sheet of known thickness. The rail and louver blank volumes use their independent K-factor strip lengths and actual clearance cuts.

Check native scalar samples, then each full native mesh for watertightness, consistent winding, one component, bounds and volume. The expected through-opening counts are 8 for the rail, 10 for the louver panel, 4 for the bead panel, 10 for the dimple plate and 4 for the tray. Their closed orientable surfaces should have Euler characteristic 2-2*count. The two blanks retain the corresponding topology. This helps catch a collapsed narrow lance or missed hole; it does not replace local thickness checks.

Record source-recipe and mesh hashes. A successful native import or a stale mesh is not a valid current result. Preserve superseded attempts when fixing a dependency. Re-render after a geometry change and verify the report's payload belongs to the accepted export.

## Development boundary

K-factor development is included for the rail and louver panel. Bead ends, dimples and rounded tray corners require in-plane deformation. Do not infer their cutting blanks from a simple geometric unfold. Before manufacturing prediction, add material plasticity and anisotropy, contact, friction, draw-in, thinning, wrinkling, springback and experimental calibration. The examples do not establish a strength benefit or an approved tooling process.

## Recorded native acceptance, 14 September 2026

The five API-authored recipes evaluated on build 42926 with 148 passing nominal signed-field probes. A longer/taller hat rail and larger/taller tray added 43 passing changed-input probes. Changing the louver K-factor from 0.42 to 0.30 added 11 passing probes: the formed opening and flap stayed fixed, while the developed edges moved. This totals 202 recorded native probes. Reproduce these checks before treating a modified recipe as accepted.

All seven native meshes, including two blanks, were closed, consistently wound and single-component with their expected Euler characteristics. Measured volume errors against independent analytic integrals were below 0.123 percent in magnitude, within the 0.25 percent acceptance limit. Expected extents agreed within 0.02 mm. Presentation edits preserved each working notebook's geometry graph. These observations apply to the recorded nominal models and sampled changes, not arbitrary parameter values.

## Forming illustrations and GIF delivery

The animation helper binds each vertex of an evaluated native mesh to the closest analytic midsurface segment, retaining local tangent and normal offsets. For an arc of final length L and changing signed angle alpha, the geometric radius is L/alpha; at zero angle it becomes a straight segment. Straight segment lengths remain fixed. Mirror a half-section for the rail and edge flanges. Form the open-ended louver flaps before completing the panel's edge-flange motion.

Apply the same meridian construction radially to beads, dimples and tray corners. Fix the outer flat's elevation and let the inner region rise or fall. Taper the outer planar radial displacement to zero between local features. This is prescribed geometric accommodation: circumferential distances can change and no material draw-in is solved. The first frame is a geometric preform, not a qualified blank. It also uses midsurface lengths rather than the separately calibrated K-factor developments.

Use unmodified native vertices and triangles at the final state and check the animated endpoint against them. Keep camera and scale fixed. The recorded GIFs use 960 by 720 pixels, 62 encoded frames, a 6.2-second loop, a shared 224-color palette and a 1.4-second final hold. Each title carries nTop blue #248AFF. Every frame contains an explicit statement that no material-forming simulation was run. A small separated stroke schematic indicates motion only and is not fitted tooling.

Decode the actual GIF to check its frame count, timing, infinite loop, changed start/middle/end images and final appearance. Save a static final poster for an HTML play/stop control. Package the five GIFs with plain-text scope notes and optional captions; do not post on the user's behalf unless separately authorized. Keep the generated media out of the shared source repository.


## Translucent tooling update, 15 September 2026

The original part-only animations remain available. Five additional 7.04-second loops add translucent upper and lower tool envelopes with an opaque sheet and a final opening hold. The tools are sampled at 1 mm spacing from the native top and bottom depth views; independent silhouette masks avoid missing values where one view sees a different outline. Nearby sheet heights fill holes for illustration. Nominal vertical display clearance is 0.6 mm. These sampled shells do not establish release, contact, split tooling, piercing tools or press loads. See [the compound method](complex.md) for the shared implementation. The native study-02 geometry is unchanged.
