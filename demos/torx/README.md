# Torx: a seven-block assembly through one import call

A complete parametric Torx screw, ported from the source project's JavaScript
builders onto this repository's offline recipe harness and imported into a live
nTop notebook in a single call.

Build under test: `nTop 6.1.0-rc commit-050d0c7cdc8e412c3a35298bc5a89dc8a6da864d`,
`D:\ntop_dev\nTop-6.1.0-rc-42926\ntop.exe`, PID 28232, launched 17 September 2026
01:32:17. Transport: `scripts/ntop_tcp.py` on `127.0.0.1:2323`, interpreter PID
verified on the connected socket before every dispatch. Receipts under
`.local/torx-run-001` to `torx-run-006` and `output/`.

[Open the report](reports/index.html).

## Why this demo exists

The recorded API surface for build 42926 says the API edits existing custom
blocks and lists no method that creates or imports one. Read literally, that puts
this screw out of reach: it is an assembly of **seven referenced custom blocks**,
and no sequence of `add_block` and `connect_block_property` calls can bring a
definition into existence. A node-by-node transport cannot express this graph at
any cost in round trips.

It is reachable through the recipe. A complete recipe carries its definitions in
`imports` and calls them by uuid, and `import_recipe` takes the whole thing at
once.

**Measured: importing the recipe into a notebook holding zero custom blocks left
it holding seven**, named exactly as the recipe names them, in one call and
32.7 s for a 1,451-node graph.

## What it builds

Eight blocks. The first five are leaves, the sixth assembles them, the seventh
places the result, and the eighth is the public interface.

| Block | Inputs | Body | Nodes | What it is |
|---|---|---|---|---|
| Countersunk Head 2013 | 4 | 7 | 20 | revolved 90 degree cone with a flat rim |
| Torx Internal | 4 | 39 | 216 | six alternating tangent arcs, extruded |
| Screw Head | 6 | 11 | 36 | revolved cylindrical head, two circular rounds |
| Pan Head | 6 | 13 | 42 | spherical crown, cylindrical side, underhead fillet |
| Metric Thread Kernel | 6 | 11 | 29 | analytic helical field, flat crest and root |
| Torx Local Development | 9 | 49 | 998 | source-row selection, validity gate, assembly |
| Place Screw | 5 | 30 | 100 | rigid placement into a surface frame |
| Torx | 13 | 6 | 10 | the public block: four native Choice Lists |

## What the port does not reach

This demo ports the **thirteen-input** public block. The released V2 compact assembly, carried here as
`inputs/recorded/torx_v2_compact_recipe.json`, exposes **eighteen**. The five it adds are a batch
placement system the port has no equivalent for:

| Input | Type | What it does |
|---|---|---|
| Placement mode | choice | Surface placement from the tangent-plane normal at the original point, or explicit placement from the untilted axis. |
| Reference Body | implicit | The host body the screws are placed against. |
| Tilt X, Tilt Y | list<real> | Applied before flush; flush then follows the final tilted axis. |
| Flush | list<bool> | Moves each screw in until its outer head envelope touches the tangent plane. |

The released assembly also returns a **paired container**, N detailed screws followed by N filled moulds,
read through two small extractor blocks (`torx_screws_recipe.json`, `torx_outer_moulds_recipe.json`)
rather than a second notebook output. Do not describe the ported thirteen-input block as the released
screw: they are different graphs, and the released one is what the catalogue package ships.

The example's Reference Body arrives from a file, and that path is container state rather than recipe
data. See F13 in [FINDINGS_RC42926_LIVE.md](../../FINDINGS_RC42926_LIVE.md): a recipe round trip
reproduces the graph and silently drops the input file. `inputs/nT-0008-Ex.implicit` is the body the
released example reads.

The recess contour is not a six-lobed sine wave. The convex lobe radius is
chosen at 0.1 A from the supplied informative Annex A, and the concave radius is
solved so the two arcs are externally tangent, which keeps the declared A and B
dimensions exact at once.

## Controls

- **Drive family**: Internal Torx, or the tamper-resistant derivative with a
  sourced Camcar round post.
- **Screw series**: Cylindrical ISO 14579:2011, Pan ISO 14583:2011, Countersunk
  ISO 14581:2013 (historical).
- **Metric size**: 14 labels spanning 31 series and size combinations.
- **Drive size**: Automatic, or one of 16 rows from T6 to T100. Eleven of those
  have a sourced tamper-resistant post.
