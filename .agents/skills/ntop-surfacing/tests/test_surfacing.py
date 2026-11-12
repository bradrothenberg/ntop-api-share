"""Offline tests of the surfacing reference code. Run with: python -m pytest tests -q

They need numpy and scipy only, and no nTop.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import BSpline

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import loft_pilot as lp
import section_curvature as sc
import surfacing as sf
from surfacing import X, Y, Z


def dense_curve(P, samples=20001, rays=0.0):
    """Points on the curve, and on its straight end rays out to the given length."""
    P = np.asarray(P, float)
    B = BSpline.design_matrix(np.clip(np.linspace(0, 1, samples), 0, 1 - 1e-12), sf.knots(len(P)), 3).toarray()
    C = B @ P
    if rays <= 0:
        return C
    t0 = (P[1] - P[0]) / np.linalg.norm(P[1] - P[0])
    t1 = (P[-1] - P[-2]) / np.linalg.norm(P[-1] - P[-2])
    s = np.linspace(0, rays, samples)[:, None]
    return np.vstack([P[0] - s * t0, C, P[-1] + s * t1])


def test_sign_is_positive_on_the_left_of_travel():
    P = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0)]          # travels in +u
    d = sf.spline_distance(P, [(1.5, 0.4), (1.5, -0.4)])
    assert d[0] > 0 > d[1]
    assert np.allclose(np.abs(d), 0.4, atol=1e-9)


def test_open_curve_continues_along_end_tangents():
    P = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 1.0)]
    d = sf.spline_distance(P, [(-5.0, 0.3), (-5.0, -0.3)])         # far before the first point
    assert np.allclose(d, [0.3, -0.3], atol=1e-9)


def test_distance_matches_brute_force_on_an_open_arc():
    P = np.array([(-0.5, 0.30), (-0.25, 0.45), (0.0, 0.50), (0.25, 0.45), (0.5, 0.30)])
    rng = np.random.default_rng(0)
    q = np.c_[rng.uniform(-0.4, 0.4, 500), rng.uniform(0.0, 0.8, 500)]
    C = dense_curve(P, rays=2.0)                                   # an open curve includes its end rays
    ref = np.sqrt(((C[None] - q[:, None]) ** 2).sum(-1)).min(1)
    assert np.abs(np.abs(sf.spline_distance(P, q)) - ref).max() < 2e-6


def test_closed_region_is_negative_inside_and_accurate():
    poly = [(0.10, 0.20), (0.35, 0.62), (0.80, 0.70), (0.95, 0.40), (0.60, 0.15)]
    P = sf.rounded_polygon(poly, 0.03)
    assert np.allclose(P[0], P[-1])
    d = sf.spline_distance(P, [(0.55, 0.42), (2.0, 2.0), (0.0, 0.0)])
    assert d[0] < 0 < d[1] and d[2] > 0
    rng = np.random.default_rng(1)
    q = np.c_[rng.uniform(0.0, 1.05, 800), rng.uniform(0.05, 0.8, 800)]
    C = dense_curve(P)
    ref = np.sqrt(((C[None] - q[:, None]) ** 2).sum(-1)).min(1)
    assert np.abs(np.abs(sf.spline_distance(P, q)) - ref).max() < 5e-5


def test_sminq_is_compact_and_offsets_by_three_sixteenths():
    k = 0.1
    a, b = X, Y
    f = sf.sminq(a, b, k)
    far = sf.evaluate(f, np.array([0.0]), np.array([0.5]), np.array([0.0]))[0]
    assert far == 0.0                                              # exactly min outside the support
    mid = sf.evaluate(f, np.array([0.2]), np.array([0.2]), np.array([0.0]))[0]
    assert np.isclose(mid, 0.2 - 3 * k / 16)
    # second derivative is continuous across the edge of the support
    s = np.array([k - 1e-4, k, k + 1e-4])
    v = sf.evaluate(f, np.zeros(3), s, np.zeros(3))               # a = 0, b = s
    assert abs(v[0] - 2 * v[1] + v[2]) / 1e-8 < 0.1
    g = sf.smaxq(a, b, k)
    assert np.isclose(sf.evaluate(g, np.array([0.2]), np.array([0.2]), np.array([0.0]))[0], 0.2 + 3 * k / 16)


def test_penalised_fit_is_fairer_than_a_traced_fit():
    x = np.linspace(0, 2, 41)
    z = 0.62 + 0.30 * np.sin(np.pi * (x / 2) ** 0.8) ** 1.3 + np.random.default_rng(7).normal(0, 0.001, len(x))
    fair, dev_fair = sf.fit_guide(x, z, 7, 0, 2, lam=0.02)
    traced, dev_traced = sf.fit_guide(x, z, 24, 0, 2)
    assert dev_traced < dev_fair < 0.004
    a, b = sf.guide_fairness(fair, 0, 2), sf.guide_fairness(traced, 0, 2)
    assert a['inflections'] < b['inflections'] and a['curvature_extrema'] < b['curvature_extrema']


def test_guide_is_the_graph_drawn_at_greville_abscissae():
    sf.Guide._names.clear()
    g = sf.Guide('Test guide', -1.0, 3.0, [0.2, 0.5, -0.3, 0.8, 0.1, 0.6, 0.4])
    # a linear function is reproduced exactly by control values taken at the Greville abscissae
    sf.Guide._names.clear()
    lin = sf.Guide('Linear guide', -1.0, 3.0, 2.0 * g.greville + 1.0)
    u = np.linspace(-1, 3, 50)
    assert np.allclose(lin(u), 2.0 * u + 1.0)
    assert g.offset >= 1.0 and min(g.ctrl) + g.offset > 0
    v = sf.evaluate(g(X * 2.0 + 1.0), np.array([0.3]), np.array([0.0]), np.array([0.0]))[0]
    assert np.isclose(v, g(1.6))


def test_pilot_host_passes():
    report = lp.host()
    assert report['signs_ok'] and report['max_abs_error_m'] < 5e-5


def test_recipe_uses_the_recorded_native_blocks(tmp_path):
    b, written = lp.recipes(tmp_path)
    doc = json.loads((tmp_path / 'Pilot_loft.json').read_text())
    manifest = json.loads((tmp_path / 'Pilot_loft_manifest.json').read_text())
    for func in (sf.SPLINE_DF, sf.VEC2, sf.GUIDE_SPLINE, sf.GUIDE_DISTANCE, sf.REMAP, 'set_bounding_box<implicit,bounding_box>'):
        assert func in manifest['functions'], func
    names = [v['name'] for v in doc['body']]
    assert len(names) == len(set(names))
    assert 'Pilot loft' in names and 'Pilot half section Spline DF' in names and 'Pilot width scale spline' in names
    ids = set()

    def walk(v):
        if isinstance(v, dict):
            if 'ref' in v:                                          # a reference, not a definition
                return
            if 'id' in v and str(v['id']).startswith('n'):
                assert v['id'] not in ids
                ids.add(v['id'])
            for w in v.values():
                walk(w)
        elif isinstance(v, list):
            for w in v:
                walk(w)

    walk(doc['body'])
    refs = []

    def collect(v):
        if isinstance(v, dict):
            if 'ref' in v:
                refs.append(v['ref']['id'])
            for w in v.values():
                collect(w)
        elif isinstance(v, list):
            for w in v:
                collect(w)

    collect(doc['body'])
    assert set(refs) <= ids                                         # every reference resolves inside the recipe
    assert len(written['Pilot loft']['expected_checks']) == len(lp.PROBES)


def test_section_curvature_of_a_circle_and_a_mesh_slice():
    t = np.linspace(0, 2 * np.pi, 2000)
    circle = np.c_[0.5 * np.cos(t), 0.5 * np.sin(t)]
    r = sc.report(circle, step=0.01)
    assert abs(r['max_abs_curvature_per_m'] - 2.0) < 0.05 and r['curvature_sign_changes'] == 0
    # a unit tetrahedron cut by a plane gives one closed triangle outline
    v = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], float)
    f = np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]])
    lines = sc.slice_mesh(v, f, 2, 0.25)
    assert len(lines) == 1 and len(lines[0]) == 4 and np.allclose(lines[0][0], lines[0][-1])


def test_layers_and_beads():
    E = (X * X + Y * Y + Z * Z) - 1.0                              # not a distance, only a test field
    layer = sf.skin(E, -0.2, 0.0)
    inside, in_layer, outside = sf.probe(layer, [[0, 0, 0], [0.95, 0, 0], [1.2, 0, 0]])
    assert inside > 0 and in_layer < 0 and outside > 0
    rod = sf.bead(X, Z, 0.0, 0.05)
    assert sf.probe(rod, [[0, 7, 0]])[0] < 0 < sf.probe(rod, [[0.2, 7, 0]])[0]
