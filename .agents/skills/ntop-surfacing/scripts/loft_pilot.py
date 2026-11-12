"""Pilot for Spline DF lofts: prove the section semantics before building a large model.

  python loft_pilot.py host
      Host evaluator against a brute-force reference, sign checks and guide fairness.
  python loft_pilot.py recipe --out pilot
      One recipe per pilot body for notebook.import_recipe, with expected probe values.
  python loft_pilot.py native --ntopcl <path to ntopcl> --out pilot
      Convert the recipes headless, mesh each body and compare the native vertices with
      the host field. Uses the nTop licence of the signed-in user.

Four bodies cover what a lofted model relies on:

  Pilot loft         half section, lofted by two guides, evaluated with |y|
  Pilot open arc     open curve used as a top surface, continued by its end rays
  Pilot region       closed curve (rounded polygon) used as a mask
  Pilot blend        two primary surfaces joined by the compact C2 blend
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from scipy.interpolate import BSpline

sys.path.insert(0, str(Path(__file__).resolve().parent))
import surfacing as sf
from surfacing import X, Y, Z, Guide, absf, fmax, region, smaxq, spline2d

# half section, clockwise from the top centre to the bottom centre. The first two and the
# last two control points share a height, so the curve meets the centreline at a right angle.
YS = [0.0, 0.30, 0.62, 0.80, 0.86, 0.84, 0.70, 0.40, 0.0]
ZS = [1.20, 1.20, 1.12, 0.95, 0.70, 0.40, 0.22, 0.18, 0.18]


def bodies():
    Guide._names.clear()
    gw = Guide('Pilot width scale', 0.0, 1.0, [0.7, 0.9, 1.05, 1.0, 0.8, 0.75])
    gh = Guide('Pilot crown scale', 0.0, 1.0, [0.8, 0.95, 1.0, 1.0, 0.9, 0.85])
    w, h = gw(X), gh(X)
    section = spline2d([(w * y, 0.18 + h * (z - 0.18)) for y, z in zip(YS, ZS)], absf(Y), Z, label='Pilot half section')
    loft = fmax(section, -X, X - 1.0)
    # travels in +y, so the inside (below) is on the right of travel and negative
    arc = spline2d([(-0.5, 0.30), (-0.25, 0.42 + 0.1 * X), (0.0, 0.50), (0.25, 0.42 + 0.1 * X), (0.5, 0.30)], Y, Z,
                   label='Pilot open arc')
    arc_body = fmax(arc, -X, X - 1.0, absf(Y) - 0.7, 0.05 - Z)
    outline = region('Pilot region outline', [(0.10, 0.20), (0.35, 0.62), (0.80, 0.70), (0.95, 0.40), (0.60, 0.15)], X, Z, 0.03)
    plate = fmax(outline, absf(Y) - 0.05)
    # a roof (transverse arc lofted in x) meeting a side wall (plan curve lofted in z)
    wall = spline2d([(-0.2, 0.55), (0.3, 0.60 + 0.05 * Z), (0.7, 0.60 + 0.05 * Z), (1.2, 0.55)], X, absf(Y), label='Pilot side wall')
    blend = fmax(smaxq(arc, wall, 0.06).named('Pilot blended surface'), -X, X - 1.0, 0.05 - Z)
    return dict(guides=(gw, gh), section=section, parts={
        'Pilot loft': (loft, [-0.05, -1.0, 0.1], [1.05, 1.0, 1.3]),
        'Pilot open arc': (arc_body, [-0.05, -0.75, 0.0], [1.05, 0.75, 0.7]),
        'Pilot region': (plate, [0.0, -0.08, 0.05], [1.05, 0.08, 0.8]),
        'Pilot blend': (blend, [-0.05, -0.8, 0.0], [1.05, 0.8, 0.7])})


PROBES = [[0.5, 0.0, 0.7], [0.5, 1.2, 0.7], [0.5, 0.0, 1.5], [0.5, 0.0, 0.05], [0.2, 0.55, 0.9], [0.8, -0.3, 0.3]]


def brute_force(pts, gw, gh, samples=40001):
    """Unsigned distance to the section curve at each point's x, by dense sampling."""
    B = BSpline.design_matrix(np.clip(np.linspace(0, 1, samples), 0, 1 - 1e-12), sf.knots(len(YS)), 3).toarray()
    out = []
    for p in pts:
        cy = B @ (float(gw(p[0])) * np.array(YS))
        cz = B @ (0.18 + float(gh(p[0])) * (np.array(ZS) - 0.18))
        out.append(np.hypot(cy - abs(p[1]), cz - p[2]).min())
    return np.array(out)


