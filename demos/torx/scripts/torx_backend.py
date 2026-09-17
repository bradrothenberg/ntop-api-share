"""The recording backend: one graph description, one complete recipe, no nTop.

Same role as `demos/i6/scripts/recipe_backend.py`, with one structural
difference that this demo exists to record.

A backend that implements the live Notebook API calls one for one lets a single
builder drive both transports. The Torx cannot be built that way at all. It is
an assembly of seven referenced custom blocks, and build 42926 has no live
method that creates a custom block: `docs/API_REFERENCE.md` states that the API
edits existing custom blocks and lists no create or import method for one. So
the node-by-node transport cannot express this graph, at any cost in round
trips. The recipe can: a complete recipe carries its definitions in `imports`
and calls them by uuid, and `import_recipe` takes the whole thing in one call.

This backend is therefore a recipe recorder, not a live-API mirror, and nothing
here should be read as evidence that the live setters could reach the same
graph. What it records is the recipe encoding measured from nTop's own
`export_as_recipe` output, ported from the source project's `src/kit/bloc.js`,
`geo.js` and `ref.js`.

Encoding rules carried over from the source method, each bought with a witness:

  U1  literals inside a recipe are SI: {"units":{"angle":1},"val":0.8482} is
      radians, never degrees
  U3  a point call needs units of length on X, Y and Z; a bare 0 converts and
      then fails at execution
  P2  a call made by an imported definition resolves only through the ROOT
      `imports` array, so root imports hold the transitive closure
  P3  within `imports`, a definition may reference only definitions that
      precede it
  P4  a call carries no [x.y.z] revision suffix
  P7  a root-level call to an import needs root `cbRefs` naming its index
  I2  a custom block is referenced by its full uuid, never by name
"""

import json
import math
from pathlib import Path

TWO_PI = 2.0 * math.pi
SQRT1_2 = math.sqrt(0.5)


# --------------------------------------------------------------------------
# literals. A recipe literal is SI (U1); the display-unit convention of the
# live setters is the opposite one and never appears here.
# --------------------------------------------------------------------------
def R(value, units=None):
    return {"type": "real", "value": {"isFinite": True, "units": dict(units or {}),
                                      "val": float(value)}}


def L(value):
    return R(value, {"length": 1})


def A(value):
    return R(value, {"angle": 1})


def I(value):
    return {"type": "integer", "value": {"val": int(value)}}


def B(value):
    return {"type": "bool", "value": {"val": bool(value)}}


def T(text):
    return {"type": "text", "value": {"string": str(text)}}


def V(x, y, z, units=None):
    return {"type": "vector",
            "value": {"units": dict(units or {}),
                      "value": [{"isFinite": True, "val": float(v)} for v in (x, y, z)]}}


def P3(x, y, z):
    return {"type": "point",
            "value": [{"isFinite": True, "val": float(v)} for v in (x, y, z)]}


def X(expression, units=None):
    return {"type": "real_field",
            "value": {"expression": str(expression),
                      "units": {"length": 1} if units is None else dict(units)}}


def E(enum_type, value):
    return {"type": enum_type, "value": {"enum": int(value)}}


def CHOICE(labels, selected=0):
    return {"type": "choice", "value": {"choices": list(labels), "selected": int(selected)}}


# --------------------------------------------------------------------------
# a definition, and how it is called
# --------------------------------------------------------------------------
def signature(definition):
    """The call signature of a definition: name<types>, no revision suffix (P4)."""
    return definition["name"] + "<" + ",".join(i["type"] for i in definition["inputs"]) + ">"


