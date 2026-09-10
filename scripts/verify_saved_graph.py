"""Compare saved API graphs against native functions, wiring, literals, and units.

This checks graph correspondence without evaluating geometry or the nTop API.
"""
import json
from project import ROOT as R
from organize_notebook import read_file
from prepare import walk

def compare(demo,filename):
 h,ch=read_file(R/'demos'/demo/'models'/filename);leaves=list(walk(ch));fn=json.loads(next(c.payload for c in leaves if c.name=='fn'));vals=json.loads(next(c.payload for c in leaves if c.name=='index'))
 vals={int(x['id']):{k:v for k,v in x.items() if k!='id'} for x in vals};nodes={x['id']:x for x in fn['code']};variables={i:x for i,x in nodes.items() if x['func'].startswith('core.var<')}
 def native_edge(x):
  i=x['instanceId'];v={'ref':variables[i]['name']} if i in variables else native_node(i)
  return {'base':v,'props':x['propchain']} if x.get('propchain') else v
 def native_node(i):
  x=nodes[i]
  if not x['func']:return vals[i]
  return {'func':x['func'],'type':x['type'],'inputs':[native_edge(v) for v in x['inputs']]}
 recipe=json.loads((R/'demos'/demo/'inputs/recipe.json').read_text());names={v['id']:v['name'] for v in recipe['body']}
 def canon(x):
  if isinstance(x,dict):
   if 'ref' in x:
    v={'ref':names[x['ref']['id']]};return {'base':v,'props':x['props']} if x.get('props') else v
   return {k:canon(v) for k,v in x.items() if k not in ['id','name']}
  if isinstance(x,list):return [canon(v) for v in x]
  return x
 expected={v['name']:canon(v['contents']) for v in recipe['body']};actual={v['name']:native_edge(v['inputs'][0]) for v in variables.values()}
 wrong=[]
 for name,expect in expected.items():
  if actual.get(name)!=expect:wrong.append({'name':name,'recipe':expect,'native':actual.get(name)})
 result={'demo':demo,'model':filename,'variables':len(expected),'matched':len(expected)-len(wrong),'mismatched_names':[x['name'] for x in wrong],'extra_native_names':sorted(set(actual)-set(expected)),'scope':'Saved construction functions, connections, properties, types, literal values and units; no native evaluation'}
 return result
