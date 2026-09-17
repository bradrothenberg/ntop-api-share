# Notebook API findings: nTop 6.1.0-rc build 42926, live session

Build under test: `nTop 6.1.0-rc commit-050d0c7cdc8e412c3a35298bc5a89dc8a6da864d`,
`D:\nTop-turbo-prchecks-windows-42926\ntop.exe`, PID 23540, launched 16 September 2026 19:10:27.
Transport: `scripts/ntop_tcp.py` over the documented loopback console `127.0.0.1:2323`, with the
interpreter PID verified on the connected socket before every dispatch. Console interpreter: Python 3.13.14.

Evidence scope. Everything marked MEASURED was executed in this session against that process and has a
retained receipt under `.local/`. Nothing here is inferred from the supplied package or from build 42594.
Receipts: `.local/tcp-run-001` through `tcp-run-006`, `probe-live.json`, `state-live.json`,
`sphere-live.json`, `sphere-native-recipe.json`, `hello-readback.json`, `Hello_RC.ntop`.

The method surface matched the published reference exactly: 31 live methods, 31 documented, with no method
present in one and absent from the other.

---

## F1. `name` and `id` are inverted with respect to the interface (MEASURED, high impact)

`list_blocks` and `list_variables` return the user-visible label in `id`, and put the **output type's**
display name in `name`. Four distinct variables therefore report two `name` values between them.

Observed:

```json
{"name": "Scalar Variable",        "id": "Harness a",      "funcId": "core.var<real>"}
{"name": "Scalar Variable",        "id": "Harness b",      "funcId": "core.var<real>"}
{"name": "Scalar Variable",        "id": "Harness sum",    "funcId": "core.var<real>"}
{"name": "Implicit Body Variable", "id": "Harness sphere", "funcId": "core.var<implicit>"}
```

The interface shows `Harness a`, `Harness b`, `Harness sum`, `Harness sphere`. The exported recipe also
carries those as `name`. Three surfaces disagree: the GUI and the recipe call it the name, the live API
calls it the id, and the live API's `name` is a type label that identifies nothing.

Impact. Any state dump keyed on `name` collapses four blocks into two. `harness/agent.py` writes exactly
such a dump. An agent reading it cannot distinguish the variables, and a human reviewing it sees a notebook
that appears to contain duplicates.

Aggravating documentation. `docs/API_REFERENCE.md` says *"Use returned IDs after renaming; a display label
is not a stable identifier."* On this build the returned id **is** the display label, and `name` is the
thing that is not an identifier. The sentence is true in letter and misleading in effect.

Suggested fix, in order of preference: (a) return `name` as the user-visible label and add `typeName` for
the type string; (b) if the wire format must not change, add `displayName` and document `name` as the type
label; (c) at minimum, correct the reference so it states which field carries which.

## F2. Notebook inputs are invisible to the API (MEASURED, high impact)

The interface shows an `Inputs` container above `Section 1`, holding the notebook's input cards.
`list_sections()` returns only `[{"name": "Section 1", "id": "section_2"}]`. No method enumerates, reads,
creates or deletes a notebook input, and none reads or sets the notebook output.

Consequence. The live API cannot author an Automate-facing notebook. The same contract is fully expressible
through the CLI extended recipe: this session converted a part carrying a dimensioned `Width` input and an
implicit output through `ntopcl convert --ext`, read it back with `exportjson --ext`, and evaluated 80 field
probes at two widths with a maximum error of 2.95e-07 mm
(`.local/assembly-pilot-42926/verification.json`). The capability exists in the product and is unreachable
from the console.

Suggested fix: `list_inputs()`, `promote_to_input(block_id, ...)`, `set_output(block_id)`, and
`list_sections()` reporting the inputs container with a distinguishable kind.

## F3. Notebook title and description are write-only (MEASURED, low impact)

`import_recipe` applied the recipe's `displayname` and `description`; the interface shows
"Notebook API hello" and "Two scalars and an SI sphere." No getter exists among the 31 methods, so an agent
cannot read back what it just set, and cannot audit a notebook it did not author.

