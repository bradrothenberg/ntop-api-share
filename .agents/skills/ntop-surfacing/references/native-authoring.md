# Native authoring

Use the installed `ntop-notebook-api` skill for the console, live editing, unit handling
and build states. It prefers live block edits for most work. This reference covers what
is specific to large lofted field graphs, as measured on prototype build 42926.

## One graph, two back ends

Both recorded cases keep a single field graph in Python and send it two ways:

- Host evaluation for previews, sections, zebra images and reference values. The cases
  used a GPU evaluator. The numpy evaluator in `scripts/surfacing.py` computes the same
  values and is enough for pilots and bodies of moderate size.
- A recipe of native blocks for nTop: coordinate fields, guide splines, Spline DF
  sections and plain field math.

This is what makes native verification cheap. Every native probe and every native mesh
vertex has a host value to compare with.

Rules for the native graph:

- Use plain math blocks, native splines and native primitives. Do not use expression
  blocks. One crashed the recorded build when added.
- Give sections, guides, shared fields and final bodies their own named variables. The
  notebook then reads like the model, and a node used twice is built once.
- Keep literals in SI and fields dimensionless, converting at block boundaries as
  described in the Spline DF reference.
- Expose a design control as a named real variable and read it back after import.
  Change it once through the API, compare the probes with a host rebuild, and restore it.

## Pilot before scale

1. `loft_pilot.py host`: evaluator against brute force, signs, guide fairness.
2. `loft_pilot.py recipe`: import one pilot recipe into a task-owned session with
   `notebook.import_recipe`, check build states, and read the `CHECK` variables against
   `pilot_expected.json`.
3. `loft_pilot.py native --ntopcl <path>`: convert headless, mesh, and compare vertices
   with the host field.

Add a pilot body for any construct the model uses that the pilot does not cover.

## Freeze before import

Decide the geometry on host previews: sections, zebra, overlay, and every camera that
will be shown. In the recorded cases any change after the import or the export repeated
hours of work, and stale exports of removed parts appeared in later renders.

## Import cost

`import_recipe` time grew roughly with the square of the notebook size on this build:

| Case | Notebook | Import time |
|---|---|---|
| Race car, eight sections, 156 parts | 1102 variables | 8132 s. Light sections took 13 s to 21 minutes, the bodywork section, imported last, 76 minutes |
| Race car, bodywork section first | same recipes | stopped after the second section took 645 s |
| Five-door body, wheels section | 155 variables, 36 parts | 333 s |

Consequences:

- Keep the graph small. Fewer primary surfaces and fewer control points pay twice.
  Aim below about 5000 graph nodes for a whole model.
- Import light sections first and the heavy body last.
- Split the recipe into self-contained sections. References do not resolve across imports.
- A client timeout does not cancel native work. Check for a completion record before
  retrying. Guard every dispatch with the process identity of the task-owned session,
  and never touch a user's own nTop session.
- A whole model can also be converted headless as one recipe. It took a similar time, about 100 minutes for the race car.

## Native mesh export

Export one part per recipe: the part's dependency closure, a mesh block, an optional
sharpen pass, and an STL export. Recorded behaviour:

- The mesh tolerance of the recorded mesh block acts like a cell size. Choose it per
  part: about 6 mm for a whole painted body, 1 to 3 mm for trim and seals.
- A body-dependent part took 7 to 35 minutes on about eight cores. The whole painted
  body took 55 minutes for 6.5 million triangles. Eight parallel workers filled a
  64-core machine.
- Point the temporary folder of the headless process at a drive with room.
- Mesh the right-hand part of a mirrored pair and reflect it for the left. This removed
  a third of the export work. Check the reflected mesh against the left field.
- Two export runs must not write the same file. Give each part one writer.
- After decimating a display mesh, project its vertices back onto the field. Decimation
  pulled vertices up to 1.3 mm off thin glass panes and left speckles.
- Remove receipts and meshes of parts that no longer exist.

Compare every exported mesh with the host field (`surface_distance`) and record the
largest distance, the triangle count, and whether the mesh touches its bounding box.
Recorded results: most parts within 0.1 mm, a whole body within 0.94 mm at a 6 mm
tolerance, and a worst part at 4.2 mm that was flagged against its own tolerance.

## Notebook presentation

Group variables into numbered sections, show only final bodies, colour by material, and
collapse authored blocks after the last save. Keep the file saved by the API unmodified
and write the presentation copy separately, with a check that the graph is unchanged.

## Evidence labels

Keep these apart in every report:

- Host checks: evaluator output, sections, zebra images, overlays.
- Native field probes read through the API.
- Native mesh vertices compared with the host field.
- Recorded results from an earlier run, with the build number.
- Not checked.
