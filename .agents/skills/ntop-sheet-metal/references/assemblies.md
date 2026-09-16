# Reusable sheet-metal assemblies

Use the adjacent native assembly skill for custom-block interfaces and saved
identity verification. The recorded build 42926 pilot passed two input values
and live Notebook API import of the complete assembly recipe. Do not infer
that unlisted input/output marking API methods exist.

The example layout expects sibling `drafted/` and `assemblies/` folders in a
development directory. First build and natively verify the drafted parts.
The additional family builder reads the revised annular cover's design
metadata for its matching bolt pattern:

```
uv run --locked python .agents/skills/ntop-sheet-metal/scripts/build_assembly_families.py --out WORK/assemblies/families
```

Save those family recipes natively and export their complete extended recipes
to `assemblies/families/contracts/<family>.saved.json`. The assembly builder
reads those native identities and signatures, plus the drafted parts' saved
API readbacks from `drafted/evidence/<part>.api-readback.json`:

```
uv run --locked python .agents/skills/ntop-sheet-metal/scripts/build_sheet_assemblies.py --out WORK/assemblies
```

Those commands generate source recipes. They do not prove successful native
evaluation. The caller still imports complete recipes through the Notebook
API, evaluates native fit probes and verifies meshes and final saves.

## Example interfaces

- A vent chassis and folded lid share the drafted mounting ledge datum. A
  length input drives both sheets and the four fastener centers. The lid is a
  free-bent part with 90-degree bends, not a drawn shell needing the same draft.
- A routing panel's length is rail spacing +20 mm. One native hat-rail family
  feeds both placements, with crown holes matching the panel's revised floor.
- A drawn housing, adapter and annular cover use six spacers. A 6 mm nominal
  stand-off leaves 2.8 mm vertical clearance beneath the M4 cover nuts. Changing
  the gap drives spacer height, both upper sheets, their fasteners and the M3
  screw length. The gap remains open; no sealing claim follows.

Drive attachments from the supporting part's actual datums. Apply translations
once, in the authored coordinate frame. Reuse one evaluated family variable
for identical input combinations. Reimport edited source families because
assembly imports are embedded snapshots.

Hardware is modeled as nominal smooth screw, nut and tube envelopes. Evaluate
each size/length variant natively rather than scaling a reference mesh. State
that threads, engagement strength, clamp load and catalog fidelity are absent.

## Verification lessons

Check representative mating planes, hole boundaries, shanks at sheet levels
and clearance points at nominal and changed inputs. Preserve the complete
geometry dependency closure when removing unused validation probes. Local
checks are not an exhaustive interference or tolerance-stack qualification.

Some recorded CLI assembly conversions saved complete candidate notebooks,
then hung in shutdown after the native completion log. Preserve that abnormal
exit scope. A candidate artifact needs independent native reopen and numeric
validation. Do not call a timeout or a completion log a geometry pass. Bound
only a proven post-write cleanup state and only terminate the owned child.

The recorded 0.10 mm hardware meshes missed a 0.25% analytic-volume criterion;
0.025 mm still missed for one screw. Refining to 0.01 mm passed the tested
hardware variants. Keep this a measured choice for small parts, not a required
setting for every model.

For presentation, show individual native placed bodies with family colors;
hide helpers and the union output. Keep separate working and final files.
Compare the main geometry graph and all imported native chunks after arranging
the UI, collapse block/section states, and reopen the final files. Build 42926
uses a variable-length header; do not assume the first study's header length.

Reports may display full native family meshes transformed by the same placement
manifest. Verify every instance's input tuple against the exported mesh and
label these as host/browser views. An explode slider changes display offsets;
it is not an evaluated assembly motion or a replacement for native dimensions.
