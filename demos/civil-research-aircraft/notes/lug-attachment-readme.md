# Source workflow record

Built with Astra. These notes describe the original source workspace. Its scripts and native execution harness are not included. Use the [package guide](../README.md) for the published files.

# Revision G: local spar attachments

This revision uses upper and lower bulkhead eyes, forked spar roots, and eight
nominal pins. It preserves the edge-aligned outboard spar directions. It retains
the separate cover connection path and 952 nominal cover fasteners.

The model is a geometry and analysis study. Local fork stresses exceed the
study ceiling. Overall structural adequacy, minimum weight, fatigue, joint
contact, and manufacturing release remain unresolved. No new STEP is released.

## Files

- `deliverables/Aircraft-G.ntop`: organized native assembly.
- `deliverables/C-Fwd.ntop` and `C-Aft.ntop`: separate primary bulkheads.
- `deliverables/P-Front-spar.ntop`, `S-Front-spar.ntop`, `P-Rear-spar.ntop`, and
  `S-Rear-spar.ntop`: separate forked spars.
- Eight `*-splice.ntop` deliverables: cover splices with the old cap strips removed.
- `parts/Root-pin.ntop`: nominal hardware family with a diameter input.
- `Aircraft-G-manifest.json`: the source definitions used by the assembly.
- `analysis/`: scoped loads, nominal joint screens, fork FEA and calculated mass.
- `evidence/`: native geometry probes, source checks, graph checks and GUI states.
- `execution/`: retained completion, failure and timeout receipts.
- `revisions/`: superseded trials and their evidence.

The self-contained illustrated review is `../Lug-attachment-review.html`.
Its native images are also retained in `views/`.

## Edit and regenerate

The part geometry uses the aircraft world frame, in millimeters in the shared
design data and SI units in the recipes. Do not apply another placement to a
part that already uses world coordinates.

The new parts have fixed nominal interfaces. Internal native variables remain
editable. Change a joint through the shared geometry and pin table, then rebuild
both mating parts and the hardware. An isolated pin-diameter edit does not resize
the bulkhead or spar bores.

Use host Python through `uv`. Set the variant for shared Candidate C helpers.
Run each command from the Airplanes repository. Use a new run label each time.
Never resubmit a command while its outcome is unknown.

```powershell
$env:CIVIL_AIRCRAFT_VARIANT='lug_attachment'
uv run --no-sync python CivilResearchAircraft/scripts/lug_revision_geometry.py
uv run --no-sync python CivilResearchAircraft/scripts/lug_revision_analysis.py
uv run --no-sync python CivilResearchAircraft/scripts/lug_revision_tangent_forks.py --install
uv run --no-sync python CivilResearchAircraft/scripts/lug_revision_analysis.py
uv run --no-sync python CivilResearchAircraft/scripts/lug_revision_fork_fea.py
```

The base generator restores the earlier fork outlines. Always install the
tangent outlines afterward. Recompute the mass and FEA after that installation.
Do not regenerate files that a live GUI command is reading.

Build the changed native parts with `lug_revision_native.py`. The `--ids`
argument selects definitions from `geometry/definitions.json`. The `--pin`
argument builds the pin family. Primary builds can take many minutes.

The delivered forward forging used the native GUI-template import route.
Its complete final expression matches the expected recipe. A duplicate display
name initially selected the pocketed blank. The repair gave the blank a unique
name and connected the finished forging. The generator now uses distinct names.

Run the qualified nested-definition pilot before the assembly build. Assembly
refresh uses the saved new parts and the eight saved old splice definitions
that remain nested inside the new wrappers. This avoids rebuilding those
nested definitions during signature compilation. Full graph comparison checks
every definition, default input and output expression after the refresh.

Imported custom blocks are embedded snapshots. Saving a separate part does not
update the assembly. Rebuild the assembly after a part change, then repeat native
probes, GUI inspection and rendering.

## Presentation and verification

`lug_revision_checks.py` prepares the probes. `lug_revision_native_checks.py`
evaluates the exact saved part definitions. `lug_revision_gui.py` provides the
independent GUI route. The final six parts pass 1,997 probes.

`lug_revision_source_check.py --run <unique-label>` checks the new structural
surfaces against the source implicit. `lug_revision_cover_trim_check.py` checks
the retained cover holes against the changed trimming boundary.

`lug_revision_presentation.py` applies measured GUI display records to saved
native files. It preserves all embedded native definitions and default buffers.
The pilot verifies native readback and an actual nTop render. For the large
assembly, every original geometry chunk remains byte-identical. GUI evaluation
and image inspection remain separate requirements.

`lug_revision_views.py` prepares the organized files and cameras.
`lug_revision_render.py` runs the qualified native renderer. It checks newly
written images, so an older camera image cannot count as a completed new view.

The pocket-tool custom-block experiment timed out during primary compilation.
It is retained as an authoring experiment and is not used by the delivered
primaries. No controlled assembly rendering benchmark has established a benefit
from larger unions or custom blocks.
