# Source workflow record

Built with Astra. These notes describe the original source workspace. Its scripts and native execution harness are not included. Use the [package guide](../README.md) for the published files.

# Wing-root architecture trade

This is a preliminary comparison for the 7,500 lb civilian research aircraft.
The native Revision E assembly remains the geometric reference. The report is
`../Wing-root-trade.html`. Its images are embedded and work without the server.

## Reproduce

Run these commands from the Airplanes repository, using its existing uv environment.
The geometry command resets the study assumptions to their documented defaults.

```powershell
uv run --no-sync python CivilResearchAircraft/scripts/wing_trade_geometry.py
uv run --no-sync python CivilResearchAircraft/scripts/wing_trade_beam.py --pilot
uv run --no-sync python CivilResearchAircraft/scripts/wing_trade_beam.py --all
uv run --no-sync python CivilResearchAircraft/scripts/wing_trade_frames.py
uv run --no-sync python CivilResearchAircraft/scripts/wing_trade_compare.py --sensitivity
uv run --no-sync python CivilResearchAircraft/scripts/wing_trade_figures.py
uv run --no-sync python CivilResearchAircraft/scripts/build_wing_trade_report.py
```

The wing uses spatial beam section integration and classical local buckling.
The bulkheads use triangular plane-stress finite elements on measured profiles.
The bulkhead stress gate fails. The weight ledger is not an equal-strength
comparison of released parts. The report separates wing efficiency, incomplete
assembly weight, frame stress, and uncertainty from missing joints.

The stringer count stays constant within each rib bay. Stringers can start or
stop only at full-depth ribs. Mass and section stiffness use the same count.
The dense check records 252 sections for each main candidate. The initial
failed check is retained under `evidence/`.

Units are N, mm, MPa, kg. The study assumptions are editable in `assumptions.json`.
Input profiles, gauge choices, stresses, checks, and sensitivity cases are JSON.
The frame meshes and displacement/stress fields are compressed NumPy arrays.
Native geometry is not meshed again for this trade; the starting source meshes
are retained geometry evidence from the existing project.

George Irving's sketch is a user-supplied, unscaled layout reference. The
subsequent bulkhead markup identifies load-path changes for the next revision.
