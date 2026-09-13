"""Stage the complete corner CSG graph for an empty nTop notebook."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
DEMO = ROOT / 'demos/kestrelsat-corner'
sys.path.insert(0, str(ROOT / 'scripts'))
from project import resolve
from verify_recipe import verify


def prepare(mesh=False):
    source = DEMO / ('inputs/mesh.recipe.json' if mesh else 'inputs/corner.recipe.json')
    recipe = json.loads(source.read_text(encoding='utf-8'))
    result = verify(recipe)
    def visit(value):
        if isinstance(value, dict):
            return {key: visit(item) for key, item in value.items()}
        if isinstance(value, list):
            return [visit(item) for item in value]
        return resolve(value) if isinstance(value, str) and value.startswith('repo://') else value
    out = DEMO / 'output' / ('mesh' if mesh else 'build')
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'recipe.json'
    target.write_text(json.dumps(visit(recipe), indent=2) + '\n', encoding='utf-8')
    working = out / 'Corner-working.ntop'
    stage = out / 'import_model.py'
    script = f'''from pathlib import Path
if notebook.list_variables() or any(notebook.list_blocks(s['id']) for s in notebook.list_sections()):
    raise RuntimeError('Use an empty task-owned notebook.')
if Path({str(working)!r}).exists():
    raise RuntimeError('Retain the previous working notebook before importing again.')
notebook.import_recipe({str(target)!r})
notebook.export_as_recipe({str(out / 'readback.json')!r})
notebook.save_notebook_as({str(working)!r})
'''
    stage.write_text(script, encoding='utf-8')
    result.update(recipe=str(target.relative_to(ROOT)), import_script=str(stage.relative_to(ROOT)),
                  scope='Offline saved-graph staging; native evaluation has not run')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh', action='store_true', help='Stage AT with Remesh, one Sharpen iteration, and STL export')
    print(json.dumps(prepare(parser.parse_args().mesh), indent=2))
