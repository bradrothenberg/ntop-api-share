---
name: unlinked-sim
description: Set up and run local Unlinked (also called unlink) simulations from MDL models and editable parameters. Use for mechanism dynamics, control models, reruns, result verification, and dashboards driven by recorded Unlinked traces.
---

# Unlinked simulations

Use Unlinked to compute the response. Deliver the model, editable parameters,
saved request and result, and a short statement of the verified behavior.
Add an animated dashboard or nTop connection when the task calls for one.

## Choose the workflow

- **Start or reopen an existing model:** read [local-setup.md](references/local-setup.md).
  Check health before starting services. Reuse the current publication.
- **Create or change a simulation:** read [models-and-api.md](references/models-and-api.md).
  Use [unlinked.py](scripts/unlinked.py) for local API operations.
- **Connect geometry, plots, or FEA:** read [dashboard-and-ntop.md](references/dashboard-and-ntop.md).
  Keep geometry, mass properties, simulation inputs, and result revisions distinct.

Locate the user's Unlinked checkout and read its current instructions.
The referenced local launchers and dashboards are optional external additions.
This package includes the API helper and decay pilot, not the service implementation.

## Define the model before building it

Use the user's existing answers. Ask only for information that changes the model:
operating modes, dimensions, masses/inertias, forces, constraints, initial state,
and whether motion is prescribed or responds to torque/force. If demonstration
values are authorized, make them editable and label their units and provenance.

Write a compact model contract in the project: coordinates and positive directions,
state variables, equations, units, outputs, numerical settings, and limits.
Do not infer dynamic mass or spring rate from appearance. Do not label inferred
aircraft geometry or demonstration FEA as validated manufacturing data.

## Build and run

1. Establish service health and inspect supported blocks in the installed source.
   Unlinked implements a subset of Simulink/MATLAB semantics.
2. Create a model directory with `.mdl`, `.m`, a signal/units manifest, and verification.
   Use a scalar graph with explicit state integrators when suitable. Model true
   feedback through states; do not mask algebraic loops with arbitrary delays.
3. Start with a short pilot using the same equations and solver as the full run.
   Save any useful existing backend results before a series of runs. The reference
   backend retains roughly the latest 20 runs per user, including across projects.
4. Pin the model version and the init-script version in every request. Save input
   bytes, hashes, requested overrides, the effective backend request, and raw trace.
5. Check terminal status, expected time coverage, finite values, aligned signal
   arrays, required signal IDs, and the model's physical invariants.
6. Run the full interval and a smaller-step comparison when numerical behavior
   warrants it. Validate an edited-input case before exposing editable controls.
7. Publish the new result only after checks pass. Keep the previous good result
   available if a rerun fails. Report failure instead of hiding or clipping it.

The helper only connects to HTTP loopback hosts. It does not create a hosted
service, alter auth settings, or retry mutation requests automatically. A timeout
can leave a run on the server: inspect its run list before submitting another.

## Reusable pilot

The included [decay.mdl](assets/decay.mdl) and [decay_params.m](assets/decay_params.m)
define `dx/dt = -rate*x`. They test upload, parameters, integration, and traces
against `x(t) = x0*exp(-rate*t)`. These are chosen test inputs, not hardware data.
See the reference for commands. Run Python with `uv run`.

The helper's structural trace check is not an engineering validation. Add
problem-specific balance, closure, endpoint, and convergence checks.

## Finish

Provide working model/dashboard links, local output paths, the run ID, and the
checks that passed. Distinguish retained older results from a fresh solve.
Do not promise that all parameter changes are valid: geometry, actuator limits,
singularities, and solver stability can change with inputs.
