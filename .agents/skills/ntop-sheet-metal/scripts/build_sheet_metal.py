"""Author complete Notebook API recipes with analytic, parametric sheet profiles.

No imported CAD or mesh defines the geometry. Millimetres enter here; recipe
literals are SI. A bend is a true circular arc in a closed sheet cross-section.
"""
from __future__ import annotations
import argparse, json, math, uuid
import sys
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()/'.local'/'sheet-metal-study'

def real(v, dim=0):
    return {'type':'real','value':{'isFinite':True,'units':{'length':dim} if dim else {},'val':v*(.001**dim)}}
def vector(v):
    return {'type':'vector','value':{'units':{},'value':[{'isFinite':True,'val':x} for x in v]}}
def literal_point(v):
    return {'type':'point','value':[{'isFinite':True,'val':x*.001} for x in v]}
def ref(name, prop=None): return {'ref':{'id':name},'props':[prop] if prop else []}

class S:
    def __init__(self,r,wire,value,dim=1): self.r,self.wire,self.value,self.dim=r,wire,value,dim
    def op(self,other,op):
        if not isinstance(other,S): other=S(self.r,real(other,0 if op in ('multiply','divide') else self.dim),other,0 if op in ('multiply','divide') else self.dim)
        dim=self.dim if op in ('add','subtract') else self.dim+(other.dim if op=='multiply' else -other.dim)
        value={'add':lambda:self.value+other.value,'subtract':lambda:self.value-other.value,'multiply':lambda:self.value*other.value,'divide':lambda:self.value/other.value}[op]()
        wire=self.r.node(op+'<real,real>','real',[self.wire,other.wire])
        return S(self.r,wire,value,dim)
    def __add__(self,x): return self.op(x,'add')
    __radd__=__add__
    def __sub__(self,x): return self.op(x,'subtract')
    def __rsub__(self,x): return -self+x
    def __mul__(self,x): return self.op(x,'multiply')
    __rmul__=__mul__
    def __truediv__(self,x): return self.op(x,'divide')
    def __neg__(self): return self*-1

