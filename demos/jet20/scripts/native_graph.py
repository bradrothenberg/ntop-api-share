"""Small original SI recipe author for the nTop Notebook API.

Only native nTop blocks are emitted. The engine uses implicit geometry.
Motion and DOE display recipes can import the engine's own native mesh exports.
Input signatures are checked against the catalog captured from the live API.
"""
import json
import math
from pathlib import Path

IDS = {
 'cyl':('cylinder<point,point,real>','cylinder'),
 'box':('box_from_corners<point,point>','box'),
 'sphere':('sphere<point,real>','sphere'),
 'torus':('torus<point,vector,real,real>','torus'),
 'cone':('cone<point,point,real,real>','cone'),
 'union':('boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]','implicit'),
 'sub':('boolean_subtract<blend_enum,real_field,implicit,list<implicit>>[5.44.0]','implicit'),
 'inter':('boolean_intersect<blend_enum,real_field,list<implicit>>[5.44.0]','implicit'),
 'translate':('translate<spatial3d,vector>','implicit'),
 'rotate':('rotate<spatial3d,point,vector,real>[1.1.0]','implicit'),
 'array':('array_implicit<implicit,vector,vector>[1.1.0]','implicit'),
 'polar':('polar_array_implicit<implicit,real,integer,axis>','implicit'),
 'axis':('axis<point,vector>','axis'),
 'point':('point<real,real,real>','point'),
 'vector':('vector<real,real,real>','vector'),
 'mesh':('mesh_from_implicit_body_2<implicit,real>','mesh'),
 'mesh_at':('mesh_by_adaptive_tets<implicit,real_field,bool>[5.42.0]','mesh'),
 'sharpen':('sharpen_mesh<mesh,implicit,integer,mesh_sharpen_enum>','mesh'),
 'split_mesh':('split_mesh<mesh>[1.1.0]','list<mesh>'),
 'filter_meshes':('filter_mesh_list<list<mesh>,real>','list<mesh>'),
 'merge_meshes':('merge<list<mesh>>','mesh'),
 'spline':('spline_by_control_points<list<point>,integer>[5.20.0]','spline'),
 'offset':('offset_implicit<implicit,real_field>','implicit'),
 'thicken':('thicken_implicit<implicit,real_field>','implicit'),
 'scale':('scale_object<spatial3d,real,point>[1.2.0]','implicit'),
 'import_mesh':('import_mesh<file_path,unit_length_enum>[1.1.0]','mesh'),
 'export':('export_mesh<file_path,mesh,unit_length_enum>','mesh_file_data'),
 'profile':('profile_from_points<list<point>>[5.20.0]','new_profile'),
 'extrude':('extrude<new_profile,real,real,bool,vector>[5.20.0]','implicit'),
}

def real(v,unit='length'):
    return {'type':'real','value':{'isFinite':True,'units':({unit:1} if unit else {}),
                                  'val':float(v)*(0.001 if unit=='length' else math.pi/180 if unit=='angle' else 1)}}

def literal(t,v): return {'type':t,'value':v}
def finite(x): return {'isFinite':True,'val':float(x)}

