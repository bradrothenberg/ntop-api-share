# Recorded propeller lessons

See [the shared technical lessons](../../docs/PROPELLER_LEARNINGS.md) and [build 42926 API guidance](../../docs/API_42926.md).

The assembly uses an eight-inch, two-blade NACA 0015 propeller with an assumed four-inch pitch.
The motor interface uses a documented M5 adapter and a 5.10 mm modeled bore.
A separate spinner attaches through a locating boss and central M3 screw to a custom M5 adapter nut.
Thread cylinders are nominal interfaces. The source notes list the remaining manufacturing and qualification work.

Ten original shape studies use elliptical sections. Ten later candidates apply airfoil sections to the same shape families.
Eight later cases use NACA 0015. Two half-twist ribbons use a NACA-derived fore-aft symmetric section and NACA 0030 supports.
The three-petal and folded-loop revisions retain untrimmed curved tips in both sets.
All final NACA candidate exports had one watertight component with consistent winding.

Replay retains construction functions, connections, literal values, units, and guide coordinates.
It does not repeat the original algorithmic generation, CFD campaign, optimization, or recorded measurements.
Native screenshots are copied from the completed source work. The published graph recipes are audited offline.

## Folded half-turn correction

The previous folded-loop guide used a periodic roll with zero net half turn. The revised airfoil case exchanges edges after 180 degrees.
It uses two half sweeps and a fore-aft symmetric section. Its mesh is one watertight component, with measured diameter 202.474 mm.
Visible native edge ripples remain in this topology study. The smooth marine return uses one uninterrupted sweep and a closed spline profile.
