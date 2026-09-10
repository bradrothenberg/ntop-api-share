"""Run engine.build against a mock notebook to catch Python-level mistakes offline."""
import sys, os, json, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

class Mock:
    def __init__(self):
        self.n = 0; self.sections = [{"name": "Section 1", "id": "section_2"}]
        self.vars = []; self.calls = collections.Counter(); self.consumed = set(); self.inputs = {}
    def _c(self, k): self.calls[k] += 1
    def new_notebook(self): self._c("new_notebook")
    def list_sections(self): return list(self.sections)
    def add_section(self, name, before=""):
        s = {"name": name, "id": "section_%d" % (len(self.sections) + 2)}
        if before: i = [x["id"] for x in self.sections].index(before); self.sections.insert(i, s)
        else: self.sections.append(s)
        return s
    def import_recipe(self, path):
        for e in json.load(open(path, encoding="utf-8"))["body"]:
            self.vars.append({"id": e["name"], "name": e["type"]})
    def list_variables(self): return list(self.vars)
    def list_blocks(self, sid): return []
    def add_block(self, ident, sid):
        self.n += 1; self._c("add_block"); assert sid, "no section"; return {"id": "blk%d" % self.n}
    def set_block_input(self, bid, param, value):
        self._c("set"); assert isinstance(value, (float, tuple)), (bid, param, value)
        if isinstance(value, tuple): assert len(value) == 3
    def connect_block_property(self, sid, prop, dst, param):
        self._c("connect")
        assert isinstance(sid, str) and isinstance(dst, str), (sid, dst)
        key = (dst, param)
        if key in self.inputs and self.inputs[key] == "value": raise RuntimeError("already has a value")
        self.inputs[key] = sid
        if prop == "": self.consumed.add(sid)
    def clear_block_input(self, bid, param): self._c("clear"); self.inputs.pop((bid, param), None)
    def append_to_list(self, src, dst, lst): self._c("append"); assert isinstance(src, str); self.consumed.add(src)
    def add_variable(self, name, bid):
        self._c("add_variable"); assert not any(v["id"] == name for v in self.vars), "dup " + name
        self.vars.append({"id": name, "name": "?"}); return {"id": name, "funcId": "x"}
    def save_notebook_as(self, p): self._c("save_as")
    def save_notebook(self): self._c("save")
    def get_block_input(self, bid, param): return 0.0

import engine
nb = Mock()
s = engine.build(nb)
print(json.dumps({k: v for k, v in s.items() if k != "section_seconds"}, indent=1))
print(dict(nb.calls))
# reuse analysis: any block id used as a source twice that is not a variable?
src_counts = collections.Counter(v for v in nb.inputs.values())
varset = {v["id"] for v in nb.vars}
multi = [(k, c) for k, c in src_counts.items() if c > 1 and k not in varset]
print("non-variable sources used more than once:", multi[:10])
print("variables:", len(nb.vars))
