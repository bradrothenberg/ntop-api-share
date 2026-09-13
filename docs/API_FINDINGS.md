# Notebook API findings

**Historical build 42594 findings.** Read [the build 42926 update](API_42926.md) for changed type, unit, clearing, and transport behavior.

Use [the current method reference](API_REFERENCE.md) for new work. The sections below retain their original experimental scope.

| Historical issue | Build 42926 status |
|---|---|
| Three writable types | Six types are supported: real, vector, point, integer, bool, and text |
| Unspecified setter units | Explicit units and display-unit getters are available |
| Wrapped inputs inaccessible | Getters/setters traverse wrappers; other methods have distinct target rules |
| Existing variables may be renamed by wrapping | Use `rename_variable`; `add_variable` can create a second wrapper |
| Rebuild after a bad connection | `clear_block_input` documents repair; retain the separate failed mesh-wrapper case |
| No external console channel | The supplied package documents loopback TCP from process startup |
| No block movement | `move_block` reorders top-level blocks and changes their section |
| No notebook input/output methods | Dedicated methods remain absent; recipe input merging is documented, and full Automate authoring needs separate verification |

These status updates reconcile source documentation and recorded evidence. They are not a new native test run.
These earlier failure records are retained as evidence, not restated as current limitations.

Eleven behaviors found while building the example export with the
prototype Notebook API, and then trying to make the result sweepable.
Measured on **nTop 6.0.0-rc, build 42594**, 29 and 30 August 2026. Error
text is verbatim.

Severity reflects an agent's experience of the API:

| | Meaning |
|---|---|
| **Blocker** | Stopped work outright until a workaround existed |
| **Trap** | Produces wrong results or a dead end, silently or confusingly |
| **Note** | Behavior to document rather than change |

Numbering follows the order of discovery. By severity:

| Severity | Findings |
|---|---|
| Blocker | 11, 1, 2 |
| Trap | 3, 4, 5, 6, 7, 8 |
| Note | 9, 10 |

Finding 11 is the one to read first. The other ten cost time; that one
caps what the API can produce.

Historical findings 1, 2, 5, 6 and 8 reproduced with a source-workspace probe in about
a minute: `probe.setters`, `probe.wiring`, `probe.import_probe`.

---

## 1. Blocker: `set_block_input` covers three types out of many

```
Parameter "0" of block "Text List_0" has type "text",
which cannot be set yet; only "real", "vector" and "point"
parameters can.
```

The same refusal applies to `file_path`, `real_field`, `integer`,
`bool`, and list-typed parameters.

**Why it blocks.** This export needs 57 text keys and one output file
path. Neither can be authored through the API at all. A block driven by
an integer, such as `polar_array_implicit`'s Count, can only be edited
by hand.

**Workaround.** Carry such literals in a recipe fragment and
`import_recipe` it, which merges rather than replaces. It works, but it
means maintaining a second authoring channel with its own value
encoding, and a recipe cannot reference blocks already in the notebook,
so the two channels have to be stitched together with
`connect_block_property`.

**Note for a fix.** `real_field` may be the cheapest win: the input
already accepts a *connection* from a `real`, so only the literal path
is missing.

---

## 2. Blocker: setters silently use display units

Reading a 5.4864 m chord on a notebook displaying inches:

```python
notebook.get_block_input("C_root", "Input")   # -> 216.00000000000003
notebook.set_block_input("C_root", "Input", 6.0)   # sets six INCHES
```

The recipe format is the opposite: it stores SI with an explicit `units`
map. Code that reads a value through one channel and writes it through
the other rescales the model by 39.37, with no error and no warning.

**Why it blocks.** An agent cannot know the notebook's display unit from
the API. Nothing exposes it. The only safe practice is to write a value,
read it back, and compare, which does not help when the correct value is
not known in advance.

**Suggested fix.** Accept and return SI, matching the recipe format and
nTop's internal storage. Failing that, expose the display unit so a
caller can convert deliberately.

---

## 3. Trap: `add_variable` wraps rather than renames

Calling `add_variable("FX fuselage Mass Properties", mp_id)` on an
ordinary block returns a new `core.var<T>` that wraps it. Wiring to the
returned id then fails:

