# Compressible-flow cases

Read the installed solver manual and custom integration revision with these recorded source lessons.
The [conditions template](../assets/conditions_ns.xml) uses implicit laminar Navier-Stokes and DIRK order two.
Its atmosphere, gas, step count, and convergence settings are example assumptions.
Replace each double-underscore marker and review every remaining value before running.

Each volume composite needs the correct expansion, order, and conserved variables: rho, rhou, rhov, rhow, and E.
Map wall and farfield composites from the actual mesh.
The source used `WallViscous` for no-slip and `RiemannInvariant` for farfield on all five variables.
For Euler, the source used `Wall` and a different equation system.
Do not change to Euler merely to bypass a viscous setup problem.

Specify viscosity from the declared Reynolds number and reference length.
The historical low-Reynolds-number laminar demonstration did not represent full-scale turbulent aircraft flow.
Its recorded time steps and memory usage apply only to that mesh, order, and operating point.
Benchmark a short case before increasing order. Measure total and per-rank memory.

## Run evidence

Keep each conditions variant separate. Save checkpoints, log step progress, and retain a case receipt.
Process existence alone does not establish progress. Check the log, checkpoint timestamps, and finite fields together.
Keep failures and the last valid checkpoint.

For a failure, locate minimum pressure and density with their coordinates.
Compare step size at fixed geometry and physics. A similar failure time can suggest a spatial problem, but it does not prove the mechanism.
Inspect sharp edges, mesh validity at solver points, boundary mapping, fluxes, and model applicability.
The source blunt-base Euler cases were unstable; viscous cases altered that behavior.
Do not generalize the observation to every Euler discretization or geometry.

Check time-step and spatial-order sensitivity, forces, wall behavior, and physical model limits before interpreting the result.
