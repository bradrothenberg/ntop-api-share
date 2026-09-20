---
name: fun3d-cfd-runner
description: "Prepare and run FUN3D CFD cases from volume meshes, with explicit force references, supported turbulence and GPU settings, convergence checks, and external refine adaptation."
---

# FUN3D CFD runner

Use this skill for case physics and solver execution. Use [fun3d-gcp](../fun3d-gcp/SKILL.md) for cloud deployment and recovery.
Require a licensed solver, its matching manual, and a validated volume mesh with boundary mapping.
No FUN3D executable, license, GPU service, or production namelist is bundled.

## Define the case

Record mesh units, Mach number, angle of attack and sideslip, temperature, Reynolds-number convention, and wall treatment.
Record reference area, chord, span, moment center, axes, and force signs before interpreting coefficients.
Check that the solver's Reynolds input matches the grid-unit convention. A length-based Reynolds number is not automatically the required input.
Choose RANS, DES, or DDES from the intended physics and available resolution. Use the installed build's support table.

In the source build, `turbulence_model` belonged to `&turbulent_diffusion_models`, not `&turbulence`.
FLUDA execution required `&gpu_support use_fluda = .true.` and a supported model and limiter.
The source recorded `sa`, `sa-neg`, and DES with DDES on GPU; other combinations required CPU.
Treat this as a build-specific record. Verify actual GPU activity rather than assuming that a GPU host implies GPU execution.

## Run and assess

1. Inspect mesh endianness, integer width, `.mapbc`, and project root name. Set the matching `&raw_grid` options.
2. Write a case-specific namelist. Keep the source mesh and baseline conditions immutable.
3. Run a short case in an isolated directory. Check ingestion, boundary conditions, finite fields, and force signs.
4. Measure memory and throughput before selecting MPI ranks or scaling the mesh.
5. Launch a managed or detached job with persistent logs and a run receipt. Identify its owned process tree.
6. Check residual histories and force/moment histories together. For unsteady cases, also check time-step convergence and averaging windows.

The source cases showed force sensitivity to limiter freezing. This is not proof that machine-zero residuals are universally required or sufficient.
Separate iterative convergence, mesh/time resolution, model-form accuracy, and comparison with experimental data.
Do not infer force accuracy from a stable image or a completed step count.

## Output and adaptation

Read [solver notes and refine](references/solver-and-adaptation.md) when configuring volume exports or an adaptation loop.
Keep forces, moments, residuals, mesh quality, boundary mapping, and run settings for every mesh revision.
Do not assume adaptation must improve drag in one direction.
For a sweep, use one directory per condition and consistent force references.
Use [engineering-report](../engineering-report/SKILL.md) to present field plots and convergence evidence.
