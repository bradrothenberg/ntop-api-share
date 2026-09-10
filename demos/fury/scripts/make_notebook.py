"""Standalone recipe encoder for the native loft demo."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CATALOG=set(json.loads((ROOT/"inputs/catalog.json").read_text()))

class Recipe:
    def __init__(self):
        self.n=0; self.body=[]; self.variables={}; self.final={}
    def ident(self):
        self.n+=1
        return 'fury%05d'%self.n
    def literal(self,t,value): return {'type':t,'value':value}
    def real(self,x,units=None): return self.literal('real',{'isFinite':True,'val':float(x),'units':units or {}})
    def length(self,x): return self.real(x,{'length':1})
    def point(self,v): return self.literal('point',[{'isFinite':True,'val':float(x)} for x in v])
    def vector(self,v): return self.literal('vector',{'units':{'length':1},'value':[{'isFinite':True,'val':float(x)} for x in v]})
    def enum(self,t,x): return self.literal(t,{'enum':x})
    def call(self,f,t,*inputs):
        assert f in CATALOG,f
        return {'func':f,'id':self.ident(),'inputs':list(inputs),'name':f.split('<')[0],'type':t}
    def list(self,t,values): return self.call('core.list<'+t+'>','list<'+t+'>',*values)
    def var(self,name,t,value,section='Controls'):
        if value.get('props') and t in ('real','real_field'):
            # get_block_input reads a variable's source before applying its
            # property chain. A real computation gives a readable scalar output.
            value=self.call('add<'+t+','+t+'>',t,value,self.length(0))
        e={'contents':value,'id':self.ident(),'name':name,'type':t,'variable':True}
        self.body.append(e);self.variables[name]=section
        return {'ref':{'id':e['id']},'props':[]}
    def prop(self,ref,prop): return {'ref':ref['ref'],'props':[prop]}
    def boxchecks(self,name,body):
        box=self.var('CHECK '+name+' box','bounding_box',self.prop(body,'bounding box'),'Checks')
        for corner in ['min point','max point']:
            point=self.var('CHECK '+name+' '+corner,'point',self.prop(box,corner),'Checks')
            for ax in 'xyz':self.var('CHECK '+name+' '+corner+' '+ax,'real',self.prop(point,ax),'Checks')
    def write(self,stem):
        rec={'body':self.body,'description':'Native conic and implicit-spline appearance study. Dimensions are demonstration design choices.','displayname':'Fury - Editable Exterior','inputs':[],'name':'user_func_5b3181c3_1a84_448c_924a_9ccb68378a23','namespaces':[],'version':[1,0,0]}
        (ROOT/'output/_agent'/f'{stem}.json').write_text(json.dumps(rec,indent=2))
        layout={'sections':['Controls','Fuselage shape controls','Editable exterior','Display details','Checks'],'variables':self.variables,'final_bodies':self.final}
        (ROOT/'output/_agent'/f'{stem}_layout.json').write_text(json.dumps(layout,indent=2))
        print(stem,len(self.body),'variables')
