"""Self-contained entry point inside the nTop Python Console."""
from pathlib import Path
import importlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
DEMOS=('i6','i6-astra','jet20','fury','b52','ddgx','f16','a12','fcat')
def check_api(notebook):
    required=('list_variables','list_available_blocks','import_recipe','export_as_recipe','get_block_input','save_notebook_as')
    missing=[n for n in required if not callable(getattr(notebook,n,None))]
    if missing:raise RuntimeError('Missing Notebook API methods: '+', '.join(missing))
    return {'compatible_surface':True,'note':'Re-measure semantics after a build change.'}
def use(demo):
    if demo not in DEMOS:raise ValueError('Unknown demo: '+demo)
    for name,module in list(sys.modules.items()):
        location=getattr(module,'__file__',None)
        if location:
            try:inside=Path(location).resolve().is_relative_to(ROOT/'demos')
            except (ValueError,OSError):inside=False
            if inside:sys.modules.pop(name,None)
    folder=ROOT/'demos'/demo/'scripts'
    demo_paths={str(ROOT/'demos'/d/'scripts') for d in DEMOS}
    sys.path[:]=[str(folder),str(ROOT/'harness')]+[p for p in sys.path if p not in demo_paths and p!=str(ROOT/'harness')]
    cached=sys.modules.get('agent')
    if cached is not None and Path(getattr(cached,'__file__','')).resolve()!=ROOT/'harness/agent.py':
        sys.modules.pop('agent',None)
    agent=importlib.import_module('agent');agent.OUT_DIR=str(ROOT/'demos'/demo/'output/_agent')
    return {'demo':demo,'scripts':str(folder),'agent':agent.__file__}
def hello(notebook):
    check_api(notebook)
    if notebook.list_variables():raise RuntimeError('Use an empty scratch notebook')
    out=ROOT/'.local/hello';out.mkdir(parents=True,exist_ok=True)
    notebook.import_recipe(str(ROOT/'examples/hello_recipe.json'))
    value=notebook.get_block_input('Harness sum','Input')
    if value!=5:raise AssertionError(f'Expected 5, got {value!r}')
    notebook.export_as_recipe(str(out/'readback.json'));notebook.save_notebook_as(str(out/'Hello.ntop'))
    return {'sum':value,'verified':True}
