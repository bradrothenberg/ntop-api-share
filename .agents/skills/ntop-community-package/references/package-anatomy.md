# Package anatomy

Three shapes exist in the catalogue. Pick the smallest one that carries the claim you are making, then fill it completely. A half-filled larger shape reads worse than a complete small one.

## Naming

The catalogue README requires kebab-case slugs for every file: lowercase, hyphens, no spaces. `csv-airfoil-sdf.ntop` is correct, `CSV Airfoil SDF.ntop` is not. Rename on the way in. A demo under `demos/` may hold `Torx.ntop`; the package holds `torx-custom-blocks.ntop`, and the README names the new file, not the old one.

Two files in one folder may not differ only by case. Git records both, Windows and macOS checkouts receive one, and the clone reports a collision. This already happened once in the catalogue.

## Tier one: a reusable block

```
packages/<author>/<id>/
  manifest.json
  README.md
  <id>.ntop
  cover.png
```

`ntop/gear-profile` is the reference. Its README is 33 lines: title, one sentence, an installation section that clones the catalogue and names the folder, an inputs table with name, type and description, an outputs table, and a license line. The descriptions carry the engineering content, including typical values and what happens when a value changes. That is the whole quality difference between a usable block and a dumped file.

## Tier two: an audited model

```
packages/<author>/<id>/
  manifest.json
  README.md
  LICENSE
  cover.png
  <id>.ntop
  <supporting>.ntop
  publication-checks.json
```

`bradrothenberg/propeller-eight-inch` is the reference: 45 README lines around one 21 MB notebook. It adds three things over tier one. A recorded-build statement that explains why `ntopVersion` cannot carry the real build. An export-path statement saying destinations were reduced to filenames and the reader must choose an output folder. A link to the exact source commit in `ntop-api-share` that holds the construction and verification scope the package omits.

## Tier three: a bundle with evidence

```
packages/<author>/<id>/
  .gitattributes            * -text, to hold recorded bytes across platforms
  manifest.json
  README.md
  LICENSE
  cover.png
  <id>.ntop                 the declared packageFile
  <many>.ntop               grouped by revision or part in the README catalogue
  evidence/*.json, *.csv    measured results, each with its own scope
  notes/*.md                per-study source notes
  references/*.csv, *.dat   input data the model reads
  reports/index.html        report catalogue
  reports/*.html            one file per study, offline
  reports/assets/<sha256>.png
  publication-checks.json   per-file source and published hashes
  publication-validation.json  the single PASS or FAIL record with its scope
```

`bradrothenberg/civil-research-aircraft-rev-g` is the reference: 74 notebooks, eight reports, 82 content-addressed images, 172 README lines. Report assets are named by the SHA-256 of their content, so an image cannot be silently swapped and two reports can share one file.

## README section order

Tier two and three follow the same order. Keep it.

1. `# Title`, matching the manifest `title`.
2. `**Built with <model>.**` when an AI model helped, matching the `aiModel` field.
3. One paragraph saying what the package is and what is in it, with counts.
4. The cover image, embedded by its relative filename, with alt text that names the subject rather than repeating the word cover.
5. `## Start here` or `## Installation and use`: numbered steps. Download and keep the folder together, open the reports, open the named notebook in the stated build, save a working copy before editing, then the one rule that prevents the most common mistake in this particular model.
6. The recorded-build paragraph. Which build produced the files, that the minimum-version field cannot encode it, that public-release compatibility was not re-tested, and that the application is not included.
7. The external-file paragraph when the model reads or writes files. Where the supplied inputs are, what to do when nTop asks for a missing one, and that export destinations are filenames rather than workstation paths.
8. `## Inputs and outputs`: a table. Tier one uses name, type, description. Tier two uses direction and contents. Tier three uses item, editable data, and result and limit. The limit column is the one that matters; it is where a nominal feature is called nominal.
9. `## Files` or `## Native model catalogue`: every shipped file as a relative link, grouped when there are more than a handful.
10. `## Evidence and source` or `## Publication checks`: what the recorded checks establish, what they do not establish, a link to `publication-checks.json`, and the permalink to the source commit.
11. `## License` or `## License and credits`: the identifier, a link to `LICENSE`, and third-party attribution that the package does not override.

## The limit sentence

Every good package README contains at least one sentence that reduces its own claim. The propeller says the retention geometry is a modeling example and not a safe-speed qualification. The aircraft says the recorded probes establish geometry and graph checks but not structural capacity, and leaves the failed fork stress screens visible. Write that sentence deliberately. A package with no limit sentence is either trivial or overclaiming, and a reviewer cannot tell which.
