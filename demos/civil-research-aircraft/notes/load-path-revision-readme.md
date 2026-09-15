# Source workflow record

Built with Astra. These notes describe the original source workspace. Its scripts and native execution harness are not included. Use the [package guide](../README.md) for the published files.

# Revision F: longeron pad ties

This revision adds eight 12 mm pad-to-inner-flange ribs to each primary.
The forward primary stays at FS 4000 mm. The aft stays at FS 5400 mm.
Each part has 34 pockets per face, 60 mm overall depth, 6 mm floors,
12.7 mm pocket plan radii, and 6.35 mm rolling-ball floor blends.
The outside contour, central opening, hat passages and spar interface stay fixed.

The long spar mark remains unresolved. A crossmember through the central
opening and a stronger perimeter route are distinct choices. The separate
crossmember analysis is an unselected study and is not installed.

## Models and evidence

- `deliverables/Aircraft-structure.ntop`: 54 separate native member outputs.
- `deliverables/Forward-primary-bulkhead.ntop`: standalone forward primary.
- `deliverables/Aft-primary-bulkhead.ntop`: standalone aft primary.
- `exports/F06E-ties.step` and `F08E2-ties.step`: matching analytic B-reps.
- `manifest.json`: saved source identities, hashes, and input contracts.
- `evidence/delivery_audit.json`: native checks and delivery consistency.
- `analysis/tie_comparison.json`: before/after plane-stress screening.

The two STEP files were reconstructed with Open CASCADE from the same profiles
used by the native nTop models. They are not direct implicit-to-STEP exports.
Reimport checks require one valid solid and one watertight check tessellation.
Each tessellation is sampled at 60,000 points against the construction formula.
This is finite verification, not a global CAM tolerance certificate.

The two-dimensional stress and local floor-buckling gates fail. The geometry
does not establish manufacturing or flight release. Inputs and limits remain
proposed. The shared analysis assumptions are in `../wing_trade/assumptions.json`.

## Reproduce a revision

Run host Python through `uv run --no-sync python` from the repository root.
The scripts are in `CivilResearchAircraft/scripts/`.

1. Generate profiles with `bulkhead_load_paths.py`. Its `tied` function controls
   rib width. Shared station, contour and passage data come from Revision E.
2. Run `analyze_bulkhead_ties.py` for the matched before/after membrane screen.
3. Build each native part with `build_bulkhead_tie_parts.py --id <id> --run <new-id>
   --timeout 600`. Use a new run identifier and inspect completion receipts.
4. Prepare native field probes with `prepare_tie_native_checks.py`.
5. Use the owned Notebook API bridge to save/evaluate the nominal parts.
   Build 42926 can stall in `set_block_input`. Use explicit native custom calls
   through `check_bulkhead_ties_remaining.py` for changed input values.
6. Run `assemble_bulkhead_ties.py --run <new-id>` to replace the two embedded
   definitions. This checks input contracts and all 54 member expressions.
7. Dispatch `save_tie_assembly_gui.py`. Prepare organized views with
   `present_bulkhead_ties.py`, then render with `render_bulkhead_ties.py`.
   The first camera is a warmup. Inspect the retained native images.
8. Run `export_bulkhead_ties.py`, then `compare_bulkhead_ties_step.py`.
9. Dispatch `reopen_bulkhead_ties_gui.py`. Run `audit_bulkhead_ties.py`.
10. Run `publish_bulkhead_ties.py` only after the audit passes. It retains
    Revision E before replacing the main and two primary notebooks.
11. Build the main review with `build_load_path_report.py`. Build the separate
    wing trade with `build_wing_trade_report.py`. Check both reports and links.

The assembly embeds snapshots. Saving a separate primary does not update the
assembly automatically. Repeat the explicit refresh and verification steps.
Axial depth and residual-floor controls preserve their current input contracts.
The geometry checks cover 60/6 mm and 64/8 mm inputs, not structural adequacy.

The GUI setter recovery is recorded in `evidence/gui_setter_recovery.json`.
The verified owned process was stopped after the nominal result was saved.
The stalled changed-value call was not blindly resubmitted. Native CLI checks
completed the changed cases. Initial console setup used the repository's
working posted-menu-key method; normal commands use the background bridge.
