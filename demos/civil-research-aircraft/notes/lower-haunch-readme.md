# Recorded source workflow

The execution scripts referenced below remain in the source workspace. Use the [demo guide](../README.md) for this snapshot.

# Revision H: integrated lower bulkhead sections

This revision connects each side-longeron passage pad to a broad, pocketed
lower side section. The side section continues to the bottom frame.
It retains the Revision G pin centers, bores, fork geometry and longeron routes.

The geometry remains a proposed design. Revision G's fork stress screen fails.
No new overall structure solve, lower-frame shell analysis, minimum-weight
claim, manufacturing release or STEP export is included.

## Files

- `deliverables/Aircraft-H.ntop`: organized native compound assembly.
- `deliverables/C-Fwd.ntop`: revised forward primary bulkhead.
- `deliverables/C-Aft.ntop`: revised aft primary bulkhead.
- `Aircraft-H-manifest.json`: updated definitions and source hashes.
- `analysis/geometry_mass.json`: calculated mass, contour widths and fork fit.
- `evidence/`: native geometry, source-envelope and graph checks.
- `views/`: native nTop implicit images.
- `references/`: the two user markups.

The illustrated report is `../Lower-bulkhead-review.html`.
The previous revision remains in `../lug_attachment/`.

## Construction and update propagation

Each primary has one native implicit output in aircraft world coordinates.
Its embedded Revision G definition is the preserved base. Native extrusions,
Boolean operations and pocket distance fields form the new lower sections.
The two sides have six new pockets per face in total for each primary.

The addition overlaps the old outer contour by 2 mm. This closes the union
without filling the existing pockets. Geometry comparisons check the side
sections below the existing lugs against the full lower-stock construction.
The addition-only build retains the existing lug stock and face reliefs.
The new fork relief uses a 0.01 mm polyline simplification. Its profile contains
the existing fork outline plus at least 0.98 mm of projected clearance. The two
face cutters share one native extrusion and a translation. Their axial faces
retain the 36 mm tongue and 0.25 mm nominal gap to each fork cheek.
The slower full-stock compile and
its stopped-process receipt remain in `revisions/monolithic_compile/` and
`execution/`.

The standalone model exposes editable internal pocket web and radius variables.
It has no promoted assembly inputs. The shared geometry file fixes the nominal
interfaces. Pin sizes and longeron positions must stay coordinated with their
mating models.

Imported custom definitions are snapshots. Saving an edited primary does not
update the main aircraft. Refresh the assembly from the verified part files,
then repeat native and assembly checks. Do not apply another placement to the
primary bodies, which already use aircraft world coordinates.

## Reproduce

Run from the Airplanes repository. Use new run names for native executions.
Use the configured build 42926 and the verified background Notebook API session.

```powershell
$env:CIVIL_AIRCRAFT_VARIANT='lower_haunch'
uv run --no-sync python CivilResearchAircraft/scripts/lower_haunch_geometry.py
uv run --no-sync python CivilResearchAircraft/scripts/lower_haunch_native.py --pilot --run fresh_pilot
uv run --no-sync python CivilResearchAircraft/scripts/lower_haunch_verify.py --pilot --run fresh_pilot
uv run --no-sync python CivilResearchAircraft/scripts/lower_haunch_native.py --ids C-Fwd C-Aft --run fresh_parts
uv run --no-sync python CivilResearchAircraft/scripts/lower_haunch_verify.py --ids C-Fwd C-Aft --source --mass --run fresh_checks
uv run --no-sync python CivilResearchAircraft/scripts/lower_haunch_native.py --assembly --run fresh_assembly
```

Use `lower_haunch_present.py` for measured display records and cameras.
Dispatch `lower_haunch_gui.py` through the owned Notebook API console to save
the two GUI working files. Use `lower_haunch_render.py` for native images.
Build `lower_haunch_report.py` only after the checked models and images exist.

The report separates proposed dimensions, calculated mass and measured native
geometry. Finite field samples do not establish global clearance or strength.
# Report handoff

`../Lower-bulkhead-review.html` contains six embedded native images. The overall
view uses the inspected nTop GUI capture. All 128 assembly variables report
`e_OK`. Browser inspection verified the revised face figure, image zoom and
assembled lower joint. Local report links and final package checks pass.

The optional standalone overall image export `hfinal01` was still running at
handoff. Check `execution/Aircraft-H_render_hfinal01.json` before any retry.
The report is complete with the native GUI image and does not depend on that
additional export. No new structural or manufacturing release is claimed.
