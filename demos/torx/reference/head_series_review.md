# Additional Torx head series: development CAD evidence

## Pan head: sufficient dimensions for the declared CAD accuracy

[ISO 14583:2011](https://www.iso.org/standard/56457.html) covers M2–M10 and is current, confirmed in 2026. The [public standard excerpt](https://cdn.standards.iteh.ai/samples/56457/0bac81ddea0f4a65ac3ef4f2233e35e0/ISO-14583-2011.pdf) contains Figure 1 and all of Table 1. Downloaded under `series_expansion/ISO14583_2011_preview.pdf`; both relevant pages were rasterised and inspected as `pan_page_6.png` and `pan_page_7.png`.

**Machine-readable hand-off:** `series_expansion/ISO14583_rows.json`, nine sizes, including non-preferred M3.5. It gives pitch, head diameter/height, dome radius, underhead radius, neck/runout bounds and drive/depth.

### Construction interpretation

Place bearing plane at z=0. A sphere of radius `rf` centred at `z=k−rf`, intersected with `rho≤dk/2` and `z≥0`, supplies the dome and cylindrical side. Its junction height is `k−rf+sqrt(rf²−(dk/2)²)`. Add the underhead fillet using `rmin` and the chosen shank diameter. This is an engineering interpretation of the section, to be checked by slices.

Source `rf` is explicitly **approximate**. The dome-to-side micro-round is not independently dimensioned. Sharp joining of the exact spherical cap to the cylindrical side is therefore a declared development simplification, not a complete manufacturing contour claim.

For full threading, `b=l−a`; choose `a=amax=2P`. All supplied `rmin` values are smaller than `amax`. For longer screws Table 1 supplies minimum thread length `bmin`, and Figure 1 locates incomplete-thread extent `x` immediately before the full thread. The source allows shank diameter approximately equal to pitch diameter or equal to major diameter. Choose the latter consistently with the existing screw policy. The pictured point is as-rolled; no extra conical-tip requirement was inferred.

## Countersunk: version-sensitive, not an interchangeable pan extension

[ISO 14581:2022](https://www.iso.org/standard/78695.html) is the current common flat countersunk-head standard, with reduced loadability. Its [downloaded preview](https://cdn.standards.iteh.ai/samples/78695/7d1c47f5e2e84c61a0591da82c08b586/ISO-14581-2022.pdf) ends after Figures 1–2, before detailed Figure 3 and Table 1. In particular its foreword records changed underhead reinforcement geometry compared with 2013.

A [2013 preview](https://cdn.standards.iteh.ai/samples/56219/1ae60f07e2a24bb691e8e71ff0a064f4/ISO-14581-2013.pdf) containing dimensions was also downloaded, but it is a superseded edition. It has not been converted into a current-series model or silently substituted for 2022. The current countersunk family requires the remaining current geometry pages or an equivalent supplier drawing. Research was bounded here so the source-ready pan family can proceed.

These findings are DOCUMENTED source readings and construction candidates, not nTop measurements. No main builder or recipe was modified by this review.

## Explicit historical option: ISO 14581:2013

Following the edition-labelled development scope, the available 2013 Figure 1 and Table 1 were fully visually inspected. `series_expansion/ISO14581_2013_rows.json` now provides nine M2–M10 rows, with theoretical/actual head diameter, k, r maximum, neck bound, shoulder requirements, pitch and drive/depth.

At nominal 90 degrees, a flat rim of height `k−(dk_actual−d)/2` above a frustum ending at diameter d is a candidate nominal envelope; that formula is a geometric derivation, not a separately specified rim dimension. Top-head edge may be flat or rounded. Length is measured from head top, unlike pan/socket-head screws. M5–M10 require an axial shoulder of at least one pitch, whose shape is discretionary and whose diameter must not exceed d. A cylinder of diameter d and length P is a candidate. Use `a≤2P` without shoulder and `a≤2.5P` with shoulder; full thread `b=l−(k+a)`.

The table specifies **r maximum only**. A sharp cone-to-shank junction is a declared development simplification; choosing and inserting a fillet requires checking k and the neck/diameter envelope. Do not silently adopt rmax as a prescribed nominal radius.

This is a usable **2013-labelled historical development family**, not the 2022 standard. Revision differences are only partially established from the new edition's foreword; dimensional equivalence remains unverified.