```
Block "FX fuselage Mass Properties" has no parameter named "Body".
```

The wrapper's only input is `Input`. Worse, the inner block becomes
unreachable through one function but not the other:

```
No block with the id "Mass properties_0" exists in the notebook.
```

That is `set_block_input` refusing an id that `connect_block_property`
resolves without complaint in the same session. Two functions, two id
scopes.

**Workaround.** Set every literal input **before** naming the block,
keep both ids, and wire inputs to the inner one. The reply's `funcId`
reveals which happened: a block that is already a `core.var<T>` is
renamed rather than wrapped, and then the two ids are the same.

**Suggested fix.** Make the id scopes consistent between the two
functions, or document the wrap clearly and return both ids.

---

## 4. Trap: reusing an output silently drops connections

Wiring one plain block's output into two inputs leaves all but one
input empty. No error is raised, and the notebook computes with a
missing input.

**Why it matters most.** Every other item on this list announces itself.
This one produces a model that looks complete and is wrong. It is the
single behavior most likely to make an agent report success on a broken
build.

**Workaround.** The moment an output feeds more than one place, make it
a variable and reference the variable everywhere. `append_to_list` and
`connect_block_property` both accept a variable name where a block id is
expected, which makes this cheap once you know.

**Suggested fix.** Raise on the second connect, or auto-promote to a
variable. Silence is the problem, not the restriction.

---

## 5. Trap: property paths are one level deep

```
Block "Fuse" has no property named "bounding box.min point".
Block "Fuse" has no property named "bounding box/min point".
```

**Cost.** Every property hop needs its own `core.var<T>` block. Reaching
`Fuse.bounding box.min point.x` takes three intermediate blocks. This is
the main reason the export section is 88 blocks rather than roughly 30,
and it triples the size of any measurement chain.

---

## 6. Trap: list seeding rules are per-block and undiscoverable

```
Input "Values" of block "Dictionary_0" holds no list to append to.
```

Yet `boolean_union`'s `Bodies` input needs no such treatment: two bare
`append_to_list` calls filled slots 0 and 1 and nTop created the
`core.list<implicit>` itself.

**Workaround.** Seed slot 0 through a `core.list<T>` container, connect
the container in, then append the rest. On the first append nTop inlines
the list into the consumer and refers to slot 0 directly, which leaves
the container detached and reading `Empty` in the tree, so it then has
to be deleted.

**Suggested fix.** Make `append_to_list` create the list when the input
is empty, everywhere, as `boolean_union` already does.

---

## 7. Trap: `import_recipe` overwrites the notebook's identity

The merge behavior is good: importing a one-variable recipe left all six
sections, all 31 variables and all six custom blocks untouched, and
added the new variable.

The side effect is not. The import also takes the recipe's `displayname`
and `description` wholesale, so importing a recipe named "Example Export
Literals" retitled `Example Notebook` to that in the tree header.

**Workaround.** The literals recipe now carries the host notebook's own
title back, which means the generator has to know the name of the
notebook it will be imported into.

**Suggested fix.** Merge the body without touching the host's identity,
or make that a flag.

---

## 8. Trap: fresh variables arrive with a value that blocks connection

```
Parameter "Input" of block "FX fuselage CG" already has a value,
which this call does not replace.
```

A newly added `core.var<point>` holds a default, and
`connect_block_property` will not overwrite it.

**Workaround.** Call `clear_block_input` first. Doing it unconditionally
would mask genuine wiring mistakes, so the build only clears after the
plain connect has failed with this specific message.

---

## 9. Note: deletion is asymmetric, ordered, and slow

```
"Scalar_0" is a variable; use deleteVariable() to remove it.
```

Three separate constraints:

- `delete_block` refuses variables; `delete_variable` is a different
  call.
- Order matters. A block still feeding something else will not delete,
  so removal has to run in reverse creation order with a second pass for
  whatever the first pass freed.
- Each delete re-evaluates the notebook. Removing the 88-block export
  section takes minutes of wall clock.

There is also **no `delete_section`**. A section added by mistake is
permanent; this repo's model still carries an empty `FALCON SCRATCH`
section from probing.

