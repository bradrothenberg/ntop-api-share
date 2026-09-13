# Custom-block input, output, and update contracts

## Part interface

Record the following before wiring the assembly:

| Field | Required meaning |
|---|---|
| Input name and index | Stable visible name and exact positional argument order |
| Input type | The measured native type, including a scalar versus field distinction |
| Dimension and units | SI recipe dimension and value; GUI display units recorded separately |
| Default | Complete typed default expression, not only its displayed number |
| Valid range | A measured or designed range, with any clamp disclosed |
| Output | One native implicit body and its coordinate frame |
| Identity and revision | Actual saved custom-function identity, version, and source hash |

Expose part-specific features in the part. Keep assembly-wide positioning and overall controls at the assembly level unless they change part geometry. A fixed part can have no inputs; do not call it parametrically resizable merely because its construction is editable.

## Measured extended-recipe form

The pilot generator writes complete documents. Its part has a `Width` input with type `real`, dimension `{"length": 1}`, and a typed SI default of 0.010 m. The body uses an input reference with `input: 0` and `props: []`. Its `output.id` identifies a top-level implicit variable.

The assembly embeds the complete saved part recipe in `imports`. It registers that definition with `cbRefs: [0]`. Its custom calls use the exported part identity and version plus the exact argument types. Do not copy only the part's body array.

Use absolute resolved command paths when invoking native CLI conversion from scripts. Use `convert --ext` to load the complete document and `exportjson --ext` to read the native result back. Preserve the complete readback as evidence.

The native save can change an authored root identity. Read the actual saved recipe before constructing calls. For zero-input custom functions, measured native identities omit empty `<>`. Do not add version or signature text to an identifier that already contains it. Read the exact installed format instead of guessing.

No dedicated live API marking calls for notebook inputs or outputs were verified in this work. Source inspection can suggest support, but it does not equal a successful live pilot. Label CLI extended-recipe conversion, live API import, and conditional native container packing separately.

## Shared definitions and placements

One stored custom definition can serve several calls. That does not guarantee that all calls share one evaluation. Reuse one family result when its inputs are identical. Use separate calls when geometry inputs differ.

Keep repeated feature subtrees in named shared variables before fan-out. The prototype's plain-block connections can lose a branch. Complete raw inputs before wrapping, then use the returned variable ID for every consumer.

Preserve rotation origin, rotation, translation, stretch mapping, and output bounds in their verified order. Do not replace an existing fixed-hole/fixed-wall map with uniform scale.

## Update propagation

Imported definitions are snapshots inside each consuming notebook. Source edits require a deliberate import refresh. Interface changes can require replacing calls or reconnecting arguments.

After a part edit, verify the new standalone part first. Read its saved contract, update consumers, compare the embedded definition with that source, and recheck the placed outputs. Repeat through nested consumers. Do not claim a live link merely because the source path remains in metadata.

A manifest should record delivered relative paths, source and consumer hashes, actual function identities, input contracts, coordinate frames, and validation revisions. Search imported definitions for external file literals; embedded code does not make those files portable.

## Conditional native container work

The measured container uses imported models such as `sf0`, default-input models such as `sf0inp0`, and imported presentation state such as `sf0_state`. Match functions by their saved identity, not by an assumed numeric slot.

The recorded input wires use `instanceId: -1`, `modelInputIdx: J`, and an empty `propchain`. Length inputs retain `unitsReq: {length: 1}`. Re-measure these records on the target build before constructing or changing a native container.

The container header depends on chunk count. A fixed header offset from one sample is not a general reader. Preserve unknown chunks and inspect the complete written container before native reopen.

Recorded cache keys include standalone `main:107`, definition `sf0:107`, and direct-instance `main:102:107`. These examples are not a universal nested-cache mapping. Rebuild unsupported contexts instead of guessing.

Transfer a cache only after exact semantic matching of its complete source expression and input defaults. Preserve every non-cache chunk. Input-dependent caches must be invalidated after a control or geometry change. A cache is neither a substitute for its source dependency nor a geometry-accuracy proof.

The portable pilot uses CLI conversion, not native container edits. It therefore needs no private packer, cache library, or binary template.
