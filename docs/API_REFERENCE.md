# Notebook API reference: build 42926

Current baseline: **nTop 6.1.0-rc, Notebook API Build 0910, build 42926**, supplied on 10 September 2026.
The Python Console binds `notebook` to the open notebook inside nTop.
Host Python prepares scripts and recipes; it does not supply this object.

This reference reconciles the supplied README and modeling skill with [31 recorded method docstrings](evidence/api-42926-surface.json).
Read [source identities](evidence/api-42926-sources.json), [the change guide](API_42926.md), and [the documentation audit](API_DOC_AUDIT_42926.md) for evidence scope.
The audit performed no new native execution. The [build 42594 reference](API_REFERENCE_42594.md) and [older findings](API_FINDINGS.md) preserve historical results.

## Setup and discovery

Use [setup](SETUP.md) to make this checkout's `harness/` importable in an owned nTop session.
Then check the required surface without changing its graph:

```python
import ntop_api
ntop_api.check_api(notebook, require_42926=True)
```

This checks method presence, not build identity, setter overloads, or native semantics.
Read the installed application's version and live docstrings before using another build.
`agent.api(notebook)` records those docstrings locally; its output can contain private host paths.

The supplied package documents a TCP console on `127.0.0.1:2323`, available from process startup.
Use the [owned-session TCP helper](BACKGROUND_CONSOLE.md) for external dispatch on this build.
The window-message bridge remains available for older builds.
TCP reaches the GUI's interpreter; it does not turn `ntopcl` into a Notebook API process.

`list_available_blocks(mask)` uses a case-sensitive substring, not a glob.
Use a narrow mask and preserve exact type parameters and version suffixes. Do not insert spaces inside identifiers.
The bounded helper retains the newest version of each distinct overload:

```python
import block_catalog
block_catalog.lookup(notebook, "boolean_union<")
```

Function identifiers select block types. Use the returned `id` for instance operations such as `list_block_inputs`.
Use returned IDs after renaming; a display label is not a stable identifier.
Inspect inputs and properties on a small scratch block when the signature alone is insufficient.
Skip `isReturnValue: True` entries when reading or setting inputs. Preserve exact parameter spelling, including trailing spaces.

## Complete method surface

The following signatures omit `self` from the recorded build 42926 docstrings.
Names and argument order are exact, including `targetBlockId` and `placeBefore`.

<!-- recorded-signatures:start -->
```text
add_block(identifier: str, section_id: str = '') -> dict
add_section(section_name: str, before_section_id: str = '') -> dict
add_variable(new_name: str, block_id: str = '') -> dict
append_to_list(source_block_id: str, target_block_id: str, target_list_id: str) -> None
block_state(block_id: str) -> dict
clear_block_input(block_id: str, parameter_name: str) -> None
close_current_open_custom_block() -> None
connect_block_property(source_block_id: str, property_name: str, target_block_id: str, parameter_name: str) -> None
current_open_custom_block() -> dict
delete_block(block_id: str) -> dict
delete_variable(block_id: str) -> dict
export_as_recipe(recipe_path: str, recipe_only: bool = False) -> None
get_block_input(block_id: str, parameter_name: str) -> object
get_block_input_units(block_id: str, parameter_name: str) -> str
import_recipe(recipe_path: str) -> None
list_available_blocks(mask: str = '') -> list[str]
list_block_inputs(id: str) -> list[dict]
list_block_properties(block_id: str) -> list[dict]
list_blocks(section_id: str = '') -> list[dict]
list_custom_blocks() -> list[dict]
list_sections() -> list[dict]
list_variables() -> list[dict]
move_block(block_id: str, targetBlockId: str, placeBefore: bool = False) -> dict
new_notebook() -> None
open_custom_block(name: str) -> None
open_notebook(notebook_path: str) -> None
rename_variable(block_id: str, new_block_id: str) -> dict
save_notebook() -> None
save_notebook_as(notebook_path: str) -> None
set_block_input(block_id: str, parameter_name: str, value: object, units: str = '') -> None
set_block_input_units(block_id: str, parameter_name: str, units: str) -> None
```
<!-- recorded-signatures:end -->

`append_to_list` takes a list input's **name** as `target_list_id`.
`rename_variable` takes the new variable **name** as `new_block_id`.
`open_custom_block` takes the custom block's display name, not its function identifier.

## Values and units

Live setters and getters support **real, vector, point, integer, bool, and text**.
The recorded [type probe](evidence/api-42926-types.json) covers real, integer, bool, and text.
Point/vector behavior is supplied-package evidence. The supplied skill specifies three components.
The getter docstring's two-item description is a known documentation conflict, not a two-dimensional point contract.

