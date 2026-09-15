from pathlib import Path
import hashlib
import importlib.util
import json
import struct
import pytest
from project import ROOT
from organize_notebook import read_file, write_file
from prepare import walk
from collapse_saved_notebook import unpack

DEMO = ROOT / 'demos/civil-research-aircraft'

@pytest.mark.parametrize('model', ['civil-research-aircraft-rev-g.ntop', 'rev-h-aircraft-h.ntop', 'rev-g-c-fwd.ntop'])
def test_expanded_native_directory_roundtrips(model):
    source = DEMO / 'models' / model
    raw = source.read_bytes()
    header, chunks = read_file(source)
    assert len(chunks) == struct.unpack_from('<Q', raw, 8)[0]
    assert write_file(header, chunks) == raw
    manifest = json.loads((DEMO / 'manifest.json').read_text())
    row = next(r for r in manifest['models'] if r['file'] == 'models/' + model)
    assert sum(c.name == 'fn' for c in walk(chunks)) == row['function_chunks']

def test_bad_native_directory_offset_is_rejected(tmp_path):
    raw = bytearray((DEMO / 'models/rev-g-c-fwd.ntop').read_bytes())
    struct.pack_into('<Q', raw, 40, 1)
    bad = tmp_path / 'invalid-directory.ntop'
    bad.write_bytes(raw)
    with pytest.raises(AssertionError, match='directory offset mismatch'):
        read_file(bad)
    with pytest.raises(ValueError, match='table offset mismatch'):
        unpack(raw)

def test_working_copy_resolves_airfoils_and_preserves_source_and_functions(tmp_path):
    path = DEMO / 'scripts/prepare_models.py'
    spec = importlib.util.spec_from_file_location('civil_prepare_models', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    source = DEMO / 'models/civil-research-aircraft-rev-g.ntop'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    module.prepare_models(['models/' + source.name], output_dir=tmp_path)
    _, original = read_file(source)
    _, prepared = read_file(tmp_path / 'models' / source.name)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    original_functions = [c.payload for c in walk(original) if c.name == 'fn']
    assert original_functions == [c.payload for c in walk(prepared) if c.name == 'fn']
    input_paths = []
    def inspect(value):
        if isinstance(value, dict):
            if value.get('type') == 'file_path' and 'value' in value:
                input_paths.append(value['value']['val'])
            for v in value.values(): inspect(v)
        elif isinstance(value, list):
            for v in value: inspect(v)
        elif isinstance(value, str): assert 'repo://' not in value
    for chunk in walk(prepared):
        if chunk.typ.lower() == 'json': inspect(json.loads(chunk.payload))
    assert input_paths
    assert all(Path(p).is_file() and Path(p).is_relative_to(tmp_path / 'inputs') for p in input_paths)
    for path in (DEMO / 'inputs').iterdir():
        assert path.read_bytes() == (tmp_path / 'inputs' / path.name).read_bytes()