def flatten(definitions):
    """Root `imports`: every definition hoisted before its caller, cbRefs rewritten.

    A definition records the blocks it calls in `_deps`. Dependencies are pushed
    first (P3) and a repeated uuid is pushed once. Only root cbRefs resolve a
    call, so a caller's cbRefs name root indices (P2, P7).
    """
    root, index = [], {}

    def push(d):
        if d["name"] in index:
            return index[d["name"]]
        refs = [push(dep) for dep in d.get("_deps", [])]
        copy = {k: v for k, v in d.items() if not k.startswith("_")}
        copy.pop("imports", None)
        if refs:
            copy["cbRefs"] = refs
        else:
            copy.pop("cbRefs", None)
        index[d["name"]] = len(root)
        root.append(copy)
        return index[d["name"]]

    for d in definitions:
        push(d)
    return root


class Recipe:
    """The recipe context for one block: inputs, body, sections, envelope.

    `inputs` is a list of (name, type, dimension, default, description). A None
    default declares an input with no preview, which is how an implicit-body
    input is passed through.
    """

    def __init__(self, inputs=()):
        self.IN = list(inputs)
        self._index = {row[0]: k for k, row in enumerate(self.IN)}
        self.body = []
        self.sections = []
        self._n = 0
        self._once = 0

    # -- node factory ------------------------------------------------------
    def nid(self):
        self._n += 1
        return "n%d" % self._n

    def F(self, func, inputs, name=None):
        node_id = self.nid()
        return {"func": func, "id": node_id, "name": name or node_id, "inputs": list(inputs)}

    @staticmethod
    def _props(props):
        return list(props) if isinstance(props, (list, tuple)) else []

    def ref(self, node_id, props=None):
        return {"ref": {"id": node_id}, "props": self._props(props)}

    def inp(self, name, props=None):
        if name not in self._index:
            raise KeyError("unknown input: %s" % name)
        return {"input": self._index[name], "props": self._props(props)}

    def sec(self, name, description=" "):
        self.sections.append({"name": name, "start": len(self.body),
                              "description": description or " "})

    def VAR(self, var_id, name, var_type, contents):
        self.body.append({"id": var_id, "name": name, "type": var_type,
                          "variable": True, "contents": contents})
        return self.ref(var_id)

    def PUT(self, node):
        self.body.append(node)
        return self.ref(node["id"])

    def once(self, value, name=None, var_type="real"):
        """One node object may appear in one place; a value used twice becomes a
        named variable and is returned as a reference."""
        if isinstance(value, dict) and "func" in value:
            self._once += 1
            return self.VAR("_k%d" % self._once, name or ("value %d" % self._once),
                            var_type, value)
        return value

    # -- arithmetic --------------------------------------------------------
    def add(self, a, b):
        return self.F("add<real,real>", [a, b])

    def sub(self, a, b):
        return self.F("subtract<real,real>", [a, b])

    def mul(self, a, b):
        return self.F("multiply<real,real>", [a, b])

    def div(self, a, b):
        return self.F("divide<real,real>", [a, b])

    def neg(self, a):
        return self.mul(a, R(-1))

    def fadd(self, a, b):
        return self.F("add<real_field,real_field>", [a, b])

    def fsub(self, a, b):
        return self.F("subtract<real_field,real_field>", [a, b])

    def fmul(self, a, b):
        return self.F("multiply<real_field,real_field>", [a, b])

    def fdiv(self, a, b):
        return self.F("divide<real_field,real_field>", [a, b])

    def fmax(self, a, b):
        return self.F("max<real_field,real_field>", [a, b])

    def fmin(self, a, b):
        return self.F("min<real_field,real_field>", [a, b])

    def sin(self, a):
        return self.F("sin<real>", [a])

    def cos(self, a):
        return self.F("cos<real>", [a])

    def abs(self, a):
        return self.F("abs<real>", [a])

    def sqrt(self, a):
        return self.F("sqrt<real>", [a])

    def atan2(self, a, b):
        return self.F("atan2<real,real>", [a, b])

    def lt(self, a, b):
        return self.F("less_than<real,real>", [a, b])

    def AND(self, a, b):
        return self.F("and<bool,bool>", [a, b])

    def OR(self, a, b):
        return self.F("or<bool,bool>", [a, b])

    def eq(self, a, b):
        return self.F("equals<real,real>", [a, b if isinstance(b, dict) else R(b)])

    def IF(self, condition, a, b):
        return self.F("core.if<bool,any,1>", [condition, a, b])

    # -- objects -----------------------------------------------------------
    def PT(self, x, y, z):
        return self.F("point<real,real,real>", [x, y, z])

    def LIST(self, item_type, items):
        return self.F("core.list<%s>" % item_type, list(items))

    def SBB(self, field, box):
        return self.F("set_bounding_box<real_field,bounding_box>[1.1.0]", [field, box])

    def REMAP(self, field, x, y, z):
        return self.F("remap<real_field,real_field,real_field,real_field>", [field, x, y, z])

    def EVF(self, field, points):
        return self.F("evaluate_field<real_field,list<point>>",
                      [field, self.LIST("point", points)])

    # -- geometry ----------------------------------------------------------
    def pt(self, x, y, z):
        """A point call. Every component must carry units of length (U3)."""
        lv = lambda v: L(v) if isinstance(v, (int, float)) else v
        return self.PT(lv(x), lv(y), lv(z))

    def axisZ(self):
        return self.F("axis<point,vector>", [P3(0, 0, 0), V(0, 0, 1)])

    def bbox(self, p0, p1):
        return self.F("create_bounding_box<point,point>", [p0, p1])

    def frame(self, origin, ax, ay):
        return self.F("frame<point,vector,vector>", [origin, ax, ay])

    def cyl(self, p1, p2, radius):
        return self.F("cylinder<point,point,real>", [p1, p2, radius])

    def revolve(self, profile, axis, angle=TWO_PI):
        return self.F("revolve<new_profile,axis,real>[5.20.0]",
                      [profile, axis, angle if isinstance(angle, dict) else A(angle)])

    def extrude(self, profile, distance, direction, symmetric=False, draft=0.0):
        return self.F("extrude<new_profile,real,real,bool,vector>[5.20.0]",
                      [profile, distance, draft if isinstance(draft, dict) else A(draft),
                       B(symmetric), direction])

    def translate(self, body, vector):
        return self.F("translate<spatial3d,vector>", [body, vector])

    def vector(self, x, y, z):
        return self.F("vector<real,real,real>", [x, y, z])

    def cross(self, a, b):
        return self.F("cross_product<vector,vector>", [a, b])

    def line(self, a, b):
        return self.F("two_point_line<point,point>", [a, b])

    def arc(self, a, b, c):
        return self.F("three_point_arc<point,point,point>", [a, b, c])

    def profile_from_curves(self, curves, normal):
        return self.F("profile_from_curves<list<curve_interface>,vector>[5.20.0]",
                      [self.LIST("curve_interface", curves), normal])

    # -- booleans. The [5.44.0] sharp family is exactly min / max / max(f,-g),
    #    which is what the mirror in torx_spec.py composes (rule G3/G4).
    def unionS(self, bodies):
        return self.F("boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]",
                      [E("blend_enum", 2), X("0"), self.LIST("implicit", bodies)])

    def subtractS(self, body, tools):
        return self.F("boolean_subtract<blend_enum,real_field,implicit,list<implicit>>[5.44.0]",
                      [E("blend_enum", 2), X("0"), body, self.LIST("implicit", tools)])

    # -- calling a referenced custom block ---------------------------------
    def call(self, definition, args, name=None):
        if len(args) != len(definition["inputs"]):
            raise ValueError("%s: %d arguments for %d inputs (%s)"
                             % (signature(definition), len(args), len(definition["inputs"]),
                                ", ".join(i["name"] for i in definition["inputs"])))
        node_id = self.nid()
        return {"func": signature(definition), "id": node_id,
                "name": name or definition.get("displayname") or node_id,
                "inputs": list(args)}

    # -- the envelope ------------------------------------------------------
    def envelope(self, name, displayname, description, output_id,
                 imports=None, cb_refs=None):
        inputs = []
        for row in self.IN:
            nm, tp, dim, default, desc = row
            entry = {"name": nm, "type": tp, "description": desc or ""}
            if dim:
                entry["dimension"] = dict(dim)
            if default is not None:
                entry["contents"] = default
            inputs.append(entry)
        recipe = {"name": name, "displayname": displayname, "description": description,
                  "inputs": inputs, "body": list(self.body), "output": {"id": output_id},
                  "namespaces": [], "version": [1, 0, 0]}
        if imports:
            recipe["imports"] = list(imports)
            recipe["cbRefs"] = list(cb_refs) if cb_refs is not None \
                else list(range(len(imports)))
        return recipe

    def sections_json(self, extra=()):
        secs = self.sections + list(extra)
        return {"decorations": [{"collapse": False, "description": s["description"],
                                 "name": s["name"]} for s in secs],
                "poles": [s["start"] for s in secs] + [len(self.body)]}


