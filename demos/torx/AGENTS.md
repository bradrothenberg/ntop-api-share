# Torx: agent instructions

Read the root AGENTS.md, the shared Notebook API skill, and this demo's README.md.
A parametric fastener ported from a sibling source project onto this repository's
recipe harness, and the one case in this collection that the node-by-node live
transport cannot express at all.

- `scripts/` holds the standalone source. `inputs/source_tables/` holds the three
  ISO row tables and is the only place a dimension is written; `torx_catalogue.py`
  reads them and nothing else invents a number.
- `torx_spec.py` is the YARDSTICK and runs with no nTop. Never change a predicted
  value to match a measurement; if they disagree, one of them is wrong and it must
  be said which. Three of its errors were found by `check_spec.py` before any
  dispatch, which is what that file is for.
- `torx.py` is the single graph source. `build_torx.py` drives it offline against
  `torx_backend`; `torx_verification.py` drives the same functions into the three
  live recipes. Change a block in one place only.
- `check_recipe.py` asserts the offline recipe equals nTop's own recorded recipe
  for this graph once identifiers and exporter-only keys are normalised. Keep it
  at 8 of 8 after any graph edit.
- Build from the repository root with `uv run --locked python scripts/build.py torx`.
  `make_figures.py` needs the `render` dependency group.
- `**/output/` is not published. A receipt the report cites goes through
  `publish_evidence.py` into `evidence/`, with machine paths reduced to file names.
  `models/` carries the two deliverables only: the figures notebook stores the
  absolute paths of its slice archives, so it stays in `output/`.
- This demo does NOT have a live-API mirror backend, and must not be described as
  if it did. Build 42926 has no live method that creates a custom block, so the
  seven definitions can only arrive through `import_recipe`. That is the finding,
  not a limitation of the port.
- The V2 example arrives as a RECIPE, never as a copied notebook. The released
  `Torx_Example.ntop` fails its own `manifest.json` (15,233,693 bytes on disk
  against 1,544,256 signed: a reconvert cached its solve into the file), so the
  demo imports `inputs/recorded/torx_example_recipe.json` and lands its own.
  `check_example.py` re-checks both the readback and the manifest every run.
  Its fifteen definitions include two different blocks both named `Torx`; the
  import keeps both, and nothing here may refer to one of them by name alone.
- A choice input cannot be set from the live API on this build. The verification
  band calls `Torx Local Development` directly with integer literals; the public
  Choice Lists are checked by reading back the four selection variables.
- A block in error reports `e_DIRTY` with no error field on build 42926. Read the
  value; do not wait on the state. The gate cases take their verdict from the pair
  (state, readable value): a refused configuration must not produce a number.
- Rasters are read with the slice-index law MEASURED on the build in hand, not the
  one recorded on 6.0.3. `make_figures.py` re-derives it from the `calibration`
  stack every run and reports both candidate brackets.
- Recorded results are for build 42926, PID 28232, 17 September 2026. Offline
  checks and the recipe comparison do not prove native execution.
- Keep the standards PDFs and the source page scans out of this repository. The
  origin project retains them; only the transcribed row tables and the reviews
  are published here.
- Do not control the user's existing session.
