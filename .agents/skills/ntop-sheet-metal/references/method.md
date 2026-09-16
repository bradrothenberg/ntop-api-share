# Analytic sheet metal method

## Dimensional convention

Thickness is t; inside bend radius is Ri; outside radius is Ro = Ri + t. Theta is the bend rotation from the original flat state, in radians. It is not the included angle between flanges. The geometric midsurface radius is Rm = Ri + t/2.

For a bend with constant K-factor, BA = theta*(Ri + K*t). The outside setback is SB = (Ri + t)*tan(theta/2), and bend deduction is BD = 2*SB - BA. For two outside virtual-sharp leg dimensions A and B, developed length is A+B-BD. For tangent lengths a and b, it is a+b+BA. Do not mix those conventions or subtract BD a second time.

The builder uses 90-degree bends. Theta = pi/2 and SB = Ro. Its `Thickness`, `Inside bend radius`, and `K factor` are separate native inputs. Sheet lengths and profile points are computed inside nTop. All lengths are encoded in metres; angles use the angle dimension and radians.

## Continuous section construction

Specify a midsurface start point and tangent, followed by tangent straight lengths and signed 90-degree turns. At a turn, offset the bend center along the signed normal by Rm. Rotate the radius and tangent by 90 degrees. For each sheet side at offset d = +/-t/2, the turn radius is Rm - sign*d. Build each circular arc from start, midpoint, and endpoint. The midpoint lies on the circle at half the bend angle, not on the chord.

Connect the two offset chains at the sheet ends to obtain one closed wire. `two_point_line`, `three_point_arc`, `profile_from_curves`, and `extrude` build the continuous native section. Use `revolve` for the idealized axisymmetric cup precursor. The report's display mesh must come from native evaluation of these features.

## Four-wall enclosure: 45-degree miter seams (revision 3)

The public Hammond 1444-8 envelope gives L = 152.4, W = 101.6, H = 50.8 mm and t = 1.016 mm. Ri = 1.5 mm, K = 0.42, normal seam gap g = 0.5 mm, relief-root radius r = 0.5 mm, and four 3.2 mm holes are study choices. The commercial source uses spot-welded construction; this study has open seams and omits joining tabs.

Set Ro = Ri+t, A = (L-2Ro)/2, B = (W-2Ro)/2, h = H-Ro and delta = g/sqrt(2). Build a planar floor from -A..A and -B..B. Extrude four exact circular-bend L sections through the outside envelope. Each has a 2t foot overlapping already retained floor stock. For each signed Y flange, keep abs(x) <= A + (sign*y-B) - delta. For each signed X flange, keep abs(y) <= B + (sign*x-A) - delta. These planes bevel the wall ends through the thickness; their normal separation is g. They trim the curved bend region as well as the straight wall.

Cut circular reliefs using (abs(x)-A)^2 + (abs(y)-B)^2 < r^2. Apply this cut to the planar floor and each flange before union. The circle at each tangent corner opens into the diagonal seam. Drill the same four holes 10 mm inward from both floor tangent datums. The floor-to-wall Ri and the cutout root radius r are separate parameters.

This is a true mitered sheet-edge detail, not merely a diagonal outline with perpendicular cut faces. A fabricator needs bevel cutting or other edge preparation to reproduce the modeled fit. Do not imply that an ordinary 2D laser-cut outline automatically produces these edge faces.

### Developed solid from the same formed fields

For a Y flange, let s = sign*y_flat-B, Rn = Ri+K*t, BA = pi*Rn/2, theta = clamp(s/BA,0,1)*pi/2, and rho = Ro-z_flat. Evaluate that flange's formed scalar field at:

```
x_formed = x_flat
y_formed = sign * (B + rho*sin(theta) + min(s,0))
z_formed = Ro - rho*cos(theta) + max(s-BA,0)
```

Clip the result to 0 <= z_flat <= t. Swap X/Y and A/B for the X flanges. Union these four mapped flanges with the relieved floor and drill the holes. The native `remap<real_field,real_field,real_field,real_field>` block evaluates these coordinate fields. Use angle-dimensioned radians for sine and cosine. This maps the same physical trim boundaries, including the bevels and the cut across the bend; it is not a separately drawn flat approximation.

For this construction, require positive tangent lengths, a floor large enough for the 2t feet, and 0 < g/sqrt(2) < r < Ri. Keep Rn positive. When Rn < Ro, the most outward developed bend edge occurs at theta_c = acos(Rn/Ro). Require g > sqrt(2)*(Ro*sin(theta_c)-Rn*theta_c) to avoid developed-flange overlap. The current minimum is 0.384877 mm; the chosen 0.5 mm gap clears it. These are model-domain checks, not native manufacturing constraints or validated allowances for a particular cutting process.

