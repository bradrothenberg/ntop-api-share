"""Build a parametric, moving inline-six engine in an nTop notebook.

Run from the nTop Python Console through the bundled agent harness:

    agent.run(notebook, "engine", "build")        # new notebook, full build, save
    agent.run(notebook, "engine", "checks")       # numeric verification
    agent.run(notebook, "engine", "set_angle", 90.0)
    agent.run(notebook, "engine", "exports")      # per-part STL export blocks

`build` starts with `new_notebook()`, so it must only be pointed at a
scratch notebook.

How the graph is organised
--------------------------
Every dimension is a recipe literal (see demos/i6/scripts/make_engine_recipe.py) so it
carries SI units; the API can only author unit-free numbers. Everything
positional is derived from those literals with live math blocks, so the
model stays parametric: change `Bore Pitch` and the block, head, crank and
cams all follow.

Motion comes from one literal, `Crank Angle`. Per cylinder the slider-crank
equations give pin position, piston height and rod swing; the camshafts
turn at half speed; and each valve's lift is the exact flat-follower lift
of the tangent-cam lobe that drives it, so lobe and bucket stay in contact
at every angle.

API facts this build relies on (all measured, see engine_probe*.py):
  - a block wired into another block nests inside it and leaves the top
    level, so single-use bodies are wired inline and only reused bodies are
    made variables;
  - a plain block's output can feed only ONE input, so anything referenced
    twice is a variable first;
  - property access is one hop, so bounding-box reads chain a variable per
    hop;
  - `rotate` follows the right-hand rule; a plane's `body` is the half-space
    opposite its normal; `array_implicit` extends from the seed in +spacing;
  - display units are inches and degrees, so the API sets only unit-free
    numbers and reads angles back in degrees.
"""

import importlib
import json
import os
import time

import engine_spec as spec

spec = importlib.reload(spec)

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_HERE)
OUT_DIR = os.path.join(ROOT, "output/_agent")
LITERALS = os.path.join(OUT_DIR, "engine_literals.json")
NOTEBOOK_PATH = os.path.join(ROOT, "output", "I6_Engine.ntop")

ID = {
    "cyl": "cylinder<point,point,real>",
    "box": "box_from_corners<point,point>",
    "sphere": "sphere<point,real>",
    "torus": "torus<point,vector,real,real>",
    "cone": "cone<point,point,real,real>",
    "union": "boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]",
    "subtract": "boolean_subtract<blend_enum,real_field,implicit,list<implicit>>[5.44.0]",
    "intersect": "boolean_intersect<blend_enum,real_field,list<implicit>>[5.44.0]",
    "translate": "translate<spatial3d,vector>",
    "rotate": "rotate<spatial3d,point,vector,real>[1.1.0]",
    "array": "array_implicit<implicit,vector,vector>[1.1.0]",
    "polar": "polar_array_implicit<implicit,real,integer,axis>",
    "plane": "plane_from_normal<point,vector>[1.1.0]",
    "axis": "axis<point,vector>",
    "point": "point<real,real,real>",
    "vector": "vector<real,real,real>",
    "var_real": "core.var<real>",
    "var_implicit": "core.var<implicit>",
    "var_point": "core.var<point>",
    "var_bbox": "core.var<bounding_box>",
    "mesh": "mesh_from_implicit_body_2<implicit,real>",
    "polyline": "polyline<list<point>>[5.20.0]",
    "var_field": "core.var<real_field>",
    "fmul": "multiply<real_field,real_field>",
    "fadd": "add<real_field,real_field>",
    "fsub": "subtract<real_field,real_field>",
    "fdiv": "divide<real_field,real_field>",
    "fatan2": "atan2<real_field,real_field>",
    "fmod": "mod<real_field,real_field>",
    "fsqrt": "sqrt<real_field>",
    "thicken": "thicken_implicit<implicit,real_field>",
    "export_mesh": "export_mesh<file_path,mesh,unit_length_enum>",
    "add": "add<real,real>",
    "sub": "subtract<real,real>",
    "mul": "multiply<real,real>",
    "div": "divide<real,real>",
    "max": "max<real,real>",
    "sin": "sin<real>",
    "cos": "cos<real>",
    "asin": "asin<real>",
    "acos": "acos<real>",
    "sqrt": "sqrt<real>",
}


class V:
    """A real-valued source: a block or variable id plus an optional property."""

    __slots__ = ("b", "id", "prop")

    def __init__(self, b, ident, prop=""):
        self.b, self.id, self.prop = b, ident, prop

    def src(self):
        return self.id, self.prop

    def __add__(self, o):
        return self.b.op("add", self, o)

    def __radd__(self, o):
        return self.b.op("add", o, self)

    def __sub__(self, o):
        return self.b.op("sub", self, o)

    def __rsub__(self, o):
        return self.b.op("sub", o, self)

    def __mul__(self, o):
        return self.b.op("mul", self, o)

    def __rmul__(self, o):
        return self.b.op("mul", o, self)

    def __truediv__(self, o):
        return self.b.op("div", self, o)

    def __neg__(self):
        # The "negative" ref property is honoured as a block input but ignored as the
        # direct contents of a core.var (measured 6 Sep 2026), so never hold a
        # property-carrying value: negate an already-propertied value with a block.
        if self.prop:
            return self.b.op("mul", self, -1.0)
        return V(self.b, self.id, "negative")


