"""Reference implementation for Spline DF lofted surfaces in nTop.

One small field graph with two back ends:

  evaluate()   numpy evaluation on the host, for previews, sections and checks
  Recipe       the same graph written as an nTop recipe of native blocks

Conventions: fields are dimensionless numbers in metres, negative inside. A Spline DF
section is the signed planar distance to a clamped uniform cubic B-spline, positive on the
left of the direction of travel. Needs numpy and scipy. Meshing on the host also needs
scikit-image.

The block identifiers and literal formats were recorded on prototype build 42926. Check them
against the installed build with a small pilot (loft_pilot.py) before a large model.
"""
from __future__ import annotations

import json
import math
import uuid
from pathlib import Path

import numpy as np
from scipy.interpolate import BSpline


# --------------------------------------------------------------------------------------
# Clamped uniform cubic B-splines
# --------------------------------------------------------------------------------------
def knots(n):
    """Knot vector on [0, 1] for n control values (n >= 4)."""
    assert n >= 4
    return np.r_[np.zeros(4), np.arange(1, n - 3) / (n - 3), np.ones(4)]


def greville(n, u0=0.0, u1=1.0):
    """Abscissae at which the control polygon of a function spline is drawn."""
    k = knots(n)
    return np.array([u0 + (u1 - u0) * k[i + 1:i + 4].sum() / 3.0 for i in range(n)])


def fit_guide(us, vs, n, u0=None, u1=None, lam=0.0):
    """Least squares control values of a guide g(u) through the keys (us, vs).

    n is the number of control values: keep it small. lam weights a third-difference
    penalty on the control values, which favours a slowly changing curvature.
    Returns (control values, largest deviation from the keys).
    """
    us, vs = np.asarray(us, float), np.asarray(vs, float)
    u0 = float(us.min()) if u0 is None else float(u0)
    u1 = float(us.max()) if u1 is None else float(u1)
    t = u0 + (u1 - u0) * knots(n)
    A = BSpline.design_matrix(np.clip(us, u0, u1 - 1e-12 * (u1 - u0)), t, 3).toarray()
    rows, rhs = [A], [vs]
    if lam > 0 and n > 3:
        rows.append(np.diff(np.eye(n), 3, axis=0) * lam)
        rhs.append(np.zeros(n - 3))
    ctrl = np.linalg.lstsq(np.vstack(rows), np.concatenate(rhs), rcond=None)[0]
    return ctrl, float(np.abs(A @ ctrl - vs).max())


def guide_fairness(ctrl, u0=0.0, u1=1.0, samples=2001):
    """Count the features of a guide that a reflection would show.

    inflections: sign changes of the second derivative.
    curvature_extrema: sign changes of the third derivative (it is piecewise constant).
    A fair guide has as few of both as the design needs.
    """
    ctrl = np.asarray(ctrl, float)
    spl = BSpline(u0 + (u1 - u0) * knots(len(ctrl)), ctrl, 3)
    u = np.linspace(u0, u1, samples)[1:-1]
    d2, d3 = spl.derivative(2)(u), spl.derivative(3)(u)

    def changes(v):
        v = v[np.abs(v) > 1e-9 * max(1.0, float(np.abs(v).max()))]
        return int(np.count_nonzero(np.sign(v[1:]) != np.sign(v[:-1])))

    return dict(control_values=len(ctrl), inflections=changes(d2), curvature_extrema=changes(d3),
                max_abs_second_derivative=float(np.abs(d2).max()))


