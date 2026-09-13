---
name: ntop-assembly-modeling
description: Build editable nTop assemblies from separate part notebooks imported as custom blocks, with dimensioned input contracts, shared family geometry, explicit placements, and native verification. Use for modularizing large models or reusing parts without losing controls.
---

# Native nTop assembly modeling

Create a maintainable assembly from reusable part definitions. Keep each part editable, preserve meaningful controls, and verify the saved native result. A smaller main tree does not by itself establish faster evaluation.

Use the bundled [Notebook API skill](../ntop-notebook-api/SKILL.md) for live authoring, units, exact identifiers, and native rendering. Read the [current method reference](../../../docs/API_REFERENCE.md) before applying recorded build findings. Use the [CSG modeling skill](../ntop-csg-modeling/SKILL.md) for source reconstruction and the [HTML report skill](../engineering-html/SKILL.md) for evidence reports. Keep geometry fidelity separate from modularization.

Read [custom-block contracts](references/custom-block-contracts.md) before defining interfaces or updating imported parts. Run the [generic part-and-assembly pilot](references/generic-pilot.md) before scaling an unfamiliar build. Read [verification and GUI delivery](references/verification-and-gui.md) before final packaging.

## Choose part boundaries

Identify distinct families, repeated placements, shared constants, part controls, and assembly controls. Audit each output's complete dependency closure before splitting an existing notebook.

Save one notebook per distinct part family. Give it one native implicit body as its output. Expose only meaningful controls, with exact names, types, units, defaults, and coordinate frames. Keep meshing and export work outside that native output.

Do not preserve a rejected construction merely because it can become a custom block. If source accuracy matters, validate each family against its reference. Graph equality with an earlier model proves preservation, not source fidelity.

For instances with identical geometry inputs, evaluate the family once, wrap that result in a variable, and reuse it across placements. Different input combinations can require separate evaluations. A translated copy should reference a shared result rather than contain the whole part construction again.

## Establish the interface first

Prove one small part, one dimensioned control, and a two-instance assembly before importing a large model. Require correct input propagation, implicit outputs, saved-file readback, and actual native checks at two values.

The recorded work has no verified dedicated live API calls for marking notebook inputs or outputs. Do not invent `add_input` or `set_output` methods. Complete extended recipes provide the measured workaround: `inputs` and defaults, one `output`, complete embedded `imports`, and `cbRefs` indexes.

The bundled pilot verifies this contract through native CLI `convert --ext` and `exportjson --ext` on build 42594. It does not establish live Notebook API marking or build 42926 compatibility. Inspect the current build and repeat the pilot when the interface changes.

Use the actual identity and version returned by the saved part, with the exact input order. Do not assume a requested UUID survives conversion. An ordinary body-only recipe merge does not create the custom-block boundary.

## Build and update the assembly

Keep high-level size, spacing, motion, or placement controls in an assembly section. Connect them through named variables to part inputs or placement wrappers. Preserve the controls that already satisfy the user's resizing contract.

Record transform order and the rotation origin. Apply the source placement once. A body already expressed in the source world frame must not receive a second centering transform.

If holes and wall thicknesses must stay fixed, move feature centers or use verified stretch regions. Uniform scaling changes those features. Check boundary positions and local signs at nominal and changed sizes. Record any clamps and the applied values.

Read [fixed-feature resizing](references/fixed-feature-resizing.md) for the retained KestrelSAT map equations, protected-region limits, and required repeat checks after a geometry edit. Earlier map verification does not certify replacement CSG parts.

Imported custom blocks are embedded snapshots. Editing a source notebook does not silently update its consumers. Reimport the changed definition, verify the interface and every call, then validate the assembly again. Record source hashes and imported identities in a manifest.

Retain shared variables and property owners. Nest single-use construction where useful, then prove complete expanded output equality. Preserve literal types, exact values, dimensions, function overloads, properties, input defaults, and ordered arguments.

Large native packing is a conditional fallback, not a substitute for verified API behavior. It requires measured records for every function and interface, complete expression equality, native reopen, and geometry evaluation. No general native packer is supplied by this skill.

## Present the native assembly

Show the separate placed native implicit bodies. Hide source construction, unused family bodies, and helpers. Keep the native per-instance results individually accessible even if a downstream union is useful.

Use stable colors by family. Repeated instances should retain the same family color. Keep geometry, coordinate frame, and controls unchanged when adjusting presentation.

For the learned 28-instance case, the requested view shows all 28 direct native bodies. Do not replace that preference with a fast mesh or grid. A lightweight preview is an optional response to a measured display problem only when the user approves it; label any snapshot refresh requirement.

Use short sections for controls, placed outputs, family definitions, and helpers. Collapse authored blocks, input cards, custom sections, and imported-definition states. Preserve the root group. Reopen after the final save to check the actual state.

## Verify and hand off

Verify part outputs and inputs, distinct family count, instance count, transform order, bounds, and selected native field or mesh checks. Compare nominal and changed control values. Confirm that updated imports match the intended source revisions.

Keep source-fidelity checks, graph-preservation checks, native evaluation, and visual verification separate. An external baseline is needed for source accuracy. An exported recipe or a successful save does not prove rendering or correct geometry.

Measure main-tree complexity and all unique imported definitions separately. For timing, control the build, machine, inputs, thread count, visible bodies, display quality, and cache state. Measure opening and live GUI updates separately from CLI process time. Retain timeouts and unresolved warnings.

Deliver the assembly, editable family notebooks, dependencies, a revision manifest, and the verification record. Describe how a part edit reaches its consumers. Keep previous accepted files while validating replacements. The generic pilot is a small contract example, not a full production assembly or a performance benchmark.
