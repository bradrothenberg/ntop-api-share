# Drive family expansion — source boundary

Research date: 15 September 2026. Evidence tier: DOCUMENTED. No nTop measurement is claimed here.

## Implementable addition: internal T with central post

The official Camcar TORX publication contains explicit nominal **post** diameters for eleven sizes already supported by the supplied ISO 10664:1999 internal-T contour construction. These are head-standard reference dimensions, not toleranced manufacturing dimensions. Combining them with the existing informative-Annex CAD contour and a custom head is a derived CAD design, not certification of the original head standard or aerospace conformity.

The following registry deliberately retains the previously selected directly metric TMH642A values, then extends coverage from two other head sheets. Each row identifies its own dimensional source; small inch/metric rounding differences are not interpreted as tolerances.

| T size | Post diameter, mm | Original value | Camcar sheet / PDF page |
|---|---:|---|---|
| 8 | 0.584 | 0.584 mm, D REF | TMH642A / 102 |
| 10 | 0.762 | 0.762 mm, D REF | TMH642A / 102 |
| 15 | 1.016 | 1.016 mm, D REF | TMH642A / 102 |
| 20 | 1.397 | 0.055 in, D REF | TXH203B / 18 |
| 25 | 1.778 | 1.778 mm, D REF | TMH642A / 102 |
| 30 | 2.29 | 2.29 mm, C DIA REF | TMH603B / 86 |
| 40 | 2.642 | 2.642 mm, D REF | TMH642A / 102 |
| 45 | 3.175 | 3.175 mm, D REF | TMH642A / 102 |
| 50 | 3.556 | 0.140 in, D REF | TXH203B / 18 |
| 55 | 4.572 | 4.572 mm, D REF | TMH642A / 102 |
| 60 | 5.3594 | 0.211 in, D REF | TXH203B / 18 |

Inch conversions use exactly 25.4 mm/in. All three sheets show an actual central post in the recess and state its top is approximately at head-top level. This supports a flush nominal CAD post, without a quantified post-height tolerance. A centred cylinder using the table diameter is a nominal CAD interpretation of the illustrated post; it does not establish the complete formed-post root, taper or process tolerances.

All three source pages were visually read. Local visual evidence: `family_expansion/torx_p18.png`, `torx_p86.png`, `torx_p102.png`. TMH642A is a socket button head; TXH203B and TMH603B are countersunk head sheets. TXH203B and TMH603B carry April 1999 revisions.

**Automatic TR coverage:** T8, T10, T15, T20, T25, T30, T40, T45, T50, T55, T60. **No automatic post value:** T6, T70, T80, T90, T100. The searched source contains T6 driver/gauge entries, but those are not nominal recess posts. TXD702, PDF page 42, has blank tamper-resistant hole entries for T6; it cannot supply a post diameter. A user-entered post for an unsupported size is a custom override, not a sourced series member.

TXH203B and TMH642A also provide T27 post data (2.032 mm), but the supplied ISO table has no T27 nominal A/B pair. A post diameter alone does not make the T27 contour implementable. Other driver sizes likewise require their own nominal recess contour data.

## Other families: findings and missing definitions

| Family | Available primary evidence | Exact gap preventing implementation at the existing source-derived accuracy |
|---|---|---|
| External TORX E | Full TORX PDF: external head sheets and TMQ801.1/.2 receiving-configuration GO gauge drawings, pages 194–195, with gauge A/B and radii E/F. | A gauge profile is not the nominal external fastener profile. Need a full nominal external contour or an explicit official construction/offset rule. No gauge offset or internal-T scaling was adopted. |
| TORX PLUS internal IP | Full official 247-page Plus PDF obtained. Owner describes an elliptically based profile. NMQ811, page 229, gives drive-size and GO gauge part-number selection; examined head sheets give head/penetration/reference dimensions. | Ellipse axes, centres, trimming/join conditions and complete nominal recess size table or an official informative construction. A nominal major diameter or gauge identifier is insufficient. |
| TORX PLUS external EP | Plus NMQ801.1, page 225, identifies external receiving gauges. | Complete nominal EP contour definition, independently sourced from IP and ordinary E. |
| TORX PLUS tamper resistant | Plus head drawings include tamper-resistant versions (e.g. page 109). | Full five-lobe tamper-resistant drive contour. Adding a post to the ordinary six-lobe T model does not reproduce this family. |
| TORX PARALOBE | Official catalogue and public viewer metadata list UNIH12 and UNMH12 sheets; metric recess sheets are viewer pages 26–27. ISO 4579:2021 and SAE AS8538 establish applicable aerospace standards. | Actual dimensional pages were not retrieved. Public metadata's advertised full PDF URL returned HTTP 404 twice, including its publication identifier. Need UNMH12 sheets 1–2 and relevant construction/gauge definition, or full applicable standard. This is an access gap, not evidence that the profile is undefined. |
| TORX ttap | Owner catalogue/product descriptions establish a stabilising feature. | Nominal stabilising recess feature dimensions, axial form, depth and fit, plus its relationship to T size. No numerical definition obtained from an official source. |
| TORXALIGN / stick fit / AUTOSERT and other specialised variants | Owner publication distinguishes variants and provides specialised head/gauge references. | Complete variant-specific axial and contour definitions. Ordinary T with a changed label or generic taper is not supported. |

The external-gauge inward-offset idea was explicitly rejected: absent an official nominal-offset rule it would introduce a new arbitrary approximation, unlike the already disclosed ISO informative-Annex T construction.

## Primary source artefacts and access

- [Camcar public catalogue](https://netspecs.camcar.com/Library/Browse?category=Non-Confidential).
- [TORX full viewer](https://netspecs.camcar.com/Checkout_NonConfidential/TorxNonConfidentialStandards/index.html): local `Torx Non Confidential Standards.pdf`, 210 pages. File provenance/hash are in `official_sources.md`.
- [TORX PLUS full PDF](https://netspecs.camcar.com/Checkout_NonConfidential/TorxPlusNonConfidentialStandards/files/assets/common/downloads/Torx%20Plus%20Non%20Confidential%20Standards.pdf): local `family_expansion/Torx Plus Non Confidential Standards.pdf`, 247 pages, 59,134,872 bytes. Full publication available; the limitation is the dimensional content found, not a paywall claim.
- [PARALOBE viewer](https://netspecs.camcar.com/Checkout_NonConfidential/TorxParalobeNonConfidentialStandards/index.html) and its [public workspace metadata](https://netspecs.camcar.com/Checkout_NonConfidential/TorxParalobeNonConfidentialStandards/files/assets/workspace.js): metadata saved as `family_expansion/paralobe_workspace.js`. Advertised 52-page, 61,311,324-byte PDF was not retrieved. Browser surface unavailable for further viewer inspection during this pass.
- [ISO 4579:2021](https://www.iso.org/standard/80125.html) and [SAE AS8538](https://saemobilus.sae.org/standards/as8538-recess-internal-torx-paralobe-drive-dimensions-recess-gage): catalogue/status only, not full dimensional text.

Large source PDFs and page renders stay local; this note records the engineering data required for the selected CAD interpretation. No source document was modified.
