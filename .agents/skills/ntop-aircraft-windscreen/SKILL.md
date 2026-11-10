---
name: ntop-aircraft-windscreen
description: Reconstruct planar aircraft windscreens in editable nTop implicit fuselages. Measure CAD pane planes and trimmed boundaries, form locally bounded fuselage transitions, expose pane and frame controls, and verify flatness and surrounding fairness. Use for windscreen-to-loft transitions, not aircraft certification or generic CAD import.
---

# Aircraft windscreens in nTop

Use this skill when a flat pane must meet a smooth fuselage. Keep the pane plane, its aperture, the frame, and the surrounding transition as separate design elements.

Use the repository Notebook API skill for native recipes, units, owned processes, and saved-file presentation. Read [the measured DC-10 case](references/dc10.md) before reusing its scripts or numerical findings. The case uses new native CLI conversion and scalar probes. It does not establish live Notebook API execution.

## Establish the source geometry

- Resolve the representation's effective units. A millimetre declaration can be the basis of an inch conversion. Measure imported geometry after the conversion.
- Inventory solids, open shells, duplicates, and symmetry. An open exterior cannot supply a valid solid-volume overlap metric without further work.
- Read the actual trimmed wire. A B-spline's rectangular parameter domain can include regions outside the face.
- Test a candidate plane using its control poles when available. For a non-rational B-spline, a control-pole plane bound also bounds the surface's plane deviation. Check rational weights before extending that argument.
- Do not call a nearby curved fairing a flat window. Record whether each pane is measured, fitted to a curved patch, or authored from design intent.
- Preserve the source hash, coordinate frame, face or shell identity, and edge-sampling settings.

## Build the parent loft

Fit smooth section guides before adding pane detail. Keep nominal dimensions and source coordinates separate from scale controls.

Use actual trimmed section intersections when available. Arbitrary vertex bands can bias section fits and introduce waviness. Check the conditioning of ellipse fits near narrow or incomplete tips. Preserve silhouette extrema or use bounded section corrections when an ellipse fit becomes unstable.

Compare native guide values with the host fit at several positions. A successful recipe import does not prove matching spline parameterization, sign, or units.

`curve_axis_distance` returns a length field. If its ordinate encodes a dimensionless correction, divide by the chosen ordinate length unit before using it. A host numeric evaluator cannot establish native unit compatibility. Native CLI conversion can save a notebook that still contains an unbuilt output; require native evaluation or rendering as well.

## Form a flat seat with a local transition

Let `F` be the parent implicit field and `d` the signed pane-plane distance. Use an orthonormal pane frame to define projected coordinates `u, v`. Express the trimmed aperture with a planar profile or bounded half-spaces.

A useful candidate construction is:

```text
F_seat = (1 - w) F + w d
w = footprint_weight * normal_band_weight * pane_partition_weight
```

Set `w = 1` throughout the protected pane and frame seat. Set `w = 0` outside a finite transition region. A clamped quintic smoothstep has zero first and second derivatives at its endpoints.

Important limits:

- A projected polygon defines an infinite prism. A footprint mask alone can create remote sheets or solid extensions along the pane normal. Bound the mask in the normal direction. Test the opposite fuselage surface and distant points explicitly.
- Set the full-strength normal band from measured parent-to-pane differences. Keep its taper away from the intended seat. The DC-10 band's dimensions are local pilot choices, not universal settings.
- Prevent a later pane operation from changing an earlier pane's protected interior. Partition mirrored panes at their centerline or use explicit exclusion masks. Test adjacent panes after the complete sequence.
- A quintic weight does not prove that the complete surface is C2. Polygon distance ridges, parent-field defects, vanishing gradients, and intersecting supports can reduce continuity. Check edges and corners separately.
- Field magnitudes affect a weighted blend. A parent field need not be a signed-distance field. Keep the parent field definition fixed while comparing transition widths.
- Transition width is a support parameter. It is not a physical rolling-ball fillet radius.

Choose a different local construction if a weight blend folds or produces an unacceptable shoulder. Tangent contact with a planar seat requires a nonzero surface gradient and a transition with the intended limiting normal.

## Glazing and frames

Make a pane from its plane slab intersected with its aperture prism. Define frame width independently from pane thickness and transition width.

Remove the complete pane-and-frame footprint from the fuselage before inserting separate visible parts. Coplanar overlapping body and frame faces can produce display interference. Keep the outer glass face flush with the intended seat unless a recess is requested.

Normalize a modified plane normal. Expose the plane location and orientation through named inputs. Define whether an angle or slope control rotates the pane frame or only changes its plane within a fixed projected aperture. Test the resulting edge positions.

Surface-only CAD does not establish glass thickness, frame strength, or manufacturing details. Label authored defaults accordingly.

## Verify the geometry

### Preserve the complete cockpit, not only its front plane

