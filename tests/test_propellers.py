from pathlib import Path
import json,hashlib,sys
import pytest
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'demos/propellers'
sys.path[:0]=[str(D/'scripts'),str(ROOT/'scripts')]
from verify_recipe import verify
from saved_graph import extract
from replay import prepare
CASES=json.loads((D/'manifest.json').read_text())['cases']
@pytest.mark.parametrize('item',CASES,ids=[c['id'] for c in CASES])
def test_saved_graph_integrity_and_resources(item):
 p=D/item['recipe'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['recipe_sha256']
 r=json.loads(p.read_text());verify(r);assert len(r['body'])==item['variables']
 if item['group']!='assembly':
  assert any(v.get('contents',{}).get('func','').startswith('sweep_along_two_rails<') for v in r['body'])
  g=item['recorded_geometry'];assert g['components']==1 and g['watertight'] and g['winding_consistent']
  assert hashlib.sha256((D/item['image']).read_bytes()).hexdigest()==item['image_sha256']
  assert (D/item['measurements']).is_file() and (D/item['design']).is_file()
 if 'notebook' in item:
  p=D/item['notebook'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['notebook_sha256']
  assert extract(p,item['title'])==r
@pytest.mark.parametrize('item',CASES,ids=[c['id'] for c in CASES])
def test_all_cases_stage_with_local_output_paths(item):
 result=prepare(item['id']);r=json.loads(Path(result['recipe']).read_text())
 def walk(v):
  if isinstance(v,dict):
   for q in v.values():yield from walk(q)
  elif isinstance(v,list):
   for q in v:yield from walk(q)
  elif isinstance(v,str):yield v
 paths=[Path(s) for s in walk(r) if len(s)>2 and s[1]==':' and s[2] in '/\\']
 assert paths
 assert all(p.resolve().is_relative_to((D/'output').resolve()) for p in paths)
 script=Path(result['native_import_script']).read_text();assert 'new_notebook' not in script
 assert 'Use an empty task-owned notebook' in script

def test_half_turn_revision_replaces_periodic_folded_recipe():
 row=next(c for c in CASES if c['id']=='airfoil_10_folded_loop')
 assert row['half_twist_degrees']==180 and 'derived' in row['profile']
 r=json.loads((D/row['recipe']).read_text())
 sweeps=[v for v in r['body'] if v.get('contents',{}).get('func','').startswith('sweep_along_two_rails<')]
 assert len(sweeps)==2 and all('Folded Mobius half' in v['name'] for v in sweeps)
 assert row['recorded_geometry']['native_closed_curves']==0
