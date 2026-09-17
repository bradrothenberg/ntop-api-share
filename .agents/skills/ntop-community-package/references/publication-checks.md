# Publication checks

A published package is downloaded by someone who cannot rerun anything. The only thing they can check is what the folder says about itself. `publication-checks.json` is that statement, and its value comes entirely from what it refuses to claim.

## What the file records

The published aerospace packages use this shape, one entry per model:

```json
{
  "scope": "Offline publication preparation; no new native execution",
  "models": [
    {
      "file": "propeller-eight-inch.ntop",
      "source_sha256": "6a5845a7...",
      "published_sha256": "5256ae8a...",
      "bytes": 21689386,
      "changed_chunks": ["index"],
      "relative_export_filenames": ["propeller.stl", "spinner.stl"],
      "source_unchanged": true,
      "geometry_graph_and_binary_payloads_unchanged": true,
      "new_native_execution": false
    }
  ],
  "cover_sha256": "4c64b9b6...",
  "source_commit": "92f13bc0a873aacba62526ee43e9e6895ef051f8"
}
```

`source_sha256` and `published_sha256` differ in that example, and `source_unchanged` is still true. The two are not contradictory: `source_unchanged` says the audited file in the source repository was not modified by publication, not that the bytes match. Publication produced a new file; the original still hashes to its recorded value. Say which one you mean.

`new_native_execution: false` is the load-bearing field. Offline packaging checks establish that a file was copied, that its container still parses, and which parts of it moved. They establish nothing about geometry. If you did not open the published file in nTop and evaluate it, the package may not claim that the geometry was verified after publication.

The bundled stager writes a `changed_chunks_are_state_only` boolean beside `changed_chunks`, computed rather than asserted.

## The container, measured

A `.ntop` file is a `MAGIC%$1` container: a count at byte 8, a directory, then chunks of `MAGIC@@9` plus a 16-byte type, a 16-byte name, a payload size, and the payload. `scripts/organize_notebook.py` and `scripts/collapse_saved_notebook.py` in this repository document and parse it; the stager reuses the same offsets and verifies that the walk consumes the file exactly and that the chunk count matches the directory.

A save from build 6.1.0-rc 42926 carrying seven custom blocks exposes 70 chunks:

- `main`, the function graph.
- `inp0` to `inp12`, the top-level inputs.
- `sf0` to `sf6` with their `sf<N>inp<M>` entries, one group per sub-function.
- `cache`, `customColors`, `open`, `res`, `sections`, `tools`, `view`, `viewport`.

The stager treats that last group as saved state and everything else as graph or input data. A diff confined to the state group means the presentation changed. A diff touching `main`, any `inp`, or any `sf` means the graph or an input value changed, and the README owes the reader a sentence about what and why.

Rewriting an export destination changes an input, not the presentation. Expect `changed_chunks_are_state_only` to be false after that edit, and say in the README that destinations were reduced to filenames.

The published packages record `changed_chunks: ["index"]`. No chunk of that name appears in the directory of a 42926 save, so either the name comes from another build or that tooling reported the container directory rather than a chunk. Do not copy the value. Record what your own comparison produced, between two files from the same build.

## Copy bytes, do not re-save

Produce the published file by copying the audited file, or by making one deliberate edit in nTop and saving once. A convenience re-save rewrites the state chunks, sometimes the cache, and leaves you unable to say which differences were intended. If that happens, go back to the audited file and start again rather than widening the claim to cover the noise.

Keep a package-level `.gitattributes` containing `* -text` whenever the folder records hashes or byte counts. Without it the repository's `text=auto` policy rewrites line endings on checkout and a recorded hash stops matching on a different platform. This is not hypothetical: the catalogue's own byte-sensitive folders carry that file, and so does `demos/torx` in this repository.

## The single verdict file

Tier-three packages add `publication-validation.json`: one status, one scope sentence, the counts that were checked, and a notes field. The aircraft package reads `"status": "PASS"`, `"scope": "Offline publication checks; no new native execution"`, then counts of models, reports, preserved function chunks, checked links, and reviewed figures. It is the file a reviewer reads first. Keep its scope sentence identical to the scope in `publication-checks.json`, and keep a failed study inside the package rather than deleting it to reach PASS.

## The claim ledger

Before writing the README's evidence section, sort every statement you intend to make into one of four rows, and write only the ones you can name a file for.

| Class | Established by | Example claim |
|---|---|---|
| Recorded native execution | A run on a named build, with its receipt in the source repository | Geometry probes passed on 42926 |
| Offline packaging check | Hashes, container parse, chunk diff, link resolution | The published notebook is the audited notebook with two inputs changed |
| Recorded source evidence | Evidence files carried over from the source demo, with their original scope | Recipe check at 8 of 8 against nTop's own recording |
| Unverified | Nothing in the folder | Manufacturability, load capacity, public-release compatibility |

An unverified row is not forbidden. It is forbidden to write it as though it belonged to one of the other three.
