"""Copy the receipts the report cites out of the ignored output/ tree.

`**/output/` is not published, so a report that links into it links nowhere in a
fresh checkout. This writes the compact, path-free receipts to `evidence/`, the
same place the other demos keep theirs, and drops the two fields that would carry
a machine path.

Run: `uv run --locked python demos/torx/scripts/publish_evidence.py`
"""

import json
from pathlib import Path

DEMO = Path(__file__).resolve().parents[1]
OUT = DEMO / "output"
EVIDENCE = DEMO / "evidence"

# absolute paths belong to the run, not to the evidence
MACHINE_PATHS = ("model", "verification_model", "torx_recipe", "verification_recipe",
                 "rejections_recipe", "figures_recipe", "zip", "archive")


def strip(node):
    if isinstance(node, dict):
        return {k: (Path(v).name if k in MACHINE_PATHS and isinstance(v, str) else strip(v))
                for k, v in node.items()}
    if isinstance(node, list):
        return [strip(v) for v in node]
    return node


def main():
    EVIDENCE.mkdir(exist_ok=True)
    written = []

    live = json.loads((OUT / "live_run.json").read_text(encoding="utf8"))
    # the full sample table is 295 kB; publish the summary and the boundary points,
    # which are what the report cites, and say where the rest lives
    boundary = [s for s in live["samples"] if s["kind"] == "boundary"]
    published = {k: v for k, v in live.items() if k != "samples"}
    published["boundary_samples"] = boundary
    published["sign_samples_omitted"] = len(live["samples"]) - len(boundary)
    published["note"] = ("the %d sign probes are summarised in `summary` and retained "
                         "in the ignored output/live_run.json"
                         % published["sign_samples_omitted"])

    spec_check = json.loads((OUT / "check_spec.json").read_text(encoding="utf8"))
    spec_published = {k: v for k, v in spec_check.items() if k != "rows"}
    spec_published["failed_rows"] = [r for r in spec_check["rows"] if not r["pass"]]

    for name, payload in (
            ("live_run.json", published),
            ("check_spec.json", spec_published),
            ("check_recipe.json", json.loads((OUT / "check_recipe.json").read_text(encoding="utf8"))),
            ("rejections.json", json.loads((OUT / "rejections.json").read_text(encoding="utf8"))),
            ("figures_measured.json", json.loads((OUT / "figures_measured.json").read_text(encoding="utf8"))),
            ("port_receipt.json", json.loads((OUT / "port_receipt.json").read_text(encoding="utf8"))),
            ("check_example.json", json.loads((OUT / "check_example.json").read_text(encoding="utf8"))),
            ("example_run.json", json.loads((OUT / "example_run.json").read_text(encoding="utf8")))):
        path = EVIDENCE / name
        path.write_text(json.dumps(strip(payload), indent=2), encoding="utf8")
        written.append({"file": "evidence/%s" % name, "bytes": path.stat().st_size})

    manifest = {
        "scope": "receipts cited by reports/index.html, copied out of the ignored "
                 "output/ tree with machine paths reduced to file names",
        "build": "nTop 6.1.0-rc commit-050d0c7cdc8e412c3a35298bc5a89dc8a6da864d",
        "session": {"pid": live["interpreter_pid"], "started": live["started"],
                    "finished": live["finished"]},
        "files": written,
    }
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