def host():
    b = bodies()
    gw, gh = b['guides']
    rng = np.random.default_rng(1)
    pts = np.c_[rng.uniform(0.02, 0.98, 3000), rng.uniform(-1.0, 1.0, 3000), rng.uniform(0.0, 1.4, 3000)]
    val = sf.probe(b['section'], pts)
    # the Spline DF also has end rays; near them the plain curve distance is not the reference
    core = (pts[:, 2] > 0.25) & (pts[:, 2] < 1.15)
    err = np.abs(np.abs(val) - brute_force(pts, gw, gh))[core]
    centre, outside, above, below = sf.probe(b['section'], PROBES[:4])
    report = dict(points=int(core.sum()), max_abs_error_m=float(err.max()), mean_abs_error_m=float(err.mean()),
                  centre_value=float(centre), outside_value=float(outside), above_value=float(above), below_value=float(below),
                  signs_ok=bool(centre < 0 < outside and above > 0 and below > 0),
                  guides=[g.fairness() for g in (gw, gh)])
    print(json.dumps(report, indent=1))
    return report


def recipes(out, stl=False):
    out = Path(out)
    b = bodies()
    written = {}
    for name, (field, lo, hi) in b['parts'].items():
        stem = name.replace(' ', '_')
        r = sf.Recipe(name, 'Spline DF loft pilot body.')
        r.part(name, field, lo, hi)
        for i, p in enumerate(PROBES):
            r.check(f'{name} {i}', field, p)
        export = dict(part=name, stl=(out / f'{stem}.stl').resolve(), tolerance=0.006) if stl else None
        manifest = r.write(out / f'{stem}.json', export)
        written[name] = dict(recipe=str(out / f'{stem}.json'), variables=manifest['variables'],
                             expected_checks=manifest['expected_checks'])
    (out / 'pilot_expected.json').write_text(json.dumps(written, indent=1))
    print(json.dumps({k: dict(recipe=v['recipe'], variables=v['variables']) for k, v in written.items()}, indent=1))
    return b, written


def native(ntopcl, out, timeout=1800):
    out = Path(out)
    b, written = recipes(out, stl=True)
    tmp = (out / 'tmp').resolve()
    tmp.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TEMP=str(tmp), TMP=str(tmp))          # ntopcl writes large temporary files
    report = {}
    for name, (field, lo, hi) in b['parts'].items():
        recipe = Path(written[name]['recipe']).resolve()
        stl = recipe.with_suffix('.stl')
        stl.unlink(missing_ok=True)
        t = time.time()
        ret = subprocess.run([ntopcl, 'convert', str(recipe), str(recipe.with_suffix('.ntop'))], capture_output=True,
                             text=True, timeout=timeout, env=env)
        rec = dict(exit_code=ret.returncode, seconds=round(time.time() - t, 1), log=(ret.stdout + ret.stderr).strip()[-400:])
        if stl.exists() and stl.stat().st_size > 200:
            v, f = sf.read_stl(stl)
            v = v * 1e-3                                           # the export block writes millimetres
            pick = v[np.random.default_rng(0).choice(len(v), min(len(v), 20000), replace=False)]
            d = sf.surface_distance(field, pick)
            rec.update(triangles=int(len(f)), bounds_m=[v.min(0).round(4).tolist(), v.max(0).round(4).tolist()],
                       sampled_vertices=int(len(pick)), native_vs_host_max_mm=float(d.max() * 1e3),
                       native_vs_host_mean_mm=float(d.mean() * 1e3))
        else:
            rec['status'] = 'no mesh written'
        report[name] = rec
        print(name, json.dumps(rec, indent=1), flush=True)
    (out / 'pilot_native_report.json').write_text(json.dumps(report, indent=1))
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('mode', choices=['host', 'recipe', 'native'])
    ap.add_argument('--out', default='pilot')
    ap.add_argument('--ntopcl')
    a = ap.parse_args()
    if a.mode == 'host':
        sys.exit(0 if host()['signs_ok'] else 1)
    elif a.mode == 'recipe':
        recipes(a.out)
    else:
        if not a.ntopcl:
            ap.error('native mode needs --ntopcl')
        native(a.ntopcl, a.out)
