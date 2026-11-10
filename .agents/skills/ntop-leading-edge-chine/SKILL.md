---
name: ntop-leading-edge-chine
description: Integrate a wing leading edge into a fuselage chine with controlled section lofts, explicit twist, and straight edge constraints. Use to repair root hooks, upper or lower wrinkles, trailing-edge bites, or a wavy leading edge in nTop.
---

# Leading-edge and chine integration

Make the section geometry compatible before applying an implicit blend. A smooth
averaging operator cannot repair a wrong edge, twisted fit, or incompatible skin.
Use the [Notebook API skill](../ntop-notebook-api/SKILL.md) for task-owned console access, native graph authoring, and verification.
Use `ntop-hm-blending` when applying the Holder-Minkowski operator.

## Recover the geometry contract

Read the reference construction, not only its rendered silhouette. Identify the
planform, airfoil, camber, thickness, chine, twist angles, rotation sign, and pivot.
Measure these from the graph or geometry. Keep the source during iteration.

Separate the constraints:

- The outer leading edge can be a straight spatial line or only straight in plan.
- The root entry can be curved while the exposed wing edge stays straight.
- A chine can remain intentionally sharp while the adjacent skins stay smooth.
- Twist specifies section orientation. Its pivot also determines section position.
- A wing trailing edge at the fin base is a different boundary from the fin's
  trailing line. Resolve the marked component and projection before changing it.

Use the user's stated priorities to resolve conflicts. With variable twist, a
fixed pivot generally curves the leading edge in 3D. Straightening it while
retaining the angles requires moving sections. Measure that placement change.
Do not describe the resulting model as an exact reference reproduction.

## Build compatible sections

Read [construction.md](references/construction.md) for the frame, section, and HM
equations before implementing this construction.

1. Recover untwisted section samples if the reference already contains twist.
   Fit camber and thickness in that frame. Do not encode rotation in camber and
   then apply the rotation a second time.
2. Define leading and trailing boundaries first. Constrain endpoint camber to
   zero relative to the chosen chord. Treat a finite trailing-edge thickness
   separately from camber.
3. Blend body-side and wing-side section parameters over a broad, smooth span
   interval. Use a shared center and positive thickness law for both skins.
   Retain separate named source lofts for inspection.
4. Align the conic section's narrow edge with the intended chine. Control its
   rounding independently of the blend extent. Inspect the whole upper and
   lower transition, not just the centerline crown and keel.
5. Give the candidate fields the same chord bounds and compatible thickness.
   Apply a normalized HM average only after these constraints hold.
6. Place each section using a complete rigid rotation about its edge anchor.
   Transform both longitudinal and vertical coordinates. A height offset alone
   does not implement twist. Keep unrelated tail geometry in world coordinates.
7. At a mirrored centerline, make the one-sided span derivatives vanish for
   every active shape and placement law. Absolute span alone can create a crease.
   Test an even local coordinate and report any inboard twist easing it requires.
8. Check curvature across the full center body after removing the crease. A
   center-height-preserving coordinate can overshoot its span derivative and leave
   a shoulder. If crown and keel can move, compare a monotone rounded coordinate
   with a smooth width envelope. Report the resulting body-shape changes.

Use positive, explicit field normalization lengths. Compact C2 weights can match
derivatives at support boundaries, but they do not bound curvature inside them.
Do not use a sharp final clip through a desired smooth skin. Intentional edge or
tip caps need their own visual and geometric checks.

## Keep a tight planform without skin valleys

When tightening the chine-to-wing corner, read
[root-fairness.md](references/root-fairness.md). It gives the approved construction
that separates planform radius from upper and lower skin recovery.

Calibrate the compact blend width against the actual planform curvature. Open
that width with height from the leading-edge chine, using separate upper and
lower recovery heights. Keep the longitudinal return as a separate control.
Do not drive width growth only by distance aft of the edge. That construction
left valleys even though its transition weights were C2.

Select recovery heights from measured sections and a small parameter sweep.
Then check denser sections between the first test stations. Preserve the straight
outboard edge, twist, chine, and protected features through measured checks.

For a strict aft crease limit, read the rejected short-runout example in that
reference. A short support and smooth endpoint derivatives do not preserve the
accepted skin shape. Compare signed surface displacement, transverse sections,
and oblique views. Do not trade a long crease for a local dent or bulge.

For a shorter recovery that retains a fair nose, read
[compact-recovery.md](references/compact-recovery.md). Tune axial length,
height opening and local section regularization together. Preserve the native
coordinate-composition order and check actual edges after changing rounding.
Record the baseline for each reduction percentage. A recovery window is not a
measured visible crease length.

## Verify the actual result

Run a small native build first. Compare native evaluated fields with an independent
implementation at interior, exterior, root, and edge points. Inspect graph units
and wiring. Then verify:

- Leading-edge distance from the prescribed spatial line over the exposed span.
  Check the actual surface nose as well as the nominal airfoil endpoint.
- Section angle from chord vectors, separately from camber and dihedral.
- Upper and lower surface roots, positive interior thickness, and edge closure.
- Surface normals and section curvature through root entry and aft runout.
- Upper and lower one-sided slope convergence at BL 0. Mirror symmetry of point
  positions does not establish matching normals.
- Curvature variation and longitudinal profiles through the entire fairing band.
  Zero center slope alone does not establish a visually fair body.
- Upper and lower slope progression between sparse test sections. A C2 map can
  still introduce interior valleys. Check map invertibility and measure surface
  displacement, as described in the root-fairness reference.
- Reference fit with the intended placement change reported separately.
- Native top, front/edge-on, upper oblique, and lower oblique views.

For CSV section measurements, use `scripts/check_sections.py`. It expects a
header with `y_m,x_le_m,z_le_m,x_te_m,z_te_m,twist_deg`. It compares each side's
leading edge with the line through its first and last sample, and checks chord
angles. Supply acceptance tolerances from the task. Its report does not establish
surface fairness or native evaluation by itself.

## Refine adjacent inlet and trailing edges

For inlet-lip straightening, finite trailing edges, or a fin-root runout, read
[inlet-and-trailing-edges.md](references/inlet-and-trailing-edges.md). Preserve a
curved inlet through a local coordinate map when a plane cut would create an
unwanted flat zone. Measure the physical crest or edge, including thickness and
twist. Taper an aft root blend toward the specified bead size instead of carrying
its full forward width to the termination.

Save named sections and collapsed authored blocks. Show only the intended final
body. Deliver the notebook, native views, and measured limits. Distinguish exact
algebraic constraints, sampled verification, source fitting, and aero validation.

When asked to deliver a clean model or remove old revisions, use
[notebook-cleanup.md](references/notebook-cleanup.md). Keep only the current
output's dependencies, prove geometry equivalence, and make rebuild and check
tools independent of retired folders before deleting them.

See [aircraft-case.md](references/aircraft-case.md) for the measured outcomes and
failure mechanisms behind this workflow. Case measurements are not defaults.