class Recipe:
    def __init__(self,key,title):
        self.key,self.title=key,title; self.serial=0; self.body=[]; self.parameters=[]; self.sections={}; self.curves={}; self.extrusions=[]; self.checks=[]
    def node(self,func,typ,inputs):
        self.serial+=1
        # Copying symbolic subexpressions requires fresh node IDs at serialization.
        return {'func':func,'type':typ,'inputs':inputs,'id':f'n{self.serial:05d}','name':func.split('<')[0]}
    def hold(self,name,typ,contents,section='Construction'):
        self.body.append({'id':name,'name':name,'type':typ,'variable':True,'contents':contents});self.sections[name]=section
        return ref(name)
    def param(self,name,value,dim=1):
        i=len(self.parameters)
        self.parameters.append({'name':name,'type':'real','dimension':{'length':dim} if dim else {},'description':'Study input; see source ledger and report for dimensional convention.','contents':real(value,dim)})
        return S(self,self.hold(name,'real',{'input':i,'props':[]},'Inputs'),value,dim)
    def named_scalar(self,name,s): return S(self,self.hold(name,'real',s.wire,'Calculations'),s.value,s.dim)
    def pt(self,coords): return self.node('point<real,real,real>','point',[c.wire if isinstance(c,S) else real(c,1) for c in coords])
    def boolean(self,op,name,bodies,base=None):
        inputs=[{'type':'blend_enum','value':{'enum':0}},real(0,1)]
        if base is not None: inputs.append(base)
        inputs.append(self.node('core.list<implicit>','list<implicit>',bodies))
        sig='blend_enum,real_field,'+('implicit,' if base is not None else '')+'list<implicit>'
        return self.hold(name,'implicit',self.node(f'boolean_{op}<{sig}>[5.44.0]','implicit',inputs))
    def profile(self,name,edges,mapping,normal):
        curves=[]; sampled=[]
        for kind,pts in edges:
            inputs=[self.pt(mapping(*p)) for p in pts]
            curves.append(self.node('two_point_line<point,point>' if kind=='line' else 'three_point_arc<point,point,point>', 'line_segment' if kind=='line' else 'arc',inputs))
            sampled.append({'kind':kind,'points':[[float(q.value if isinstance(q,S) else q) for q in mapping(*p)] for p in pts]})
        self.curves[name]=sampled
        listing=self.node('core.list<curve_interface>','list<curve_interface>',curves)
        return self.hold(name,'new_profile',self.node('profile_from_curves<list<curve_interface>,vector>[5.20.0]','new_profile',[listing,vector(normal)]))
    def extrude(self,name,profile,distance,direction):
        d=distance.wire if isinstance(distance,S) else real(distance,1)
        val=distance.value if isinstance(distance,S) else distance
        self.extrusions.append({'name':name,'profile':profile['ref']['id'],'distance':val,'direction':direction})
        zero_angle={'type':'real','value':{'isFinite':True,'units':{'angle':1},'val':0.0}}
        return self.hold(name,'implicit',self.node('extrude<new_profile,real,real,bool,vector>[5.20.0]','implicit',[profile,d,zero_angle,{'type':'bool','value':{'val':False}},vector(direction)]))
    def drill(self,name,positions,t,diameter,body):
        tools=[]
        for x,y in positions:
            tools.append(self.node('cylinder<point,point,real>','cylinder',[self.pt([x,y,-t*3]),self.pt([x,y,t*4]),(diameter/2).wire]))
        return self.boolean('subtract',name,tools,base=body)
    def check(self,name,body,p,expectation):
        w=self.hold(name,'real',self.node('evaluate_field<real_field,point>','real',[ref(body['ref']['id'],'scalar field'),literal_point(p)]),'Checks')
        self.checks.append({'name':name,'point_mm':p,'expectation':expectation});return w
    def document(self,output):
        doc={'name':'user_func_'+str(uuid.uuid5(uuid.NAMESPACE_URL,'sheet-metal-dev/'+self.key)).replace('-','_'),'displayname':self.title,'description':'Analytic sheet metal study. Source dimensions and authored assumptions are distinguished in the accompanying HTML report. No forming simulation is claimed.','version':[1,0,0],'inputs':self.parameters,'imports':[],'cbRefs':[],'namespaces':[],'body':self.body,'output':{'id':output['ref']['id']}}
        # Compile repeated exact expressions into named variables. This preserves
        # native input-driven math without exponentially expanding nested formulas.
        def canonical(x):
            if isinstance(x,dict):return {k:canonical(v) for k,v in x.items() if k not in ('id','name') or k=='id' and 'func' not in x}
            if isinstance(x,list):return [canonical(v) for v in x]
            return x
        counts=Counter(); keys={}
        def scan(x):
            if isinstance(x,dict):
                if 'func' in x:
                    key=json.dumps(canonical(x),sort_keys=True);keys[id(x)]=key;counts[key]+=1
                for v in x.values():scan(v)
            elif isinstance(x,list):
                for v in x:scan(v)
        scan(doc['body']);serial=0;aux=0;seen={};ordered=[]
        def compile_node(x):
            nonlocal serial,aux
            if isinstance(x,dict):
                key=keys.get(id(x))
                if key is not None and key in seen:return ref(seen[key])
                y={k:compile_node(v) for k,v in x.items()}
                if 'func' in y:
                    serial+=1;y['id']=f'owned_{serial:05d}'
                    if counts[key]>1:
                        aux+=1;name=f'aux {aux:03d} {y["func"].split("<")[0]}';seen[key]=name
                        ordered.append({'id':name,'name':name,'type':y['type'],'variable':True,'contents':y});self.sections[name]='Expressions'
                        return ref(name)
                return y
            if isinstance(x,list):return [compile_node(v) for v in x]
            return x
        for row in doc['body']:ordered.append(compile_node(row))
        doc['body']=ordered
        return doc

