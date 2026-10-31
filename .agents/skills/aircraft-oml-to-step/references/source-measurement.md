# Source inspection and measured fit

## Recover the construction, not only the final mesh

For an nTop source, locate the intended OML output and walk its dependencies.
Record profile definitions, dimensions, coordinate systems, remap fields, rail
curves, sweep changes, twist/camber rules, blends, clipping tools and passages.
Inspect imported custom block definitions. Names alone can hide a very different
operation. Keep upstream components available for component-specific queries.

Prefer the current native API for inspection and numerical measurements. A saved
notebook parser is an alternative only when its format is understood and tested
against the current build. Never treat a copied block ID or cached output as a
universal interface. Check that the requested output actually evaluates.

Use a manifest containing the source path and hash, runtime/build, selected output,
query units, dependency paths and hashes, and purpose of each measurement set.
Hash the original source again after the run. Relative file references can change
meaning when a notebook is copied; verify their resolution.

## Units and sampling

Some serialized nTop values use SI units even when the UI displays inches or mm.
Inspect unit metadata and confirm a known dimension numerically. Convert at the
input/output boundary exactly once. A factor-of-1000 or 25.4 error can still
produce a valid-looking closed CAD model.

Useful measurements include:

- Section profiles normal to the relevant component axis or local span direction.
- Rays with known start points, directions and component selection.
- Scalar-field samples for surface projection and intersection searches.
- Construction-field boundaries for body shoulders and wing transitions.

Check ray misses, multiple crossings, loop ordering, holes and branch identity.
A body section that intersects the inlet and outer skin can have several loops.
Do not join unrelated loops because they share a station.

Sample extra stations at sweep changes, tips, leading/trailing edges, junctions,
inlets and passages. Use fewer samples first to verify the complete pipeline.
Reserve additional stations or independent surface samples for validation.

Give each query a unique identifier. Retain exact inputs, units, output, execution
status and receipt. Reuse a cache only when the source, queried feature, settings
and input points match. A timeout or missing result is not a successful query.

## Source-fit measurement

Do not use the magnitude of an arbitrary implicit field as Euclidean distance.
For a field f, a local zero-set projection can use:

    p_next = p - f(p) * grad(f(p)) / dot(grad(f(p)), grad(f(p)))

Probe the gradient numerically if needed. Bound steps, detect a small gradient,
track the intended component and record the final field residual. At a sharp
edge or competing surface, Newton projection may reach the wrong branch.

For difficult points, search locally for sign changes in the native field.
Refine the search and project candidate crossings to the zero set. Report the
search scale and residual. Do not present this as an exact closest-point solver.
Do not label residuals as mm unless the queried field has length units.

Sample only the trimmed CAD face domain. Include approximately area-weighted
coverage and extra samples on small, important faces. Label the weighting policy;
extra samples change global percentiles. Group results by component or region so
a large smooth wing does not hide a poor inlet or fin root.

Report sample count, median, RMS, p95, p99, maximum, worst-point locations, residuals
and unresolved projections. Use all sampled points in the record; do not silently
drop failed projections. Separate intentional design changes from fit errors.

One-sided CAD-to-source samples can miss a source feature absent from the CAD.
Use source-to-CAD checks where required by the fidelity contract or where missing
features are plausible. Report the actual directions tested. Finite sampling is
not a global Hausdorff bound.

The `compare_points.py` helper summarizes already computed point pairs. Its input
is a CSV with these headers, in mm:

    cad_x,cad_y,cad_z,source_x,source_y,source_z,region,source_residual_mm

The last two columns are optional. Region names are free text. Supply residuals
only when the field's units justify the `_mm` label. If a residual column exists,
every row must contain a finite residual. Set `--max-source-residual-mm` only to
an actual chosen convergence threshold, not a desired surface-fit tolerance.
