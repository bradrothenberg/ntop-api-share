"""Three API-authored assemblies of native implicit-output part families.

Family inputs are connected by exact saved order. Identical input tuples share
one family evaluation. Every placed body remains individually addressable.
"""
import argparse,copy,hashlib,json,math
from pathlib import Path
import build_sheet_metal as api
import build_advanced_sheet_metal as a
import build_drafted_sheet_metal as d
ROOT=Path.cwd()/'.local'/'sheet-metal-study'/'assemblies'
KEYS=['electronics_enclosure','routing_cassette','instrument_pod']
TITLES=['Ventilated electronics enclosure','Cable-routing cassette','Raised-cover instrument pod']
BLUE=[.141,.541,1.0];SILVER=[.69,.75,.79];DARK=[.24,.34,.43]

def wire(x):return x.wire if isinstance(x,api.S) else api.real(x,1)
def val(x):return a.val(x)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load_family(key):
    path=(ROOT.parents[0]/'drafted/evidence'/(key+'.api-readback.json')) if key in d.KEYS else ROOT/'families/contracts'/(key+'.saved.json')
    doc=json.loads(path.read_text());assert next(x for x in doc['body'] if x['id']==doc['output']['id'])['type']=='implicit'
    return doc,path

class Assembly(api.Recipe):
    def __init__(self,key,title):
        super().__init__(key,title);self.imports={};self.family_cache={};self.instances=[];self.contracts={};self.joints=[];self.fit_notes=[]
    def family(self,key,overrides=None,mesh_key=None):
        overrides=overrides or {}
        if key not in self.imports:
            doc,path=load_family(key);self.imports[key]=doc;self.contracts[key]={'identity':doc['name'],'version':doc['version'],'saved_recipe_sha256':digest(path),'inputs':[p['name'] for p in doc['inputs']]}
        doc=self.imports[key];assert set(overrides)<=set(x['name'] for x in doc['inputs'])
        inputs=[wire(overrides[p['name']]) if p['name'] in overrides else p['contents'] for p in doc['inputs']]
        signature=json.dumps([key,inputs],sort_keys=True)
        if signature not in self.family_cache:
            func=doc['name']+('<'+','.join(p['type'] for p in doc['inputs'])+'>' if doc['inputs'] else '')+'['+'.'.join(map(str,doc['version']))+']'
            ref=self.hold('Family '+str(len(self.family_cache)+1)+' '+key,'implicit',self.node(func,'implicit',inputs),'Part families')
            effective={p['name']:val(overrides[p['name']]) if p['name'] in overrides else p['contents']['value']['val']*1000 for p in doc['inputs']}
            self.family_cache[signature]=(ref,{'family':key,'mesh_key':mesh_key or key,'inputs_mm':effective})
        return self.family_cache[signature]
    def place(self,name,family,xyz=(0,0,0),explode=(0,0,0),color=SILVER):
        ref,info=family
        vector=self.node('vector<real,real,real>','vector',[wire(q) for q in xyz])
        body=self.hold(name,'implicit',self.node('translate<spatial3d,vector>','implicit',[ref,vector]),'Placed bodies')
        self.instances.append({'name':name,**info,'translation_mm':[val(q) for q in xyz],'explode_mm':list(explode),'color':color,'native_variable':name})
        return body
    def probe(self,name,body,xyz,expectation):
        self.hold('CHECK '+name,'real',self.node('evaluate_field<real_field,point>','real',[api.ref(body['ref']['id'],'scalar field'),self.pt(xyz)]),'Checks')
        self.checks.append({'name':'CHECK '+name,'point_mm':[val(q) for q in xyz],'expectation':expectation})
    def joint(self,label,sheet,hole_radius,x,y,z,t,screw,nut=None):
        self.probe(label+' sheet bore',sheet,[x,y,z+t/2],'positive')
        self.probe(label+' sheet bore boundary',sheet,[x+hole_radius,y,z+t/2],'zero')
        self.probe(label+' sheet stock',sheet,[x+hole_radius+.3,y,z+t/2],'negative')
        self.probe(label+' screw at sheet',screw,[x,y,z+t/2],'negative')
        self.joints.append({'name':label,'hole_radius_mm':hole_radius,'center_mm':[val(x),val(y),val(z)],'sheet_thickness_mm':val(t)})
    def document(self,output):
        doc=super().document(output);doc['imports']=list(self.imports.values());doc['cbRefs']=list(range(len(self.imports)))
        doc['description']='Authored sheet-metal assembly. Native reusable implicit families, exact mounting datums and separate nominal hardware envelopes. See report for fit-check scope.'
        return doc

def m4(r):return r.family('socket_screw'),r.family('hex_nut')
def m3(r,length,mesh_key):
    return r.family('socket_screw',{'Shank diameter':3,'Under-head length':length,'Head diameter':5.5,'Head height':2.4,'Socket across flats':2},mesh_key),r.family('hex_nut',{'Nominal diameter':3,'Across flats':5.5,'Height':2.4},'m3_nut')

