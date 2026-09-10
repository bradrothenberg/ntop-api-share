# Public release audit

Scope: the new public snapshot only. This repository uses fresh Git history.
Source workspaces remain unchanged. Private histories, raw session notes, and machine-specific configuration are excluded.

## Included and omitted material

- Six demos contain standalone builders, local agent instructions, HTML reports, and 12 native notebooks.
- Jet20 includes the original assembled and exploded nTop UI screenshots, with capture and model hashes.
- Large exported meshes, movies, solver runs, caches, application binaries, application license files, and source-workspace backups are omitted.
- Unverified reference notebooks and reference photographs are omitted. Fury uses numerical shape controls and native geometry.
- DDGX retains authored inferred geometry. Its external concept image is linked, not redistributed.
- B52 retains the upstream artist-model source, authors, full GPL-2.0 license, and complete editable derivative recipe.
- Reports retain compact authored images and the jet viewer. Embedded media is included in the size and payload audit.
- Commercial fonts are not bundled. Reports use local fallback fonts and work without network requests.

## Automated and manual checks

The scanner checks the exact Git file manifest after staging. It inspects text, native-file chunks,
binary and UTF-16 strings, embedded data URLs, compressed viewer geometry, and image metadata.
Checks cover recognized credential formats, private keys, credential assignments, internal addresses,
personal home paths, source-workspace paths, retired-project imports, missing links, and files over 50 MiB.
All native containers must roundtrip byte for byte. model-publication.json records the native path edits and hashes.
Only the original I6 notebook needed path changes: 13 export paths became repo:// references.
Working-copy preparation resolves those references into the recipient checkout and preserves source files.

Native screenshot provenance and model hashes are tested. Report images and browser layouts receive visual review.
Historical notes distinguish their recorded revisions from this package's new offline checks.

This is a bounded content and provenance review, not a guarantee that every possible secret format can be detected.
No fresh native geometry evaluation is claimed. The licensed custom nTop build remains a separate prerequisite.
The exact release checks and results are in [RELEASE_VERIFICATION.md](RELEASE_VERIFICATION.md).
