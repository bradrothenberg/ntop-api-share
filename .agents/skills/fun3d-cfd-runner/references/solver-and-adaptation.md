# Recorded FUN3D and refine workflow

These notes adapt the 2026 source campaigns. Inspect the matching solver and refine versions before reuse.
They do not establish that a defect persists in another build.

## Endianness and outputs

The recorded converter used three inputs: project base, integer-width selector, and source-endian selector.
Inspect the tool prompts. Do not infer endianness from the operating system alone.
The recorded `.lb8.ugrid` route used `data_format = 'stream'` with `grid_format = 'aflr3'`.

Volume output required both the variable selection and a write trigger:

```fortran
&volume_output_variables
  export_to = 'vtk'
  primitive_variables = .true.
  mach = .true.
  cp = .true.
  drho_mag = .true.
/
&global
  volume_animation_freq = -1
/
```

The observed `-1` wrote at the final step. Verify this convention in the selected build.
Use the history and force summary files for moments and pressure/viscous contributions.
Static-margin calculations require consistent moment center, axis direction, coefficient definitions, and derivative conventions.
Do not copy a neutral-point formula without checking those signs.

## External adaptation

The source integrated `--adapt` path failed during a post-adaptation restart write.
The recorded workaround used an external `refmpi` loop followed by a cold solve.

1. Preserve a converged baseline and its restart.
2. Export the solution to a primitive-variable SOLB with a write trigger.
3. Confirm the field layout and node count expected by the installed refine build.
4. Convert the volume mesh to MESHB and run the external loop.
5. Verify adapted mesh quality and boundary tags. Copy `.mapbc` only after checking tag preservation.
6. Solve the adapted case and compare convergence, forces, and local fields under identical conditions.

The recorded SA route exported six fields and explicitly excluded coordinates:

```fortran
&volume_output_variables
  export_to = 'solb'
  primitive_variables = .true.
  turb1 = .true.
  x = .false.
  y = .false.
  z = .false.
/
&global
  volume_animation_freq = -1
/
```

The default coordinate fields had caused a nine-field file to be misinterpreted.
Check actual field metadata; file size is only a secondary diagnostic.

```text
mpirun -np N refmpi translate case.lb8.ugrid case.meshb
mpirun -np N refmpi loop case adapted COMPLEXITY
```

Replace `N` and `COMPLEXITY` with measured, case-specific choices.
The loop expects the case mesh and corresponding solution file. Inspect its help for naming conventions.
The recorded workflow froze mixed/prism regions, which imposed a lower bound on useful complexity.
Read that bound from the mesh and log. An oversized frozen layer can prevent refinement near a shock foot.

Mach was the default interpolant. A separate scalar SOLB could supply a density-gradient-based metric.
Keep that scalar file separate from the primitive solution used for restart interpolation.
Choose the metric to resolve the quantity of interest, including wakes or expansions when relevant.
Compare rank count and concurrent-case throughput from measurements; more ranks did not ensure faster adaptation in the source cases.

## Field figures

The recorded `drho_mag` field supports numerical schlieren views.
A square-root transform can reveal weaker gradients, but label the transform and keep its scale fixed across comparisons.
Use each case's own geometry overlay, the same slice plane, camera, units, and color limits.
Field plots supplement convergence and force evidence; they do not replace them.