- **Length**: underhead to tip for raised heads; total length including the head
  for countersunk, which also uses the flush top face as its datum.
- **Override shank / Shank radius** and **Override Torx / Torx radius**: two
  independent scalings. A custom size no longer carries a standard metric thread
  designation.
- **Insertion Point, Axis, Tangent Reference, Clocking Angle**: the placement.
  No fallback is defined for a zero axis or a tangent parallel to it; both are
  refused rather than guessed.

## The port, checked against nTop's own recipe

The source project authored this screw in JavaScript and converted each block
with `ntopcl`. nTop then wrote back what it believes the graph is, and that
readback is kept here as `inputs/recorded/torx_recorded_recipe.json`. `torx.py`
rebuilds the same eight blocks in Python from the same ISO source tables.

`check_recipe.py` compares the two. Identifiers are the only thing allowed to
differ, because nTop mints its own on every conversion; the exporter also writes
a `type` key on call nodes and an empty `dimension` on dimensionless inputs,
which the recipe form omits. Everything else must agree exactly.

**8 of 8 blocks identical**, across 1,451 graph nodes: every function
identifier, every literal value and unit, every input index, every reference,
every import and every `cbRefs` entry.

## The yardstick

`torx_spec.py` is a closed-form mirror with no nTop import, frozen before the
first dispatch. It predicts the **surface**, not interior distances: the composed
field is not a Euclidean signed distance and is not claimed to be one.

Each prediction is a point where any correct field must read zero, plus the sign
of the field two micrometres either side of it along the outward normal. A
constant zero field would pass the first test and fail the second.

`check_spec.py` checks the mirror on its own terms before anything native runs:
**627 checks at first, 748 after the placement configurations were added, 0
failed, worst disagreement 5.1e-14 mm.** It recomputes the concave arc radius by
bisection for all sixteen drive sizes, asserts external tangency and sixfold
symmetry, recovers the declared A and B exactly, verifies the thread's axial and
angular periods and its flank slope, and confirms the placement frame is
orthonormal, right-handed and rigid.

Two errors in the mirror were found by these checks and fixed before any
dispatch: the underhead fillet's outward normal pointed the wrong way, and the
recess floor and void samples sat inside the tamper-resistant post. A third was
a badly designed test, not a mirror error: sampling either side of the contour's
arc handover measures the step size, not continuity, because the contour has a
non-zero slope there. The two branches are now evaluated at the handover angle
itself.

## Result

**479 of 479 field samples pass**, across eight configurations: 146 boundary
points and 333 sign probes. Every prediction was written before the run.

| Configuration | Metric | Drive | Boundary | Sign | Worst residual |
|---|---|---|---|---|---|
| default | M3 x 0.5 | T10 | 18 | 41 | 5.87e-11 m |
| oblique | M3 x 0.5 | T10 | 18 | 41 | 5.01e-10 m |
| rotated | M3 x 0.5 | T10 | 18 | 41 | 5.93e-11 m |
| farfield | M3 x 0.5 | T10 | 18 | 41 | 7.71e-08 m |
| m8 | M8 x 1.25 | T45 | 18 | 41 | 1.31e-10 m |
| t25 | M5 x 0.8 | T25 | 18 | 41 | 7.28e-11 m |
| tamper | M5 x 0.8 | T25 | 20 | 46 | 7.28e-11 m |
| custom | M3 x 0.5 | T10 | 18 | 41 | 1.15e-10 m |

The gate is 1e-7 m at a boundary point. The worst residual over the whole set is
7.71e-8 m, and it belongs to the configuration placed 1.48 m from the origin.

**All four Choice Lists resolve to the source identifier the assembly expects.**
A choice input cannot be set from the live API on this build, so the band calls
the local assembly directly with integer literals the recipe carries; the public
selectors are checked by reading back the four selection variables the root body
computes.

**7 of 7 validity-gate cases.** A valid control builds and reads
-5.421e-17 mm at the recess lobe. Six invalid configurations refuse to evaluate:
a tamper-resistant T6 with no sourced post, a recess that would break out through
the head side, two lengths that leave no threaded shank, an M12 pan screw whose
source table stops at M10, and a countersunk recess deep enough to break through
the cone.

## The V2 example: fifteen definitions, two of them called Torx

