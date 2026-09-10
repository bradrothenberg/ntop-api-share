# Fury: native lofting lessons

Sources: builder,
inlet,
root blends,
and historical RC record.

## Surfaces from section fields

Longitudinal spline guides define half-width, crown, chine, and underside depth.
The builder fits cubic B-splines with fixed endpoints and records residuals.
A guide residual measures sampled guide agreement, not the complete aircraft surface.

Spline control points feed curve_axis_distance fields along the longitudinal axis.
conic_implicit defines a section in vector-field coordinates.
Guide fields vary the conic's defining points along the aircraft.
Implicit-spline fields provide extra section freedom.

The forebody underside uses one signed-span conic.
At one station, A=(-w,0), B=(0,-2d), C=(w,0), and rho=0.5.
This avoids a flat center with steep shoulder joins. Longitudinal guides still control width, depth, and chine.

The native Fury build uses its own recipe graph.
The earlier Fury_Editable model instead imports meshes. Keep that distinction explicit.

## Signs and field meaning

Use signed Y for one continuous bilateral arc. Absolute Y changes the seam mapping.
Expose guide lists and section controls. Keep dimensionless factors separate from lengths.
Apply the RC scale at an explicit boundary.

A positive field multiplier preserves the zero surface and material sign.
It does not create a certified distance field.
Blends can depend on field magnitude, so rescaling before blending can change local geometry.

## Inlet, splitter, and cavity

Build roof, cheeks, and lip as one shell.
A separate overlapping lip can leave a step or close the opening.
The current gap splitter is the pointed feature between fuselage underside and inlet roof.
Older records used splitter for the upper lip. Current controls distinguish the two.

Separate intentional splitter material from left/right passage checks.
Centerline probes cannot establish an open lateral gap. Sample across the span and near cheek returns.
Subtract the cavity after additive geometry. A wing or root blend must not seal it again.

Restrict local trims to their intended region. Global cutters can intersect distant bends.
Finite field probes establish sampled material state. They do not establish continuous clearance or flow.

## Root blends and Ramp

Wing, horizontal tail, and fin roots use local C2 polynomial field blends.
Compact supports preserve surfaces away from the roots.
A smoothing control is a field parameter, not a measured fillet radius.

The native Ramp arguments are:
Scalar Field, In Min, In Max, Out Min, Out Max, Continuity.
Measured enum 2 selects the C2 clamped quintic form.
Its longitudinal coordinate follows the live wing offset.

Wing root blend size controls the leading value. Wing TE root blend size controls the trailing value.
The source selects 1/8 inch at the nominal RC span for the trailing control.
The small Ramp fixture isolates its endpoint checks.
Verify both endpoints and support boundaries before testing the aircraft.

## Photos and evidence

Use actual native captures with a camera fitted to visible landmarks.
Hold that camera between variants and preserve image hashes.
Exclude occluded landmarks. A photograph is not a production section drawing.
Do not report a percentage likeness without a defined metric and calibrated reference.

The source retains a failed fixed-offset cavity diagnostic.
Later tests locate native section boundaries before placing interior probes.
Keep both records. A changed sampling method must not erase a failure.

Before reusing evidence, compare the full dependency closure: functions, types, units, inputs, and properties.
Exact unchanged dependencies support reuse only for that scope.
Changes still need current final-assembly, transform, layout, and visual checks.

## B52 and DDGX: continuity and fair shape

A continuous loft can still have unwanted changes in curvature. B52's R7 cap correction removed
two underside curvature reversals while retaining the accepted cockpit and rounded tip.
Compare the same meridian, camera, and fit domain before and after a change.
See [B52's recorded lessons](../demos/b52/LEARNINGS.md) and its complete editable recipe.

DDGX uses shared lower hull and bulb rails, then introduces the blend over a limited longitudinal region.
Measure the contour of the combined native field. A smooth input rail alone does not establish a fair final union.
Finite contour samples are evidence at those samples. Inferred shape controls do not establish real ship dimensions.
See [DDGX's recorded lessons](../demos/ddgx/LEARNINGS.md).

## Finite edges and later aircraft studies

Fury and F-16 retain finite trailing-edge controls. Define full physical thickness, then convert to each surface's half-thickness contribution and guide scale. Inspect the native sections and exported mesh separately. Smooth display shading does not prove topology.

F-16 R6 uses sparse cubic guides to reduce aft-fuselage oscillation. A-12 uses independent upper and lower section surfaces and separates cockpit crown shape from pane borders. F-Cat uses one continuous bent tail loft and local pod-fairing controls. Each method retains its own recorded validation limits.

Read [F-16 lessons](../demos/f16/LEARNINGS.md), [A-12 lessons](../demos/a12/LEARNINGS.md), and [F-Cat lessons](../demos/fcat/LEARNINGS.md). The [B52 historical source](../demos/b52/history-source/README.md) preserves R2-R6 graphs alongside the current R7 builder.
