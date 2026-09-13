# Recorded September report-expansion audit

This page records the earlier nine-demo report expansion. Its counts are historical.
For the current API documentation audit, read [build 42926 audit results](API_DOC_AUDIT_42926.md).
The scanner described below remains the public-payload check; rerun it against each staged update.

The September update preserves the existing public history. Source workspaces and the separate downloadable collection remain unchanged. Private histories, raw sessions, and machine-specific configuration are excluded.

## Included and omitted material

- Nine demos contain local agent guidance, native notebooks, and scripts. Six use construction builders; F-16, A-12, and F-Cat replay saved graphs.
- Seventeen native notebooks include F-16 R6, A-12 R33, F-Cat geometry and meshing, and the finite-edge Fury snapshot.
- The 27-report catalogue includes Jet20 requirements and later reviews, both F-Cat reports, cross-CAD comparisons, B52 history, and the full I6 Astra reference.
- Reference photos and photographic composites remain only in the separate downloadable collection. Visible images, JavaScript image maps, and download attachments were reviewed together. The excluded-image digest list guards against reintroduction.
- Large meshes, movies, animated previews, solver runs, caches, binaries, license files, and workspace backups are omitted.
- Jet20 retains the assembled and exploded nTop UI screenshots with capture and model hashes.
- B52 retains its artist-model source, authors, GPL-2.0 license, current construction, and historical R2-R6 saved graphs.
- Reports use local figures, viewer code, and fonts. They need the complete repository folder for offline viewing.

## Audit method

The scanner checks the exact staged file list, native JSON and binary chunks, UTF-16 strings, image metadata, data URLs, nested image maps, and compressed viewer payloads. Repeated identical payloads are scanned once by SHA-256.

Checks cover recognized credentials, private keys, internal addresses, personal home paths, old workspace paths, retired dependencies, missing local links, prohibited media, and individual files above 50 MiB. Photo exclusions apply to decoded payloads as well as standalone files.

All native containers must roundtrip exactly. [Publication records](model-publication.json) identify path-only edits. I6 has 13 portable export paths; F-Cat meshing and finite-edge Fury each have two. Working-copy preparation resolves these under the recipient checkout.

[Recipe correspondence](recipe-publication.json) compares 697 saved variables against the three native snapshots, including functions, connections, types, properties, literals, and units. Browser checks exercise local figures, controls, downloads, and desktop/mobile layouts. These are packaging and recorded-graph checks, not new geometry or solver runs.

The licensed custom nTop build remains an external prerequisite. A bounded audit cannot detect every possible secret format. See [release verification](RELEASE_VERIFICATION.md) and [report notes](REPORTS.md) for the exact scope.
