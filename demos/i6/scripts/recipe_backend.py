"""A stand-in for the console's `notebook` that records a recipe instead.

`engine.build` drives the Notebook API through a handful of calls:
add_block, set_block_input, connect_block_property, clear_block_input,
add_variable, append_to_list, plus section and listing calls. Against the
live API every one of those costs ~0.5 s once the notebook holds a few
hundred variables, so a full engine is an hour of round trips. Against
this class the same code runs in milliseconds and produces one recipe
JSON that `import_recipe` loads in a single call.

The encoding mirrors what `export_as_recipe` writes on build 42594
(see docs/API_NOTES.md and _agent/partial_engine.json):

  literal real      {"type":"real","value":{"isFinite":true,"units":{"length":1},"val":0.043}}
  literal point     {"type":"point","value":[{"isFinite":true,"val":0},{...},{...}]}        metres
  literal vector    {"type":"vector","value":{"units":{},"value":[{...},{...},{...}]}}
  enum              {"type":"blend_enum","value":{"enum":0}}
  reference         {"props":["negative"],"ref":{"id":"inst12"}}          props = property hops
  nested block      {"func":"cylinder<point,point,real>","id":...,"inputs":[...],"name":...,"type":"cylinder"}
  variable          {"contents": <block or value or ref>, "id":..., "name":..., "type":..., "variable": true}

A `core.var<T>` block is a variable whose contents are its input directly;
exports carry no `func: core.var<T>` form, so this class does the same.

Limits: a property hop is only allowed on a variable (make the block a
variable first), and every `core.var<T>` must end up named with
add_variable. Both are asserted.
"""

import json

MM = 1e-3

# Input order per identifier, with the default used when the build leaves
# an input untouched. None means "must be provided"; a leftover None fails
# validation, which is what catches a missed wire.
_ZERO_POINT = {"type": "point", "value": [{"isFinite": True, "val": 0.0}] * 3}
_Z_AXIS = {"type": "vector", "value": {"units": {}, "value": [{"isFinite": True, "val": 0.0},
                                                             {"isFinite": True, "val": 0.0},
                                                             {"isFinite": True, "val": 1.0}]}}
_BLEND = {"type": "blend_enum", "value": {"enum": 0}}
_ZERO_LEN = {"type": "real", "value": {"isFinite": True, "units": {"length": 1}, "val": 0.0}}

