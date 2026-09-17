"""The public Torx plus its measurement band, in one recipe and one import.

The band holds one configuration per entry in `torx_spec.CONFIGURATIONS` and one
`evaluate_field` probe per frozen prediction. Everything is built offline, so a
single `import_recipe` lands a notebook that is already measurable: no live
setter is involved, and no configuration has to be typed in by hand.

Three configurations go through `Place Screw` with a real frame; the rest sit at
the identity placement, so their local and world coordinates agree and a
disagreement there can only come from the assembly. The three placed ones share
one rotation and differ only in the insertion point, which is what separates a
rotation cost from a translation cost.

Why the band does not drive the public Choice Lists. A choice input cannot be
set from the live API on this build: `docs/API_REFERENCE.md` lists real, vector,
point, integer, bool and text for the live setters, and a `choice` is none of
them. Each configuration therefore calls `Torx Local Development` directly with
integer literals the recipe carries. The Choice Lists are checked separately, by
reading back the four selection variables the public root body computes.
"""

import json
from pathlib import Path

import torx_spec as spec
from torx import (IDENTITIES, TORX_DESCRIPTION, countersunk_head, metric_thread,
                  pan_head, place_screw, screw_head, torx, torx_internal, torx_local)
from torx_backend import A, B, I, L, P3, R, Recipe, V, flatten

DEMO = Path(__file__).resolve().parents[1]
MM = 1e-3

# The four root variables the public block computes from its Choice Lists, and
# the identifier each must resolve to at the recipe's own default selections.
SELECTION_VARIABLES = {
    "Drive family selection": 0,      # Internal Torx
    "Screw series selection": 0,      # Cylindrical / ISO 14579:2011
    "Metric size selection": 2,       # M3 x 0.5, the third label
    "Drive size selection": 0,        # Automatic
}


def _local_args(b, kwargs):
    """Integer and real literals for one direct call to the local assembly."""
    return [
        I(kwargs.get("family", 0)),
        I(kwargs.get("series", 0)),
        I(kwargs.get("size_id", 2)),
        I(kwargs.get("drive_size", 0)),
        L(kwargs.get("length_mm", 10.0) * MM),
        B(kwargs.get("override_shank", False)),
        L(kwargs.get("shank_radius_mm", 1.5) * MM),
        B(kwargs.get("override_torx", False)),
        L(kwargs.get("torx_radius_mm", 1.4) * MM),
    ]


def build():
    """The complete recipe: the public block, then the measurement band."""
    head, pan, csk = screw_head(), pan_head(), countersunk_head()
    thread, drive = metric_thread(), torx_internal()
    local = torx_local(head, pan, csk, thread, drive)
    place = place_screw()
    b = torx(local, place)

    predictions = spec.predictions()
    by_config = {}
    for row in predictions["samples"]:
        by_config.setdefault(row["configuration"], []).append(row)

    band = {"configurations": [], "probes": []}
    for entry in predictions["configurations"]:
        name = entry["name"]
        b.sec("Verification: %s" % name, entry["why"])
        screw = b.once(b.call(local, _local_args(b, entry["kwargs"]),
                              "Local screw %s" % name),
                       "Screw %s" % name, "implicit")
        placement = entry["placement"]
        body = b.once(
            b.call(place, [screw,
                           P3(*[v * MM for v in placement["origin_mm"]]),
                           V(*placement["axis"]),
                           V(*placement["tangent"]),
                           A(placement["clocking_rad"])],
                   "Placed %s" % name),
            "Body %s" % name, "implicit")
        band["configurations"].append({"name": name, "variable": "Body %s" % name})

        for row in by_config.get(name, []):
            point = b.PT(*[L(v) for v in row["point_m"]])
            probe = b.F("evaluate_field<real_field,point>", [body, point])
            var = "d %s" % row["id"]
            b.VAR(var, var, "real", probe)
            band["probes"].append({"variable": var, "id": row["id"]})

    imports = flatten([local, place])
    recipe = b.envelope(IDENTITIES["Torx"], "Torx",
                        TORX_DESCRIPTION + " This copy carries the verification band.",
                        "result", imports=imports)
    return recipe, b, band, predictions