Use complete recipes for enums, file paths, lists, and direct `real_field` literals.
An unsupported getter or a connected expression can raise even when the graph is valid.
An unset readable input returns `None`.
The supplied skill reports strict bool/int/text typing; do not rely on coercion.

| Operation | Meaning on build 42926 |
|---|---|
| `set_block_input(id, name, value, units)` | Interpret the supplied real, vector, or point in the named unit |
| Setter with no `units` | Interpret dimensioned values in the application's current display units |
| `get_block_input` plus `get_block_input_units` | Return a value and its display unit, not the originally typed expression |
| `set_block_input_units` on a dimensioned value | Preserve the quantity and rewrite its expression in the requested unit |
| `set_block_input_units` on a bare number | Attach the named unit to that number |
| Recipe literals | Explicit SI dimensions and values, including radians for angles |

For a known sphere instance in a scratch notebook:

```python
notebook.set_block_input(sphere_id, "Radius", 1.0, "in")
radius = notebook.get_block_input(sphere_id, "Radius")
display_unit = notebook.get_block_input_units(sphere_id, "Radius")
```

In a notebook displaying millimeters, the expected radius is 25.4 and the unit is `mm`.
Record both fields. Do not assume every notebook uses millimeters.
Typed unit text can appear in an input box but is not exposed by these getters.
The recorded unit setter says a later global unit change can clear that stored expression text.

`set_block_input_units` supports real inputs and real_field inputs holding numbers.
It refuses point/vector inputs and computed fields. Direct `set_block_input` still refuses real_field values.
Connect a dimensioned real variable when driving a field-valued tolerance or blend radius.

The first explicit unit can fix the dimension of a previously dimensionless input.
Wrong dimensions, unknown units, declared bare ratios, and absolute-temperature units are rejected as documented.
Set angles with `deg` or `rad` in the live setter. Keep recipe angles in SI radians.
Demo helpers that explicitly accept degrees retain their own documented conversion boundary.
Negate a length by multiplying by dimensionless -1, not by subtracting it from dimensionless zero.

## Variables, properties, and repaired connections

Wrap a computed output with `add_variable(name, block_id)` before using it in multiple downstream inputs.
The supplied skill reports dropped connections when one plain block is reused.
Use `rename_variable` for an existing `core.var<T>`; wrapping it creates another variable.
`add_variable(name)` without a block creates an empty variable, not a typed literal.
For a literal, create `core.var<real>` or another supported type, set `Input`, then rename it.

A variable wrapping a computed block can expose its supported scalar result through `get_block_input(id, "Input")`.
A variable holding a property connection is not guaranteed to return that property's value as a literal.
There is no `get_block_property` method. Inspect exported wiring and evaluate a downstream measurement.
An error alone proves neither correct wiring nor a correct value.

Getters and setters look through variable wrappers for named inputs.
`list_block_inputs` reports the named wrapper's own interface.
Connection and clearing operations must address the actual target parameter; they do not inherit getter traversal.
Keep raw inputs complete before wrapping when practical.

Properties are one level per connection. Use the exact names from `list_block_properties`.
Materialize intermediate expressions for longer paths. Reused property owners need variables too.
The supplied skill reports integer `round`, `floor`, and `ceiling` properties on real-valued blocks.
Use a verified integer property when a computed count cannot accept a real output directly.

Build 42926 documents input repair with `clear_block_input`:

- A variable or property reference is disconnected; its source remains.
- A nested block held in the input returns to the top level above its consumer.
- Clearing an empty input succeeds. A default value can remain unchanged after a successful call.
- Raw and nested targets are documented. A failed clear of a wrapped mesh `Input` remains a separate recorded case.

Inspect the target after clearing, then reconnect and verify the exported recipe.
Do not make a complete rebuild the default response to a repairable reference.
If the specific wrapper target still refuses repair, finish a replacement raw block and reconnect its consumers.

`list_blocks()` covers only the first section by default. Iterate all sections for a complete top-level inventory.
Nesting removes a block from that inventory without deleting it.
The docstrings describe nested access for several calls, while the supplied skill reports some failed nested lookups.
Treat reachability as method-specific. Preserve returned IDs and verify the exact operation.
`list_variables()` reports variables across the notebook and includes the wrapped `blockFuncId`.
Use `delete_variable` for a variable and `delete_block` for an ordinary block.
Remove dependent consumers before a source when references prevent deletion. Historical deletion timings are not current-build benchmarks.

