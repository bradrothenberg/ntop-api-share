# Historical Notebook API reference: build 42594

**Historical build 42594 reference.** For build 42926 use [the current reference](API_REFERENCE.md) and [September update](API_42926.md).
That build supports six value types, explicit units, build states, movement, descriptive docstrings, and a documented TCP service.
The limitations below remain a record of the older build; they are not the current method contract.

Reference for the prototype Python API inside nTop's GUI. Everything
here was measured on **nTop 6.0.0-rc, build 42594**, in August 2026. The
API is unreleased and absent from the public documentation; a search of
the nTop docs server returns zero hits for `list_available_blocks`,
`add_block(` and `Python Console`. Re-measure after a build bump rather
than trusting this file.

---

## 1. What it is, and where it lives

The API is a single Python object named `notebook`, bound in the Python
Console inside the nTop GUI (**Utilities > Python Console**). It can add
blocks, wire them together, read block properties, and save the
notebook: the same actions a person performs by clicking.

It has **no socket, pipe, or RPC**. The internal `NotebookRemoteControl`
facade marshals every call onto the Qt UI thread; it is not a network
server. Reaching it from outside the GUI needs UI automation, which is
what the bundled `scripts/ntop_console_post.ps1` bridge does.
See [background dispatch](BACKGROUND_CONSOLE.md).

Which binary has it:

| Binary | Notebook API |
|---|---|
| `ntop.exe` (GUI) | Yes. The only one. |
| `ntopcl.exe` (Automate) | No. Contains no Notebook API bindings. |

The console runs **CPython 3.13.14** (Anaconda-packaged), bundled with
the build.

### Making your own modules importable

The console imports from `%USERPROFILE%\Documents\nTopScripts\` (the
literal string `nTopScripts` is in the binary). It also extends
`sys.path` from the `NTOP_PYSCRIPTS` environment variable, and takes
`NTOP_PYHOME` for the interpreter home. Both are confirmed present in
`ntop.exe`.

Set this before launching nTop:

```powershell
$env:NTOP_PYSCRIPTS = (Resolve-Path "./harness").Path
```

If nTop is already running without it, prepend the path inline instead
of restarting:

Use the Python Console to prepend the absolute path to this checkout's harness folder.
Then run `import ntop_api; ntop_api.use("i6"); import agent; agent.api(notebook)`.

`agent.api(notebook)` dumps the live signatures and `sys.path` to
`demos/i6/output/_agent/api.txt`, which confirms the path took effect.

---

## 2. The surface

Verbatim from `agent.api(notebook)` on build 42594, so these signatures
are exact rather than inferred.

```
new_notebook()                                                      -> None
open_notebook(notebook_path: str)                                   -> None
save_notebook()                                                     -> None
save_notebook_as(notebook_path: str)                                -> None
export_as_recipe(recipe_path: str, recipe_only: bool = False)       -> None
import_recipe(recipe_path: str)                                     -> None

list_sections()                                                     -> list[dict]
add_section(section_name: str, before_section_id: str = '')         -> dict

list_available_blocks(mask: str = '')                               -> list[str]
add_block(identifier: str, section_id: str = '')                    -> dict
list_blocks(section_id: str = '')                                   -> list[dict]
delete_block(block_id: str)                                         -> dict

add_variable(new_name: str, block_id: str = '')                     -> dict
list_variables()                                                    -> list[dict]
rename_variable(block_id: str, new_block_id: str)                   -> dict
delete_variable(block_id: str)                                      -> dict

list_block_inputs(id: str)                                          -> list[dict]
set_block_input(block_id: str, parameter_name: str, value: object)  -> None
get_block_input(block_id: str, parameter_name: str)                 -> object
clear_block_input(block_id: str, parameter_name: str)               -> None
list_block_properties(block_id: str)                                -> list[dict]
connect_block_property(source_block_id: str, property_name: str,
                       target_block_id: str, parameter_name: str)   -> None
append_to_list(source_block_id: str, target_block_id: str,
               target_list_id: str)                                 -> None

