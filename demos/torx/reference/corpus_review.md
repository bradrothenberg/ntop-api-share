# Torx corpus review

Date: 2026-09-15. Read-only investigation: no geometry authored, no ntopcl execution, no new measured fact.

## Finding

The master pair contains the native vocabulary for a fully parametric closed circular-arc profile, extrusion, and arbitrary placement. No Torx or hexalobular generator was found in the searched text corpus. This is a search result, not proof that no such notebook exists. Official drive geometry and a numerical tolerance remain prerequisites to selecting the profile construction.

## Search and evidence

1. Read both `library/master/Library_master.ntop` through the seek-based container reader and `Library_master.json`. The binary main function has 1,440 code entries; the arc/profile/extrusion/frame signatures below occur in both surfaces.
2. Searched `work/doc_exports`; inspected Frame, Parametric Extruded Parallelogram, and Complete -- Modeling a Cylinder Head with Curves and Profiles. The cylinder-head example combines Arc by Tangent, Profile from Curves and Extrude Profile. The parallelogram demonstrates algebraic fields and remapping, not a Torx section.
3. Searched `knowledge`, `work/doc_exports`, `Utilities-community` and `projects` recursively for Torx/hexalobular in JSON, Markdown, JavaScript and Python. The only match was an unrelated archived web-image result; no relevant generator was identified. Read the master block cards and `scripts/brief.js` results, which join notes and usage.
4. Read complete exported definitions of Local Point, Field from Profile and Cylinder Inf Direction in `projects/vortex/reference/exemplar/cb`. Consulted the geometry and grammar analyses for the mature Nanuqx exemplar. The applicable grammar is: coordinates in a frame; a closed profile is one section field; derive dimensions inside the graph; bound or extrude once. An aerodynamic section-morphing chain is unnecessary for a constant drive section.

## Exact native candidates

| Signature | Ports in order | Role / limits |
|---|---|---|
| `three_point_arc<point,point,point>` | Start, intermediate, end | Circular arc. A candidate only when the authoritative profile actually consists of circular arcs. |
| `arc_by_tangent<point,vector,point>[5.20.0]` | Start point, start tangent, end point | Alternative circular-arc construction; shared junction coordinates are essential. |
| `arc_by_angle<axis,point,real>[5.23.0]` | Centre axis, start point, angle | Circle-centre construction; recipe angles are radians with angle dimension. |
| `profile_from_curves<list<curve_interface>,vector>[5.20.0]` | Curves, normal | Closed section. Normal dimensionless. Closure must reuse identical endpoints. |
| `extrude<new_profile,real,real,bool,vector>[5.20.0]` | Profile, distance, draft angle, symmetric, direction | Implicit output; distance has length dimension, draft has angle dimension. False symmetry produces 0..distance from profile plane, per existing measured notes. |
| `frame<point,vector,vector>` | Origin, X axis, Y axis | Right-handed local frame. Axes cannot be parallel. Z follows right-hand rule in official mirrored documentation. |
| `ntoptoolkits.create.point_in_frame<real,real,real,frame>[5.30.0]` | X, Y, Z, frame | Native local-coordinate point placement, present in master pair. Coordinates have length dimension in observed usage. |
| `transform_object<spatial3d,transformation>[1.1.0]` | Object, transformation | Alternative placement after construction. Polymorphic output requires correct typed variable. |

These signatures are resolved from the master pair. No new execution result is claimed for their combination.

## Mature custom blocks, read whole

| Full identity | Definition and assessment |
|---|---|
| `user_func_09e9c877_4a37_42e9_8259_c3e58f283396` — Local Point, version 1.0.0 | Inputs X/Y/Z length scalars and Coordinate Frame. Output point. Translates frame origin by each local coordinate times the corresponding frame axis using three translation transforms. It has an unused global point and default frame. This is a reusable placement exemplar; native Point in Frame already has matching semantic ports, so no need to rebuild this custom block. |
| `user_func_c3646965_4a7c_4d1a_8433_76b0fc4fdf64` — Field from Profile, version 1.0.0 | One node: reads input profile `distance to extrusion` into a typed real_field variable. Reusable if an infinite section field is needed. Direct extrusion can consume the profile without it. |
| `user_func_23177cee_d27e_4c60_a4ee_a995976d8a2d` — Cylinder Inf Direction, version 1.0.1 | Axis from point/direction, offset by radius, fixed 0.254 m preview bounds. Not recommended for Torx because finite extent and driven bounds are needed. |

If any custom block is used, import unchanged by full UUID, include dependencies and root cbRefs, and convert with --ext. Do not flatten or regenerate it.

## Candidate construction and verification boundary

Conditional on obtaining official circular-arc profile data: compute all circle centres, radii and shared tangency points in notebook expressions; make alternating arc segments; assemble one closed curve list; create one profile; extrude by requested length; place with an insertion point and orthonormal frame. A surface-normal axis plus an in-plane reference direction fixes both axial alignment and roll. A single axis alone cannot fix roll.

No official Torx profile coefficients have been inferred from the nTop corpus. An arbitrary radius can represent uniform scaling, but its compliance with a named standard size must be settled separately.

Existing measurement traps:

- Profile from Curves has an endpoint-gap inversion trap; reuse shared points rather than independently recomputing the same junction.
- Existing spline-profile field measurements show adaptive tessellation errors up to approximately 0.62 micrometres in one glyph test. This does not establish the error for circular arcs; it means exact analytic curves do not by themselves certify the implicit field. Measure on-arc samples between obvious symmetry stations before choosing this route for the requested tolerance.
- Extruded implicit bounding boxes are padded, so they cannot certify depth or radius. Use field samples at predicted face positions.
- Volume integration has its own floor. Compare field samples and analytic geometry before using volume as a secondary check.
- Profile winding does not create holes. A security-pin feature needs explicit solid/cavity treatment according to the chosen output.
- `-j` cannot directly feed point/vector/list inputs. Scalar test wrappers can exercise placement while preserving typed point/vector inputs in the delivered custom block.

No aerospace compliance, fit, torque capacity, manufacturing tolerance or finished Torx geometry is verified by this review.
