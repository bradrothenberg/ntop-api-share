---
name: aflr3-mesh-generator
description: "Generate and validate a boundary-layer volume mesh from body and farfield surfaces with an installed AFLR3 driver, for FUN3D or a downstream CFD conversion."
---

# AFLR3 mesh generation

Require the body surface, farfield surface, output base, units, boundary tags, and intended solver.
Locate an authorized AFLR3 installation and the matching `aflr3_cfd_mesh.py` driver.
The driver and mesher binaries are external prerequisites; this repository does not redistribute them.
Read the installed driver's help before selecting version-specific flags.

The source driver uses positional surface arguments:

```text
uv run python /path/to/aflr3_cfd_mesh.py body.obj farfield.obj -o .local/case/case
```

The output base has no file extension. Do not substitute unsupported `--body` or `--farfield` flags.
The recorded driver writes `.b8.ugrid`, `.mapbc`, and an optional generated FUN3D namelist.

## Mesh design and checks

Confirm surface closure, orientation, intersections, units, and body-to-farfield clearance before volume meshing.
Derive near-wall spacing from the intended flow and wall treatment. Record the y-plus estimate and its assumptions.
Choose growth, layer count, and total thickness together. Do not use historical default values as universal settings.
The source driver exposed `--initial-spacing`, `--growth-rate`, `--bl-thickness`, and `--num-layers`.
Options such as `--angqbf 180 --angqbfmin 0` relaxed angle checks in recorded cases.
Use them only after reviewing the resulting mesh quality; they do not establish validity.

Inspect cell volumes, element quality, boundary layers, boundary tags, and mesh extents.
Verify `.mapbc` against the exported surface groups and intended conditions.
Record counts, checks, warnings, executable versions, source hashes, and output locations.
Check mesh endianness and integer width before solver ingestion.

Use [FUN3D](../fun3d-cfd-runner/SKILL.md) for the solver case or [Nektar++](../ntop-nektar-cfd/SKILL.md) for high-order conversion.
Nektar++ curving has a separate macro-layer strategy; do not reuse a RANS prism stack without checking curving validity.