def electronics_enclosure():
    r=Assembly(KEYS[0],TITLES[0]);L=r.param('Enclosure length',220)
    base=r.place('01 Drafted vent chassis',r.family('vent_chassis',{'Length':L}),color=BLUE)
    lid=r.place('02 Folded lid',r.family('folded_lid',{'Base length':L}),explode=(0,0,65))
    screw,nut=m4(r);y=55+2*2.6*d.SB+d.wall_leg(30,2.6)*d.CB+8
    for i,(x,yy) in enumerate([(L*.38*s,y*sy) for s in [-1,1] for sy in [-1,1]]):
        s=r.place(f'03.{i+1} M4 screw',screw,(x,yy,32.4),(0,0,93),DARK)
        n=r.place(f'04.{i+1} M4 nut',nut,(x,yy,30),(0,0,-25),DARK)
        r.joint(f'Chassis joint {i}',base,2.5,x,yy,30,1.2,s,n);r.joint(f'Lid joint {i}',lid,2.5,x,yy,31.2,1.2,s,n)
    for b,label in [(base,'chassis'),(lid,'lid')]:r.probe(label+' mating plane',b,[0,y,31.2],'zero')
    r.probe('length-controlled floor edge',base,[L/2,0,.6],'zero')
    r.probe('lid end clearance',lid,[L/2,0,10],'positive')
    r.fit_notes=[{'item':'M4 clearance holes','nominal_clearance_mm':.5,'meaning':'Radial clearance: 5 mm hole around 4 mm smooth shank.'},{'item':'Roof-to-chassis flanges','nominal_clearance_mm':0,'meaning':'Mating sheet faces at Z31.2 mm.'},{'item':'Lid end bends','nominal_clearance_mm':.5,'meaning':'Base end is 0.5 mm inside the start of the roof bend; straight end wall has larger clearance.'}]
    return r,{'Enclosure length':240},'Enclosure length 220 → 240 mm; lid length and all four fastener centers follow.'

def routing_cassette():
    r=Assembly(KEYS[1],TITLES[1]);spacing=r.param('Rail center spacing',180);L=spacing+20
    panel=r.place('01 Drafted routing panel',r.family('cable_panel',{'Length':L}),explode=(0,0,45),color=BLUE)
    rail=r.family('support_rail');left=r.place('02 Left support rail',rail,(-spacing/2,0,0),(-20,0,-10));right=r.place('03 Right support rail',rail,(spacing/2,0,0),(20,0,-10))
    screw,nut=m3(r,6,'m3_short_screw');edgeleg=(15-.6-2.2*(1-d.CB)-.6*d.CB)/d.SB;y=70-2.2*d.SB-edgeleg*d.CB-.6*d.SB-10
    for i,(sign,yy) in enumerate([(s,y*sy) for s in [-1,1] for sy in [-1,1]]):
        x=spacing/2*sign;b=left if sign<0 else right
        s=r.place(f'04.{i+1} M3 screw',screw,(x,yy,1.2),(0,0,70),DARK);n=r.place(f'05.{i+1} M3 nut',nut,(x,yy,-1.5),(0,0,-30),DARK)
        r.joint(f'Panel joint {i}',panel,2,x,yy,0,1.2,s,n);r.joint(f'Rail joint {i}',b,2,x,yy,-1.5,1.5,s,n)
    for sign,b in [(-1,left),(1,right)]:
        r.probe(f'Rail {sign} crown contact',b,[spacing/2*sign,0,0],'zero');r.probe(f'Panel {sign} contact',panel,[spacing/2*sign,0,0],'zero')
    r.probe('panel resized end',panel,[L/2,0,.6],'zero')
    r.fit_notes=[{'item':'M3 clearance holes','nominal_clearance_mm':.5,'meaning':'Radial clearance: 4 mm holes around 3 mm smooth shanks.'},{'item':'Panel-to-rail crowns','nominal_clearance_mm':0,'meaning':'Panel underside and rail crown tops share Z0.'},{'item':'Rail reuse','nominal_clearance_mm':None,'meaning':'Both placements reference one evaluated rail family.'}]
    return r,{'Rail center spacing':200},'Rail center spacing 180 → 200 mm; panel length grows 200 → 220 mm and mounting holes remain aligned.'

