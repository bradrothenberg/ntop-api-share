"""Run each registered build and validate every complete recipe."""
import json,os,subprocess,sys,time
from project import ROOT,JOBS,prepare
def main():
    prepare();rows=[]
    for demo in JOBS:
        start=time.monotonic()
        run=subprocess.run([sys.executable,str(ROOT/'scripts/build.py'),demo],cwd=ROOT,env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True,encoding='utf8',errors='replace',timeout=115)
        (ROOT/'.local'/f'{demo}-smoke.log').write_text(run.stdout+run.stderr,encoding='utf8')
        row={'demo':demo,'returncode':run.returncode,'seconds':round(time.monotonic()-start,3)};rows.append(row);print(json.dumps(row),flush=True)
        if run.returncode:print(run.stderr[-2500:]);break
    result={'passed':len(rows)==len(JOBS) and all(r['returncode']==0 for r in rows),'runs':rows,'scope':'offline source builders; no new native execution'}
    (ROOT/'.local/smoke.json').write_text(json.dumps(result,indent=2),encoding='utf8');return not result['passed']
if __name__=='__main__':raise SystemExit(main())
