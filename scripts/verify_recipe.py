"""Check graph closure, unique named variables, and finite literals."""
import math
def verify(recipe):
    body=recipe['body'];ids=[b['id'] for b in body];names=[b['name'] for b in body]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate variable IDs')
    if len(names)!=len(set(names)):raise ValueError('Duplicate variable names')
    defined=set(ids);refs=set();functions=set();count=0
    def walk(node):
        nonlocal count
        if isinstance(node,dict):
            if 'ref' in node:refs.add(node['ref']['id'])
            if 'func' in node:functions.add(node['func']);count+=1
            for x in node.values():walk(x)
        elif isinstance(node,list):
            for x in node:walk(x)
        elif isinstance(node,float) and not math.isfinite(node):raise ValueError('Nonfinite recipe literal')
    walk(body)
    if refs-defined:raise ValueError('Unresolved references: '+str(sorted(refs-defined)[:10]))
    return {'variables':len(body),'expressions':count,'functions':len(functions),'references_resolve':True,'scope':'offline graph validation'}