## Lists and repeated features

Use native list processing when the same operation applies to many items.
The package demonstrates a scalar list feeding points, cylinders, and subtraction tools through a shared graph.
Keep reusable list outputs in named variables. Verify item counts, positions, units, and final geometry.
A fixed block count alone does not prove the result.

Seed slot `"0"` in `core.list<T>` when the target has no list to append to.
Connect that list to a list-typed consumer, then use `append_to_list` on that consumer.
An explicit `core.var<list<real>>` can hold a seeded literal list while it grows.
Fresh Bodies and Curves inputs can already hold empty lists; inspect the actual target.
Appending uses the source output, not one of its named properties.

The supplied skill reports that `add<real,real>` does not lift where the reducing `add<list<real>>` overload conflicts.
The package uses subtraction and multiplication to form an equivalent expression.
Check overloads, dimensions, and a small numerical case before applying that pattern.
Direct list-value readback remains unsupported. Use structural checks and evaluated downstream measurements.

## Sections, movement, and evaluation

`add_section` appends or inserts before a section ID. No section-delete or section-move method is documented.
`move_block` reorders a top-level block or moves it into the target block's section.
The two IDs must be distinct top-level blocks. Nested blocks cannot be moved this way.
Its documented behavior retains identity, inputs, connections, and build state.

```python
notebook.move_block(block_id, targetBlockId=target_id, placeBefore=True)
```

Use this method for supported live ordering. Saved-file helpers still handle visibility and collapse state.
They require a separate output and an unchanged geometry graph.

`block_state` returns `blockId`, `buildState`, and `pauseState`, plus `error` on failure.

| Build state | Interpretation |
|---|---|
| `e_OK` | Built successfully; still verify dimensions and geometry |
| `e_DIRTY`, `e_QUEUED`, `e_BUILDING` | Incomplete evaluation; neither a success nor a failure verdict |
| `e_FAILED` | Evaluation failed; retain the returned error |
| `e_UNBUILDABLE`, `e_WEAK` | Documented states with insufficient interpretation here; investigate before accepting the output |

Pause states are `e_UNPAUSED`, `e_PAUSED`, and `e_RUN_ONCE`.
Wire-time success can precede an evaluation failure, including a dimensional error.
Command completion, block evaluation, mesh export, and viewport rendering are separate events.

## Custom blocks, files, and recipes

While a custom block is open, console operations work on its contents.
Check `current_open_custom_block()` before exporting: `export_as_recipe` exports the open custom block in that context.
Close it to work on the notebook. Closing when no custom block is open raises.
The API edits existing custom blocks; no dedicated create/import-custom-block method is listed.

`new_notebook` and `open_notebook` discard unsaved work without prompts.
`save_notebook_as` and recipe export overwrite existing files. Create the destination directory first.
Operate on the task-owned notebook and retain separate working and deliverable files.
`save_notebook` uses the current file path and raises if the notebook has never been saved.
The save-as and recipe-export methods apply `.ntop` and `.json` extensions, respectively, as their recorded docstrings describe.

`import_recipe` merges blocks and appends recipe inputs, according to its recorded docstring.
It also takes the recipe's name and description. It does not replace the open notebook.
`export_as_recipe(..., recipe_only=False)` includes extended custom-block and state data by default.
Use `True` when only the recipe is required.

Complete recipes can carry `inputs` and `output`; preserve them during replay.
There is no dedicated live method to promote a block to a notebook input or set a notebook output.
Input merging is documented; a complete newly authored Automate input/output workflow was not tested by this audit.

The later [assembly-skill pilot](../.agents/skills/ntop-assembly-modeling/references/generic-pilot.md) supplies recorded build 42594 CLI evidence for complete part inputs, custom imports, and implicit outputs. It uses `convert --ext` and `exportjson --ext`; it does not establish live API promotion or build 42926 compatibility.
Do not turn that remaining verification gap into a claim that recipe-based authoring is impossible.

Cross-import references are not a substitute for a complete dependency closure.
Use this repository's build and stage helpers, then compare the native recipe readback.
The [archived reference](API_REFERENCE_42594.md#5-authoring-literals-the-api-refuses-to-set) retains measured recipe encodings; its old type restrictions do not apply to this build.

Dedicated camera, visibility, comments, title/description setters, indexed list-slot editing, block duplication, and version switching remain absent from this recorded surface.
Saved-file and native-render tools are separate workflows. Their success does not establish a missing API method.
