"""Build and stage an import for an empty nTop notebook."""
import argparse
from project import ROOT,JOBS
from build import build
def main():
    p=argparse.ArgumentParser();p.add_argument('demo',choices=JOBS);a=p.parse_args();recipe=build(a.demo)
    out=ROOT/'.local/staged'/a.demo;out.mkdir(parents=True,exist_ok=True)
    script=out/'import_model.py'
    code='\n'.join(['from pathlib import Path','import json,time',f'source=Path({str(recipe)!r})',f'out=Path({str(out)!r})',
      "if notebook.list_variables():raise RuntimeError('Open an empty scratch notebook first.')",
      'start=time.time()','notebook.import_recipe(str(source))',"notebook.save_notebook_as(str(out/'Model-working.ntop'))",
      "notebook.export_as_recipe(str(out/'readback.json'))",
      "(out/'receipt.json').write_text(json.dumps({'seconds':time.time()-start,'variables':len(notebook.list_variables()),'scope':'imported; geometry readback still required'},indent=2))"])
    script.write_text(code+'\n',encoding='utf8')
    print('Run in the nTop Python Console:')
    print(f"exec(compile(open({str(script)!r},encoding='utf-8').read(),{str(script)!r},'exec'))")
if __name__=='__main__':main()
