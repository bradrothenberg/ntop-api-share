---
name: ntop-hm-blending
description: Build constrained implicit blends in nTop using Holder-Minkowski field averaging, including wing-fuselage roots with crown and keel anchors. Use for spatial blend control, root-shoulder repair, or comparison with a conventional smooth union.
---

# Constrained Holder-Minkowski blends in nTop

Build editable native field graphs. Use the paper's averaging operator to combine
candidate fields that already satisfy the required surface constraints.

This skill covers the construction and its checks. Use the available
ntop-notebook-api skill for console access, block discovery, wiring, units, and
build-state checks. Use ntop-modeling for the surrounding geometry when available.
If this folder is installed alone, obtain those API mechanics from the installed
nTop build's documentation rather than copying a transport from the worked example.

## Establish the blend contract

Recover the source fields, axes, units, and upstream construction. Keep the
existing model and make a versioned result. Record:

- Which surface can change, the permitted blend region, and intended sharp edges.
- Which curves or surfaces must stay fixed, especially the fuselage crown or keel.
- Whether local removal of source material is allowed. Anchoring can trim a source.
- The requested wing position, profile, camber, twist, and symmetry.
- The geometric acceptance measures and any supplied tolerances.

Use the source and conversation before asking about missing constraints.
Example dimensions are selected design inputs, not defaults for customer aircraft.
Do not replace the user's wing profile with the illustrative analytic wing.

Confirm negative-inside and positive-outside signs at known points. Establish
compatible field scales before blending. Equal zero surfaces with different
field scaling can produce different blends. The example fields have length
units but are not signed-distance fields.

## Construct the candidates first

Read [construction.md](references/construction.md) for the equations and domains.

1. Build smooth source fields near the junction. Averaging a sharp min/max union
   does not by itself remove its inherited crease.
2. Form two compact C2 smooth unions, with independently editable widths.
   Taper their width smoothly along the chord to end the aft fairing.
3. For an upper or lower wing, anchor each candidate to the actual crown and
   keel before averaging. Re-evaluate the source expressions at the anchor
   coordinates. Do not assume an arbitrary imported field has zero there.
4. Spread the anchor correction smoothly across the root. Inspect the shoulders
   at its transition, not just the maximum fuselage height.
5. Keep the corrected candidates as named intermediate outputs.

A narrow band where blend width falls to zero created long shoulders in the
worked example. A broad, smooth anchor correction removed those shoulders.
That correction is an engineering addition, not a result proved by the paper.
Neither its Gaussian width nor its longitudinal taper is universal.

For a wing leading edge that must meet a chine with a tight planform corner,
use `ntop-leading-edge-chine` when available. That skill separates planform
control from upper and lower skin recovery and checks valleys between sparse
sections. Its inlet, edge, and cleanup methods are engineering additions to
this averaging workflow, not claims from the paper.

The compact union is C2 for positive width and smooth inputs. Where width
vanishes it becomes an exact min: verify that a source intersection does not
reintroduce a crease there. A regular smooth field also needs a nonzero gradient
on its zero surface before its surface continuity follows.

## Apply the paper operator

Normalize fields with an explicit positive reference length. Apply Eq.20 with
finite dimensionless log weights and parameter p. Use shifted log-sum-exp and an
explicit p=0 arithmetic-mean branch. Keep every branch finite, including unused
branches that the native evaluator might evaluate.

Read [native-implementation.md](references/native-implementation.md) before
authoring the graph. It gives the measured block families, dependency layout,
unit rules, and verification path.

For fixed finite log weights, p=0 is the **unweighted** mean. For negative p,
increasing a candidate's log weight reduces its effective weight. Do not confuse
these log weights with ordinary positive mixing coefficients.

The average stays between the candidate field values at each point and preserves
their shared zero points. It does not guarantee source enclosure, a bump-free
surface, small curvature, or aerodynamic performance. Spatial p or log weights
add derivative terms; the paper's constant-parameter gradient bound does not
automatically apply.

## Check the resulting shape

Start with a small native pilot. Inspect build state and compare evaluated
native field samples with an independent reference. Then check the regions that
matter to the requested model:

- Find surface roots in transverse and longitudinal sections. Inspect slope
  changes and normal curvature through the whole root, including aft runout.
- Compare actual crown and keel surfaces across the fuselage width. A fixed
  centerline or unchanged bounding box does not exclude adjacent ridges.
- Measure inward source retreat if anchoring is allowed to remove material.
- Check finite field values, nonzero surface gradients, expected connectivity,
  and outboard preservation. Refine sampling before reporting a small defect.
- Inspect native renders at matched camera and detail settings. A render's voxel
  size is not a geometric error tolerance.

For method comparisons, hold source geometry, anchors, support, and dimensions
constant. Compare one conventional C2 union, a linear average of the same two
candidates with matched effective weights, and HM. Report the measured outcome;
do not assume the paper method wins. The
[worked example](references/wing-example.md) records a mixed result.

Use the portable reference and checks when useful:

~~~powershell
uv run python "<skill>/scripts/check_blend.py"
~~~

The script tests algebra and compares the scalar example with frozen native
samples. It does not start nTop or replace validation of a newly authored model.

## Deliver

Save named sections for controls, source fields, candidates, averaging, results,
and checks. Hide reference bodies and show the selected result. Collapse authored
blocks and sections on final save, with the notebook root expanded. Follow the
available view-state workflow and verify that presentation edits preserve geometry.

Deliver the versioned notebook, useful native views, and measured limitations.
Keep source-fit errors separate from intended changes. State any remaining aft
feature, source trimming, or unverified region. Do not label continuity or a
successful geometry check as aerodynamic qualification.
