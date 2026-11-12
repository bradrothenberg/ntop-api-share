"""Curvature of plane sections: the numeric companion of the zebra check.

  python section_curvature.py body.stl --scale 0.001 --axis x --at 0.3 0.8 1.5 --step 0.004 --out sections

For each cutting plane the outline is traced, resampled at a fixed arc length step, and its
curvature (turn per metre) is reported against arc length. A kink shows as a spike. A ripple
shows as extra sign changes or extra peaks. A fair section has few of both.

From a field instead of a mesh, which avoids mesh noise:

    import surfacing as sf, section_curvature as sc
    a, b, vals = sf.section_grid(field, axis=0, value=0.8, lo=(0.0, 0.1), hi=(1.1, 1.8), n=1400)
    for poly in sc.grid_contours(a, b, vals):
        print(sc.report(poly, step=0.004))

Choose the step several times larger than the mesh or grid cell. Smaller steps report the
sampling, not the surface. Needs numpy; plots need matplotlib; grid_contours needs scikit-image.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))


def slice_mesh(v, f, axis, value):
    """Polylines where the mesh crosses the plane coordinate[axis] = value, as (N, 2) arrays in
    the two remaining coordinates."""
    d = v[:, axis] - value
    d = np.where(d == 0.0, 1e-12, d)
    tri = f[(np.sign(d[f]).min(1) < 0) & (np.sign(d[f]).max(1) > 0)]
    keep = [k for k in range(3) if k != axis]
    segs = []
    for t in tri:
        pts = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            a, b = t[i], t[j]
            if d[a] * d[b] < 0:
                s = d[a] / (d[a] - d[b])
                pts.append((v[a] + s * (v[b] - v[a]))[keep])
        if len(pts) == 2:
            segs.append(pts)
    if not segs:
        return []
    segs = np.array(segs)
    key = lambda p: (round(float(p[0]), 7), round(float(p[1]), 7))
    link = {}
    for i, (p, q) in enumerate(segs):
        link.setdefault(key(p), []).append((i, 0))
        link.setdefault(key(q), []).append((i, 1))
    used, lines = np.zeros(len(segs), bool), []
    for start in range(len(segs)):
        if used[start]:
            continue
        used[start] = True
        chain = [segs[start][0], segs[start][1]]
        for grow_front in (False, True):
            while True:
                tip = chain[0] if grow_front else chain[-1]
                nxt = [(i, e) for i, e in link.get(key(tip), []) if not used[i]]
                if not nxt:
                    break
                i, e = nxt[0]
                used[i] = True
                other = segs[i][1 - e]
                chain.insert(0, other) if grow_front else chain.append(other)
        lines.append(np.array(chain))
    return lines


def grid_contours(a, b, vals):
    """Zero contours of a section grid from surfacing.section_grid, in section coordinates."""
    from skimage import measure
    da, db = a[1] - a[0], b[1] - b[0]
    return [np.c_[a[0] + c[:, 1] * da, b[0] + c[:, 0] * db] for c in measure.find_contours(vals, 0.0)]


def curvature_along(poly, step):
    """Resample a polyline at a fixed arc length step. Returns (arc length, curvature, points),
    or None when the polyline is shorter than eight steps."""
    seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    s = np.r_[0.0, np.cumsum(seg)]
    if s[-1] < 8 * step:
        return None
    u = np.arange(0.0, s[-1], step)
    p = np.c_[np.interp(u, s, poly[:, 0]), np.interp(u, s, poly[:, 1])]
    t = np.diff(p, axis=0)
    ang = np.unwrap(np.arctan2(t[:, 1], t[:, 0]))
    return u[1:-1], np.diff(ang) / step, p


def report(poly, step, noise=0.5):
    """Summary of one outline. noise: curvature below this (1/m) does not count as a sign."""
    r = curvature_along(poly, step)
    if r is None:
        return None
    u, k, _ = r
    sig = np.sign(k[np.abs(k) > noise])
    peaks = int(np.count_nonzero((np.abs(k[1:-1]) > np.abs(k[:-2])) & (np.abs(k[1:-1]) >= np.abs(k[2:])) & (np.abs(k[1:-1]) > noise)))
    worst = float(np.abs(k).max())
    return dict(length_m=round(float(u[-1] + 2 * step), 4), max_abs_curvature_per_m=round(worst, 2),
                min_radius_mm=round(1000.0 / worst, 1) if worst > 0 else None,
                curvature_sign_changes=int(np.count_nonzero(sig[1:] != sig[:-1])), curvature_peaks=peaks)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('mesh')
    ap.add_argument('--axis', choices=['x', 'y', 'z'], default='x')
    ap.add_argument('--at', type=float, nargs='+', required=True, help='plane positions in metres')
    ap.add_argument('--step', type=float, default=0.004, help='arc length step in metres')
    ap.add_argument('--scale', type=float, default=1.0, help='multiply coordinates, for example 0.001 for a millimetre STL')
    ap.add_argument('--out', default='sections')
    a = ap.parse_args()
    from zebra import load
    v, f, _ = load(a.mesh, a.scale)
    axis = 'xyz'.index(a.axis)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    result, plots = {}, []
    for value in a.at:
        rows = []
        for poly in slice_mesh(v, f, axis, value):
            r = report(poly, a.step)
            if r is not None:
                rows.append(r)
                plots.append((f'{a.axis} = {value:g}', poly, curvature_along(poly, a.step)))
        result[f'{a.axis}={value:g}'] = rows
    (out / 'section_curvature.json').write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1))
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return
    titles = list(dict.fromkeys(t for t, _, _ in plots))
    if not titles:
        return
    fig, axes = plt.subplots(2, len(titles), figsize=(5.2 * len(titles), 9), dpi=80, squeeze=False)
    for i, title in enumerate(titles):
        for t, poly, (u, k, _) in plots:
            if t == title:
                axes[0, i].plot(poly[:, 0], poly[:, 1], lw=1.2)
                axes[1, i].plot(u, k, lw=1.0)
        axes[0, i].set_title(title)
        axes[0, i].set_aspect('equal')
        axes[0, i].grid(True, lw=0.3)
        axes[1, i].set_title('curvature [1/m] against arc length [m]')
        axes[1, i].grid(True, lw=0.3)
    fig.tight_layout()
    fig.savefig(out / 'section_curvature.png')
    print(out / 'section_curvature.png')


if __name__ == '__main__':
    main()
