# LAVA v1.0.0 source lessons

These notes preserve useful findings from April 2026. They are not new solver validation or a statement about later releases.

## Unstructured build compatibility

| Recorded route | Implicit unstructured | Explicit unstructured |
|---|---|---|
| x86 CPU AVX2/AVX512 distribution | Supported in the source manual and CPU smoke test | Listed in the source manual |
| NVIDIA x86 GPU distribution | Unsupported in the recorded v1.0.0 path | Listed in the source manual |
| NVIDIA ARM GPU distribution | No CPU unstructured build in the inspected distribution | Listed in the source manual |

The source CPU invocation used `lavaunst.3D.NS1.AVX512` or its `.FLOAT` variant.
Select only an instruction set supported by the host. A single-precision smoke test does not establish double-precision resource needs.
The GPU implicit attempts failed during linear-algebra initialization on different hosts.
Changing runtime libraries did not establish support for that missing solver path.

Preserve distribution symlinks and executable permissions when staging binaries.
Inspect the actual MPI and compiler-runtime dependencies. Do not combine library paths from unrelated toolchain versions without validation.
The former cloud scripts and host snapshots are deployment-specific and are not public prerequisites.

## Mesh routes

Cartesian cases used immersed-boundary geometry and adaptive Cartesian grids.
Curvilinear cases used structured near-body grids and off-body or overset tools.
Unstructured cases used polyhedral CGNS with a volume zone and separate surface zones.
LAVAVORO was supplied as an x86 mesher in the inspected v1.0.0 distribution.
An AFLR3-to-CGNS route still requires format and boundary validation before LAVA use.

Use the installed grid-information utility to obtain the boundary index-to-zone mapping.
Set `BC_n` entries from that mapping. Keep fan and nozzle faces separate from the airframe walls.
For a fresh tutorial, inspect partition/restart settings rather than assuming that saved partition files exist.

## Propulsion conventions from the source manual

| Physical role | Recorded formulation | Required checks |
|---|---|---|
| Engine fan face drawing flow from the domain | Outlet with a target Mach condition | Direction, reverse-flow treatment, mass balance |
| Exhaust entering the domain | Inlet with stagnation or mass-flow conditions | Thermodynamic anchor, energy, species, signs |
| Resolved nozzle profile | Nozzle data-file condition | File schema, profile coordinates, ramping |
| Imported distributed field | Distributed condition | Solver/build support and field mapping |
| Rotor surrogate | Actuator-region source terms where supported | Solver-family availability, thrust/torque conventions |

These are boundary-selection notes, not a validated propulsion installation or a ready-to-run aircraft input file.

## Preprocessing, tests, and outputs

Wall-distance computation was substantial in the source viscous cases.
Check the chosen turbulence and wall model before changing preprocessing. Removing turbulence changes the modeled physics.
Measure thread and rank scaling. More MPI ranks than supported GPUs failed the source GPU health check.

The recorded diamond-airfoil CPU smoke test completed a short iteration sequence.
The ONERA M6 GPU implicit attempts remained failed tests. Their mesh ingestion and wall-distance progress were not converged CFD results.
Inspect the rank-zero log, iteration histories, force output, restart data, and finite fields.
Do not label a run successful solely because it produced volume, surface, or monitor directories.

Use the versioned manual supplied with the solver for exact input syntax and support.
Source logs and binaries are not redistributed, and no fresh LAVA case was executed for this package.
