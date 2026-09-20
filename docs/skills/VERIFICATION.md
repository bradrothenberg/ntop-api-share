# Skill package verification

The public package was checked on 20 September 2026 against base commit `1723796`.
It contains instructions, references, paper figures, and an input-preparation helper.
No nTop, CFD solver, or cloud job was run for this update.

| Check | Result |
|---|---|
| Original paper inventory | All 18 named skills present |
| Repository skill metadata | All 20 entries pass the supplied skill-creator validator |
| Future proposals | Ten briefs remain outside the installed skill tree |
| Existing skills | All six pre-existing skill directories remain unchanged |
| Offline model preparation | Pass; working copies and portable paths prepared locally |
| Demo source smoke checks | All 11 source/replay checks pass |
| Repository tests | 212 passed, including 13 input-preparation tests |
| Assembly pilot | Offline recipe and reference checks pass; no native execution |
| KestrelSAT example | Saved graph, manifest, and container checks pass |
| Civil aircraft example | 78 models and 10 reports pass snapshot integrity checks |
| Public-content and link audit | Zero findings across 1,331 tracked files and 1,687 local links |
| Paper figures | Two 7 by 9 inch PDF pages; vector SVGs; original 450-dpi PNGs |

The public audit scanned 685 embedded payloads, two gzip payloads, and 617 images.
The source receipt retains logical filenames and SHA-256 identities without private workspace paths.
The native-container checks inspect saved data. They do not reevaluate geometry or establish solver accuracy.

The figure source regenerated both pages in ignored local output. PDF text matches the packaged originals.
Both rendered pages were visually reviewed. The 18-skill figure scope and ten proposal labels remain explicit.
The retained PNG exports use a different rasterizer from the portable regeneration script; minor antialiasing differences are expected.

The typed input helper was checked for factorial and paired grids, units, vectors, booleans, enums, and selective output-path changes.
Tests also reject unknown or duplicate inputs, malformed values, unequal paired axes, excessive task counts, and output-file overwrites.
The helper prepares inputs only. It does not launch nTop or validate a native run.

The continuous-integration workflow runs the inventory check with the existing offline suite and public audit.