def build_rejections():
    """Every invalid configuration the mirror predicts, plus a valid control.

    The graph's gate is `sqrt(+1 or -1)`: an invalid configuration is made to
    refuse evaluation rather than build a plausible wrong screw. The control
    separates "the gate refused this input" from "the notebook failed".
    """
    head, pan, csk = screw_head(), pan_head(), countersunk_head()
    thread, drive = metric_thread(), torx_internal()
    local = torx_local(head, pan, csk, thread, drive)
    place = place_screw()
    b = Recipe([])
    band = {"control": None, "rejections": []}

    b.sec("Control", "A valid configuration, so a failure below is the gate and not "
                     "the import.")
    control = b.VAR("Control", "Control", "implicit",
                    b.call(local, _local_args(b, {}), "Control screw"))
    b.VAR("d control", "d control", "real",
          b.F("evaluate_field<real_field,point>",
              [control, b.PT(L(1.4 * MM), L(0.0), L(-2.365 * MM))]))
    band["control"] = {"body": "Control", "probe": "d control",
                       "expected": "builds; the probe reads the recess lobe at 0"}

    b.sec("Refused inputs",
          "Each of these breaks one named condition of the validity gate.")
    for name, kwargs, gate, why in spec.REJECTIONS:
        body = b.once(b.call(local, _local_args(b, kwargs), "Rejected %s" % name),
                      "Reject %s" % name, "implicit")
        var = "d reject %s" % name
        b.VAR(var, var, "real",
              b.F("evaluate_field<real_field,point>",
                  [body, b.PT(L(0.0), L(0.0), L(0.0))]))
        band["rejections"].append({"name": name, "body": "Reject %s" % name,
                                   "probe": var, "gate": gate, "why": why})

    imports = flatten([local, place])
    recipe = b.envelope("user_func_Torx_Rejections", "Torx Rejections",
                        "Validity-gate cases. Every block below the control is expected "
                        "to refuse evaluation. Not a deliverable.",
                        "Control", imports=imports)
    return recipe, b, band


# Slice stacks. The print volume stays strictly inside the body's own driven
# bounding box: a slice plane lying exactly on a print-volume face rasterises the
# box outline instead of the section (measured on this block family), and a
# one-layer volume writes no archive at all.
FIGURES = [
    {"name": "recess", "axis": "z",
     "box_mm": [[-2.749, -2.749, -2.95], [2.749, 2.749, -1.80]],
     "layer_mm": 0.2, "px": [900, 900],
     "why": "transverse sections through the head: the recess mouth, the lobed wall "
            "and the solid web below the recess floor"},
    {"name": "profile", "axis": "y",
     # y from -0.8 in steps of 0.4 puts slice 3 exactly on the axis, under the
     # measured first-plane law BOX0 + (k-1)h.
     "box_mm": [[-2.749, -0.8, -2.98], [2.749, 0.8, 9.98]],
     "layer_mm": 0.4, "px": [1500, 700],
     "why": "axial sections through the screw: head, seat, fillet, plain shank, "
            "thread and flat tip"},
    # A fine stack across one plane the mirror knows exactly: the recess floor at
    # z = -1.73 mm. The body is re-bounded to a thin slab first, so the stack
    # cannot overrun the whole screw at this layer height. The index at which the
    # recess hole closes pins the slicer's first-plane offset to half a layer,
    # which is 0.0025 mm here.
    {"name": "calibration", "axis": "z",
     "box_mm": [[-1.9, -1.9, -1.79], [1.9, 1.9, -1.67]],
     "slab_mm": [[-2.0, -2.0, -1.80], [2.0, 2.0, -1.66]],
     "layer_mm": 0.005, "px": [128, 128],
     "why": "the recess floor, at 5 micrometre layers, to measure where the "
            "slicer puts its first plane",
     "known_plane_mm": -1.73,
     "publish": False},
]


