"""Run only inside nTop's prototype Python Console."""
from pathlib import Path
import json,time,traceback
ROOT=Path(__file__).resolve().parents[1]

def save_json(name,data):
    p=ROOT/'output/evidence'/name;p.write_text(json.dumps(data,indent=2,default=str),encoding='utf-8')

def exports(notebook,filters=None):
    manifest=json.loads((ROOT/'output/evidence'/'export_manifest.json').read_text())
    history=[];start=time.time()
    for i,p in enumerate(manifest):
        if filters and not any(s.lower() in p['name'].lower() for s in filters):continue
        mesh=Path(p['mesh'])
        if mesh.exists() and mesh.stat().st_size>84:continue
        item={'name':p['name'],'index':i,'started':time.time(),'state':'running'}
        history.append(item);save_json('export_progress.json',{'elapsed':time.time()-start,'items':history})
        try:
            notebook.new_notebook()
            notebook.import_recipe(p['recipe'])
            item['seconds']=time.time()-item['started']
            item['bytes']=mesh.stat().st_size if mesh.exists() else 0
            item['state']='complete' if item['bytes']>84 else 'missing_mesh'
        except Exception:
            item['state']='error';item['error']=traceback.format_exc()
        save_json('export_progress.json',{'elapsed':time.time()-start,'items':history})
        with (ROOT/'output/evidence'/'export_history.jsonl').open('a') as fh:fh.write(json.dumps(item)+'\n')
    return history

def assemble(notebook):
    notebook.new_notebook();t=time.time()
    save_json('assembly_progress.json',{'state':'importing','started':t})
    notebook.import_recipe(str(ROOT/'output/evidence'/'engine_recipe.json'))
    notebook.save_notebook_as(str(ROOT/'output/evidence'/'I6_Astra_raw.ntop'))
    notebook.export_as_recipe(str(ROOT/'output/evidence'/'native_readback.json'))
    vals={}
    for v in notebook.list_variables():
        name=v['id']
        if name.startswith('CHECK') or name in ['Bore','Stroke','Cylinder pitch','Crank angle']:
            try:vals[name]=notebook.get_block_input(name,'Input')
            except Exception as e:vals[name]=str(e)
    save_json('native_checks.json',vals)
    out={'state':'complete','seconds':time.time()-t,'variables':len(notebook.list_variables())}
    save_json('assembly_progress.json',out);return out

def assemble_packed(notebook):
    """Reopen, read back and save the host-packaged native graph through the API."""
    t=time.time()
    notebook.open_notebook(str(ROOT/'output/evidence'/'I6_Astra_packed.ntop'))
    notebook.export_as_recipe(str(ROOT/'output/evidence'/'native_readback.json'))
    vals={}
    for v in notebook.list_variables():
        name=v['id']
        if name.startswith('CHECK') or name in ['Bore','Stroke','Cylinder pitch','Crank angle']:
            vals[name]=notebook.get_block_input(name,'Input')
    save_json('native_checks.json',vals)
    notebook.save_notebook_as(str(ROOT/'output/evidence'/'I6_Astra_raw.ntop'))
    result={'state':'complete','seconds':time.time()-t,'variables':len(notebook.list_variables())}
    save_json('packed_assembly_result.json',result)
    return result

def scalar_sweep(notebook):
    # Reuse exactly the same dependency closure as the engine, with no geometry.
    fn=ROOT/'output/evidence'/'kinematic_recipe.json';recipe=json.loads(fn.read_text())
    notebook.new_notebook();notebook.import_recipe(str(fn))
    rows=[]
    for angle in [0,30,90,180,270,360,470,615,720]:
        for attempt in range(6):
            current=notebook.get_block_input('Crank angle','Input')
            if abs(current-angle)<1e-9:break
            try:notebook.set_block_input('Crank angle','Input',float(angle))
            except RuntimeError:
                # This prototype can report a failed setter after changing the
                # value. Read it back before deciding whether to retry.
                if abs(notebook.get_block_input('Crank angle','Input')-angle)<1e-9:break
                if attempt==5:raise
            time.sleep(.25)
        assert abs(notebook.get_block_input('Crank angle','Input')-angle)<1e-9
        row={'angle_deg':angle}
        for b in recipe['body']:
            if b['name'].startswith('CHECK'):row[b['name']]=notebook.get_block_input(b['name'],'Input')
        rows.append(row);save_json('kinematic_readbacks.json',rows)
    return rows