class _Basis:
    """Per-span power-basis matrices of the clamped uniform cubic B-spline with K control points."""
    _cache: dict = {}

    @classmethod
    def get(cls, K, per_span=8):
        if (K, per_span) not in cls._cache:
            cls._cache[(K, per_span)] = cls(K, per_span)
        return cls._cache[(K, per_span)]

    def __init__(self, K, per_span):
        ns = K - 3
        kn = knots(K)
        tau = np.array([0.125, 0.375, 0.625, 0.875])
        V = np.vander(tau, 4, increasing=True)
        self.M = np.zeros((ns, 4, 4))                       # [span, power, local control point]
        for sp in range(ns):
            B = BSpline.design_matrix((sp + tau) / ns, kn, 3).toarray()[:, sp:sp + 4]
            self.M[sp] = np.linalg.solve(V, B)
        self.ts = np.linspace(0.0, 1.0, ns * per_span + 1)
        self.Bs = BSpline.design_matrix(np.clip(self.ts, 0.0, 1.0 - 1e-12), kn, 3).toarray()
        self.Bs[-1] = 0.0
        self.Bs[-1, -1] = 1.0
        self.ns, self.dt = ns, 1.0 / (ns * per_span)

    def curve(self, P, t, order=0):
        """P (N, K, 2), t (N,): the point and its derivatives up to `order`, each (N, 2)."""
        ns = self.ns
        sp = np.clip(np.floor(t * ns).astype(int), 0, ns - 1)
        tau = t * ns - sp
        idx = sp[:, None] + np.arange(4)[None, :]
        Pl = np.take_along_axis(P, np.repeat(idx[:, :, None], 2, axis=2), axis=1)
        Ms = self.M[sp]
        one, zero = np.ones_like(tau), np.zeros_like(tau)
        out = [np.einsum('np,npj,njc->nc', np.stack([one, tau, tau ** 2, tau ** 3], 1), Ms, Pl)]
        if order >= 1:
            out.append(np.einsum('np,npj,njc->nc', np.stack([zero, one, 2 * tau, 3 * tau ** 2], 1) * ns, Ms, Pl))
        if order >= 2:
            out.append(np.einsum('np,npj,njc->nc', np.stack([zero, zero, 2 * one, 6 * tau], 1) * ns * ns, Ms, Pl))
        return out


def _unit(v):
    return v / np.maximum(np.sqrt((v * v).sum(-1, keepdims=True)), 1e-30)


def _spline_block(P, q, closed, per_span):
    K = P.shape[1]
    sb = _Basis.get(K, per_span)
    Cs = np.einsum('tk,nkc->ntc', sb.Bs, P)
    t = sb.ts[((Cs - q[:, None, :]) ** 2).sum(-1).argmin(1)]
    del Cs

    def polish(t):
        for _ in range(8):
            C, C1, C2 = sb.curve(P, t, 2)
            r = C - q
            g = (r * C1).sum(-1)
            hg = (C1 * C1).sum(-1)
            h = hg + (r * C2).sum(-1)
            # Newton where the second derivative is safely positive, Gauss-Newton elsewhere
            h = np.maximum(np.where(h > 0.3 * hg, h, hg), 1e-12)
            t = np.clip(t - np.clip(g / h, -sb.dt, sb.dt), 0.0, 1.0)
        return t

    t = polish(t)
    lo_end, hi_end = t <= 1e-9, t >= 1.0 - 1e-9
    if closed and (lo_end | hi_end).any():
        # the seam of a closed curve is one point with two parameters
        t2 = polish(np.where(lo_end, 1.0, 0.0))
        d1 = ((sb.curve(P, t, 0)[0] - q) ** 2).sum(-1)
        d2 = ((sb.curve(P, t2, 0)[0] - q) ** 2).sum(-1)
        t = np.where((lo_end | hi_end) & (d2 < d1), t2, t)
    C, C1 = sb.curve(P, t, 1)
    tan = _unit(C1)
    ends = (t <= 1e-9) | (t >= 1.0 - 1e-9)
    if closed and ends.any():
        z = np.zeros_like(t)
        both = _unit(sb.curve(P, z, 1)[1]) + _unit(sb.curve(P, z + 1.0, 1)[1])
        tan = np.where(ends[:, None], _unit(both), tan)
    nrm = np.stack([-tan[:, 1], tan[:, 0]], -1)             # left of the direction of travel
    r = q - C
    side = (r * nrm).sum(-1)
    dist = np.sqrt((r * r).sum(-1) + 1e-30)
    sd = np.where(~ends, side, np.where(side > 0, dist, -dist))
    if not closed:
        best = dist
        for point, tangent, forward in ((P[:, 0], _unit(P[:, 1] - P[:, 0]), -1.0),
                                        (P[:, -1], _unit(P[:, -1] - P[:, -2]), 1.0)):
            along = ((q - point) * tangent).sum(-1) * forward
            foot = point + (np.maximum(along, 0.0) * forward)[:, None] * tangent
            rr = q - foot
            rd = np.sqrt((rr * rr).sum(-1) + 1e-30)
            perp = np.stack([-tangent[:, 1], tangent[:, 0]], -1)
            rs = ((q - point) * perp).sum(-1)
            ray_sd = np.where(along > 0, rs, np.where(rs > 0, rd, -rd))
            take = rd < best - 1e-12
            sd = np.where(take, ray_sd, sd)
            best = np.where(take, rd, best)
    return sd


