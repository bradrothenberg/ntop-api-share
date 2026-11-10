# Native nTop implementation

Use the available ntop-notebook-api skill for the live API mechanics, or the
installed build's API documentation. Discover the runtime and exact task document. Do not
copy process IDs, console ports, or local paths from an earlier session.

## Graph layout

Build named variables for shared quantities before fan-out:

1. Controls: p, positive L, two base widths, aft taper endpoints, anchor span.
2. Source fields: x/y/z coordinates, F, W, and the crown/keel coordinate fields.
3. Candidate fields: U_small and U_large, anchor residuals, C_small and C_large.
4. HM: normalized candidate fields, spatial log weights, stabilized sums.
5. Results: length-valued H converted to a bounded implicit result.
6. Verification: field evaluations at known points and near the exposed root.

Preserve the actual source geometry. For the worked example, plane scalar fields
supply coordinates and the analytic source equations are recomputed at the
anchor coordinates. Do not substitute a constant anchor evaluation for a field.

Useful identifiers measured on the 6.1.0 prototype build 42926 are listed below.
Look them up on the current build before authoring. Input labels and display
units also need current-build verification.

| Operation | Measured identifier |
|---|---|
| Add/subtract/multiply/divide fields | add/subtract/multiply/divide<real_field,real_field> |
| Pairwise min/max fields | min/max<real_field,real_field> |
| Scalar-field absolute value, square root, exponential, natural log | abs/sqrt/exp/log<real_field> |
| p=0 test | equals<real,real> |
| Conditional | core.if<bool,any,1> |
| Coordinate plane | plane_from_normal<point,vector>[1.1.0] |
| Point evaluation | evaluate_field<real_field,point> |
| Bounding box | create_bounding_box<point,point> |
| Set implicit bounds | set_bounding_box<implicit,bounding_box> |

Slash-separated names above describe families, not literal combined identifiers.
The plane's "scalar field" property was used for coordinates. Field-to-implicit
conversion was accepted by set_bounding_box on the measured build. Recheck this
conversion on another build.

Use multiplication for integer powers of dimensional values. Normalize before
exp/log. A recipe length literal uses SI metres and explicit length units.
For example, 10 mm is value 0.01 with units {"length":1}. Read values back; do not
assume a fresh notebook uses millimetres for setters.

## Branch-safe evaluation

For the compact union, avoid division by zero even if k=0:

~~~text
normalized_k = k/L
safe_k = max(normalized_k, epsilon)
h = max(1 - abs(F/L-W/L)/safe_k, 0)
correction = normalized_k*h^3*(4-h)/16
~~~

The numerator uses the true normalized_k. Thus the correction is zero at k=0.
The worked example used epsilon=1e-12. This changes the positive-width formula
below that floor; treat it as a numerical guard, not a design parameter. Verify
that it is negligible over the supported dimensions.

For HM, protect both branches:

~~~text
is_zero = (p == 0)
safe_p = if(is_zero, 1, p)
N = shifted_LSE(safe_p*(f_i+w_i))
D = shifted_LSE(safe_p*w_i)
H_normalized = if(is_zero, mean(f_i), (N-D)/safe_p)
H = L*H_normalized
~~~

This was the native construction used for the frozen samples at p=-4.
It avoids exponential overflow but can lose accuracy near p=0 through subtraction.
The portable reference handles that regime more carefully. If continuous sweeps
through very small p are required, verify a cancellation-safe native implementation
against that reference. Do not describe the unmodified graph as tested there.

## Author and verify

Prefer current supported API operations. A full dependency-closed recipe import
is an option when the graph is large or a required literal cannot be set live.
Recipe references cannot be assumed to resolve into a previous import. Re-imports
can duplicate variables and overwrite notebook metadata.

Check wire metadata and build completion, not just absence of exceptions.
Read named evaluate-field results at interior, exterior, crown, keel, root,
outboard, and runout locations. Export a recipe when required to inspect
otherwise unreadable wiring; audit references, input slots, and actual units.
The worked comparison's 270 samples are dimensionless fields divided by L=10 mm.

The helper scripts do not author nTop geometry. They provide independent scalar
reference values and a reproducible example for checking the native graph.
They have no nTop, NumPy, or workstation-path dependency.

Finish in a new saved notebook. Use native geometry captures to inspect the
result. Match camera, visible result, and rendering detail for comparisons.
Organize sections and collapse the authored tree after the final geometry save.
Use a verified container round trip if file-level presentation edits are needed;
confirm geometry payloads stay unchanged.
