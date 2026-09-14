# Inline-six and jet assembly lessons

These lessons retain their recorded demo revisions. Use [the current build 42926 reference](API_REFERENCE.md) for API calls and units.

For reusable part notebooks, start with the [assembly modeling skill](../.agents/skills/ntop-assembly-modeling/SKILL.md). It includes a generic two-instance pilot, complete custom-block contracts, and [fixed-feature resizing guidance](../.agents/skills/ntop-assembly-modeling/references/fixed-feature-resizing.md) derived from KestrelSAT. Use the [CSG skill](../.agents/skills/ntop-csg-modeling/SKILL.md) for source reconstruction before modularization.

Sources: I6 notes,
Astra log, Jet log,
and joint builder.

Read the [recent assembly lessons](RECENT_MODELING_LEARNINGS.md) for the DDG(X) attachment/support checks and the KestrelSAT comparison of default and symbolic body expressions. Drive attachments from their actual supports and test contact across parameter states. Keep presentation changes separate from geometry evaluation.

## One definition per interface

Store dimensions once with units. Derive part positions and mating features from those values.
Build local parts, then place them with named transforms.
Separate visible assembly bodies, construction bodies, and checks.

Jet joint definitions generate holes and hardware placements together.
Through-joint checks include grip, two washers, nut height, and screw length.
Tapped joints need receiver bores and engagement.
A bolt pattern does not attach a floating module. Check the supporting bodies.

Hardware and bearing envelopes support layout.
They do not define production threads, preload, fits, torque transfer, or thermal capability.
Contacting surfaces can merge in a mesh while the bill of materials counts separate parts.

## Mechanisms

I6 piston and rod motion follow independent slider-crank equations.
Cams follow the crank at half speed. Valve lift must match the cam/follower geometry.
Compare native scalars across a crank cycle.

Move rod bolts with their rods. Keep housing bolts in the housing frame.
For Astra's open timing belt, cams rotate in the crank's direction at half speed.
A displayed belt path remains a packaging envelope until pitch, tension, and engagement are verified.

Test a kinematic dependency closure before the expensive assembly.
A posed mesh animation is not a full implicit reevaluation at every frame. Label the rendering method.

## Springs and gears

The sampled polyline helix made original I6 evaluation slow.
An analytic periodic field reduced graph cost. Clip it with a finite body.
Join closed spring ends to the active coil and count mesh regions.

Astra uses documented involute flanks. Radial decorative blocks cannot establish a gear pair.
Check clearance across a tooth period at adequate local resolution.
An unloaded geometric check does not establish stress, root strength, or durability.

## Hollow routes

A cubic spline needs at least four control points.
Offset its scalar field for the outer tube, then subtract an inner offset for the bore.
Distance-field endpoints otherwise close the tube with spherical caps.

Trim each cap with an outward halfspace inside a local sphere.
The measured workflow uses a sphere 1.05 times the outer radius.
An unrestricted halfspace can cut a remote bend.
Check both bore centers and the expected connected-component count.

Wires, pumps, and sensor bosses remain envelopes until interfaces are specified.
An open, watertight pipe can still cross an unacceptable region.

## Jet interfaces

The jet axis is +Z. Check passage continuity through compressor, diffuser, liners, guide vanes, and nozzle.
A shroud offset can close the radial compressor outlet. Inspect that interface in section.
Check the hollow tail cone against the rear nut and rotating shaft stack.

P1 recorded a rear-bearing feed crossing the combustion annulus.
The refreshed source includes P2 routing work. Check its native receipts before claiming a correction complete.
Mesh topology does not establish acceptable routing.

Extending a tapered nozzle cutter with unchanged endpoint radii changes its physical exit radius.
Account for cone slope when adding overrun.
The cycle connector reads native nozzle area but retains imposed efficiencies and pressure ratio.
Its result is conditional sizing, not measured thrust.

## Explain the assembly

Use one component inventory for assembled, exploded, and section views.
Document hardware, mating bodies, holes, and stack checks for each joint.
Exploded display offsets do not prove an assembly motion.

Measure original native exports. Use separately documented display copies for browser viewers.
Keep source hashes with figures and reports.

## P2 geometry checks added in the refreshed source

The diffuser backplate could close the radial turn while vane/post clearance still passed.
A connected free-space check must trace the passage into the liner air space.
The P2 source records the rejected P1 geometry and the corrected passage test separately.

A long unconstrained route spline can cross the combustor. Separate radial, bend, and axial spans make the route controllable.
Use the same coordinates for tube, housing passage, guides, and receiver. Include hardware in the interference screen.
Nearest-face pseudonormal signs gave false collisions in the recorded check. Use independent containment and unsigned penetration depth.
See the refreshed Jet LEARNINGS.md and route receipts for the sampled scope and remaining interface work.