SPEC = {
    "cylinder<point,point,real>": (["Point 1", "Point 2", "Radius"], [_ZERO_POINT, None, None], "cylinder"),
    "box_from_corners<point,point>": (["Point 1", "Point 2"], [None, None], "box"),
    "sphere<point,real>": (["Center Point", "Radius"], [_ZERO_POINT, None], "sphere"),
    "torus<point,vector,real,real>": (["Center", "Axis", "Radius", "Torus Radius"], [_ZERO_POINT, _Z_AXIS, None, None], "torus"),
    "cone<point,point,real,real>": (["Point 1", "Point 2", "Radius 1", "Radius 2"], [_ZERO_POINT, None, None, None], "cone"),
    "boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]": (["Blend Type", "Blend Radius", "Bodies"], [_BLEND, _ZERO_LEN, "list<implicit>"], "implicit"),
    "boolean_subtract<blend_enum,real_field,implicit,list<implicit>>[5.44.0]": (["Blend Type", "Blend Radius", "Primary Body", "Subtraction Bodies"], [_BLEND, _ZERO_LEN, None, "list<implicit>"], "implicit"),
    "boolean_intersect<blend_enum,real_field,list<implicit>>[5.44.0]": (["Blend Type", "Blend Radius", "Bodies"], [_BLEND, _ZERO_LEN, "list<implicit>"], "implicit"),
    "translate<spatial3d,vector>": (["Object", "Vector"], [None, None], "@object"),
    "rotate<spatial3d,point,vector,real>[1.1.0]": (["Object", "Rotation Center", "Axis", "Angle"], [None, _ZERO_POINT, None, None], "@object"),
    "array_implicit<implicit,vector,vector>[1.1.0]": (["Body", "Count", "Spacing"], [None, None, None], "implicit"),
    "polar_array_implicit<implicit,real,integer,axis>": (["Body", "Angular Spacing", "Count", "Axis"], [None, None, None, None], "implicit"),
    "plane_from_normal<point,vector>[1.1.0]": (["Origin", "Normal"], [_ZERO_POINT, _Z_AXIS], "plane"),
    "axis<point,vector>": (["Point", "Vector"], [_ZERO_POINT, _Z_AXIS], "axis"),
    "point<real,real,real>": (["X", "Y", "Z"], [_ZERO_LEN, _ZERO_LEN, _ZERO_LEN], "point"),
    "vector<real,real,real>": (["X", "Y", "Z"], [None, None, None], "vector"),
    "polyline<list<point>>[5.20.0]": (["Points"], [None], "polycurve"),
    "core.var<real_field>": (["Input"], [None], "real_field"),
    "multiply<real_field,real_field>": (["Operand A", "Operand B"], [None, None], "real_field"),
    "add<real_field,real_field>": (["Operand A", "Operand B"], [None, None], "real_field"),
    "subtract<real_field,real_field>": (["Operand A", "Operand B"], [None, None], "real_field"),
    "divide<real_field,real_field>": (["Operand A", "Operand B"], [None, None], "real_field"),
    "atan2<real_field,real_field>": (["Operand A", "Operand B"], [None, None], "real_field"),
    "mod<real_field,real_field>": (["Operand A", "Operand B"], [None, None], "real_field"),
    "sqrt<real_field>": (["Operand"], [None], "real_field"),
    "thicken_implicit<implicit,real_field>": (["Body", "Thickness"], [None, None], "implicit"),
    "core.var<real>": (["Input"], [None], "real"),
    "core.var<implicit>": (["Input"], [None], "implicit"),
    "core.var<point>": (["Input"], [None], "point"),
    "core.var<bounding_box>": (["Input"], [None], "bounding_box"),
    "mesh_from_implicit_body_2<implicit,real>": (["Body", "Tolerance"], [None, None], "mesh"),
    "export_mesh<file_path,mesh,unit_length_enum>": (["Path", "Mesh", "Units"], [None, None, {"type": "unit_length_enum", "value": {"id": "mm"}}], "mesh_file_data"),
    "add<real,real>": (["Operand A", "Operand B"], [None, None], "real"),
    "subtract<real,real>": (["Operand A", "Operand B"], [None, None], "real"),
    "multiply<real,real>": (["Operand A", "Operand B"], [None, None], "real"),
    "divide<real,real>": (["Operand A", "Operand B"], [None, None], "real"),
    "max<real,real>": (["Operand A", "Operand B"], [None, None], "real"),
    "sin<real>": (["Operand"], [None], "real"),
    "cos<real>": (["Operand"], [None], "real"),
    "asin<real>": (["Operand"], [None], "real"),
    "acos<real>": (["Operand"], [None], "real"),
    "sqrt<real>": (["Operand"], [None], "real"),
}


# Inputs that natively take a list; connecting a list there does not lift the block.
NATIVE_LIST_INPUTS = {("polyline<list<point>>[5.20.0]", "Points")}


def _fin(x):
    return {"isFinite": True, "val": float(x)}


