---
name: ntop-adjoint-optimization
description: Set up, verify, run, or resume adjoint shape optimization coupled to native nTop implicit geometry. Use for geometry-to-solver sensitivities, gradient checks, constrained optimization, and validated native optimization demos. Includes the verified Mach 3/5/7 SU2 inlet recipe; ordinary nTop modeling alone does not need this skill.
---

# nTop adjoint optimization

Connect native nTop design parameters to solver coordinates and adjoint sensitivities. Deliver an accepted design with reproducible evidence, or report the specific failed check.

## Establish the study

Read the project's handoff, specification, current results, and run records before changing anything. Distinguish accepted results from failed attempts and obsolete summaries.

Record the actual geometry, physics, boundary conditions, units, objectives, constraint definitions, parameter scales, bounds, mesh, and acceptance criteria. Resolve material uncertainty from existing evidence before asking the user. Preserve established targets and prior runs.

The completed inlet examples used native nTop geometry with closed, axisymmetric SU2 Euler CFD. Their open shells and Mach-angle cutouts were display geometry. A physical cutout requires its own flow domain and validation. Do not transfer axisymmetric performance claims to an open 3D inlet.

Read [the inlet recipe](references/inlet-recipe.md) only when reproducing or adapting that study. Its four modes, SLSQP settings, and numerical tolerances are case settings, not defaults for every problem.

## Build and verify the native connection

Read [native coupling](references/native-coupling.md) before implementing geometry or sensitivities.

- Use the installed `ntop-notebook-api` skill for desktop Notebook API authoring. If unavailable, inspect the installed API and establish a small native probe first. Do not substitute a Python geometry replay and call it native coupling.
- Prefer the tested PID-scoped Ctrl+backtick helper to open the Python Console. Leave an open console open. Verify an API probe, then use the background command bridge.
- Specify units and read dimensions back. Validate native build states, exported sample positions, values, derivatives, and source hashes.
- Prove the mesh uses the native fields. Check native perturbations against the geometry derivative at nonzero coefficients as well as the baseline.
- Cache a verified affine geometry operator when appropriate. Revalidate after changing the notebook, basis, units, sampling, or bounds. A nonlinear parameterization needs a current derivative.
- Contract the solver sensitivity with the derivative of the complete mesh motion. Check point IDs and coordinates before contraction.

Native coupling does not imply automatic differentiation of arbitrary nTop notebooks. State how each derivative is obtained and verified.

## Verify before optimization

Read [verification and recovery](references/verification-and-recovery.md) when preparing gates, diagnosing failures, or resuming a study.

1. Run a small complete pipeline: native geometry, mesh, primal, and required adjoints. Measure runtime. For this project's workflow, establish a sub-minute pilot before increasing resolution.
2. Verify the primal from raw convergence histories, field validity, conservation, boundary behavior, and independent functional calculations.
3. Check every design-variable component on the pilot. Check several directions on the production mesh at two finite-difference step sizes.
4. Use the exact optimizer coordinates, functional definitions, units, and normalization. Fix sign, scaling, ordering, or convergence errors before optimizing.

Stop dependent optimization when a required gate fails. Keep the failed evidence. Diagnose the cause without silently loosening tolerances or physical limits.

For saved inlet-format gates, use [the read-only audit helper](scripts/audit_directional_gate.py). It reconstructs comparisons from raw functional vectors and Jacobians. It does not certify solver convergence or native geometry provenance by itself. Its schema and command are in the verification reference.

## Optimize and validate the returned design

Use the optimizer already selected for a continuing study. SLSQP is the tested option for these small constrained inlet problems. Supply verified objective and constraint Jacobians, explicit bounds, and geometry constraints.

Preserve parameter scaling when changing allowed travel. At an active bound, inspect gradients and feasible directions. Expand bounds only within the user's authorized scope, then recheck geometry and CFD. A failed bounded search does not establish global infeasibility.

Save coefficients, functionals, constraints, solver evidence, and actual fields for every retained state. Separate trial evaluations, optimizer callbacks, and the returned point.

Before declaring scientific acceptance:

- Check the returned point against the original physical and geometry limits, independently of optimizer success.
- Verify its derivatives again, including constraint gradients.
- Solve from fresh initialization to check restart dependence. Compare fields as well as outlet numbers.
- Validate on an independently finer mesh and compare baseline and final designs on that same mesh.
- Record remaining mesh sensitivity. Two passing grids do not demonstrate grid independence.

Preserve failed attempts and use a new version when the study contract changes. Resume only unfinished stages after validating their dependencies. Track numerical acceptance, native export, rendering, and delivery separately.

## Deliver

Provide the native notebook, parameter and unit contract, solver configurations, accepted coefficients, gate reports, measured results, and source fingerprints. Keep the specification and status current. Use `uv` for Python work.

When videos or native views are requested, read [rendering and presentation](references/rendering.md). Use native captures and actual saved CFD fields. Keep chart references, simulation scope, and visual geometry consistent with the evidence.
