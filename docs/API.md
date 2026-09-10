# Notebook API lessons

Sources: full reference,
engine notes, and
API skill.
These observations describe the tested prototype.

## Author small, then author in bulk

Discover identifiers with list_available_blocks. Never infer an identifier from a display label.
Finish a block's inputs before another block consumes it. Consumption can nest it and remove it from top-level listings.

The live setter supports a limited type set.
Use an exported recipe for text, file paths, integers, Booleans, enums, and lists.
Boolean literals use {"val": false}. The I6 backend records notebook operations and imports one complete recipe.

References resolve within one recipe. A second recipe cannot reliably reference an earlier import.
Export each subsystem with its complete dependency closure. Do not split a graph at arbitrary variable counts.

## Reuse and properties

Wrap reused outputs in named variables before fan-out. The prototype can silently drop plain-block connections.
A successful call does not establish wiring.

add_variable wraps the block. Its wrapper exposes Input. Set literals before wrapping.
Property chains generally need a variable per hop: body, bounding box, point, coordinate.
Use an explicit computation when readback ignores a direct property reference inside a variable.
The I6 measured this with the negative property. Multiplying by -1 avoids the ambiguity.

Seed a typed list container for fresh list inputs, then append.
Some Boolean body lists accept direct appends. Use the observed signature.

## Units

| Boundary | Convention observed |
|---|---|
| Recipes | Explicit SI; angles in radians |
| Fresh GUI setter/readback | Inches and degrees in the tested default |
| Legacy Automate template | Millimeters and degrees |
| Measurement meshes | Explicit STL export in millimeters |

Display units can change. Read their declaration or perform a calibration check.
Dimensionally wrong connections can evaluate without a useful error.
Negate a length by multiplication, not subtraction from a dimensionless zero.
Arc length divided by radius is already in radians. Jet's degree-accepting angle helper needs conversion.

## Performance and presentation

Live mutation becomes slow in a large graph. Use the recorder and subsystem closures.
A setter can return before evaluation finishes. The next read can block.
It can report "was not carried out" after applying a value. Read before retrying.

Sections, visibility, colors, and cameras were applied through saved-file metadata.
Prove a byte-exact container round trip before editing metadata.
Compare function graphs and unit-carrying literal tables after organizing.

Saved files have different container version bytes.
The shared preparation tool locates the first chunk instead of assuming one version byte.
No general camera setter or Automate input/output authoring method was established for this prototype.