Nominal BA = 3.026484699 mm, BD = 2.005515301 mm and blank extents = 249.988969398 x 199.188969398 mm. The developed object is a three-dimensional blank with beveled edges, not just an extruded flat outline. K is an illustrative development parameter requiring material/tooling calibration.

### Earlier corner option

`--corner-style rounded` reproduces revision 2: a base U section plus narrower end L sections, 1.5 mm corner setbacks and 1.5 mm wide relief slots with R0.75 roots. Those cutters lie in the common planar floor and are directly reusable in both configurations. The default `--corner-style miter45` is revision 3. Keep earlier native models and figures in the development archive for comparison.

## Verification lessons from development

- A successful CLI recipe conversion or API import did not force every lazy block to evaluate. `get_block_input` returned None on unevaluated field-check variables. Keep this distinct from a failure and force a native output evaluation.
- Live schema inspection showed the third scalar input of Extrude is Draft Angle. Use an angle-dimensioned zero. The first draft accidentally gave this zero a length dimension; that attempt is not the accepted model.
- Revision 3 passes 79 formed-body probes: floor, holes, true bend surfaces, diagonal seam centers/faces/material at multiple bend angles, and relief roots at all four corners. The other four examples retain 3 nominal probes each.
- A changed envelope of 172.4 x 111.6 x 40 mm passes 30 native probes, including moved seam faces, fixed gap, radius, thickness and hole diameter. A separate developed-solid closure passes 162 probes including miter edges at two depths through the sheet, matching folded coordinates, holes, roots, extents and separation. Together with the other four examples, 283 native probes pass. The first 162-probe evaluation exceeded its 180-second CLI limit; the owned process was terminated and a fresh evaluation completed in 204 seconds with a longer bound. Keep that timeout receipt as historical evidence.
- In the positive-overlap region the compound implicit field returned a magnitude greater than half the sheet thickness. Its sign was useful; the value was not a global physical thickness measurement.
- In the mesh-export recipe, a file path literal requires `{"type":"file_path","value":{"val":"..."}}`. A bare string value was rejected during native recipe loading.
- Multiple processes can appear to listen on port 2323. Verify the selected process executable and creation time and confirm the PID on the exact connected socket before sending edits. This guard detects a wrong destination; it does not route a client to an arbitrary process. Prefer distinct server ports if the build supports their configuration.

## Native mesh and presentation evidence

The exports use `mesh_by_adaptive_tets<implicit,real_field,bool>[5.42.0]` at 0.10 mm tolerance with remeshing enabled, followed by `export_mesh` in millimetres. Inspect each revised export for connected components, winding, closed surfaces, bounds, and analytic volume agreement. All five formed exports and the revision 3 developed enclosure are watertight, consistently wound and single-component. Revision 3 analytic volumes are 40,594.525110 mm3 formed and 40,529.602926 mm3 developed. The native mesh volumes are 40,578.644670 and 40,523.301875 mm3, differences of -0.039% and -0.016%. Independent annular-strip integration includes the miter planes, circular root clipping, holes and the floor counted once. Keep actual mesh measurements in the development evidence and refresh them after geometry changes.

The native model provides the geometric midsurface, while the developed blank uses K = 0.42. The revision 3 analytic formed/flat volume difference is 64.922184 mm3 (0.160%). This is a modeling limitation to disclose, not a mesher correction to hide.

Host simplification must be checked independently. A `decimate_pro` trial generated open edges even with its topology-preservation setting enabled. The accepted report instead retains every native triangle, indexes the vertices, and gzip-compresses the payload without changing connectivity. Its figures render the full native exports on the host; they are not native viewport screenshots.

Saved-file presentation helpers must recognize the actual file container. These API saves had a variable-length header/chunk table, so a fixed first-chunk offset from older helper code was unsuitable. The local finalizer located the first chunk marker, proved a byte-identical read/write roundtrip, organized and collapsed only presentation state, then checked the native graph unchanged. Keep the API working save and the presentation copy separate. Do not interpret an unexplained header byte as a format version.

## Stamping extension

Simple bends preserve developable regions separated by bend zones. A deep-drawn cup introduces material draw-in and circumferential strain. A constant-thickness revolved cup can be an editable target shape and tooling reference, but it does not determine the actual blank or predict thinning, earing, wrinkling, or springback. Use the cited AA5754-O cup experiment as a future validation case, retaining the distinction between punch geometry, deformed sheet geometry, and material/process response.

## Report colors

Follow the adjacent [engineering HTML skill](../../engineering-html/SKILL.md)
for current nTop blue tokens: #16489D for light-surface highlights and #248AFF
on dark surfaces. The recorded first reports and animations used website blue
#248AFF, with #165399 and #7CB9FF for light/dark link contrast. Those are historical
rendering choices; use the shared report skill for new HTML output.