def addv(p,v,k=1): return (p[0]+v[0]*k,p[1]+v[1]*k)
def left(u): return (-u[1],u[0])
def strip_edges(start,tangent,steps,t):
    """Offset both sides of a midsurface tangent chain; turns are +/-90 degrees."""
    side_edges=[[],[]];p=start;u=tangent
    for kind,val in steps:
        if kind=='straight':
            end=addv(p,u,val)
            for edges,d in zip(side_edges,[t/2,-t/2]):
                n=left(u);edges.append(('line',[addv(p,n,d),addv(end,n,d)]))
            p=end
        else:
            radius,sign=val; n=left(u); center=addv(p,n,radius*sign)
            un=(n[0]*sign,n[1]*sign); nn=left(un)
            end=addv(center,nn,-radius*sign)
            for edges,d in zip(side_edges,[t/2,-t/2]):
                begin=addv(p,n,d);finish=addv(end,nn,d)
                mid=(center[0]+((begin[0]-center[0])+(finish[0]-center[0]))/math.sqrt(2),center[1]+((begin[1]-center[1])+(finish[1]-center[1]))/math.sqrt(2))
                edges.append(('arc',[begin,mid,finish]))
            p=end;u=un
    a,b=side_edges
    return a+[('line',[a[-1][1][-1],b[-1][1][-1]])]+[(kind,list(reversed(pts))) for kind,pts in reversed(b)]+[('line',[b[0][1][0],a[0][1][0]])]

def common(r,t0=1.5,ri0=2):
    t=r.param('Thickness',t0);ri=r.param('Inside bend radius',ri0);k=r.param('K factor',.42,0)
    ro=r.named_scalar('Outside bend radius',ri+t);rm=r.named_scalar('Geometric midsurface radius',ri+t/2)
    ba=r.named_scalar('90 degree bend allowance',(ri+k*t)*(math.pi/2))
    r.named_scalar('90 degree bend deduction',ro*2-ba)
    return t,ri,k,ro,rm,ba

def section_part(kind):
    names={'bracket':'01 - Single bend mounting bracket','ucover':'02 - U-shaped enclosure cover','strut':'04 - Return-flange channel coupon'}
    r=Recipe(kind,names[kind]);t,ri,k,ro,rm,ba=common(r,2.667 if kind=='strut' else 1.5,2.7 if kind=='strut' else 2)
    width=r.param('Outside width',41.275 if kind=='strut' else 100 if kind=='ucover' else 40)
    height=r.param('Outside height',41.275 if kind=='strut' else 40 if kind=='ucover' else 30)
    depth=r.param('Extrusion length',120 if kind=='strut' else 140 if kind=='ucover' else 50)
    if kind=='bracket':
        steps=[('straight',width-ro),('bend',(rm,1)),('straight',height-ro)];start=(0,t/2);u=(1,0)
        flat_length=width+height-ro*2+ba
    elif kind=='ucover':
        steps=[('straight',height-ro),('bend',(rm,1)),('straight',width-ro*2),('bend',(rm,1)),('straight',height-ro)];start=(-width/2+t/2,height);u=(0,-1)
        flat_length=width-ro*2+(height-ro)*2+ba*2
    else:
        opening=r.param('Opening width',22.225)
        lip=(width-opening)/2-ro
        steps=[('straight',lip),('bend',(rm,1)),('straight',height-ro*2),('bend',(rm,1)),('straight',width-ro*2),('bend',(rm,1)),('straight',height-ro*2),('bend',(rm,1)),('straight',lip)]
        start=(-opening/2,height-t/2);u=(-1,0)
        flat_length=lip*2+(height-ro*2)*2+width-ro*2+ba*4
    edges=strip_edges(start,u,steps,t)
    prof=r.profile('Continuous bent sheet section',edges,lambda y,z:(-depth/2,y,z),(1,0,0))
    body=r.extrude('Formed sheet',prof,depth,(1,0,0))
    flat=r.named_scalar('Developed strip width',flat_length)
    fp=r.profile('Developed blank outline',polygon_edges([(-depth/2,-flat/2),(depth/2,-flat/2),(depth/2,flat/2),(-depth/2,flat/2)]),lambda x,y:(x,y,0),(0,0,1))
    r.extrude('Flat blank',fp,t,(0,0,1))
    sample_y=(width.value-ro.value)/2 if kind=='bracket' else 0
    r.check('CHECK base material',body,[0,sample_y,t.value/2],'negative')
    r.check('CHECK below base',body,[0,sample_y,-.5],'positive')
    r.check('CHECK empty interior',body,[0,sample_y,10],'positive')
    return r,body,{'kind':kind,'flat_width_mm':flat.value,'depth_mm':depth.value,'thickness_mm':t.value,'inside_radius_mm':ri.value,'bend_count':1 if kind=='bracket' else 2 if kind=='ucover' else 4}

