"""Build one complete recipe without launching nTop."""
import argparse,json,subprocess,sys,time
from project import ROOT,JOBS,prepare
def build(demo):
    prepare();base=ROOT/'demos'/demo;scripts=base/'scripts'
    start=time.monotonic()
    for name in JOBS[demo][0]:
        args=['-c','import engine; engine.make_recipe()'] if name=='-engine' else [str(scripts/name)]
        subprocess.run([sys.executable,*args],cwd=scripts,check=True,timeout=115)
    recipe=base/JOBS[demo][1]
    from verify_recipe import verify
    result=verify(json.loads(recipe.read_text(encoding='utf8')))
    result.update(demo=demo,seconds=round(time.monotonic()-start,3),recipe=str(recipe.relative_to(ROOT)))
    (base/'output/build_receipt.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result));return recipe
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('demo',choices=JOBS);a=p.parse_args();build(a.demo)