Suggested fix: a getter pair, or include both fields in an existing structural call.

## F4. `examples/hello_recipe.json` does not import on this build (MEASURED, blocking for new users)

```
RuntimeError: Failed to import the recipe at "...\examples\hello_recipe.json":
Function sphere<point,real> is not compatible with input/output information.
```

This is the repository's own first-run check, invoked by `ntop_api.hello(notebook)` and by `README.md`.
The identifier is valid on this build. The defect is one field: the sphere **function node** declares
`"type": "implicit"` where the build requires `"type": "sphere"`.

Established by asking the build directly. `list_block_inputs` on a live `sphere<point,real>` returns:

```json
{"name": "Sphere_0", "type": "sphere", "isReturnValue": true}
```

and `implicit` appears only among its properties, as `body`. The build's own `export_as_recipe` writes
`"type": "sphere"` for that node (`.local/sphere-native-recipe.json`). Correcting that single token makes
the recipe import cleanly: the sum reads 5.0, the sphere reaches `e_OK`, and the notebook saves
(`.local/Hello_RC.ntop`, 10 725 B).

The repository already records the correct value elsewhere. `demos/i6/scripts/recipe_backend.py` has
`"sphere<point,real>": (["Center Point", "Radius"], [_ZERO_POINT, None], "sphere")`. The hand-written
example contradicts the project's own measured table.

Suggested fix: correct the example, and, more usefully, make the import error name the offending node id,
the offending field, and the expected value. "not compatible with input/output information" gave no node,
no field and no expected type; locating it required building the block live and diffing the build's own
export.

## F5. Error message quality is uneven (MEASURED, medium impact)

Two errors from the same session:

- Good. `get_block_input("Harness sphere", "Input")` returns: *Parameter "Input" of block "Harness sphere"
  has type "implicit", which cannot be read yet; only "real", "vector", "point", "bool", "integer" and
  "text" parameters can.* It names the block, the parameter, the actual type, and the supported set.
- Poor. The F4 import error names none of the node, the field, the expected value, or the position.

The first is the standard the second should meet.

## F6. A documentation conflict is settled (MEASURED)

`docs/API_REFERENCE.md` records a conflict over whether points carry two or three components.
`get_block_input("Harness sphere", "Center Point")` returned `[0.0, 0.0, 0.0]`. Three components. The
getter docstring's two-item wording is a documentation error, as the reference suspected.

## F7. `blockFuncId` is an empty string, not absent (MEASURED, low impact)

For a variable holding a literal, `list_variables()` returns `"blockFuncId": ""`; for one wrapping a
computation it returns the function identifier. An empty string is a falsy value a parser can confuse with
a missing key. `null` or omission would be unambiguous.

## F8. "Empty notebook" is checked four different ways, and the quickstart uses the weakest (MEASURED, medium impact)

A notebook is never structurally empty: the interface always carries an `Inputs` container and an `Output`
field, neither of which the API can see (F2). The repository's guards therefore approximate emptiness, and
they do not agree with each other.

| guard | check |
|---|---|
| `harness/ntop_api.py` `hello()` | `list_variables()` only |
| `scripts/stage.py` generated script | `list_variables()` only |
| `examples/probe_42926.py` | `list_variables()` **and** blocks across all sections |
| `demos/kestrelsat-corner/scripts/replay.py` | `list_variables()` and blocks across all sections |

The two that check variables alone are the ones a new user meets first: `hello()` is the README quickstart
and `stage.py` writes the import script for every demo. A notebook holding non-variable blocks, notebook
inputs, or an open custom block passes those guards while plainly not being empty, and `import_recipe`
then merges into occupied state.

The stronger pair is still incomplete: neither inspects `current_open_custom_block()`, and no guard can
inspect notebook inputs at all, because F2 leaves no method for it. This matters because
`export_as_recipe` silently retargets to the open custom block when one is being edited, which the
reference documents but no guard checks.

