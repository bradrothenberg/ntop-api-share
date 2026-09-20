# Geometry and high-order meshing

This is an adaptation of the July 2026 custom-integration workflow, not a stock Nektar++ guarantee.

## Geometry contract

Use one body surface and matching `.implicit` from the same revision.
The source nTop Core route used meters. State the mesh and implicit units explicitly.
Sample agreement at surface points and at tips or other critical features before meshing.
Choose tolerances from the intended geometry and analysis; the source campaign's tolerances are not universal.
Keep the farfield extent and boundary tags in the case manifest and check domain-size sensitivity.

## Hybrid mesh and conversion

The source high-order approach used a thick prism macro layer that could accommodate wall curvature.
Thin anisotropic slivers inverted during curving in the source cases.
This macro layer alone did not resolve viscous wall gradients.
Do not substitute it for a verified wall-resolved RANS stack.

The CGNS ingestion route handled prism and pyramid ordering in the custom branch.
Its recorded composites were prisms, pyramids, tetrahedra, wall, and farfield in that order.
Inspect actual composites after every conversion. Do not assign boundary conditions from that historical order alone.

Illustrative recorded invocation, with case-dependent tolerances and order:

```text
NekMesh -v -f -m projectimplicit:field=body.implicit:units=m:order=3:projector=normal:tol=1e-7:surf=3 case.cgns curved.xml
NekMesh -v -f -m linearise:invalid=0 curved.xml checked.xml
NekMesh -v -f -m jac:list checked.xml .local/jacobian-check.xml
```

The values above describe the source example. Confirm module availability, syntax, surface composite, order, and tolerance for the current build.
Track nodes or elements relaxed or linearized by guards. A repaired mesh can have lower surface fidelity or local order.
Check surface error spatially and inspect tips, trailing edges, collapsed layers, and curvature transitions.
Run a separate saved-mesh Jacobian check. In-module checks and solver quadrature can sample different locations.

## Recorded boundary-layer split limitation

The source `bl` split produced meshes with passing sampled Jacobians but immediate solver NaNs.
The unsplit macro layer ran, but its weakly enforced wall conditions left unresolved near-wall behavior.
Do not claim that the split defect is fixed or that the unsplit workaround gives accurate wall shear.
Reproduce a small case on the selected integration before relying on either route.