---

## 10. Note: the API has no entry point outside the GUI

The API exists only as an object inside the GUI's Python Console. There
is no socket, pipe, or stdin channel, and `ntopcl.exe` contains no
Notebook API bindings.

The historical console transport existed to work around that, and
three separate failure modes had to be engineered out:

- **The Windows clipboard wedged mid-session.** Every `Set-Clipboard`
  call began failing with *"Requested Clipboard operation did not
  succeed"*, with no owner reported by `GetOpenClipboardWindow` or
  `GetClipboardOwner`, and it never recovered. A wedged clipboard is a
  machine-wide condition that cannot be fixed from inside the script.
- **Simulated typing drops leading characters.** Seen repeatedly as a
  prompt line missing exactly its first nine characters, which then ran
  as a `SyntaxError` while the intended command never ran. Longer waits
  did not help; the script now reads the prompt line back and retypes
  until it matches.
- **The console buffer scrolls.** Completion was detected by watching
  the buffer grow, which stops working once the buffer hits its size
  limit, so finished commands were reported as timeouts.

**Suggested fix.** A local socket, named pipe, or stdin channel into the
console would delete this entire layer and make the API usable from CI.
This is the single change that would most improve the API for automated
use.

---

## 11. Blocker: the API cannot make a notebook automatable

There is no `add_input`, no `promote_to_input`, and no `set_output` in
the surface. Both are GUI actions today.

**Why this is the sharpest gap.** The API authors notebooks. It cannot
author the two things that make a notebook runnable by anything except a
person. A notebook built entirely through this API has no inputs for
`ntopcl -j` to set and no output for `ntopcl -o` to return, so it cannot
be swept, batched, or put in CI. The API produces models that only the
GUI can drive.

**Measured on the finished model.** `ntopcl -t` returns an empty input
template:

```json
{ "description": "", "inputs": [], "title": "Example Notebook" }
```

and fails on the output:

```
Error generating output template : Output of function not set
```

exit code 1. A run with `-o run_out.json` produced **no file at all**.

Every design variable in this model is a `core.var<real>`: `C_root`,
`Angle`, `Panel 1 LE Angle`. `set_block_input` writes to them happily.
None of them is reachable from `ntopcl`.

**Partial workaround, and its limit.** Export blocks fire headless even
with no output set. `ntopcl` on this model built the whole `FX` chain,
ran `FX Export`, rewrote the measurements file, and exited 0:

```
FX JSON complete 0ms
JSON File Data_0 complete 0ms
FX Export complete 0ms
nTop successfully built.
```

The rewritten file matched the previous one bit for bit. So a notebook
can report results headless by writing its own file. That is enough for
a single run and not enough for a sweep: the export path is a
`file_path` literal, identical in every run, so N design points either
overwrite each other or collide outright in parallel.

**The recipe format already carries both.** Read from a real generated
recipe, not inferred; the fragments are kept in
`reference/automate_schema_example.json`:

```json
"inputs": [ { "name": "Wing Density", "type": "real",
              "dimension": {"mass": 1, "length": -3},
              "description": "...",
              "contents": {"type": "real", "value": {...}} } ],
"output": { "id": "inst2663" }
```

A block consumes an input by index, `{"input": 0, "props": []}`, which
appears 9 times in that file. The output points at a body entry, there a
variable of type `json`.

**Untested:** whether `import_recipe` honors top-level `inputs` and
`output` when it merges. It is proven to merge the `body`. If it reaches
the other two, the gap has a workaround today and the fix is
documentation. If it does not, there is no programmatic route at all.
Worth answering before designing an API change.

**Suggested fix.** `promote_to_input(block_id, name, description)` and
`set_output(block_id)`. Between them they would turn an API-authored
notebook into something `ntopcl` can run, which is the difference
between authoring a model and shipping a pipeline.

---

## Reproduction in this handoff

These findings record earlier experiments. Historical probe scripts and their private fixtures are not included.
Use [the current setup](SETUP.md) for this checkout. `ntop_api.hello(notebook)` verifies a small import and scalar result.
The bundled demo builders exercise complete dependency closures. Re-measure any listed API behavior on a changed build.
