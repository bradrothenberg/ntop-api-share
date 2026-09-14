# Flow-field renders (pyvista) and profile plots (matplotlib)

These notes retain recorded rendering recipes from the local report skill.
They are not new measurements or verification on the current host.

## Reading solver output

Nektar++/Fun3D-style VTUs usually carry conserved variables. Derive what
the report needs (ideal gas, gamma = 1.4):

```python
import numpy as np, pyvista as pv
m = pv.read("field.vtu")
rho = m["rho"]; ru, rv, rw = m["rhou"], m["rhov"], m["rhow"]; E = m["E"]
ke = 0.5 * (ru**2 + rv**2 + rw**2) / rho
p = 0.4 * (E - ke)                      # (gamma-1)*(E - ke)
m["p_kPa"] = p / 1000.0
m["Cp"]    = (p - P_INF) / Q_INF        # Q_INF = 0.5*rho_inf*U_inf^2
m["speed"] = np.sqrt(ru**2 + rv**2 + rw**2) / rho
```

Run with `uv run --with pyvista --with numpy python render.py`.
Volume VTUs can be hundreds of MB - fetch once, render everything in one
script, and delete the copies afterward if they landed in a synced
folder (keep originals at the source). Never leave multi-hundred-MB
files in OneDrive/Dropbox trees.

## Slice renders

```python
sl = m.slice(normal=[0, 1, 0], origin=[xc, 0, 0])   # symmetry plane
pl = pv.Plotter(off_screen=True, window_size=(1600, 1000))
pl.add_mesh(sl, scalars="p_kPa", clim=(99, 105), cmap="coolwarm",
            scalar_bar_args={"title": "p [kPa]", "vertical": True})
pl.view_xz()
pl.camera.focal_point = (x0, 0, 0)
pl.camera.position = (x0, -1.0, 0)      # normal to the slice
pl.camera.up = (0, 0, 1)
pl.camera.parallel_projection = True    # engineering figures: no perspective
pl.camera.parallel_scale = half_height_in_model_units
pl.screenshot(path)
```

- **clim is the whole figure.** The interesting structure usually spans
  a small fraction of the global range (a stagnation bump of +3 kPa on
  a 101 kPa field is invisible on a (50,140) scale). Print the field's
  min/max/percentiles first, then choose clim per view: wide for
  anomaly shots, tight for structure shots.
- Same probe discipline as meshes: render, Read the PNG, adjust.
- Good standard set for a body-in-flow report: full-domain slice
  (context), nose/leading-edge close-up (stagnation), the phenomenon
  close-up (separation, shock, corner jet - whatever the report is
  about), plus a wall render colored by Cp.

## Profile plots

Extract wall/line data and plot with matplotlib (Agg backend). For
surface quantities vs arc/axis position, bin the scattered points and
show mean + percentile band - the band width is itself evidence
(narrow = axisymmetric/converged):

```python
idx = np.digitize(x, bins)
mean = [cp[idx == i].mean() for i in range(1, len(bins))]
lo, hi = 5th and 95th percentiles per bin
ax.fill_between(bx, lo, hi, alpha=0.25, label="5th-95th percentile")
ax.plot(bx, mean, label="circumferential mean")
ax.axhline(theory_value, ls="--", label="isentropic stagnation Cp")
```

Always add the theoretical/reference line when one exists - a plot that
lands on theory is worth three paragraphs of claims.

## Gotchas

- **Criss-cross triangles when section-cutting a prism/BL mesh**: slicing an
  unstructured grid with prisms (boundary-layer meshes) makes each cut prism
  side-face a quad, but VTK's default cutter (and pyvista `show_edges`) splits
  those quads with a diagonal -- the structured BL layers render as ugly
  criss-crossed triangles. Fix: `mesh.slice(normal, origin,
  generate_triangles=False)` keeps the cut faces as quads. CRITICAL: do NOT
  `clip_box`/`clip` the slice afterward to trim it -- those filters
  re-triangulate and the diagonals come back. Trim by framing with the camera
  instead (`parallel_projection=True`, set `focal_point` + `parallel_scale`).
  For a clean boundary-layer section, a crossflow (streamwise-normal) slice
  shows the body cross-section wrapped in concentric quad prism layers; cut
  tets stay (correctly) triangular.
- **Jagged/notched body outlines in slices of high-order solutions**:
  FieldConvert linearizes each curved element at the solution's point
  count, so curved wall faces become chords; on a circumferentially
  curved body the per-cell chord sag varies and the slice boundary
  shows triangular "bites". Not missing elements - a tessellation
  artifact. Fix at export: `FieldConvert -n 5 session.xml conditions.xml
  field.chk out.vtu` (more output points per element; the tessellation
  then follows the curved geometry). Expect a much larger VTU.
- **Bash heredocs eat matplotlib mathtext**: `$_L` inside an unquoted
  heredoc is a shell variable and vanishes ("Re$_L$" renders as
  "Re$="). Quote the heredoc delimiter (`<<'EOF'`) or use plain text
  labels.

## Verification numbers for the text

While the mesh/field is loaded, extract the quantities the narrative
needs: min/max and their LOCATIONS (argmin coordinates prove "the
minimum is at the base rim"), values at named stations, integrated
quantities. Put locations in the text; reviewers check them.
