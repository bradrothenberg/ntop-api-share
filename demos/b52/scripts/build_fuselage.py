"""Rebuild the final editable R7 recipe from its complete, audited source graph.

The graph is the source of every native block, literal, and connection. Edit
inputs/final_recipe.json to change it. No earlier project or private notebook
is needed. Numerical guide and cap inputs accompany the graph for analysis.
"""
from pathlib import Path
import copy,json
ROOT=Path(__file__).resolve().parents[1]
def build():
    recipe=json.loads((ROOT/'inputs/final_recipe.json').read_text())
    out=ROOT/'output/build';out.mkdir(parents=True,exist_ok=True)
    (out/'final_recipe.json').write_text(json.dumps(recipe,indent=2))
    return recipe
if __name__=='__main__':build()
