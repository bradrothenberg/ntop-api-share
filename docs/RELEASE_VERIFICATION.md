# September report expansion verification

The public update contains nine demos, seventeen native notebooks, and twenty-seven reports. The existing public history is preserved. Reference photographs remain only in the separate downloadable collection.

The exact staged files were exported to a separate recipient folder with spaces. No original workspace imports were used. The locked dependency installation, all nine build/replay jobs, and all 43 tests passed without skips. Native working-copy preparation resolved all 17 export paths under that recipient folder. Imports for the three new demos were staged, but not executed inside nTop.

The three saved recipes match all 697 native variables by functions, connections, properties, types, literal values, and units. Tests verify the Fury wing, horizontal-tail, and fin controls are each 12.7 mm full thickness. Mesh and export operations in that notebook remain paused.

All 27 reports, the catalogue, nine demo entry pages, and the retained Fury baseline page passed offline browser checks: 38 pages total. Checks covered image loading, SVG images, available view controls, attachments, and desktop/mobile layouts. Every F-16 slide was checked. The pages produced no script errors, failed local requests, or network dependencies during these checks.

The staged content audit found no privacy, credential, excluded-photo, native-container, media-size, or local-link findings. It includes nested image maps and decoded downloads. The 31 excluded reference-image digests are checked against public files and decoded payloads. The original downloadable ZIP retains its prior SHA-256.

[Expansion receipt](report-expansion-verification.json) | [Report manifest](../reports/manifest.json) | [Public audit scope](PUBLIC_AUDIT.md)

These checks establish packaging and saved-graph correspondence. They do not establish new native geometry evaluation, solver validation, hardware qualification, or compatibility with a different nTop build.

---

# Initial six-demo release verification

Verified on 10 September 2026 in an independent Git clone whose folder name contains spaces.
The source and clone files matched byte for byte. No private source checkout was used by the test commands.
The old nTop and Python environment settings were cleared before setup.

## Results

- Locked dependency installation and bootstrap passed with host Python 3.12.11.
- All six complete recipe builders passed. Jet20 also passed its six cycle and geometry unit checks.
- All 30 handoff tests passed, with no failures or skips.
- All 12 native files parsed and roundtripped exactly. Collapse tests preserved non-UI chunks and source files.
- Preparation made separate working notebooks. The 13 portable I6 export paths resolved into the recipient checkout.
- The staged B52 import script was generated successfully. It was not executed inside nTop during this audit.
- Both PowerShell scripts passed syntax checks.
- The clean-checkout content scan reported no findings across 211 files before these release receipts were added.
- The scan inspected 76 embedded payloads, including compressed jet geometry, and 92 image payload occurrences.
- All six reports loaded offline with no script errors, missing images, external requests, or horizontal overflow at 390 px.
- Jet assembly modes produced different rendered views. B52 comparisons, DDGX tabs, and report themes responded correctly.
- Published report images and desktop/mobile layouts received visual review. Original jet UI captures retain matching hashes.

| Demo | Variables | Expressions | Dependency references |
|---|---:|---:|---|
| i6 | 1106 | 1473 | Pass |
| i6-astra | 254 | 4276 | Pass |
| jet20 | 532 | 4059 | Pass |
| fury | 373 | 1909 | Pass |
| b52 | 409 | 553 | Pass |
| ddgx | 123 | 776 | Pass |

See [machine-readable checks](release-checks.json), [browser receipt](report-verification.json),
[native publication edits](model-publication.json), and [audit scope](PUBLIC_AUDIT.md).
The code/input manifest in the machine-readable receipt identifies the exact tested implementation.

## Reproduce the offline checks

Run from the repository root:

```powershell
uv sync --locked
uv run --locked python scripts/prepare.py --models
uv run --locked python scripts/smoke.py
uv run --locked pytest -q
uv run --locked python scripts/audit.py
```

These checks validate packaging, path relocation, dependency closure, and saved-file integrity.
They do not establish fresh native geometry evaluation, engineering qualification, or compatibility with another nTop build.
Native values and images in the reports remain recorded evidence for their stated revisions.
The licensed Notebook API custom build is required for the in-application checks in [setup](SETUP.md).