# --------------------------------------------------------------------------
# validation: what a recipe must satisfy before it is worth dispatching
# --------------------------------------------------------------------------
def validate(recipe):
    """Structural checks that cost nothing and catch what convert would refuse."""
    problems = []
    ids = set()
    imports = recipe.get("imports", [])
    names = [d["name"] for d in imports]

    for k, d in enumerate(imports):
        for j in d.get("cbRefs", []):
            if j >= k:
                problems.append("P3: import %d (%s) references import %d, which does not "
                                "precede it" % (k, d["displayname"], j))
            if j >= len(imports):
                problems.append("import %d (%s) cbRefs %d is out of range"
                                % (k, d["displayname"], j))

    def walk(node, path, definition):
        if isinstance(node, dict):
            if "func" in node:
                func = node["func"]
                if func.startswith("user_func_"):
                    base = func.split("<", 1)[0]
                    if "[" in func:
                        problems.append("P4: %s carries a revision suffix on a call" % path)
                    allowed = [names[j] for j in definition.get("cbRefs", [])] \
                        if definition is not None else \
                        [names[j] for j in recipe.get("cbRefs", [])]
                    if base not in allowed:
                        problems.append("P2/P7: %s calls %s, which its cbRefs do not name"
                                        % (path, base))
                for k, sub in enumerate(node["inputs"]):
                    if sub is None:
                        problems.append("%s: %s input %d unset" % (path, func, k))
                    else:
                        walk(sub, path + "/" + str(node.get("name", "?")), definition)
            elif "ref" in node:
                if node["ref"]["id"] not in ids:
                    problems.append("%s: dangling ref %s" % (path, node["ref"]["id"]))
            elif "contents" in node:
                walk(node["contents"], path + "/" + str(node.get("name", "?")), definition)
            elif "value" in node and node.get("type") == "real":
                if node["value"].get("val") is None:
                    problems.append("X3: %s carries a null literal" % path)
        elif isinstance(node, list):
            for sub in node:
                walk(sub, path, definition)

    for definition in imports + [recipe]:
        ids = {e["id"] for e in definition["body"] if "id" in e}
        d = definition if definition is not recipe else None
        for entry in definition["body"]:
            walk(entry, "%s/%s" % (definition.get("displayname", "root"),
                                   entry.get("name", "?")), d)
        out = definition.get("output", {}).get("id")
        if out and out not in ids:
            problems.append("%s: output %s names no body entry"
                            % (definition.get("displayname", "root"), out))
    return problems


def count_nodes(node):
    if isinstance(node, dict):
        return ("func" in node) + sum(count_nodes(v) for v in node.values())
    if isinstance(node, list):
        return sum(count_nodes(v) for v in node)
    return 0


def write(recipe, path, sections=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(recipe, indent=1), encoding="utf8")
    if sections is not None:
        sib = path.with_suffix("")
        Path(str(sib) + ".sections.json").write_text(json.dumps(sections, indent=1),
                                                     encoding="utf8")
    return path
