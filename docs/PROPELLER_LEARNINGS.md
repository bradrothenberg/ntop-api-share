# Lessons from the propeller studies

These lessons record native work on build 42926. They describe construction and verification, not qualified propeller performance.
The [shared propeller folder](../demos/propellers/README.md) carries audited recipes, two assembly notebooks, native screenshots, and selected measurements. CFD outputs and supplied photographs remain excluded.

## Sweep along Two Rails

The verified profile overload is:

```text
sweep_along_two_rails<new_profile,curve_interface,curve_interface,curve_interface,bool>[6.0.0]
```

Its inputs are Profile, Spine, Rail 1, Rail 2, and Caps.
In the rectangular calibration, Rail 2 anchored the section center. Rail 1 controlled width and relative rotation.
Using two section edges as rails doubled the intended width and displaced the section.
A center rail plus one edge rail produced the intended dimensions. Repeat this calibration for a different profile frame.
Apply root twist to the initial profile as well as the guides; guide rotation is relative to that initial frame.

Use a NACA section when the design intent calls for it, and record the specific section and trailing-edge convention.
NACA 0015 was used for ordinary blades. It is a baseline choice, not evidence of optimal efficiency or noise.
Keep profile coordinates, both rails, spine, caps, and native graph connections in the verification record.
Match all coordinate lists to the generator, not only the profile list.

## Closed loops and half twists

The working closed-loop pattern used:

```text
spline_through_points<list<point>,integer,bool,vector,vector>[5.28.0]
```

Set Degree to 3 and Closed to true. The reference left both endpoint tangent vectors unset.
The corresponding profile sweep retained Caps=true. Coincident endpoints on an open spline did not establish a closed sweep.

A half-twist ribbon exchanges section edges after one circuit. The studies used overlapping half sweeps and an explicitly symmetric section.
The ribbon was labeled NACA-derived, since imposing fore-aft symmetry changes the original NACA profile.
Do not drop a distinct endpoint while removing an assumed duplicate: this broke exact half-turn symmetry.
Check seam geometry and mesh connectivity after applying thickness. An ideal Mobius surface is not itself a printable solid.

## Natural tips and flat hub faces

A radial cylinder can cut an otherwise smooth loop tip into a flat face.
The corrected three-petal and folded-loop studies scaled the complete untrimmed sweeps to fit their envelope.
The outer radial trim was disabled. Validation checked the final diameter and absence of faces on the former clipping radius.

A smooth hub union can protrude beyond both nominal clamp faces.
The correction intersected the union with a revolved envelope: flat through the hub and adjacent roots, then smoothly relieved into the blades.
Measure the face region after export. Stopping the flat envelope exactly at the hub radius left small protrusions in the adjacent roots.

## Separate spinner retention

The spinner remained separate from the propeller. An internal boss and locating spigot positioned it.
A central screw attached to a custom adapter nut; the nut clamped the propeller independently.
The model used nominal threaded-interface cylinders. It did not model thread flanks, runout, manufacturing fit, or hardware qualification.
Check blade clearance, screw access, clamp load path, assembly order, and the motor interface separately.

## Native mesh and runtime evidence

AT with Remesh enabled, followed by Sharpen Mesh, produced the visualization exports.
Coarse settings created disconnected fragments. A finer export was checked for component count, watertightness, winding, and triangle area.

Retain raw exports before cleanup. Filtering a fragment by volume alone is insufficient: a long, thin artifact can have a very small volume.
The later cleanup measured fragment size and distance to the retained surface, then proved the retained surface vertices were unchanged.
A sampled distance is not a global distance bound. The stronger check subdivided discarded triangles and used distance's Lipschitz bound.
Keep the raw mesh hash, thresholds, removed-part records, and final mesh checks together.

Complete cheap remesh parameters before connecting an expensive Surface input. Live mutations can trigger repeated evaluation.
Recorded saved-notebook re-evaluation took as long as a full build for some loop models.
A nonresponsive window or high CPU load does not establish whether a command finished. Read its unique completion receipt first.

## Downstream CFD handoff

Declare mesh units and any coordinate permutation explicitly. Verify that the transform preserves handedness.
Check geometry and wall rotation numerically before interpreting thrust, efficiency, or wake pictures.
A solver launch, finite force history, or watertight surface does not establish convergence, boundary-layer quality, noise, or an optimum.
Keep smoke checks, failed mesh trials, baseline solves, and optimization results distinct in reports.

## Continuous marine return loops

A single open two-rail sweep can run from one axial hub attachment to the other through a smooth outer bend.
Use a closed cubic profile spline and continuous cubic guides. A rotation-minimizing frame avoids frame-axis switches.
Keep the outer bend inside one sweep, so no overlapping sweep endpoints meet at the tip.
A native edge-swap study may still show display ripples even when mesh topology passes. Report these checks separately.

The marine-prop revision uses smooth spline profiles and an uninterrupted outer return. It increases barrel diameter and root chord while burying the entire sweep end sections in the hub. Keep its service-cap retention separate from shaft torque transfer and axial propeller retention. A cover with screws does not establish a compatible splined drive.