Suggested fix, repository side: one shared `require_empty(notebook)` helper covering variables, blocks in
every section, and `current_open_custom_block()`. Product side: F2, so that inputs can be part of the check.

---

# Second session, 17 September 2026

Build under test: the same `nTop 6.1.0-rc commit-050d0c7cdc8e412c3a35298bc5a89dc8a6da864d`, from
`D:\ntop_dev\nTop-6.1.0-rc-42926\ntop.exe`, PID 28232, launched 01:32:17, the only nTop process on the host.
Same transport and the same interpreter-PID check on the connected socket before every dispatch.
Receipts: `.local/torx-run-001` through `torx-run-006` and `demos/torx/output/`.

## F9. `import_recipe` creates custom blocks (MEASURED, closes a documented gap)

`docs/API_REFERENCE.md` says the API edits existing custom blocks and lists no method that creates or
imports one. That is true of the *dedicated* methods, and it has been read as a hard limit: it would put
every assembly of referenced custom blocks out of reach of the Notebook API.

It is not a hard limit. A complete recipe carries its definitions in `imports` and calls them by uuid, and
importing one creates them. Measured on a notebook that held **zero** custom blocks before the call:

```json
{"before": {"variables": 0, "sections": 1, "custom_blocks": 0},
 "after":  {"variables": 6, "sections": 1, "custom_blocks": 7},
 "created": ["Place Screw", "Countersunk Head 2013", "Torx Internal", "Screw Head",
             "Torx Local Development", "Pan Head", "Metric Thread Kernel"],
 "calls": 1, "seconds": 32.708, "recipe_bytes": 1067220, "graph_nodes": 1451}
```

The seven definitions carry a nested call depth of two and a root `cbRefs` naming all of them. A second
import of the same graph plus a 479-probe measurement band, 2,425 nodes and 501 variables, also took one
call, at 186.3 s; every probe read a value on the **first** poll.

Suggested fix: document `import_recipe` as the create path for custom blocks, beside the sentence that
currently reads as a prohibition. Nothing needs to change in the product.

Receipt: `demos/torx/output/live_run.json`.

## F10. A `choice` input cannot be set from the live API (MEASURED, medium impact)

`docs/API_REFERENCE.md` lists real, vector, point, integer, bool and text for the live setters. A `choice`
is none of them, so a notebook whose public interface is native Choice Lists, which is the shape the
interface encourages for selecting a standard size, cannot be driven from the console at all. The recipe
route carries the choice and its selected index without difficulty.

Worked around here by calling the inner assembly with integer literals the recipe carries, and checking the
Choice Lists separately by reading back the selection variables the graph computes from them: 4 of 4 resolve
to the expected source identifier.

## F11. The slice-index law changed from the recorded 6.0.3 behaviour (MEASURED, medium impact)

For `slice_implicit_to_image<...>[2.0.0]`, the recorded behaviour puts the plane of slice k at
`BOX0 + h/2 + (k-1)h`. **On this build it is `BOX0 + (k-1)h`.**

Pinned against a plane known independently to be at -1.7300 mm, at 5 micrometre layers, with the body
re-bounded to a thin slab so the stack could not overrun:

| law | bracket the transition puts the known plane in | contains it |
|---|---|---|
| `BOX0 + (k-1)h` | [-1.7300, -1.7250] mm | yes |
| `BOX0 + h/2 + (k-1)h` | [-1.7275, -1.7225] mm | no |

Half a layer is 2.5 micrometres here, twenty-five times the geometric gate in use, so this is not a
rounding question. Anything that converts a slice index to a coordinate against the recorded law is off by
half a layer on this build.

Two recorded behaviours did hold: the stack does not stop at the print-volume ceiling but continues until
the body's own bounds are exhausted, and a plane lying exactly on a boundary surface rasterises as open.

Receipt: `demos/torx/output/figures_measured.json`, which re-derives the law every run and reports both
candidate brackets rather than assuming either.

## F12. The placement residual scales with the insertion distance (MEASURED, inference flagged)

Three configurations of one body under one rotation and clocking, differing only in the insertion point:

