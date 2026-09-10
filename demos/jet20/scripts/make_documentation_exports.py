"""Export every component through the Notebook API, with audited cache reuse."""
from pathlib import Path
import sys,json,hashlib,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_jet import build
from native_graph import literal,real
g=build();recipe=g.recipe(g.body)
outdir=ROOT/'output/exports/P3d';edir=ROOT/'output/build/documentation_exports';outdir.mkdir(parents=True,exist_ok=True);edir.mkdir(parents=True,exist_ok=True)
def hashes(rec):
    by={b['id']:b for b in rec['body']};memo={}
    def walk(x):
        if isinstance(x,list):return [walk(v) for v in x]
        if not isinstance(x,dict):return x
        if 'ref' in x:return {'source':vh(x['ref']['id']),'props':x.get('props',[])}
        if 'value' in x:return {'type':x['type'],'value':x['value']}
        return {k:walk(v) for k,v in x.items() if k not in ['id','name','type']}
    def vh(k):
        if k not in memo:memo[k]=hashlib.sha256(json.dumps(walk(by[k]['contents']),sort_keys=True).encode()).hexdigest()
        return memo[k]
    return {b['name']:vh(b['id']) for b in rec['body']}
old_path=ROOT/'output/archive/native_readback.json'
old=hashes(json.loads(old_path.read_text())) if old_path.is_file() else {}
current=hashes(recipe)
cache={'COMP Impeller':0,'TURB Rotor blisk':1,'TURB Nozzle guide vanes':2,'F01 Main fuel feed':3,'E03 Temperature harness':4,'NOZZLE Convergent duct':5}
manifest=[]
previous_path=ROOT/'output/build/documentation_manifest.json'
previous={r['name']:r for r in json.loads(previous_path.read_text())} if previous_path.is_file() else {}
for i,p in enumerate(g.parts):
    name=p['name'];slug=f'{i:02d}_'+re.sub(r'[^A-Za-z0-9]+','_',name)
    row=p|{'source_hash':current[name],'cached':False}
    if name in previous and Path(previous[name].get('mesh','')).is_file() and previous[name]['source_hash']==current[name] and (name!='TURB Nozzle guide vanes' or previous[name].get('mesh_method')=='implicit_then_sharpen'):
        row.update({k:v for k,v in previous[name].items() if k in ['mesh','mesh_scale_mm','numerical_island_filter_mm3','mesh_method','recipe','export_provenance']})
        row.update(cached=True,cache_revision='source-identical',cached_mesh_sha256=hashlib.sha256(Path(row['mesh']).read_bytes()).hexdigest())
    elif name in cache and name!='TURB Nozzle guide vanes' and old.get(name)==current[name] and (ROOT/'output/results'/f'sharp_component_{cache[name]:02d}.stl').is_file():
        row.update(mesh=str(ROOT/'output/results'/f'sharp_component_{cache[name]:02d}.stl'),cached=True,mesh_scale_mm=None)
    else:
        ref={'ref':{'id':p['id']},'props':[]};sub=g.closure([p['id']])
        scale=.35
        if name.startswith('FAST '):scale=.2
        elif name.startswith(('F01','F02','F03','P01','FUEL Manifold','FUEL Injector')):scale=.12
        elif 'gasket' in name.lower():scale=.12
        elif name=='TURB Nozzle guide vanes':scale=.2
        elif name.startswith('E0'):scale=.4
        if name in ['SHAFT Bearing tunnel','BEARING Front retainer']:scale=.12
        elif name=='CASE Front barrel':scale=.2
        if name=='TURB Nozzle guide vanes':
            # R2: the AT variants retained excess surface handles on this field.
            # Standard implicit meshing, then Sharpen, reproduced its 33 holes.
            mesh=g.node('sharpen',g.node('mesh',ref,real(scale)),ref,literal('integer',{'val':1}),literal('mesh_sharpen_enum',{'enum':0}))
            row['mesh_method']='implicit_then_sharpen'
        else:mesh=g.sharp_mesh(ref,scale)
        cleanup=None
        if name.startswith('FAST ') or name=='NOZZLE Convergent duct':
            # Joint probe measured 12 full assemblies plus islands <=0.02331 mm3.
            cleanup=.05 if name.startswith('FAST ') else .001
            threshold=literal('real',{'isFinite':True,'units':{'length':3},'val':cleanup*1e-9})
            mesh=g.node('merge_meshes',g.node('filter_meshes',g.node('split_mesh',mesh),threshold))
        path=outdir/(slug+'.stl');export=g.node('export',literal('file_path',{'val':str(path)}),mesh,literal('unit_length_enum',{'id':'mm'}))
        sub.append({'contents':export,'id':g.uid(),'name':'Documentation export','type':'mesh_file_data','variable':True})
        rp=edir/(slug+'.json');rp.write_text(json.dumps(g.recipe(sub),indent=1))
        row.update(mesh=str(path),recipe=str(rp),mesh_scale_mm=scale,numerical_island_filter_mm3=cleanup)
    manifest.append(row)
(ROOT/'output/build/documentation_manifest.json').write_text(json.dumps(manifest,indent=2))
print('Documentation exports',len(manifest),'cached',sum(x['cached'] for x in manifest))
