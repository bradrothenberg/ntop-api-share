"""Generate and verify a small native input-driven custom-block assembly.

Standard library only. The measured transport is nTopCL extended-recipe
conversion, not a live Notebook API import. Each native command has a 45 s limit.
Use --offline for source-only recipe checks. Pass an empty --out directory.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,os,shutil,subprocess,time,uuid
from pathlib import Path


def mm(x):return dict(type='real',value=dict(isFinite=True,units={'length':1},val=x/1000))
def scalar(x):return dict(type='real',value=dict(isFinite=True,units={},val=x))
def point(x,y,z):return dict(type='point',value=[dict(isFinite=True,val=a/1000) for a in (x,y,z)])
def vector(x,y,z,length=False):return dict(type='vector',value=dict(units={'length':1} if length else {},value=[dict(isFinite=True,val=a/(1000 if length else 1)) for a in (x,y,z)]))
def ref(name,prop=None):return dict(ref={'id':name},props=[] if prop is None else [prop])

class Recipe:
    def __init__(self,title):self.title=title;self.body=[];self.serial=0
    def node(self,func,typ,inputs,name=None):
        self.serial+=1;return dict(func=func,type=typ,inputs=inputs,id=f'node_{self.serial:04d}',name=name or func.split('<')[0])
    def hold(self,name,typ,value):
        assert all(row['id']!=name for row in self.body)
        self.body.append(dict(id=name,name=name,type=typ,variable=True,contents=value));return ref(name)
    def boolean(self,operation,name,bodies,base=None):
        listing=self.node('core.list<implicit>','list<implicit>',bodies)
        common=[dict(type='blend_enum',value={'enum':0}),mm(0)]
        if operation=='subtract':inputs=common+[base,listing];types='blend_enum,real_field,implicit,list<implicit>'
        else:inputs=common+[listing];types='blend_enum,real_field,list<implicit>'
        return self.hold(name,'implicit',self.node(f'boolean_{operation}<{types}>[5.44.0]','implicit',inputs))
    def document(self,output,imports=()):
        return dict(name='user_func_'+str(uuid.uuid5(uuid.NAMESPACE_URL,'ntop-custom-assembly/example/'+self.title)).replace('-','_'),
            displayname=self.title,description='Generic CSG skill example. Millimetre design dimensions are explicitly encoded in SI. No source CAD is imported.',version=[1,0,0],
            inputs=[dict(name='Width',type='real',dimension={'length':1},description='Overall X span. Hole diameter2 mm and plate thickness2 mm stay fixed.',contents=mm(10))],
            imports=list(imports),cbRefs=list(range(len(imports))),namespaces=[],body=self.body,output={'id':output['ref']['id']})

def part_recipe():
    r=Recipe('Example drilled chamfered part');width=r.hold('Width','real',{'input':0,'props':[]})
    upper=r.hold('Stock upper corner','point',r.node('point<real,real,real>','point',[width,mm(8),mm(2)]))
    stock=r.hold('Rectangular stock','box',r.node('box_from_corners<point,point>','box',[point(0,0,0),upper]))
    planes=[]
    for name,p,n in [('Left front chamfer',point(.5,0,0),vector(-1,-1,0)),
                     ('Right front chamfer',r.node('point<real,real,real>','point',[r.node('subtract<real,real>','real',[width,mm(.5)]),mm(0),mm(0)]),vector(1,-1,0))]:
        pl=r.hold(name+' plane','plane',r.node('plane_from_normal<point,vector>[1.1.0]','plane',[p,n]))
        planes.append(r.hold(name,'implicit',r.node('add<real_field,real_field>','real_field',[ref(pl['ref']['id'],'scalar field'),mm(0)])))
    chamfered=r.boolean('intersect','Continuous chamfered stock',[stock]+planes)
    drill=r.hold('Fixed2 mm bore','cylinder',r.node('cylinder<point,point,real>','cylinder',[point(3,4,-1),point(3,4,3),mm(1)]))
    body=r.boolean('subtract','Body',[drill],base=chamfered)
    return r.document(body)

def assembly_recipe(part):
    r=Recipe('Example two-instance assembly');width=r.hold('Width','real',{'input':0,'props':[]})
    function=part['name']+'<real>['+'.'.join(map(str,part['version']))+']'
    a=r.hold('Part A','implicit',r.node(function,'implicit',[width],'Custom part instance A'))
    raw_b=r.hold('Part B family','implicit',r.node(function,'implicit',[width],'Custom part instance B'))
    b=r.hold('Part B','implicit',r.node('translate<spatial3d,vector>','implicit',[raw_b,vector(0,12,0,length=True)]))
    body=r.boolean('union','Assembly body',[a,b])
    return r.document(body,[part])

def validation_recipe(assembly):
    r=Recipe('Example assembly field validation');r.body=copy.deepcopy(assembly['body']);r.serial=1000;checks=[];expected=[]
    def add(label,body,coordinate,value10,value14=None):
        p=point(*coordinate) if not isinstance(coordinate,dict) else coordinate
        checks.append(r.hold(label,'real',r.node('evaluate_field<real_field,point>','real',[ref(body,'scalar field'),p])))
        expected.append(dict(name=label,expected_mm={'10':value10,'14':value10 if value14 is None else value14}))
    def at_width(dx,y,z):
        x=ref('Width') if dx==0 else r.node('add<real,real>','real',[ref('Width'),mm(dx)])
        return r.node('point<real,real,real>','point',[x,mm(y),mm(z)])
    for body,dy in [('Part A',0),('Part B',12)]:
        for dx,expected_value in [(-.1,-.1),(0,0),(.1,.1)]:add(f'{body} far span {dx:+g}',body,at_width(dx,4+dy,1),expected_value)
        add(body+' left span',body,[0,4+dy,1],0)
        add(body+' fixed X12 station',body,[12,4+dy,1],2,-1)
        for x,v in [(1.9,-.1),(2,0),(2.1,.1),(3,1),(3.9,.1),(4,0),(4.1,-.1)]:add(f'{body} bore X{x:g}',body,[x,4+dy,1],v)
        for z,v in [(-.1,.1),(0,0),(.1,-.1),(1.9,-.1),(2,0),(2.1,.1)]:add(f'{body} thickness Z{z:g}',body,[7,4+dy,z],v)
        add(body+' left chamfer plane',body,[.25,.25+dy,1],0)
        add(body+' right chamfer plane',body,at_width(-.25,.25+dy,1),0)
    output=r.hold('CHECK Values','list<real>',r.node('core.list<real>','list<real>',checks))
    return r.document(output,assembly['imports']),expected

def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def check_document(document):
    variables={row['id']:row for row in document['body']}
    assert len(variables)==len(document['body'])
    assert document['output']['id'] in variables
    assert document['cbRefs']==list(range(len(document['imports'])))
    assert len(document['inputs'])==1
    spec=document['inputs'][0]
    assert spec['name']=='Width' and spec['type']=='real' and spec['dimension']=={'length':1}
    assert spec['contents']==mm(10)
    imported={item['name']+'<real>['+'.'.join(map(str,item['version']))+']' for item in document['imports']}
    identifiers=[];references=set()
    def walk(value):
        if isinstance(value,dict):
            if 'ref' in value:
                assert value['ref']['id'] in variables
                references.add(value['ref']['id'])
            if 'input' in value:assert value['input']==0
            if 'func' in value:
                identifiers.append(value['id'])
                if value['func'].startswith('user_func_'):assert value['func'] in imported
            for child in value.values():walk(child)
        elif isinstance(value,list):
            for child in value:walk(child)
    walk(document['body'])
    assert len(identifiers)==len(set(identifiers))
    for imported_document in document['imports']:check_document(imported_document)
    return dict(root_variables=len(variables),function_nodes=len(identifiers),reference_owners=len(references),
        imported_definitions=len(document['imports']),output_type=variables[document['output']['id']]['type'])


def emit_offline(out):
    part=part_recipe();assembly=assembly_recipe(part);validation,expected=validation_recipe(assembly)
    counts={name:check_document(doc) for name,doc in [('part',part),('assembly',assembly),('validation',validation)]}
    assert counts['part']['output_type']==counts['assembly']['output_type']=='implicit'
    assert counts['validation']['output_type']=='list<real>' and len(expected)==40
    calls=[row for row in assembly['body'] if row['contents'].get('func','').startswith(part['name'])]
    assert len(calls)==2
    for name,doc in [('part.recipe.json',part),('assembly.authored.recipe.json',assembly),('validation.authored.recipe.json',validation),('field_expectations.json',expected)]:save(out/name,doc)
    for width in [10,14]:save(out/f'width_{width}.inputs.json',{'inputs':[{'name':'Width','type':'real','value':width/1000,'units':'m'}]})
    result=dict(offline_checks_passed=True,native_execution=False,native_custom_identity_verified=False,
        description='Complete generic recipes and reference closures only. Native save/readback is still required before trusting custom identities.',
        counts=counts,width_cases_mm=[10,14],checks_per_case=len(expected),native_checks_planned=80,
        files={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    save(out/'offline_verification.json',result);print(json.dumps(result),flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ntopcl',type=Path,default=os.environ.get('NTOPCL') or shutil.which('ntopcl'))
    ap.add_argument('--out',type=Path,required=True,help='New or empty output directory; generated evidence can contain local executable paths.')
    ap.add_argument('--offline',action='store_true',help='Write and audit recipes without nTop. Custom identities remain authored, not native-verified.')
    args=ap.parse_args()
    out=args.out.resolve()
    if out.exists() and any(out.iterdir()):ap.error('Use a new or empty --out directory to preserve prior evidence.')
    out.mkdir(parents=True,exist_ok=True)
    if args.offline:
        emit_offline(out)
        return
    if args.ntopcl is None or not args.ntopcl.is_file():ap.error('Pass --ntopcl with the installed nTopCL executable path, or use --offline.')
    exe=args.ntopcl.resolve();runs=[];started=time.perf_counter()
    def run(label,arguments):
        command=[str(exe),*map(str,arguments),'-m','2','-v','2'];start=time.perf_counter()
        try:
            completed=subprocess.run(command,capture_output=True,text=True,timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        except subprocess.TimeoutExpired as exc:
            def decoded(value):return value.decode(errors='replace') if isinstance(value,bytes) else (value or '')
            save(out/(label+'.execution.json'),dict(label=label,command=command,elapsed_s=time.perf_counter()-start,
                timed_out=True,timeout_s=45,stdout=decoded(exc.stdout),stderr=decoded(exc.stderr),
                outcome='Incomplete. The owned CLI process was stopped. No automatic retry or geometry pass.'))
            raise

        record=dict(label=label,command=command,elapsed_s=time.perf_counter()-start,returncode=completed.returncode,stdout=completed.stdout,stderr=completed.stderr)
        # Build42594 can assert during cleanup after a successful conversion.
        # Keep the failed exit receipt, then require a separate native reopen
        # and all geometry checks below. Other errors remain hard failures.
        known_cleanup=(arguments[0]=='convert' and 'nTop successfully built.' in completed.stdout and 'non-failed onBuildStateUpdate called on dummy listener' in completed.stderr and Path(arguments[3]).is_file())
        record['post_save_cleanup_assertion']=known_cleanup
        save(out/(label+'.execution.json'),record);runs.append(record)
        assert (completed.returncode==0 or known_cleanup) and '[E]' not in completed.stdout,(label,completed.stdout,completed.stderr)
        print(label,round(record['elapsed_s'],3),'s',flush=True)
    authored=part_recipe();save(out/'part.recipe.json',authored)
    run('part_convert',['convert','--ext',out/'part.recipe.json',out/'Drilled_Chamfered_Part.ntop'])
    run('part_readback',['exportjson','--ext',out/'Drilled_Chamfered_Part.ntop',out/'part.saved.recipe.json'])
    part=json.loads((out/'part.saved.recipe.json').read_text());assert len(part['inputs'])==1 and part['inputs'][0]['contents']['value']['val']==.01
    assert next(b for b in part['body'] if b['id']==part['output']['id'])['type']=='implicit'
    assembly=assembly_recipe(part);save(out/'assembly.recipe.json',assembly)
    run('assembly_convert',['convert','--ext',out/'assembly.recipe.json',out/'Two_Instance_Assembly.ntop'])
    run('assembly_readback',['exportjson','--ext',out/'Two_Instance_Assembly.ntop',out/'assembly.saved.recipe.json'])
    saved_assembly=json.loads((out/'assembly.saved.recipe.json').read_text());assert len(saved_assembly['imports'])==1 and len(saved_assembly['cbRefs'])==1
    assert next(b for b in saved_assembly['body'] if b['id']==saved_assembly['output']['id'])['type']=='implicit'
    validation,expected=validation_recipe(assembly);save(out/'validation.recipe.json',validation);save(out/'field_expectations.json',expected)
    run('validation_convert',['convert','--ext',out/'validation.recipe.json',out/'Assembly_Field_Validation.ntop'])
    checks=[]
    for width in [10,14]:
        inputs=out/f'width_{width}.inputs.json';values=out/f'width_{width}.values.json';save(inputs,{'inputs':[{'name':'Width','type':'real','value':width/1000,'units':'m'}]})
        run(f'evaluate_width_{width}',[out/'Assembly_Field_Validation.ntop','-j',inputs,'-o',values])
        output=json.loads(values.read_text());row=next(x for x in output if x['name']=='CHECK Values');measured=[v['val']*1000 for v in row['value']['value']];assert len(measured)==len(expected)
        for exp,value in zip(expected,measured):
            target=exp['expected_mm'][str(width)];error=abs(value-target);assert error<1e-5,(width,exp['name'],value,target)
            checks.append(dict(width_input_mm=width,name=exp['name'],measured_field_mm=value,expected_field_mm=target,error_mm=error,passed=True))
    # Reopen and evaluate the actual assembly body, not just the validation copy.
    run('assembly_evaluate_reopen',[out/'Two_Instance_Assembly.ntop','-j',out/'width_14.inputs.json','-o',out/'assembly_implicit_output.json'])
    manifest=dict(transport='nTopCL convert --ext and exportjson --ext. This pilot did not use the live Notebook API.',executable=str(exe),executable_sha256=digest(exe),part_authored_identity=authored['name'],part_saved_identity=part['name'],assembly_uses_actual_saved_part_identity=True,
        part_output='implicit',assembly_output='implicit',part_inputs=part['inputs'],assembly_import_count=1,assembly_custom_instance_count=2,assembly_translation_B_mm=[0,12,0],fixed_hole_diameter_mm=2,fixed_thickness_mm=2,width_cases_mm=[10,14],field_checks=checks,field_check_tolerance_mm=1e-5,passed=True,elapsed_s=time.perf_counter()-started,
        post_save_cleanup_assertions=[r['label'] for r in runs if r['post_save_cleanup_assertion']],command_times_s={r['label']:r['elapsed_s'] for r in runs},files={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='verification.json'})
    save(out/'verification.json',manifest);print(json.dumps(dict(passed=True,checks=len(checks),maximum_error_mm=max(c['error_mm'] for c in checks),elapsed_s=manifest['elapsed_s'],output=str(out))),flush=True)

if __name__=='__main__':main()