def spline_distance(P, q, closed=None, per_span=8):
    """Signed planar distance to a clamped uniform cubic B-spline (the Spline DF value).

    P: control points, (K, 2) for a fixed curve or (N, K, 2) when they differ per query point.
    q: query points (N, 2). Positive on the left of the direction of travel. An open curve is
    continued by straight rays along its end tangents. closed defaults to first point == last.
    """
    q = np.atleast_2d(np.asarray(q, float))
    P = np.asarray(P, float)
    if closed is None:
        closed = bool(np.allclose(P[..., 0, :], P[..., -1, :]))
    if P.ndim == 2:
        P = np.broadcast_to(P, (len(q),) + P.shape)
    block = max(2000, int(6_000_000 // ((P.shape[1] - 3) * per_span + 1)))
    out = [_spline_block(P[i:i + block], q[i:i + block], closed, per_span) for i in range(0, len(q), block)]
    return np.concatenate(out)


# --------------------------------------------------------------------------------------
# Field graph
# --------------------------------------------------------------------------------------
class F:
    """Scalar field node. Build with the operators and helpers below."""
    __slots__ = ('op', 'args', 'val', 'label')

    def __init__(self, op, args=(), val=None):
        self.op, self.args, self.val, self.label = op, tuple(args), val, None

    def named(self, label):
        """A named node becomes a named variable in the notebook."""
        self.label = label
        return self

    def __add__(self, o): return _binary('add', self, o)
    def __radd__(self, o): return _binary('add', o, self)
    def __sub__(self, o): return _binary('sub', self, o)
    def __rsub__(self, o): return _binary('sub', o, self)
    def __mul__(self, o): return _binary('mul', self, o)
    def __rmul__(self, o): return _binary('mul', self, o)
    def __truediv__(self, o): return _binary('div', self, o) if isinstance(o, F) else self * (1.0 / o)
    def __rtruediv__(self, o): return _binary('div', o, self)
    def __neg__(self): return self * -1.0


def const(v):
    return F('const', (), float(v))


def lift(v):
    return v if isinstance(v, F) else const(v)


_FOLD = {'add': lambda a, b: a + b, 'sub': lambda a, b: a - b, 'mul': lambda a, b: a * b, 'div': lambda a, b: a / b}


def _binary(op, a, b):
    a, b = lift(a), lift(b)
    if a.op == 'const' and b.op == 'const':          # constants fold, so no block takes two literals
        return const(_FOLD[op](a.val, b.val))
    return F(op, (a, b))


X, Y, Z = F('x'), F('y'), F('z')


def absf(a):
    a = lift(a)
    return const(abs(a.val)) if a.op == 'const' else F('abs', (a,))


def sqrt(a):
    a = lift(a)
    return const(math.sqrt(max(a.val, 0.0))) if a.op == 'const' else F('sqrt', (a,))


def _nary(op, fold, vals):
    vals = [lift(v) for v in vals]
    fields = [v for v in vals if v.op != 'const']
    consts = [v.val for v in vals if v.op == 'const']
    if consts:
        fields.append(const(fold(consts)))
    return fields[0] if len(fields) == 1 else F(op, fields)


def fmin(*a):
    return _nary('min', min, a)


def fmax(*a):
    return _nary('max', max, a)


def clamp(v, lo, hi):
    return F('clamp', (lift(v), lift(lo), lift(hi)))


def length2(a, b):
    a, b = lift(a), lift(b)
    return sqrt(a * a + b * b)


def smootherstep(e0, e1, v):
    """C2 step from 0 at e0 to 1 at e1."""
    t = clamp((lift(v) - e0) * (1.0 / (e1 - e0)), 0.0, 1.0)
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def sminq(a, b, k):
    """Compact quartic smooth minimum, C2 at the edge of its support.

    Equal to min(a, b) wherever |a - b| >= k. k is the blend width in field units and may be
    a field, so a blend can stay tight in one place and open in another. Where a = b the
    result lies 3k/16 below both.
    """
    a, b = lift(a), lift(b)
    q = fmax(1.0 - absf(a - b) / k, 0.0)
    return fmin(a, b) - (q * q * q) * (4.0 - q) * (k * (1.0 / 16.0))


def smaxq(a, b, k):
    """Compact quartic smooth maximum: the intersection counterpart of sminq."""
    return -sminq(-lift(a), -lift(b), k)


def skin(E, lo, hi):
    """The layer lo <= E <= hi of an envelope field E (lo and hi are offsets, negative inward)."""
    return fmax(lift(E) - hi, lo - lift(E))


def bead(mask, E, offset, r):
    """Round bead of radius r along the edge of a region mask, lying `offset` under the surface E."""
    return length2(mask, lift(E) + offset) - r


class Guide:
    """Fair function g(u) on [u0, u1]: a clamped uniform cubic B-spline from few control values.

    Call it with a field to get a field (a native spline in nTop), or with numbers.
    """
    _names: set = set()

    def __init__(self, name, u0, u1, ctrl, deviation=None):
        assert name not in Guide._names, 'duplicate guide name: ' + name
        Guide._names.add(name)
        self.name, self.u0, self.u1 = name, float(u0), float(u1)
        self.ctrl = [float(c) for c in ctrl]
        assert len(self.ctrl) >= 4
        self.deviation = deviation
        self.spline = BSpline(self.u0 + (self.u1 - self.u0) * knots(len(self.ctrl)), np.array(self.ctrl), 3)
        self.greville = greville(len(self.ctrl), self.u0, self.u1)
        # the native curve is drawn at a positive height, because the axis distance is unsigned
        self.offset = float(math.ceil(max(0.0, -min(self.ctrl))) + 1.0)

    @classmethod
    def fit(cls, name, us, vs, n, u0=None, u1=None, lam=0.0):
        us = np.asarray(us, float)
        u0 = float(us.min()) if u0 is None else u0
        u1 = float(us.max()) if u1 is None else u1
        ctrl, dev = fit_guide(us, vs, n, u0, u1, lam)
        return cls(name, u0, u1, ctrl, deviation=dev)

    def __call__(self, u):
        if isinstance(u, F):
            return F('guide', (clamp(u, self.u0, self.u1),), self)
        return self.spline(np.clip(u, self.u0, self.u1))

    def fairness(self):
        return dict(name=self.name, max_deviation=self.deviation, **guide_fairness(self.ctrl, self.u0, self.u1))


def spline2d(cps, u, v, label=None):
    """Native Spline DF. cps: (a, b) control points in the section plane, numbers or fields.
    u, v: the section coordinates of the query point.

    Control points that are fields of the third coordinate turn the section into a loft.
    The curve is closed when the first and last control points are the same.
    """
    cps = [(lift(a), lift(b)) for a, b in cps]
    assert len(cps) >= 4, 'a cubic Spline DF needs at least four control points'

    def same(p, q):
        return p is q or (p.op == 'const' and q.op == 'const' and p.val == q.val)

    closed = same(cps[0][0], cps[-1][0]) and same(cps[0][1], cps[-1][1])
    node = F('spline', [lift(u), lift(v)] + [c for pair in cps for c in pair], (3, len(cps), closed))
    node.label = label
    return node


def rounded_polygon(pts, r, max_gap=0.22):
    """Control points of a closed cubic B-spline that follows a polygon with rounded corners.

    Three control points per corner: one on each edge at distance r and the corner itself.
    Long edges get extra collinear points, so the parameter speed stays even. The loop is
    ordered clockwise (negative inside) and closes at the middle of its longest straight leg.
    """
    P = np.asarray(pts, float)
    if np.linalg.norm(P[0] - P[-1]) < 1e-9:
        P = P[:-1]
    area = 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1])
    if area > 0:
        P = P[::-1]
    n = len(P)
    corners = []
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        la, lc = np.linalg.norm(a - b), np.linalg.norm(c - b)
        corners.append([b + (a - b) / la * min(r, 0.45 * la), b, b + (c - b) / lc * min(r, 0.45 * lc)])
    full = []
    for i in range(n):
        full += corners[i]
        p0, p1 = corners[i][2], corners[(i + 1) % n][0]
        m = int(np.linalg.norm(p1 - p0) // max_gap)
        full += [p0 + (p1 - p0) * (j + 1) / (m + 1) for j in range(m)]
    out = np.array(full)
    k = int(np.argmax(np.linalg.norm(np.roll(out, -1, axis=0) - out, axis=1)))
    out = np.roll(out, -(k + 1), axis=0)
    mid = 0.5 * (out[0] + out[-1])
    return np.vstack([mid, out, mid])


def region(label, pts, u, v, r=0.02):
    """Closed region mask from polygon vertices in the (u, v) plane. Negative inside."""
    return spline2d([(float(a), float(b)) for a, b in rounded_polygon(pts, r)], u, v, label=label)


# --------------------------------------------------------------------------------------
# Host evaluation
# --------------------------------------------------------------------------------------
def _topo(roots):
    seen, order = set(), []
    stack = [(r, False) for r in roots]
    while stack:
        n, done = stack.pop()
        if done:
            order.append(n)
        elif id(n) not in seen:
            seen.add(id(n))
            stack.append((n, True))
            stack.extend((a, False) for a in n.args)
    return order


def evaluate(fields, x, y, z):
    """Evaluate one field or a list of fields at numpy arrays x, y, z of one shape."""
    single = isinstance(fields, F)
    roots = [fields] if single else list(fields)
    x, y, z = (np.asarray(v, float) for v in (x, y, z))
    val = {}
    for n in _topo(roots):
        a = [val[id(c)] for c in n.args]
        op = n.op
        if op == 'const':
            v = np.full(x.shape, n.val)
        elif op in ('x', 'y', 'z'):
            v = {'x': x, 'y': y, 'z': z}[op]
        elif op == 'add': v = a[0] + a[1]
        elif op == 'sub': v = a[0] - a[1]
        elif op == 'mul': v = a[0] * a[1]
        elif op == 'div': v = a[0] / a[1]
        elif op == 'abs': v = np.abs(a[0])
        elif op == 'sqrt': v = np.sqrt(np.maximum(a[0], 0.0))
        elif op == 'min': v = np.minimum.reduce(a)
        elif op == 'max': v = np.maximum.reduce(a)
        elif op == 'clamp': v = np.minimum(np.maximum(a[0], a[1]), a[2])
        elif op == 'guide': v = n.val.spline(a[0])
        elif op == 'spline':
            _, K, closed = n.val
            q = np.stack([a[0].reshape(-1), a[1].reshape(-1)], -1)
            if all(c.op == 'const' for c in n.args[2:]):
                P = np.array([[n.args[2 + 2 * i].val, n.args[3 + 2 * i].val] for i in range(K)])
            else:
                P = np.stack([np.stack([a[2 + 2 * i].reshape(-1), a[3 + 2 * i].reshape(-1)], -1) for i in range(K)], 1)
            v = spline_distance(P, q, closed).reshape(x.shape)
        else:
            raise ValueError(op)
        val[id(n)] = v
    out = [val[id(r)] for r in roots]
    return out[0] if single else out


def probe(field, points):
    p = np.atleast_2d(np.asarray(points, float))
    return evaluate(field, p[:, 0], p[:, 1], p[:, 2])


def surface_distance(field, points, h=1e-4):
    """First-order distance of points from the zero surface: |f| / |grad f| by central differences."""
    p = np.atleast_2d(np.asarray(points, float))
    f = probe(field, p)
    g = np.stack([(probe(field, p + d) - probe(field, p - d)) / (2 * h) for d in np.eye(3) * h], -1)
    return np.abs(f) / np.maximum(np.linalg.norm(g, axis=1), 1e-9)


def field_normals(field, points, h=1e-4):
    """Unit outward normals of the field at the points, by central differences."""
    p = np.asarray(points, float)
    g = np.empty_like(p)
    for k in range(3):
        d = np.zeros(3)
        d[k] = h
        hi_, lo_ = p + d, p - d
        g[:, k] = evaluate(field, hi_[:, 0], hi_[:, 1], hi_[:, 2]) - evaluate(field, lo_[:, 0], lo_[:, 1], lo_[:, 2])
    return g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-30)


