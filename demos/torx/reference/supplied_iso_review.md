# Supplied ISO 10664 review

## Finding

The supplied PDF enables a source-backed **derived CAD representation of the 1999 internal hexalobular feature**. It does not prescribe one unique exact nominal circular-arc contour. The nominal A and B dimensions can be honoured exactly while using the informative Annex A radius ratio as a design choice and deriving the other radius for tangency.

This review uses the PDF skill. All ten pages were read and visually inspected, including all figures and Tables 1–5. Poppler rendering reported a missing Symbol display font and rendered the approximate sign incorrectly; PyMuPDF renders correctly and agrees with extracted text. The approximate signs on Annex A are confirmed visually.

## Identity and scope

- Supplied original: a complete ISO 10664:1999(E) PDF, left unchanged and not redistributed.
- SHA-256: `e80415498ecc49b5ce35f5a65b760ce67069cd277d12689a3617c5dd95c1f3dc`.
- Ten PDF pages: cover, foreword, seven numbered substantive pages, back cover.
- Front and substantive pages identify **ISO 10664:1999(E), first edition, 1999-09-01**. The back cover unexpectedly says ISO/FDIS 10664:1999(E). This provenance inconsistency is retained, not silently repaired. The supplied copy has not been authenticated against an ISO-issued original.
- This is the superseded 1999 edition. Current 2014 status was separately checked in `official_sources.md`; no equivalence between their dimension tables has been established.
- Clause 1 states that this is an inspection standard and not a manufacturing standard. Tables 3–5 define the gauged contour requirements.
- Annex A is expressly informative and gives approximate correlations for drawing/CAD representation: B approximately 0.72A, re approximately 0.1A, ri approximately 0.175A.

## Page map and semantics

PDF page 3 / printed page 1: Figure 1 identifies A as opposite lobe-tip diameter and B as the inscribed valley diameter. Counterbore c is at most 0.13 mm through socket 15 and at most 0.25 mm above socket 15. Text extraction incorrectly returns a strict inequality; the visual shows less-than-or-equal. Penetration t comes from the relevant screw product standard. Bottom geometry beyond the gauge is left to the manufacturer.

PDF page 4 / printed page 2: Table 1 provides sixteen nominal A/B pairs. Table 2 gives maximum allowed no-go penetration (fallaway); this is not a prescribed recess depth or a default chamfer depth.

PDF pages 5–6 / printed pages 3–4: Figure 3 and Table 3 define GO-gauge A, B, Ri, Re, H limits. H is gauge geometry, not screw recess depth. Gauge edge radius note is 0.076 mm maximum for sizes **greater than or equal to 10**, and 0.0254 mm below 10; extraction loses the inequality glyphs.

PDF page 7 / printed page 5: Figure 4 and Table 4 define a different NOT GO gauge for A/Re. B is a maximum, not a min/max interval. The other limiting dimensions must not be collapsed into a nominal recess.

PDF page 8 / printed page 6: Table 5 provides cylindrical NOT GO gauge diameters. These exceed nominal B; do not substitute this table into the CAD B input.

PDF page 9 / printed page 7: Figure A.1 draws alternating concave and convex arcs with sixfold symmetry. The sketch's auxiliary circle touches three points; it is not a definition of a single central circle. The radius correlations remain approximate.

## Nominal values admitted from Table 1

Values in millimetres, visually checked against PDF page 4. Supported size IDs are not consecutive; absent IDs are not interpolated.

| Socket | A | B | Socket | A | B |
|---|---:|---:|---|---:|---:|
| 6 | 1.75 | 1.27 | 45 | 7.93 | 5.64 |
| 8 | 2.4 | 1.75 | 50 | 8.95 | 6.45 |
| 10 | 2.8 | 2.05 | 55 | 11.35 | 8.05 |
| 15 | 3.35 | 2.4 | 60 | 13.45 | 9.6 |
| 20 | 3.95 | 2.85 | 70 | 15.7 | 11.2 |
| 25 | 4.5 | 3.25 | 80 | 17.75 | 12.8 |
| 30 | 5.6 | 4.05 | 90 | 20.2 | 14.4 |
| 40 | 6.75 | 4.85 | 100 | 22.4 | 16 |

## Derived tangent-arc construction

All these formulae are **derived**, not quoted standard equations. Let b=B/2, choose re=0.1A using Annex A's approximate guidance, and let c=A/2-re. Put a convex lobe-circle centre at (c,0), and the adjacent concave valley-circle centre at d(cos30°,sin30°), where d=b+ri. External tangency requires the centre separation to equal re+ri. Solving gives:

```
ri = (b*b + c*c - 2*b*c*cos(30deg) - re*re)
     / (2*(re + c*cos(30deg) - b))
```

The point of tangency is `C + re/(re+ri)*(D-C)`. Repeat every 60 degrees and mirror each half-sector. The construction preserves exact Table 1 A/B and exact circle tangency. It does not impose all three rounded Annex ratios as exact constraints, which would generally be inconsistent.

For T20 the derived radii are re=0.395 mm and ri=0.696511312589 mm. Across all sixteen rows ri/A varies approximately 0.163794–0.189115 because Table 1 B/A is not fixed. The whole profile must scale together in a user radius override; it then ceases to represent the selected standard nominal size.

## Bounded independent numerical audit

`contour_reference.py` contains the checked Table 1 values, the checked Table 3 A/B/Ri/Re limits, exact circle/ray intersection formulae, and a reproducible sampled audit. Run `python projects/torx/reference/contour_reference.py`.

For every size it samples nine values of each GO A, B, Re dimension (729 candidate combinations), derives a tangent Ri, and retains only combinations within the source Ri limits. It then compares the derived recess and each retained aligned, coaxial GO profile at 3,601 angles over a half-sector. This deliberately avoids pretending independent limit combinations are necessarily tangent circles.

The audit found **no sampled aligned GO interference in any of the sixteen nominal candidates**. Between 129 and 690 feasible sampled gauges were retained per size. Minimum sampled radial clearance over all sizes was 0.012 mm, at T10. T20's minimum sampled radial clearance was 0.0285 mm. These are computed diagnostic results, not ntopcl measurements and not a continuum proof.

The audit does **not** certify arbitrary tolerated profiles, optimise free gauge position/rotation, inspect NOT GO behaviour, or test axial penetration/fallaway. Do not label its result ISO conformity. Full screw head, shank, thread, runout, and overall length need a selected product/thread standard. This PDF only defines the internal driving feature.
