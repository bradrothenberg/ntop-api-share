"""The registered offline build: one complete Torx recipe, no nTop.

`uv run --locked python scripts/build.py torx` runs this, then the repository's
own `verify_recipe` pass over the result.
"""

import json
import time
from pathlib import Path

from torx import graph
from torx_backend import count_nodes, validate, write

DEMO = Path(__file__).resolve().parents[1]
OUT = DEMO / "output" / "build"


def main():
    start = time.monotonic()
    recipe, ctx, blocks = graph()
    problems = validate(recipe)
    if problems:
        raise RuntimeError("incomplete recipe:\n  " + "\n  ".join(problems))

    write(recipe, OUT / "torx_recipe.json", sections=ctx.sections_json())
    for name, definition in blocks.items():
        sections = definition.get("_sections")
        clean = {k: v for k, v in definition.items() if not k.startswith("_")}
        write(clean, OUT / "blocks" / ("%s.json" % name.replace(" ", "_")),
              sections=sections)

    receipt = {
        "recipe": str((OUT / "torx_recipe.json").relative_to(DEMO)),
        "seconds": round(time.monotonic() - start, 3),
        "blocks": len(blocks),
        "imports": len(recipe["imports"]),
        "import_order": [d["displayname"] for d in recipe["imports"]],
        "root_cbRefs": recipe["cbRefs"],
        "notebook_inputs": len(recipe["inputs"]),
        "root_body_entries": len(recipe["body"]),
        "func_nodes": count_nodes(recipe),
        "func_nodes_by_block": {d["displayname"]: count_nodes(d)
                                for d in recipe["imports"]},
        "bytes": (OUT / "torx_recipe.json").stat().st_size,
        "problems": problems,
        "scope": "offline recipe construction and structural validation only; "
                 "no nTop was launched",
    }
    # The repository harness writes its own output/build_receipt.json over this
    # demo when `scripts/build.py torx` runs, so the port receipt has its own name.
    (DEMO / "output" / "port_receipt.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
