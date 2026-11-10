# Native authoring and display workflow

Read the installed `ntop-notebook-api` skill before live authoring.
The car case used prototype build 42926. Older workspace notes describe build 42594 and some obsolete transport behavior.
Verify the installed executable, catalog, and current API with a small pilot instead of combining incompatible instructions.

## Run one guarded authoring session

Use the prototype GUI's Python Console Notebook API. The renderer and `ntopcl` are separate capabilities.
The case supports a Windows message bridge and a local TCP console, depending on the build.
Guard the exact process ID, executable path, and process start time before every dispatch.
Preserve unrelated or unsaved user notebooks. Continue within existing authorization for task-owned saved copies.

The 9 October recovery used build 42926's console at `127.0.0.1:2323` after opening the Python Console.
A running process does not prove that its console or listener is ready.
Require the listener to belong to the verified task PID and bind only to the documented loopback address.
Then read the prompt and query the embedded PID before sending model code.
The measured build exposed neither `paused_updates` nor `set_block_visibility`. Inspect actual capabilities; do not infer them from newer documentation.
When visibility setters are absent, retain importer defaults and verify saved presentation separately.

Do not reuse the historical CarSurface session record as a live session.
Its authoring process was stopped after the full display mesh exceeded the available resource envelope.
Verify or establish the current task session before using the helper.

Dispatch one command at a time with a unique run tag and a completion receipt.
A visible `py>` prompt or increasing CPU use does not establish completion.
Require a result receipt, check success or cancellation, and inspect the resulting file before the next dependent call.
Never select the first process named nTop or send blind foreground keystrokes.

Case transport:
dispatch.ps1 (source-project artifact; not bundled),
ntop_console_post.ps1 (source-project artifact; not bundled), and
guarded TCP dispatch (source-project artifact; not bundled).
These helpers use local paths and session data. Inspect and adapt them for a new task.

## Build and verify recipes

Use explicit SI literals. Live input readback can use display units instead.
Validate the export unit convention with a known one-metre control before interpreting field values.
Use named variables for shared outputs and property owners; plain-block fan-out can lose connections in this prototype.
Give function occurrences unique IDs. References to the same existing definition can repeat.

`import_recipe` merges into the current book. Use a fresh task-owned book or a controlled saved revision.
Importing only a few controls can still reevaluate a retained heavy graph.
For a small native test, build the dependency closure of the requested output and its witnesses.

`connect_block_property` does not replace a populated input in the measured build.
If the call reports that the input already has a value, clear only that target input and reconnect.
Check the resulting native connection and value. Do not treat the exception as proof of successful wiring.

Host Python work uses `uv run`. Code inside the nTop Python Console uses its embedded interpreter.
Load project modules from the intended directory and reload their changed dependencies.
Check `__file__` if results conflict with the source. Avoid the retired `nTopScriptsOLD` path.

### Recover a large import with bounded stages

Recipe references resolve within one import. Splitting a recipe at variable boundaries leaves cross-import references unresolved.
The measured recovery imports each small stage with empty typed dependency variables.
It connects earlier named variables to each dependency variable's `Input` through `connect_block_property`.
Properties remain on their original reference edges. These added variables are transparent aliases, not copied geometry.

Start with a small bridge pilot, then measure early construction stages before scaling.
Use topological order and exact expected-name checks; `import_recipe` can rename duplicates.
After each stage, export the recipe, verify expanded graph identity, check states, and save a separate checkpoint.
Keep function identifiers, types, literals, units, and property paths in the graph comparison.
Named outputs and independent native field witnesses still require verification.

The 9 October pilot completed in 0.385 seconds on build 42926.
The first eight six-variable stages verified 48 original variables and completed in 0.185 to 2.339 seconds each.
These measurements establish early recovery behavior only. They do not establish full-car import, QA, rendering, or Class A acceptance.
A single QA variable can contain hundreds of field evaluations; variable count alone does not bound its runtime.

See chunked_import.py (source-project artifact; not bundled),
pilot receipt (source-project artifact; not bundled), and
checkpoint plan and recovery instructions (source-project artifact; not bundled).
The staged case preserves the source recipe and adds aliases to its section layout.

