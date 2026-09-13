"""Extract a complete variable graph from these saved notebooks, without evaluation."""
import copy
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from organize_notebook import read_file
from verify_recipe import verify


def extract(source, name):
    _,chunks=read_file(Path(source))
    main=next(c for c in chunks if c.name=='main')
    fn=json.loads(main.find('fn').payload)
    nodes={n['id']:n for n in fn['code']}
    literals={int(v['id']):{k:x for k,x in v.items() if k!='id'} for v in json.loads(main.find('leaves').find('index').payload)}
    variables={i:n for i,n in nodes.items() if n['func'].startswith('core.var<')}
    if any(n['func'].startswith('user_func') for n in nodes.values()):
        raise ValueError('Custom block dependency requires separate packaging')
    if fn.get('dependencies') or fn.get('externalDependencies'):
        raise ValueError('Inspect nonempty notebook dependencies before extracting')
    def edge(e):
        i=e['instanceId']
        if i==0:return None
        if i in variables:return {'ref':{'id':str(i)},'props':copy.deepcopy(e.get('propchain',[]))}
        result=node(i)
        if e.get('propchain'):
            result['props']=copy.deepcopy(e['propchain'])
        return result
    def node(i):
        n=nodes[i]
        if not n['func']:return copy.deepcopy(literals[i])
        return {'func':n['func'],'id':str(i),'name':n['name'],'type':n['type'],'inputs':[edge(e) for e in n['inputs']]}
    body=[]
    for i,n in variables.items():
        if len(n['inputs'])!=1:raise ValueError('Expected one variable input')
        body.append({'id':str(i),'name':n['name'],'type':n['type'],'variable':True,'contents':edge(n['inputs'][0])})
    result={'displayname':name,'description':'Recorded native construction graph. Replay requires build 42926.','name':'user_func_shared_propeller',
            'inputs':[],'namespaces':[],'version':[1,0,0],'body':body}
    verify(result)
    return result
