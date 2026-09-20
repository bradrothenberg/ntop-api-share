# ntopCL JSON Input / Output Reference

Recorded source schema. The selected executable's generated templates take precedence.
Forward slashes are also usable where accepted by the target platform.
Inspect enum encodings and iteration behavior in a small run before scaling.

## Input file structure

The file is a dict with an `inputs` array. Each input:

```json
{
  "description": "",
  "name": "Length",
  "type": "real",
  "value": 7.0,
  "units": "mm"
}
```

- `name`, `type`, `value` (or `values`) are required. Each input is matched by `name` - names must be unique and match the notebook exactly.
- `description` is optional. `units` is required, optional, or ignored depending on type (below).

Full example:

```json
{
  "description": "",
  "inputs": [
    { "description": "", "name": "Output directory", "type": "text", "value": "C:\\CLI-numtext\\" },
    { "description": "", "name": "Length", "type": "real", "units": "mm", "value": 7.0 },
    { "description": "", "name": "Width",  "type": "real", "units": "mm", "value": 2.0 },
    { "description": "", "name": "Height", "type": "real", "units": "mm", "value": 2.0 }
  ],
  "title": "Surface Area of Box"
}
```

## Supported types

| Type | `type` string | Notes |
|------|---------------|-------|
| Boolean | `boolean` | `true`/`false`, not quoted. (nTop also accepts 0/1 as boolean integer values.) |
| Scalar | `real` / `scalar` | integer or float; units optional |
| Integer | `integer` | integer only, no units |
| Text | `text` | string |
| File Path | `file_path` | valid path string; **backslashes need JSON escaping** (`"C:\\Outputs\\x.stl"`) per JSON escaping |
| Point | `point` | array of numbers, e.g. `[0,0,10]` |
| Vector | `vector` | array of numbers; units optional, but **some vectors require units** or the notebook won't run |
| Enum | `enum` | array of integer index ids matching the dropdown order (0-based). Find the id from the block's dropdown. |

## Iterative runs (`values`)

Swap `value` for `values` and pass an array. The notebook is built once and run once per set:

```json
{
  "inputs": [
    { "name": "Resolution", "type": "scalar", "values": [2.5, 3.1], "units": "mm" },
    { "name": "Path", "type": "file_path", "values": ["d:\\auto1", "d:\\auto2"] }
  ]
}
```

Rules:
- Every varying input must have the **same number of values**.
- An input that stays constant can list a **single** value - it's reused across all runs:

```json
{
  "inputs": [
    { "name": "Scale", "type": "vector", "values": [[0.003,0.003,0.003]], "units": "m" },
    { "name": "Path",  "type": "file_path",
      "values": ["C:\\Out\\1.stl","C:\\Out\\2.stl","C:\\Out\\3.stl"] },
    { "name": "Rotation", "type": "vector", "values": [[1,1,1]] }
  ]
}
```
Here the notebook builds 3 times (3 paths), with Scale/Rotation constant.

For a full factorial grid across **two or more** list inputs, enumerate the Cartesian product first. Use one JSON per combination or explicitly paired arrays for all combinations.

## Output file structure (`-o`)

The recorded scalar-output example is an array of named output objects. Iterative and grouped output shapes depend on the build; inspect the generated output template and a small run. Fields include: `name`, `type`, `value`, `components`, and `properties` (only if `-p` was passed).

```json
[
  {
    "components": [],
    "name": "SurfaceArea",
    "type": "real",
    "value": { "isFinite": true, "units": { "length": 2 }, "val": 6.34e-05 }
  }
]
```

- `value` is the serialized value, or `null` when unavailable.
- List/group outputs put their items in `components` (same shape, minus the `name` key).
- With `-p`, each object gains a `properties` array of `{name, type, value}` objects.
- `units` is encoded as exponents per dimension (e.g. `{"length": 2}` = area).
