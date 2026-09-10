"""Bridge between the nTop Python Console and an AI agent working on files.

The console is inside the GUI. An agent editing files cannot see what the
console prints, so every entry point here writes its result to a JSON file
under `_agent/` next to this repo. The agent reads those files with ordinary
file tools; the human only ever pastes a one-liner into the console.

Usage from the console (one line, repeat after every edit):

    py> import agent; agent.run(notebook, "demo1", "sphere_cube")

Everything else (`dump`, `blocks`, `api`) writes a file and returns its path.
"""

import contextlib
import importlib
import io
import json
import os
import sys
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(_HERE), "_agent")


def _write(name, payload):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=str)
    print(path)
    return path


# --- the main loop ------------------------------------------------------


def run(notebook, module_name, func_name="main", *args, **kwargs):
    """Reload `module_name`, call `func_name(notebook, *args, **kwargs)`.

    Writes `_agent/last_run.json`: status, printed output, return value and
    the full traceback on failure. Also refreshes `_agent/state.json`.
    """
    record = {
        "module": module_name,
        "func": func_name,
        "args": list(args),
        "kwargs": kwargs,
        "status": "error",
    }
    buffer = io.StringIO()
    try:
        module = importlib.import_module(module_name)
        module = importlib.reload(module)
        fn = getattr(module, func_name)
        with contextlib.redirect_stdout(buffer):
            record["result"] = fn(notebook, *args, **kwargs)
        record["status"] = "ok"
    except Exception:
        record["traceback"] = traceback.format_exc()
    record["stdout"] = buffer.getvalue()

    try:
        record["state"] = _state(notebook)
    except Exception:
        record["state_error"] = traceback.format_exc()

    _write("last_run.json", record)
    if record["status"] == "error":
        print(record["traceback"])
    return record["status"]


# --- inspection ---------------------------------------------------------


def _state(notebook):
    """Sections, every block in each of them, and every variable."""
    sections = notebook.list_sections()
    state = {"sections": [], "variables": notebook.list_variables()}
    for section in sections:
        blocks = notebook.list_blocks(section["id"])
        for block in blocks:
            try:
                block["inputs"] = _inputs(notebook, block["id"])
            except Exception as exc:
                block["inputs_error"] = str(exc)
        state["sections"].append({**section, "blocks": blocks})
    return state


def _inputs(notebook, block_id):
    """Every settable input on a block with its current value.

    list_block_inputs() also reports the block's own output, as a trailing
    entry with isReturnValue True whose name is the block id -- skip it,
    get_block_input() rejects that name.
    """
    out = []
    for spec in notebook.list_block_inputs(block_id):
        if spec.get("isReturnValue"):
            continue
        entry = dict(spec)
        try:
            entry["value"] = notebook.get_block_input(block_id, spec["name"])
        except Exception as exc:
            # Only real, vector and point can be read back; the rest raise.
            entry["value_error"] = str(exc)
        out.append(entry)
    return out


def dump(notebook):
    """Write the whole notebook state to `_agent/state.json`."""
    return _write("state.json", _state(notebook))


def recipe(notebook, name="notebook"):
    """Export the notebook as a JSON recipe the agent can read directly.

    This is the highest-fidelity view of what actually got built. Prefer it
    over state.json when checking wiring.
    """
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name + ".json")
    notebook.export_as_recipe(path)
    print(path)
    return path


def blocks(notebook, mask=""):
    """Write the block identifiers matching `mask` to `_agent/blocks.json`.

    Block identifiers are only known at runtime; they are not in the binary.
    Run this once with no mask to give the agent the full catalog.
    """
    found = notebook.list_available_blocks(mask)
    return _write("blocks.json", {"mask": mask, "count": len(found), "ids": found})


def properties(notebook, block_id):
    """Inputs and output properties of one block, to `_agent/block.json`."""
    return _write(
        "block.json",
        {
            "id": block_id,
            "inputs": notebook.list_block_inputs(block_id),
            "properties": notebook.list_block_properties(block_id),
        },
    )


def api(notebook):
    """Dump the real pybind signatures and docstrings to `_agent/api.txt`.

    Ground truth for argument order. Read this instead of trusting README.md
    or this file's comments, which lag the build.
    """
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "api.txt")
    buffer = io.StringIO()
    buffer.write("python: %s\n" % sys.version.replace("\n", " "))
    buffer.write("sys.path:\n  %s\n\n" % "\n  ".join(sys.path))
    for name in sorted(dir(notebook)):
        if name.startswith("_"):
            continue
        member = getattr(notebook, name)
        buffer.write("=== %s ===\n%s\n\n" % (name, getattr(member, "__doc__", None)))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(buffer.getvalue())
    print(path)
    return path
