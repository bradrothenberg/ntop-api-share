---
name: ntop-surfacing
description: Build smooth lofted surfaces in nTop from Spline DF sections whose control points are fair guide fields, joined by compact C2 blends, and check them with zebra stripes and section curvature. Use for vehicle bodies, fairings, canopies, hulls, ducts and other free-form skins that must reflect cleanly, and to repair wobbles, ripples, dimples or pinched seams in an implicit loft.
---

# Surfacing and lofting in nTop

Build a free-form skin as a few simple primary surfaces. Each one is a planar section
field whose control points are fair functions of the loft coordinate. Join the surfaces
with compact C2 blends of a chosen width, and cut every detail from the resulting envelope.

A surface that matches every measured point can still reflect badly. Agreement with the
reference and fairness are separate results. Report both, and decide with the user which
one gives way when they conflict.

Use the installed `ntop-notebook-api` skill for console access, block discovery, wiring,
units and build states. For a shell fitted to a photograph, with silhouette scoring and
wheel openings, also read `ntop-class-a-car-body`. This skill adds the surfacing method,
its checks, and bundled reference code:

| Script | Purpose |
|---|---|
| `scripts/surfacing.py` | Host evaluator for Spline DF sections, guide fitting, compact blends, layers, region masks, and a recipe writer for the same graph |
| `scripts/loft_pilot.py` | Four pilot bodies that prove section sign, end rays, closed curves and blends on the host and in nTop |
| `scripts/example_body.py` | A small body built from primary surfaces, in a fair and a traced variant |
| `scripts/zebra.py` | Zebra (isophote) images of a mesh |
| `scripts/section_curvature.py` | Curvature against arc length on plane sections of a mesh or a field |

The scripts need numpy and scipy. Meshing and contours also need scikit-image, zebra
images need pyvista, plots need matplotlib.

## Establish the surface contract

Read the task's files and conversation before asking. Record:

- Frame, units, symmetry plane, and the sign of every field. This skill uses metres,
  dimensionless field values, and negative inside.
- Reference data with its scale and trust: dimensioned drawings, traced outlines,
  photographs, or a reference mesh. Calibrate each view separately. In the recorded
  case the views of one drawing disagreed in scale by one to three percent.
- Which lines are real features of the design (a crease, a belt line, a lip, a pillar)
  and which regions must only be smooth.
- Fidelity tolerance for stations and silhouettes, and the fairness evidence required.
- What is unknown. A side view does not define a plan curve.

## Prove the section semantics first

Read [Spline DF sections](references/spline-df-sections.md) before the first section.

The native Spline DF block (`spline_implicit`) returns the signed planar distance to a
clamped uniform cubic B-spline. Recorded on build 42926:

- The value is positive on the left of the direction of travel. A curve that keeps the
  body on its right is negative inside.
- An open curve continues as straight rays along its end tangents.
- The curve is closed when its first and last control points coincide.
- Control points are 2D vector fields. Control points that vary with the third
  coordinate turn the section into a loft.
- The value is a distance in the section plane, not a 3D distance to the loft.

Run `python scripts/loft_pilot.py host`, then build the pilot natively (`recipe` or
`native` mode) and compare. Do this again for each new build of nTop, and before using
Conic DF, a degree other than three, or any block not covered by the pilot.
`assets/recorded-pilot-42926.json` holds the native result recorded for that build:
all four bodies within 0.08 mm of the host field.

## Choose a few primary surfaces

Read [primary surfaces](references/primary-surfaces.md).

Decompose the shape the way a surfacing studio would. For each large face pick the
section plane in which it is simple, and loft that section along the remaining axis.
Give each section four to about ten control points, apart from a plan outline that has
to turn two corners.

Let surfaces overshoot each other and trim one with the other. Place the intersections
where the design has its feature lines. Do not make one section carry two faces and the
edge between them. Do not let control rows collapse onto each other at the ends of a
loft: converging rows produce dimples.

Use a half section with the absolute lateral coordinate for symmetric bodies. Give the
first two control points the same height so the mirrored halves meet without a crease.

## Make the guides fair

Read [fair guides](references/fair-guides.md).

Every control point coordinate is a constant, a low-order function, or a guide: a cubic
B-spline function of the loft coordinate with few control values. Fit guides by least
squares with a fairness penalty and record their deviation from the keys. Do not
interpolate measured keys with many control values. Tracing scatter of a millimetre is
invisible in a shaded view and obvious in a reflection.

Where the curvature history matters most, design it. State the curvature as a few
bumps along arc length, integrate it, and fit those few numbers to the traced outline.
Use analytic profiles where a face is a simple arc or parabola.

## Join surfaces with compact C2 blends

Read [blends and seams](references/blends-and-seams.md).

Use the compact quartic smooth minimum and maximum (`sminq`, `smaxq`). They leave both
surfaces untouched outside the blend support and are C2 at its edge. The width is a
field parameter, not a fillet radius. Choose it per seam: about 14 mm reads as a crisp
belt line on a car-sized body, 60 to 90 mm as a soft pillar. Let the width be a field
where one seam must be tight in one place and open in another.

A blend cannot repair incompatible surfaces. If a seam pinches or waves, change the
surfaces so they cross at a steadier angle, then choose the width.

## Cut details from the envelope

Read [details and masks](references/details-and-masks.md).

Build skins, glass, covers and trim as layers of the one envelope field, limited by
region masks drawn in a view plane. Parts made this way share the surface exactly.
Draw masks as closed Spline DF curves with rounded corners. Make panel gaps as shallow
grooves driven by the distance to a gap curve.

## Check fairness, then fix the cause

Read [fairness checks](references/fairness-checks.md).

Check in this order, on a host preview, before any native import:

1. Guide report: control values, deviation from keys, inflections, curvature extrema.
2. Plane sections of every primary surface and the blended result, at stations between
   the ones used for fitting.
3. Curvature against arc length on those sections.
4. Zebra stripes from several views, in two stripe directions.
5. Silhouette overlay on the calibrated reference.

Fix flaws at their source: the guide, the control polygon, or the choice of surfaces.
Do not smooth the final field, widen a blend, or move single control values to hide a
flaw. The table in the fairness reference maps each symptom to its usual cause.

## Author natively and deliver

Read [native authoring](references/native-authoring.md) before a large import or export.

Freeze the geometry on host previews first. A change after the notebook import or the
native export repeats hours of work. Keep the graph small, import heavy sections last,
and export left-right twins once. Compare native field probes and native mesh vertices
with the host field, and report the largest difference.

Deliver the editable notebook or recipe, the guide report, section and zebra images,
the reference overlay, and the native comparison. Name what was checked on the host,
what was checked natively, and what was not checked. Sampled checks do not prove the
whole surface. Zebra images are an inspection aid, not a Class A acceptance.

See [worked cases](references/worked-cases.md) for the measured outcomes behind this
method. Case measurements are not defaults.
