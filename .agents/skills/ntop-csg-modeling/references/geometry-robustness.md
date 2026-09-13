# Geometry robustness and verification limits

Use these checks when the corresponding feature occurs. The corner demo is the compact reference; it does not include the larger panel or handle examples that motivated some of these lessons.

## Boolean fields and internal contacts

A native compound implicit field is not necessarily a signed-distance field. On recorded build 42594, blend enum 0 is Rounded and 2 is Sharp. A zero-radius rounded blend can preserve the zero set while changing interior field values. Inspect the installed build's enum and Boolean semantics before using exact min/max field algebra.

Two components that touch only on a face can leave an internal zero sheet in a min-union field. A regularized CAD union may remove that interface. When this occurs, extend one component into already retained stock and keep the external feature guards. Prove positive overlap and zero exterior difference, then probe the old interface in the native field.

Check cutters too. Extend a bore into an adjacent countersink only where the cone is already wider. Prove containment in the original complete cutter union. Another tool may already cover the suspected cap, so probe the complete cutter union before changing it. A narrowing transition needs a different construction.

For chamfered plate corners, a full-height cylinder intersected with full-height cones can express the same radius envelope as stacked pieces without internal cap contacts. Prove the geometric equivalence before adopting it. A construction-cell inradius is not physical wall thickness.

## Grouped profiles

Keep one profile for compatible coplanar closed wires with the same depth. Include an outer loop, hole, and separate island in a small native calibration when relying on their semantics.

Recorded build 42594's versioned Circle returns a profile, not a curve. A full Arc by Angle can provide a circular curve. Query exact identifiers and output types on another build.

A source CAD wire can have endpoint gaps larger than the native join tolerance. Preserve analytic arcs. A measured correction can move an adjacent line endpoint within the source gap or add a short connector. Check that the correction does not cross a neighboring edge. Require closed, degree-two endpoint groups and an actual native profile evaluation. Record the maximum change.

## Fillets and mouths

Derive a fillet from the source surface arrangement before selecting a smooth Boolean. At an oblique cylinder/end-plane junction, a rolling-ball centerline can be an ellipse. A perpendicular-plane shortcut can fail despite high whole-part overlap.

If using a conic-distance tube, verify its distance field and trim region in a small native pilot. An unrestricted tube can protect unrelated material. Contact endpoints alone may not delimit the valid region. This repository's corner example does not supply or validate a general handle-fillet helper.

For a rounded opening, preserve the throat separately from the mouth transition. Limit expanded mouth geometry to the fillet depth. Probe multiple axial and angular stations on both sides of the original cylindrical wall.

## Evidence and display warnings

Exact CAD Booleans can fail on complex but valid coincident solids. Retain the failure and cross-check classification. A documented converged mesh intersection can provide an alternative comparison; volume difference cannot replace intersection-over-union.

Imported display meshes require their own topology checks. A closed, manifold, oriented mesh can still report self-intersection. A prior isolated test retained every STL triangle and coordinate in indexed OBJ: the vertex-merging warning disappeared, but self-intersection remained. This does not establish the cause or prove a false positive.

Keep such warnings explicit. Test transport or repair changes in separate copies while retaining accepted native geometry and its evidence. Never suppress a warning by changing the claimed metric or silently replacing the accepted mesh.

A successful render, an exact graph audit, a source comparison, and a timing measurement establish different facts. Report each with its own scope.