class Graph:
    def __init__(self):
        self.body=[]; self.k=0; self.layout={'sections':[],'variables':{},'final_bodies':{}}
        self.section='00 Design inputs'; self.parts=[]
        self.routes=[]
    def uid(self):
        self.k+=1; return 'astra_%06d'%self.k
    def node(self,key,*inputs):
        func,t=IDS[key]
        return {'func':func,'id':self.uid(),'inputs':list(inputs),'name':key.title(),'type':t}
    def math(self,op,*args,field=False):
        t='real_field' if field else 'real'
        return {'func':op+'<'+','.join([t]*len(args))+'>','id':self.uid(),'inputs':list(args),'name':op.title(),'type':t}
    def var(self,name,value,t=None):
        if any(b['name']==name for b in self.body): raise ValueError(name)
        entry={'contents':value,'id':self.uid(),'name':name,'type':t or value.get('type','implicit'),'variable':True}
        self.body.append(entry)
        if self.section not in self.layout['sections']: self.layout['sections'].append(self.section)
        self.layout['variables'][name]=self.section
        return {'props':[],'ref':{'id':entry['id']}}
    def prop(self,ref,name): return {'ref':ref['ref'],'props':[name]}
    def param(self,name,v,unit='length'): return self.var(name,real(v,unit),'real')
    def pt(self,p):
        if not any(isinstance(x,dict) for x in p): return literal('point',[finite(x*.001) for x in p])
        return self.node('point',*[x if isinstance(x,dict) else real(x) for x in p])
    def vec(self,p,dim=True):
        if not any(isinstance(x,dict) for x in p):
            return literal('vector',{'units':{'length':1} if dim else {},'value':[finite(x*(.001 if dim else 1)) for x in p]})
        return self.node('vector',*[x if isinstance(x,dict) else real(x,'length' if dim else '') for x in p])
    def length(self,r): return r if isinstance(r,dict) else real(r)
    def cyl(self,a,b,r):return self.node('cyl',self.pt(a),self.pt(b),self.length(r))
    def box(self,a,b):return self.node('box',self.pt(a),self.pt(b))
    def sphere(self,c,r):return self.node('sphere',self.pt(c),self.length(r))
    def cone(self,a,b,r,s):return self.node('cone',self.pt(a),self.pt(b),self.length(r),self.length(s))
    def torus(self,c,axis,r,t):return self.node('torus',self.pt(c),self.vec(axis,False),self.length(r),self.length(t))
    def lst(self,bodies):return {'func':'core.list<implicit>','id':self.uid(),'inputs':list(bodies),'name':'Bodies','type':'list<implicit>'}
    def union(self,*bodies):
        return self.node('union',literal('blend_enum',{'enum':0}),real(0),self.lst(bodies))
    def sub(self,body,*tools):return self.node('sub',literal('blend_enum',{'enum':0}),real(0),body,self.lst(tools))
    def inter(self,*bodies):return self.node('inter',literal('blend_enum',{'enum':0}),real(0),self.lst(bodies))
    def move(self,body,p):return self.node('translate',body,self.vec(p))
    def rot(self,body,deg,axis=(1,0,0),center=(0,0,0)):
        return self.node('rotate',body,self.pt(center),self.vec(axis,False),deg if isinstance(deg,dict) else real(deg,'angle'))
    def array(self,body,count,spacing):return self.node('array',body,self.vec(count,False),self.vec(spacing))
    def polar(self,body,n,axis=(1,0,0),center=(0,0,0)):
        return self.node('polar',body,real(360/n,'angle'),literal('integer',{'val':n}),self.node('axis',self.pt(center),self.vec(axis,False)))
    def tube(self,a,b,ro,ri):
        v=[b[i]-a[i] for i in range(3)]; L=math.sqrt(sum(x*x for x in v)); u=[x/L for x in v]
        return self.sub(self.cyl(a,b,ro),self.cyl([a[i]-u[i] for i in range(3)],[b[i]+u[i] for i in range(3)],ri))
    def capsule(self,a,b,r):return self.union(self.cyl(a,b,r),self.sphere(a,r),self.sphere(b,r))
    def path(self,points,r):
        return self.union(*[self.cyl(a,b,r) for a,b in zip(points,points[1:])],*[self.sphere(p,r) for p in points])
    def pipe(self,points,ro,ri):
        # Extend the bore beyond both rounded outer endpoints. Otherwise the
        # difference of two capsule paths silently produces a closed vessel.
        a,b=points[0],points[1];c,d=points[-2],points[-1]
        ua=[b[i]-a[i] for i in range(3)];ub=[d[i]-c[i] for i in range(3)]
        la=math.sqrt(sum(v*v for v in ua));lb=math.sqrt(sum(v*v for v in ub))
        start=[a[i]-(ro+2)*ua[i]/la for i in range(3)]
        end=[d[i]+(ro+2)*ub[i]/lb for i in range(3)]
        return self.sub(self.path(points,ro),self.path([start]+list(points)+[end],ri))
    def prism(self,points,distance,direction=(1,0,0)):
        pts={'func':'core.list<point>','id':self.uid(),'inputs':[self.pt(p) for p in points],
             'name':'Profile points','type':'list<point>'}
        return self.node('extrude',self.node('profile',pts),real(distance),real(0,'angle'),
                         literal('bool',{'val':False}),self.vec(direction,False))
    def spline_curve(self,name,points):
        pts={'func':'core.list<point>','id':self.uid(),'inputs':[self.pt(p) for p in points],
             'name':name+' control points','type':'list<point>'}
        return self.var(name,self.node('spline',pts,literal('integer',{'val':3})),'spline')
    def spline_route(self,name,points,outer_radius,inner_radius=0,trim=True):
        curve=self.spline_curve(name+' centerline',points)
        field=self.var(name+' distance field',self.prop(curve,'scalar field'),'implicit')
        result=self.node('offset',field,real(outer_radius))
        if inner_radius:result=self.sub(result,self.node('offset',field,real(inner_radius)))
        if trim:
            caps=[]
            for label,p,q,sign in [('start',points[0],points[1],-1),('end',points[-1],points[-2],-1)]:
                # Remove only the endpoint cap. A global halfspace intersection
                # also cuts distant sections of a hose that doubles back.
                v=[-sign*(q[i]-p[i]) for i in range(3)];n=math.sqrt(sum(a*a for a in v));v=[a/n for a in v]
                plane={'func':'plane_from_normal<point,vector>[1.1.0]','id':self.uid(),
                       'inputs':[self.pt(p),self.vec(v,False)],'name':name+' '+label+' trim','type':'plane'}
                ref=self.var(name+' '+label+' plane',plane,'plane')
                caps.append(self.inter(self.sphere(p,outer_radius*1.05),self.prop(ref,'body')))
            result=self.sub(result,*caps)
        self.routes.append({'name':name,'control_points_mm':points,'degree':3,'outer_radius_mm':outer_radius,
                            'inner_radius_mm':inner_radius,'end_planes':trim,'centerline_id':curve['ref']['id']})
        return result
    def gear(self,n,module,width,bore,backlash=.12):
        # 20 degree unshifted full-depth involute. Tooth thickness includes backlash.
        rp=module*n/2; rb=rp*math.cos(math.radians(20)); ra=rp+module; rf=rp-1.25*module
        inv=lambda a: math.tan(a)-a
        half=math.pi/(2*n)-backlash/(2*rp)
        coords=[]
        for sign,rev in [(-1,False),(1,True)]:
            rs=[max(rb,rf)+(ra-max(rb,rf))*i/14 for i in range(15)]
            flank=[]
            for r in rs:
                a=half+inv(math.radians(20))-inv(math.acos(min(1,rb/r)))
                flank.append((0,r*math.sin(sign*a),r*math.cos(sign*a)))
            roota=half+inv(math.radians(20))
            flank=[(0,(rf-.3)*math.sin(sign*roota),(rf-.3)*math.cos(sign*roota))]+flank
            coords.extend(reversed(flank) if rev else flank)
        tooth=self.prism(coords,width)
        gear=self.union(self.cyl((0,0,0),(width,0,0),rf),self.polar(tooth,n))
        return self.sub(gear,self.cyl((-1,0,0),(width+1,0,0),bore))
    def sharp_mesh(self,body,tolerance):
        mesh=self.node('mesh_at',body,real(tolerance),literal('bool',{'val':False}))
        return self.node('sharpen',mesh,body,literal('integer',{'val':1}),literal('mesh_sharpen_enum',{'enum':0}))
    def part(self,name,body,color,system,**meta):
        self.section=system; ref=self.var(name,body,'implicit')
        self.layout['final_bodies'][name]=list(color)+[1.0]
        self.parts.append({'name':name,'id':ref['ref']['id'],'system':system,'color':color,**meta})
        return ref
    def recipe(self,body=None):
        return {'body':self.body if body is None else body,'cbRefs':[],'description':'Original preliminary inline-six engine. SI units. Geometry authored through the nTop Notebook API.',
                'displayname':'I6 Astra | 3.2 L preliminary design','imports':[],'inputs':[],
                'name':'user_func_astra_41669005_3e62_4334_ba5c_640ee10b3434','namespaces':[],'version':[1,0,0]}
    def closure(self,ids):
        by={x['id']:x for x in self.body}; needed=set()
        def visit(x):
            if isinstance(x,dict):
                if 'ref' in x:
                    rid=x['ref']['id']
                    if rid not in needed: needed.add(rid); visit(by[rid])
                else:
                    for v in x.values():visit(v)
            elif isinstance(x,list):
                for v in x:visit(v)
        for rid in ids:
            needed.add(rid);visit(by[rid])
        return [x for x in self.body if x['id'] in needed]
    def write(self,path):
        Path(path).write_text(json.dumps(self.recipe(),indent=1),encoding='utf-8')
