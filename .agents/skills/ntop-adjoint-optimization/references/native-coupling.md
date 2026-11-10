# Native geometry and the derivative connection

## Define the contract

Store parameter names, physical units, optimizer coordinates, scale factors, bounds, fixed boundaries, field sign convention, and topology. Store native notebook and export hashes with the solver mesh/configuration fingerprint.

The inlet parameterization is:

```text
a = S q                            physical coefficients from normalized variables
r(x, a) = r0(x) + sum_i a_i b_i(x) wall radius from native fields
phi(x, y, z, a) = sqrt(y*y + z*z) - r(x, a)
```

`S` is a declared diagonal scale matrix. The implicit field defines a zero surface; do not assume it is an exact signed distance field.

The native graph must evaluate the baseline, basis, and resulting wall. A native render of independently generated Python geometry is insufficient evidence of this connection.

## Native API execution

The measured desktop implementation used nTop 6.2.0-rc and its `notebook` Python Console object. Probe the installed build instead of assuming old block signatures still apply. `ntopcl` notebook execution and the desktop Notebook API are different interfaces.

The existing `ntop-notebook-api` skill contains `references/open-console-shortcut.md` and the PID-scoped helper. Ctrl+backtick opens the console on the tested build. Confirm the task-owned instance, leave an open console open, and verify a Notebook API probe. Send routine authoring through the background bridge. Do not queue commands over unfinished work; a visible prompt alone is insufficient completion evidence. Use unique command files and completion receipts.

Important failure cases from the native authoring work:

- Some setters and getters use display units. Explicitly set units and read dimensions back.
- Reused expressions may need named variables to preserve graph fan-out. Verify built output values, not only successful API calls.
- Table precision affected sampled fields. Validate actual exports. The final inlet recipes used coefficient high/low reconstruction, with CSV-backed maps for Mach 7.
- A successful build or a good-looking render does not prove the native wall matches the solver wall.
- Saved-file captures show the saved notebook. Save the intended coefficients before requesting a native render.

For scalar point maps, the measured import format is headerless CSV with four columns: `x,y,z,s`. Check row count, coordinates, point order, finite values, and dimensions before using it.

## Admit a native field operator

1. Export the baseline and each mode at the exact CFD axial stations. Preserve this immutable baseline snapshot before changing coefficients.
2. Check exported samples against the intended equations and endpoint conditions. Inspect native sections and scalar probes.
3. Perturb each coefficient in the live native notebook in both directions. Export new wall samples and verify that exports actually refreshed.
4. Compare live values with the proposed cached operator. Compare central differences with its analytic derivative.
5. Repeat at a representative nonzero design and after an expanded parameter range. Restore and verify the intended notebook state afterward.

For a proven affine family, native baseline and mode exports define an exact cached operator within numerical precision. Live nTop execution at every CFD evaluation is unnecessary. State that the optimization uses this verified native affine operator.

For a nonlinear field, recompute or differentiate the current geometry mapping. For a regular zero surface:

```text
grad_X(phi) dot dX/dq_i = -partial(phi)/partial(q_i)
```

This fixes normal motion only. A surface tracking rule and volume mesh motion are still required. Topology changes, vanishing field gradients, or nonsmooth Boolean seams require separate treatment and new derivative checks.

## Move the complete mesh and contract sensitivities

The inlet mesh keeps axial coordinates fixed and uses the baseline radial fraction `eta`:

```text
eta_j = y0_j / r0(x_j)
y_j(q) = eta_j * r(x_j, S q)
dy_j/dq_i = eta_j * b_i(x_j) * S_ii
```

This moves interior nodes as well as the wall. The verified derivative includes all those nodes. A general mesh motion method needs its own derivative.

For shape variables that enter the residual and objective only through coordinates:

```text
R(U, X(q)) = 0
R_U^T lambda = J_U^T
dJ/dq = (J_X - lambda^T R_X) X_q
```

Include additional explicit parameter terms if boundary conditions, material properties, or the functional depend directly on `q`. If the solver already exports the total coordinate sensitivity, contract it once with `X_q`.

Before contraction, verify global point IDs, ordering, coordinate values, component axes, units, objective sign, and any symmetry or reference-area factors. Do not substitute a wall-normal sensitivity for an all-node coordinate sensitivity without a justified mapping.

The inlet pressure objective was weighted by `1/p0_inf` on the adjoint tape. Its coordinate sensitivity already represented pressure recovery. Dividing by `p0_inf` again would be an error. No fitted correction factor should be used to force agreement with finite differences.