| insertion distance | mean boundary residual | residual / distance |
|---|---|---|
| 0 mm | 2.84e-11 m | not applicable |
| 14.775 mm | 2.12e-10 m | 1.44e-08 |
| 1477.540 mm | 2.66e-08 m | 1.80e-08 |

The rotation alone costs nothing measurable. The residual is proportional to the distance from the origin
at about 1.8e-8 of it, stable across two decades. Double precision on these coordinates would give a
relative error near 1e-16.

**MEASURED**: the proportionality and its coefficient. **INFERRED**: that a reduced-precision step in the
coordinate map causes it. The implementation was not inspected and the inference is not a finding.

Practical consequence: a 0.1 micrometre boundary gate is reachable out to roughly 5.5 m from the origin.

Receipt: `demos/torx/output/live_run.json`, configurations `rotated`, `oblique` and `farfield`.

---

## F13. An external input path is container state, not recipe data (MEASURED, high impact)

A notebook's `file_path` input value lives in the `MAGIC%$1` `main` chunk as JSON, and **not** in the
exported recipe. Measured on the released `Torx_Example.ntop`: one node carries
`{"id":"103","type":"file_path","value":{"val":"<path>"}}` in `main`, and `grep` over the paired
`Torx_Example.json` export finds nothing.

The consequence is silent. A recipe round trip, which is the transport this demo is built on, reproduces
the graph and drops the path. The imported notebook has the same blocks and no input file, and nothing in
the import reports a loss. A notebook whose geometry depends on an external body therefore cannot be
carried by `import_recipe` alone.

Repointing one is a container edit, not an API call: rewrite the string, repack the chunk, and correct the
directory offsets. Measured on a 226-chunk, 15.2 MB example, 225 chunks stayed byte-identical and only
`main` changed. A re-save through the interface would also rewrite the state chunks, which is a larger
change than the one intended.

The cached solve is separate and larger. The released `Torx_Example.ntop` is 15,233,693 bytes against the
1,544,256 its own release manifest signs, because converting a notebook runs every block at its defaults
and caches the result inside the file. Recipe import instead produced 1,559,105 bytes, within one per cent
of the signed size. Both facts are about the same file and neither is about the recipe.

Receipt: `.agents/skills/ntop-community-package/scripts/repoint_file_path.py` and its printed record.

---

## Open, with the exact test

**O1. Does `list_blocks()` with no argument really cover only the first section?**
`docs/API_REFERENCE.md` states it does. This notebook has one section, so the claim is unfalsifiable here:
the default call and the explicit `list_blocks("section_2")` returned identical four-block lists.
Test: `add_section`, `move_block` one variable into it, then compare `list_blocks()` against the union of
`list_blocks(s["id"])` over `list_sections()`. Not run here because `add_section` has no documented inverse
and the notebook under test was on screen.

**O2. Do the 6.0.3 and 6.1.0 block libraries agree beyond the pilot's signatures?**
The extended-recipe contract is stable across the two builds: for the pilot part the saved body/graph and
the saved `inputs` contract are byte-identical, and only the stamped uuid differs. That covers roughly a
dozen signatures. F4 shows at least one encoding a hand-written recipe got wrong. A full library comparison
is the only way to size this.

## Reproduction

```powershell
$rc = "D:\nTop-turbo-prchecks-windows-42926"
$env:NTOP_PYSCRIPTS = "<checkout>\harness"
$p = Start-Process -FilePath "$rc\ntop.exe" -WorkingDirectory $rc -PassThru
Get-NetTCPConnection -State Listen -LocalPort 2323 | Select-Object LocalAddress,LocalPort,OwningProcess
uv run --locked python scripts/ntop_tcp.py --session .local/session.json --file .local/command.py --run-dir .local/tcp-run-001 --timeout 45
```

Exactly one loopback listener owned by the launched PID is required before any dispatch, and a fresh run
directory per dispatch. The helper verifies the listener's PID, executable and creation ticks, then probes
the interpreter PID on the connected socket, and sends notebook code only on a match.
