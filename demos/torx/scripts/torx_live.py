"""Run the two imports inside the nTop Python Console and read the band back.

Dispatched with `scripts/ntop_tcp.py` against a verified task-owned process. It
calls `new_notebook()`: point it only at a task-owned scratch session, never at a
notebook someone is working in.

    import sys; sys.path.insert(0, r"<checkout>/demos/torx/scripts")
    import torx_live; torx_live.run(notebook)

What the run settles, in order:

  1. whether `import_recipe` accepts a recipe carrying custom-block definitions
     in `imports`, and whether those definitions become custom blocks in the
     notebook. `docs/API_REFERENCE.md` records no live method that creates one,
     so this is the question the demo exists to answer;
  2. what one import costs for a seven-block assembly of this size;
  3. whether the four native Choice Lists resolve to the source identifiers the
     public block expects;
  4. whether the geometry matches the frozen mirror at every surface point and
     sign probe `torx_spec.predictions()` declares.

Every wait is capped. A block in error reports `e_DIRTY` with no error field on
this build, which is indistinguishable from one still queued, so the value is
read and the state is recorded beside it rather than waited on.
"""

import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import torx_spec as spec
from torx_verification import SELECTION_VARIABLES

DEMO = os.path.dirname(_HERE)
BUILD = os.path.join(DEMO, "output", "build")
# models/ holds the released reference notebooks and is never written to.
# The port's own saves go to the ignored output tree.
MODELS = os.path.join(DEMO, "output", "ported")
OUT = os.path.join(DEMO, "output")

READ_BUDGET_S = 300.0
POLL_S = 2.0


def _safe(fn, *args):
    try:
        return {"value": fn(*args)}
    except Exception as exc:
        return {"error": "%s: %s" % (type(exc).__name__, exc)}


def _inventory(nb):
    """What the notebook holds, without assuming any one call tells the truth."""
    out = {"variables": _safe(nb.list_variables),
           "sections": _safe(nb.list_sections),
           "custom_blocks": _safe(nb.list_custom_blocks),
           "open_custom_block": _safe(nb.current_open_custom_block)}
    counts = {}
    for key in ("variables", "sections", "custom_blocks"):
        v = out[key].get("value")
        counts[key] = len(v) if isinstance(v, list) else None
    out["counts"] = counts
    return out


def _import(nb, recipe_name, record, tag, base=None):
    path = os.path.join(base or BUILD, recipe_name)
    record["%s_recipe" % tag] = path
    record["%s_recipe_bytes" % tag] = os.path.getsize(path)
    nb.new_notebook()
    empty = _inventory(nb)
    record["%s_empty_before" % tag] = empty["counts"]
    t0 = time.time()
    nb.import_recipe(path)
    record["%s_import_seconds" % tag] = round(time.time() - t0, 3)
    record["%s_after" % tag] = _inventory(nb)
    return record["%s_after" % tag]


def _read_many(nb, names, record, tag):
    """Read every named variable, polling only while something is still unread."""
    values, errors, polls = {}, {}, 0
    deadline = time.time() + READ_BUDGET_S
    t0 = time.time()
    while True:
        polls += 1
        for name in names:
            if values.get(name) is None:
                try:
                    values[name] = nb.get_block_input(name, "Input")
                except Exception as exc:
                    errors[name] = "%s: %s" % (type(exc).__name__, exc)
        if all(values.get(n) is not None for n in names) or time.time() > deadline:
            break
        time.sleep(POLL_S)
    record["%s_polls" % tag] = polls
    record["%s_read_seconds" % tag] = round(time.time() - t0, 3)
    record["%s_unread" % tag] = [n for n in names if values.get(n) is None]
    if errors:
        record["%s_read_errors" % tag] = errors
    return values


