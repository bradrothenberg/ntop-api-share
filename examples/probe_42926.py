"""Optional native probe. Call run(notebook) in an owned, empty scratch notebook."""
from pathlib import Path
import json
from uuid import uuid4
from ntop_api import check_api

ROOT = Path(__file__).resolve().parents[1]

def run(notebook):
    check_api(notebook, require_42926=True)
    if notebook.list_variables() or any(notebook.list_blocks(s['id']) for s in notebook.list_sections()):
        raise RuntimeError('Use an empty task-owned scratch notebook; this probe does not clear it')
    output = ROOT / '.local' / ('probe-42926-' + uuid4().hex)
    output.mkdir(parents=True)
    result = {'scope': 'New native value/unit probe only', 'checks': {}}
    try:
        for kind, value in [('real', 25.4), ('integer', 7), ('bool', True), ('text', 'API unit probe')]:
            block = notebook.add_block(f'core.var<{kind}>')['id']
            if kind == 'real':
                notebook.set_block_input(block, 'Input', value, 'mm')
            else:
                notebook.set_block_input(block, 'Input', value)
            actual = notebook.get_block_input(block, 'Input')
            units = notebook.get_block_input_units(block, 'Input')
            state = notebook.block_state(block)
            result['checks'][kind] = {'requested':value, 'requested_units':'mm' if kind=='real' else '',
                                     'value':actual, 'display_units':units, 'state':state}
            if kind == 'real':
                factors = {'mm':1.0, 'cm':10.0, 'm':1000.0, 'in':25.4, 'ft':304.8}
                if units not in factors:
                    raise RuntimeError(f'Calibrate unsupported display unit {units!r} before asserting a length')
                assert abs(actual * factors[units] - 25.4) < 1e-9
            else:
                assert type(actual) is type(value) and actual == value
            assert state['buildState'] == 'e_OK'
        notebook.export_as_recipe(str(output / 'readback.json'))
        notebook.save_notebook_as(str(output / 'Probe-working.ntop'))
        result['passed'] = True
    finally:
        (output / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result
