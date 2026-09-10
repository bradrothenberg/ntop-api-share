"""Audit only publishable files; inspect native, gzip, and embedded data too."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import argparse,base64,gzip,hashlib,json,re,subprocess,sys,zlib
from project import ROOT
SKIP={'.git','.local','.venv','.uv-cache','__pycache__','.pytest_cache','node_modules','output'}
PATTERNS={
 'personal-home':re.compile(rb'[A-Za-z]:[\\/]+Users[\\/]+[^\s\x00"<>]{2,}',re.I),
 'original-workspace':re.compile(rb'(?:[A-Za-z]:[\\/]+nTop[\\/]+(?:Notebook API Demos|ntop-api(?:[\\/]|[\x00"\s])))',re.I),
 'private-repository':re.compile(rb'github\.com[/\\]+nTopology[/\\]+(?:ntop-falcon|brad-ntop-notebook-api|ntop-api)\b',re.I),
 'retired-dependency':re.compile(rb'FalconAero|falcon_spec|falcon_deck',re.I),
 'private-key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
 'service-token':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,})\b'),
 'credential-assignment':re.compile(rb'(?i)(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*["\x27][A-Za-z0-9_+/=-]{16,}["\x27]'),
 'jwt':re.compile(rb'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\b'),
 'authenticated-url':re.compile(rb'https?://[^\s/:<>]+:[^\s/@<>]+@',re.I),
 'private-ip':re.compile(rb'\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b'),
}
def files():
    # When a commit exists, use its exact tracked manifest. Before Git init, use the explicit output tree.
    if (ROOT/'.git').exists():
        run=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True,check=True)
        return [ROOT/p for p in run.stdout.decode().split('\0') if p]
    return [p for p in ROOT.rglob('*') if p.is_file() and not SKIP.intersection(p.relative_to(ROOT).parts)]
def native_leaves(chunks):
    for c in chunks:
        if c.children is not None:yield from native_leaves(c.children)
        else:yield c
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set();self.embedded=[];self.remote_assets=[];self.script_type=None;self.script_text=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script':self.script_type=a.get('type');self.script_text=[]
        if 'id' in a:self.ids.add(a['id'])
        for key in ['href','src','poster']:
            val=a.get(key,'')
            if not val:continue
            if val.startswith('data:') and ';base64,' in val:
                self.embedded.append(base64.b64decode(val.split(',',1)[1]))
            else:
                self.links.append(val)
                if tag in ('img','script','link','video','source') and val.startswith(('http:','https:')):self.remote_assets.append(val)
    def handle_data(self,data):
        if self.script_type=='application/octet-stream':self.script_text.append(data)
    def handle_endtag(self,tag):
        if tag=='script':
            if self.script_type=='application/octet-stream':
                self.embedded.append(base64.b64decode(''.join(self.script_text).strip(),validate=True))
            self.script_type=None;self.script_text=[]

def inspect(root=ROOT):
    candidates=files();findings=[];native=[];embedded_count=0;gzip_count=0;links_count=0;image_count=0
    def flag(file,kind,detail):findings.append({'file':file,'kind':kind,'detail':detail})
    def scan(label,raw):
        nonlocal gzip_count,image_count
        for kind,pattern in PATTERNS.items():
            match=pattern.search(raw)
            if match and not (label=='scripts/audit.py' and kind=='retired-dependency'):flag(label,kind,'byte '+str(match.start()))
        # Search common UTF-16 text paths without dumping arbitrary payloads.
        if b'\x00' in raw:
            compact=raw.replace(b'\x00',b'')
            for kind in ('personal-home','original-workspace','private-repository','service-token'):
                m=PATTERNS[kind].search(compact)
                if m:flag(label,kind+'-utf16','encoded string')
        if raw.startswith(b'\x1f\x8b'):
            gzip_count+=1;scan(label+'::gzip',gzip.decompress(raw))
        if raw.startswith(b'\x89PNG'):
            image_count+=1;pos=8
            while pos+12<=len(raw):
                size=int.from_bytes(raw[pos:pos+4],'big');kind=raw[pos+4:pos+8];data=raw[pos+8:pos+8+size]
                if kind in (b'eXIf',):flag(label,'image-metadata','EXIF chunk requires review')
                if kind==b'tEXt':scan(label+'::metadata',data)
                if kind==b'zTXt':scan(label+'::metadata',zlib.decompress(data.split(b'\x00',1)[1][1:]))
                if kind==b'iTXt':
                    keyword,rest=data.split(b'\x00',1);compressed=rest[0];text=rest[2:].split(b'\x00',2)[2]
                    scan(label+'::metadata',zlib.decompress(text) if compressed else text)
                pos+=size+12
        if raw.startswith(b'\xff\xd8'):
            image_count+=1
            if b'Exif\x00\x00' in raw:flag(label,'image-metadata','EXIF requires review')
    for p in candidates:
        rel=p.relative_to(ROOT).as_posix();raw=p.read_bytes();scan(rel,raw)
        if len(raw)>50*1024*1024:flag(rel,'large-file',str(len(raw)))
        if p.suffix.lower() in {'.exe','.msi','.dll','.pem','.key','.mp4','.zip'}:flag(rel,'excluded-file-type',p.suffix)
        if p.suffix=='.py':
            try:compile(raw,str(p),'exec')
            except SyntaxError as e:flag(rel,'python-syntax',str(e))
        if p.suffix=='.ntop':
            from organize_notebook import read_file,write_file
            try:
                header,chunks=read_file(p)
                if write_file(header[:],chunks)!=raw:raise ValueError('Non-exact container roundtrip')
                count=0
                for c in native_leaves(chunks):
                    scan(rel+'::'+c.name,c.payload)
                    if c.typ.lower()=='json':json.loads(c.payload);count+=1
                native.append({'file':rel,'json_chunks':count,'roundtrip':True})
            except Exception as e:flag(rel,'native-container',str(e))
        if p.suffix.lower() in {'.md','.html'}:
            t=raw.decode('utf-8-sig')
            if p.suffix=='.html':
                parser=Links();parser.feed(t);links=parser.links
                for i,data in enumerate(parser.embedded):scan(rel+f'::embedded-{i}',data);embedded_count+=1
                for asset in parser.remote_assets:flag(rel,'remote-report-asset',asset)
                # Embedded compressed geometry can live in JSON/script strings rather than data URLs.
                for i,m in enumerate(re.finditer(r'["\x27](H4sI[A-Za-z0-9+/=]{64,})["\x27]',t)):
                    try:scan(rel+f'::encoded-gzip-{i}',base64.b64decode(m[1]))
                    except Exception as e:flag(rel,'invalid-gzip',str(e))
            else:links=re.findall(r'\[[^\]]*\]\(([^)]+)\)',t)
            for link in links:
                if link.startswith(('http:','https:','mailto:','data:','javascript:')):continue
                path=unquote(urlsplit(link.strip('<>')).path)
                if not path:continue
                links_count+=1
                if not (p.parent/path).is_file():flag(rel,'missing-link',path)
    return {'files':len(candidates),'bytes':sum(p.stat().st_size for p in candidates),'native_notebooks':native,
            'embedded_payloads':embedded_count,'gzip_payloads':gzip_count,'images_scanned':image_count,'local_links':links_count,'findings':findings,
            'scope':'Pattern checks, native roundtrips, resource links, image metadata, and embedded/compressed payloads. Visual/provenance review is recorded separately.'}
def main():
    result=inspect();out=ROOT/'.local/audit.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='native_notebooks'},indent=2));return bool(result['findings'])
if __name__=='__main__':raise SystemExit(main())
