# Source workflow record

Built with Astra. These notes describe the original source workspace. Its scripts and native execution harness are not included. Use the [package guide](../README.md) for the published files.

# Initial rib buckling and longeron section study

Open `../Buckling-review.html`. The main aircraft and its STEP files remain
Revision D. The reduced analysis does not support uniform bulkhead thinning.

The new `.ntop` files in `models/` are editable straight section coupons. They
are not full curved ribs or fitted longerons. `Thin-sections-study.ntop` imports
the three generators as custom definitions and shows six section examples.
Imports are embedded snapshots. Rebuild the comparison after editing a source.

## Reproduce

Run from the Airplanes repository root. Use uv for all Python work.

```powershell
uv run --with-requirements CivilResearchAircraft/buckling/requirements.txt python CivilResearchAircraft/scripts/run_buckling_study.py
uv run --with-requirements CivilResearchAircraft/buckling/requirements.txt python CivilResearchAircraft/scripts/check_buckling_workflow.py
uv run --with-requirements CivilResearchAircraft/buckling/requirements.txt python CivilResearchAircraft/scripts/reanalyze_thin_ribs.py
uv run --with-requirements CivilResearchAircraft/buckling/requirements.txt python CivilResearchAircraft/scripts/plot_buckling_results.py
uv run --with-requirements CivilResearchAircraft/buckling/requirements.txt python CivilResearchAircraft/scripts/build_buckling_report.py
```

Edit `assumptions.json` before the first command. The scripts read the saved
Revision D profiles. Regenerate those source profiles when geometry changes.
The native build uses the pinned nTop installation in `config/runtime.json`.
`scripts/build_thin_section_models.py --run YOUR_UNIQUE_LABEL` rebuilds the
native coupons and checks. Unique labels retain native completion receipts.

## Method

- Linear plane-stress triangular elements recover in-plane loads.
- The primary model retains actual plan outlines, pockets and projected bores.
  It replaces three-dimensional blends with a step in axial thickness.
- Wing tributary loads sum to the assigned half-wing lift. The first tail case
  assigns equal load per rib and a total 15% maneuver-load fraction.
- Classical plate interaction, local outstanding-plate buckling, weak-axis
  Euler buckling and an assumed stress ceiling screen candidate sections.
- The default sweep uses force envelopes from the flat rib models. The two
  highlighted candidates then receive a new in-plane stiffness calculation.
- The section area comparison does not include a complete rib, fittings,
  manufacturing stock or production radii.

The 3.8 g case, 1.5 load multiplier, 0.65 buckling reduction and 250 MPa ceiling
are explicit study assumptions. They are not regulatory requirements or
certified forging allowables. Sensitivity cases use 2.5 and 6.0 g.

## Native controls

The I generator has section depth, wall thickness, flange width and coupon
length inputs. Its wall thickness also stays below 24% of depth and flange
width to prevent an invalid profile. The hat generator has the same controls
and fixed 10 mm feet. The flat generator has depth, thickness and length.

Every part uses local coordinates: X is the coupon length, Y and Z define its
section. The comparison translates the instances once with dimensioned vectors.
The standalone I default represents the 28 mm deep, 2 mm wall, 25 mm flange
wing example. The second instance uses 18 mm, 1.5 mm and 15 mm for the tail.

## Limits and retained evidence

All numerical results, matrices' source meshes, stress arrays, failed trial
results and native completion receipts are retained. The initial coarse rib
results and the first section integration implementation remain in `revisions/`.
An integration guard prevents a cut on a mesh edge from counting material twice.

This is a preliminary workflow. It excludes global aircraft buckling, nonlinear
imperfections, plasticity, skin load sharing, joints, fatigue and manufacturing
release. The broader checks must pass before a candidate replaces aircraft
structure. A hat longeron also needs revised frame passages and skin attachments.
