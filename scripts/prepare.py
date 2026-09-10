"""Prepare runtime folders and separate native working copies."""
import argparse,json
from project import ROOT,prepare,resolve
from organize_notebook import read_file,write_file
def walk(chunks):
    for c in chunks:
        if c.children is not None:yield from walk(c.children)
        else:yield c
def relocate(source,target):
    if source.resolve()==target.resolve():raise ValueError('Retain the source model')
    header,chunks=read_file(source)
    if write_file(header[:],chunks)!=source.read_bytes():raise ValueError('Container roundtrip failed')
    changed=0
    def replace(x):
        nonlocal changed
        if isinstance(x,dict):return {k:replace(v) for k,v in x.items()}
        if isinstance(x,list):return [replace(v) for v in x]
        if isinstance(x,str) and x.startswith('repo://'):changed+=1;return resolve(x)
        return x
    for c in walk(chunks):
        if c.typ.lower()=='json':
            data=json.loads(c.payload);before=changed;data=replace(data)
            if changed!=before:c.payload=json.dumps(data,separators=(',',':')).encode()
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(write_file(header,chunks));return changed
def main():
    p=argparse.ArgumentParser();p.add_argument('--models',action='store_true');a=p.parse_args();prepare();rows=[]
    if a.models:
        for source in sorted((ROOT/'demos').glob('*/models/*.ntop')):
            target=ROOT/'.local/models'/source.relative_to(ROOT/'demos')
            if target.exists():continue
            rows.append({'model':source.relative_to(ROOT).as_posix(),'paths_resolved':relocate(source,target)})
    print(json.dumps({'prepared':True,'new_working_models':rows},indent=2))
if __name__=='__main__':main()