def polygon_edges(points):return [('line',[p,points[(i+1)%len(points)]]) for i,p in enumerate(points)]

def enclosure_round():
    r=Recipe('enclosure','03 - Four-wall sheet metal enclosure');t,ri,k,ro,rm,ba=common(r,1.016,1.5)
    L=r.param('Outside length',152.4);W=r.param('Outside width',101.6);H=r.param('Outside height',50.8);g=r.param('Corner relief setback',1.5);dh=r.param('Mounting hole diameter',3.2)
    rr=r.param('Relief root radius',.75)
    assert 0<2*rr.value<=g.value, 'Round relief width must fit the corner setback'
    lf=r.named_scalar('Base tangent length',L-ro*2);wf=r.named_scalar('Base tangent width',W-ro*2);h=r.named_scalar('Wall tangent height',H-ro)
    steps=[('straight',h),('bend',(rm,1)),('straight',wf),('bend',(rm,1)),('straight',h)]
    p=r.profile('Base and two long walls section',strip_edges((-W/2+t/2,H),(0,-1),steps,t),lambda y,z:(-lf/2,y,z),(1,0,0))
    base=r.extrude('Base and long walls',p,lf,(1,0,0));ends=[]
    for sign,label in [(1,'Right'),(-1,'Left')]:
        edges=strip_edges((lf/2-t*2,t/2),(1,0),[('straight',t*2),('bend',(rm,1)),('straight',h)],t)
        prof=r.profile(label+' end wall section',edges,lambda x,z,s=sign:(x*s,-wf/2+g,z),(0,1,0))
        ends.append(r.extrude(label+' end wall',prof,wf-g*2,(0,1,0)))
    stock=r.boolean('union','Joined enclosure',[base,*ends])
    # Round-ended slots terminate in the shared flat base. Their width fits
    # the corner gap, so the same cutters describe formed and developed stock.
    A=lf/2;B=wf/2;cx=A-rr;cy=B-g+rr;end=A+rr
    reliefs=[];relief_centers=[]
    for sx in [-1,1]:
        for sy in [-1,1]:
            label=f'{sx:+d} {sy:+d}'
            edges=[('line',[(cx,cy-rr),(end,cy-rr)]),('line',[(end,cy-rr),(end,cy+rr)]),('line',[(end,cy+rr),(cx,cy+rr)]),('arc',[(cx,cy+rr),(cx-rr,cy),(cx,cy-rr)])]
            prof=r.profile('Round relief slot '+label,edges,lambda x,y,sx=sx,sy=sy:(x*sx,y*sy,-t),(0,0,1))
            reliefs.append(r.extrude('Round relief cutter '+label,prof,t*3,(0,0,1)))
            relief_centers.append([sx*cx.value,sy*cy.value])
    relieved=r.boolean('subtract','Corner relieved enclosure',reliefs,base=stock)
    hx=lf/2-10;hy=wf/2-10;holes=[(hx*sx,hy*sy) for sx in [-1,1] for sy in [-1,1]]
    formed=r.drill('Formed enclosure',holes,t,dh,relieved)
    f=r.named_scalar('Blank wing extension',h+ba);A=lf/2;B=wf/2
    points=[(-A,-B-f),(A,-B-f),(A,-B+g),(A+f,-B+g),(A+f,B-g),(A,B-g),(A,B+f),(-A,B+f),(-A,B-g),(-A-f,B-g),(-A-f,-B+g),(-A,-B+g)]
    fp=r.profile('Relieved flat blank outline',polygon_edges(points),lambda x,y:(x,y,0),(0,0,1))
    flat_stock=r.extrude('Flat blank stock',fp,t,(0,0,1))
    flat_relieved=r.boolean('subtract','Corner relieved flat blank',reliefs,base=flat_stock)
    r.drill('Flat enclosure blank',holes,t,dh,flat_relieved)
    r.named_scalar('Flat blank X extent',lf+f*2);r.named_scalar('Flat blank Y extent',wf+f*2)
    tv,rv,rvout,lv,wv,hv= t.value,rm.value,ro.value,lf.value,wf.value,h.value
    volume=tv*(lv*(wv+2*hv+math.pi*rv)+2*(wv-2*g.value)*(hv+math.pi/2*rv))-4*math.pi*(dh.value/2)**2*tv
    flat_area=lv*wv+2*lv*f.value+2*(wv-2*g.value)*f.value-4*math.pi*(dh.value/2)**2
    relief_area=4*(2+math.pi/2)*rr.value**2
    volume-=relief_area*tv;flat_area-=relief_area
    checks=[('base center',[0,0,tv/2],'negative'),('floor top',[0,0,tv],'zero'),('floor bottom',[0,0,0],'zero'),('cavity',[0,0,20],'positive'),('long wall',[0,W.value/2-tv/2,25],'negative'),('short wall',[L.value/2-tv/2,0,25],'negative'),('foot overlap',[lv/2-tv,0,tv/2],'negative'),('open corner',[L.value/2-tv/2,W.value/2-tv/2,25],'positive')]
    for i,(x,y) in enumerate(holes):checks.append((f'hole {i+1}',[x.value,y.value,tv/2],'positive'))
    for sx in [-1,1]:
        for sy in [-1,1]:
            checks.extend([(f'round relief {sx} {sy} void',[sx*cx.value,sy*cy.value,tv/2],'positive'),(f'round relief {sx} {sy} root',[sx*(cx.value-rr.value),sy*cy.value,tv/2],'zero'),(f'round relief {sx} {sy} stock',[sx*(cx.value-rr.value-.2),sy*cy.value,tv/2],'negative')])
    cy=wv/2;cz=rvout
    for angle in [15,45,75]:
        a=math.radians(angle)
        for radius,label,exp in [(ri.value,'inside surface','zero'),(rv,'mid thickness','negative'),(rvout,'outside surface','zero')]:
            checks.append((f'bend {angle} {label}',[0,cy+radius*math.sin(a),cz-radius*math.cos(a)],exp))
    for name,p,exp in checks:r.check('CHECK '+name,formed,p,exp)
    return r,formed,{'kind':'enclosure','revision':2,'outside_mm':[L.value,W.value,H.value],'thickness_mm':tv,'inside_radius_mm':ri.value,'relief_mm':g.value,'relief_root_radius_mm':rr.value,'relief_centers_mm':relief_centers,'relief_area_removed_mm2':relief_area,'hole_diameter_mm':dh.value,'base_tangent_mm':[lv,wv],'wall_tangent_mm':hv,'bend_allowance_mm':ba.value,'bend_deduction_mm':2*rvout-ba.value,'flat_extents_mm':[lv+2*f.value,wv+2*f.value],'analytic_formed_volume_mm3':volume,'flat_area_mm2':flat_area,'flat_volume_mm3':flat_area*tv,'K':k.value,'bend_count':4,'flat_outline_mm':[[x.value,y.value] for x,y in points]}

