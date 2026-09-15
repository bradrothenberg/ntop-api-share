# Source workflow record

Built with Astra. These notes describe the original source workspace. Its scripts and native execution harness are not included. Use the [package guide](../README.md) for the published files.

# Revision E: installed hat longerons

The main model contains eight native 50 x 32 mm hat longerons with 2 mm nominal
transverse walls. All twelve frame and bulkhead notebooks have revised passages.
The 54 separate member outputs and four promoted assembly controls are retained.

Open `../Design-review.html` for native images, checks, and model links.
Open `../Aircraft-structure.ntop` for the delivered assembly. Separate models are
in `../Bulkheads/` and `../Longerons/`. This folder retains their build inputs,
native readbacks, API-saved working files, view files, and verification evidence.

## Geometry and controls

- `geometry/routes.json`: eight paths, local width directions, and inward normals.
- `geometry/stations.json`: authoritative station-to-definition mapping. The final
  aft primary is F08E2. The adjacent frame is F09E2. Earlier F08E/F09E files are trials.
- `geometry/F*.json`: delivered perimeters, openings, pockets, and hat cutouts.
- `manifest.json`: saved part identities, source hashes, inputs, and update rules.
- `parts/`: native definitions. Each standalone longeron retains the shared
  Aircraft interior input. Its local Hat wall thickness variable defaults to 2 mm.
- `deliverables/`: organized copies with construction hidden and sections collapsed.

The hats use native Sweep along Two Rails with an axial station spine. The center
and orientation guides follow the aircraft section data. Equal axial guide spacing
prevents short end spans from folding the native interpolation.

The outer transverse profile stays fixed when the local wall control changes.
Its implemented range is 1.5 to 3 mm. Native checks exercised 2 and 3 mm.
The 2 mm value is not a certified minimum wall normal to the curved surface.

Each passage uses native hat contours measured on five planes through the maximum
frame thickness. A filled convex envelope includes the hat cavity. A proposed
3 mm rounded offset adds clearance. Local frame pads prevent isolated islands.
Three upper routes move an additional 6 mm inward at FS 5400 to protect the land.

## Reproduction sequence

Use nTop build 42926 from the repository runtime configuration. Use the owned
process identity and background console bridge documented in the repository.
Never dispatch another GUI command until the prior completion receipt is known.
Every native CLI or GUI run needs a new receipt suffix.

1. Build the raw and fitted hats with `../scripts/hat_longerons.py`.
2. Sample the actual native sections with `../scripts/sample_hat_sections.py`.
3. Rebuild affected station parts with `../scripts/build_hat_stations.py`.
   Keep `geometry/stations.json` as the final definition map. Do not publish trial IDs.
4. Refresh the twenty changed definitions with `../scripts/assemble_hat_revision.py`.
   This preserves the qualified assembly slots and compares all 54 expanded outputs.
5. Prepare field checks with `../scripts/prepare_hat_gui_checks.py`, then execute
   `../scripts/save_check_hat_gui.py` through the owned Notebook API console.
6. Run the wall and passage checks. Save the final longeron and assembly GUI files.
7. Regenerate STEP with `../scripts/export_hat_bulkheads.py F06E F08E2` and run
   `../scripts/compare_hat_step.py`.
8. Prepare organized views with `../scripts/present_hat_revision.py`, then render
   them with `../scripts/render_hat_revision.py` using unique receipt names.
   First apply `../scripts/prepare_final_hat_views.py` for Adaptive hat preview
   and a discarded initial camera frame. Fixed-resolution previews can show
   false ladder-like gaps in these long, thin members.
9. Publish with `../scripts/publish_hat_revision.py`, generate the report with
   `../scripts/build_hat_report.py`, and run `../scripts/audit_hat_delivery.py`.

Run host Python from the repository root with `uv run --no-sync python`.
The scripts retain failed trials and native completion receipts. Review receipts
before retrying an operation with an unknown outcome.

## Verification scope

The evidence includes native expressions, wall controls, 480 measured sections,
96 passage clearances, native station fields at nominal and changed dimensions,
retained wing and tail contact samples, CAD validity, and native implicit views.
All 70,752 longitudinal wall and cavity samples pass on the eight fitted hats.
These checks use 5 mm axial spacing. They are finite checks, not a global proof.
The delivered organized assembly reopens with every native build state OK.

Use close-ups to inspect the 2 mm transverse walls. At full-aircraft scale,
both fixed and Adaptive previews can leave these surfaces stippled. The saved
joint close-ups resolve the continuous native walls and matching frame openings.

The initial GUI parameter setter stalled during the forward changed-thickness
verification copy. Its completed results were retained. Only the owned process
was restarted. Bounded native CLI calls completed the remaining cases. The
recovery record and failed trials remain in `evidence/` and `execution/`.

The STEP models are independent Open CASCADE solids built from the same profiles.
They are not direct implicit-to-STEP exports. Tessellations are used only to check
those two CAD solids. Other aircraft members are rendered as native implicits.

Revision D remains in `../modular/` and `../Design-review-D.html`.
Its buckling results remain a historical baseline. They do not validate Revision E.
Skin attachments, clips, splices, bend radii, joint sizing, material temper,
manufacturing tolerances, and structural substantiation remain open.
