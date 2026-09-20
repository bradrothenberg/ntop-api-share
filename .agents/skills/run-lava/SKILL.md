---
name: run-lava
description: "Prepare and run NASA LAVA cases with solver-family and build compatibility checks, mesh and boundary contracts, propulsion conditions, run evidence, and postprocessing."
---

# NASA LAVA workflow

This skill adapts recorded LAVA v1.0.0 work. Require an authorized distribution and its matching manual.
The repository includes no LAVA binaries, manual, licensed meshes, or cloud lifecycle scripts.
Read [version-specific lessons](references/version-1-lessons.md) before using the historical workflow.

## Select the compatible route

Identify the solver family, mesh format, architecture, precision, MPI runtime, time integration, and turbulence model together.
The source families were Cartesian `lavacart`, curvilinear `lavacurv`, and unstructured `lavaunst`.
Their mesh preparation and boundary syntax differ. Confirm the requested family before editing a case.

For recorded v1.0.0 unstructured cases, implicit stepping required the CPU build.
The GPU unstructured build did not implement that implicit path.
Earlier runtime and CUDA hypotheses in the source notes were superseded by this compatibility finding.
Do not treat a GPU-equipped host as evidence that implicit RANS can run on its GPU.

## Case preparation

1. Record the distribution hash, manual version, installed executable, libraries, and host architecture.
2. Run a small compatible tutorial or established case before a new aircraft.
3. Check mesh units, cell quality, zone names, and the boundary index table.
4. Define flow conditions, reference area and length, moment center, axes, and turbulence assumptions.
5. Match each boundary entry to the actual surface zone. Retain separate propulsion faces.
6. Choose memory, rank count, threads, and time settings from a measured short case.

For propulsion boundaries, interpret direction relative to the fluid domain.
An engine suction face can be an outflow boundary; an exhaust plane can be an inflow boundary.
Use the matching manual to select Mach, mass-flow, total-pressure, and total-temperature conditions.
Check mass and energy balance. Do not assume an actuator-region option exists in every solver family or GPU path.

## Execute and report

Run in a unique owned case directory with persistent logs, input hashes, and checkpoints.
Track iteration progress and finite fields after initialization. Mesh ingestion is not solver completion.
Check residuals, force histories, mass balance, and output integrity together.
Retain failed cases and distinguish preprocessing success from completed iterations and converged solutions.
Extract compact surface/volume figures and report mesh, time-step, and physical-model limits.
Use [engineering-report](../engineering-report/SKILL.md) for figures and evidence.
For cloud execution, use the access and resource-ownership principles in [fun3d-gcp](../fun3d-gcp/SKILL.md), with LAVA-specific commands.