def run(nb):
    os.makedirs(MODELS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    record = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "interpreter_pid": os.getpid()}

    # ---- 1. the deliverable: the public block, one import --------------------
    after = _import(nb, "torx_recipe.json", record, "torx")
    blocks = after["custom_blocks"].get("value")
    record["custom_blocks_created"] = (
        [b.get("name") if isinstance(b, dict) else b for b in blocks]
        if isinstance(blocks, list) else blocks)
    model = os.path.join(MODELS, "Torx.ntop")
    nb.save_notebook_as(model)
    nb.export_as_recipe(os.path.join(OUT, "torx.readback.json"), True)
    record["model"] = model
    record["model_bytes"] = os.path.getsize(model) if os.path.exists(model) else None

    # the four Choice Lists, resolved by the notebook itself
    selections = {}
    for name, expected in SELECTION_VARIABLES.items():
        got = _safe(nb.get_block_input, name, "Input")
        got["expected"] = expected
        got["agrees"] = got.get("value") == expected
        got["state"] = _safe(nb.block_state, name).get("value")
        selections[name] = got
    record["selections"] = selections
    record["selections_agreeing"] = sum(1 for v in selections.values() if v["agrees"])

    # ---- 2. the measurable notebook, one import ------------------------------
    _import(nb, "torx_verification_recipe.json", record, "verification")

    predictions = spec.predictions()
    by_id = {s["id"]: s for s in predictions["samples"]}
    names = ["d %s" % s["id"] for s in predictions["samples"]]
    values = _read_many(nb, names, record, "band")

    results, boundary_worst, failures = [], 0.0, []
    for sample in predictions["samples"]:
        name = "d %s" % sample["id"]
        value = values.get(name)
        row = {"id": sample["id"], "configuration": sample["configuration"],
               "where": sample["where"], "kind": sample["kind"],
               "point_mm": sample["point_mm"], "value_mm": value}
        if value is None:
            row["verdict"] = "unread"
            row["state"] = _safe(nb.block_state, name).get("value")
        elif sample["kind"] == "boundary":
            residual_m = abs(value) * 1e-3
            row["residual_m"] = residual_m
            row["tolerance_m"] = sample["tolerance_m"]
            row["verdict"] = "pass" if residual_m <= sample["tolerance_m"] else "fail"
            boundary_worst = max(boundary_worst, residual_m)
        else:
            row["expected_sign"] = sample["expect"]
            row["verdict"] = "pass" if (value * sample["expect"] > 0) else "fail"
            row["margin_mm"] = abs(value)
        if row["verdict"] != "pass":
            failures.append(row)
        results.append(row)

    record["samples"] = results
    record["summary"] = {
        "total": len(results),
        "passed": sum(1 for r in results if r["verdict"] == "pass"),
        "failed": sum(1 for r in results if r["verdict"] == "fail"),
        "unread": sum(1 for r in results if r["verdict"] == "unread"),
        "boundary_worst_residual_m": boundary_worst,
        "boundary_gate_m": predictions["gate_m"],
        "selections_agreeing": record["selections_agreeing"],
        "selections_total": len(SELECTION_VARIABLES),
    }
    record["first_failures"] = failures[:20]

    verification_model = os.path.join(MODELS, "Torx_Verification.ntop")
    nb.save_notebook_as(verification_model)
    record["verification_model"] = verification_model
    record["verification_model_bytes"] = (os.path.getsize(verification_model)
                                          if os.path.exists(verification_model) else None)
    record["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    record["scope"] = ("one native session; field samples and a graph readback. "
                       "No mesh comparison and no manufacturing claim.")

    with open(os.path.join(OUT, "live_run.json"), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, default=str)
    return record["summary"]


