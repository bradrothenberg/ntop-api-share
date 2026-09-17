> Copied from the origin project as provenance. Its links were relative to that
> checkout; the ones that pointed at directories this demo does not carry
> (`placement_v1/`, `placement_v2/`, `release/`, `optimisation/`) are now plain
> text. The origin project retains them.

# Torx

**V2:** mould outputs and flush placement, from `release/V2/Torx_Example.ntop`, the ready-wired two-list workflow. V0 and V1 remain preserved in the origin project.

**Placement V1:** a batch and surface-placement guide, with the notebook in `release/V1/Torx.ntop`. Frozen V0 is retained in `release/V0/`. The geometry coverage and accuracy limitations below apply to both.

Status: working DEVELOPMENT complete screw; not a standards-conforming final release.

Open `release/dropdown_v2/Torx.ntop`; its export JSON is beside it. Default: cylindrical M3, T10, 10 mm underhead length. See [SOURCE_SPEC.md](SOURCE_SPEC.md) and the source reviews beside it.

## Controls

- Drive family: native Choice List, Internal Torx or Tamper-resistant Torx.
- Screw series: native Choice List, Cylindrical / ISO 14579:2011, Pan / ISO 14583:2011, Countersunk / ISO 14581:2013 (historical).
- Metric size: native Choice List with diameter and coarse pitch. Series-specific coverage is below.
- Drive size: native Choice List, Automatic or T6, T8, T10, T15, T20, T25, T30, T40, T45, T50, T55, T60, T70, T80, T90, T100.
- Length: underhead to tip for cylindrical/pan; total length including the head for countersunk. Must leave positive threaded length.
- Override shank + Shank radius: scale the selected screw envelope, head and pitch.
- Override Torx + Torx radius: independently scale the recess maximum radius.
- Insertion Point: underhead seating centre for cylindrical/pan; flush top-face centre for countersunk. Axis points towards tip; Tangent Reference fixes orientation; Clocking Angle adds rotation. Axis must be non-zero and tangent must not be parallel to it.

Invalid series/size pairs, unsupported TR posts, excessive recess radius and insufficient lengths are rejected. Custom scaling does not retain a standard metric thread designation. The checks preserve the declared CAD envelope; they do not establish strength or manufacturing tolerances. Head and pitch scale with shank radius; post diameter scales with recess radius.

## Coverage

| Series | Metric sizes | Source-derived head construction |
|---|---|---|
| Cylindrical | M2, M2.5, M3, M4, M5, M6, M8, M10, M12, M14, M16, M18, M20 | Maximum plain head diameter/height, top quarter-round chosen at vmax, underhead rmin. Short neck chosen at 2P; longer source regime uses l-b. |
| Pan | M2, M2.5, M3, M3.5, M4, M5, M6, M8, M10 | Source approximate rf represented by an exact spherical crown; cylindrical side, underhead rmin, neck amax. |
| Countersunk, 2013 | M2, M2.5, M3, M3.5, M4, M5, M6, M8, M10 | Actual maximum head diameter, flat rim and 90-degree included cone; source amax neck provides the M5+ shoulder. |

Tamper-resistant post coverage: T8, T10, T15, T20, T25, T30, T40, T45, T50, T55, T60. These are custom derivatives combining the ISO recess construction with actual Camcar reference post dimensions. An automatic T6 recess has no supported TR post; select a supported compatible drive manually. T27 remains unavailable because the supplied nominal contour table has no T27 A/B pair.

External E, Torx Plus, Paralobe and ttap are not offered as working selections: their complete nominal contours were not established. See [family_expansion.md](family_expansion.md) for the exact source gaps.

## Evidence and limitations

The 16-size derived recess construction passes 5,840 independent boundary/sign checks. The analytic thread kernel passes 444 checks; placement passes 38 field/bounds checks. Expanded acceptance covers 44 valid configurations: 31 head-series/metric rows, 11 TR post sizes, a long shank and independent oblique scaling. After replacing the faulty long revolved countersunk neck, its nine sizes pass 144/144 checks, combined with 452/452 unaffected checks: 596/596 across the recorded branch-specific versions. Six invalid-input cases reject execution. Final default passes 7/7. These checks establish the implemented construction, not manufacturing conformity.

Native 3D inspection and sections were performed. One native X-slice stack incorrectly omitted the pan shank despite correct field samples and full bounds; the independent Y stack and native 3D view show the complete screw. Both raster witnesses are retained. Do not use that X stack as a geometry reference.

The supplied ISO 10664:1999 nominal A/B dimensions are used exactly, with a chosen informative Annex A radius ratio and tangent circle construction. Full relevant head tables were recovered and visually inspected; the earlier missing ISO14579-table limitation is resolved. Source limits and approximate radii still do not prescribe one unique manufactured surface. The generic thread remains the ISO68-1 basic profile; actual external root, runout and tip details remain simplified. The pan crown-to-side micro-round is omitted. Countersunk uses a sharp cone-to-neck junction and the explicitly historical 2013 envelope, not the changed 2022 design. Reference rounding differences and the approximate rf/Annex ratios limit physical accuracy regardless of numerical residuals.

## Maintenance

`Torx` references `Torx_Local` and `Place_Screw`; local assembly references the drive, three separate head definitions and metric thread kernel. Source facts and stable identifiers are centralised in `recipes/catalogue.js` and source JSON tables, separate from geometry. A bounded native cylinder extends the plain shank, avoiding a measured long-neck failure in the unchanged cylindrical-head kernel. Each component has its own notebook/export pair and independent probes. The former numeric-input version is preserved in `archive/v1_numeric_inputs/`. No production-conformity release has been registered.
