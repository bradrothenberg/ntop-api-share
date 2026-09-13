"""Check the portable corner example without nTop or geometry evaluation."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

DEMO = Path(__file__).resolve().parents[1]
ROOT = DEMO.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from organize_notebook import read_file, write_file
from verify_recipe import verify as verify_recipe

REQUIRED = ['models/Corner_block.ntop', 'inputs/corner.recipe.json',
            'inputs/corner.csg.json', 'inputs/Corner_block_source.step', 'inputs/mesh.recipe.json',
            'evidence/validation.json', 'evidence/geometry-binding.json',
            'evidence/source-extraction.json', 'evidence/native-portability.json',
            'scripts/check_example.py']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def exact_numbers(value):
    """Equal decoded JSON numbers match; adjacent floats remain distinct."""
    if isinstance(value, bool):
        return ['boolean', value]
    if isinstance(value, int):
        return ['number', str(value), '1']
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('Nonfinite JSON number')
        a, b = value.as_integer_ratio()
        return ['number', str(a), str(b)]
    if isinstance(value, dict):
        return {k: exact_numbers(v) for k, v in value.items()}
    if isinstance(value, list):
        return [exact_numbers(v) for v in value]
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def owned_paths(doc):
    blocks = {b['id']: b for b in doc['code']}
    roots = {w['instanceId'] for w in blocks[100]['inputs']}
    found = {'100_'}
    def visit(index, path, top=False, ancestors=()):
        assert index not in ancestors, 'Cycle in owned UI subtree'
        found.add(path)
        if index in roots and not top:
            return
        for slot, wire in enumerate(blocks[index]['inputs']):
            if wire['instanceId'] >= 0:
                visit(wire['instanceId'], path + '_' + str(slot),
                      ancestors=ancestors + (index,))
    for slot, wire in enumerate(blocks[100]['inputs']):
        visit(wire['instanceId'], '100_' + str(slot), top=True)
    return found


def graph_check(chunks, recipe):
    main = next(c for c in chunks if c.name == 'main')
    doc = json.loads(main.find('fn', 'json').payload)
    leaves = json.loads(main.find('leaves').find('index', 'json').payload)
    literals = {int(v['id']): {'type': v['type'], 'value': v['value']} for v in leaves}
    blocks = {b['id']: b for b in doc['code']}
    variables = {i: b for i, b in blocks.items() if b['func'].startswith('core.var<')}
    assert not doc['def']['inputs'] and not recipe.get('inputs'), 'This recorded part has no exposed inputs'
    assert not doc.get('dependencies') and not doc.get('externalDependencies')
    assert not recipe.get('imports') and not recipe.get('cbRefs')
    assert not [v for v in leaves if v['type'] == 'file_path'], 'Unexpected external file dependency'
    assert [c.name for c in chunks if c.typ == 'ntopfn'] == ['main']
    assert len({b['name'] for b in variables.values()}) == len(variables)
    def native_edge(wire):
        assert wire.get('modelInputIdx', -1) == -1
        index = wire['instanceId']
        value = None if index < 0 else ({'ref': variables[index]['name']}
                  if index in variables else native_node(index))
        return {'base': value, 'props': wire['propchain']} if wire.get('propchain') else value
    def native_node(index):
        if index in literals:
            return literals[index]
        node = blocks[index]
        return {'func': node['func'], 'type': node['type'],
                'inputs': [native_edge(w) for w in node['inputs']]}
    names = {v['id']: v['name'] for v in recipe['body']}
    def canon(value):
        if value is None:
            return None
        if 'ref' in value:
            base = {'ref': names[value['ref']['id']]}
            return {'base': base, 'props': value['props']} if value.get('props') else base
        if 'func' in value:
            return {'func': value['func'], 'type': value['type'],
                    'inputs': [canon(v) for v in value['inputs']]}
        assert set(value) == {'type', 'value'}, 'Unrecognized recipe literal'
        return value
    expected = {v['name']: canon(v['contents']) for v in recipe['body']}
    actual = {v['name']: native_edge(v['inputs'][0]) for v in variables.values()}
    assert set(expected) == set(actual), 'Named variable set differs'
    assert exact_numbers(expected) == exact_numbers(actual), 'Native and recipe graphs differ'
    native_output = blocks[doc['output']]
    assert native_output['id'] in variables
    assert native_output['name'] == names[recipe['output']['id']]
    assert native_output['type'] == doc['def']['output']['type'] == 'implicit'
    assert doc['def']['function'] == recipe['name'], 'Unexpected custom function identity'
    memo = {}
    def variable(name):
        if name not in memo:
            memo[name] = expression(actual[name])
        return memo[name]
    def expression(value):
        if value is None:
            return digest(None)
        if 'ref' in value:
            return variable(value['ref'])
        if 'base' in value:
            return digest(['property', expression(value['base']), value['props']])
        if 'func' in value:
            return digest(['function', value['func'], value['type'],
                           [expression(v) for v in value['inputs']]])
        return digest(['literal', value['type'], exact_numbers(value['value'])])
    signature = variable(native_output['name'])
    return dict(variables=len(expected), matched=len(expected), extra_native_names=[],
                output_name=native_output['name'], output_type='implicit',
                output_expression_sha256=signature, input_count=0,
                external_geometry_dependencies=0,
                complete_named_expressions_and_output_equal=True,
                numeric_comparison='Exact decoded numeric ratios; no geometric or numeric tolerance')


def mesh_recipe_check(expected_body_signature):
    recipe = json.loads((DEMO / 'inputs/mesh.recipe.json').read_text())
    verify_recipe(recipe)
    assert not recipe.get('inputs') and not recipe.get('imports')
    variables = {v['id']: v for v in recipe['body']}
    memo = {}
    def variable(name):
        if name not in memo:
            memo[name] = expression(variables[name]['contents'])
        return memo[name]
    def expression(value):
        if value is None:
            return digest(None)
        if 'ref' in value:
            result = variable(value['ref']['id'])
        elif 'func' in value:
            result = digest(['function', value['func'], value['type'],
                             [expression(v) for v in value['inputs']]])
        else:
            assert set(value) == {'type', 'value'}
            result = digest(['literal', value['type'], exact_numbers(value['value'])])
        return digest(['property', result, value['props']]) if value.get('props') else result
    body_signature = variable('RESULT Body')
    assert body_signature == expected_body_signature, 'Meshing recipe uses different geometry'
    nodes = []
    paths = []
    def collect(value):
        if isinstance(value, dict):
            if 'func' in value:
                nodes.append(value)
            if value.get('type') == 'file_path' and 'value' in value:
                paths.append(value['value']['val'])
            for item in value.values():
                collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)
    collect(recipe['body'])
    path = 'repo://demos/kestrelsat-corner/output/native.stl'
    assert paths == [path], 'Unexpected native export path or file dependency'
    def one(prefix):
        matches = [n for n in nodes if n['func'].startswith(prefix + '<')]
        assert len(matches) == 1
        return matches[0]
    at = one('mesh_by_adaptive_tets')
    sharpen = one('sharpen_mesh')
    export = one('export_mesh')
    assert expression(at['inputs'][0]) == body_signature
    assert at['inputs'][1]['type'] == 'real'
    assert at['inputs'][1]['value']['units'] == {'length': 1}
    assert exact_numbers(at['inputs'][1]['value']['val']) == exact_numbers(.00005)
    assert at['inputs'][2] == {'type': 'bool', 'value': {'val': True}}
    assert at['inputs'][2]['value']['val'] is True
    assert expression(sharpen['inputs'][0]) == expression(at)
    assert expression(sharpen['inputs'][1]) == body_signature
    assert sharpen['inputs'][2] == {'type': 'integer', 'value': {'val': 1}}
    assert sharpen['inputs'][3] == {'type': 'mesh_sharpen_enum', 'value': {'enum': 0}}
    assert expression(export['inputs'][1]) == expression(sharpen)
    assert export['inputs'][2] == {'type': 'unit_length_enum', 'value': {'id': 'mm'}}
    assert variable(recipe['output']['id']) == expression(export)
    return dict(body_expression_sha256=body_signature, matches_native_output=True,
                only_file_path=path, at_tolerance_mm=.05, remesh=True,
                sharpen_iterations=1, export_units='mm', pipeline_connections_verified=True,
                native_execution_performed=False)


def check(no_manifest=False):
    model = DEMO / 'models/Corner_block.ntop'
    recipe_path = DEMO / 'inputs/corner.recipe.json'
    raw = model.read_bytes()
    header, chunks = read_file(model)
    assert write_file(header[:], chunks) == raw, 'Native container roundtrip differs'
    recipe = json.loads(recipe_path.read_text())
    offline = verify_recipe(recipe)
    graph = graph_check(chunks, recipe)
    mesh = mesh_recipe_check(graph['output_expression_sha256'])
    doc = json.loads(next(c for c in chunks if c.name == 'main').find('fn', 'json').payload)
    states = json.loads(next(c for c in chunks if c.name == 'open').payload)
    sections = json.loads(next(c for c in chunks if c.name == 'sections').payload)
    keys = [(r['modelIndex'], r['relativePath']) for r in states]
    assert len(keys) == len(set(keys)), 'Duplicate saved UI rows'
    saved = {r['relativePath']: r for r in states if r['modelIndex'] == -1}
    assert owned_paths(doc).issubset(saved), 'Missing authored UI rows'
    assert all(r['collapsed'] is True for r in states if r['relativePath'] != '100_')
    assert all(r['collapse'] is True for r in sections['decorations'])
    assert sections['poles'][0] == 0
    assert sections['poles'][-1] == len(next(b for b in doc['code'] if b['id'] == 100)['inputs'])
    assert len(sections['poles']) == len(sections['decorations']) + 1
    manifest_checks = []
    if not no_manifest:
        manifest = json.loads((DEMO / 'evidence/manifest.json').read_text())
        rows = manifest['files']
        listed = {row['path'] for row in rows}
        assert len(listed) == len(rows), 'Duplicate manifest entries'
        assert set(REQUIRED).issubset(listed), 'Manifest does not cover required evidence'
        for row in rows:
            path = (DEMO / row['path']).resolve()
            assert path.is_relative_to(DEMO.resolve()) and path.is_file(), 'Invalid manifest path'
            assert sha(path) == row['sha256'], 'Changed manifest file: ' + row['path']
            manifest_checks.append(row['path'])
        validation = json.loads((DEMO / 'evidence/validation.json').read_text())
        binding = json.loads((DEMO / 'evidence/geometry-binding.json').read_text())
        extraction = json.loads((DEMO / 'evidence/source-extraction.json').read_text())
        assert validation['native_model_sha256'] == sha(model)
        assert validation['extracted_step_sha256'] == sha(DEMO / 'inputs/Corner_block_source.step')
        assert extraction['extracted_step_sha256'] == validation['extracted_step_sha256']
        assert binding['contract']['part_default_expression_sha256'] == graph['output_expression_sha256']
        assert binding['contract']['mesh_sha256'] == validation['native_mesh_sha256']
        assert validation['volume_iou'] >= .995 and validation['passed_volume_target'] is True
    return dict(passed=True, native_model_sha256=sha(model), recipe_sha256=sha(recipe_path),
                native_container_roundtrip_exact=True, offline_recipe=offline, graph=graph,
                mesh_recipe=mesh,
                authored_rows_collapsed=len(owned_paths(doc))-1,
                sections_collapsed=len(sections['decorations']),
                manifest_checked=not no_manifest, manifest_files_checked=len(manifest_checks),
                scope='Offline saved-graph, presentation, dependency and file-identity checks. Recorded geometry evidence is referenced, not rerun.',
                native_execution_performed=False, geometry_evaluation_performed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-manifest', action='store_true',
                        help='Initial native/recipe audit only; does not verify the release manifest.')
    args = parser.parse_args()
    print(json.dumps(check(args.no_manifest), indent=2))


if __name__ == '__main__':
    main()
