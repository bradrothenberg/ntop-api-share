# Verified native inlet recipe

This is the local Mach 3/5/7 example, inspected on 12 October 2026. Use its settings only when reproducing that problem. New physics, topology, geometry families, or constraints need new admission checks.

## Study settings

| Setting | Recorded implementation |
| --- | --- |
| Native geometry | nTop implicit radial wall with a verified exported affine operator |
| CFD | SU2 discrete-adjoint-capable build; closed 2D axisymmetric inviscid Euler flow |
| Gas | Calorically perfect gas, gamma 1.4, declared nondimensional freestream |
| Freestream / outlet design reference | Mach 3 / 1.5; Mach 5 / 3; Mach 7 / 4 |
| Mach 7 parent | 25% wider than the narrow reference at fixed length |
| Objective | Minimize negative total-pressure recovery |
| Shape variables | Four radial modes, i = 2, 3, 4, 5, degree 7 |
| Mode formula | `b_i(t) = t^i (1-t)^(7-i) / [(i/7)^i (1-i/7)^(7-i)]` |
| Mode coordinate | Axial distance divided by compression length, clamped to [0,1] |
| Baseline | Native Hermite representation, verified against source wall samples |
| Optimizer | SciPy SLSQP with explicit objective and constraint Jacobians |
| Optimizer controls | `maxiter=60`, `ftol=1e-8` in the accepted controllers |
| Standard normalized bounds | Four variables in [-1,1] |
| Mach 7 expanded bounds | Four variables in [-2,2], original coefficient scale retained |
| Outlet Mach acceptance band | Design reference +/- 0.05 |
| Outlet angle limits | Native raw and smooth means <= 0.999 degrees; independent mean <= 1 degree, with recorded numerical tolerance |
| Geometry constraints | Continuous minimum radius and monotonic wall constraints, plus mesh validity |
| Mesh levels | N8 pilot, N64 optimization, N128 independent validation |
| Mesh structure | 9N axial intervals, N radial intervals; 9N^2 quadrilateral cells |
| Production residual limit | All four relevant log10 RMS components <= -12 |
| Derivative references | -13 normally; selected Mach 3 and Mach 5 gates required -14 |
| CFD finite-difference steps | 3.90625e-6 and 1.953125e-6 in normalized q |
| Functional scaling for gates | [1, outlet Mach design reference, 1] |
| Component derivative acceptance | Relative error <= 0.01 OR absolute error <= 1e-6 |

The original M3 workflow and later native studies share a method, but the native coupling has its own evidence. Do not substitute the original Python-only run or ONERA ADflow RANS results for native SU2 results.

The modes vanish with zero first derivative at the compression endpoints. Radius and slope constraints used piecewise Bernstein coefficient bounds over the continuous wall. Checking a few surface samples alone would miss possible extrema between them.

The three adjoints correspond to recovery, outlet Mach, and a smooth angularity functional. Pressure recovery weighting is applied on the tape exactly once. Inspect the runtime and objective contracts before reproducing the custom angle expression; do not assume an arbitrary installed SU2 build has that implementation.

## Lessons from the completed runs

- The small native wall perturbations used a physical step of `1e-4 * capture_radius`. Their derivative errors were checked against `1e-8`. These native geometry checks are separate from CFD finite differences.
- The initial Map from Lists representation needed precision checks and later coefficient reconstruction. Mach 7 used CSV-backed native tables. Preserve the admitted native field snapshot.
- Mach 3 and Mach 5 needed tighter reference convergence for selected derivative checks. Production limits and physical targets stayed unchanged.
- Mach 7 reached its original parameter bounds. The user authorized larger bounds. Native checks were repeated over the expanded range before accepting the new CFD result.
- Fresh-start solves and independently finer-grid checks were required after optimization. Accepted metrics were recomputed from actual saved fields.
- Earlier physical open-scoop attempts and wider-geometry feasibility failures remain separate evidence. Their results cannot be replaced by closed-axisymmetric results.

## Local source map

The study implementation is external to this package. The skill does not bundle the solver, large notebooks, or run data. Reproducing this recorded case requires those separate artifacts.

Under `work/ntop_inlet_suite_v1/`:

| Source | Purpose |
| --- | --- |
| `SPEC.md` | Study contract and native implementation decisions |
| `build_native.py` and later native recipe scripts | Native graph construction; early versions require the later precision fixes |
| `verify_native_fields.py` | Native sample checks and immutable baseline admission |
| `native/check_live_derivatives.py` | Actual Notebook API wall perturbation/export check |
| `native/live_expanded_mach7_v2.py` | Native derivative verification at expanded Mach 7 coefficients |
| `native_study.py` | Native baseline/mode exports drive CFD wall and mesh derivatives |
| `native_engine_v3.py` | Native evaluator, admission checks, and fingerprints |
| `native_engine_expanded_v2.py` | Mach 7 expanded range with preserved parameter scale |
| `run_suite_v6.py` | Accepted Mach 3 continuation; not a generic all-case launcher |
| `run_suite_v5.py` | Mach 5 controller and validation sequence |
| `run_mach7_expanded_v2.py` | Mach 7 feasibility restoration and pressure optimization |
| `native_validation_v3.py` | Physical acceptance and independent verification |

Supporting engine: `work/busemann_m7/axisymmetric_wide_v1/engine.py`. Inspect its pressure objective normalization, all-node contraction, runtime contracts, and evidence checks.

Accepted final audit records under the suite's `runs/`:

- `mach3_map_v2/coupled_v6/independent_final_audit.json`
- `mach5_map_v2/coupled_v5/independent_final_audit.json`
- `mach7_map_csv_v3/expanded_bounds_v2/independent_final_audit.json`

Final saved directional gates:

- `mach3_map_v2/coupled_v6/final_gradient_n64.json`
- `mach5_map_v2/returned_reference14_v1/final_gradient_n64.json`
- `mach7_map_csv_v3/expanded_bounds_v2/final_gradient_n64.json`

Read the referenced raw records and their dependencies. Older summary tables can retain failed statuses after a later accepted continuation. Do not select a result solely because a directory is named `latest` or `final`.
