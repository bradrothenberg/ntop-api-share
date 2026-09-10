"""Checkout-local paths and registered demo builds."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JOBS={
 'i6':(['make_engine_recipe.py','-engine'], 'output/_agent/engine_full.json'),
 'i6-astra':(['build_engine.py'], 'output/evidence/engine_recipe.json'),
 'jet20':(['cycle.py','verify.py','build_jet.py','make_documentation_exports.py'], 'output/build/jet20_recipe.json'),
 'fury':(['build_rc_native.py'], 'output/_agent/rc_native_recipe.json'),
 'b52':(['build_fuselage.py'], 'output/build/final_recipe.json'),
 'ddgx':(['build_ddgx.py'], 'output/build/ddgx.json'),
}
def prepare():
    (ROOT/'.local').mkdir(exist_ok=True)
    for demo in JOBS:
        base=ROOT/'demos'/demo
        for name in ['_agent','evidence','build','results','exports','validation','report_figures']:
            (base/'output'/name).mkdir(parents=True,exist_ok=True)
def resolve(value):
    if not value.startswith('repo://'):return value
    suffix=value[7:]
    if not suffix or ':' in suffix or '\\' in suffix or '..' in suffix.split('/'):
        raise ValueError('Invalid portable reference')
    target=(ROOT/suffix).resolve()
    if not target.is_relative_to(ROOT):raise ValueError('Path escaped checkout')
    return str(target)