def run_rejections(nb):
    """Import the gate cases and record what each block actually did.

    A block in error reports `e_DIRTY` with no error field on this build, so the
    verdict is taken from the pair (state, readable value): a refused
    configuration must not produce a number.
    """
    band = json.load(open(os.path.join(BUILD, "torx_band.json"), encoding="utf-8"))
    record = {"started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    _import(nb, "torx_rejections_recipe.json", record, "rejections")

    control = band["rejections"]["control"]
    time.sleep(5.0)
    rows = []
    for entry in [dict(control, name="control", expected_refused=False)] + \
            [dict(r, expected_refused=True) for r in band["rejections"]["rejections"]]:
        value = _safe(nb.get_block_input, entry["probe"], "Input")
        row = {"name": entry["name"], "gate": entry.get("gate"),
               "why": entry.get("why"), "expected_refused": entry["expected_refused"],
               "body_state": _safe(nb.block_state, entry["body"]).get("value"),
               "probe_state": _safe(nb.block_state, entry["probe"]).get("value"),
               "probe": value}
        got_number = isinstance(value.get("value"), (int, float))
        row["refused"] = not got_number
        row["verdict"] = "pass" if row["refused"] == entry["expected_refused"] else "fail"
        rows.append(row)
    record["cases"] = rows
    record["summary"] = {"total": len(rows),
                         "passed": sum(1 for r in rows if r["verdict"] == "pass"),
                         "failed": sum(1 for r in rows if r["verdict"] == "fail")}
    record["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(os.path.join(OUT, "rejections.json"), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, default=str)
    return record["summary"]


def run_figures(nb):
    """Import the slice stacks and wait, capped, for the archives to appear."""
    band = json.load(open(os.path.join(BUILD, "torx_band.json"), encoding="utf-8"))
    record = {"started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    _import(nb, "torx_figures_recipe.json", record, "figures")

    stacks = band["figures"]
    deadline = time.time() + 600
    while time.time() < deadline:
        if all(os.path.exists(s["zip"]) and os.path.getsize(s["zip"]) > 0
               for s in stacks):
            break
        time.sleep(5.0)
    record["stacks"] = [{
        "name": s["name"], "axis": s["axis"], "why": s["why"],
        "box_mm": s["box_mm"], "layer_mm": s["layer_mm"], "px": s["px"],
        "zip": s["zip"],
        "exists": os.path.exists(s["zip"]),
        "bytes": os.path.getsize(s["zip"]) if os.path.exists(s["zip"]) else None,
        "state": _safe(nb.block_state, s["variable"]).get("value"),
    } for s in stacks]
    # models/ carries the two deliverables only: this notebook stores the
    # absolute paths of its slice archives, so it stays in the ignored output/.
    model = os.path.join(OUT, "Torx_Figures.ntop")
    nb.save_notebook_as(model)
    record["model"] = model
    record["model_bytes"] = os.path.getsize(model) if os.path.exists(model) else None
    record["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(os.path.join(OUT, "figures.json"), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, default=str)
    return {"stacks": [{"name": s["name"], "bytes": s["bytes"]}
                       for s in record["stacks"]]}


def run_example(nb):
    """Import the source project's V2 example and land it as a notebook here.

    This is the harder import of the two. The Torx demo's own recipe carries
    seven definitions; this one carries fifteen, nested three deep, and TWO of
    them are both called `Torx`: the thirteen-input public block and the
    eighteen-input V2 wrapper that adds the mould branch and the flush
    placement. One display name, two different behaviours, two different uuids.

    A recipe refers to a definition by uuid, never by name, so the ambiguity is
    only in what a human reads. Whether `import_recipe` keeps both, or collapses
    them, is the question this run settles.

    The example itself is self-contained: no notebook inputs, one configured
    Torx call feeding both named list extractors and two native Boolean
    consumers.
    """
    record = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "interpreter_pid": os.getpid()}
    source = os.path.join(DEMO, "inputs", "recorded", "torx_example_recipe.json")
    recipe = json.load(open(source, encoding="utf-8"))
    record["source"] = os.path.basename(source)
    record["source_displayname"] = recipe["displayname"]
    record["source_description"] = recipe["description"]
    record["expected"] = {
        "imports": len(recipe["imports"]),
        "import_names": [d["displayname"] for d in recipe["imports"]],
        "duplicate_display_names": sorted(
            {n for n in (d["displayname"] for d in recipe["imports"])
             if [x["displayname"] for x in recipe["imports"]].count(n) > 1}),
        "root_variables": [e.get("name") for e in recipe["body"]],
        "root_inputs": len(recipe["inputs"]),
    }

    after = _import(nb, "torx_example_recipe.json", record, "example",
                    base=os.path.join(DEMO, "inputs", "recorded"))
    blocks = after["custom_blocks"].get("value")
    created = ([b.get("name") if isinstance(b, dict) else b for b in blocks]
               if isinstance(blocks, list) else blocks)
    record["custom_blocks_created"] = created
    if isinstance(created, list):
        record["custom_blocks_count"] = len(created)
        record["both_torx_blocks_kept"] = created.count("Torx") == 2

    variables = after["variables"].get("value")
    names = [v.get("id") if isinstance(v, dict) else v for v in variables] \
        if isinstance(variables, list) else []
    record["variables"] = names
    # a list-valued variable is not readable through get_block_input on this
    # build, so the verdict is taken from the build state of each one
    time.sleep(5.0)
    states = {}
    for name in names:
        state = _safe(nb.block_state, name).get("value") or {}
        states[name] = state.get("buildState", state.get("error", "unknown"))
    record["variable_states"] = states
    record["variables_ok"] = sum(1 for s in states.values() if s == "e_OK")

    model = os.path.join(MODELS, "Torx_Example.ntop")
    nb.save_notebook_as(model)
    readback = os.path.join(OUT, "torx_example.readback.json")
    nb.export_as_recipe(readback, True)
    record["model"] = model
    record["model_bytes"] = os.path.getsize(model) if os.path.exists(model) else None
    record["readback_bytes"] = (os.path.getsize(readback)
                                if os.path.exists(readback) else None)
    record["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    record["scope"] = ("one import and a graph readback. The geometry of this "
                       "example is not re-verified here; the Torx demo's own "
                       "samples cover the screw it calls.")
    with open(os.path.join(OUT, "example_run.json"), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, default=str)
    return {"custom_blocks": record.get("custom_blocks_count"),
            "both_torx_kept": record.get("both_torx_blocks_kept"),
            "variables_ok": record["variables_ok"], "of": len(names),
            "seconds": record["example_import_seconds"],
            "model_bytes": record["model_bytes"]}