list_custom_blocks()                                                -> list[dict]
open_custom_block(name: str)                                        -> None
current_open_custom_block()                                         -> dict
close_current_open_custom_block()                                   -> None
```

There are no docstrings beyond the signatures.

**Two names mislead.** `append_to_list`'s third argument
`target_list_id` is the list **input's name**, not an id:
`append_to_list(src, union_id, "Bodies")`. And `rename_variable`'s
`new_block_id` is just the new name.

### Exercised on this build

`add_section`, `add_block`, `add_variable`, `delete_block`,
`delete_variable`, `connect_block_property`, `clear_block_input`,
`append_to_list`, `import_recipe`, `export_as_recipe`, `save_notebook`,
`list_*`, `set_block_input`, `get_block_input`.

**Not exercised:** `rename_variable`, the four custom-block calls,
`new_notebook`, `save_notebook_as`, `open_notebook`.

---

## 3. Block identifiers

Identifiers are exact strings built at runtime, such as
`sphere<point,real>` or
`boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]`. They are
**not** present in the binary and **cannot be guessed**. Some need a
version suffix; the unversioned form is rejected.

Always look them up:

```python
notebook.list_available_blocks("mass_propert")
```

Build 42594 returns **2,571** identifiers for an empty mask.
`agent.blocks(notebook)` writes the whole catalog to `_agent/blocks.json`.

**Block ids are block names.** Rename a block and its id changes. Keep
the id `add_block()` returned.

### Identifiers this project uses

| Purpose | Identifier |
|---|---|
| Mass, volume, CG | `mass_properties<implicit,real_field,real>[1.1.0]` |
| Key/value table | `core.dictionary<list<text>,list<real>>` |
| Serialize | `json_from_dictionary<dictionary<text,real>>[5.30.0]` |
| Write a file | `export_json<file_path,json>` |
| Literal lists | `core.list<text>`, `core.list<real>` |
| Hold one value | `core.var<T>` for T in point, bounding_box, real, line_segment, implicit, json, file_path, text |
| Arithmetic | `subtract<real,real>`, `divide<real,real>`, `multiply<real,real>`, `add<real,real>`, `atan2<real,real>`, `max<real,real>` |
| One-operand math | `sqrt<real>`, `abs<real>` |

Math blocks take `Operand A` / `Operand B`, except `sqrt` and `abs`
which take `Operand`.

### Properties worth knowing

All confirmed by `list_block_properties`.

| Block or type | Properties |
|---|---|
| `mass_properties` | `mass`, `volume`, `center of gravity`, `principal moments`, `principal frame` |
| any implicit | `bounding box`, `inverted`, `scalar field` |
| `bounding_box` | `min point`, `max point`, `span`, `centroid`, `box`, `diagonal` |
| `point` | `x`, `y`, `z` (lowercase), `vector`, `body`, `scalar field` |
| `line_segment` | `length`, `start point`, `end point`, `center point`, `direction`, `axis` |
| `text` | `length`, `path` (converts text to a file_path) |
| `file_path` | `Text` |
| spline list | `start point`, `end point`, `length`, `size`, `name` |

---

## 4. Traps

Eleven behaviors that cost real time. `API_FINDINGS.md` has the same
list written up for the API's developer, with severity and verbatim
error text.

**Read trap 11 first.** It is the only one that caps what the API can
produce rather than how long it takes you to get there.

**1. Only `real`, `vector`, `point` can be set.**
`set_block_input` raises on everything else:

> Parameter "0" of block "Text List_0" has type "text", which cannot be
> set yet; only "real", "vector" and "point" parameters can.

Same for `file_path`, `real_field`, `integer`, `bool`, and list types. A
text literal and an output path cannot be authored with the plain API at
all. Use `import_recipe` (section 5). A `real_field` input still accepts
a *connection* from a `real`, so only literals are blocked.

**2. Three unit conventions, one model.** `set_block_input` and
`get_block_input` speak the notebook's DISPLAY unit. On this notebook,
which displays inches, `get_block_input("C_root", "Input")` on a
5.4864 m chord returns `216.0`, and setting `6.0` sets six **inches**.

The other two channels disagree with it and with each other:

| Channel | Units | How you know |
|---|---|---|
| `set_block_input` / `get_block_input` | notebook DISPLAY unit (inches here) | nothing exposes it; you must read a value back |
| recipe JSON | SI, metres and radians | explicit `units` map per value |
| `ntopcl -j` input template | **mm and deg** here | explicit `"units"` string per input |

Only the last two declare themselves. Mixing the API and the recipe
rescales a model by 39.37 with no error at all. Read every value back
after setting it, and take `-j` units from the generated template rather
than assuming they match either of the others.

**3. `add_variable` WRAPS a block, it does not rename it.** The returned
id is a new `core.var<T>` whose only input is `Input`:

> Block "FX fuselage Mass Properties" has no parameter named "Body"

Worse, the inner block is then nested and `set_block_input` cannot reach
it, although `connect_block_property` resolves the same id fine:

> No block with the id "Mass properties_0" exists in the notebook

**Set every literal input before calling `add_variable`.** A block that
is already a `core.var<T>` is renamed rather than wrapped; the reply's
`funcId` tells you which happened.

**4. Reusing an output silently drops connections.** Wiring one plain
block's output into two inputs leaves all but one empty, with no error.
The moment an output feeds more than one place, `add_variable()` it and
reference the variable everywhere. `append_to_list` and
`connect_block_property` both accept a variable **name** where a block
id is expected.

**5. Property paths are one level only.**

> Block "Fuse" has no property named "bounding box.min point"

A `/` separator fails the same way. Chain a `core.var<T>` per hop:
body -> `core.var<bounding_box>` -> `core.var<point>` -> its `x`.

**6. Some list inputs need seeding, not all.**

> Input "Values" of block "Dictionary_0" holds no list to append to

Seed slot 0 through a `core.list<T>` container, connect that in, then
`append_to_list` the rest. On the first append nTop inlines the list and
refers to slot 0 directly, leaving the container detached and reading
`Empty`; delete it afterwards. **But** `boolean_union`'s `Bodies` needs
none of this: two bare appends filled slots 0 and 1 and nTop built the
list itself. Try the plain call first and check the recipe.

**7. `connect_block_property` will not overwrite a value.** A fresh
`core.var<point>` arrives with `Input` already filled:

> Parameter "Input" of block "FX fuselage CG" already has a value, which
> this call does not replace.

Call `clear_block_input` first, but only after the plain connect has
failed, so a genuine wiring mistake still raises.

**8. `import_recipe` overwrites `displayname` and `description`.** It
retitled `Example Notebook` to the recipe's own name in the tree header. A
literals recipe must carry the host notebook's title back.

**9. Deletion is asymmetric and slow.** `delete_block` refuses
variables:

> "Scalar_0" is a variable; use deleteVariable() to remove it.

Delete in reverse creation order, since a block still feeding something
else will not go. Each delete re-evaluates the notebook, so removing 88
blocks takes minutes. There is **no `delete_section`**, so a section you
add is permanent.

**10. Reading and listing surprises.**
- `list_blocks()` with no argument reports only the first section.
  Iterate `list_sections()`.
- `list_block_inputs()` includes the block's own output as a trailing
  entry with `isReturnValue: True`, named after the block id, which
  `get_block_input()` rejects. Skip it.
- A block plugged into another block's input leaves `list_blocks()`.
  Absence from the top level does not mean deleted.
- Reading back a non-scalar input returns an error string, not a value.
  An input holding a `sphere` or `implicit` is normal and fine.
- `list_variables()`'s `name` field is the **type's** display name, so
  three unrelated variables all report `Sphere Variable`. The variable's
  actual name is its **block id**. Key off `id`, never `name`.
- Feeding a `list<real>` into a scalar input triggers list processing:
  the whole downstream chain lifts to the list type. Sometimes wanted,
  never by accident.

**11. The API cannot make a notebook automatable.** There is no
`add_input`, no `promote_to_input`, and no `set_output`. A notebook
authored entirely through this API has no inputs for `ntopcl -j` to set
and no output for `ntopcl -o` to return, so it cannot be swept, batched,
or put in CI. Measured on the finished model: `ntopcl -t` returns
`"inputs": []` and fails with

> Error generating output template : Output of function not set

Export blocks are the partial way out. They fire headless even with no
output set, so a notebook can report results by writing its own file.
That works for a single run. It does not survive a sweep, because the
path is a `file_path` literal and every run writes to it.

The recipe format carries both `inputs` and `output` at the top level
(section 5 has the schema). Whether `import_recipe` honors them on a
merge is **untested**.

**Destructive with no prompt.** `new_notebook()` and `open_notebook()`
discard unsaved work. `save_notebook_as()` and `export_as_recipe()`
overwrite. Confirm with a human before calling any of them on a notebook
they care about.

---

## 5. Authoring literals the API refuses to set

Trap 1 blocks `text` and `file_path`. `import_recipe` has no such limit,
and **it merges**: measured on this build, importing a one-variable
recipe left all six sections, all 31 variables and all six custom blocks
untouched, and added the new variable.

A recipe cannot reference blocks already in the notebook, so the working
pattern is:

1. Write a small recipe holding only the literals: text lists, file
   paths, and any real that needs explicit units.
2. `import_recipe` it.
3. Build everything numeric with the plain API and wire the imported
   variables in with `connect_block_property`.

The worked literal encoder is `demos/i6/scripts/make_engine_recipe.py`. Its output is created under the demo output folder.

### Recipe value encodings

| Type | Encoding |
|---|---|
| text | `{"string": "main_wing__semispan"}` |
| file path | `{"val": "output/exports/part.stl"}` |
| dimensioned real | `{"isFinite": true, "units": {"length": 1}, "val": 1.0}` |
| dimensionless real | `{"isFinite": true, "units": {}, "val": 0.1}` |
| point | `[{"isFinite": true, "val": 0.0}, ...]` |

A recipe variable entry looks like this:

```json
{
  "contents": {"type": "real",
               "value": {"isFinite": true, "units": {"mass": 1}, "val": 1.0}},
  "id": "example_lit_1",
  "name": "Example One Kilogram",
  "type": "real",
  "variable": true
}
```

Top-level keys are `body`, `cbRefs`, `description`, `displayname`,
`imports`, `inputs`, `name`, `namespaces`, `version`, and `output` when
one is set. **The recipe format carries no section structure**, so a
full-notebook export and re-import would flatten the tree. Keep imported
recipes small.

### Automate inputs and the output

Read from a real generated recipe that has both, so this is the actual
schema rather than a guess. The fragments are kept as evidence in
`reference/automate_schema_example.json`. See trap 11 for why it
matters.

```json
"inputs": [
  { "name": "Wing Density",
    "type": "real",
    "dimension": {"mass": 1, "length": -3},
    "description": "Effective bulk density of the wing body.",
    "contents": {"type": "real",
                 "value": {"isFinite": true,
                           "units": {"mass": 1, "length": -3},
                           "val": 80.0}} }
],
"output": { "id": "inst2663" }
```

A block consumes an input **by index**, in place of a `ref`:

```json
{"input": 0, "props": []}
```

`output` points at a `body` entry's id; in that file it is a variable of
type `json`. Whether `import_recipe` honors either key on a merge is
**untested**.

---

## 6. Making a notebook write its own JSON

A notebook can produce an Automate-shaped measurements file with no
`ntopcl` round trip, and it rewrites the file whenever an upstream input
changes. Verified: changing `C_root` rewrote the export within seconds,
and restoring the old value reproduced every number bit for bit.

The chain is three blocks plus the two lists:

```
core.list<text>   (keys, from the recipe)
core.list<real>   (values, appended in matching order)
        |