The origin project also ships a wired example on top of this screw: one
configured Torx call feeding two named list extractors and two native Boolean
consumers, with mould outputs and flush placement. Its recipe is carried here as
`inputs/recorded/torx_example_recipe.json` and imported the same way.

It is the harder import of the two. Fifteen definitions nested three deep, and
**two of them are both called `Torx`**: the thirteen-input public block and the
eighteen-input V2 wrapper that adds the mould branch and the flush shift. One
display name, two behaviours, two uuids. A recipe refers to a definition by uuid
and never by name, so the ambiguity is only in what a human reads, but whether
the import would keep both was not known until it was run.

**It keeps both.** Importing into a notebook holding zero custom blocks left it
holding fifteen, fourteen distinct names with `Torx` twice, in **one call and
13.4 s**. All six root variables read `e_OK`: `Main body`, `Torx result pair`,
`Detailed screws`, `Outer moulds`, `Detailed subtraction comparison` and
`Main body minus outer moulds`.

`check_example.py` then compares nTop's own readback of the imported notebook
against the recipe it came from. `recipe_only` omits the definitions, so the
comparison covers the root graph: **identical**, same six variables in the same
order.

### Why the recipe travels and the released notebook does not

`release/V2_compact/` ships a `manifest.json` with a size and SHA-256 for each
file. Seven of the eight match. `Torx_Example.ntop` does not: on disk it is
**15,233,693 bytes against the 1,544,256 the manifest signed**, with a different
digest. Converting a notebook runs every block at its default inputs and caches
the result inside the file, so the released example had been reconverted after
the manifest was written and carries about 13.7 MB of cached solve.

Copying that file would have published an artefact that fails its own release
manifest. Importing the recipe instead produces **1,559,105 bytes, within 1 per
cent of the signed size**. The mismatch is a fact about the source release, not
about this demo; the origin project is read-only from here and was not touched.

The frozen V2 release (3,036 nodes against the compact 1,249) stays in the origin
project. The compact version is the one its own README points at.

## Two findings worth carrying forward

**1. The placement residual scales with the insertion distance.** Three of the
eight configurations are the same screw under the same oblique rotation and
clocking, differing only in where the insertion point sits.

| Configuration | Insertion distance | Mean residual | Residual / distance |
|---|---|---|---|
| rotated | 0 mm | 2.84e-11 m | not applicable |
| oblique | 14.775 mm | 2.12e-10 m | 1.44e-08 |
| farfield | 1477.540 mm | 2.66e-08 m | 1.80e-08 |

The rotation alone costs nothing measurable: at the origin the residual is the
same band as the configurations that are not placed at all. The residual is
proportional to the distance from the origin, at about 1.8e-8 of it, stable
across two decades. Double precision on these coordinates would give a relative
error near 1e-16, so a reduced-precision step somewhere in the coordinate map is
the natural reading. **That is an inference from the scaling, not a measurement
of the implementation.**

The consequence is a working limit rather than a defect: a 0.1 micrometre
boundary gate is reachable out to roughly 5.5 m from the origin.

**2. The slicer's first plane is not where the recorded law puts it.** The
recorded index law for `slice_implicit_to_image` puts the plane of slice k at
`BOX0 + h/2 + (k-1)h`. On this build it is `BOX0 + (k-1)h`.

A fine stack across the recess floor settles it. That plane sits at exactly
-1.7300 mm, at five micrometre layers, with the body re-bounded to a thin slab so
the stack cannot run the length of the screw. The recess closes between slices 13
and 14, which brackets the floor at [-1.7300, -1.7250] under the measured law and
at [-1.7275, -1.7225] under the recorded one. The true value sits on the edge of
the first bracket and outside the second. Half a layer is 2.5 micrometres here,
twenty-five times the boundary gate, so this is not a rounding question.

Two further behaviours held as recorded: the stack does not stop at the
print-volume ceiling but continues until the body's own bounds are exhausted, and
a plane lying exactly on a boundary surface rasterises as open.

With the measured mapping applied, the recess contour read off the raster agrees
with the mirror at all six angles, worst 0.005044 mm against a pixel of
0.006109 mm: inside one pixel.

## Cost

