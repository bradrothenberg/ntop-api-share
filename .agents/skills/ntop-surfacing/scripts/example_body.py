"""Worked example: a small cabin-like body from primary surfaces, built two ways.

  python example_body.py report                 guide and section fairness of both variants
  python example_body.py recipe --out example   nTop recipe of the fair variant
  python example_body.py zebra --out example    zebra images of both variants (scikit-image, pyvista)

The body is 2 m long. Three primary surfaces, each a Spline DF section with few control points:

  Roof    transverse section (|y|, z) lofted along x by a crown height guide and a width guide
  Wall    plan section (x, |y|) lofted along z by a tumble guide
  Floor   a plane

joined by compact C2 blends, plus one detail cut the way details should be cut: a window is a
layer of the envelope limited by a closed region mask, so it follows the surface exactly.

The two variants differ only in how the crown guide is made from the same measured keys
(station heights with about one millimetre of tracing scatter):

  fair    7 control values, third-difference penalty: follows the keys within tolerance
  traced  24 control values, no penalty: passes close to every key and carries their scatter

The traced variant fits the keys better and looks the same in a shaded view. Its reflections
ripple. That is the lesson this skill is built on.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import section_curvature as sc
import surfacing as sf
from surfacing import X, Y, Z, Guide, absf, fmax, region, skin, smaxq, spline2d

AY = absf(Y).named('Lateral distance from centreline')
LO, HI = [-0.05, -0.75, 0.0], [2.05, 0.75, 1.05]


def crown_keys():
    """Station heights of the roof centreline as they would be read off a drawing."""
    x = np.linspace(0.0, 2.0, 41)
    z = 0.62 + 0.30 * np.sin(np.pi * (x / 2.0) ** 0.8) ** 1.3
    scatter = np.random.default_rng(7).normal(0.0, 0.0010, len(x))       # about 1 mm of tracing scatter
    return x, z + scatter


def build(variant='fair'):
    Guide._names.clear()
    x, z = crown_keys()
    if variant == 'fair':
        crown = Guide.fit('Roof crown height', x, z, 7, 0.0, 2.0, lam=0.02)
    else:
        crown = Guide.fit('Roof crown height', x, z, 24, 0.0, 2.0)
    width = Guide('Roof half width', 0.0, 2.0, [0.46, 0.52, 0.56, 0.56, 0.50, 0.44])
    tumble = Guide('Wall tumble', 0.0, 1.1, [0.0, 0.0, -0.02, -0.07, -0.13])
    zc, w = crown(X), width(X)
    # Roof: half section from the crown to past the wall. The first two control points share a
    # height, so the mirrored halves meet without a crease. The last two run straight outward.
    roof = spline2d([(0.0, zc), (w * 0.35, zc), (w * 0.75, zc - 0.03), (w * 1.05, zc - 0.12), (w * 1.5, zc - 0.34), (w * 2.2, zc - 0.70)],
                    AY, Z, label='Roof transverse section').named('Roof field')
    # Wall: plan curve, front centre to rear centre, clockwise seen from above (inside on the right).
    t = tumble(Z)
    plan = [(0.0, 0.0), (0.0, 0.25), (0.12, 0.52), (0.60, 0.60), (1.40, 0.60), (1.88, 0.52), (2.0, 0.25), (2.0, 0.0)]
    wall = spline2d([(px, py + t * (py / 0.60)) for px, py in plan], X, AY, label='Wall plan section').named('Wall field')
    floor = (0.08 - Z).named('Floor field')
    envelope = smaxq(smaxq(roof, wall, 0.07), floor, 0.03).named('Body envelope field')
    window = region('Window outline (side view)', [(0.45, 0.50), (0.62, 0.78), (1.30, 0.80), (1.62, 0.52)], X, Z, 0.04)
    glass = fmax(skin(envelope, -0.006, -0.002), window, 0.3 - AY).named('Side glass field')
    shell = fmax(skin(envelope, -0.020, 0.0), -fmax(window, 0.3 - AY)).named('Painted shell field')
    return dict(crown=crown, guides=[crown, width, tumble], envelope=envelope, glass=glass, shell=shell)


def report():
    out = {}
    for variant in ('fair', 'traced'):
        b = build(variant)
        # the centreline profile is the surface the crown guide drives directly
        a, c, vals = sf.section_grid(b['envelope'], axis=1, value=0.0, lo=(0.25, 0.55), hi=(1.75, 1.0), n=1500)
        polys = [p for p in sc.grid_contours(a, c, vals) if len(p) > 50]
        row = sc.report(max(polys, key=len), step=0.01)
        f = b['crown'].fairness()
        out[variant] = dict(crown_control_values=f['control_values'], crown_max_deviation_mm=round(f['max_deviation'] * 1e3, 2),
                            crown_inflections=f['inflections'], crown_curvature_extrema=f['curvature_extrema'],
                            centreline_curvature_sign_changes=row['curvature_sign_changes'],
                            centreline_curvature_peaks=row['curvature_peaks'])
    print(json.dumps(out, indent=1))
    return out


def recipe(out):
    b = build('fair')
    r = sf.Recipe('Primary surface example', 'Roof and wall Spline DF lofts joined by compact C2 blends.')
    r.part('Painted shell', b['shell'], LO, HI)
    r.part('Side glass', b['glass'], LO, HI)
    r.check('Envelope at roof', b['envelope'], [1.0, 0.0, 0.9])
    r.check('Envelope at wall', b['envelope'], [1.0, 0.59, 0.4])
    path = Path(out) / 'primary_surface_example.json'
    print(path, json.dumps(r.write(path), indent=1)[:600])


def zebra(out):
    import zebra as zb
    for variant in ('fair', 'traced'):
        envelope = build(variant)['envelope']
        v, f, _ = sf.mesh_field(envelope, LO, HI, 0.012)
        # normals from the field, so the stripes show the surface and not the mesh facets
        zb.render(v, f, sf.field_normals(envelope, v), Path(out) / variant, ['front34', 'top'], count=30.0)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('mode', choices=['report', 'recipe', 'zebra'])
    ap.add_argument('--out', default='example')
    a = ap.parse_args()
    {'report': report, 'recipe': lambda: recipe(a.out), 'zebra': lambda: zebra(a.out)}[a.mode]()
