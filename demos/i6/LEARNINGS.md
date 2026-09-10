# Recorded lessons

This is an edited record of prior work. Its native results apply to those recorded revisions.
Local machine paths and omitted artifact links were removed for this public handoff.
Historical tool and artifact names below describe the source work. Use README.md for the runnable commands and files in this checkout.

# Notebook API notes from the engine build

Measured on nTop 6.0.0-rc build 42594, 2 September 2026, with the three
probes in `nTopScripts/engine_probe*.py`. Results are in
`_agent/engine_probe*.json`. These extend `earlier API harness/docs/NOTEBOOK_API.md`;
nothing there was contradicted.

## Units

A notebook created with `new_notebook()` displays **inches and degrees**.
The default 10 mm cylinder reads back as 0.3937, and `set_block_input(...,
43.0)` on a radius lands in the recipe as 1.0922 m. Angles read back in
degrees (a 0.5236 rad literal reads 30.0).

Consequence: every dimensioned literal in this project is authored by
recipe in SI with an explicit `units` map. The API only ever sets numbers
that are unit-free (indices, ratios, direction vectors, array counts).

## Speed

`add_block` averaged 0.075 s over 50 different identifiers, maximum
0.19 s. The full engine build is about 1000 blocks and 2000 connections.

## Geometry semantics

| Block | Measured behaviour |
|---|---|
| `rotate<spatial3d,point,vector,real>[1.1.0]` | Right-hand rule. (0,0,1) about +X by +90 deg gives (0,-1,0). |
| `plane_from_normal` property `body` | The half-space on the side **opposite** the normal. Normal +Z keeps z <= 0. |
| `array_implicit<implicit,vector,vector>` | `Count` is a settable vector such as (6,1,1). Copies extend from the seed body in the +Spacing direction. |
| `translate` / `rotate` on an implicit | Output keeps the input's concrete type (a rotated cylinder is still `cylinder`), and chains implicit -> rotate -> translate -> boolean union work. |
| `boolean_*` blend | `Blend Type` is an enum the API cannot set; blend radius defaults to 0. |

## Readback as a verification channel

`get_block_input(var, "Input")` on a `core.var<real>` or `core.var<point>`
that is fed by a computation returns the **evaluated** value: a 30 deg + 30
deg chain read 60. Bounding box -> `core.var<point>` -> coordinate chains
also read back. A value derived from `mass_properties` read back as
`None`, so numeric checks in this project use bounding boxes and the
kinematic scalars.

Connecting a dimensionless real into a length input, or an angle into a
radius, raises nothing. Unit mistakes must be caught numerically.

## Recipes

- `import_recipe` puts imported variables into the **first** section,
  regardless of which sections exist. Adding `PARAMETERS` before
  `Section 1` and then importing is how this project gets them where it
  wants them.
- Recipe literals of type `real` with `units` of `{"angle": 1}`,
  `{"length": 1}`, `{"length": 3}` or `{}`, plus `integer`, `text` and
  `file_path`, all import and wire. An `integer` literal connected to
  `polar_array_implicit`'s `Count` works, which is the only way to author
  an integer input.
- A recipe body entry may be a whole block (for example a
  `boolean_union` with its enum preset and its `Bodies` list left null),
  wrapped as a variable. This is the route to a blend enum, untested here.
- A recipe with a top-level `inputs` entry and a variable whose contents
  are `{"input": 0}` imports without error and the variable reads 0.
  Whether the notebook then has an Automate input is untested.

## Nesting

A block wired into another block's input nests inside it: it leaves
`list_blocks()` and `list_block_inputs()` on it fails, although
`connect_block_property` into it still resolves. Rule used here: finish
wiring a block's own inputs before consuming its output, and make anything
consumed twice a variable first.

## Driving the console with the screen locked

`earlier API harness/tools/ntop_console.ps1` types with `SendKeys`, which needs the
interactive desktop and fails with "could not type the launch line" once
Windows is locked. `tools/ntop_console_post.ps1` posts `WM_CHAR` messages
to the console window instead. It works while locked and never steals
focus. UI Automation can still read the console text while locked, so the
verification loop keeps working.

## Cost of API calls on a large notebook

On the empty notebook `add_block` took 0.075 s. With 340 variables every
mutating call (`add_block`, `connect_block_property`, `set_block_input`,
`add_variable`) took about 0.5 s; with 700 variables and the full engine
geometry present, adding 25 bounding-box checks (about 250 calls) ran for
over 30 minutes with the UI thread blocked. Each call appears to
re-evaluate and redraw the notebook. Reads (`get_block_input`,
`list_variables`) stay at a millisecond.

