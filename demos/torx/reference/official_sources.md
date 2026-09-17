# Torx — official source evidence

Research date: 15 September 2026. Evidence tier: DOCUMENTED, not ntopcl-measured.

## Result

The official Camcar non-confidential TORX standards are publicly accessible and were downloaded in full. They supply useful head, driver, and inspection data, but the examined internal-T sheets do **not** supply a complete nominal recess contour. A reference diameter is not a profile definition. No radius ratio, spline, or circular-arc approximation has been adopted.

The remaining decisive source is the complete ISO 10664:2014, including its contour Annex A and gauge Tables 3–5, or the corresponding fully dimensioned Camcar recess/production gauge specification. This is a specific dimensional gap, not a claim that TORX documentation is inaccessible.

## Primary sources and access

| Source | Access and what it establishes |
|---|---|
| [ISO 10664:2014](https://www.iso.org/standard/63207.html) | Official abstract/status read. Current edition 3, confirmed in 2024. Defines internal hexalobular geometry and inspection. Explicitly not a manufacturing standard. Complete dimensional text not obtained. |
| [NEN-EN-ISO 10664:2014](https://www.nen.nl/en/nen-en-iso-10664-2014-en-200510) | National standards body catalogue read. Identifies gauge Tables 3–5 as the contour definition and Annex A as drawing information. Complete PDF is offered on purchase; no purchase made. |
| [DIN Media ISO 10664](https://www.dinmedia.de/en/standard/iso-10664/224734148) | Official distributor lists current 2014 edition and complete publication. Catalogue, not full dimensional text. |
| [Camcar TORX product page](https://camcar.com/2021/01/19/torx/) | Owner's page distinguishes internal, external, tamper-resistant, TORXALIGN, and other configurations. Links directly to NetSpecs. Marketing describes benefits; it cannot define missing contour coordinates. |
| [Camcar non-confidential catalogue](https://netspecs.camcar.com/Library/Browse?category=Non-Confidential) | Read in normal browser without login. Lists separate TORX, TORX PLUS, TORX PARALOBE, and TORX AEROSPACE publications. TORX catalogue revision shown as 26 August 2026. |
| [Camcar TORX full viewer](https://netspecs.camcar.com/Checkout_NonConfidential/TorxNonConfidentialStandards/index.html) | Complete 210-page publication, with a public PDF download control. Source for the local PDF below. |

### Local source artefact

- File: `Torx Non Confidential Standards.pdf` beside this note.
- Size: 136,669,757 bytes; 210 pages.
- SHA-256: `064839b1565445a1432f38da18a47ab86bede9ab023747a00eb931b38a343db7`
- [Exact observed PDF link](https://netspecs.camcar.com/Checkout_NonConfidential/TorxNonConfidentialStandards/files/assets/common/downloads/Torx%20Non%20Confidential%20Standards.pdf?uni=2181fb4bb0794e05e0cac17e2555b33c).
- Keep the PDF local; it is a source reference, not a deliverable or a file to add to a public repository. Pages carry the owner's redistribution notice. Each individual sheet has its own issue/revision date; the catalogue's recent date does not revise every historical sheet.
- Initial web-tool fetches returned cache errors. The ordinary browser succeeded. A shell download required network escalation and succeeded. No login, registration, contact, purchase, or acceptance of an agreement was performed.

## Internal T: precise page map and unresolved geometry

All page numbers below are **one-based PDF page numbers**, not printed sheet identifiers. Text extraction is OCR and visibly corrupts some digits. Tables must be checked against the scanned page before any value is admitted into a size registry.

| PDF page | Printed sheet | Finding |
|---|---|---|
| 75–76 | TMH index | Separates head styles and references their individual dimensional sheets. It does not establish one universal recess depth for each T size. |
| 77 | TMH-2.0 | Recess no-go penetration/fallaway specification. This is axial inspection information, not a nominal two-dimensional profile. |
| 170 | TMD index | Driver/bit specification index. |
| 172 | TMD-702, revised October 2002 | Internal driver bits. Provides reference A, maximum B, minimum engagement G, and tooling information. These are **driver** data, not the recess profile. No complete lobe-radius definition on this sheet. Raster saved as `camcar_p172.png`. |
| 184–185 | TMQ index | Metric inspection/gauge catalogue. |
| 187 | TMQ-0 sheet 2, revised April 1999 | Manufacturing inspection points to **TMF-804** for the go penetration and no-go fallaway elements. That sheet is not listed in this non-confidential volume's TMQ contents; its complete dimensional definition has not been obtained. |
| 188 | TMQ-0 sheet 3, revised September 1994 | Final/receiving inspection identifies profile dimensions A and B and radii E and F, then refers to TMQ-811 and TMQ-812. It contains an inspection sketch, not numerical E/F tables. Raster saved as `camcar_p188.png`. |
| 198 | TMQ-805.4, revised January 2002 | **Driver-bit receiving inspection gauge** with multiple hole dimensions. This must not be treated as the nominal recess contour. |
| 201 | TMQ-811, revised August 1981 | Final/receiving internal-head go gauge. Reference A and gauge-series numbers are given, plus optional tamper-resistant hole information. **No B, E, F or nominal contour tolerances.** Visual inspection confirms this limitation. Raster saved as `camcar_p201.png`. |
| 202 | TMQ-812 | Fallaway gauge, a separate inspection object. |

Example of why semantics matter: the T20 driver reference A on TMD-702 is 3.840 mm; the T20 final go-gauge reference A on TMQ-811 is 3.89 mm. Neither number by itself is a complete nominal recess definition. Do not mix these tables into one profile.

### Exact missing data before a source-derived internal-T build

1. The accepted nominal contour's arc/curve construction, with all size-dependent parameters and precise definition of major/minor diameter.
2. The nominal-to-limit relationship: recess versus go/no-go gauge versus driver, and any clearance or profile tolerances.
3. Whether the requested CAD primitive is a nominal recess cutter or another specified inspection envelope.
4. For a complete screw, the selected head/product standard determines penetration, lead-in, bottom detail and thread/head dimensions. A general TORX family designation does not settle those.

ISO 10664 Annex A and Tables 1–5 are the named next reference for a nominal internal hexalobular CAD feature; Camcar's full corresponding geometry sheets remain the alternative for branded owner geometry. Neither should be silently substituted for the other.

## Other families: source map, not implemented coverage

- [Camcar TORX PLUS](https://camcar.com/2020/12/15/torx-plus/) identifies elliptically based geometry. Its external tools are not compatible with external TORX. The basic T profile cannot simply be reused for Plus.
- [ISO 4579:2021](https://www.iso.org/standard/80125.html) is the published aerospace TORX PARALOBE internal-drive geometrical/gauging/engineering standard. Only abstract/status obtained.
- [SAE AS8538](https://saemobilus.sae.org/standards/as8538-recess-internal-torx-paralobe-drive-dimensions-recess-gage) is the TORX PARALOBE recess/gauge standard, reaffirmed 4 May 2026. Only abstract/status obtained.
- [ISO/DIS 18700](https://www.iso.org/standard/92412.html) concerns aerospace TORX PLUS internal-drive geometry, gauging, technical and quality requirements. At the checked date it is **under development**, stage 40.99, not a published ISO standard.
- External E, tamper-resistant variants, Plus, Paralobe and TTAP need their own verified dimensional packages. Their appearance in the catalogue is not proof of dimensional coverage in this implementation.

No patent figure, secondary sizing chart, Wikipedia value, or reconstructed picture was used as a dimensional authority. The task's geometry has not been labelled aerospace qualified; exact CAD geometry and qualification of a manufactured fastener are separate claims.