def cup():
    r=Recipe('cup','05 - Cylindrical drawn-cup geometry precursor');t,ri,k,ro,rm,ba=common(r,1,3)
    diameter=r.param('Internal diameter',33);H=r.param('Outside height',20)
    flat_radius=diameter/2-ri
    edges=strip_edges((S(r,real(0,1),0),t/2),(1,0),[('straight',flat_radius),('bend',(rm,1)),('straight',H-ro)],t)
    p=r.profile('Cup meridian section',edges,lambda rad,z:(rad,0,z),(0,-1,0))
    axis=r.node('axis<point,vector>','axis',[literal_point([0,0,0]),vector([0,0,1])])
    angle={'type':'real','value':{'isFinite':True,'units':{'angle':1},'val':2*math.pi}}
    body=r.hold('Idealized cup','implicit',r.node('revolve<new_profile,axis,real>[5.20.0]','implicit',[p,axis,angle]))
    r.check('CHECK base',body,[0,0,t.value/2],'negative');r.check('CHECK cavity',body,[0,0,10],'positive');r.check('CHECK wall',body,[17,0,10],'negative')
    return r,body,{'kind':'cup','thickness_mm':t.value,'inside_radius_mm':ri.value,'internal_diameter_mm':diameter.value,'height_mm':H.value,'source_blank_diameter_mm':60,'forming_simulated':False,'bend_count':None}

