# Torx — specification

Status: IN DEVELOPMENT. A complete parametric screw has converted, run and passed independent integration checks. It is available in out/Torx.ntop for development review; source completeness prevents a standards-conforming final release.

The source work was supplied a complete ISO 10664:1999(E) PDF, not redistributed here, with approximate informative CAD contour ratios and full gauge tables. This permits a labelled derived 1999 CAD contour; it does not establish a unique normative nominal contour or current-2014 conformity. See reference/supplied_iso_review.md. The complete screw additionally needs product and thread geometry; candidate supplier sources are in reference/screw_sources.md.

## Deliverable

A complete screw from a custom nTop block named `Torx`, with geometry driven inside the notebook by family, size/radius, axial length, insertion point and orientation. The user confirmed a cylindrical head and metric thread first, and separate shank and Torx radius overrides. The user requests all families over time, starting with standard internal Torx. No dimensional values are taken from the pasted Wikipedia article.

## Reference and accuracy

Primary reference candidate for the standard internal hexalobular feature: ISO 10664:2014, edition 3, https://www.iso.org/standard/63207.html (accessed 2026-09-15). The ISO catalogue says it was confirmed in 2024. It covers inspection geometry and gauging, and expressly is not a manufacturing standard. The catalogue is not the full dimensional reference.

The user clarified that the target is precise CAD geometry checked against official dimensions. Aerospace manufacturing qualification is outside the requested acceptance claim.

Reference floor: the informative ratios are approximate and have no certified error bound. Table 1 A/B values are exact declared nominal dimensions, not metrology of one physical sample. The independent circle construction uses these nominal values and chooses convex radius 0.1 A, deriving the concave radius to enforce tangency. The nTop geometry acceptance for this declared CAD construction is 0.1 micrometre at sampled boundary points, plus signs 2 micrometres either side. This is a numerical construction check, not a claim that the source specifies the entire physical contour to that tolerance. No contour optimisation is performed. Nominal-reference and gauge semantics remain separate.

Every family must have its own source record. A standard size identifies a source table row. A freely overridden radius describes a custom size, unless independently shown to satisfy the selected standard row. Other families must not reuse the internal T profile by assumption.

## Input contract

| Input | Meaning | Constraint / status |
|---|---|---|
| Family | Native Choice List | Internal Torx or Tamper-resistant Torx |
| Series | Native Choice List | Cylindrical, pan or historical 2013 countersunk; exact revisions in README |
| Metric size | Native Choice List | Fourteen labels spanning 31 supported series/size combinations; incompatible pairs rejected |
| Drive size | Native Choice List | Automatic or sixteen internal drive rows T6 through T100 as listed in README; eleven supported TR posts |
| Shank radius override | Maximum radial envelope of screw thread | Separate from Torx radius; custom sizing mode |
| Torx radius override | Maximum radial envelope of recess | Positive; explicit custom sizing mode |
| Length | Screw length from the underhead seating plane towards the tip | Positive |
| Insertion point | Centre of the underhead seating plane | Point with length units |
| Axis | Direction from seating plane towards screw tip | Non-zero vector; normalised; head lies on opposite side |
| Tangent reference | Direction fixing angular orientation | Must have a non-zero projection perpendicular to Axis |
| Clocking angle | Additional rotation about Axis | Angle; proposed default zero |

Frame proposal: z = normalised Axis; x = normalised projection of Tangent reference onto the plane perpendicular to z; y = z cross x. Clocking rotates x and y about z. No silent fallback for a zero axis or parallel tangent. A surface normal and tangent can be connected upstream. Automatic surface selection is not yet specified. Recipe units are SI.

## Construction and acceptance

Read the existing mature construction grammar before authoring; findings belong in reference/corpus_review.md. Select an exact contour representation from the full source, then extrude and place it parametrically. Do not approximate the contour by a generic six-lobed sine wave.

Acceptance will compare source dimensions and independent contour predictions with nTop field samples across supported sizes, custom scaling, lengths and oblique placements. Check symmetry, boundary positions and invalid inputs. Inspect axial and transverse slices and a whole-object view against the source drawing before delivery. Write predictions before execution. Preserve the .ntop and its export JSON together.

## Open decisions

1. Complete screw confirmed, cylindrical head and metric thread first.
2. Exact supported standard sizes after source review; size selector and override accepted.
3. Full authoritative dimensional source for each included family.
4. No manufacturing qualification requested: source-checked CAD geometry is the target.

## Current acceptance and remaining work

Measured: 5,840 recess checks over sixteen sizes; 444 generic thread checks; 38 placement checks; six head boundary checks; seven default assembly checks; 105 public integration checks with independent scaling and oblique placement. Boundary acceptance is numerical construction accuracy, not a source tolerance certification. Native transverse recess and axial screw slices were inspected.

The supplied 1999 Annex A ratios support a declared derived CAD contour. The user's subsequent expansion request accepts this development accuracy. Full relevant tables were recovered for ISO14579:2011 cylindrical, ISO14583:2011 pan and ISO14581:2013 historical countersunk. Source facts and exact scope are in README and the three source JSON tables. The flat-root basic thread, abrupt runout and flat tip remain explicit simplifications; no manufacturing-conformity claim is made.

The public family, series, metric size and drive size inputs are native Choice Lists. Incompatible series/size combinations, unsupported TR post sizes, excessive recess radius and too-short lengths are rejected. The countersunk datum is the top-face centre and its length includes the head. Cylindrical and pan retain the underhead datum and length convention.

Reference floor for expanded profiles: pan rf is explicitly approximate; ISO informative drive ratios have no certified error bound. Camcar inch/metric post rounding differs by up to a few micrometres between cited sheets. Each chosen row retains its own units and provenance, not an averaged value. The 0.1 micrometre numerical boundary gate verifies the declared construction only; it does not resolve these reference uncertainties. Countersunk2013 is not asserted equivalent to the revised2022 profile.

## Evolution and maintainability

Keep a stable public `Torx` interface, a shared placement/length layer and separate family definitions. Store source data with source document, revision, page/table, units and feature role (recess, gauge or driver); these roles are not interchangeable. Preserve old family identifiers. Each family carries its own independent reference predictions and acceptance evidence. Add a family only when its complete contour and dimensions are source-backed and validated. Unsupported families must report unsupported rather than silently use the standard Torx profile. Preserve superseded implementations in archive/.
