"""Gate a Utilities-community package folder before the pull request.

Runs everything the catalogue's own validator runs, then everything it does not:
the declared packageFile and coverImage exist, tags are sane, aiModel carries the
ai-assisted tag, README relative links resolve, large files sit in Git LFS, no two
names differ only by case, no staging marker survives, and no workstation path or
credential is left in any byte.

  uv run python check_package.py <catalogue>/packages/<author>/<id> [...]
  uv run python check_package.py --all <catalogue>

Errors exit 1. Warnings are printed and do not fail unless --strict is passed.
"""
import argparse,json,re,subprocess,sys
from pathlib import Path

MAX_BYTES=50*1024*1024
COVER_NAMES={'cover.png','cover.jpg','cover.jpeg','cover.webp','cover.svg','cover.gif'}
MARKER=re.compile(r'\bTODO\b')
LINK=re.compile(r'\[[^\]]*\]\(([^)\s]+)')
# Pattern names follow scripts/audit.py in ntop-api-share; keep the two in step.
SECRETS={
 'personal-home':re.compile(rb'[A-Za-z]:[\\/]+Users[\\/]+[^\s\x00"<>]{2,}',re.I),
 'private-key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
 'service-token':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,})\b'),
 'credential-assignment':re.compile(rb'(?i)(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*["\x27][A-Za-z0-9_+/=-]{16,}["\x27]'),
 'jwt':re.compile(rb'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\b'),
 'authenticated-url':re.compile(rb'https?://[^\s/:<>]+:[^\s/@<>]+@',re.I),
}

def schema_errors(obj,schema,path=''):
    """Port of the draft-07 subset that scripts/validate-manifests.js implements."""
    errs=[]
    t='array' if isinstance(obj,list) else 'null' if obj is None else \
      'boolean' if isinstance(obj,bool) else 'number' if isinstance(obj,(int,float)) else \
      'string' if isinstance(obj,str) else 'object' if isinstance(obj,dict) else type(obj).__name__
    if schema.get('type') and schema['type']!=t:
        return [f"{path or '(root)'}: expected {schema['type']}, got {t}"]
    if 'enum' in schema and obj not in schema['enum']:
        errs.append(f"{path}: {json.dumps(obj)} not in [{', '.join(map(str,schema['enum']))}]")
    if t=='string':
        if schema.get('minLength') is not None and len(obj)<schema['minLength']:errs.append(f"{path}: shorter than {schema['minLength']}")
        if schema.get('maxLength') is not None and len(obj)>schema['maxLength']:errs.append(f"{path}: longer than {schema['maxLength']}")
        if schema.get('pattern') and not re.search(schema['pattern'],obj):errs.append(f"{path}: does not match /{schema['pattern']}/")
    if t=='array':
        if schema.get('minItems') is not None and len(obj)<schema['minItems']:errs.append(f"{path}: fewer than {schema['minItems']} items")
        if schema.get('maxItems') is not None and len(obj)>schema['maxItems']:errs.append(f"{path}: more than {schema['maxItems']} items")
        if schema.get('items'):
            for i,el in enumerate(obj):errs+=schema_errors(el,schema['items'],f'{path}[{i}]')
    if t=='object':
        for key in schema.get('required',[]):
            if key not in obj:errs.append(f"{path or '(root)'}: missing required \"{key}\"")
        for key,sub in schema.get('properties',{}).items():
            if key in obj:errs+=schema_errors(obj[key],sub,f'{path}.{key}' if path else key)
        if schema.get('additionalProperties') is False and schema.get('properties'):
            for key in obj:
                if key not in schema['properties']:errs.append(f"{path or '(root)'}: unknown property \"{key}\"")
    return errs

def catalogue_root(start):
    for d in [start,*start.parents]:
        if (d/'packages'/'_schema'/'manifest.schema.json').is_file():return d
    return None

def lfs_tracked(repo,rel):
    try:
        out=subprocess.run(['git','-C',str(repo),'check-attr','filter','--',rel],
          capture_output=True,text=True,timeout=30)
    except (OSError,subprocess.SubprocessError):return None
    return 'filter: lfs' in out.stdout

def scan_bytes(path):
    try:raw=path.read_bytes()
    except OSError:return []
    return [name for name,pat in SECRETS.items() if pat.search(raw)]