def write_case(r,body,meta):
    folder=ROOT/'models';folder.mkdir(exist_ok=True)
    doc=r.document(body)
    # Graph audit: references can only point to the complete local dependency closure.
    variables={b['id'] for b in doc['body']};ids=[];functions=set()
    def walk(x):
        if isinstance(x,dict):
            if 'ref' in x:assert x['ref']['id'] in variables
            if 'func' in x:ids.append(x['id']);functions.add(x['func'])
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(doc);assert len(ids)==len(set(ids))
    (folder/(r.key+'.recipe.json')).write_text(json.dumps(doc,indent=1),encoding='utf-8')
    vals={'metadata':meta,'parameters':[{**p,'default_design_units':p['contents']['value']['val']/(.001**p['dimension'].get('length',0))} for p in r.parameters],'sections':r.sections,'profile_edges_mm':r.curves,'extrusions':r.extrusions,'field_checks':r.checks,'function_identifiers':sorted(functions),'nodes':len(ids),'output':body['ref']['id']}
    (ROOT/'evidence'/(r.key+'.design.json')).write_text(json.dumps(vals,indent=2),encoding='utf-8')
    checks=[ref(row['name']) for row in r.checks]
    validation=r.hold('Field check values','list<real>',r.node('core.list<real>','list<real>',checks),'Checks')
    (folder/(r.key+'.checks.recipe.json')).write_text(json.dumps(r.document(validation),indent=1),encoding='utf-8')
    return {'case':r.key,'nodes':len(ids),'checks':len(checks),'metadata':meta}

def main():
    global ROOT
    ap=argparse.ArgumentParser();ap.add_argument('--case',choices=['all','enclosure','bracket','ucover','strut','cup'],default='all');ap.add_argument('--out',type=Path,default=ROOT);ap.add_argument('--corner-style',choices=['miter45','rounded'],default='miter45');args=ap.parse_args()
    ROOT=args.out.resolve()
    for name in ['models','evidence']: (ROOT/name).mkdir(parents=True,exist_ok=True)
    cases=['enclosure','bracket','ucover','strut','cup'] if args.case=='all' else [args.case]
    rows=[]
    for key in cases:
        if key=='enclosure':
            from miter_geometry import enclosure_miter
            part=enclosure_miter(sys.modules[__name__]) if args.corner_style=='miter45' else enclosure_round()
        else:part=cup() if key=='cup' else section_part(key)
        rows.append(write_case(*part))
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