def build_figures(out_dir):
    """The default screw plus two native slice stacks, for the report figures.

    Numbers describing a shape are not a check of the shape. These rasters are
    nTop's own, produced by the same notebook that produced the samples.
    """
    head, pan, csk = screw_head(), pan_head(), countersunk_head()
    thread, drive = metric_thread(), torx_internal()
    local = torx_local(head, pan, csk, thread, drive)
    place = place_screw()
    b = Recipe([])
    b.sec("Screw", "The block's own defaults, placed at the origin.")
    screw = b.once(b.call(local, _local_args(b, {}), "Local screw"), "Screw", "implicit")
    body = b.VAR("Torx", "Torx", "implicit",
                 b.call(place, [screw, P3(0, 0, 0), V(0, 0, 1), V(1, 0, 0), A(0)],
                        "Placed screw"))

    stacks = []
    b.sec("Slice stacks", "Native rasters. The print volume stays inside the body's "
                          "own driven bounds.")
    for figure in FIGURES:
        lo, hi = figure["box_mm"]
        box = b.bbox(b.PT(*[L(v * MM) for v in lo]), b.PT(*[L(v * MM) for v in hi]))
        if figure["axis"] == "z":
            first, second = V(1, 0, 0), V(0, 1, 0)
        else:                                     # slicing normal to Y
            first, second = V(0, 0, 1), V(1, 0, 0)
        frame = b.frame(b.PT(*[L(v * MM) for v in lo]), first, second)
        target = body
        if figure.get("slab_mm"):
            # Re-declare the body's bounds so the stack cannot run the length of
            # the screw at a five micrometre layer height.
            slo, shi = figure["slab_mm"]
            slab = b.bbox(b.PT(*[L(v * MM) for v in slo]), b.PT(*[L(v * MM) for v in shi]))
            target = b.once(b.SBB(body, slab), "Slab %s" % figure["name"], "implicit")
        path = str(Path(out_dir) / ("torx_%s.zip" % figure["name"])).replace("\\", "/")
        node = b.F("slice_implicit_to_image<file_path,bool,implicit,real,frame,"
                   "bounding_box,integer,integer,gray_scale_bits_enum>[2.0.0]",
                   [{"type": "file_path", "value": {"val": path}}, B(False), target,
                    L(figure["layer_mm"] * MM), frame, box,
                    I(figure["px"][0]), I(figure["px"][1]),
                    {"type": "gray_scale_bits_enum", "value": {"enum": 1}}])
        var = "Slices %s" % figure["name"]
        b.VAR(var, var, "slice_image_data", node)
        stacks.append(dict(figure, variable=var, zip=path))

    imports = flatten([local, place])
    recipe = b.envelope("user_func_Torx_Figures", "Torx Figures",
                        "Native slice stacks of the default screw. Not a deliverable.",
                        "Torx", imports=imports)
    return recipe, b, stacks


if __name__ == "__main__":
    from torx_backend import count_nodes, validate, write
    recipe, ctx, band, predictions = build()
    problems = validate(recipe)
    if problems:
        raise RuntimeError("incomplete recipe:\n  " + "\n  ".join(problems))
    out = DEMO / "output" / "build" / "torx_verification_recipe.json"
    write(recipe, out, sections=ctx.sections_json())

    reject_recipe, reject_ctx, reject_band = build_rejections()
    reject_problems = validate(reject_recipe)
    reject_out = DEMO / "output" / "build" / "torx_rejections_recipe.json"
    write(reject_recipe, reject_out, sections=reject_ctx.sections_json())

    figure_dir = DEMO / "output" / "report_figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    fig_recipe, fig_ctx, stacks = build_figures(figure_dir)
    fig_problems = validate(fig_recipe)
    fig_out = DEMO / "output" / "build" / "torx_figures_recipe.json"
    write(fig_recipe, fig_out, sections=fig_ctx.sections_json())

    (DEMO / "output" / "build" / "torx_band.json").write_text(
        json.dumps({"configurations": band["configurations"],
                    "probes": band["probes"],
                    "selection_variables": SELECTION_VARIABLES,
                    "rejections": reject_band,
                    "figures": stacks,
                    "counts": predictions["counts"]}, indent=2), encoding="utf8")
    print(json.dumps({
        "verification": {"recipe": str(out.relative_to(DEMO)),
                         "bytes": out.stat().st_size,
                         "root_body_entries": len(recipe["body"]),
                         "imports": len(recipe["imports"]),
                         "func_nodes": count_nodes(recipe),
                         "configurations": len(band["configurations"]),
                         "probes": len(band["probes"]),
                         "problems": problems},
        "rejections": {"recipe": str(reject_out.relative_to(DEMO)),
                       "bytes": reject_out.stat().st_size,
                       "cases": len(reject_band["rejections"]),
                       "problems": reject_problems},
        "figures": {"recipe": str(fig_out.relative_to(DEMO)),
                    "bytes": fig_out.stat().st_size,
                    "stacks": [s["name"] for s in stacks],
                    "problems": fig_problems},
        "selection_variables": len(SELECTION_VARIABLES)}, indent=2))