class Builder:
    def __init__(self, nb, literal_names):
        self.nb = nb
        self.section = None
        self.literals = set(literal_names)
        self.names = set(literal_names)
        self.memo = {}
        self.consts = {}
        self.n_blocks = 0
        self.n_vars = 0
        self.k = 0
        self.timing = {}
        self.math_section = None   # section name that receives scalar math, or None for current
        self._section_ids = {}

    # ---- sections ------------------------------------------------------
    def section_id(self, name):
        if name not in self._section_ids:
            for s in self.nb.list_sections():
                if s["name"] == name:
                    self._section_ids[name] = s["id"]
                    break
            else:
                self._section_ids[name] = self.nb.add_section(name)["id"]
        return self._section_ids[name]

    def use_section(self, name):
        self.section = self.section_id(name)

    def add_math(self, key):
        """A scalar block goes to the math section when one is set."""
        sid = self.section_id(self.math_section) if self.math_section else self.section
        bid = self.nb.add_block(ID[key], sid)["id"]
        self.n_blocks += 1
        return bid

    # ---- primitives of the API -----------------------------------------
    def add(self, key):
        bid = self.nb.add_block(ID[key], self.section)["id"]
        self.n_blocks += 1
        return bid

    def set(self, bid, param, value):
        self.nb.set_block_input(bid, param, value)

    def wire(self, src, dst, param):
        if isinstance(src, V):
            sid, prop = src.src()
        elif isinstance(src, tuple):
            sid, prop = src
        else:
            sid, prop = src, ""
        try:
            self.nb.connect_block_property(sid, prop, dst, param)
            return
        except Exception as exc:
            if "already has a value" not in str(exc):
                raise
        self.nb.clear_block_input(dst, param)
        self.nb.connect_block_property(sid, prop, dst, param)

    def var(self, name, bid):
        if name in self.names:
            raise RuntimeError("duplicate variable name %r" % name)
        self.names.add(name)
        vid = self.nb.add_variable(name, bid)["id"]
        self.n_vars += 1
        return vid

    def lit(self, name):
        if name not in self.literals:
            raise RuntimeError("no literal %r; regenerate the recipe" % name)
        return V(self, name)

    # ---- scalars -----------------------------------------------------------
    def const(self, x):
        x = float(x)
        if x in self.consts:
            return self.consts[x]
        bid = self.add_math("var_real")
        self.set(bid, "Input", x)
        vid = self.var("c %g" % x, bid)
        v = V(self, vid)
        self.consts[x] = v
        return v

    def _val(self, x):
        if isinstance(x, V):
            return x
        if isinstance(x, str):
            return V(self, x)
        return self.const(x)

    def hold(self, v, name=None):
        if isinstance(v, V) and v.prop:
            # a var whose contents is a ref with a property reads back WITHOUT the property
            return self.op("mul", v, 1.0, name=name)
        bid = self.add_math("var_real")
        self.wire(v, bid, "Input")
        return V(self, self.var(name or self._auto(), bid))

    def _auto(self):
        self.k += 1
        return "k%04d" % self.k

    def op(self, key, a, b=None, name=None):
        a = self._val(a)
        b = self._val(b) if b is not None else None
        mk = (key, a.src(), b.src() if b else None)
        if mk in self.memo and name is None:
            return self.memo[mk]
        bid = self.add_math(key)
        if b is None:
            self.wire(a, bid, "Operand")
        else:
            self.wire(a, bid, "Operand A")
            self.wire(b, bid, "Operand B")
        v = V(self, self.var(name or self._auto(), bid))
        self.memo[mk] = v
        return v

    def sin(self, a, name=None):
        return self.op("sin", a, name=name)

    def cos(self, a, name=None):
        return self.op("cos", a, name=name)

    def asin(self, a, name=None):
        return self.op("asin", a, name=name)

    def acos(self, a, name=None):
        return self.op("acos", a, name=name)

    def sqrt(self, a, name=None):
        return self.op("sqrt", a, name=name)

    def max(self, a, b, name=None):
        return self.op("max", a, b, name=name)

    # ---- points and vectors ---------------------------------------------
    def P(self, x=None, y=None, z=None):
        """A point; None leaves the coordinate at its default of 0."""
        bid = self.add("point")
        for param, v in zip("XYZ", (x, y, z)):
            if v is not None:
                self.wire(self._val(v), bid, param)
        return bid

    def VEC(self, x=None, y=None, z=None, name=None):
        """A translation vector with length units; None is a zero length."""
        zero = self.lit("Zero Length")
        bid = self.add("vector")
        for param, v in zip("XYZ", (x, y, z)):
            self.wire(zero if v is None else self._val(v), bid, param)
        return self.var(name, bid) if name else bid

    def DIR(self, x, y, z):
        """A unit-free direction vector; numbers are set, V sources wired."""
        bid = self.add("vector")
        for param, v in zip("XYZ", (x, y, z)):
            if isinstance(v, V):
                self.wire(v, bid, param)
            else:
                self.set(bid, param, float(v))
        return bid

    # ---- bodies ------------------------------------------------------------
    def cyl(self, p1, p2, r):
        bid = self.add("cyl")
        self.wire(p1, bid, "Point 1")
        self.wire(p2, bid, "Point 2")
        self.wire(self._val(r), bid, "Radius")
        return bid

    def box(self, p1, p2):
        bid = self.add("box")
        self.wire(p1, bid, "Point 1")
        self.wire(p2, bid, "Point 2")
        return bid

    def sphere(self, c, r):
        bid = self.add("sphere")
        self.wire(c, bid, "Center Point")
        self.wire(self._val(r), bid, "Radius")
        return bid

    def cone(self, p1, p2, r1, r2):
        bid = self.add("cone")
        self.wire(p1, bid, "Point 1")
        self.wire(p2, bid, "Point 2")
        self.wire(self._val(r1), bid, "Radius 1")
        self.wire(self._val(r2), bid, "Radius 2")
        return bid

    def torus(self, c, axis, R, rt):
        bid = self.add("torus")
        self.wire(c, bid, "Center")
        self.set(bid, "Axis", tuple(float(a) for a in axis))
        self.wire(self._val(R), bid, "Radius")
        self.wire(self._val(rt), bid, "Torus Radius")
        return bid

    def union(self, bodies, name=None):
        bid = self.add("union")
        for body in bodies:
            self.nb.append_to_list(body, bid, "Bodies")
        return self.var(name, bid) if name else bid

    def subtract(self, primary, bodies, name=None):
        bid = self.add("subtract")
        self.wire(primary, bid, "Primary Body")
        for body in bodies:
            self.nb.append_to_list(body, bid, "Subtraction Bodies")
        return self.var(name, bid) if name else bid

    def intersect(self, bodies, name=None):
        bid = self.add("intersect")
        for body in bodies:
            self.nb.append_to_list(body, bid, "Bodies")
        return self.var(name, bid) if name else bid

    def translate(self, body, vec, name=None):
        bid = self.add("translate")
        self.wire(body, bid, "Object")
        self.wire(vec, bid, "Vector")
        return self.var(name, bid) if name else bid

    def rotate(self, body, center, axis, angle, name=None):
        bid = self.add("rotate")
        self.wire(body, bid, "Object")
        if isinstance(center, tuple):
            self.set(bid, "Rotation Center", tuple(float(c) for c in center))
        else:
            self.wire(center, bid, "Rotation Center")
        self.set(bid, "Axis", tuple(float(a) for a in axis))
        self.wire(self._val(angle), bid, "Angle")
        return self.var(name, bid) if name else bid

    def array(self, body, count, spacing, name=None):
        bid = self.add("array")
        self.wire(body, bid, "Body")
        self.set(bid, "Count", tuple(float(c) for c in count))
        self.wire(spacing, bid, "Spacing")
        return self.var(name, bid) if name else bid

    def polar(self, body, angle, count_lit, axis_bid, name=None):
        bid = self.add("polar")
        self.wire(body, bid, "Body")
        self.wire(self._val(angle), bid, "Angular Spacing")
        self.wire(self.lit(count_lit), bid, "Count")
        self.wire(axis_bid, bid, "Axis")
        return self.var(name, bid) if name else bid

    def axis(self, point, direction):
        bid = self.add("axis")
        if point is not None:
            self.wire(point, bid, "Point")
        self.set(bid, "Vector", tuple(float(a) for a in direction))
        return bid

    def halfspace(self, origin, normal, name):
        """The half-space on the side OPPOSITE `normal`, as an implicit variable."""
        pl = self.add("plane")
        self.wire(origin, pl, "Origin")
        if isinstance(normal, tuple):
            self.set(pl, "Normal", tuple(float(a) for a in normal))
        else:
            self.wire(normal, pl, "Normal")
        # A property can only be taken off a variable, so name the plane.
        plv = self.var(name + " plane", pl)
        hv = self.add("var_implicit")
        self.wire((plv, "body"), hv, "Input")
        return self.var(name, hv)

    def body_var(self, body, name):
        bid = self.add("var_implicit")
        self.wire(body, bid, "Input")
        return self.var(name, bid)

    # ---- curves and fields -------------------------------------------------
    def polyline(self, points_src, name=None):
        bid = self.add("polyline")
        self.wire(points_src, bid, "Points")
        return self.var(name, bid) if name else bid

    def tube(self, curve_var, radius, name=None):
        """A round tube of `radius` along a curve variable: its distance field, thickened."""
        fb = self.add("var_implicit")
        self.wire((curve_var, "scalar field"), fb, "Input")
        fbv = self.var((name or curve_var) + " field body", fb)
        th = self.add("thicken")
        self.wire(fbv, th, "Body")
        self.wire(self._val(radius), th, "Thickness")
        return self.var(name, th) if name else th

    # ---- scalar fields ----------------------------------------------------------
    def coord_field(self, axis_name, normal, name):
        """The signed distance to a plane through the origin: a linear coordinate field."""
        pl = self.add_math("plane")
        self.set(pl, "Normal", tuple(float(a) for a in normal))
        plv = self.var(name + " plane", pl)
        f = self.add_math("var_field")
        self.wire((plv, "body"), f, "Input")
        return self.var(name, f)

    def fop(self, key, a, b=None, name=None):
        """Field arithmetic; operands are field variable names or real V values."""
        bid = self.add_math(key)
        if b is None:
            self.wire(self._val(a) if not isinstance(a, str) else a, bid, "Operand")
        else:
            self.wire(self._val(a) if not isinstance(a, str) else a, bid, "Operand A")
            self.wire(self._val(b) if not isinstance(b, str) else b, bid, "Operand B")
        return self.var(name or self._auto(), bid)

    def helix_field_body(self, xf, yf, zf, radius, wire_radius, pitch, full_turn, name):
        """Exact distance field of a helix of `radius` about +Z with the given pitch,
        offset by the wire radius, as an (unbounded) implicit body. Clip it afterwards."""
        rho = self.fop("fsqrt", self.fop("fadd", self.fop("fmul", xf, xf), self.fop("fmul", yf, yf)))
        phi = self.fop("fatan2", yf, xf)
        rise = self.fop("fmul", self.fop("fdiv", phi, full_turn), pitch)
        u = self.fop("fmod", self.fop("fsub", zf, rise), pitch)
        w = self.fop("fsub", u, self._val(pitch * 0.5) if isinstance(pitch, V) else pitch)
        dr = self.fop("fsub", rho, radius)
        d = self.fop("fsqrt", self.fop("fadd", self.fop("fmul", dr, dr), self.fop("fmul", w, w)))
        dist = self.fop("fsub", d, wire_radius, name=name + " field")
        iv = self.add_math("var_implicit")
        self.wire(dist, iv, "Input")
        return self.var(name, iv)

    # ---- measurement -------------------------------------------------------
    def bbox_coord(self, body_var, which, coord, name):
        """`which` is 'min' or 'max'; `coord` is 'x', 'y' or 'z'. Returns V in mm."""
        bb = self.add("var_bbox")
        self.wire((body_var, "bounding box"), bb, "Input")
        bbv = self.var(name + " bbox", bb)
        pt = self.add("var_point")
        self.wire((bbv, which + " point"), pt, "Input")
        ptv = self.var(name + " " + which, pt)
        return self.op("div", V(self, ptv, coord), self.lit("One Millimetre"), name=name)


# ============================================================================


EXTENT_CHECKS = [
    ("Crank Throw", "max", "z"), ("Crank Throw", "min", "z"), ("Crank Throw", "max", "y"), ("Crank Throw", "max", "x"),
    ("Piston", "max", "z"), ("Piston", "min", "z"), ("Piston", "max", "x"),
    ("Connecting Rod", "max", "z"), ("Connecting Rod", "min", "z"), ("Connecting Rod", "max", "y"), ("Connecting Rod", "max", "x"),
    ("Intake Valve", "max", "z"), ("Intake Valve", "min", "z"), ("Intake Valve", "max", "x"),
    ("Crankshaft at TDC", "min", "x"), ("Crankshaft at TDC", "max", "x"),
    ("Cylinder Block", "min", "z"), ("Cylinder Block", "max", "x"), ("Cylinder Block", "max", "y"),
    ("Cylinder Head", "max", "y"), ("Cylinder Head", "max", "x"),
    ("Intake Camshaft static", "max", "x"), ("Intake Camshaft static", "min", "x"),
    ("Bedplate", "min", "z"), ("Oil Pan", "min", "z"),
]


def _first_section_id(nb):
    return nb.list_sections()[0]["id"]


