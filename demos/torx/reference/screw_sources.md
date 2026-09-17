# Complete Torx screw: primary source candidates

Research date: 15 September 2026. Evidence tier: DOCUMENTED; no geometry has been measured here.

## Product family

[ISO 14579:2011](https://www.iso.org/standard/56455.html) covers hexalobular socket head cap screws, M2–M20, product grade A. ISO lists edition 2 as current, confirmed in 2024. The public abstract establishes scope, not complete dimensions; the full standard was not inspected.

[Bossard BN 4853](https://www.bossard.com/us-en/eshop/screws-and-bolts-with-internal-drive/hexalobular-6-lobe-socket-head-cap-screws-fully-threaded/p/4853/) is a supplier-authored candidate: cylindrical head, internal hexalobular drive, fully threaded, stainless A2, identified with ISO 14579. Fully threaded construction removes a separately selected long plain shank, but still requires thread runout and underhead geometry. This is a modelling recommendation, not a user-confirmed head choice.

## Concrete CAD dimensions

[Bossard CAD catalogue](https://bossard.partcommunity.com/3d-cad-models/?countryIso=TW&info=bossard%2F01%2F01_100%2F01_100_100%2F01_100_100_10%2Fbn_4853%2Fbn_4853.prj&languageIso=zh), retrieved public table; all values millimetres except drive number:

| Parameter | M2 × 10 | M2.5 × 10 | M3 × 10 |
|---|---:|---:|---:|
| Article | 9014525 | 9014533 | 9014541 |
| D | 2 | 2.5 | 3 |
| D3, core diameter | 1.509 | 1.948 | 2.387 |
| P, pitch | 0.4 | 0.45 | 0.5 |
| B, thread length | 9.2 | 9.1 | 9 |
| X, runout | 1 | 1.1 | 1.25 |
| A1, maximum | 0.8 | 0.9 | 1 |
| DK, maximum head diameter | 3.8 | 4.5 | 5.5 |
| DA, maximum contact diameter | 2.6 | 3.1 | 3.6 |
| K, maximum head height | 2 | 2.5 | 3 |
| R, catalogue maximum | 0.1 | 0.1 | 0.1 |
| R1, maximum | 0.2 | 0.25 | 0.3 |
| W, minimum residual head | 0.5 | 0.85 | 1.15 |
| Drive number | 6 | 8 | 10 |
| A, reference drive diameter | 1.75 | 2.4 | 2.8 |
| T, maximum recess depth | 0.84 | 1.04 | 1.27 |

The table alone does not locate A1, R and R1 unambiguously. Its R label is a maximum: do not silently reinterpret it as a standard minimum underhead fillet. The engineering drawing must settle these meanings before authoring those details. Catalogue D3 values describe its CAD representation; they do not establish a 6g thread tolerance policy.

## Independent dimensions and thread reference

[Aspen Fasteners ISO 14579 sheet](https://www.aspenfasteners.com/content/pdf/Metric_ISO_14579_spec.pdf), page 1, independently agrees on M3 pitch 0.5, head diameter 5.5, head height 3, drive 10 and A 2.8. Its nominal threaded length B is 18; this differs from the fully threaded product's B = L − A1 and must not be mixed indiscriminately with it. Aspen is the publisher of its own supplier sheet, not the standards authority.

[Bossard metric threads](https://media.bossard.com/global-en/-/media/bossard-group/website/documents/technical-resources/en/f_079_en.pdf), page F.089, gives ISO 965 coarse external thread 6g limits. For M3: major diameter 2.874–2.980, pitch diameter 2.580–2.655, minimum root radius 0.063. For M6: major diameter 5.794–5.974, pitch diameter 5.212–5.324, minimum root radius 0.125. The adjacent selection table gives pitches 0.5 and 1 respectively. Page F.088 identifies a 60° thread and explains clearance between external and internal tolerance zones. These values constrain the thread but do not define one unique manufactured profile.

[Bossard thread profile calculator](https://website-assets.bossard.com/Metric-Thread-Profile/Metric-thread-profile-calc-en.html) names ISO 965-1:1998, ISO 68-1:1998 and ASME B1.13M-2005 as its basis. The public text retrieval exposes no formula or computed result; no values were inferred from it.

## Remaining decisions and access limits

- Confirm cylindrical socket head versus another head family.
- Choose a representative geometry within tolerances, or a manufacturer CAD exemplar with enough detail. Maximum envelopes, reference diameters and minimum radii are not automatically a mutually consistent nominal screw.
- Resolve thread crest/root truncation, actual underhead fillet and top-edge treatment, end chamfer, thread runout shape, and the recess entrance/bottom geometry from a drawing or full standard. None is licensed merely by an external appearance.
- Use ISO 10664 for drive contour; it does not on its own define the entire screw.
- Arbitrary radius overrides produce a custom derivative; do not label those dimensions a standard catalogue size.

The web reader returned the Bossard thread PDF text, but its screenshot fetch returned 404. Direct shell downloads were refused by the network environment and left no downloaded source files. Alternate legacy Bossard PDF URLs also returned 404. Thus numeric text is useful DOCUMENTED evidence; complete illustrated profile inspection remains outstanding. The Bossard product drawing link resolved as an image but its dimensions were not readable through the returned tool view.

## Follow-up: recovered drawings and exact basic thread formulae

The user has confirmed a cylindrical head and metric thread, with independent radius overrides. Browser control was attempted: Chrome unavailable, then browser selection explicitly returned “No browser is available”. Approved shell downloads succeeded; the earlier network limitation is therefore resolved for these URLs.

### ISO 14579 Figure 1 inspected

The [iTeh-hosted ISO preview](https://cdn.standards.iteh.ai/samples/56455/8d50d06494564e18a4b8296633f6b418/ISO-14579-2011.pdf) contains the entire Figure 1 on printed page 2, but **not Table 1**. Saved as `screw_sources/ISO14579_2011_preview.pdf`; inspected raster `screw_sources/ISO14579_2011_figure1.png`.

Figure 1 establishes:

- `l` runs from the head bearing plane to the point; `k` is head height; `t` is penetration from the head top; `w` is residual head material.
- Top outer edge may be rounded or chamfered at the manufacturer's discretion; the pictured chamfer angle is at most 45 degrees. Its axial extent `v` requires Table 1.
- Bottom outer edge may be rounded or chamfered to bearing diameter `dw`.
- Underhead fillet has `rmax = (da,max − ds,max)/2`, and maximum axial extent `lf,max = 1.7 rmax`; `rmin` requires Table 1.
- Point is chamfered, with an as-rolled alternative permitted through M4; ISO 4753 governs that detail.
- Incomplete thread at the point obeys `u ≤ 2P`.

This is direct inspection of an identified standard excerpt, **not evidence that the full standard or its dimensional tables were inspected**. It licenses a rounded or chamfered top-edge design choice but does not supply every magnitude. Bossard's public product drawing was downloaded and inspected as `screw_sources/bossard_bn4853_drawing.webp`; its simple schematic does not annotate R/R1/A1 and therefore does not resolve those CAD-table symbols.

### ISO 68-1:2023 basic profile inspected

[ISO identifies the 2023 edition](https://www.iso.org/standard/85107.html) as the current basic/design profile standard. The [iTeh preview](https://cdn.standards.iteh.ai/samples/85107/2562fb7b223244f5a95c287e78f257a6/ISO-68-1-2023.pdf), saved in `screw_sources/ISO68_1_2023_preview.pdf`, includes clause 5 and Figure 1 but ends before clause 6. Clause 5 explicitly gives:

`H = sqrt(3) P/2`; `H1 = 5H/8`; subsidiary heights `3H/8`, `H/4`, `H/8`.

The basic profile is common to internal and external threads; it is not identical to the external **design** profile. Symbols distinguish basic minor diameter `d1` from design minor diameter `d3`, and distinguish full root radius `R` from root-corner radius `R1`. No external design-root formula was obtained from this excerpt.

### Official Bossard calculator source inspected

Downloaded the HTML and its linked [application module](https://website-assets.bossard.com/Assets/js/app-thread-dimension.js), preserving both and its linked data module under `screw_sources/`. This is source inspection, not execution of downloaded code. Lines 103–115 establish `H = P sqrt(3)/2`, `rootRadius = P/8`, `d2 = d − 3H/4`, and an external nominal minor formula `d − 2(0.69717)H`. The internal nominal minor is `d − 5H/4`. The calculator uses tolerance data separately.

Do not silently equate that external minor formula or the minimum root radius with a complete ISO external design profile. The recovered source settles what the calculator computes, not an uninspected standard clause. A basic-profile CAD screw can be identified explicitly as such; a standard design-profile claim still requires clause 6 or equivalent authoritative drawing.
