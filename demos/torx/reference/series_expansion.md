# Cylindrical Torx screw series expansion

## Evidence

15 September 2026: found a longer public preview containing **ISO 14579:2011 Table 1 in full**, printed pages 3–4. This supersedes the earlier missing-table limitation. It remains a labelled preview, not the purchased full publication.

[Source PDF](https://cdn.standards.iteh.ai/samples/56455/12ad7960b6da426593b3a6a783c47b84/ISO-14579-2011.pdf) saved as `series_expansion/ISO14579_2011_extended_preview.pdf`. Both pages were rasterised and visually read: `series_expansion/page_7.png`, `series_expansion/page_8.png`. Source role: actual standards text hosted by iTeh. Edition 2, 2011-03-15. Evidence tier DOCUMENTED; no nTop measurement here.

## Usable dimensional data

All dimensions millimetres. `dk` is the plain-head maximum; `k` maximum; `t` socket penetration; `r` minimum underhead fillet; `v` maximum top-edge treatment extent; `da` maximum; `lf` maximum axial fillet extent. M14/M18 are non-preferred.

| d | P | dk | k | drive | t min | t max | r min | v max | da max | lf max |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | .4 | 3.8 | 2 | 6 | .71 | .84 | .1 | .2 | 2.6 | .51 |
| 2.5 | .45 | 4.5 | 2.5 | 8 | .91 | 1.04 | .1 | .25 | 3.1 | .51 |
| 3 | .5 | 5.5 | 3 | 10 | 1.01 | 1.27 | .1 | .3 | 3.6 | .51 |
| 4 | .7 | 7 | 4 | 20 | 1.42 | 1.80 | .2 | .4 | 4.7 | .6 |
| 5 | .8 | 8.5 | 5 | 25 | 1.65 | 2.03 | .2 | .5 | 5.7 | .6 |
| 6 | 1 | 10 | 6 | 30 | 2.02 | 2.42 | .25 | .6 | 6.8 | .68 |
| 8 | 1.25 | 13 | 8 | 45 | 2.92 | 3.31 | .4 | .8 | 9.2 | 1.02 |
| 10 | 1.5 | 16 | 10 | 50 | 3.62 | 4.02 | .4 | 1 | 11.2 | 1.02 |
| 12 | 1.75 | 18 | 12 | 55 | 4.82 | 5.21 | .6 | 1.2 | 13.7 | 1.45 |
| 14 | 2 | 21 | 14 | 60 | 5.62 | 5.99 | .6 | 1.4 | 15.7 | 1.45 |
| 16 | 2 | 24 | 16 | 70 | 6.62 | 7.01 | .6 | 1.6 | 17.7 | 1.45 |
| 18 | 2.5 | 27 | 18 | 80 | 7.50 | 8.00 | .6 | 1.8 | 20.2 | 1.87 |
| 20 | 2.5 | 30 | 20 | 90 | 8.69 | 9.20 | .8 | 2 | 22.4 | 2.04 |

## Implementation judgement

Use the existing development-CAD policy explicitly. Table limits are bounds, not a unique manufactured contour. Choosing `kmax`, `dkmax`, `tmax`, `rmin` and a top round within `vmax` is a declared representative geometry; it does not independently prove complete standards compliance. The source resolves the supplier R ambiguity: ISO's underhead `r` row is **minimum**. Any future migration from supplier rows should carry that semantic correction.

Length-dependent partial/full threading needs separate policy. The table's reference threaded lengths are not a licence to model every arbitrary length fully threaded and call it a standard part. Retain user-requested arbitrary length as a custom CAD option; expose standard-range validation separately when implemented.

The saved source includes lower-head bearing diameter and residual-head bounds; use the original table when those checks are added. Recess contour remains defined by the user's ISO10664 source. No different drive family or screw head family has been fabricated to fill missing references.

## Machine-readable hand-off and design policy

`series_expansion/ISO14579_rows.json` carries 13 rows, column roles, source page, residual/bearing bounds, reference thread length `b`, and the visually read full-thread preferred-length thresholds. It also records the source's length-regime formulae and a printed inconsistency: M12 × 55 lists `lg=29`, although `l−b=19` and the paired `ls=10.25` agree with 19. Do not silently present that row as internally consistent; the general formula has explicit provenance.

Recommended development geometry choices, **not unique prescribed nominal values**:

- Set plain head diameter to `dk_max_plain` and height to `k_max`; choose underhead circular radius `r_min`. Its radial extent is below `(da_max−d)/2` and axial extent below `lf_max` in every listed row.
- A quarter-circle top round of radius `v_max` has axial extent `v_max`; this is a design interpretation of the Figure 1 rounded-edge permission. The table gives an axial edge-treatment extent, not an instruction that every manufacturer's round radius equals `v`.
- Keep the bottom outer edge sharp in the development model, or limit a chosen lower-edge round/chamfer's radial loss so that the bearing diameter stays at least `dw_min`. A globally rounded cylinder changes both ends and must be checked against this bound.
- Choose socket depth `t_max` for consistency with current catalogue-based development geometry; flat-bottom residual thickness `k_max−t_max` exceeds `w_min` for each row. Any additional bottom cone changes this check.
- For the short/full-thread regime, a chosen head-to-full-thread distance `2P` satisfies the source's `≤3P` bound. Exact shoulder length and the thread fade shape are design choices. Do not call `2P` a mandatory ISO runout value.
- For long screws following the standard regime, use `lg_max=l−b` and `ls_min=lg_max−5P`; choose and document a transition between those stations. A fully threaded long override remains custom geometry.

The development choices require their own field/slice checks. These are deductions from source bounds; their inclusion here is not verification that the current nTop construction meets them.