def section_grid(field, axis, value, lo, hi, n=400):
    """Sample a field on a cutting plane. axis 0, 1 or 2 is held at `value`; lo and hi bound the
    other two coordinates in axis order. Returns (a, b, values[b, a])."""
    others = [k for k in range(3) if k != axis]
    a = np.linspace(lo[0], hi[0], n)
    b = np.linspace(lo[1], hi[1], max(8, int(round(n * (hi[1] - lo[1]) / (hi[0] - lo[0])))))
    A, B = np.meshgrid(a, b)
    c = [None] * 3
    c[axis], c[others[0]], c[others[1]] = np.full(A.shape, float(value)), A, B
    return a, b, evaluate(field, *c)


def mesh_field(field, lo, hi, h):
    """Marching cubes mesh of the zero surface on a grid of cell size h (needs scikit-image)."""
    from skimage import measure
    ax = [np.arange(lo[k], hi[k] + h, h) for k in range(3)]
    vals = np.empty((len(ax[0]), len(ax[1]), len(ax[2])), np.float32)
    Yg, Zg = np.meshgrid(ax[1], ax[2], indexing='ij')
    for i, xv in enumerate(ax[0]):
        vals[i] = evaluate(field, np.full(Yg.shape, xv), Yg, Zg)
    v, f, n, _ = measure.marching_cubes(vals, 0.0, spacing=(h, h, h))
    return v + np.array(lo, float), f, n


