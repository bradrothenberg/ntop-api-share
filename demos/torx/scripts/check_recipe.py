"""Compare the ported offline recipe with nTop's own recorded recipe for this graph.

The source project authored the Torx in JavaScript, converted each block with
`ntopcl`, and nTop wrote back what it believes the graph is. That readback is
`inputs/recorded/torx_recorded_recipe.json`. This demo rebuilds the same graph in
Python against `torx_backend`. If the two agree once identifiers and the keys
nTop's exporter adds are normalised away, the port reproduces the native graph
and one `import_recipe` is a faithful substitute for the whole JavaScript and
`ntopcl` chain.

What is allowed to differ, and why:

  id / ref.id   nTop mints its own (`inst101`...); rule I1 says every conversion
                stamps new ones. Replaced by position.
  name          an anonymous node is named after the body counter that made it
                ("n17"), and nTop keeps that name while renumbering the id it was
                taken from. Auto-generated names are normalised to "". Named
                variables and named calls must still agree.
  type          `exportjson` writes a `type` key on every call node. Rule P6
                measures that `type` on a call node is refused at load, so the
                recipe route omits it. Dropped wherever a node carries `func`;
                kept on literals and on variable entries, where both routes
                write it and it must agree.
  props: []     an empty props array and an absent one mean the same thing.

Everything else — every function identifier, every literal value and unit, every
input index, every reference, every import and every cbRefs entry — must agree
exactly. `python check_recipe.py` prints the report and exits non-zero on any
difference.
"""

import json
import re
import sys
from pathlib import Path

DEMO = Path(__file__).resolve().parents[1]
OFFLINE = DEMO / "output" / "build" / "torx_recipe.json"
RECORDED = DEMO / "inputs" / "recorded" / "torx_recorded_recipe.json"

# names a body counter generates for an unnamed node, in either route
ANONYMOUS = re.compile(r"^[nd]\d+$")


def normalise_body(body):
    """Replace every node id with its position and drop exporter-only keys."""
    order = {}

    def collect(node):
        if isinstance(node, dict):
            if "id" in node:
                order.setdefault(node["id"], len(order))
            for k in sorted(node):
                collect(node[k])
        elif isinstance(node, list):
            for v in node:
                collect(v)

    for entry in body:
        collect(entry)

    def rewrite(node):
        if isinstance(node, dict):
            is_call = "func" in node
            out = {}
            for k, v in sorted(node.items()):
                if k == "id":
                    out[k] = "#%d" % order[v]
                elif k == "ref":
                    out[k] = {"id": "#%d" % order.get(v["id"], v["id"])}
                elif k == "name":
                    out[k] = "" if isinstance(v, str) and ANONYMOUS.match(v) else v
                elif k == "type" and is_call:
                    continue          # exportjson writes it; the recipe route omits it
                elif k == "props" and not v:
                    continue
                else:
                    out[k] = rewrite(v)
            return out
        if isinstance(node, list):
            return [rewrite(v) for v in node]
        return node

    return [rewrite(e) for e in body]


def normalise_inputs(inputs):
    """An input row, with the exporter's empty `dimension` key removed.

    nTop writes `"dimension": {}` on a dimensionless input; the recipe form omits
    the key entirely. Both declare the same input, and bloc.js only ever emitted
    a non-empty dimension, so an absent key and an empty one are the same fact.
    The preview under `contents` is normalised the same way a body node is.
    """
    out = []
    for i in inputs:
        row = {k: v for k, v in sorted(i.items()) if not (k == "dimension" and not v)}
        if "contents" in row:
            row["contents"] = normalise_body([row["contents"]])[0]
        out.append(row)
    return out


def compare_definition(a, b, label):
    """Compare one definition (an import, or the root recipe)."""
    result = {"block": label}
    result["same_signature"] = (a["name"] == b["name"])
    ia, ib = normalise_inputs(a["inputs"]), normalise_inputs(b["inputs"])
    result["inputs"] = {"offline": len(ia), "recorded": len(ib), "identical": ia == ib}
    if ia != ib:
        result["inputs"]["first_difference"] = next(
            ({"index": k, "offline": x, "recorded": y}
             for k, (x, y) in enumerate(zip(ia, ib)) if x != y), None)
    na, nb = normalise_body(a["body"]), normalise_body(b["body"])
    result["body"] = {"offline": len(na), "recorded": len(nb), "identical": na == nb}
    if na != nb:
        diffs = [{"index": k, "name": x.get("name"),
                  "offline": json.dumps(x, sort_keys=True)[:600],
                  "recorded": json.dumps(y, sort_keys=True)[:600]}
                 for k, (x, y) in enumerate(zip(na, nb)) if x != y]
        result["body"]["entries_differing"] = len(diffs)
        result["body"]["first_differences"] = diffs[:3]
    result["same_cbRefs"] = (a.get("cbRefs") == b.get("cbRefs"))
    result["same_description"] = (a.get("description") == b.get("description"))
    result["identical"] = all([result["same_signature"], result["inputs"]["identical"],
                               result["body"]["identical"], result["same_cbRefs"]])
    return result


def main():
    if not OFFLINE.exists():
        print("run build_torx.py first: %s is missing" % OFFLINE)
        return 2
    off = json.loads(OFFLINE.read_text(encoding="utf8"))
    rec = json.loads(RECORDED.read_text(encoding="utf8"))

    by_name_off = {d["displayname"]: d for d in off["imports"]}
    by_name_rec = {d["displayname"]: d for d in rec["imports"]}
    report = {
        "recorded": str(RECORDED.relative_to(DEMO)),
        "offline": str(OFFLINE.relative_to(DEMO)),
        "same_import_order": ([d["displayname"] for d in off["imports"]]
                              == [d["displayname"] for d in rec["imports"]]),
        "same_root_cbRefs": off.get("cbRefs") == rec.get("cbRefs"),
        "blocks": [],
    }
    for name in [d["displayname"] for d in rec["imports"]]:
        if name not in by_name_off:
            report["blocks"].append({"block": name, "identical": False,
                                     "error": "absent from the offline build"})
            continue
        report["blocks"].append(compare_definition(by_name_off[name], by_name_rec[name], name))
    report["blocks"].append(compare_definition(off, rec, "Torx (root)"))

    report["blocks_identical"] = sum(1 for b in report["blocks"] if b["identical"])
    report["blocks_total"] = len(report["blocks"])
    report["identical"] = (report["blocks_identical"] == report["blocks_total"]
                           and report["same_import_order"] and report["same_root_cbRefs"])
    (DEMO / "output" / "check_recipe.json").write_text(
        json.dumps(report, indent=2), encoding="utf8")
    print(json.dumps({k: v for k, v in report.items() if k != "blocks"}
                     | {"blocks": [{"block": b["block"], "identical": b["identical"],
                                    "body_entries": b["body"]["offline"],
                                    "inputs": b["inputs"]["offline"]}
                                   for b in report["blocks"]]}, indent=2))
    return 0 if report["identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
