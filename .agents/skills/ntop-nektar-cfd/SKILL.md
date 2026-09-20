---
name: ntop-nektar-cfd
description: "Prepare nTop implicit geometry for a compatible Nektar++ integration, curve hybrid meshes, run compressible cases, diagnose validity failures, and postprocess fields."
---

# nTop to Nektar++ CFD

The source workflow used a custom Nektar++ integration and nTop Core SDK during the July 2026 AGARD-B campaign.
Stock Nektar++ availability does not establish support for `projectimplicit`.
Require the compatible integration source/build, licensed SDK, AFLR3 tools, MPI runtime, and solver documentation.
These dependencies and the former cloud fleet scripts are not bundled.

## Workflow

1. Export a surface mesh and matching implicit body from the same native revision. Record units and hashes.
2. Check surface-to-implicit agreement before meshing. Use a geometric distance query or a documented field normalization before reporting length errors.
3. Generate a hybrid volume mesh and preserve boundary tags.
4. Curve the mesh using the compatible integration, then check round-trip Jacobians and surface agreement.
5. Run a short compressible-flow case. Check finite fields and boundary behavior before increasing order, duration, or case count.
6. Convert fields with the same mesh and expansion definitions used by the solver.

Read [meshing](references/meshing.md), [solving](references/solving.md), and [postprocessing](references/postprocessing.md) for the relevant stage.
The [conditions template](assets/conditions_ns.xml) preserves a historical laminar demonstration.
Replace all marked parameters and confirm composite IDs, gas assumptions, viscosity, and boundary conditions before use.

The source integration used build options including `NEKTAR_USE_NTOPCORE`, `NTOPCORE_ROOT`, CGNS, MPI, and solver enablement.
Inspect the integration's own build instructions. Do not assume those options exist upstream.
Record the integration commit and shared-library environment with each run.

Passing a sampled Jacobian check is necessary but does not establish solver validity or resolved wall gradients.
Keep source-build limitations visible. Use [engineering-report](../engineering-report/SKILL.md) for figures and evidence.
