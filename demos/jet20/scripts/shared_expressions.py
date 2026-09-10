"""Promote repeated native expressions to variables without changing their meaning."""
import copy,json,hashlib,collections
def compact(recipe,min_cost=6):
    d=copy.deepcopy(recipe);counts=collections.Counter();examples={};costs={}
    def key(x):
        if isinstance(x,list):return [key(v) for v in x]
        if not isinstance(x,dict):return x
        if 'ref' in x:return {'ref':x['ref']['id'],'props':x.get('props',[])}
        if 'value' in x:return {'type':x['type'],'value':x['value']}
        if 'func' in x:return {'func':x['func'],'type':x['type'],'inputs':key(x['inputs'])}
        return {k:key(v) for k,v in x.items() if k not in ['id','name']}
    def visit(x):
        if isinstance(x,list):return sum(visit(v) for v in x)
        if not isinstance(x,dict):return 0
        n=sum(visit(v) for v in x.values())
        if 'func' in x:
            n+=1;k=hashlib.sha256(json.dumps(key(x),sort_keys=True,separators=(',',':')).encode()).hexdigest()
            counts[k]+=1;examples[k]=x;costs[k]=n;x['_share_key']=k
        return n
    for b in d['body']:visit(b['contents'])
    selected={k for k in counts if counts[k]>1 and costs[k]>=min_cost}
    shared={};new=[]
    def transform(x,skip=None):
        if isinstance(x,list):return [transform(v) for v in x]
        if not isinstance(x,dict):return x
        k=x.get('_share_key')
        if k in selected and k!=skip:
            if k not in shared:
                bid='jet_shared_'+k[:20];shared[k]=bid
                value=transform(examples[k],k)
                new.append({'id':bid,'name':f'SHARED {len(new)+1:03d} '+x['func'].split('<')[0],'contents':value,'type':x['type'],'variable':True})
            return {'ref':{'id':shared[k]},'props':[]}
        return {a:transform(v) for a,v in x.items() if a!='_share_key'}
    for b in d['body']:b['contents']=transform(b['contents'])
    d['body']+=new
    return d,{'helpers':len(new),'repeated_candidates':len(selected)}

def expanded_hashes(recipe):
    by={b['id']:b for b in recipe['body']};cache={}
    def vh(k):
        if k not in cache:cache[k]=walk(by[k]['contents'])
        return cache[k]
    def walk(x):
        if isinstance(x,list):return [walk(v) for v in x]
        if not isinstance(x,dict):return x
        if 'ref' in x:
            source=vh(x['ref']['id'])
            return {'source':source,'props':x['props']} if x.get('props') else source
        if 'value' in x:o={'type':x['type'],'value':x['value']}
        elif 'func' in x:o={'func':x['func'],'inputs':walk(x['inputs'])}
        else:o={k:walk(v) for k,v in x.items() if k not in ['id','name','type']}
        return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {b['name']:vh(b['id']) for b in recipe['body']}