The DC-10 R4 rejection exposed a missing validation step. Its front pane matched the source plane, but its side patches were absent. The parent ellipse and broad blend changed the surrounding roof and skin. Compare each source patch separately before accepting a cockpit.

Classify each trimmed source patch from its measured geometry. Do not flatten a curved side window because the front windscreen is planar. Keep the source outer boundaries fixed and inset the frame. Preserve concave outlines with a union of polygon pieces, rather than a convex hull.

For a radial fuselage field, evaluate a pane's boundary at its radial intersection with the pane plane. An orthogonal footprint can affect a neighboring lower panel. Bound the transition in the plane-normal direction as well. Inspect the resulting seam; a source open seam does not establish a smooth fillet.

An entirely implicit reconstruction can fit a radius field in longitudinal and angular coordinates. A tensor spline permits local corrections without importing the source CAD or mesh. A local polynomial patch can preserve a sharp adjacent panel when the global spline rounds its edge. Check gradients and source residuals after every mask and blend.

The DC-10 R16 cockpit has host measurements against independently sampled trimmed CAD surfaces and 30 matching native field probes. Full-aircraft delivery validation is separate. Do not cite host distance estimates as a global native-model certification.

Native authoring performance needs its own pilot. Verify literal scalar tables, interpolation modes, dimensions, and field results before expanding a tensor representation. Retain unsuccessful conversions and distinguish cancelled execution from a completed build.

The R16 pilot uses a single numeric map for cardinal tensor coefficients. `map_from_lists<list<real>,list<real>,interpolation_enum>` produces `map_1_1`; `evaluate_map<map_1_1,real_field>` selects a coefficient at an integer index. Native floor and cubic weights combine the sixteen active tensor coefficients. Build 43139 verified this route. A four-sample pilot differed from the host by at most 1.22e-8 m. Large field-valued transfer tables were much slower and were cancelled.

Use native concave profiles for trim masks when available. In build 43139, `profile_from_points<list<point>>[5.20.0]` and `extrude<new_profile,real,real,bool,vector>[5.20.0]` preserved the measured polygon. Read the prism's `scalar field` property, then remap it into the surface chart. This replaced many triangle halfspaces. The 30-probe cockpit conversion fell from 242 seconds to 42 seconds. These are measured run times for this model, not general performance guarantees.

Treat conversion from Chebyshev coefficients to power-basis Horner form as a performance tradeoff, not a default. Compare both bases at float64 and float32 precision over the fitted surface and the full active support. Large power coefficients can cancel and shift the surface. Prefer a stable basis or a verified local cubic coefficient table when the transformed expression loses precision. Native CPU agreement does not certify GPU evaluation.

Saved native rendering can fall back to voxels. R16 used Aether for four objects and voxel fallback for seven. State this in image captions. A smooth-looking image is not a distance measurement, and visible voxel seams are not automatically geometric seams.

Run a small nose pilot before the aircraft. Retain failed pilots and their cause.

1. Check source-plane residuals and trimmed boundary agreement.
2. Sample the full pane interior after all neighboring operations. Evaluate the final implicit field at the intended plane.
3. Probe the centerline, aperture edges, blend boundary, opposite skin, and the normal-band limits. Look for extra zero crossings and sign reversals.
4. Inspect silhouettes and surface normals across the surrounding transition. Check corners independently of edge midpoints.
5. Change pane offset, orientation, frame width, and blend width independently. Check flatness, valid frames, and finite support again.
6. Compare against the source with region-specific metrics. A low whole-aircraft error can hide a bad windscreen.

Finite gradient-projection distances are not certified nearest distances or Hausdorff bounds. Report failed projections. A one-way source comparison cannot detect every extra modeled surface. Use reverse checks or native mesh inspection where that distinction matters.

Native scalar agreement, native rendering, source comparison, and mesh topology establish different facts. Bind every result to the corresponding recipe and model hashes. Revalidate changed geometry.

## Deliver and retain evidence

### A local panel can expose a hidden parent mismatch

The DC-10 R16 lower panel exposed a real crease, not just a rendering artifact.
Its fitted angular chart ended at 1.12, but the lower panel reached 1.43149.
The parent had already faded to an ellipse across angular coordinates 0.85 to 1.05.
The separate panel differed from that parent by up to 18.2824 mm at sampled boundary points.
A narrow blend hid neither the position mismatch nor the rapid normal change.
The earlier CAD comparison used z above 0.35 m and missed the marked lower perimeter.

Extend the shared parent fit across the complete local support before adding corrections.
The R19 trial extended the chart to 1.792 and faded between 1.50 and 1.75.
It removed the original crease but left a broader ridge at the new underside transition.
Native inspection rejected that trial. Moving a short transition only moves its shape defect.
The accepted R20 chart extends to 2.80 and fades between 1.50 and 2.70.
One shared native tensor field spans the marked boundary and the wider underside transition.
An upper-sill correction remains near the windscreen, with a quintic fade from z=0.40 to 0.65 m.
It has zero weight below z=0.40 m. These are measured model choices, not universal dimensions.

