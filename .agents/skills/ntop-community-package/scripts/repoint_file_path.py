"""Swap a file_path value inside a saved .ntop without disturbing anything else.

A notebook's external input paths live in the MAGIC%$1 `main` chunk as JSON, not in
the recipe export, so a recipe round trip never carries them and a re-save in nTop
rewrites state chunks that were not the point. This rewrites the one string, repacks
the container, and then proves every other chunk is byte-identical.

  uv run python repoint_file_path.py source.ntop -o out.ntop \
      --from D:/Private/thing.implicit --to thing.implicit

Container layout is the one scripts/organize_notebook.py documents and
scripts/collapse_saved_notebook.py repacks; this reuses both.
"""
import argparse,hashlib,json,struct,sys
from pathlib import Path

def unpack(raw):
    if raw[:8]!=b'MAGIC%$1' or len(raw)<104:raise ValueError('Unrecognized nTop container')
    count=struct.unpack_from('<Q',raw,8)[0];first=104+24*count
    if count==0 or first>=len(raw):raise ValueError('Invalid chunk directory size')
    chunks=[];offset=first
    while offset<len(raw):
        head=raw[offset:offset+128]
        if len(head)!=128 or head[:8]!=b'MAGIC@@9':raise ValueError('Invalid chunk header')
        name=head[24:40].rstrip(b'\0').decode();size=struct.unpack_from('<Q',head,40)[0];end=offset+128+size
        if end>len(raw):raise ValueError('Truncated chunk')
        chunks.append((name,head,raw[offset+128:end],end-first));offset=end
    if len(chunks)!=count:raise ValueError('Chunk directory count mismatch')
    ends={c[0]:c[3] for c in chunks}
    for i,pos in enumerate(range(24,24+24*count,24)):
        name=raw[pos:pos+16].rstrip(b'\0').decode()
        if name!=chunks[i][0]:raise ValueError('Chunk table name mismatch')
        if struct.unpack_from('<Q',raw,pos+16)[0]!=ends[name]:raise ValueError('Chunk table offset mismatch')
    return bytearray(raw[:first]),chunks

def repack(header,chunks,updates):
    body=[];ends={};size=0
    for name,head,payload,_ in chunks:
        if name in updates:
            payload=updates[name];head=bytearray(head);struct.pack_into('<Q',head,40,len(payload))
        piece=bytes(head)+payload;body.append(piece);size+=len(piece);ends[name]=size
    for pos in range(24,24+24*len(chunks),24):
        name=header[pos:pos+16].rstrip(b'\0').decode()
        struct.pack_into('<Q',header,pos+16,ends[name])
    return bytes(header)+b''.join(body)

def node_ids(payload,old):
    """Report which file_path nodes carry this value, from the surrounding JSON."""
    found=[]
    marker=b'"type":"file_path","value":{"val":"'+old
    start=0
    while True:
        at=payload.find(marker,start)
        if at<0:return found
        head=payload.rfind(b'{"id":"',max(0,at-64),at)
        found.append(payload[head+7:payload.find(b'"',head+7)].decode() if head>=0 else '<unknown>')
        start=at+1

def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('source');p.add_argument('-o','--output',required=True)
    p.add_argument('--from',dest='old',required=True,help='exact current value')
    p.add_argument('--to',dest='new',required=True,help='replacement value')
    p.add_argument('--chunk',default='main',help='chunk holding the value (default main)')
    a=p.parse_args()
    source=Path(a.source).resolve();output=Path(a.output).resolve()
    if source==output:p.error('Write a separate output file; retain the source')
    raw=source.read_bytes();header,chunks=unpack(raw);lookup={c[0]:c for c in chunks}
    if a.chunk not in lookup:p.error(f'No {a.chunk} chunk in this container')
    payload=lookup[a.chunk][2]
    old=a.old.encode('utf8');new=a.new.encode('utf8')
    marker=b'"type":"file_path","value":{"val":"'
    hits=payload.count(marker+old+b'"')
    if hits!=1:p.error(f'Expected exactly one file_path with that value, found {hits}')
    ids=node_ids(payload,old)
    updated=payload.replace(marker+old+b'"',marker+new+b'"')
    result=repack(header,chunks,{a.chunk:updated})
    _,checked={},None
    checked_header,checked_chunks=unpack(result)
    if len(checked_chunks)!=len(chunks):raise SystemExit('Chunk count changed')
    for (name,head,before,_),(cname,chead,after,_) in zip(chunks,checked_chunks):
        if name!=cname:raise SystemExit('Chunk order changed')
        if name==a.chunk:
            if after!=updated:raise SystemExit('Edited chunk did not round trip')
        elif head!=chead or before!=after:
            raise SystemExit(f'Chunk {name} is not byte-identical')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(result)
    if source.read_bytes()!=raw:raise SystemExit('Source changed during the edit')
    print(json.dumps({'source':str(source),'output':str(output),'chunk':a.chunk,'nodes':ids,
      'old':a.old,'new':a.new,'source_bytes':len(raw),'output_bytes':len(result),
      'other_chunks_byte_identical':True,'chunks':len(chunks),
      'source_sha256':hashlib.sha256(raw).hexdigest(),
      'output_sha256':hashlib.sha256(result).hexdigest()},indent=2))
    return 0

if __name__=='__main__':sys.exit(main())