A client timeout does not cancel native work. Do not retry an unknown outcome or continue over a pending stage.
After an application exit, reconcile receipts and restart from the last complete checkpoint in a verified task-owned process.
Check its hash and live graph before continuation. Preserve partial failure evidence before any explicit retry.
Never reset a nonempty book based only on its process name.

## Independent native witnesses

Check variable states and independently predicted field values. `e_OK` alone proves neither correct geometry nor correct units.
Include exterior surface points, retained material, cavity points, wheel transitions, caps, and the underside.
Use exact cubic section distance in the mathematical reference, rather than a coarse polyline matching the implementation's approximation.
Report excluded or unbracketed probes separately.

The case's bulk method evaluates a list of points and exports a dictionary in one operation.
It avoids repeated live getter overhead. Run its small end-to-end pilot before scaling the sample set.
See bulk_qa.py (source-project artifact; not bundled),
prepare_shell_bulk.py (source-project artifact; not bundled), and
audit_shell_native.py (source-project artifact; not bundled).
The staging script writes files and creates code that starts a new notebook; inspect its paths and session assumptions before dispatch.

Remove temporary export consumers before packaging a read-only viewer file.
Include QA-only dependency aliases in cleanup; this case names them `QA __Chunk ...`.
Retain construction aliases that support geometry and include them in the final section layout.
Prove the reachable geometry expression remains identical after cleanup.
The case fingerprint resolves literals from `main/leaves/index` only.
Cached object chunks reuse IDs; scanning every chunk as one literal namespace produced false geometry conflicts.
See qa_finalize.py (source-project artifact; not bundled).

## Native cameras and pixels

Use a saved-file native render with explicit camera settings and a source-file hash.
Do not claim it shows unsaved GUI changes.
Build 42926 forced a 60-degree perspective field of view in the measured renderer.
The case matched focal pixels by enlarging the sensor height and taking an exact integer central crop.
This preserved native samples; it did not rescale or warp the model image.
Measure current renderer behavior before reusing this workaround.

Bind the crop plan, raw image, final image, and physical camera to the comparison receipt.
If a renderer option is ignored or downgraded, record actual behavior and inspect the pixels.
Use native shaded and zebra images. Synthetic illustrations are not evidence of nTop geometry.
See native_camera.py (source-project artifact; not bundled) and
render_native.ps1 (source-project artifact; not bundled).

## Keep display work bounded

Keep editable implicit geometry separate from expensive display meshing.
The preferred measured route is Mesh from Implicit Body by AT with Remesh enabled, then one Sharpen pass.
Verify current block identifiers and enum values in the Notebook API skill before use.

Start with a sub-minute connectivity and export pilot. Then time a representative geometry pilot before attempting a full fine mesh.
Check actual exported bounds, components, winding, edge incidence, visual quality, and deviation from the source where measurable.
Record free system memory and process memory as the build runs.
Define the permitted time and memory envelope for the current machine and task.

Do not extrapolate runtime from strip width: this AT path expanded its bounds to a cube internally.
A strip can also introduce artificial corner components and sharpening overshoot at its clip planes.
Closed, manifold, oriented triangles do not by themselves prove acceptable surface deviation or lack of self-intersection.

If time or resource limits are exceeded, preserve receipts and the accepted source, then stop only the verified task-owned job.
Record cancellation as cancellation. A local strip success is not a full-model success.
Do not thicken, fill, or move the source body to conceal a display artifact.

See prepare_full_shell_mesh.py (source-project artifact; not bundled) and
audit_shell_mesh.py (source-project artifact; not bundled).
The full-mesh helper has a hard-coded case tolerance; adapt it only after a new pilot.

## Save presentation without changing geometry

Use named sections and saved inspection views. Keep only the intended final body visible.
Collapse every authored and nested block and section; preserve the expanded notebook root.
Reapply after the final GUI or API save.

Container edits in this workflow are limited to verified presentation mechanics.
Require an exact unmodified byte round trip, reject unknown layouts, and preserve the API-saved source.
Prove reachable geometry, literals, units, input contracts, and property connections stayed unchanged.
Do not use presentation patching as an alternate geometry-authoring route.
Reopen or render the final saved result and inspect it.

See finish_native.py (source-project artifact; not bundled) and
presentation_views.py (source-project artifact; not bundled).