def instrument_pod():
    r=Assembly(KEYS[2],TITLES[2]);gap=r.param('Cover stand-off',6);adapter_z=35.2+gap;cover_z=adapter_z+1.5
    housing=r.place('01 Drafted stepped housing',r.family('stepped_housing'),color=BLUE)
    adapter=r.place('02 Raised adapter plate',r.family('adapter_plate'),(0,0,adapter_z),(0,0,55))
    cover=r.place('03 Drafted annular cover',r.family('annular_cover'),(0,0,cover_z),(0,0,105),BLUE)
    spacer=r.family('spacer',{'Height':gap});screw,nut=m3(r,gap+8,'m3_long_screw')
    for i,(x,y) in enumerate([(x,y) for x in [-45,0,45] for y in [-71.5,71.5]]):
        r.place(f'04.{i+1} Spacer',spacer,(x,y,35.2),(0,0,28),DARK)
        s=r.place(f'05.{i+1} M3 stand-off screw',screw,(x,y,cover_z),(0,0,82),DARK)
        r.place(f'06.{i+1} M3 housing nut',nut,(x,y,34),(0,0,-24),DARK)
        # Slot is 12 x 4 mm: use the Y boundary, not the rounded end.
        r.probe(f'Housing slot {i}',housing,[x,y,34.6],'positive');r.probe(f'Housing slot side {i}',housing,[x,y+2,34.6],'zero');r.probe(f'Stand-off screw {i}',s,[x,y,34.6],'negative')
        r.joint(f'Adapter stand-off {i}',adapter,2,x,y,adapter_z,1.5,s)
    s4,n4=m4(r);meta=json.loads((ROOT.parent/'drafted/evidence/annular_cover.design.json').read_text())['metadata'];bolt=meta['outside_mm'][0]/2-7
    for i in range(8):
        x=bolt*math.cos(i*math.pi/4);y=bolt*math.sin(i*math.pi/4)
        s=r.place(f'07.{i+1} M4 cover screw',s4,(x,y,cover_z+1.2),(0,0,140),DARK);r.place(f'08.{i+1} M4 adapter nut',n4,(x,y,adapter_z),(0,0,33),DARK)
        r.joint(f'Cover joint {i}',cover,2.5,x,y,cover_z,1.2,s);r.joint(f'Adapter cover joint {i}',adapter,2.5,x,y,adapter_z,1.5,s)
        r.probe(f'Nut envelope clears housing {i}',housing,[x,y,adapter_z-3.2],'positive')
    r.probe('annular mating face',cover,[bolt+4,0,cover_z],'zero');r.probe('adapter mating face',adapter,[bolt+4,0,cover_z],'zero')
    r.fit_notes=[{'item':'Adapter stand-off','nominal_clearance_mm':6,'meaning':'Open vented separation above the housing flange; not a gasketed enclosure.'},{'item':'M4 nut-to-housing height','nominal_clearance_mm':2.8,'meaning':'Lowest M4 nut is 2.8 mm above the highest housing surface at nominal stand-off.'},{'item':'M3 spacer bore','nominal_clearance_mm':.25,'meaning':'3.5 mm spacer bore around a 3 mm smooth shank.'},{'item':'Cover bearing annulus','nominal_clearance_mm':None,'meaning':'Cover flange rests on the adapter around its 100 mm center opening.'}]
    return r,{'Cover stand-off':10},'Cover stand-off 6 → 10 mm; spacers and M3 under-head length grow with both upper sheets and all upper fasteners.'

def main():
    global ROOT
    p=argparse.ArgumentParser();p.add_argument('--case',default='all');p.add_argument('--out',type=Path,default=ROOT);args=p.parse_args();ROOT=args.out.resolve();records=[]
    for folder in ['models','evidence','inputs']:(ROOT/folder).mkdir(parents=True,exist_ok=True)
    for key in KEYS if args.case=='all' else args.case.split(','):
        r,changed,summary=globals()[key]();body=r.boolean('union','Assembly output',[api.ref(x['name']) for x in r.instances]);r.sections['Assembly output']='Assembly output'
        source=r.document(body);(ROOT/'models'/(key+'.recipe.json')).write_text(json.dumps(source,indent=1))
        checks=r.hold('Field check values','list<real>',r.node('core.list<real>','list<real>',[api.ref(x['name']) for x in r.checks]),'Checks')
        (ROOT/'models'/(key+'.checks.recipe.json')).write_text(json.dumps(r.document(checks),indent=1))
        design={'title':r.title,'instances':r.instances,'contracts':r.contracts,'family_evaluations':len(r.family_cache),'sections':r.sections,'output':body['ref']['id'],'field_checks':r.checks,'joints':r.joints,'fit_notes':r.fit_notes,'changed_inputs_mm':changed,'changed_summary':summary,'parameters':r.parameters,'source_recipe_sha256':digest(ROOT/'models'/(key+'.recipe.json'))}
        (ROOT/'evidence'/(key+'.design.json')).write_text(json.dumps(design,indent=2));records.append({'key':key,'instances':len(r.instances),'checks':len(r.checks),'family_evaluations':len(r.family_cache)})
        (ROOT/'inputs'/(key+'.changed.json')).write_text(json.dumps({'inputs':[{'name':k,'type':'real','value':v/1000,'units':'m'} for k,v in changed.items()]}))
        print(records[-1],flush=True)
    (ROOT/'evidence/assembly-summary.json').write_text(json.dumps(records,indent=2))
if __name__=='__main__':main()
