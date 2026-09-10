"""Copy a complete saved API recipe into a demo's generated output folder."""
import json
from pathlib import Path
from project import resolve
from verify_recipe import verify

def replay(demo: Path):
    source = demo / "inputs" / "recipe.json"
    recipe = json.loads(source.read_text(encoding="utf8"))
    verify(recipe)
    def visit(value):
        if isinstance(value, dict):
            return {key: visit(item) for key, item in value.items()}
        if isinstance(value, list):
            return [visit(item) for item in value]
        return resolve(value) if isinstance(value, str) and value.startswith("repo://") else value
    recipe = visit(recipe)
    target = demo / "output" / "build" / "recipe.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf8")
    return target
