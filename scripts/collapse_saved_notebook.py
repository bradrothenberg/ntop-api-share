"""Collapse saved nTop block/section UI state without touching model chunks.

Prototype MAGIC%$1 container only. Write a separate file; retain the source.
Files without saved UI chunks are copied unchanged.
Run with uv run python collapse_saved_notebook.py source.ntop -o final.ntop.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

def unpack(raw):
    if raw[:8] != b'MAGIC%$1' or len(raw)<104:
        raise ValueError('Unrecognized nTop container; do not patch this build')
    count=struct.unpack_from('<Q',raw,8)[0]
    first_chunk=104+24*count
    if count==0 or first_chunk>=len(raw):raise ValueError('Invalid chunk directory size')
    chunks=[];offset=first_chunk
    while offset<len(raw):
        head=raw[offset:offset+128]
        if len(head)!=128 or head[:8]!=b'MAGIC@@9':
            raise ValueError('Invalid chunk header')
        name=head[24:40].rstrip(b'\0').decode()
        size=struct.unpack_from('<Q',head,40)[0];end=offset+128+size
        if end>len(raw):raise ValueError('Truncated chunk')
        chunks.append((name,head,raw[offset+128:end],end-first_chunk));offset=end
    if len(chunks)!=count:raise ValueError('Chunk directory count mismatch')
    if len({c[0] for c in chunks})!=len(chunks):raise ValueError('Duplicate chunk names')
    ends={c[0]:c[3] for c in chunks}
    for i,pos in enumerate(range(24,24+24*count,24)):
        name=raw[pos:pos+16].rstrip(b'\0').decode()
        if name!=chunks[i][0]:raise ValueError('Chunk table name mismatch')
        if struct.unpack_from('<Q',raw,pos+16)[0]!=ends[name]:
            raise ValueError('Chunk table offset mismatch')
    return bytearray(raw[:first_chunk]),chunks

def collapse(source,output):
    source=Path(source).resolve();output=Path(output).resolve()
    if source==output:raise ValueError('Use a separate output file; retain the API-saved source')
    raw=source.read_bytes();header,chunks=unpack(raw);lookup={c[0]:c for c in chunks}
    states=json.loads(lookup['open'][2]) if 'open' in lookup else []
    sections=json.loads(lookup['sections'][2]) if 'sections' in lookup else {'decorations':[]}
    if not isinstance(states,list) or not isinstance(sections.get('decorations'),list):
        raise ValueError('Unrecognized UI-state schema')
    changed=0;blocks=0
    for row in states:
        if not isinstance(row.get('collapsed'),bool) or not isinstance(row.get('relativePath'),str):
            raise ValueError('Unrecognized block expansion record')
        if not row['relativePath'].startswith('100_'):raise ValueError('Unrecognized root path')
        # 100_ is the root notebook group, not an authored block.
        if row['relativePath']=='100_':continue
        changed+=not row['collapsed'];row['collapsed']=True;blocks+=1
    for row in sections['decorations']:
        if not isinstance(row.get('collapse'),bool):raise ValueError('Unrecognized section expansion record')
        row['collapse']=True
    updates={}
    if 'open' in lookup:updates['open']=json.dumps(states,separators=(',',':')).encode()
    if 'sections' in lookup:updates['sections']=json.dumps(sections,separators=(',',':')).encode()
    body=[];ends={};size=0
    for name,head,payload,_ in chunks:
        if name in updates:
            payload=updates[name];head=bytearray(head);struct.pack_into('<Q',head,40,len(payload))
        piece=bytes(head)+payload;body.append(piece);size+=len(piece);ends[name]=size
    for pos in range(24,24+24*len(chunks),24):
        name=header[pos:pos+16].rstrip(b'\0').decode()
        struct.pack_into('<Q',header,pos+16,ends[name])
    result=bytes(header)+b''.join(body)
    _,checked=unpack(result)
    for (name,head,payload,_),(newname,newhead,newpayload,_) in zip(chunks,checked):
        assert name==newname
        if name not in updates:assert head==newhead and payload==newpayload,name
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(result)
    assert output.read_bytes()==result and source.read_bytes()==raw
    return {'blocks_collapsed':blocks,'block_flags_changed':changed,'sections_collapsed':len(sections['decorations']),
      'root_container_preserved':True,'non_UI_chunks_byte_identical':True,'source_unchanged':True,
      'output':str(output),'sha256':hashlib.sha256(result).hexdigest()}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('-o','--output',required=True)
    args=p.parse_args();print(json.dumps(collapse(args.source,args.output),indent=2))