| Step | Calls | Time |
|---|---|---|
| Offline build of the complete recipe | none | 0.062 s |
| `import_recipe`, the public block (1,451 nodes, 7 custom blocks) | **1** | **32.7 s** |
| `import_recipe`, the same plus the measurement band (2,425 nodes, 501 variables) | **1** | **186.3 s** |
| Reading 479 probes | 479 | 0.058 s, **one poll** |

Every probe read a value on the first poll. Nothing had to be waited on.

## Files

```
scripts/torx_catalogue.py     source facts and stable identifiers   (no nTop)
scripts/torx_spec.py          the frozen mirror and predictions     (no nTop)
scripts/check_spec.py         the mirror checked against itself     (no nTop)
scripts/torx_backend.py       the recording backend: graph -> recipe (no nTop)
scripts/torx.py               the eight blocks, one graph           (no nTop)
scripts/build_torx.py         the registered offline build          (no nTop)
scripts/check_recipe.py       offline recipe == nTop's own recipe   (no nTop)
scripts/torx_verification.py  the three live recipes                (no nTop)
scripts/torx_live.py          the console run: import, read, save
scripts/check_example.py      the V2 example readback and manifest  (no nTop)
scripts/make_figures.py       slice archives -> report figures      (no nTop)
scripts/publish_evidence.py   receipts out of the ignored output/   (no nTop)
scripts/render_report.py      the report, from the receipts         (no nTop)
inputs/source_tables/         the three ISO row tables
inputs/nT-0008-Ex.implicit    the reference body the released example reads
inputs/recorded/              nTop's own recipe, and the block identifiers
reference/                    the source reviews from the origin project
source_builders/              the original JavaScript builders, as provenance
inputs/recorded/              nTop's own recipes, the block identifiers, the
                              V2 example recipe and its release manifest, plus
                              the V2 compact assembly and its two extractors
models/                       THE RELEASED ORIGINALS, and nothing else. The
                              port's own saves go to output/ported/, ignored.
models/Torx.ntop              the 18-input assembly, 1,367,456 B
models/Torx_Example.ntop      the released wired example, 15,233,679 B, its
                              Reference Body repointed at D:/nT-0008-Ex.implicit
models/Torx_Screws.ntop       detailed screw list extractor, 14,099 B
models/Torx_Outer_Moulds.ntop outer mould list extractor, 13,837 B
evidence/                     the receipts the report cites
reports/index.html            the report and its five native sections
output/                       every raw receipt and the slice archives; ignored by Git
```

## Reproduce

Everything except the last step runs without nTop.

```powershell
uv run --locked python demos/torx/scripts/check_spec.py
uv run --locked python scripts/build.py torx
uv run --locked python demos/torx/scripts/check_recipe.py
uv run --locked python demos/torx/scripts/torx_verification.py
uv run --group render python demos/torx/scripts/make_figures.py
uv run --locked python demos/torx/scripts/publish_evidence.py
uv run --locked python demos/torx/scripts/render_report.py
```

For the live step, launch a separate task-owned nTop process as
[docs/BACKGROUND_CONSOLE.md](../../docs/BACKGROUND_CONSOLE.md) describes, verify
that exactly one loopback listener belongs to it, then dispatch
`torx_live.run`, `torx_live.run_rejections` and `torx_live.run_figures`.

## Limits

The supplied ISO 10664:1999 Table 1 A and B values are exact declared nominal
dimensions, not metrology of one sample. The informative Annex A radius ratio is
approximate and carries no certified error bound, so this is a labelled derived
CAD contour, not a unique normative one. The pan crown uses an exact spherical
cap to stand in for an explicitly approximate source rf, and its crown-to-side
micro-round is omitted. The countersunk series is the historical 2013 envelope
with a sharp cone-to-neck junction, and is not asserted equivalent to the revised
2022 design. The thread is the ISO 68-1 basic profile: actual external root,
runout and tip details remain simplified. Tamper-resistant posts are custom
derivatives combining the ISO recess construction with Camcar reference post
dimensions. T6 has no sourced post; T27 has no A and B pair in the supplied
table. External E, Torx Plus, Paralobe and ttap are not offered, because their
complete nominal contours were not established.

The standards themselves are not redistributed. Each row cites its own document,
revision and printed page in `inputs/source_tables/`.

Converted and measured is not delivered. The geometry verdict rests on 479 field
samples, one validity-gate sweep and native sections, not on a mesh comparison or
a physical part. None of these checks establish strength, manufacturing tolerance
or production conformity.
