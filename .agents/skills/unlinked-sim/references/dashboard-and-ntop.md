# Geometry and result presentation

## Dashboard connection

Use one saved result as the source for the scene, chart cursor, readouts, CSV,
and timeline. Interpolate recorded samples for playback. Do not solve a second
set of dynamics in the browser. Compute verification metrics from original samples.

Keep pending edits separate from inputs of the completed run. On success, replace
geometry parameters, plots, metrics, and effective inputs together. On failure,
retain the previous good result and identify it as such. Preserve saved result
JSON locally because backend run retention can expire the database copy.

The reference dashboard is a buildless Node/Three.js app under `dashboard/`.
Its server proxies approved backend routes and preserves authentication and origin
checks. Reuse that pattern without copying hard-coded project IDs into new apps.
Read the current `gear/config` and publication manifest for the active geometry.

Test playback, scrub, plot selection, view reset, input rerun, failure behavior,
and CSV units. Ensure camera orbit persists during animation. Place Main view
inside the 3D scene when following this project's layout.

For nTop styling, use the installed nTop design skill when available. The current
demo uses the heading `nTop Mechanism Demo`, the running model name, blue main
accents, and distinct chart-line colors. Avoid eyebrow labels and slogans. Load
licensed Aeonik fonts before video capture; do not distribute local font files.

## Native nTop integration

Use the available `ntop-notebook-api` skill when native authoring is requested.
This simulation skill does not require nTop for ordinary control models.
Keep native notebooks organized in named sections and reusable custom blocks.
Collapse authored blocks and sections after the final save.

Define a shared interface manifest:

- Geometry and motion revision identifiers, source paths and SHA-256 hashes.
- Parameter names, units, values, and whether measured, derived, or assumed.
- Part names, geometry files, local coordinate frames, and rigid group membership.
- Joint axes, pivots, and the mapping from simulated coordinates to part transforms.
- Mass, COM, and inertia sources; distinguish display mesh from analysis geometry.
- Signal IDs, names, units, and sign conventions.

Check transformed joint coincidence, branch continuity, service endpoints, and
clearance over travel. For flexible hoses, preserve routing supports, bend limits,
and length constraints rather than stretching every object with the strut.
Sampled checks do not establish continuous collision clearance.

When geometry changes, either recalculate dependent mass/inertia and rerun, or
explicitly label the retained dynamics basis. The reference R08 display retained
an R06 motion/mass basis. Never report fresh dynamics or FEA merely because the
visible geometry changed. Do not rerun an old publish script blindly; it can
replace a newer publication with an older revision.

## Load export for FEA

Export simultaneous force/moment states with time, frame, application point,
units, body identifier, source run, and assumptions. Do not combine unrelated
component peaks into a single supposedly simultaneous assembly load case.
Include inertia, gravity, joint reaction and actuator/spring contributions as
appropriate to the selected analysis. Avoid double-counting an equivalent load.

Separate component solves displayed in assembly context are not a coupled full
assembly solve. Preserve this distinction in files and reports. Use current
geometry for a new FEA solve; do not map old stress fields onto changed surfaces
and describe them as new results. Stress display clipping must leave raw values intact.

## Video, only when requested

Render from the same recorded simulation time at fixed frame intervals. Verify a
short encoded pilot, then the final duration, frame count, decode, fonts, and
motion/plot synchronization. Keep actual UI capture distinct from geometry renders.
This user does not want Computer Use skills/tools for video captures. Do not
fabricate nTop UI or alter geometry with generative enhancement.

Raw output frames can be removed after explicit cleanup requests and verified
video delivery. Preserve models, input textures, animated display source images,
motion data, final videos, and enough provenance to rerender. Do not mistake an
animated display image sequence for expendable rendered output.