core.dictionary<list<text>,list<real>>        Keys, Values
        |
json_from_dictionary<dictionary<text,real>>[5.30.0]
        |
export_json<file_path,json>                   Path, JSON
```

Keys and values pair **positionally**, so append order is the contract.
Check it against the exported recipe, not against the code that wrote
it.

The value type is `real`, so such a notebook **cannot write a unit
string into its own output**. Emit a numeric marker instead
(`schema_si_metres_kilograms = 1.0`) and have the reader turn that into
a unit declaration.

---

## 7. Verifying work

An API call that does not raise proves nothing. The failure mode this
API produces most often is a silently unwired input. Verify against
files:

| Check | How |
|---|---|
| Is it actually wired? | `agent.recipe(notebook)`, then read `_agent/notebook.json`. Ground truth. |
| Same, from outside nTop | `ntopcl.exe --exportjson model.ntop --exportedjson out.json` |
| Did an input take the value? | `agent.dump(notebook)`, then check it reports what you set |
| Does it look right? | Native viewport capture with a known camera and model hash |
| Is the measurement right? | Compare a measured output against a known design input |

The last row is the strongest. This project's dihedral chain measures
tip geometry and returns 3.0000000000000004 degrees, where 3.0 is the
design input two custom blocks upstream. The first build returned 177
degrees, and only that comparison caught it.

---

## 8. When not to use this API

The Notebook API **authors** notebooks. It is the wrong tool for running
them.

- Running a finished notebook headless, DOE sweeps, STL/STEP export: use
  `ntopcl.exe` (`-j input.json -o out.json`, `-t` for templates).
- Opening the GUI at a specific design point:
  `ntop.exe -j input.json model.ntop`.
- Remote or cluster execution: `ntopcl --remote`.

### Untested, worth measuring

Recorded because the flags exist in `ntop.exe`, not because they have
been run. Do not present these as working.

- `--genScreenshotConfig` (needs width and height), then
  `--screenshot <dir> --screenshotConfig <json>`, which would render
  headless off a saved `.ntop` with scripted cameras.
- `--strict` makes any incomplete or failed block fail the notebook.
  Likely the right default for agent-authored notebooks, since it turns
  a silent partial build into a nonzero exit.
- `-b` builds after load; `-p` includes top-level properties in the
  output JSON.
