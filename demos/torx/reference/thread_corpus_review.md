# Complete-screw thread corpus review

2026-09-15. READ/CANDIDATE only; no ntopcl calls or new geometry measurements.

## Result

No ready-made exact metric thread generator was identified. The native master pair has no signature named thread, screw, helix or spiral; `ntop_find` returned zero for all four queries. This is not proof that the capability is unavailable. An existing parametric Bolt is explicitly unthreaded. A community Spiral Curve is sampled and spline-fitted, so it cannot silently serve as an exact thread path.

## Searches and complete definitions read

Both master surfaces were searched, followed by doc_exports, knowledge identities/community, MCP find, then Utilities-community. Relevant documentation examples include `spring_bolt.json` (an FE spring between bolted blocks, not screw threads) and the complete cylinder-head modelling example (arcs, profiles, extrusion and revolution).

Read the whole `projects/acc_flange/recipes/Bolt.js` builder and identified `cb_Bolt.json`; inspected the whole native graph and input definitions of the two community notebooks below through the seek-based binary reader. Online fallback searches for thread/screw/helix on nTop support/docs produced no relevant nTop implementation. No unrelated search result is used as a technical authority.

### Bolt

`user_func_bff7294c_e97e_4e75_9535_b4cf47e293a9`

Source: `projects/acc_flange/recipes/cb_Bolt.json`, builder beside it.

Inputs: `d_shank`, `L_shank`, `s_af`, `h_head`, `x_offset`, all real length scalars. Grammar: three rotated box slabs intersect sharply to make a hexagonal head; one plain cylinder makes the shank; sharp union at seating plane z=0. Head extends above seating plane, shank below. This is useful as a convention and test exemplar but cannot supply a Torx head or a thread. Do not present it as a threaded fastener.

### Spiral Curve

`user_func_eed98dd8_8fc2_48db_819a_d02b61788588<point,vector,real,real,real>`

Source: `Utilities-community/packages/ntop/spiral-curve/spiral-curve.ntop`.

Ports: Starting Point (point), Direction (vector), Height (real), Radius (real, required length), Number of Rotations (real, recorded required units angle^-1). Output curve_interface. No custom dependencies.

Complete grammar: translate the start point by Height*Direction to create an axial line; choose a perpendicular unit vector and offset by Radius; create equally spaced axial positions; rotate those positions through a sequence from zero to Number of Rotations*360 deg; pass the resulting points to `spline_through_points<list<point>,integer,bool,vector,vector>[5.28.0]`. Point count is rounded from line length divided by an increment proportional to Radius. Original points and a centre cylinder are display branches. The output is the fitted spline.

Limits: sampled approximation, not an analytic helix. Axial length depends on Direction magnitude in the initial line while subsequent placement uses its unit vector. The unusual angle^-1 units of Number of Rotations require an explicit probe before reuse. No exposed fit tolerance or sample count. Useful as a visual/grammar exemplar; not an exact thread primitive.

### Non Linear Twist to Implicit

`user_func_44971658_d1ab_44df_83dd_9505750fcbc6<implicit,real_field>`

Source: `Utilities-community/packages/DaveMakesStuff/non-linear-twist-to-implicit/non-linear-twist-to-implicit.ntop`.

Ports: Implicit; Rotation Field, required angle dimension. Output implicit. No custom dependencies.

Complete grammar: x'=x*cos(a)-y*sin(a), y'=x*sin(a)+y*cos(a); remap the input field at (x',y',z); reset bounds from the larger source x/y bounding-box span, symmetrically around global Z, retaining source z bounds. Rotation depends on the supplied field. The description calls the field degrees, but recipes still use SI radians with angle dimension.

Limits: this only twists a supplied body; it provides no standard thread profile, root rounding, crest truncation, pitch selection or lead-in. It twists around global Z, not an input frame. Its bounds assume geometry near that axis. Reuse unchanged by UUID only if the desired construction actually needs this transformation. Twisting alone does not make a metric screw thread.

## Native candidates and brief findings

| Signature | Ports / result | Evidence or caution |
|---|---|---|
| `atan2<real_field,real_field>` | y, x → angular field | Existing measured note: length-coordinate inputs return angle units. |
| `mod<real_field,real_field>` | operand a, operand b → field | Master present; negative-argument convention must be measured before axial phase wrapping. |
| `remap<real_field,vector_field>[5.43.0]` | source field, coordinate vector field | Present in master; use a constant-size graph to place a periodic axial profile in cylindrical phase. |
| `revolve<new_profile,axis,real>[5.20.0]` | profile, axis, angle → implicit | Existing measurement: accepts an axial profile with an edge on the axis; field reads zero on the axis itself, so validation samples must avoid that singular line. |
| `cylinder<point,point,real>` | end points, radius → cylinder | Shank or cylindrical-head primitive. |
| `rounded_cylinder<point,point,real,real>[5.26.0]` | end points, radius, rounding radius → implicit | Appropriate only if the official head really has the corresponding circular edge round. |

A prospective analytic thread uses an authoritative axial profile evaluated at radius and periodic helical phase. This is a CANDIDATE construction, not a measured recipe. The angular branch cut and negative modulo seam need predicted point samples. A helical zero set can be exact while its field values are not Euclidean signed distance; do not compare them as distances without deriving the field law.

## Head and acceptance strategy

A complete Torx screw needs an independently sourced head outline plus recess dimensions. For an axisymmetric head, revolve one closed axial profile, preserving the documented fillets/chamfers, then subtract the Torx recess. This follows existing curve/profile/revolve grammar and avoids approximating a specified profile with generic blends.

Before building, settle thread standard, pitch/diameter pairing, actual external-thread profile including root, thread tolerance class, threaded length, lead-in/runout, head type and recess depth. Do not infer these from the Torx drive size.

Validation should predict crest/root/flank locations from the chosen standard, check phase at several azimuths and several turns, test both sides of the atan2 cut and modulo boundary, and test thread length/lead-in and seating convention separately. Then test translated and rotated placements. Independent analytic on-surface samples between spline stations would detect a fitted-helix error if that route were selected. Existing volume-integrator floors and padded bounds cannot certify thread form.

No new standards dimensions, thread fit or aerospace compliance are established by this review.
