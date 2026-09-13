"""Stage one saved propeller graph; no geometry evaluation occurs on the host."""
from pathlib import Path
import argparse
import json
import sys
ROOT=Path(__file__).resolve().parents[3]
DEMO=ROOT/'demos/propellers'
sys.path.insert(0,str(ROOT/'scripts'))
from project import resolve
from verify_recipe import verify


def prepare(case='assembly'):
    manifest=json.loads((DEMO/'manifest.json').read_text())
    item=next((row for row in manifest['cases'] if row['id']==case),None)
    if item is None:raise ValueError('Unknown case: '+case)
    recipe=json.loads((DEMO/item['recipe']).read_text())
    verify(recipe)
    def visit(v):
        if isinstance(v,dict):return {k:visit(x) for k,x in v.items()}
        if isinstance(v,list):return [visit(x) for x in v]
        if isinstance(v,str) and v.startswith('repo://'):
            resolved=resolve(v);Path(resolved).parent.mkdir(parents=True,exist_ok=True);return resolved
        return v
    out=DEMO/'output'/case
    out.mkdir(parents=True,exist_ok=True)
    target=out/'recipe.json';target.write_text(json.dumps(visit(recipe),indent=2),encoding='utf-8')
    notebook=out/'Model-working.ntop'
    stage=out/'import.py'
    script=f"""from pathlib import Path
if notebook.list_variables() or any(notebook.list_blocks(s['id']) for s in notebook.list_sections()):
    raise RuntimeError('Use an empty task-owned notebook. This import does not discard existing work.')
if Path({str(notebook)!r}).exists():
    raise RuntimeError('Retain the previous working notebook before running this import again')
notebook.import_recipe({str(target)!r})
notebook.export_as_recipe({str(out/'readback.json')!r})
notebook.save_notebook_as({str(notebook)!r})
"""
    stage.write_text(script,encoding='utf-8')
    if case=='assembly':
        default=DEMO/'output/build/recipe.json';default.parent.mkdir(parents=True,exist_ok=True);default.write_bytes(target.read_bytes())
    return {'case':case,'recipe':str(target),'native_import_script':str(stage),'scope':'Offline staging, not native execution'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',default='assembly')
    args=parser.parse_args();print(json.dumps(prepare(args.case),indent=2))

if __name__=='__main__':main()