class RecipeNotebook:
    def __init__(self):
        self.n = 0
        self.entries = []          # top-level body entries in creation order
        self.blocks = {}           # block id -> entry dict (top-level or nested)
        self.top = {}              # block id -> True while at top level
        self.ident = {}            # block id -> identifier
        self.vars = {}             # variable name -> (inst id, type)
        self.var_order = []
        self.sections = [{"name": "Section 1", "id": "section_2"}]
        self.meta = {"displayname": "I6 Engine", "description": ""}
        self.saved_to = None
        self.block_section = {}    # block id -> section id at creation
        self.var_section = {}      # variable name -> section name

    # ---- ids ---------------------------------------------------------------
    def _inst(self):
        self.n += 1
        return "eng%05d" % self.n

    # ---- sections and listings -----------------------------------------
    def new_notebook(self):
        pass

    def list_sections(self):
        return list(self.sections)

    def add_section(self, name, before=""):
        s = {"name": name, "id": "section_%d" % (len(self.sections) + 2)}
        if before:
            i = [x["id"] for x in self.sections].index(before)
            self.sections.insert(i, s)
        else:
            self.sections.append(s)
        return s

    def list_blocks(self, section_id=""):
        return []

    def list_variables(self):
        return [{"id": name, "name": t, "funcId": ""} for name, (_, t) in self.vars.items()]

    def import_recipe(self, path):
        with open(path, encoding="utf-8") as fh:
            rec = json.load(fh)
        for e in rec["body"]:
            self.entries.append(e)
            if e.get("variable"):
                self.vars[e["name"]] = (e["id"], e["type"])
                self.var_section[e["name"]] = "INPUTS"
        self.meta["displayname"] = rec.get("displayname", self.meta["displayname"])
        self.meta["description"] = rec.get("description", self.meta["description"])

    def save_notebook_as(self, path):
        self.saved_to = path

    def save_notebook(self):
        pass

    # ---- blocks ------------------------------------------------------------
    def add_block(self, identifier, section_id=""):
        if identifier not in SPEC:
            raise KeyError("recipe_backend has no spec for %r" % identifier)
        names, defaults, out_type = SPEC[identifier]
        inputs = []
        for d in defaults:
            if d == "list<implicit>":
                inputs.append({"func": "core.list<implicit>", "id": self._inst(), "inputs": [],
                               "name": "Implicit Body List", "type": "list<implicit>"})
            else:
                inputs.append(json.loads(json.dumps(d)) if d is not None else None)
        bid = self._inst()
        entry = {"func": identifier, "id": bid, "inputs": inputs,
                 "name": identifier.split("<")[0].replace("core.var", "Variable").title(), "type": out_type}
        self.blocks[bid] = entry
        self.top[bid] = True
        self.ident[bid] = identifier
        self.block_section[bid] = section_id
        self.entries.append(entry)
        return {"id": bid}

    def _index(self, bid, param):
        names = SPEC[self.ident[bid]][0]
        if param not in names:
            raise KeyError("block %s (%s) has no input %r" % (bid, self.ident[bid], param))
        return names.index(param)

    def _resolve(self, ident_or_name):
        """A variable name -> ('var', inst, type); a block id -> ('block', id, type)."""
        if ident_or_name in self.vars:
            inst, t = self.vars[ident_or_name]
            return "var", inst, t
        if ident_or_name in self.blocks:
            return "block", ident_or_name, self.blocks[ident_or_name]["type"]
        raise KeyError("unknown source %r" % ident_or_name)

    def set_block_input(self, bid, param, value):
        i = self._index(bid, param)
        if isinstance(value, tuple):
            if param in ("Rotation Center", "Origin", "Center Point", "Center", "Point"):
                enc = {"type": "point", "value": [_fin(v * 0.0254) for v in value]}  # display inches -> metres
                # Only zero points are set by tuple in this project, so the
                # unit question never arises; assert it stays that way.
                assert all(v == 0.0 for v in value), "non-zero point literal set via API: %r" % (value,)
            else:
                enc = {"type": "vector", "value": {"units": {}, "value": [_fin(v) for v in value]}}
        else:
            enc = {"type": "real", "value": {"isFinite": True, "units": {}, "val": float(value)}}
        self.blocks[bid]["inputs"][i] = enc

    def _ref(self, src, prop):
        kind, inst, t = self._resolve(src)
        if kind == "var":
            return {"props": [prop] if prop else [], "ref": {"id": inst}}, t
        if prop:
            raise RuntimeError("property %r taken off non-variable block %s; make it a variable first" % (prop, src))
        # nest the block inside its consumer
        entry = self.blocks[inst]
        if self.top.get(inst):
            self.entries.remove(entry)
            self.top[inst] = False
        else:
            raise RuntimeError("block %s consumed twice; make it a variable" % inst)
        return entry, t

    def connect_block_property(self, src, prop, dst, param):
        i = self._index(dst, param)
        enc, t = self._ref(src, prop)
        self.blocks[dst]["inputs"][i] = enc
        ident = self.ident[dst]
        if SPEC[ident][2] == "@object" and param == "Object":
            self.blocks[dst]["type"] = t
        # list processing: a list<T> into a scalar input lifts the block's output
        if (not prop and t.startswith("list<") and (ident, param) not in NATIVE_LIST_INPUTS
                and not self.blocks[dst]["type"].startswith("list<") and not ident.startswith("core.var<")):
            self.blocks[dst]["type"] = "list<%s>" % self.blocks[dst]["type"]

    def clear_block_input(self, bid, param):
        self.blocks[bid]["inputs"][self._index(bid, param)] = None

    def append_to_list(self, src, dst, list_param):
        i = self._index(dst, list_param)
        lst = self.blocks[dst]["inputs"][i]
        assert isinstance(lst, dict) and lst.get("func") == "core.list<implicit>"
        enc, _ = self._ref(src, "")
        lst["inputs"].append(enc)

    def add_variable(self, name, bid):
        if name in self.vars:
            raise RuntimeError("duplicate variable %r" % name)
        entry = self.blocks[bid]
        if not self.top.get(bid):
            raise RuntimeError("block %s already consumed; cannot make it variable %r" % (bid, name))
        idx = self.entries.index(entry)
        t = entry["type"]
        if t == "@object":
            raise RuntimeError("transform %s has no Object wired" % bid)
        if self.ident[bid].startswith("core.var<"):
            contents = entry["inputs"][0]
            if contents is None:
                raise RuntimeError("variable %r has no input" % name)
            if isinstance(contents, dict) and "ref" in contents and not contents.get("props"):
                src_t = next((tt for (_i, tt) in self.vars.values() if _i == contents["ref"]["id"]), None)
                if src_t and src_t.startswith("list<"):
                    t = src_t
        else:
            contents = entry
        var_entry = {"contents": contents, "id": self._inst(), "name": name, "type": t, "variable": True}
        self.entries[idx] = var_entry
        self.top[bid] = False
        self.vars[name] = (var_entry["id"], t)
        self.var_order.append(name)
        sid = self.block_section.get(bid, "")
        self.var_section[name] = next((x["name"] for x in self.sections if x["id"] == sid), "OTHER")
        return {"id": name, "funcId": self.ident[bid]}

    def get_block_input(self, bid, param):
        return 0.0

    # ---- output ----------------------------------------------------------------
    def validate(self):
        problems = []

        def walk(node, path):
            if isinstance(node, dict):
                if "func" in node:
                    for k, inp in enumerate(node["inputs"]):
                        if inp is None:
                            problems.append("%s/%s input %d (%s) unset" % (path, node["func"], k, SPEC[node["func"]][0][k] if node["func"] in SPEC else "?"))
                        else:
                            walk(inp, path + "/" + node["name"])
                elif "ref" in node:
                    if node["ref"]["id"] not in ids:
                        problems.append("%s dangling ref %s" % (path, node["ref"]["id"]))
                elif "contents" in node:
                    walk(node["contents"], path + "/" + node["name"])

        ids = set()
        for e in self.entries:
            ids.add(e["id"])
        for e in self.entries:
            walk(e, e.get("name", "?"))
            if not e.get("variable") and self.ident.get(e["id"], "").startswith("core.var<"):
                problems.append("unnamed core.var block %s" % e["id"])
            if e.get("type") == "@object":
                problems.append("transform %s type unresolved" % e["id"])
        return problems

    def write(self, path):
        problems = self.validate()
        if problems:
            raise RuntimeError("recipe not valid:\n  " + "\n  ".join(problems[:20]))
        rec = {
            "body": self.entries,
            "cbRefs": [],
            "description": self.meta["description"],
            "displayname": self.meta["displayname"],
            "imports": [],
            "inputs": [],
            "name": "user_func_i6_engine_full_0000_0000_000000000000",
            "namespaces": [],
            "version": [1, 0, 0],
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=1)
        return {"path": path, "entries": len(self.entries), "variables": len(self.vars),
                "top_level_blocks": sum(1 for e in self.entries if not e.get("variable"))}