# --------------------------------------------------------------------------------------
# nTop recipe
# --------------------------------------------------------------------------------------
FUNC = {'add': 'add<real_field,real_field>', 'sub': 'subtract<real_field,real_field>',
        'mul': 'multiply<real_field,real_field>', 'div': 'divide<real_field,real_field>',
        'abs': 'abs<real_field>', 'sqrt': 'sqrt<real_field>', 'clamp': 'clamp<real_field,real_field,real_field>'}
SPLINE_DF = 'spline_implicit<list<vector_field_2d>,integer,vector_field_2d>[5.53.0]'
VEC2 = 'vector_field_2d_from_components<real_field,real_field>[5.31.0]'
GUIDE_SPLINE = 'spline_by_control_points<list<point>,integer>[5.20.0]'
GUIDE_DISTANCE = 'curve_axis_distance<curve_interface,axis,vector>[5.30.0]'
REMAP = 'remap<real_field,real_field,real_field,real_field>'


class Recipe:
    """Collects bodies and probes and writes one nTop recipe (JSON) for import or ntopcl."""

    def __init__(self, title, description=''):
        self.title, self.description = title, description
        self.parts, self.checks, self._n = [], [], 0

    def part(self, name, field, lo, hi):
        """An implicit body from a field, with its bounding box corners in metres."""
        self.parts.append((name, lift(field), [float(v) for v in lo], [float(v) for v in hi]))

    def check(self, name, field, point):
        """A native field probe: variable 'CHECK <name>' holds the field value at the point."""
        self.checks.append((name, lift(field), [float(v) for v in point]))

    def _id(self):
        self._n += 1
        return f'n{self._n:07d}'

    @staticmethod
    def real(v, units=None):
        return {'type': 'real', 'value': {'val': float(v), 'isFinite': True, 'units': units or {}}}

    @classmethod
    def length(cls, v):
        return cls.real(v, {'length': 1})

    @staticmethod
    def point(p):
        return {'type': 'point', 'value': [{'val': float(v), 'isFinite': True} for v in p]}

    @staticmethod
    def vec(p):
        return {'type': 'vector', 'value': {'units': {}, 'value': [{'val': float(v), 'isFinite': True} for v in p]}}

    @staticmethod
    def integer(v):
        return {'type': 'integer', 'value': {'val': int(v)}}

    def call(self, func, typ, *inputs):
        return {'func': func, 'type': typ, 'inputs': list(inputs), 'id': self._id(), 'name': func.split('<')[0]}

    def seq(self, typ, vals):
        return self.call('core.list<' + typ + '>', 'list<' + typ + '>', *vals)

    def emit(self, export=None):
        """export: optional dict(part=name, stl=path, tolerance=metres, sharpen=passes)."""
        body, names = [], set()

        def var(name, typ, contents):
            base, k = name, 2
            while name in names:
                name, k = f'{base} ({k})', k + 1
            names.add(name)
            item = {'name': name, 'id': self._id(), 'type': typ, 'contents': contents, 'variable': True}
            body.append(item)
            return {'ref': {'id': item['id']}, 'props': []}

        coord = {}
        for i, ax in enumerate('XYZ'):
            plane = var(ax + ' reference plane', 'plane',
                        self.call('plane_from_normal<point,vector>[1.1.0]', 'plane', self.point([0, 0, 0]),
                                  self.vec([int(j == i) for j in range(3)])))
            coord[ax.lower()] = var(ax + ' coordinate [m]', 'real_field',
                                    self.call('divide<real_field,real_field>', 'real_field',
                                              {'ref': plane['ref'], 'props': ['scalar field']}, self.length(1)))
        roots = [p[1] for p in self.parts] + [c[1] for c in self.checks]
        uses = {}
        for n in _topo(roots):
            for a in n.args:
                uses[id(a)] = uses.get(id(a), 0) + 1
        refs, guides, axis, auto = {}, {}, [], [0]
        leaves = ('const', 'x', 'y', 'z')

        def guide_field(g):
            if g.name not in guides:
                if not axis:
                    axis.append(var('Guide axis', 'axis', self.call('axis<point,vector>', 'axis', self.point([0, 0, 0]),
                                                                    self.vec([1, 0, 0]))))
                pts = var(g.name + ' control points', 'list<point>',
                          self.seq('point', [self.point([u, v + g.offset, 0]) for u, v in zip(g.greville, g.ctrl)]))
                spl = var(g.name + ' spline', 'spline', self.call(GUIDE_SPLINE, 'spline', pts, self.integer(3)))
                dist = self.call(GUIDE_DISTANCE, 'real_field', spl, axis[0], self.vec([0, 1, 0]))
                guides[g.name] = var(g.name, 'real_field',
                                     self.call('divide<real_field,real_field>', 'real_field',
                                               self.call('subtract<real_field,real_field>', 'real_field', dist,
                                                         self.length(g.offset)), self.length(1)))
            return guides[g.name]

        def expr(n):
            if n.op == 'const':
                return self.real(n.val)
            if n.op in ('x', 'y', 'z'):
                return coord[n.op]
            if id(n) in refs:
                return refs[id(n)]
            if n.op == 'guide':
                u = self.call('multiply<real_field,real_field>', 'real_field', expr(n.args[0]), self.length(1))
                e = self.call(REMAP, 'real_field', guide_field(n.val), u, self.length(0), self.length(0))
            elif n.op == 'spline':
                deg, K, _ = n.val

                def as_len(a):
                    if a.op == 'const':
                        return self.length(a.val)
                    return self.call('multiply<real_field,real_field>', 'real_field', expr(a), self.length(1))

                def xy(a, b):
                    return self.call(VEC2, 'vector_field_2d', as_len(a), as_len(b))

                cps = [xy(n.args[2 + 2 * i], n.args[3 + 2 * i]) for i in range(K)]
                auto[0] += 1
                sp = var((n.label or f'Section {auto[0]}') + ' Spline DF', 'implicit',
                         self.call(SPLINE_DF, 'implicit', self.seq('vector_field_2d', cps), self.integer(deg),
                                   xy(n.args[0], n.args[1])))
                e = self.call('divide<real_field,real_field>', 'real_field', sp, self.length(1))
            elif n.op in ('min', 'max'):
                ins = [expr(a) for a in n.args]
                e = (self.call(n.op + '<real_field,real_field>', 'real_field', *ins) if len(ins) == 2 else
                     self.call(n.op + '<list<real_field>>', 'real_field', self.seq('real_field', ins)))
            else:
                e = self.call(FUNC[n.op], 'real_field', *[expr(a) for a in n.args])
            if is_variable(n):
                auto[0] += 1
                if n.op == 'spline':
                    name = (n.label or f'Section {auto[0]}') + ' field'
                else:
                    name = n.label or f'Shared field {auto[0]}'
                e = var(name, 'real_field', e)
                refs[id(n)] = e
            return e

        def is_variable(n):
            # named nodes, sections and anything used twice become notebook variables
            return n.op not in leaves and bool(n.label or n.op == 'spline' or uses.get(id(n), 0) > 1)

        def emit_tree(root):
            for n in _topo([root]):                      # dependencies first, which bounds recursion
                if is_variable(n):
                    expr(n)
            return expr(root)

        part_refs = {}
        for name, field, lo, hi in self.parts:
            scaled = self.call('multiply<real_field,real_field>', 'real_field', emit_tree(field), self.length(1))
            bbox = self.call('create_bounding_box<point,point>', 'bounding_box', self.point(lo), self.point(hi))
            part_refs[name] = var(name, 'implicit', self.call('set_bounding_box<implicit,bounding_box>', 'implicit', scaled, bbox))
        expected = {}
        for name, field, point in self.checks:
            var('CHECK ' + name, 'real', self.call('evaluate_field<real_field,point>', 'real', emit_tree(field), self.point(point)))
            expected['CHECK ' + name] = float(probe(field, [point])[0])
        if export:
            part = part_refs[export['part']]
            mesh = {'func': 'mesh_from_implicit_body_2<implicit,real>', 'type': 'mesh', 'id': self._id(),
                    'name': 'mesh_from_implicit_body_2', 'inputs': [part, self.length(export.get('tolerance', 0.004))]}
            if export.get('sharpen', 2):
                mesh = {'func': 'sharpen_mesh<mesh,implicit,integer,mesh_sharpen_enum>', 'type': 'mesh', 'id': self._id(),
                        'name': 'sharpen_mesh', 'inputs': [mesh, part, self.integer(export.get('sharpen', 2)),
                                                           {'type': 'mesh_sharpen_enum', 'value': {'enum': 1}}]}
            body.append({'name': export['part'] + ' mesh export', 'id': self._id(), 'type': 'mesh_file_data',
                         'func': 'export_mesh<file_path,mesh,unit_length_enum>',
                         'inputs': [{'type': 'file_path', 'value': {'val': str(export['stl'])}}, mesh,
                                    {'type': 'unit_length_enum', 'value': {'id': 'mm'}}]})
        doc = {'body': body, 'displayname': self.title, 'description': self.description,
               'name': 'user_func_' + str(uuid.uuid4()).replace('-', '_'), 'inputs': [], 'namespaces': [], 'version': [1, 0, 0]}
        funcs = set()

        def walk(v):
            if isinstance(v, dict):
                if 'func' in v:
                    funcs.add(v['func'])
                for w in v.values():
                    walk(w)
            elif isinstance(v, list):
                for w in v:
                    walk(w)

        walk(body)
        return doc, dict(variables=len(body), functions=sorted(funcs), expected_checks=expected,
                         parts=[p[0] for p in self.parts])

    def write(self, path, export=None):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        doc, manifest = self.emit(export)
        path.write_text(json.dumps(doc))
        path.with_name(path.stem + '_manifest.json').write_text(json.dumps(manifest, indent=1))
        return manifest


def read_stl(path):
    """Binary STL to welded (vertices, faces). Units are whatever the file holds."""
    dt = np.dtype([('n', '<f4', (3,)), ('v', '<f4', (3, 3)), ('a', '<u2')])
    with open(path, 'rb') as stream:
        stream.seek(80)
        count = int(np.frombuffer(stream.read(4), '<u4')[0])
        tri = np.frombuffer(stream.read(count * dt.itemsize), dt, count)
    v, inverse = np.unique(tri['v'].reshape(-1, 3), axis=0, return_inverse=True)
    return v.astype(float), inverse.reshape(-1, 3)