`import_recipe` of the whole engine (682 variables, 987 blocks) took 405 s
in one call, so bulk authoring goes through a recipe and the API is kept
for reads, single edits, and `set_block_input` on the drive variable.

The setter also fails intermittently on a busy notebook:

    The request to set parameter "Axis" of block "Torus_0" was not carried out.

The same call succeeded on a fresh notebook, so treat it as a race with
re-evaluation and retry, or avoid it by authoring through a recipe.

## The .ntop file format

Enough of the saved file was decoded to organise a notebook after an
import (`tools/organize_notebook.py`; round-trip is byte exact):

- `MAGIC%$1\n` header; at byte 24 a table of 16-byte chunk name plus
  8-byte chunk END offset relative to byte 344, where the chunks start.
- Each chunk: `MAGIC@@9`, type (16 bytes), name (16 bytes), payload size
  (8 bytes), padded to 128 bytes, then the payload. `ntopfn` and
  `obj_container` payloads hold child chunks (`obj_container` after an
  8-byte prefix).
- `main/fn` (json): `{"code": [blocks]}`. Block 100 is the root group;
  its `inputs` order is the tree order. Every block has `id`, `func`,
  `name`, `type`, `units`, and `inputs` of `{instanceId, propchain, ...}`.
  Variables are `core.var<T>` blocks whose one input is the wrapped block.
- `sections` (json): `{"decorations": [{"name", "collapse",
  "description"}], "poles": [0, n1, ..., N]}`. Sections are consecutive
  index ranges over the root order. That is the whole section model.
- `open` (json): per tree node UI state keyed by index path
  `"100_<top index>_<input index>..."`.
- `view` (json): per body `{"id", "visible", "attributes": [display_mode,
  color RGBA, display_style, transparency, opacity], ...}`. This is where
  visibility and colour live; the API has no call for either.

Import order matters for one reason: the recipe body order becomes the
root order, so a recipe that is already grouped by section needs only the
`poles` written.

## Springs, and blocks to avoid (3 Sep 2026)

A helix is built by list processing: a recipe `core.list<real>` of 151
parameters lifts one `point<real,real,real>` to `list<point>`, `polyline`
turns that into a polycurve, the polycurve's `scalar field` feeds a
`core.var<implicit>`, and `thicken_implicit` gives the wire radius. The
polyline box read back exact (radius 10 mm, z 42..83 mm); the tube's box is
padded by ~1.9 mm for a 1.6 mm wire. `offset_implicit` on the curve field
returned an empty box; the profile `sweep` blocks evaluated to nothing; and
adding one of `evaluate_imp_expression`, `sweep<new_profile,...>`,
`vector_field_from_components` crashed nTop on an empty notebook, twice.

The Python Console can be opened without touching the foreground: `Invoke`
the `main_menu_button`, `Expand` the `View` action, then post Down/Right/Down/
Return key messages to the QMenu windows (see the skill for the sequence).

## Two more findings (4 Sep 2026)

- Export tolerance can drop geometry: `mesh_from_implicit_body_2` at 0.6 mm
  exported only the bucket of the valve (head, stem and retainer missing),
  while the mesh block's `bounding box` property still reported the full body.
  At 1.0 and 1.5 mm the same union exported whole. Verify exported STL extents.
- Distance-to-polyline fields are expensive to re-evaluate: 24 springs built
  that way made one `Crank Angle` change take over 30 minutes. The exact helix
  field from plane coordinate fields (`sqrt`, `atan2`, `mod` on `real_field`)
  gives the same coil and evaluates in a fraction of the time.

## The `negative` ref property, measured (6 Sep 2026)

A recipe input `{"props": ["negative"], "ref": {"id": X}}` negates X when it
feeds a block input: a `point<real,real,real>` built that way read back
(-3.39, 3.39, 3.39). The same ref as the direct contents of a `core.var<real>`
does NOT negate: the variable read back +3.39. In the engine this affected
exactly one variable, `CHECK Cyl1 Rod Angle deg` (built by holding a negated
value), which reported +17.25 deg at 90 deg crank where the geometry, driven
by the same negation through a `rotate` input, was correct at -17.25. The
builder now negates with a `multiply` block before holding, and the check
matches to 4e-15 deg. Lesson: a property on a held reference is a silent
no-op; verify every derived check numerically at an angle where it is
non-zero, not only at the rest position.

Chunked recipe import is not possible: references resolve only inside the
one file (a second recipe naming a variable already in the notebook fails with
"Could not resolve reference"). In the notebook a variable's id is its name.
