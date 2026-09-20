# Field conversion and analysis

Use the same mesh, conditions, expansions, and field revision as the solve.

```text
FieldConvert -f mesh.xml conditions.xml field.chk volume.vtu
FieldConvert -f -m extract:bnd=0 mesh.xml conditions.xml field.chk wall.fld
```

Confirm output naming and boundary IDs in the installed build.
For curved geometry, increase visualization sampling only when needed for the figure.
The recorded route used `-n 5` for close-ups and `-r` for a spatial range slab.
Sampling density changes visual interpolation, not solver resolution.
Avoid interpreting chordal slice artifacts or clipped slab boundaries as physical geometry defects.

For a single perfect gas with total energy density E:

```python
kinetic_energy_density = 0.5 * (rhou**2 + rhov**2 + rhow**2) / rho
p = (gamma - 1) * (E - kinetic_energy_density)
cp = (p - p_inf) / (0.5 * rho_inf * speed_inf**2)
```

Read gamma and reference conditions from the case. Check positive density and consistent dimensional conventions before applying the formulas.
Report extrema with locations, wall-pressure profiles, boundary-layer samples, and reverse-flow regions where relevant.
State whether boundary conditions are imposed weakly and report residual wall slip rather than hiding it.
Use fixed camera, plane, units, and color limits for comparisons.
Keep large fields in ignored run storage. Retain compact figures and their scripts with the report.
See [scientific reporting](../../engineering-report/SKILL.md).
