from pathlib import Path
import importlib.util,json,sys
import pytest
from project import ROOT,JOBS,resolve
from verify_recipe import verify
from organize_notebook import read_file,write_file
from prepare import relocate,walk
from collapse_saved_notebook import collapse

MODELS=sorted((ROOT/'demos').glob('*/models/*.ntop'))

@pytest.mark.parametrize('model',MODELS,ids=lambda p:p.name)
def test_native_container_and_collapse_preserve_geometry(model,tmp_path):
    header,chunks=read_file(model)
    assert write_file(header[:],chunks)==model.read_bytes()
    out=tmp_path/model.name
    original=model.read_bytes();collapse(model,out)
    _,changed=read_file(out)
    before={c.name:c.serialize() for c in chunks if c.name not in {'open','sections'}}
    after={c.name:c.serialize() for c in changed if c.name not in {'open','sections'}}
    assert before==after
    again=tmp_path/('again-'+model.name);collapse(out,again)
    assert out.read_bytes()==again.read_bytes()
    assert model.read_bytes()==original

def test_prepare_preserves_source_and_resolves_into_checkout(tmp_path):
    source=ROOT/'demos/i6/models/I6_Engine.ntop';before=source.read_bytes()
    target=tmp_path/'recipient copy.ntop';count=relocate(source,target)
    assert count>0 and source.read_bytes()==before
    _,chunks=read_file(target)
    def paths(x):
        if isinstance(x,dict):
            if x.get('type')=='file_path' and 'value' in x:yield x['value']['val']
            for v in x.values():yield from paths(v)
        elif isinstance(x,list):
            for v in x:yield from paths(v)
    values=[v for c in walk(chunks) if c.typ.lower()=='json' for v in paths(json.loads(c.payload))]
    assert values and all(Path(v).is_relative_to(ROOT) for v in values)
    with pytest.raises(ValueError):relocate(source,source)

@pytest.mark.parametrize('bad',['repo://../outside','repo:///outside','repo://C:/outside','repo://demos/../../outside','repo://demos\\outside'])
def test_reference_cannot_escape_checkout(bad):
    with pytest.raises(ValueError):resolve(bad)

def test_recipe_rejects_broken_references():
    with pytest.raises(ValueError,match='Unresolved'):
        verify({'body':[{'id':'a','name':'a','contents':{'ref':{'id':'missing'}}}]})

def test_recipe_rejects_duplicate_names():
    with pytest.raises(ValueError,match='Duplicate variable names'):
        verify({'body':[{'id':'a','name':'same'},{'id':'b','name':'same'}]})

@pytest.mark.parametrize('demo',JOBS)
def test_registered_build_produced_closed_recipe(demo):
    p=ROOT/'demos'/demo/JOBS[demo][1]
    if not p.exists():pytest.skip('Run scripts/smoke.py first to verify generated recipes')
    result=verify(json.loads(p.read_text()))
    assert result['references_resolve'] and result['variables']>0

def test_selecting_demo_does_not_reuse_previous_graph_module():
    import ntop_api
    original_path=sys.path[:]
    try:
        ntop_api.use('i6-astra');import native_graph
        astra=Path(native_graph.__file__).resolve()
        ntop_api.use('jet20');import native_graph as jet_graph
        jet=Path(jet_graph.__file__).resolve()
        assert astra!=jet
        assert astra.is_relative_to(ROOT/'demos/i6-astra')
        assert jet.is_relative_to(ROOT/'demos/jet20')
    finally:sys.path[:]=original_path

def test_upstream_b52_source_matches_recorded_hash():
    import hashlib
    p=ROOT/'demos/b52/upstream/B-52F-002-027e.ac'
    assert hashlib.sha256(p.read_bytes()).hexdigest()=='61b082627d340a65dd57d25dfbb77a130c07712757b04dfd2ac8304959fa1bfb'

def test_native_jet_screenshot_hashes():
    import hashlib
    base=ROOT/'demos/jet20/screenshots';record=json.loads((base/'capture_manifest.json').read_text())
    for image in record['images']:
        assert hashlib.sha256((base/image['image']).read_bytes()).hexdigest()==image['sha256']
        assert hashlib.sha256((base/image['native_file']).read_bytes()).hexdigest()==image['native_sha256']


def test_selecting_demo_replaces_a_foreign_cached_agent(tmp_path):
    import ntop_api,types
    old_module=sys.modules.get('agent');old_path=sys.path[:]
    foreign=types.ModuleType('agent');foreign.__file__=str(tmp_path/'agent.py')
    sys.modules['agent']=foreign
    try:
        ntop_api.use('i6')
        assert Path(sys.modules['agent'].__file__).resolve()==ROOT/'harness/agent.py'
    finally:
        sys.path[:]=old_path
        if old_module is None:sys.modules.pop('agent',None)
        else:sys.modules['agent']=old_module
