---
name: ntop-custom-assembly
description: "Reconstruct a measured assembly with reusable native custom parts and fixed-feature resizing. Use for the custom-assembly workflow and its KestrelSAT-derived contracts."
---

# Native custom assembly

This entry preserves the `ntop-custom-assembly` skill name from the experiment inventory.
Its portable implementation is consolidated into two maintained skills:

- [Assembly modeling](../ntop-assembly-modeling/SKILL.md): part definitions, input/output contracts, repeated instances, transforms, and controlled definition updates.
- [CSG modeling](../ntop-csg-modeling/SKILL.md): measured primitive reconstruction, analytic profiles, bores, recesses, and geometry verification.

Use both when rebuilding parts from a measured source assembly. Choose the assembly skill alone when the native parts already exist.

## Workflow

1. Record the source revision, coordinate frame, units, part identities, and assembly placements.
2. Reconstruct one representative part and compare volume, surface samples, and interfaces against the source.
3. Expose an explicit part input contract. Declare units, defaults, bounds, output type, and protected feature dimensions.
4. Store one definition per part family. Apply instance placements separately from part geometry.
5. Update imported definitions explicitly. Retain the preceding assembly until the updated interfaces pass their checks.
6. Exercise input changes at the baseline and at the intended range boundaries. Verify dimensions and clearances in native nTop.

Read [custom-block contracts](../ntop-assembly-modeling/references/custom-block-contracts.md) before creating or repairing inputs.
Read [fixed-feature resizing](../ntop-assembly-modeling/references/fixed-feature-resizing.md) when the envelope changes but holes or wall thicknesses must remain fixed.
Run the [generic pilot](../ntop-assembly-modeling/references/generic-pilot.md) before scaling a new recipe or import method.

The [source audit](../../../docs/KESTRELSAT_SKILL_AUDIT.md) identifies the consolidated versions and their recorded evidence.
The pilot's build 42594 evidence does not establish native execution on build 42926.
Use the [current API reference](../../../docs/API_REFERENCE.md) for current authoring.
