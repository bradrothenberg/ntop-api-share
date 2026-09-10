---
name: ntop-notebook-api
description: Author, inspect, and verify native nTop notebooks through the prototype Python Console API, using complete recipes and the bundled background command bridge.
---

# Notebook API

Read the repository's docs/API.md and docs/API_REFERENCE.md before changing a native graph.
The measured surface is nTop 6.0.0-rc build 42594. Re-measure after a build change.
Use the root harness/ntop_api.py and scripts/stage.py. No private checkout or personal skill installation is required.

## Authoring

- Use a task-owned notebook and a small calibration case first. Inspect the exact block identifier.
- Recipes carry SI units; live setters/readbacks use display units. Read values back.
- Set literals before wrapping blocks. Wrap reused outputs before fan-out.
- Chain properties through one variable per hop. A direct negative property inside a variable can read back incorrectly.
- Seed typed lists before appending. Finish inputs before another block consumes and nests the block.
- Import a whole dependency closure. References do not reliably resolve across separate recipe imports.
- Use the recorder in demos/i6/scripts/recipe_backend.py for large builds.
- Compare graph wiring and exact scalar expectations. A successful call alone is not evidence of a complete graph.

## Geometry and performance

Read docs/LOFTING.md for guide-driven conics, signed coordinates, cavity cuts, and local root blends.
Read docs/ASSEMBLIES.md for kinematics, nominal hardware, blade angles, and service routes.
Use analytic spring fields and small verification closures. Rotated-body boxes are conservative bounds.
Check actual mesh extents after export. A mesh block's box can disagree with the exported triangles.
The B52 and DDGX lessons distinguish continuity from surface fairness and independent references from fitted inputs.

## Background dispatch

Use scripts/ntop_console_post.ps1 with a verified ProcessId and unique ScriptPath.
Read docs/BACKGROUND_CONSOLE.md. Preserve keyboard focus. Poll the completion marker before resubmitting.
This posts commands to the GUI console; it is not a native headless API.

## Finish the notebook

Collapse all authored blocks and custom sections after the final save unless an expanded inspection is requested.
Run scripts/collapse_saved_notebook.py on the host with uv. Retain the API-saved working source and use a separate output.
The helper changes open[].collapsed and sections.decorations[].collapse. It retains the root group and other chunks.
Reopen the deliverable to inspect presentation when the GUI is available. Never patch a file while nTop is saving it.

Read docs/VERIFICATION.md for the limits of scalar checks, native renders, recipe audits, and report evidence.
