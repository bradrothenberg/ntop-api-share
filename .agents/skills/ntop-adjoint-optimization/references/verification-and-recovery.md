# Verification and recovery

## Freeze the numerical meaning

Differentiate exactly the functionals supplied to the optimizer. Record mass/area weighting, axisymmetric quadrature, total versus static pressure, angle units, smoothing, and normalization. Independently reconstruct outlet integrals from fields.

For the inlet recipe, the functional vector was recovery, mean outlet Mach, and a smooth mean angle in degrees. The smooth angle was checked against raw and independently integrated angularity. A small signed mean velocity angle can hide opposing local angles. Mean constraints do not establish pointwise limits.

Verify positive density and pressure, finite fields, mesh quality, conservation, and boundary behavior. Evaluate all required residual components. A process exit code, optimizer success, or one low residual is insufficient evidence.

## Derivative gates

Use normalized optimizer variables consistently. For direction `d`, step `h`, and positive functional scale vector `s`:

```text
AD = (J_q d) / s
FD = [F(q + h d) - F(q - h d)] / (2 h s)
absolute_error = abs(AD - FD)
relative_error = absolute_error / max(abs(AD), abs(FD), epsilon)
component_pass = relative_error <= rtol OR absolute_error <= atol
```

Require every functional component to pass. Declare tolerances and scales before inspecting the result. Use more than one step size and direction; test every variable on the small pilot. Verify production adjoints against more tightly converged reference solves where needed.

At bounds, central perturbations may leave optimizer bounds. Use them only when geometry and solver inputs remain valid. Otherwise use an interior test or a documented one-sided derivative. Do not clip a central-difference perturbation and retain the old denominator.

If decreasing the step worsens agreement, compare actual convergence and functional noise. Tighten reference solves or choose a measurable step range. Preserve the failed gate. If derivatives remain unreliable, stop gradient optimization and report the cause.

Small steps can expose shock movement, limiter switches, mesh changes, or precision loss. Do not assume that a visually smooth shape makes the entire discrete solve differentiable. Validate the actual discretized problem used by the optimizer.

## Read-only saved-gate audit

`scripts/audit_directional_gate.py` uses only the Python standard library. It supports the saved inlet suite schema, not arbitrary solver output. It reads these files:

- Gate JSON: `q`, `resolution`, `center`, `reference`, and nonempty `comparisons`. Each comparison has `direction`, `step`, `plus`, and `minus` evaluation directories.
- Each evaluation: `values.json` with `candidate`, `q`, `angular_function_names`, `angular_function_vector`, and a `fingerprint` containing `resolution`, `coefficient_scale`, and `flow_spec`.
- Center and reference: `angular_gradient.json` with matching `q`, `fingerprint`, `objectives`, and `jacobian_wrt_q`.

Paths can be absolute or relative to the gate. The helper checks sample locations, dimensions, finite numbers, functional ordering, key study settings, and center/gradient identity. It recomputes both Jacobian comparisons against the saved reference finite differences. It ignores stored comparison numbers and stored pass flags.

Example for the preserved Mach 7 final gate, from this skill's folder:

```powershell
uv run python scripts/audit_directional_gate.py "<study>/final_gradient_n64.json" --normalization 1 4 1 --rtol 0.01 --atol 0.000001
```

The helper prints a JSON report and hashes each file it read. Exit code 0 means the recorded comparisons pass. Code 1 means a derivative mismatch. Code 2 means missing or malformed evidence. It does not rerun CFD, verify original source hashes, or establish adequate directional coverage. Those are separate gates.

## Diagnose rather than relax

| Symptom | Check and response |
| --- | --- |
| Native export does not change | Check build state, units, export refresh, exact notebook, and console receipt. |
| Native samples disagree with Python | Check station order, table precision, units, endpoint handling, and baseline snapshot. |
| All adjoints differ by a factor | Check objective weighting and normalization exactly once; inspect parameter scale and angle units. |
| One parameter has a wrong sign | Check basis ordering, coordinate axes, field sign, and global node mapping. |
| FD error grows at smaller steps | Measure solve noise and numerical precision; use a tighter reference before changing criteria. |
| SLSQP returns at a bound | Inspect feasible directions and geometry. More travel is a new bounds decision, not proof of infeasibility. |
| Mach or angle passes only on the coarse grid | The returned design is not accepted on the finer grid. Preserve it and continue within authorized scope. |
| Warm restart passes, fresh solve differs | Inspect residuals, field differences, boundary state, and possible solution branches. |
| Optimization completes but validation/render fails | Keep the returned design. Resume the failed stage after verifying dependencies. |

## Evidence and acceptance

Fingerprint geometry, native exports, basis, parameter scaling, mesh coordinates, solver executable/build, physics, configurations, objective normalization, and source code. Record initialization separately. Validate cached artifacts against the intended contract before reuse.

Some fields legitimately differ between production and reference solves, such as residual limits. Permit only reviewed differences. A fresh-start validation must not silently use a checkpoint. A mesh hash alone does not prove a cached flow state is compatible.

Preserve optimizer messages and status separately from scientific acceptance. Inspect the returned point even if it differs from the last callback. Verify constraints, geometry, final derivatives, fresh-start fields, and finer-grid results. Compare improvements against a baseline solved on that same mesh.

Record remaining limitations: inviscid versus viscous physics, assumed gas model, 2D versus 3D domain, mesh sensitivity, mean versus local limits, and any validation not completed. Do not treat nondimensional example conditions as a flight condition.