Check every support perimeter, including regions excluded from the main source comparison.
Evaluate normals on both sides with successively smaller chart spacing.
For 21 R20 lower-boundary locations, maximum normal change at chart half-spacing 0.0001 fell from 29.134 to 0.010085 degrees.
At half-spacing 0.00001 it fell to 0.001009 degrees. Chart spacing is not uniform physical surface distance.
Sixty-three native cockpit and boundary probes agreed with the host within 4.230e-8 m.
The same 3,000 trimmed-CAD samples had a maximum projection distance of 0.634 mm.
These finite checks establish local sampled behavior, not global C2 continuity.
Retain the rejected geometry and its sample set. Do not label an unexplained crease as voxel noise.

Keep the source reference, fitted parameters, builder, native model, and validation evidence together. Save a separate collapsed deliverable and prove that presentation changes preserve the computation graph. Inspect a native render. Keep display sampling artifacts distinct from measured surface defects.

Document unresolved regions and the tested input range. A successful parameter edit is not evidence that all possible edits remain valid.


## Upper-roof fairness after a close source fit

A small surface-distance residual does not establish surface fairness. The R20 roof fit retained visible curvature oscillations above and behind the glazing. Its lower-skin checks did not cover this region.

Use independent longitudinal and angular sections over the complete new support. Compare curvature variation as well as position and normals. Include every transition endpoint and protect the glazing with an explicit zero-weight region.

The R21 candidate uses a low-order even Chebyshev roof radius fitted to trimmed source roof samples. A quintic support starts above the source glazing. Evaluate the polynomial in its stable basis. The first power-basis trial produced native display defects outside its fitted domain and was rejected.

Do not hard-clamp a field correction where the surface can cross the clamp limit. An R21 trial introduced curvature peaks at that limit. A smooth saturation limits off-domain corrections without a derivative jump. Test the complete resulting field, not the correction alone.

On four sampled upper-roof sections, the accepted candidate reduces curvature total variation from 2.83-6.26 per metre to 0.053-0.261 per metre. Its 138 native field probes agree within 6.45e-10 m. The focused source comparison has a 3.363 mm maximum roof projection distance. These checks apply to the recorded candidate and sample domain, not global continuity or exact STEP identity.

The source-fit and fairness objectives can conflict. Report the change in source deviation when removing small oscillations. Preserve the original planar pane and side-window controls, and recheck them after the roof correction.


## Bound fitted corrections in every active coordinate

A good fit inside its sample region can create extra zero surfaces outside it. An axial fade alone does not bound a transverse polynomial. Define the fit domain separately from the correction support. Keep the support inside the region where the fit is valid. Check all directions in which the field can extrapolate.

For a tip correction, one possible support uses normalized transverse radius squared and an independent axial fade. Use a smooth transition to zero before leaving the valid domain. Its dimensions and fade fractions are model choices, not reusable aircraft constants. Check the complete blended field for folds and extra crossings. Ensure inactive expressions stay finite; multiplying an overflow or NaN by zero does not make it safe.

Preserve accepted regions explicitly. Compare the old and new fields on the eyebrow, adjacent panes, and every support perimeter. Distinguish zero change at sampled source points from zero change throughout a volume.

When a preview exposes an extra sheet, isolate corrections with controlled before-and-after recipes. Keep the camera and evaluator fixed. Test the suspected correction alone, then the complete final body. Do not dismiss a defect as rendering noise until the evidence separates those causes.

Add regression samples where the defect actually appeared. Source-to-model samples can miss extra modeled surfaces entirely. Compare native signs before and after at identical exterior points, plus a surrounding volume grid or reverse surface check. Native sign agreement, field-magnitude agreement, and distance agreement are separate claims. Record failed magnitude checks even if signs pass. See the [R24 case](references/dc10.md#r24-lower-surround-and-bounded-tip) for the demonstrated failure and its limits.

## Render thin glazing without changing accepted geometry

For a render-only request, preserve the recipe and notebook. First distinguish pixel aliasing from coarse implicit sampling and thin-part under-resolution. More output pixels cannot repair missing surfaces in a coarse volume grid.

Prefer native rendering when available. If it times out, keep that outcome explicit. A host preview must remain labeled as such, with its source revision and representation limits. Do not present it as successful native visual verification.

For an exterior-only host preview, sample the shared exterior field, refine near the windows, and project vertices back to that same field. Split pane colors at the recipe trim contours, including the actual frame inset. Avoid coloring whole triangles using a broad distance band. Render above the report resolution, then downsample with antialiasing. This can show a clean exterior without resolving thin glass volumes; it does not verify glass thickness, frame interiors, or assembly topology.

Keep camera and scale fixed for STEP comparisons. Inspect the completed image before replacing report figures. Preserve failure evidence separately. A better preview does not repair geometry, and a corrected field does not establish a successful full-aircraft delivery. Verify the final saved artifact separately from a cockpit pilot.