def build(notebook):
    """New notebook, import literals, build every section, save. Returns a summary."""
    t_start = time.perf_counter()
    if not os.path.isfile(LITERALS):
        raise RuntimeError("%s missing; run demos/i6/scripts/make_engine_recipe.py" % LITERALS)
    with open(LITERALS, encoding="utf-8") as fh:
        literal_names = [e["name"] for e in json.load(fh)["body"]]

    nb = notebook
    nb.new_notebook()
    # Imported variables land in the first section; make that INPUTS.
    nb.add_section("INPUTS", _first_section_id(nb))
    nb.import_recipe(LITERALS)
    have = {v["id"] for v in nb.list_variables()}
    missing = [n for n in literal_names if n not in have]
    if missing:
        raise RuntimeError("recipe import lacks %r" % missing[:5])
    landed = {s["name"]: len(nb.list_blocks(s["id"])) for s in nb.list_sections()}

    b = Builder(nb, literal_names)
    Lt = b.lit
    timing = {}

    def section(name):
        b.use_section(name)
        timing[name] = time.perf_counter()

    def done(name):
        timing[name] = round(time.perf_counter() - timing[name], 1)
        # Progress and a checkpoint after every section, so a crash or a
        # reboot mid-build leaves a partial notebook and a timeline behind.
        nb.save_notebook_as(NOTEBOOK_PATH)
        with open(os.path.join(OUT_DIR, "engine_progress.json"), "w", encoding="utf-8") as fh:
            json.dump({"section_seconds": timing, "blocks": b.n_blocks, "variables": b.n_vars,
                       "elapsed": round(time.perf_counter() - t_start, 1)}, fh, indent=1)

    # ---- shared values -------------------------------------------------------
    zero = Lt("Zero Length")
    ov = Lt("Overrun")
    big = Lt("Big")
    pitch = Lt("Bore Pitch")
    B = Lt("Bore")
    S = Lt("Stroke")
    rod = Lt("Rod Length")
    ch = Lt("Compression Height")
    theta = Lt("Crank Angle")
    tilt = Lt("Valve Tilt")

    # ---- MATH: derived dimensions, then kinematics -----------------------------
    b.math_section = "MATH - DIMENSIONS"
    section("MATH - DIMENSIONS")
    r = b.op("mul", S, 0.5, name="Crank Radius")
    z_deck = b.op("add", r + rod, ch, name="Deck Height")
    z_seat = b.op("add", z_deck, Lt("Chamber Depth"), name="Seat Height")
    rod_sq = b.op("mul", rod, rod, name="Rod Length Squared")
    psi = b.op("mul", theta, Lt("Cam Ratio"), name="Cam Angle")
    Rb, rn = Lt("Cam Base Radius"), Lt("Cam Nose Radius")
    d_nose = b.op("sub", Rb + Lt("Cam Lift"), rn, name="Cam Nose Offset")
    lift_bias = b.op("sub", rn, Rb, name="Cam Lift Bias")
    x = {i: b.op("mul", Lt("Cyl Index %d" % i), pitch, name="Cyl %d X" % i) for i in range(1, 7)}
    x_m0 = b.op("mul", Lt("Main Index"), pitch, name="Rear Main X")
    x_fm = b.op("mul", pitch, 3.0, name="Front Main X")
    Lh = b.op("add", x_fm, Lt("Block End Wall"), name="Block Half Length")
    done("MATH - DIMENSIONS")
    b.math_section = "MATH - KINEMATICS"
    section("MATH - KINEMATICS")
    K = {}
    for i in range(1, 7):
        n = "Cyl %d " % i
        th = b.op("add", theta, Lt("Phase Cyl %d" % i), name=n + "theta")
        s = b.sin(th, name=n + "sin")
        co = b.cos(th, name=n + "cos")
        q = b.op("mul", r, s, name=n + "r sin")
        zpin = b.op("mul", r, co, name=n + "pin z")
        zp = b.op("add", zpin, b.sqrt(rod_sq - q * q), name=n + "piston pin z")
        beta = b.asin(q / rod, name=n + "rod tilt")
        psi_i = b.op("mul", th, Lt("Cam Ratio"), name=n + "cam angle")
        u_int = b.op("sub", psi_i, Lt("Intake Centerline"), name=n + "intake cam u")
        u_exh = b.op("sub", psi_i, Lt("Exhaust Centerline"), name=n + "exhaust cam u")
        lift_int = b.max(zero, d_nose * b.cos(u_int) + lift_bias, name=n + "intake lift")
        lift_exh = b.max(zero, d_nose * b.cos(u_exh) + lift_bias, name=n + "exhaust lift")
        K[i] = dict(th=th, q=q, zpin=zpin, ypin=-q, zp=zp, beta=beta,
                    lift_int=lift_int, lift_exh=lift_exh)
    done("MATH - KINEMATICS")
    b.math_section = "MATH - DIMENSIONS"

    # ---- CRANKSHAFT ----------------------------------------------------------
    section("CRANKSHAFT")
    wm, Dm = Lt("Main Journal Width"), Lt("Main Journal Diameter")
    wp, Dp = Lt("Rod Journal Width"), Lt("Rod Journal Diameter")
    wt = b.op("mul", pitch - wp - wm, 0.5, name="Crank Web Thickness")
    eye = Lt("Pin Eye Radius")
    web_arm = b.cyl(b.P(), b.P(wt), Lt("Web Arm Radius"))
    web_eye = b.cyl(b.P(None, None, r), b.P(wt, None, r), eye)
    web_bridge = b.box(b.P(None, -eye, None), b.P(wt, eye, r))
    cw_cyl = b.cyl(b.P(), b.P(wt), Lt("Counterweight Radius"))
    cw_half = b.halfspace(b.P(None, None, -Lt("Counterweight Top")), (0, 0, 1), "Counterweight Half-space")
    cw_hw = Lt("Counterweight Half Width")
    cw_box = b.box(b.P(None, -cw_hw, -big), b.P(wt, cw_hw, zero))
    cw = b.intersect([cw_cyl, cw_half, cw_box])
    b.union([web_arm, web_eye, web_bridge, cw], name="Crank Web")
    hwp = wp * 0.5
    pin = b.cyl(b.P(-hwp, None, r), b.P(hwp, None, r), Dp * 0.5)
    web_R = b.translate("Crank Web", b.VEC(hwp))
    web_L = b.translate("Crank Web", b.VEC(-(hwp + wt)))
    b.union([pin, web_R, web_L], name="Crank Throw")
    throws = [b.rotate(b.translate("Crank Throw", b.VEC(x[i])), (0, 0, 0), (1, 0, 0), Lt("Phase Cyl %d" % i))
              for i in range(1, 7)]
    pitch_vec = b.VEC(pitch, name="Pitch Vector")
    hwm = wm * 0.5
    mains = b.array(b.cyl(b.P(x_m0 - hwm), b.P(x_m0 + hwm), Dm * 0.5), (7, 1, 1), pitch_vec)
    nose = b.cyl(b.P(x_fm + hwm - ov), b.P(x_fm + hwm + Lt("Crank Nose Length")), Lt("Crank Nose Diameter") * 0.5)
    x_pul0 = Lh + Lt("Pulley Offset")
    x_pul1 = x_pul0 + Lt("Pulley Width")
    x_pulc = x_pul0 + Lt("Pulley Width") * 0.5
    Rpul = Lt("Pulley Diameter") * 0.5
    pulley = b.cyl(b.P(x_pul0), b.P(x_pul1), Rpul)
    gp = Lt("Pulley Groove Pitch")
    grooves = [b.torus(b.P(xc), (1, 0, 0), Rpul, Lt("Pulley Groove Radius"))
               for xc in (x_pulc - gp, x_pulc, x_pulc + gp)]
    pulley_g = b.subtract(pulley, grooves)
    tf = Lt("Rear Flange Thickness")
    x_fl1 = x_m0 - hwm
    x_fl0 = x_fl1 - tf
    flange = b.cyl(b.P(x_fl0), b.P(x_fl1 + ov), Lt("Rear Flange Diameter") * 0.5)
    x_fw0 = x_fl0 - Lt("Flywheel Thickness")
    Rfw = Lt("Flywheel Diameter") * 0.5
    flywheel = b.cyl(b.P(x_fw0), b.P(x_fl0 + ov), Rfw)
    htw = Lt("Ring Gear Tooth Width") * 0.5
    tooth = b.box(b.P(x_fw0, Rfw - ov, -htw), b.P(x_fw0 + Lt("Ring Gear Width"), Rfw + Lt("Ring Gear Tooth Height"), htw))
    teeth = b.polar(tooth, Lt("Ring Gear Tooth Pitch"), "Ring Gear Teeth", b.axis(None, (1, 0, 0)))
    rbc = Lt("Flywheel Bolt Circle Radius")
    bolt = b.cyl(b.P(x_fw0 - Lt("Flywheel Bolt Head Height"), None, rbc), b.P(x_fw0 + ov, None, rbc),
                 Lt("Flywheel Bolt Head Diameter") * 0.5)
    bolts = b.polar(bolt, Lt("Flywheel Bolt Pitch"), "Flywheel Bolts", b.axis(None, (1, 0, 0)))
    b.union([mains] + throws + [nose, pulley_g, flange, flywheel, teeth, bolts], name="Crankshaft at TDC")
    b.use_section("ENGINE ASSEMBLY")
    b.rotate("Crankshaft at TDC", (0, 0, 0), (1, 0, 0), theta, name="Crankshaft")
    done("CRANKSHAFT")

    # ---- CONNECTING RODS -----------------------------------------------------
    section("CONNECTING RODS")
    Rbe = Lt("Rod Big End Radius")
    hwb = Lt("Rod Big End Width") * 0.5
    big_end = b.cyl(b.P(-hwb), b.P(hwb), Rbe)
    boss_hw = Lt("Rod Cap Boss Half Width")
    boss = b.box(b.P(-hwb, -boss_hw, -Lt("Rod Cap Boss Bottom")), b.P(hwb, boss_hw, Lt("Rod Cap Boss Top")))
    hws = Lt("Rod Small End Width") * 0.5
    Rse = Lt("Rod Small End Radius")
    small_end = b.cyl(b.P(-hws, None, rod), b.P(hws, None, rod), Rse)
    hsw = Lt("Rod Shank Width") * 0.5
    hst = Lt("Rod Shank Thickness") * 0.5
    shank = b.box(b.P(-hsw, -hst, None), b.P(hsw, hst, rod))
    yb = Lt("Rod Bolt Spacing") * 0.5
    rbolt = Lt("Rod Bolt Diameter") * 0.5
    bz0 = -(Rbe + Lt("Rod Bolt Head Height"))
    bz1 = Lt("Rod Cap Boss Top")
    rhead = Lt("Rod Bolt Head Diameter") * 0.5
    rod_parts = [big_end, boss, small_end, shank]
    for yy in (yb, -yb):
        rod_parts.append(b.cyl(b.P(None, yy, bz0), b.P(None, yy, bz1), rbolt))
        rod_parts.append(b.cyl(b.P(None, yy, bz0), b.P(None, yy, -Rbe + ov), rhead))
    rod_plus = b.union(rod_parts)
    clr = Lt("Rod Bearing Clearance")
    big_bore = b.cyl(b.P(-(hwb + ov)), b.P(hwb + ov), Dp * 0.5 + clr)
    small_bore = b.cyl(b.P(-(hws + ov), None, rod), b.P(hws + ov, None, rod), Lt("Pin Diameter") * 0.5 + clr)
    px0 = Lt("Rod Web Thickness") * 0.5
    px1 = hsw + ov
    py = hst - Lt("Rod Flange Thickness")
    pz1 = rod - Rse
    pocket_R = b.box(b.P(px0, -py, Rbe), b.P(px1, py, pz1))
    pocket_L = b.box(b.P(-px1, -py, Rbe), b.P(-px0, py, pz1))
    b.subtract(rod_plus, [big_bore, small_bore, pocket_R, pocket_L], name="Connecting Rod")
    b.use_section("ENGINE ASSEMBLY")
    for i in range(1, 7):
        swung = b.rotate("Connecting Rod", (0, 0, 0), (1, 0, 0), -K[i]["beta"])
        b.translate(swung, b.VEC(x[i], K[i]["ypin"], K[i]["zpin"]), name="Connecting Rod Cyl %d" % i)
    done("CONNECTING RODS")

    # ---- PISTONS -------------------------------------------------------------
    section("PISTONS")
    Rp = b.op("sub", B * 0.5, Lt("Piston Clearance"), name="Piston Radius")
    z_top = ch
    z_bot = -(Lt("Piston Length") - ch)
    env_bid = b.cyl(b.P(None, None, z_bot), b.P(None, None, z_top), Rp)
    b.var("Piston Envelope", env_bid)
    Rd = Lt("Dish Sphere Radius")
    dish = b.sphere(b.P(None, None, z_top + Rd - Lt("Dish Depth")), Rd)
    hs = b.op("mul", Lt("Valve Spacing"), 0.5, name="Half Valve Spacing")
    ys = Lt("Valve Offset")
    Din, Dex = Lt("Intake Valve Diameter"), Lt("Exhaust Valve Diameter")
    rel_d, rel_m = Lt("Valve Relief Depth"), Lt("Valve Relief Margin")
    reliefs = []
    for sx in (hs, -hs):
        for sy, D in ((ys, Din), (-ys, Dex)):
            reliefs.append(b.cyl(b.P(sx, sy, z_top - rel_d), b.P(sx, sy, z_top + ov), D * 0.5 + rel_m))
    rw, ow, land, gd = Lt("Compression Ring Width"), Lt("Oil Ring Width"), Lt("Ring Land"), Lt("Ring Groove Depth")
    g1t = z_top - Lt("Top Land")
    g1b = g1t - rw
    g2t = g1b - land
    g2b = g2t - rw
    g3t = g2b - land
    g3b = g3t - ow

    def groove(zt, zb):
        outer = b.cyl(b.P(None, None, zb), b.P(None, None, zt), Rp + ov)
        inner = b.cyl(b.P(None, None, zb - ov), b.P(None, None, zt + ov), Rp - gd)
        return b.subtract(outer, [inner])

    grooves = [groove(g1t, g1b), groove(g2t, g2b), groove(g3t, g3b)]
    hollow = b.cyl(b.P(None, None, z_bot - ov), b.P(None, None, z_top - Lt("Crown Thickness")), Rp - Lt("Piston Wall"))
    srw, srt = Lt("Skirt Relief Width"), Lt("Skirt Relief Top")
    cut_R = b.box(b.P(Rp - srw, -big, z_bot - ov), b.P(Rp + ov, big, -srt))
    cut_L = b.box(b.P(-(Rp + ov), -big, z_bot - ov), b.P(-(Rp - srw), big, -srt))
    piston_cut = b.subtract("Piston Envelope", [dish] + reliefs + grooves + [hollow, cut_R, cut_L])
    hp = Lt("Pin Length") * 0.5
    bosses = b.intersect([b.cyl(b.P(-hp), b.P(hp), Lt("Pin Boss Radius")), "Piston Envelope"])
    pin_body = b.cyl(b.P(-hp), b.P(hp), Lt("Pin Diameter") * 0.5)
    b.union([piston_cut, bosses, pin_body], name="Piston")
    b.use_section("ENGINE ASSEMBLY")
    for i in range(1, 7):
        b.translate("Piston", b.VEC(x[i], None, K[i]["zp"]), name="Piston Cyl %d" % i)
    done("PISTONS")

    # ---- CYLINDER BLOCK ------------------------------------------------------
    section("CYLINDER BLOCK")
    Wb2 = b.op("mul", Lt("Block Width"), 0.5, name="Block Half Width")
    Wc2 = b.op("mul", Lt("Crankcase Width"), 0.5, name="Crankcase Half Width")
    cut_box = b.box(b.P(-big, Lt("Cutaway Y"), -big), b.P(big, big, big))
    b.var("Cutaway Box", cut_box)
    z_bore_bot = b.op("sub", (rod - r) - (Lt("Piston Length") - ch), Lt("Bore Overrun"), name="Bore Bottom Z")
    z_roof = z_bore_bot + Lt("Crankcase Roof Offset")
    # Upper block around the bores, wider crankcase below the bore bottoms.
    env_blk = b.union([b.box(b.P(-Lh, -Wb2, zero), b.P(Lh, Wb2, z_deck)),
                       b.box(b.P(-Lh, -Wc2, zero), b.P(Lh, Wc2, z_roof + Lt("Block Side Wall")))])
    x6 = x[6]
    bores = b.array(b.cyl(b.P(x6, None, z_bore_bot), b.P(x6, None, z_deck + ov), B * 0.5), (6, 1, 1), pitch_vec)
    jt, jd = Lt("Jacket Top Offset"), Lt("Jacket Depth")
    r_in = B * 0.5 + Lt("Bore Wall")
    r_out = r_in + Lt("Jacket Width")
    jacket_out = b.array(b.cyl(b.P(x6, None, z_deck - jt - jd), b.P(x6, None, z_deck - jt), r_out), (6, 1, 1), pitch_vec)
    jacket_in = b.array(b.cyl(b.P(x6, None, z_deck - jt - jd - ov), b.P(x6, None, z_deck - jt + ov), r_in), (6, 1, 1), pitch_vec)
    jacket = b.subtract(jacket_out, [jacket_in])
    bed = Lt("Bedplate Depth")
    hbt = Lt("Bulkhead Thickness") * 0.5
    bulkheads = b.array(b.box(b.P(x_m0 - hbt, -(Wc2 + ov), -(bed + ov)), b.P(x_m0 + hbt, Wc2 + ov, z_roof + ov)), (7, 1, 1), pitch_vec)
    yin = Wc2 - Lt("Block Side Wall")
    cavity_box = b.box(b.P(-x_fm, -yin, -(bed + ov)), b.P(x_fm, yin, z_roof))
    b.subtract(cavity_box, [bulkheads], name="Crankcase Cavity")
    main_bore_bid = b.cyl(b.P(-(Lh + ov)), b.P(Lh + ov), Dm * 0.5 + Lt("Bearing Shell Thickness"))
    b.var("Main Bearing Bore", main_bore_bid)
    hb_r = Lt("Head Bolt Diameter") * 0.5
    hb_y = Lt("Head Bolt Offset")
    hb_z0 = z_deck - Lt("Head Bolt Depth")
    hb_z1 = z_deck + Lt("Head Height") + ov
    hb_pair = b.union([b.cyl(b.P(x_m0, hb_y, hb_z0), b.P(x_m0, hb_y, hb_z1), hb_r),
                       b.cyl(b.P(x_m0, -hb_y, hb_z0), b.P(x_m0, -hb_y, hb_z1), hb_r)])
    b.array(hb_pair, (7, 1, 1), pitch_vec, name="Head Bolt Holes")
    # Solid bosses carry the head bolts through the water jacket.
    boss_r = Lt("Head Bolt Boss Diameter") * 0.5
    boss_pair = b.union([b.cyl(b.P(x_m0, hb_y, hb_z0 - boss_r), b.P(x_m0, hb_y, z_deck), boss_r),
                         b.cyl(b.P(x_m0, -hb_y, hb_z0 - boss_r), b.P(x_m0, -hb_y, z_deck), boss_r)])
    bosses_blk = b.array(boss_pair, (7, 1, 1), pitch_vec)
    block_jacketed = b.union([b.subtract(env_blk, [jacket]), bosses_blk])
    block_solid = b.subtract(block_jacketed, [bores, "Crankcase Cavity", "Main Bearing Bore", "Head Bolt Holes"])
    b.var("Cylinder Block solid", block_solid)
    bed_box = b.box(b.P(-Lh, -Wc2, -bed), b.P(Lh, Wc2, zero))
    bed_solid = b.subtract(bed_box, ["Crankcase Cavity", "Main Bearing Bore"])
    b.var("Bedplate solid", bed_solid)
    pan, pw = Lt("Oil Pan Depth"), Lt("Oil Pan Wall")
    pan_outer = b.box(b.P(-Lh, -Wc2, -(bed + pan)), b.P(Lh, Wc2, -bed))
    pan_inner = b.box(b.P(-(Lh - pw), -(Wc2 - pw), -(bed + pan - pw)), b.P(Lh - pw, Wc2 - pw, -bed + ov))
    b.var("Oil Pan solid", b.subtract(pan_outer, [pan_inner]))
    b.use_section("ENGINE ASSEMBLY")
    b.intersect(["Cylinder Block solid", "Cutaway Box"], name="Cylinder Block")
    b.intersect(["Bedplate solid", "Cutaway Box"], name="Bedplate")
    b.intersect(["Oil Pan solid", "Cutaway Box"], name="Oil Pan")
    done("CYLINDER BLOCK")

    # ---- VALVETRAIN (valve bodies and pairs) ----------------------------------
    section("VALVETRAIN")
    st = b.sin(tilt, name="sin Valve Tilt")
    ct = b.cos(tilt, name="cos Valve Tilt")
    Lv = Lt("Valve Length")
    stem_r = Lt("Valve Stem Diameter") * 0.5
    floor_t = Lt("Bucket Floor")
    Rbk = Lt("Bucket Diameter") * 0.5
    valve_names = {}
    for kind, D in (("Intake", Din), ("Exhaust", Dex)):
        Rv = D * 0.5
        head = b.cone(b.P(), b.P(None, None, -Lt("Valve Head Thickness")), Rv, Rv - Lt("Valve Head Margin"))
        fillet = b.cone(b.P(), b.P(None, None, Lt("Valve Fillet Height")), Rv, stem_r)
        # The stem runs half way into the bucket crown: a stem that only touches
        # the bucket floor meshes as a separate component and the exporter drops it.
        stem = b.cyl(b.P(None, None, Lt("Valve Fillet Height") - ov), b.P(None, None, Lv + floor_t * 0.5), stem_r)
        ret0 = Lv - Lt("Retainer Offset")
        retainer = b.cyl(b.P(None, None, ret0), b.P(None, None, ret0 + Lt("Retainer Thickness")), Lt("Retainer Radius"))
        keeper = b.torus(b.P(None, None, Lv - Lt("Keeper Groove Offset")), (0, 0, 1), stem_r, Lt("Keeper Groove Radius"))
        valve_core = b.subtract(b.union([head, fillet, stem, retainer]), [keeper])
        bk_top = Lv + floor_t
        bk_bot = bk_top - Lt("Bucket Height")
        bucket_outer = b.cyl(b.P(None, None, bk_bot), b.P(None, None, bk_top), Rbk)
        bucket_inner = b.cyl(b.P(None, None, bk_bot - ov), b.P(None, None, Lv), Rbk - Lt("Bucket Wall"))
        bucket = b.subtract(bucket_outer, [bucket_inner])
        vname = kind + " Valve"
        b.union([valve_core, bucket], name=vname)
        valve_names[kind] = vname
    vec_plus = b.VEC(hs, name="Half Spacing +X")
    vec_minus = b.VEC(-hs, name="Half Spacing -X")
    for kind in ("Intake", "Exhaust"):
        vn = valve_names[kind]
        b.union([b.translate(vn, vec_plus), b.translate(vn, vec_minus)], name=kind + " Valve Pair")
    ang = {"Intake": -tilt, "Exhaust": tilt}
    y_seat = {"Intake": ys, "Exhaust": -ys}
    # Valve springs: an exact helix distance field. Three plane distance fields
    # give x, y, z; the helix of mean radius R and pitch p is the set where the
    # distance to the coil centreline is the wire radius. The pitch is
    # (installed length - lift) / turns, so the spring compresses with its valve
    # while its seat end stays on the head. Analytic, so cheap to re-evaluate.
    b.math_section = "MATH - SPRING FIELDS"
    xf = b.coord_field("x", (1, 0, 0), "Spring Field X")
    yf = b.coord_field("y", (0, 1, 0), "Spring Field Y")
    zf = b.coord_field("z", (0, 0, 1), "Spring Field Z")
    full_turn = b.op("mul", Lt("Half Turn"), 2.0, name="Full Turn")
    z_spring_seat = Lt("Spring Seat Height")
    spring_installed = b.op("sub", Lv - Lt("Retainer Offset"), z_spring_seat, name="Spring Installed Length")
    spring_R = Lt("Spring Mean Radius")
    wire_r = b.op("mul", Lt("Spring Wire Diameter"), 0.5, name="Spring Wire Radius")
    clip_r = b.op("add", spring_R, wire_r * 1.5, name="Spring Clip Radius")
    turns = Lt("Spring Turns")

    def spring_coil(length_v, tag, name=None):
        pitch = b.op("div", length_v, turns, name=tag + " pitch")
        helix = b.helix_field_body(xf, yf, zf, spring_R, wire_r, pitch, full_turn, tag + " helix")
        # the helix must start at the seat: shift the field's z origin to the seat
        # by clipping between seat and seat + length (phase at the seat is fixed by mod)
        clip = b.cyl(b.P(None, None, z_spring_seat), b.P(None, None, z_spring_seat + length_v), clip_r)
        return b.intersect([helix, clip], name=name or (tag + " coil"))

    def spring_pair(length_v, tag):
        one = spring_coil(length_v, tag)
        return b.union([b.translate(one, vec_plus), b.translate(one, vec_minus)], name=tag + " pair")

    spring_coil(spring_installed, "Valve Spring static", name="Valve Spring")
    b.math_section = "MATH - DIMENSIONS"
    b.use_section("ENGINE ASSEMBLY")
    for i in range(1, 7):
        for kind, lift in (("Intake", K[i]["lift_int"]), ("Exhaust", K[i]["lift_exh"])):
            lifted = b.translate(kind + " Valve Pair", b.VEC(None, None, -lift))
            tilted = b.rotate(lifted, (0, 0, 0), (1, 0, 0), ang[kind])
            b.translate(tilted, b.VEC(x[i], y_seat[kind], z_seat), name="%s Valves Cyl %d" % (kind, i))
            b.use_section("VALVETRAIN")
            b.math_section = "MATH - SPRING FIELDS"
            pair = spring_pair(spring_installed - lift, "%s Spring Cyl %d" % (kind, i))
            b.math_section = "MATH - DIMENSIONS"
            b.use_section("ENGINE ASSEMBLY")
            tilted_s = b.rotate(pair, (0, 0, 0), (1, 0, 0), ang[kind])
            b.translate(tilted_s, b.VEC(x[i], y_seat[kind], z_seat), name="%s Springs Cyl %d" % (kind, i))
    done("VALVETRAIN")

    # ---- CAMSHAFTS -----------------------------------------------------------
    section("CAMSHAFTS")
    H = b.op("add", Lv + floor_t, Rb, name="Seat To Cam Axis")
    y_cam_i = b.op("add", ys, H * st, name="Intake Cam Y")
    y_cam = {"Intake": y_cam_i, "Exhaust": -y_cam_i}
    z_cam = b.op("add", z_seat, H * ct, name="Cam Axis Z")
    hlw = Lt("Cam Lobe Width") * 0.5
    base = b.cyl(b.P(-hlw), b.P(hlw), Rb)
    nose_c = b.cyl(b.P(-hlw, None, d_nose), b.P(hlw, None, d_nose), rn)
    cosphi = b.op("div", Rb - rn, d_nose, name="Cam Flank cos")
    sinphi = b.sin(b.acos(cosphi), name="Cam Flank sin")
    ty = b.op("mul", Rb, sinphi, name="Cam Tangent Y")
    tz = b.op("mul", Rb, cosphi, name="Cam Tangent Z")
    z_flank_top = d_nose + rn * cosphi
    flank_box = b.box(b.P(-(hlw + ov), -Rb, None), b.P(hlw + ov, Rb, z_flank_top))
    hs_R = b.halfspace(b.P(None, ty, tz), b.DIR(0.0, sinphi, cosphi), "Cam Flank Half-space +Y")
    hs_L = b.halfspace(b.P(None, -ty, tz), b.DIR(0.0, -sinphi, cosphi), "Cam Flank Half-space -Y")
    flank = b.intersect([flank_box, hs_R, hs_L])
    b.union([base, nose_c, flank], name="Cam Lobe")
    b.union([b.translate("Cam Lobe", vec_plus), b.translate("Cam Lobe", vec_minus)], name="Cam Lobe Pair")
    half_turn = Lt("Half Turn")
    lobe_base_angle = {"Intake": b.op("sub", half_turn, tilt, name="Intake Lobe Base Angle"),
                       "Exhaust": b.op("add", half_turn, tilt, name="Exhaust Lobe Base Angle")}
    centerline = {"Intake": Lt("Intake Centerline"), "Exhaust": Lt("Exhaust Centerline")}
    x_cam0 = -Lh + Lt("Cam Sprocket Offset")
    x_spr0 = Lh + Lt("Cam Sprocket Offset")
    x_spr1 = x_spr0 + Lt("Cam Sprocket Width")
    Rspr = Lt("Cam Sprocket Diameter") * 0.5
    hjw = Lt("Cam Journal Width") * 0.5
    htw2 = Lt("Cam Sprocket Tooth Width") * 0.5
    for kind in ("Intake", "Exhaust"):
        yc = y_cam[kind]
        center = b.P(None, yc, z_cam)
        b.var("%s Cam Center" % kind, center)
        cname = "%s Cam Center" % kind
        tube = b.cyl(b.P(x_cam0, yc, z_cam), b.P(x_spr1, yc, z_cam), Lt("Cam Shaft Diameter") * 0.5)
        journals = b.array(b.cyl(b.P(x_m0 - hjw, yc, z_cam), b.P(x_m0 + hjw, yc, z_cam), Lt("Cam Journal Diameter") * 0.5),
                           (7, 1, 1), pitch_vec)
        sprocket = b.cyl(b.P(x_spr0, yc, z_cam), b.P(x_spr1, yc, z_cam), Rspr)
        tooth = b.box(b.P(x_spr0, yc + Rspr - ov, z_cam - htw2), b.P(x_spr1, yc + Rspr + Lt("Cam Sprocket Tooth Height"), z_cam + htw2))
        teeth = b.polar(tooth, Lt("Sprocket Tooth Pitch"), "Sprocket Teeth", b.axis(cname, (1, 0, 0)))
        lobes = []
        for i in range(1, 7):
            a_i = b.op("sub", lobe_base_angle[kind] + Lt("Phase Cyl %d" % i) * Lt("Cam Ratio"), centerline[kind],
                       name="%s Lobe Angle Cyl %d" % (kind, i))
            lobes.append(b.translate(b.rotate("Cam Lobe Pair", (0, 0, 0), (1, 0, 0), a_i), b.VEC(x[i], yc, z_cam)))
        b.union([tube, journals, sprocket, teeth] + lobes, name="%s Camshaft static" % kind)
        b.use_section("ENGINE ASSEMBLY")
        b.rotate("%s Camshaft static" % kind, cname, (1, 0, 0), psi, name="%s Camshaft" % kind)
        b.use_section("CAMSHAFTS")
    done("CAMSHAFTS")

    # ---- CYLINDER HEAD -------------------------------------------------------
    section("CYLINDER HEAD")
    Wh2 = b.op("mul", Lt("Head Width"), 0.5, name="Head Half Width")
    Hh = Lt("Head Height")
    z_head_top = b.op("add", z_deck, Hh, name="Head Top Z")
    env_head = b.box(b.P(-Lh, -Wh2, z_deck), b.P(Lh, Wh2, z_head_top))
    chamber = b.cyl(b.P(None, None, z_deck - ov), b.P(None, None, z_seat), Lt("Chamber Diameter") * 0.5)
    cuts = [chamber]
    tl = Lt("Throat Length")
    g0, g1 = Lt("Guide Start"), Lv - Lt("Guide End Offset")
    bb0 = Lv - Lt("Bucket Bore Start Offset")
    bb1 = bb0 + Lt("Bucket Bore Length")
    rs = Lt("Runner Start")

    def along(a, sign_pos):
        """(y, z) of the point a distance `a` up a valve axis, for the +y or -y bank."""
        yy = ys + a * st
        return (yy if sign_pos else -yy), z_seat + a * ct

    for kind, D, pos in (("Intake", Din, True), ("Exhaust", Dex, False)):
        y0 = ys if pos else -ys
        y_t, z_t = along(tl, pos)
        y_g0, z_g0 = along(g0, pos)
        y_g1, z_g1 = along(g1, pos)
        y_b0, z_b0 = along(bb0, pos)
        y_b1, z_b1 = along(bb1, pos)
        for sx in (hs, -hs):
            cuts.append(b.cyl(b.P(sx, y0, z_seat - ov), b.P(sx, y_t, z_t), D * 0.5 - ov))
            cuts.append(b.cyl(b.P(sx, y_g0, z_g0), b.P(sx, y_g1, z_g1), Lt("Guide Bore Diameter") * 0.5))
            cuts.append(b.cyl(b.P(sx, y_b0, z_b0), b.P(sx, y_b1, z_b1), Lt("Bucket Bore Diameter") * 0.5))
        y_r0, z_r0 = along(rs, pos)
        y_exit = (Wh2 + ov * 5.0) if pos else -(Wh2 + ov * 5.0)
        cuts.append(b.cyl(b.P(None, y_r0, z_r0), b.P(None, y_exit, z_r0 + Lt("Runner Rise")), Lt("Runner Diameter") * 0.5))
    z_plug = z_deck + Lt("Spark Plug Depth")
    cuts.append(b.cyl(b.P(None, None, z_deck - ov), b.P(None, None, z_plug), Lt("Spark Plug Diameter") * 0.5))
    cuts.append(b.cyl(b.P(None, None, z_plug - ov), b.P(None, None, z_head_top + ov), Lt("Plug Well Diameter") * 0.5))
    cut_one = b.union(cuts)
    head_cuts = b.array(b.translate(cut_one, b.VEC(x6)), (6, 1, 1), pitch_vec)
    pk_m = Lt("Cam Pocket Margin")
    y_pk = y_cam_i + pk_m
    z_pk = z_cam - Lt("Cam Pocket Depth")
    x_pk = x_fm + Lt("Cam Tower Thickness") * 0.5
    pocket_box = b.box(b.P(-x_pk, -y_pk, z_pk), b.P(x_pk, y_pk, z_head_top + ov))
    htt = Lt("Cam Tower Thickness") * 0.5
    towers = b.array(b.box(b.P(x_m0 - htt, -(Wh2 + ov), z_pk - ov), b.P(x_m0 + htt, Wh2 + ov, z_head_top + ov * 2.0)), (7, 1, 1), pitch_vec)
    pocket = b.subtract(pocket_box, [towers])
    r_cb = Lt("Cam Journal Diameter") * 0.5 + Lt("Cam Bearing Clearance")
    cam_bores = [b.cyl(b.P(-(Lh + ov), y_cam[k], z_cam), b.P(Lh + ov, y_cam[k], z_cam), r_cb) for k in ("Intake", "Exhaust")]
    head_solid = b.subtract(env_head, [head_cuts, "Head Bolt Holes", pocket] + cam_bores)
    b.var("Cylinder Head solid", head_solid)
    b.use_section("ENGINE ASSEMBLY")
    b.intersect(["Cylinder Head solid", "Cutaway Box"], name="Cylinder Head")
    done("CYLINDER HEAD")

    # ---- CHECKS --------------------------------------------------------------
    section("CHECKS")
    b.math_section = "CHECKS"
    mm = Lt("One Millimetre")
    disp = b.op("div", B * B * S * Lt("Displacement Factor"), Lt("One Cubic Centimetre"), name="CHECK Displacement cc")
    b.op("div", z_deck, mm, name="CHECK Deck Height mm")
    b.op("div", K[1]["zp"], mm, name="CHECK Cyl1 Piston Pin Z mm")
    b.op("mul", K[1]["beta"], -1.0, name="CHECK Cyl1 Rod Angle deg")
    b.op("div", K[1]["lift_int"], mm, name="CHECK Cyl1 Intake Lift mm")
    b.op("div", K[1]["lift_exh"], mm, name="CHECK Cyl1 Exhaust Lift mm")
    b.op("div", K[3]["zp"], mm, name="CHECK Cyl3 Piston Pin Z mm")
    b.bbox_coord("Piston Cyl 1", "max", "z", "CHECK Piston1 Crown Z mm")
    b.bbox_coord("Piston Cyl 1", "min", "x", "CHECK Piston1 Min X mm")
    b.bbox_coord("Connecting Rod Cyl 1", "max", "z", "CHECK Rod1 Top Z mm")
    b.bbox_coord("Cam Lobe", "max", "z", "CHECK Lobe Max Z mm")
    b.bbox_coord("Cam Lobe", "min", "z", "CHECK Lobe Min Z mm")
    b.bbox_coord("Cam Lobe", "max", "y", "CHECK Lobe Max Y mm")
    b.bbox_coord("Intake Valves Cyl 1", "min", "z", "CHECK Intake1 Min Z mm")
    b.bbox_coord("Crankshaft", "max", "z", "CHECK Crank Max Z mm")
    b.bbox_coord("Cylinder Block", "max", "z", "CHECK Block Max Z mm")
    b.bbox_coord("Cylinder Head", "max", "z", "CHECK Head Max Z mm")
    b.op("div", z_cam, mm, name="CHECK Cam Axis Z mm")
    b.op("div", y_cam_i, mm, name="CHECK Intake Cam Y mm")
    # Exact extents of un-rotated bodies; verify() compares them with the spec.
    for part, which, coord in EXTENT_CHECKS:
        b.bbox_coord(part, which, coord, "CHECK %s %s %s mm" % (part, which, coord))
    # Rod swing clearance: largest |y| any big end reaches, against the crankcase inner wall.
    rod_reach = r + b.max(Lt("Rod Cap Boss Half Width"), Lt("Rod Bolt Spacing") * 0.5 + Lt("Rod Bolt Head Diameter") * 0.5)
    b.op("div", (Wc2 - Lt("Block Side Wall")) - rod_reach, mm, name="CHECK Rod To Crankcase Wall mm")
    b.op("div", (Wc2 - Lt("Block Side Wall")) - Lt("Counterweight Radius"), mm, name="CHECK Counterweight To Wall mm")
    done("CHECKS")

    # Exports are added afterwards with engine.exports(); meshing the big
    # parts inside the import made it run for an hour.

    nb.save_notebook_as(NOTEBOOK_PATH)
    summary = {
        "notebook": NOTEBOOK_PATH,
        "literals_landed_in": landed,
        "blocks": b.n_blocks,
        "variables": b.n_vars,
        "seconds": round(time.perf_counter() - t_start, 1),
        "section_seconds": timing,
        "sections": [s["name"] for s in nb.list_sections()],
    }
    with open(os.path.join(OUT_DIR, "engine_build.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    return summary


# ============================================================================


FULL_RECIPE = os.path.join(OUT_DIR, "engine_full.json")
LAYOUT = os.path.join(OUT_DIR, "engine_layout.json")

SECTION_ORDER = ["INPUTS", "MATH - DIMENSIONS", "MATH - KINEMATICS", "MATH - SPRING FIELDS", "CRANKSHAFT", "CONNECTING RODS",
                 "PISTONS", "CYLINDER BLOCK", "CYLINDER HEAD", "VALVETRAIN", "CAMSHAFTS", "CHECKS",
                 "ENGINE ASSEMBLY", "EXPORT"]

# The renderable bodies and their display colours (RGBA, 0-1).
_STEEL = [0.55, 0.60, 0.68, 1.0]
_ALU = [0.80, 0.81, 0.83, 1.0]
_DARK = [0.42, 0.44, 0.47, 1.0]
FINAL_BODY_COLORS = {"Crankshaft": _STEEL, "Intake Camshaft": [0.83, 0.68, 0.30, 1.0],
                     "Exhaust Camshaft": [0.83, 0.68, 0.30, 1.0], "Cylinder Block": _ALU,
                     "Cylinder Head": [0.72, 0.74, 0.77, 1.0], "Bedplate": _DARK, "Oil Pan": _DARK}
for _i in range(1, 7):
    FINAL_BODY_COLORS["Piston Cyl %d" % _i] = [0.90, 0.90, 0.88, 1.0]
    FINAL_BODY_COLORS["Connecting Rod Cyl %d" % _i] = [0.85, 0.50, 0.20, 1.0]
    FINAL_BODY_COLORS["Intake Valves Cyl %d" % _i] = [0.30, 0.65, 0.35, 1.0]
    FINAL_BODY_COLORS["Exhaust Valves Cyl %d" % _i] = [0.75, 0.25, 0.25, 1.0]
    FINAL_BODY_COLORS["Intake Springs Cyl %d" % _i] = [0.35, 0.38, 0.42, 1.0]
    FINAL_BODY_COLORS["Exhaust Springs Cyl %d" % _i] = [0.35, 0.38, 0.42, 1.0]


def make_recipe():
    """Run `build` against the recording backend and write the full recipe.

    Runs anywhere Python runs; nTop is not involved. Returns the summary.
    """
    import recipe_backend
    recipe_backend = importlib.reload(recipe_backend)
    rn = recipe_backend.RecipeNotebook()
    summary = build(rn)
    summary["recipe"] = rn.write(FULL_RECIPE)
    layout = {"sections": SECTION_ORDER, "variables": rn.var_section, "final_bodies": FINAL_BODY_COLORS}
    with open(LAYOUT, "w", encoding="utf-8") as fh:
        json.dump(layout, fh, indent=1)
    summary["layout"] = {"path": LAYOUT, "per_section": {
        sec: sum(1 for v in rn.var_section.values() if v == sec) for sec in SECTION_ORDER}}
    return summary


def import_full(notebook):
    """new_notebook(), import the full recipe in one call, save. Scratch only."""
    if not os.path.isfile(FULL_RECIPE):
        raise RuntimeError("%s missing; run make_recipe() first" % FULL_RECIPE)
    t0 = time.perf_counter()
    notebook.new_notebook()
    notebook.import_recipe(FULL_RECIPE)
    t_import = time.perf_counter() - t0
    names = [v["id"] for v in notebook.list_variables()]
    notebook.save_notebook_as(NOTEBOOK_PATH)
    out = {"import_seconds": round(t_import, 1), "variables": len(names),
           "has_crankshaft": "Crankshaft" in names, "has_head": "Cylinder Head" in names,
           "sections": [s["name"] for s in notebook.list_sections()], "notebook": NOTEBOOK_PATH}
    with open(os.path.join(OUT_DIR, "engine_import.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    return out


def _read(nb, name):
    try:
        return nb.get_block_input(name, "Input")
    except Exception as exc:
        return "ERR " + str(exc)[:200]


def checks(notebook):
    """Read every CHECK variable and compare with engine_spec.expected()."""
    import math

    nb = notebook
    theta = nb.get_block_input("Crank Angle", "Input")
    exp = spec.expected(theta)
    c1 = exp["cylinders"][1]
    L = spec.L
    t = math.radians(spec.A("Valve Tilt"))
    Din = L("Intake Valve Diameter")
    R, rn, lift = L("Cam Base Radius"), L("Cam Nose Radius"), L("Cam Lift")
    d = R + lift - rn
    cosphi = (R - rn) / d
    sinphi = math.sqrt(1 - cosphi ** 2)
    H = L("Valve Length") + L("Bucket Floor") + R
    # lowest point of the tilted intake valve head at its current lift
    head_low = (exp["z_seat"] - c1["lift_intake"] * math.cos(t)
                - L("Valve Head Thickness") * math.cos(t) - (Din / 2 - L("Valve Head Margin")) * math.sin(t))
    expected = {
        "CHECK Displacement cc": exp["displacement_cc"],
        "CHECK Deck Height mm": exp["deck_height"],
        "CHECK Cyl1 Piston Pin Z mm": c1["z_pin_piston"],
        "CHECK Cyl1 Rod Angle deg": c1["rod_angle_deg"],
        "CHECK Cyl1 Intake Lift mm": c1["lift_intake"],
        "CHECK Cyl1 Exhaust Lift mm": c1["lift_exhaust"],
        "CHECK Cyl3 Piston Pin Z mm": exp["cylinders"][3]["z_pin_piston"],
        "CHECK Piston1 Crown Z mm": c1["crown_z"],
        "CHECK Piston1 Min X mm": c1["x"] - (L("Bore") / 2 - L("Piston Clearance")),
        "CHECK Rod1 Top Z mm": c1["z_pin_piston"] + L("Rod Small End Radius"),
        "CHECK Lobe Max Z mm": d + rn,
        "CHECK Lobe Min Z mm": -R,
        "CHECK Lobe Max Y mm": R,
        "CHECK Intake1 Min Z mm": head_low,
        # the teeth are a polar array; nTop pads a polar array's bounding box (+3 mm measured), so this reads 151 for 148
        "CHECK Crank Max Z mm": L("Flywheel Diameter") / 2 + L("Ring Gear Tooth Height"),
        "CHECK Block Max Z mm": exp["deck_height"],
        "CHECK Head Max Z mm": exp["deck_height"] + L("Head Height"),
        "CHECK Cam Axis Z mm": exp["z_seat"] + H * math.cos(t),
        "CHECK Intake Cam Y mm": L("Valve Offset") + H * math.sin(t),
    }
    rows = []
    worst = 0.0
    for name, want in expected.items():
        got = _read(nb, name)
        row = {"check": name, "expected": want, "measured": got}
        if isinstance(got, (int, float)):
            row["delta"] = got - want
            worst = max(worst, abs(row["delta"]))
        rows.append(row)
    result = {"crank_angle_deg": theta, "worst_abs_delta": worst, "rows": rows}
    with open(os.path.join(OUT_DIR, "engine_checks_%03d.json" % (int(round(theta)) % 1000)), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    return result


def set_angle(notebook, deg, max_wait_s=900.0):
    """Set the crank angle (degrees) and read it back.

    A no-op set (same value) and a set while the notebook is still evaluating
    both raise "was not carried out"; skip the first and keep retrying the
    second every 5 s until the notebook accepts it or max_wait_s passes.
    """
    import time as _time
    cur = notebook.get_block_input("Crank Angle", "Input")
    if abs(float(cur) - float(deg)) < 1e-9:
        return cur
    deadline = _time.time() + max_wait_s
    while True:
        try:
            notebook.set_block_input("Crank Angle", "Input", float(deg))
            break
        except RuntimeError as e:
            if "not carried out" not in str(e) or _time.time() > deadline:
                raise
            _time.sleep(5.0)
    return notebook.get_block_input("Crank Angle", "Input")


def exports(notebook, parts=None):
    """Add mesh + STL export blocks for `parts` (default: all) in an EXPORT section.

    Each export fires as soon as it is wired, so add the small parts first
    and watch exports/ before committing to the block and head.
    """
    nb = notebook
    have = {v["id"] for v in nb.list_variables()}
    b = Builder(nb, have)
    b.use_section("EXPORT")
    made = []
    for part in (parts or list(spec.EXPORT_PARTS)):
        fname, tol = spec.EXPORT_PARTS[part]
        pv = spec.export_path_var(part)
        if part not in have or pv not in have:
            made.append({"part": part, "skipped": "missing %s" % ("part" if part not in have else pv)})
            continue
        if ("Export " + part) in have:
            made.append({"part": part, "skipped": "already exported"})
            continue
        t0 = time.perf_counter()
        mesh = b.add("mesh")
        b.wire(part, mesh, "Body")
        b.wire(b.lit(tol), mesh, "Tolerance")
        exp = b.add("export_mesh")
        b.wire(pv, exp, "Path")
        b.wire(mesh, exp, "Mesh")
        b.var("Export " + part, exp)
        made.append({"part": part, "file": fname, "seconds": round(time.perf_counter() - t0, 1)})
    return made


# ============================================================================


def verify(notebook):
    """Exact part-extent checks, a crank-angle sweep, and a zero-tilt valve test.

    Bounding boxes of rotated bodies and of polar arrays come back padded
    (the rotated axis-aligned box, not the tight box), so the extent checks
    here are on bodies in their local, un-rotated frame, and the valve
    transform chain is checked with `Valve Tilt` set to zero, where the box
    is exact. Restores Crank Angle 0 and the design tilt, then saves.
    """
    import math

    nb = notebook
    L = spec.L
    have = {v["id"] for v in nb.list_variables()}
    b = Builder(nb, have)
    b.use_section("Section 1")
    r = L("Stroke") / 2
    rod = L("Rod Length")
    Lh = 3 * L("Bore Pitch") + L("Block End Wall")
    x_m0 = -3 * L("Bore Pitch")
    x_fl0 = x_m0 - L("Main Journal Width") / 2 - L("Rear Flange Thickness")
    extents = {
        ("Crank Throw", "max", "z"): r + L("Pin Eye Radius"),
        ("Crank Throw", "min", "z"): -L("Counterweight Radius"),
        ("Crank Throw", "max", "y"): L("Counterweight Half Width"),
        ("Crank Throw", "max", "x"): L("Rod Journal Width") / 2 + (L("Bore Pitch") - L("Rod Journal Width") - L("Main Journal Width")) / 2,
        ("Piston", "max", "z"): L("Compression Height"),
        ("Piston", "min", "z"): -(L("Piston Length") - L("Compression Height")),
        ("Piston", "max", "x"): L("Bore") / 2 - L("Piston Clearance"),
        ("Connecting Rod", "max", "z"): rod + L("Rod Small End Radius"),
        ("Connecting Rod", "min", "z"): -(L("Rod Big End Radius") + L("Rod Bolt Head Height")),
        ("Connecting Rod", "max", "y"): max(L("Rod Cap Boss Half Width"), L("Rod Bolt Spacing") / 2 + L("Rod Bolt Head Diameter") / 2),
        ("Connecting Rod", "max", "x"): L("Rod Big End Width") / 2,
        ("Intake Valve", "max", "z"): L("Valve Length") + L("Bucket Floor"),
        ("Intake Valve", "min", "z"): -L("Valve Head Thickness"),
        ("Intake Valve", "max", "x"): L("Intake Valve Diameter") / 2,
        ("Crankshaft at TDC", "min", "x"): x_fl0 - L("Flywheel Thickness") - L("Flywheel Bolt Head Height"),
        ("Crankshaft at TDC", "max", "x"): 3 * L("Bore Pitch") + L("Main Journal Width") / 2 + L("Crank Nose Length"),
        ("Cylinder Block", "min", "z"): 0.0,
        ("Cylinder Block", "max", "x"): Lh,
        ("Cylinder Block", "max", "y"): L("Crankcase Width") / 2,
        ("Cylinder Head", "max", "y"): L("Head Width") / 2,
        ("Cylinder Head", "max", "x"): Lh,
        ("Intake Camshaft static", "max", "x"): Lh + L("Cam Sprocket Offset") + L("Cam Sprocket Width"),
        ("Intake Camshaft static", "min", "x"): -Lh + L("Cam Sprocket Offset"),
        ("Bedplate", "min", "z"): -L("Bedplate Depth"),
        ("Oil Pan", "min", "z"): -(L("Bedplate Depth") + L("Oil Pan Depth")),
    }
    rows = []
    named = {("CHECK Rod To Crankcase Wall mm",): (L("Crankcase Width") / 2 - L("Block Side Wall")) - (
        r + max(L("Rod Cap Boss Half Width"), L("Rod Bolt Spacing") / 2 + L("Rod Bolt Head Diameter") / 2)),
        ("CHECK Counterweight To Wall mm",): (L("Crankcase Width") / 2 - L("Block Side Wall")) - L("Counterweight Radius")}
    for (name,), want in named.items():
        if name in have:
            got = _read(nb, name)
            row = {"check": name, "expected": want, "measured": got}
            if isinstance(got, (int, float)):
                row["delta"] = got - want
            rows.append(row)
    for (part, which, coord), want in extents.items():
        name = "CHECK %s %s %s mm" % (part, which, coord)
        if name not in have:
            b.bbox_coord(part, which, coord, name)
        got = _read(nb, name)
        row = {"check": name, "expected": want, "measured": got}
        if isinstance(got, (int, float)):
            row["delta"] = got - want
        rows.append(row)
    worst_extent = max(abs(rw["delta"]) for rw in rows if "delta" in rw)

    sweep = []
    for deg in (0.0, 90.0, 180.0, 270.0, 470.0, 615.0):
        set_angle(nb, deg)
        res = checks(nb)
        kin = [rw for rw in res["rows"] if rw["check"] in (
            "CHECK Cyl1 Piston Pin Z mm", "CHECK Cyl1 Rod Angle deg", "CHECK Cyl1 Intake Lift mm",
            "CHECK Cyl1 Exhaust Lift mm", "CHECK Cyl3 Piston Pin Z mm", "CHECK Piston1 Crown Z mm",
            "CHECK Rod1 Top Z mm", "CHECK Piston1 Min X mm")]
        sweep.append({"deg": deg, "worst_kinematic_delta": max(abs(rw.get("delta", 1e9)) for rw in kin),
                      "rows": kin})

    # zero tilt: the valve box is exact, so this checks the translate/rotate chain and lift sign
    tilt_design = nb.get_block_input("Valve Tilt", "Input")
    nb.set_block_input("Valve Tilt", "Input", 0.0)
    zero_tilt = []
    for deg in (0.0, 470.0):
        set_angle(nb, deg)
        exp = spec.expected(deg)
        want = exp["z_seat"] - exp["cylinders"][1]["lift_intake"] - L("Valve Head Thickness")
        got = _read(nb, "CHECK Intake1 Min Z mm")
        zero_tilt.append({"deg": deg, "expected": want, "measured": got,
                          "delta": (got - want) if isinstance(got, (int, float)) else None,
                          "lift": exp["cylinders"][1]["lift_intake"]})
    nb.set_block_input("Valve Tilt", "Input", float(tilt_design))
    set_angle(nb, 0.0)
    nb.save_notebook()

    result = {"extent_rows": rows, "worst_extent_delta_mm": worst_extent, "sweep": sweep,
              "zero_tilt": zero_tilt, "tilt_restored_deg": nb.get_block_input("Valve Tilt", "Input")}
    with open(os.path.join(OUT_DIR, "engine_verify.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, default=str)
    return {"worst_extent_delta_mm": worst_extent,
            "sweep_worst": [(s["deg"], s["worst_kinematic_delta"]) for s in sweep],
            "zero_tilt": [(z["deg"], z["delta"]) for z in zero_tilt]}


# ============================================================================
# Read-only pieces of verify(), for a sweep driven from outside nTop so the
# viewport can be captured between angles (tools/sweep_and_capture.ps1).


def extents(notebook):
    """Compare every CHECK extent and clearance scalar with the spec. Read-only."""
    import math

    nb = notebook
    L = spec.L
    r = L("Stroke") / 2
    rod = L("Rod Length")
    Lh = 3 * L("Bore Pitch") + L("Block End Wall")
    x_m0 = -3 * L("Bore Pitch")
    x_fl0 = x_m0 - L("Main Journal Width") / 2 - L("Rear Flange Thickness")
    inner = L("Crankcase Width") / 2 - L("Block Side Wall")
    want = {
        "CHECK Crank Throw max z mm": r + L("Pin Eye Radius"),
        "CHECK Crank Throw min z mm": -L("Counterweight Radius"),
        "CHECK Crank Throw max y mm": L("Counterweight Half Width"),
        "CHECK Crank Throw max x mm": L("Rod Journal Width") / 2 + (L("Bore Pitch") - L("Rod Journal Width") - L("Main Journal Width")) / 2,
        "CHECK Piston max z mm": L("Compression Height"),
        "CHECK Piston min z mm": -(L("Piston Length") - L("Compression Height")),
        "CHECK Piston max x mm": L("Bore") / 2 - L("Piston Clearance"),
        "CHECK Connecting Rod max z mm": rod + L("Rod Small End Radius"),
        "CHECK Connecting Rod min z mm": -(L("Rod Big End Radius") + L("Rod Bolt Head Height")),
        "CHECK Connecting Rod max y mm": max(L("Rod Cap Boss Half Width"), L("Rod Bolt Spacing") / 2 + L("Rod Bolt Head Diameter") / 2),
        "CHECK Connecting Rod max x mm": L("Rod Big End Width") / 2,
        "CHECK Intake Valve max z mm": L("Valve Length") + L("Bucket Floor"),
        "CHECK Intake Valve min z mm": -L("Valve Head Thickness"),
        "CHECK Intake Valve max x mm": L("Intake Valve Diameter") / 2,
        "CHECK Crankshaft at TDC min x mm": x_fl0 - L("Flywheel Thickness") - L("Flywheel Bolt Head Height"),
        "CHECK Crankshaft at TDC max x mm": 3 * L("Bore Pitch") + L("Main Journal Width") / 2 + L("Crank Nose Length"),
        "CHECK Cylinder Block min z mm": 0.0,
        "CHECK Cylinder Block max x mm": Lh,
        "CHECK Cylinder Block max y mm": L("Crankcase Width") / 2,
        "CHECK Cylinder Head max y mm": L("Head Width") / 2,
        "CHECK Cylinder Head max x mm": Lh,
        "CHECK Intake Camshaft static max x mm": Lh + L("Cam Sprocket Offset") + L("Cam Sprocket Width"),
        "CHECK Intake Camshaft static min x mm": -Lh + L("Cam Sprocket Offset"),
        "CHECK Bedplate min z mm": -L("Bedplate Depth"),
        "CHECK Oil Pan min z mm": -(L("Bedplate Depth") + L("Oil Pan Depth")),
        "CHECK Rod To Crankcase Wall mm": inner - (r + max(L("Rod Cap Boss Half Width"), L("Rod Bolt Spacing") / 2 + L("Rod Bolt Head Diameter") / 2)),
        "CHECK Counterweight To Wall mm": inner - L("Counterweight Radius"),
    }
    rows, worst = [], 0.0
    for name, w in want.items():
        got = _read(nb, name)
        row = {"check": name, "expected": w, "measured": got}
        if isinstance(got, (int, float)):
            row["delta"] = got - w
            worst = max(worst, abs(row["delta"]))
        rows.append(row)
    out = {"worst_abs_delta_mm": worst, "rows": rows}
    with open(os.path.join(OUT_DIR, "engine_extents.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    return {"worst_abs_delta_mm": worst, "n": len(rows)}


def zero_tilt(notebook, deg):
    """With Valve Tilt at 0 the valve box is exact: check the lowest intake valve point."""
    nb = notebook
    L = spec.L
    exp = spec.expected(deg)
    want = exp["z_seat"] - exp["cylinders"][1]["lift_intake"] - L("Valve Head Thickness")
    got = _read(nb, "CHECK Intake1 Min Z mm")
    out = {"deg": deg, "tilt_deg": nb.get_block_input("Valve Tilt", "Input"), "expected": want, "measured": got,
           "lift": exp["cylinders"][1]["lift_intake"],
           "delta": (got - want) if isinstance(got, (int, float)) else None}
    with open(os.path.join(OUT_DIR, "engine_zero_tilt_%03d.json" % (int(round(deg)) % 1000)), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    return out
