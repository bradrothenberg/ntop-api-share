# Aircraft fairing case: observed results and limits

This note summarizes a native modeling case without the source aircraft,
customer dimensions, station coordinates, or workstation paths. The reusable
equations are in the other references. These observations are not defaults.

## Compatible sections and centerline fairness

Local field corrections left long shoulders above and below the chine.
Competing section candidates produced wrinkles and a trailing-edge bite.
Shared camber, positive thickness, and common chord bounds removed those
incompatibilities before averaging.

A fitted camber field had also absorbed existing twist. Recovering untwisted
sections and applying a complete rotation separated the section angle from
its leading-edge location. Holding a straight spatial edge required section
translation instead of retaining the old fixed pivot everywhere.

At BL 0, zero derivatives of body coefficients were insufficient. Chord guides
and section placement still used absolute span. An even coordinate removed the
crease. A later curvature check found a shoulder from derivative overshoot in
that map. The selected monotone rounded coordinate reduced sampled transverse
curvature variation by 51.4 percent above and 49.8 percent below. Those results
apply only to the measured case and domain.

## Tight planform and smooth skins

The accepted root correction kept a tight planform corner and opened the blend
with height from the chine. Upper and lower recovery heights were independent.
Growing width only with distance aft left valleys despite C2 support boundaries.

A sparse four-section check missed a lower-skin valley. The dense check used
17 span stations and 321 longitudinal samples per skin at each station.
Both skins retained the intended slope progression in that domain. Native
checks covered 383 points, including 156 skin points. Maximum native field
residual was 1.31404e-11 m; maximum map disagreement was 1.33227e-15 m.
The sampled minimum map Jacobian was 0.978666. These are agreement and sampled
regularity results, not geometric tolerances or a global continuity proof.

## Shorter recovery and the latest candidate

A later request shortened the visible crease aft of the intersection. A
front-loaded return eliminated its correction within the requested distance,
but created an inward dent and an outward shoulder. The earlier smooth skin
was restored. Zero correction beyond a station did not establish fair geometry
inside the transition.

A one-sided fullness envelope also left a shoulder. After the user allowed a
broader planform corner, a bounded shifted-conic height opening passed sampled
checks without inward movement. Its strict visible-crease limit remained
unverified. Planform radius and longitudinal crease length were separate controls.

Further shortening required a coupled sweep of axial length, height-opening
scale, and local section-nose regularization. See
[compact-recovery.md](compact-recovery.md) for the equations and composition order.
The final candidate used a recovery window 46.15 percent shorter than its
immediate predecessor. It retained some inward skin motion, so the previous
no-inward-motion result did not apply.

Checks covered 60,701 locations per skin and 60 transverse or oblique cuts.
The sampled nose region retained the required curvature sign. All checked cuts
had zero detected interior minima. Normal differences approximately halved as
sample spacing halved. Native checks included 924 skin points, 484 guide points,
and 700 retained points. All 443 samples selected as protected matched exactly.
An independent forward-envelope check covered 162,004 points with no sampled
added material ahead of the guide.

These checks support the candidate. They do not prove global C2 continuity,
exact source-surface preservation, or the strict visible-crease distance.
User visual approval of this latest candidate was still pending when recorded.
Byte-exact replay of its retained graph and edits to the preceding graph are
reproduction methods. Neither independently fits a new aircraft from its source.

## Curved inlet restored after a failed plane repair

A plane made the lip projection straight but introduced a flat shelf. The
accepted correction restored the curved inlet and moved measured crest points
with a local inverse coordinate map. Rounded returns had separate transitions.
An even transverse law removed an inherited cusp at the upper middle lip.

Checks used 69 main-lip stations per side, including 34 independent intermediate
stations. Maximum estimated projected-line error was 0.01124 mm. Separate
return-normal and centerline checks were needed; the line check alone missed
those defects. All 341 protected field samples matched the preceding root model.

## Rear edges, attachment, and cleanup

The physical wing edge differed from its chord guide because of finite thickness
and twist. Paired longitudinal and vertical coordinate corrections straightened
the selected panel segments. All 200 native stations per side passed section
brackets at plus/minus 0.025 mm. Intended corners, tip cuts, and the center exhaust
return were excluded and were not certified straight by that check.

An extended fin initially overhung the aircraft because the nominal aft station
lay beyond the upper shell after the exhaust cut. Measuring that shell junction
fixed the attachment. The fin used the wing's measured thickness/chord rule.
A later root-blend taper reduced the aft flare while leaving the fin line fixed.
Native checks covered 464 protected points, 31 fin sections, and 81 taper stations.

Cleaning the selected notebook removed 1,342 unused blocks and 409 literals.
All retained geometry definitions were unchanged, and 2,556 native field samples
matched exactly. The later tapered-root file was checked separately.

A follow-up request to straighten the center wing edge below the fin remained
unresolved between side-view and plan-view intent. Do not present the accepted
outer-panel or root-taper checks as verification of that unfinished correction.

These outcomes concern the constructed geometry and sampled regions. They do
not demonstrate aerodynamic performance or an intrinsic fairness advantage of
the paper's averaging operator over compatible conventional constructions.
