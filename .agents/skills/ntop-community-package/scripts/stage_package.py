"""Stage a Utilities-community package folder from audited files.

Copies the named files under kebab-case names, records SHA-256 for every copy,
diffs the MAGIC%$1 chunk directory of each .ntop against its audited source, and
writes manifest.json, README.md, LICENSE and publication-checks.json with TODO
markers wherever a human claim is required. It never invents a claim.

  uv run python stage_package.py --author Cortex78 --id torx-custom-blocks \
      --into D:/ntop_dev/Utilities-community \
      --file demos/torx/models/Torx.ntop=torx-custom-blocks.ntop \
      --cover demos/torx/reports/assets/torx_recess_wall.png

Pass --audited PUBLISHEDNAME=PATH when the published copy differs from the file
that was audited, which is the normal case after export paths are rewritten.
"""
import argparse,hashlib,json,re,shutil,struct,sys
from datetime import date
from pathlib import Path

TODO='TODO'
MIT="""MIT License

Copyright (c) {year} {holder}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def kebab(name):
    stem,dot,ext=name.rpartition('.')
    if not dot:stem,ext=name,''
    slug=re.sub(r'[^a-z0-9]+','-',stem.lower()).strip('-')
    return slug+('.'+ext.lower() if ext else '')

def rel(path):
    """Record a source location without publishing a workstation path."""
    try:return Path(path).resolve().relative_to(Path.cwd()).as_posix()
    except ValueError:return Path(path).name

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()

def chunks(path):
    """Return {chunk name: sha256 of payload} for a MAGIC%$1 container, else None."""
    raw=Path(path).read_bytes()
    if raw[:8]!=b'MAGIC%$1' or len(raw)<104:return None
    count=struct.unpack_from('<Q',raw,8)[0]
    first=104+24*count
    if count==0 or first>=len(raw):return None
    out={};offset=first
    while offset<len(raw):
        head=raw[offset:offset+128]
        if len(head)!=128 or head[:8]!=b'MAGIC@@9':return None
        name=head[24:40].rstrip(b'\0').decode('utf8','replace')
        size=struct.unpack_from('<Q',head,40)[0];end=offset+128+size
        if end>len(raw):return None
        out[name]=hashlib.sha256(raw[offset+128:end]).hexdigest();offset=end
    return out if len(out)==count else None

# Measured on a 6.1.0-rc 42926 save: everything else in the directory is graph or input data.
STATE_CHUNKS={'cache','customColors','open','res','sections','tools','view','viewport'}

def changed_chunks(published,audited):
    a,b=chunks(audited),chunks(published)
    if a is None or b is None:return None
    names=sorted(set(a)|set(b))
    return [n for n in names if a.get(n)!=b.get(n)]

def split(pair):
    src,sep,dest=pair.partition('=')
    return Path(src),(dest or kebab(Path(src).name))

def bad_segment(dest):
    """Published paths are kebab-case in every segment; subfolders are allowed."""
    parts=dest.split('/')
    for seg in parts[:-1]:
        if seg!=re.sub(r'[^a-z0-9]+','-',seg.lower()).strip('-'):return seg
    return None if parts[-1]==kebab(parts[-1]) else parts[-1]

def readme(pkg_id,title,all_files,cover):
    files=[f for f in all_files if f.endswith('.ntop')] or all_files
    folders=sorted({f.split('/')[0] for f in all_files if '/' in f})
    lines=[f'# {title}','',f'**Built with {TODO}: name the AI model, or delete this line.**','',
      f'{TODO}: one paragraph saying what this package is and what is in it, with counts.','',
      f'![{title}]({cover})' if cover else f'{TODO}: add a cover image and reference it here.','',
      '## Installation and use','',
      '1. Download the package files and keep them together.',
      f'2. Open `{files[0]}` in the matching licensed nTop build.' if files else f'2. {TODO}: name the file to open.',
      '3. Save a working copy before editing. Expand the relevant section and change one control at a time.',
      '4. Inspect the rebuilt bodies and block states before accepting the changed model.','',
      f'Recorded native build: **{TODO}**. The catalogue version field cannot encode a custom build number. '
      'Public release compatibility has not been re-tested. The application and license are not included.','',
      f'{TODO}: external files. Say where supplied inputs live, what to select if nTop asks for a missing one, '
      'and that export destinations are filenames rather than workstation paths. Delete this paragraph if the '
      'model reads and writes nothing.','',
      '## Inputs and outputs','','| Item | Editable data | Result and limit |','|---|---|---|',
      f'| {TODO} | {TODO} | {TODO} |','',
      f'{TODO}: the limit sentence. State what this package is not, in one sentence a reviewer can check.','',
      '## Files','']
    lines+= [f'- [{f}]({f})' for f in files]
    if folders:lines+=['',f'Supporting folders: {", ".join(folders)}. Keep them beside the notebooks.']
    lines+=['','## Evidence and source','',
      'Publication checks are offline. They record file hashes and container chunk changes. '
      'They do not constitute new native execution. See [publication-checks.json](publication-checks.json).','',
      f'{TODO}: link the exact source commit that holds the construction and verification scope this folder omits.','',
      '## License','',
      f'MIT. See [LICENSE](LICENSE). This license covers the original models and supporting material in this package.','']
    return '\n'.join(lines)

def manifest(pkg_id,author,title):
    return {'id':pkg_id,'type':TODO+': Notebook | Block | Connector | Script | Bundle','title':title,
      'summary':TODO+': one or two sentences, 10 to 240 characters.','author':author,'version':'0.1.0',
      'ntopVersion':TODO+': 6.1 or 5.43+, never a build number','license':'MIT',
      'domain':TODO+': Aerospace | Additive Manufacturing | Medical | Mechanical | Thermal | Simulation | Optimization | Geometry | AI Tools',
      'application':TODO+': Geometry, Analysis, ...','complexity':TODO+': Beginner | Intermediate | Advanced',
      'tags':[TODO+'-lowercase-tag'],'preview':TODO+': geometry | code | graph | bundle'}

def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--author',required=True,help='GitHub handle; becomes the parent folder and manifest author')
    p.add_argument('--id',required=True,help='kebab-case package id; becomes the folder name')
    p.add_argument('--into',required=True,type=Path,help='Utilities-community checkout root')
    p.add_argument('--file',action='append',default=[],metavar='SRC[=NAME]',help='file to publish; repeatable')
    p.add_argument('--cover',type=Path,help='cover image; copied as cover.<ext>')
    p.add_argument('--audited',action='append',default=[],metavar='NAME=PATH',help='audited source of a published file')
    p.add_argument('--title',help='display title; defaults to the id')
    p.add_argument('--holder',help='copyright holder for LICENSE; defaults to the author')
    p.add_argument('--source-commit',help='commit SHA of the repository that produced these files')
    p.add_argument('--force',action='store_true',help='overwrite an existing package folder')
    a=p.parse_args()

    if a.id!=kebab(a.id):p.error(f'--id must be kebab-case; try {kebab(a.id)!r}')
    if not a.file:p.error('at least one --file is required')
    root=a.into/'packages'/a.author/a.id
    if root.exists() and not a.force:p.error(f'{root} exists; pass --force to overwrite its generated files')
    audited={k:Path(v) for k,_,v in (s.partition('=') for s in a.audited)}

    root.mkdir(parents=True,exist_ok=True)
    published=[]
    for pair in a.file:
        src,name=split(pair)
        if not src.is_file():p.error(f'missing source file {src}')
        bad=bad_segment(name)
        if bad is not None:
            # An explicit destination is the author's choice: recorded evidence often has to keep
            # the exact filename its own manifest cites. A derived name must be kebab-case.
            if '=' in pair:print(f'note: {name} is not kebab-case, keeping the name you gave')
            else:p.error(f'published path segment must be kebab-case; {bad!r} in {name!r} for {src}')
        (root/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,root/name);published.append((src,name))
    cover=None
    if a.cover:
        if not a.cover.is_file():p.error(f'missing cover {a.cover}')
        cover='cover'+a.cover.suffix.lower();shutil.copy2(a.cover,root/cover)

    models=[];carried=[]
    for src,name in published:
        source=audited.get(name,src)
        entry={'file':name,'source':rel(source),'source_sha256':sha256(source),
          'published_sha256':sha256(root/name),'bytes':(root/name).stat().st_size}
        if name.endswith('.ntop'):
            diff=changed_chunks(root/name,source)
            if diff is None:
                entry['changed_chunks']=TODO+': not a readable MAGIC%$1 container'
                entry['changed_chunks_are_state_only']=TODO+': container not readable, inspect by hand'
            else:
                entry['changed_chunks']=diff
                entry['changed_chunks_are_state_only']=all(n in STATE_CHUNKS for n in diff)
            entry['relative_export_filenames']=[TODO+': list export destinations, or [] if none']
        entry['source_unchanged']=True
        entry['new_native_execution']=False
        (models if name.endswith('.ntop') else carried).append(entry)

    checks={'scope':'Offline publication preparation; no new native execution','models':models}
    if carried:checks['carried_files']=carried
    if cover:checks['cover_sha256']=sha256(root/cover)
    checks['source_commit']=a.source_commit or TODO+': commit SHA of the repository that produced these files'

    title=a.title or a.id.replace('-',' ').capitalize()
    (root/'publication-checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf8')
    (root/'manifest.json').write_text(json.dumps(manifest(a.id,a.author,title),indent=2)+'\n',encoding='utf8')
    (root/'README.md').write_text(readme(a.id,title,[n for _,n in published],cover),encoding='utf8')
    (root/'LICENSE').write_text(MIT.format(year=date.today().year,holder=a.holder or a.author),encoding='utf8')
    if any(e.get('changed_chunks') or 'evidence' in e['file'] for e in models+carried):
        (root/'.gitattributes').write_text('# Preserve audited file bytes and published hashes on every platform.\n'
          '* -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n',encoding='utf8')

    print(f'staged {root}')
    for _,name in published:print(f'  {name}')
    if cover:print(f'  {cover}')
    print('  manifest.json, README.md, LICENSE, publication-checks.json')
    print('Fill every TODO, then run check_package.py on this folder.')
    return 0

if __name__=='__main__':sys.exit(main())
