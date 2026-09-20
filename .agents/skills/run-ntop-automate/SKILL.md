---
name: run-ntop-automate
description: "Execute prepared nTop notebooks with ntopcl. Use for headless runs, template discovery, geometry export, version checks, and Linux CAD interoperability diagnostics."
---

# Run nTop Automate

nTop Automate (`ntopcl`, also called nTop CL) evaluates prepared `.ntop` notebooks.
Use [Notebook API](../ntop-notebook-api/SKILL.md) to author native graphs.
Use [ntop-automate](../ntop-automate/SKILL.md) for JSON schemas and [DOE sweeps](../ntop-doe-sweep/SKILL.md) for studies.

## Prepare and execute

Locate a licensed executable and record `ntopcl --version` and `ntopcl --help`.
Check compatibility with the notebook's saved version. Do not assume backward compatibility.
Generate templates in a task-owned run directory:

```text
ntopcl --template model.ntop
ntopcl -j input.json -o output.json model.ntop -v 2
```

Resolve executable, notebook, and JSON paths before starting a subprocess in another working directory.
Use the generated names, types, units, and enum values. Preserve the source notebook; `--save` overwrites it.
Set export inputs to the owned output directory. Imported file paths must still point to actual input files.
Use `--trustnotebook` only for a notebook whose file-writing and Run Command blocks are understood and authorized.
Obtain license options from the installed build. Inject named-user credentials at runtime or use the configured license.
Keep credentials out of committed JSON, printed commands, and shared logs.

## Decide whether the run succeeded

Record the exit code, log, returned JSON, and expected exports together.
Check that outputs are fresh, nonempty, parseable, and complete for this input configuration.
A JSON file or one early export can survive a later meshing failure.
An expected STL count must come from the model contract, not a universal count.

Older source experiments recorded exit 72 with usable outputs in one setup.
That observation is not a general success rule. Keep a nonzero exit as an anomaly until the matching build and outputs are checked.
An exit of zero also does not prove every export succeeded.

## Linux CAD export diagnostics

Historical 5.49.2 and 5.50.2 deployments needed the bundled InterOp libraries and Parasolid schemas for CAD exports.
Mesh exports could succeed while STEP or Parasolid exports failed.
Inspect the installed layout and log before applying this pattern:

```bash
NTOP_INSTALL=/path/to/ntop
export LD_LIBRARY_PATH="$NTOP_INSTALL:$NTOP_INSTALL/interop/dependencies/code/bin${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export P_SCHEMA="$NTOP_INSTALL/Schemas"
```

Check library dependencies on minimal Linux images. Use paths from the actual installation.
Check notebook path concatenation: a Windows backslash can become a literal filename character on Linux.
Fix the output expression or create a documented working copy. Do not rename imported inputs blindly.

## Timeouts and recovery

Measure a representative run before choosing timeout and concurrency settings.
Bound each attempt. Keep its input, log, PID, start time, return code, and output checks.
Terminate only the owned process tree on timeout; terminating a launcher may leave child processes alive.
Use a new attempt directory so old exports cannot pass a later run's checks.
Retry only a bounded number of times. Repeated failure at the same input requires a model-level investigation.
Keep geometry warnings and failed points for reproduction.

These are portable adaptations of recorded deployments. This package does not install nTop, provide a license, or establish fresh native results.
