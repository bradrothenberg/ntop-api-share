"""Check the imported V2 example against the recipe it came from, and its manifest.

Two independent questions, both answerable with no nTop:

1. Did nTop reconstruct the graph? `export_as_recipe(..., recipe_only=True)` on
   the imported notebook writes back the root body only, with no `imports`. That
   readback must equal the source recipe's root body once identifiers and the
   keys the exporter adds are normalised away, using the same rules as
   `check_recipe.py`.

2. Does the source release match its own manifest? `release/V2_compact/` ships a
   `manifest.json` recording a size and SHA-256 for every file. Seven of the
   eight match. `Torx_Example.ntop` does not: on disk it is 15,233,693 bytes
   against the 1,544,256 the manifest signed, with a different digest. Converting
   a notebook runs every block at its default inputs and caches the result inside
   the file, so the released example had been reconverted after the manifest was
   written and carried about 13.7 MB of cached solve. The notebook this demo
   imports is 1,559,105 bytes, within 1 percent of the signed size.

That is why this demo carries the recipe and lands its own notebook, rather than
copying the released artefact across.

Run: `python check_example.py`. Exits non-zero if the graph differs.
"""

import hashlib
import json
import sys
from pathlib import Path

from check_recipe import normalise_body

DEMO = Path(__file__).resolve().parents[1]
SOURCE = DEMO / "inputs" / "recorded" / "torx_example_recipe.json"
MANIFEST = DEMO / "inputs" / "recorded" / "torx_v2_compact_manifest.json"
READBACK = DEMO / "output" / "torx_example.readback.json"
MODEL = DEMO / "models" / "Torx_Example.ntop"
RUN = DEMO / "output" / "example_run.json"

# The release the recipe was taken from, in the origin project. Absent from a
# public checkout, which is the point: only the recipe travels.
RELEASE = Path("D:/ntop_dev/ntop-mcp/projects/torx/release/V2_compact")


def compare_graph():
    source = json.loads(SOURCE.read_text(encoding="utf8"))
    result = {"source": SOURCE.name,
              "source_displayname": source["displayname"],
              "source_imports": len(source["imports"]),
              "source_root_body": len(source["body"]),
              "source_root_inputs": len(source["inputs"])}
    names = [d["displayname"] for d in source["imports"]]
    result["duplicate_display_names"] = sorted({n for n in names if names.count(n) > 1})
    if not READBACK.exists():
        result["readback"] = "absent; run torx_live.run_example first"
        result["identical"] = None
        return result
    readback = json.loads(READBACK.read_text(encoding="utf8"))
    result["readback_root_body"] = len(readback.get("body", []))
    # recipe_only omits the definitions, so only the root graph is comparable
    result["readback_carries_imports"] = bool(readback.get("imports"))
    a, b = normalise_body(source["body"]), normalise_body(readback["body"])
    result["same_variable_order"] = ([e.get("name") for e in source["body"]]
                                     == [e.get("name") for e in readback["body"]])
    result["identical"] = (a == b)
    if a != b:
        result["first_difference"] = next(
            ({"index": k, "name": x.get("name"),
              "source": json.dumps(x, sort_keys=True)[:500],
              "readback": json.dumps(y, sort_keys=True)[:500]}
             for k, (x, y) in enumerate(zip(a, b)) if x != y), None)
    return result


def compare_manifest():
    """Check every released file against the digest its own manifest records."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf8"))
    rows = []
    for name, recorded in sorted(manifest.items()):
        path = RELEASE / name
        row = {"file": name, "manifest_bytes": recorded["bytes"]}
        if not path.exists():
            row["on_disk"] = "not in this checkout"
            row["matches"] = None
        else:
            data = path.read_bytes()
            row["on_disk_bytes"] = len(data)
            row["matches"] = hashlib.sha256(data).hexdigest() == recorded["sha256"]
        rows.append(row)
    checked = [r for r in rows if r["matches"] is not None]
    return {"release": str(RELEASE),
            "files": rows,
            "checked": len(checked),
            "matching": sum(1 for r in checked if r["matches"]),
            "mismatched": [r["file"] for r in checked if not r["matches"]],
            "note": "a mismatch here is a fact about the source release, not about "
                    "this demo; the origin project is read-only from here"}


def main():
    report = {"graph": compare_graph(), "manifest": compare_manifest()}
    if MODEL.exists():
        report["imported_notebook"] = {
            "file": MODEL.name, "bytes": MODEL.stat().st_size}
        signed = json.loads(MANIFEST.read_text(encoding="utf8")).get("Torx_Example.ntop")
        if signed:
            report["imported_notebook"]["manifest_bytes"] = signed["bytes"]
            report["imported_notebook"]["relative_to_manifest"] = round(
                MODEL.stat().st_size / signed["bytes"] - 1, 4)
    if RUN.exists():
        run = json.loads(RUN.read_text(encoding="utf8"))
        report["import"] = {k: run.get(k) for k in
                            ("example_import_seconds", "custom_blocks_count",
                             "both_torx_blocks_kept", "variables_ok")}
    (DEMO / "output" / "check_example.json").write_text(
        json.dumps(report, indent=2), encoding="utf8")
    print(json.dumps(report, indent=2))
    return 0 if report["graph"]["identical"] in (True, None) else 1


if __name__ == "__main__":
    sys.exit(main())
