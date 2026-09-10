"""Write the engine's parameter table as an nTop recipe.

The Notebook API sets `real` inputs in the notebook's DISPLAY unit and
cannot attach a dimension, so every length, angle, volume, integer and
file path is authored here in SI with an explicit `units` map and
imported with `import_recipe`, which merges into the open notebook.

Run from the I6Engine folder:

    uv run python demos/i6/scripts/make_engine_recipe.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import engine_spec as spec  # noqa: E402

OUT = ROOT / "output/_agent" / "engine_literals.json"
EXPORT_DIR = ROOT / "output/exports"


def _real(value: float, units: dict) -> dict:
    return {"type": "real", "value": {"isFinite": True, "units": dict(units), "val": float(value)}}


def _var(i: int, name: str, type_name: str, contents: dict, description: str = "") -> dict:
    entry = {"contents": contents, "id": "eng_lit_%03d" % i, "name": name, "type": type_name, "variable": True}
    if description:
        entry["description"] = description
    return entry


def build_recipe() -> dict:
    body = []
    i = 0
    for name, (mm, desc) in spec.LENGTHS.items():
        body.append(_var(i, name, "real", _real(mm * 1e-3, {"length": 1}), desc)); i += 1
    for name, (cc, desc) in spec.VOLUMES.items():
        body.append(_var(i, name, "real", _real(cc * 1e-6, {"length": 3}), desc)); i += 1
    for name, (deg, desc) in spec.ANGLES.items():
        body.append(_var(i, name, "real", _real(math.radians(deg), {"angle": 1}), desc)); i += 1
    for name, (val, desc) in spec.DIMENSIONLESS.items():
        body.append(_var(i, name, "real", _real(val, {}), desc)); i += 1
    for name, (val, desc) in spec.INTEGERS.items():
        body.append(_var(i, name, "integer", {"type": "integer", "value": {"val": int(val)}}, desc)); i += 1
    for part, (fname, _tol) in spec.EXPORT_PARTS.items():
        path = (EXPORT_DIR / fname).as_posix()
        body.append(_var(i, spec.export_path_var(part), "file_path",
                         {"type": "file_path", "value": {"val": path}}, "STL export of " + part)); i += 1
    return {
        "body": body,
        "cbRefs": [],
        "description": "Parametric inline-six engine authored through the nTop Notebook API. "
                       "Change 'Crank Angle' to move it.",
        "displayname": "I6 Engine",
        "imports": [],
        "inputs": [],
        "name": "user_func_i6_engine_literals_0000_000000000000",
        "namespaces": [],
        "version": [1, 0, 0],
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    recipe = build_recipe()
    OUT.write_text(json.dumps(recipe, indent=1), encoding="utf-8")
    print("%s  (%d variables)" % (OUT, len(recipe["body"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
