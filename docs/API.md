# Notebook API lessons

Use [the current build 42926 reference](API_REFERENCE.md) for exact methods and [the change guide](API_42926.md) for migration.
The [documentation audit](API_DOC_AUDIT_42926.md) identifies source conflicts and evidence limits.
The [older reference](API_REFERENCE_42594.md) and failure log retain their build 42594 scope.

## Author small, then author in bulk

Discover identifiers with list_available_blocks. Never infer an identifier from a display label.
Finish a block's inputs before another block consumes it. Consumption can nest it and remove it from top-level listings.

Build 42926 supports real, vector, point, integer, bool, and text through live setters/readers.
Use an exported recipe for unsupported file paths, enums, lists, and direct real_field values.
Build 42594 required recipes for additional types, including text, integers, and Booleans.
Boolean literals use {"val": false}. The I6 backend records notebook operations and imports one complete recipe.

References resolve within one recipe. A second recipe cannot reliably reference an earlier import.
Export each subsystem with its complete dependency closure. Do not split a graph at arbitrary variable counts.

## Reuse and properties

Wrap reused outputs in named variables before fan-out. The prototype can silently drop plain-block connections.
A successful call does not establish wiring.

add_variable wraps the block. Use rename_variable for an existing typed variable.
Getters and setters traverse wrappers; input listings, connections, and clearing have their own target rules.
Finish raw inputs before wrapping where practical. Inspect the actual target before repairing a connection.
Build 42926 documents clear_block_input for reference removal and nested-block extraction.
Property chains generally need a variable per hop: body, bounding box, point, coordinate.
Use an explicit computation when readback ignores a direct property reference inside a variable.
The I6 measured this with the negative property. Multiplying by -1 avoids the ambiguity.

Use native list processing for repeated geometry when the operation and types support it.
Seed a typed list only when the target has no list; some Bodies and Curves inputs accept direct appends.
Watch for reducing-overload conflicts, including add<real,real>. Verify count and geometry, not only block count.
Computed integer counts can use the supplied skill's round, floor, or ceiling property route after identifier checks.

## Units

| Boundary | Convention observed |
|---|---|
| Recipes | Explicit SI; angles in radians |
| Build 42926 setter | Explicit units when supplied; display units otherwise |
| Getter and unit getter | Display units, not the originally entered expression |
| Legacy Automate template | Millimeters and degrees |
| Measurement meshes | Explicit STL export in millimeters |

Display units can change. Read their declaration or perform a calibration check.
Dimensionally wrong connections can succeed at wiring and fail only during evaluation. Check units and block_state.
Negate a length by multiplication, not subtraction from a dimensionless zero.
Arc length divided by radius is already in radians. Jet's degree-accepting angle helper needs conversion.

## Performance and presentation

The older builds recorded slow large-graph mutation and delayed reads. Re-measure performance on the selected build.
Use compact native list processing or complete recipe closures where each fits the graph.
An earlier setter reported "was not carried out" after applying a value. Inspect state before retrying an uncertain mutation.

Use add_section and move_block for supported live section creation and block ordering on build 42926.
Visibility, colors, camera, and collapse handling remain separate saved-file or rendering workflows.
Prove a byte-exact container round trip before editing metadata.
Compare function graphs and unit-carrying literal tables after organizing.

Saved files have different container version bytes.
The shared preparation tool locates the first chunk instead of assuming one version byte.
No general camera setter or Automate input/output authoring method was established for this prototype.
