"""Native recipe writer using block identifiers measured in FuryModel."""
import json, copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = set(json.loads((ROOT/'inputs/ntop_block_catalog.json').read_text()))

class Recipe:
    def __init__(self):
        self.n=0; self.body=[]; self.sections={}; self.final={}
    def ident(self):
        self.n+=1
        return 'ddgx_%05d'%self.n
    def literal(self,t,v): return {'type':t,'value':v}
    def real(self,v,units=None): return self.literal('real',{'isFinite':True,'val':float(v),'units':units or {}})
    def length(self,v): return self.real(v,{'length':1})
    def point(self,v): return self.literal('point',[{'isFinite':True,'val':float(a)} for a in v])
    def vec(self,v): return self.literal('vector',{'units':{},'value':[{'isFinite':True,'val':float(a)} for a in v]})
    def enum(self,t,v): return self.literal(t,{'enum':v})
    def call(self,f,t,*args):
        assert f in CATALOG, f
        return {'func':f,'id':self.ident(),'name':f.split('<')[0],'type':t,'inputs':list(args)}
    def list(self,t,values): return self.call('core.list<'+t+'>','list<'+t+'>',*values)
    def var(self,name,t,value,section='Construction'):
        assert name not in self.sections, name
        e={'contents':value,'id':self.ident(),'name':name,'type':t,'variable':True}
        self.body.append(e); self.sections[name]=section
        return {'ref':{'id':e['id']},'props':[]}
    def prop(self,ref,p): return {'ref':ref['ref'],'props':[p]}
    def mul(self,a,b):return self.call('multiply<real_field,real_field>','real_field',a,b)
    def add(self,a,b):return self.call('add<real_field,real_field>','real_field',a,b)
    def sub(self,a,b):return self.call('subtract<real_field,real_field>','real_field',a,b)
    def div(self,a,b):return self.call('divide<real_field,real_field>','real_field',a,b)
    def neg(self,a):return self.mul(a,self.real(-1))
    def both(self,*args):return self.call('max<list<real_field>>','real_field',self.list('real_field',args))
    def either(self,*args):return self.call('min<list<real_field>>','real_field',self.list('real_field',args))
    def xy(self,a,b):return self.call('vector_field_2d_from_components<real_field,real_field>[5.31.0]','vector_field_2d',a,b)
    def field(self,axis):
        plane=self.var('Coordinate '+axis+' plane','plane',self.call('plane_from_normal<point,vector>[1.1.0]','plane',self.point([0,0,0]),self.vec([int(a==axis) for a in 'xyz'])),'Coordinates')
        return self.var('Coordinate '+axis,'real_field',self.prop(plane,'scalar field'),'Coordinates')
    def bound(self,body,lo,hi):
        return self.call('set_bounding_box<implicit,bounding_box>','implicit',body,self.call('create_bounding_box<point,point>','bounding_box',self.point(lo),self.point(hi)))
    def blend(self,bodies,radius):
        return self.call('boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]','implicit',self.enum('blend_enum',4),radius,self.list('implicit',bodies))
    def ramp(self,x,a,b,lo=0,hi=1):
        return self.call('ramp<real_field,real_field,real_field,real_field,real_field,continuity_enum>','real_field',x,self.length(a),self.length(b),self.real(lo),self.real(hi),self.enum('continuity_enum',2))
    def write(self,stem,output=None):
        doc={'body':self.body,'description':'DDG(X) 2022 public concept exterior. One-metre normalized hull. Inferred sections and proportions, not production data. Orthographic 99% reference match is unverified.','displayname':'DDG(X) | Public concept reconstruction','inputs':[],'name':'user_func_5aa73c11_1526_47a0_b723_0417111d9dc0','namespaces':[],'version':[1,0,0]}
        # JSON roundtrip breaks shared Python object aliases before assigning IDs.
        doc=json.loads(json.dumps(doc))
        def unique(node):
            if isinstance(node,dict):
                if 'func' in node:node['id']=self.ident()
                for a in node.values():unique(a)
            elif isinstance(node,list):
                for a in node:unique(a)
        unique(doc['body'])
        if output:doc['output']=output['ref']
        dest=ROOT/'output/build'/f'{stem}.json'
        dest.write_text(json.dumps(doc,indent=2))
        layout={'sections':list(dict.fromkeys(self.sections.values())),'variables':self.sections,'final_bodies':self.final}
        (ROOT/'output/build'/f'{stem}_layout.json').write_text(json.dumps(layout,indent=2))
        return doc
