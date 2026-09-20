"""Input preparation must preserve the native template and reject ambiguity."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.agents/skills/ntop-doe-sweep/scripts/prepare_sweep.py'
spec = importlib.util.spec_from_file_location('prepare_sweep', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def template():
    return {'title': 'Fixture', 'inputs': [
        {'name': 'Radius', 'type': 'real', 'units': 'mm', 'value': 1.0},
        {'name': 'Count', 'type': 'integer', 'value': 2},
        {'name': 'Source', 'type': 'file_path', 'value': 'inputs/profile.csv'},
        {'name': 'Export_Path', 'type': 'file_path', 'value': './old/'},
        {'name': 'Origin', 'type': 'point', 'units': 'mm', 'value': [0, 0, 0]},
        {'name': 'Enabled', 'type': 'boolean', 'value': False},
        {'name': 'Mode', 'type': 'enum', 'value': [0]},
    ]}


def values(task):
    return {entry['name']: entry['value'] for entry in task['inputs']}


def test_factorial_preserves_imports_units_and_source(template):
    before = copy.deepcopy(template)
    tasks = module.prepare(template, ['Radius=1,2', 'Count=3,4'], constants=['Export_Path=./'])
    assert [(values(t)['Radius'], values(t)['Count']) for t in tasks] == [(1., 3), (1., 4), (2., 3), (2., 4)]
    assert all(values(t)['Source'] == 'inputs/profile.csv' for t in tasks)
    assert all(values(t)['Export_Path'] == './' for t in tasks)
    assert all(t['inputs'][0]['units'] == 'mm' for t in tasks)
    assert template == before


def test_zip_vectors_booleans_and_enums(template):
    tasks = module.prepare(template, ['Radius=1,2', 'Origin=0,0,0;1,2,3', 'Mode=[0];[1]'], constants=['Enabled=true'], zipped=True)
    assert len(tasks) == 2
    assert values(tasks[1])['Origin'] == [1., 2., 3.]
    assert values(tasks[1])['Mode'] == [1]
    assert values(tasks[1])['Enabled'] is True


@pytest.mark.parametrize('kwargs', [
    {'sweeps': ['Missing=1']},
    {'sweeps': ['Radius=1'], 'constants': ['Radius=2']},
    {'sweeps': ['Enabled=maybe']},
    {'sweeps': ['Radius=nan']},
    {'sweeps': ['Origin=1,2']},
    {'sweeps': ['Mode=true']},
    {'sweeps': ['Radius=1,2', 'Count=1,2,3'], 'zipped': True},
    {'linspaces': ['Count=0:1:3']},
    {'sweeps': ['Radius=1,2', 'Count=1,2'], 'max_tasks': 3},
])
def test_reject_invalid_or_ambiguous_input(template, kwargs):
    with pytest.raises(ValueError):
        module.prepare(template, **kwargs)


def test_linspace_and_constant_case(template):
    tasks = module.prepare(template, linspaces=['Radius=0:1:3'])
    assert [values(t)['Radius'] for t in tasks] == [0., .5, 1.]
    assert module.prepare(template) == [template]
    assert module.prepare(template, zipped=True) == [template]


def test_cli_preserves_existing_output(tmp_path, template):
    source = tmp_path / 'template.json'
    target = tmp_path / 'inputs.ndjson'
    source.write_text(json.dumps(template))
    command = [sys.executable, str(SCRIPT), '--template', str(source), '--out', str(target), '--sweep', 'Radius=2,3']
    first = subprocess.run(command, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    original = target.read_bytes()
    assert len(target.read_text().splitlines()) == 2
    second = subprocess.run(command, capture_output=True, text=True)
    assert second.returncode != 0
    assert target.read_bytes() == original
