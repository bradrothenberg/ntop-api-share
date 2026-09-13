---
name: ntop-notebook-api
description: Author, inspect, and verify native nTop notebooks with the build 42926 Python Console API, complete recipes, and owned-session dispatch. Preserve older snapshots and their recorded build scope.
---

# Notebook API

Start with [the current method reference](../../../docs/API_REFERENCE.md) and [authoring lessons](../../../docs/API.md).
The default documented build is nTop 6.1.0-rc build 42926. Read [migration guidance](../../../docs/API_42926.md) and [source conflicts](../../../docs/API_DOC_AUDIT_42926.md).
Older demos retain build 42594 provenance. Its archived reference describes historical behavior, not current restrictions.
Re-measure after a build change. Feature presence is not a semantic compatibility test.
Use the root harness/ntop_api.py and scripts/stage.py. No private checkout or personal skill installation is required.

## Authoring

- Use a task-owned notebook and a small calibration case first. Inspect the exact block identifier.
- Recipes carry SI units. Build 42926 setters accept explicit units; getters report display units. Record both value and unit.
- Real, vector, point, integer, bool, and text are supported live on build 42926. Keep unsupported values in recipes.
- Use explicit live units for lengths and angles. Unit rewriting preserves a dimensioned quantity but attaches units to a bare number.
- Set point/vector values with three components. The supplied getter's two-item wording and old three-type limit are documented source errors.
- Inspect block_state after evaluation. Dirty or queued blocks are incomplete; e_OK does not prove geometric correctness.
- Fill raw-block literals and connections before wrapping computed blocks. Wrap reused outputs before fan-out.
- Get/set wrapper traversal does not imply connect/clear traversal. Inspect repaired graph connections.
- Use clear_block_input to repair supported raw or nested targets. A reference is dropped; an owned nested block returns to the top level.
- A successful clear can retain an untouched default. Verify the input before reconnecting. The failed wrapped-mesh clear is a specific exception.
- Rename existing core.var<T> blocks instead of wrapping them a second time.
- Query exact identifiers with harness/block_catalog.py. Preserve overloads; do not guess enums or signatures.
- Chain properties through one variable per hop. A direct negative property inside a variable can read back incorrectly.
- A wrapped computation can be readable while a property connection is not a literal. Check graph wiring and evaluated downstream measurements.
- Prefer native list processing for repeated features when supported. Seed typed lists only when the target has no list to append to.
- Check reducing-overload conflicts such as add<list<real>>. Verify item count, dimensions, and geometry after list processing.
- For computed integer counts, inspect the source's round, floor, or ceiling property. Do not connect an unconverted real to an integer input.
- Import a whole dependency closure. References do not reliably resolve across separate recipe imports.
- Use the recorder in demos/i6/scripts/recipe_backend.py for large builds.
- Compare graph wiring and exact scalar expectations. A successful call alone is not evidence of a complete graph.
- Use move_block(block_id, targetBlockId, placeBefore=False) for live ordering and moves into the target's section. Both IDs must be top-level.
- Check current_open_custom_block before export. Recipe export targets the open custom block when one is being edited.
- Recipe import merges blocks and appends inputs, and takes the recipe name/description. Preserve complete input/output contracts during replay.
- Dedicated live input/output promotion remains absent. Do not infer that recipe-based Automate authoring is impossible or newly verified.

For reusable part inputs and imported custom definitions, use the [assembly modeling skill](../ntop-assembly-modeling/SKILL.md). Its generic pilot records build 42594 CLI conversion and readback. It does not certify the live import route or build 42926.

## Geometry and performance

Read docs/LOFTING.md for guide-driven conics, signed coordinates, cavity cuts, and local root blends.
Read docs/PROPELLER_LEARNINGS.md for two-rail profile mapping, closed loops, half twists, natural tips, and flat clamp faces.
Read docs/ASSEMBLIES.md for kinematics, nominal hardware, blade angles, and service routes.
Use analytic spring fields and small verification closures. Rotated-body boxes are conservative bounds.
Check actual mesh extents after export. A mesh block's box can disagree with the exported triangles.
The B52 and DDGX lessons distinguish continuity from surface fairness and independent references from fitted inputs.

## Background dispatch

For build 42926, use scripts/ntop_tcp.py with verified listener ownership and a fresh run directory.
Read [background dispatch](../../../docs/BACKGROUND_CONSOLE.md). TCP is documented from process startup and needs no console window.
It reaches the GUI interpreter; it is not a native headless API. The public helper has offline transport tests, not a new native TCP certification.
For an older build without TCP, use scripts/ntop_console_post.ps1 with a verified ProcessId and unique ScriptPath.
Preserve keyboard focus and use the returned completion marker.
Never automatically retry a timeout. Check its local completion file and inspect an unknown outcome first.
Do not use an existing user session to audit this public repo. Use an explicitly owned scratch notebook for native probes.

## Finish the notebook

Collapse all authored blocks and custom sections after the final save unless an expanded inspection is requested.
Run scripts/collapse_saved_notebook.py on the host with uv. Retain the API-saved working source and use a separate output.
The helper changes open[].collapsed and sections.decorations[].collapse. It retains the root group and other chunks.
Reopen the deliverable to inspect presentation when the GUI is available. Never patch a file while nTop is saving it.

Read docs/VERIFICATION.md for the limits of scalar checks, native renders, recipe audits, and report evidence.