def check(pkg,schema,repo):
    errs,warns=[],[]
    slug,author=pkg.name,pkg.parent.name
    man=pkg/'manifest.json'
    if not man.is_file():return [f'missing manifest.json'],[]
    try:data=json.loads(man.read_text(encoding='utf8'))
    except (OSError,json.JSONDecodeError) as e:return [f'manifest.json: invalid JSON, {e}'],[]

    errs+=schema_errors(data,schema)
    if data.get('id')!=slug:errs.append(f'id "{data.get("id")}" does not match folder slug "{slug}"')
    if data.get('author')!=author:errs.append(f'author "{data.get("author")}" does not match parent folder "{author}"')
    if not (pkg/'README.md').is_file():errs.append('missing README.md')
    if data.get('distribution')=='redirect' and not data.get('redirectUrl'):errs.append('distribution is "redirect" but redirectUrl is missing')

    names=[p.name for p in pkg.iterdir()]
    lower={}
    for n in names:lower.setdefault(n.lower(),[]).append(n)
    for group in lower.values():
        if len(group)>1:errs.append(f'names differ only by case: {", ".join(sorted(group))}')

    for field in ('packageFile','coverImage'):
        declared=data.get(field)
        if declared and not (pkg/declared).is_file():errs.append(f'{field} "{declared}" does not exist in the folder')
    if not data.get('coverImage') and not any(n.lower() in COVER_NAMES for n in names):
        warns.append('no coverImage declared and no cover.{png,jpg,jpeg,webp,svg,gif} found; the catalogue card will have no image')
    if not data.get('packageFile') and data.get('distribution','download')=='download':
        ntop=sorted(n for n in names if n.lower().endswith('.ntop'))
        if len(ntop)>1:warns.append(f'no packageFile declared and {len(ntop)} notebooks present; the catalogue picks one by file order')
        elif not ntop and not any(n.lower().endswith(('.exe','.msi','.zip','.py','.pdf')) for n in names):
            warns.append('no packageFile declared and no obvious downloadable artifact found')

    tags=data.get('tags') or []
    if len(set(tags))!=len(tags):errs.append('duplicate tags')
    if data.get('aiModel') and 'ai-assisted' not in tags:
        errs.append(f'aiModel is "{data["aiModel"]}" but the ai-assisted tag is missing')
    for tag in tags:
        if tag!=tag.lower():warns.append(f'tag "{tag}" is not lowercase')

    for p in sorted(pkg.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(pkg).as_posix()
        if '__pycache__' in p.parts or p.suffix in {'.pyc','.pyo'}:warns.append(f'{rel}: build artefact should not be published')
        if p.stat().st_size>MAX_BYTES:
            tracked=lfs_tracked(repo,p.relative_to(repo).as_posix()) if repo else None
            if tracked is False:errs.append(f'{rel}: {p.stat().st_size//1024//1024} MB and not tracked by Git LFS')
            elif tracked is None:warns.append(f'{rel}: over 50 MB; Git LFS status not checked')
        for hit in scan_bytes(p):errs.append(f'{rel}: contains {hit}')

    for doc in ('README.md','manifest.json','publication-checks.json'):
        f=pkg/doc
        if f.is_file() and MARKER.search(f.read_text(encoding='utf8',errors='replace')):
            errs.append(f'{doc}: still contains a TODO staging marker')

    rm=pkg/'README.md'
    if rm.is_file():
        for target in LINK.findall(rm.read_text(encoding='utf8',errors='replace')):
            if target.startswith(('http://','https://','mailto:','#')):continue
            if not (pkg/target.split('#')[0]).exists():errs.append(f'README.md: broken relative link "{target}"')
    return errs,warns

def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('paths',nargs='+',type=Path,help='package folders, or a catalogue root with --all')
    p.add_argument('--all',action='store_true',help='check every package under the given catalogue root')
    p.add_argument('--strict',action='store_true',help='treat warnings as failures')
    a=p.parse_args()

    targets=[]
    for path in a.paths:
        if a.all:
            base=path/'packages'
            if not base.is_dir():p.error(f'{base} is not a directory')
            targets+=[d for author in sorted(base.iterdir()) if author.is_dir() and not author.name.startswith(('_','.'))
                      for d in sorted(author.iterdir()) if d.is_dir()]
        else:targets.append(path)

    total_e=total_w=0
    for pkg in targets:
        pkg=pkg.resolve()
        repo=catalogue_root(pkg)
        if repo is None:print(f'[FAIL] {pkg}: no packages/_schema/manifest.schema.json above this folder');total_e+=1;continue
        schema=json.loads((repo/'packages'/'_schema'/'manifest.schema.json').read_text(encoding='utf8'))
        errs,warns=check(pkg,schema,repo)
        label=f'{pkg.parent.name}/{pkg.name}'
        if errs:
            print(f'[FAIL] {label}:')
            for e in errs:print(f'  - {e}')
        elif warns:print(f'[WARN] {label}:')
        else:print(f'[OK]   {label}')
        for w in warns:print(f'  ~ {w}')
        total_e+=len(errs);total_w+=len(warns)

    print(f'\n{len(targets)} package(s), {total_e} error(s), {total_w} warning(s).')
    return 1 if total_e or (a.strict and total_w) else 0

if __name__=='__main__':sys.exit(main())
