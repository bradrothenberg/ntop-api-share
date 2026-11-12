"""Isophote (zebra) check of a surface mesh.

  python zebra.py body.stl --scale 0.001 --out zebra
  python zebra.py body.npz --views front34 rear34 --stripes 46

Stripes are bands of constant angle between the surface normal and a fixed direction, drawn
for two directions. Read them like reflections of light bars:

  a kink in a stripe            tangent break (G1 flaw)
  a wiggle or a pinched stripe  curvature flaw (G2 flaw or an unwanted inflection)
  even, slowly varying stripes  fair surface

The mesh must be finer than the features being judged. Mesh a host preview at a cell size of
a few millimetres for a car-sized body, or use the native export. Needs numpy and pyvista.
Input: binary STL, or NPZ with arrays v (vertices), f (triangles) and optionally n (normals).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))


def load(path, scale=1.0):
    path = Path(path)
    if path.suffix.lower() == '.npz':
        d = np.load(path)
        v, f, n = d['v'].astype(float), d['f'], (d['n'] if 'n' in d.files else None)
    else:
        from surfacing import read_stl
        v, f = read_stl(path)
        n = None
    return v * scale, f, n


def vertex_normals(v, f):
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])      # area weighted
    n = np.zeros_like(v)
    for k in range(3):
        np.add.at(n, f[:, k], fn)
    return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-30)


def stripes(normals, direction, count=46.0):
    """Signed stripe value per vertex: bands of the angle between the normal and the direction.

    The sign is the stripe colour. Keeping the value continuous lets the renderer place the
    stripe edge inside a triangle instead of along mesh edges.
    """
    d = np.asarray(direction, float)
    ang = np.arccos(np.clip(normals @ (d / np.linalg.norm(d)), -1.0, 1.0))
    return np.sin(ang * count).astype(np.float32)


def default_views(v, aspect=16 / 9, fov=28.0, margin=1.06):
    """Cameras that frame the bounding box. X is taken as rearward and Z as up."""
    lo, hi = v.min(0), v.max(0)
    c = 0.5 * (lo + hi)
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]) - c
    tv = np.tan(np.radians(fov / 2))
    out = {}
    for name, d, up in (('front34', (-0.80, 0.55, 0.30), (0, 0, 1)), ('rear34', (0.80, 0.55, 0.30), (0, 0, 1)),
                        ('side', (0.0, 1.0, 0.08), (0, 0, 1)), ('top', (0.0, 0.0, 1.0), (0, 1, 0)),
                        ('front_low', (-0.85, 0.40, 0.08), (0, 0, 1)), ('rear_low', (0.85, 0.40, 0.08), (0, 0, 1))):
        d = np.array(d, float) / np.linalg.norm(d)
        right = np.cross(up, d)
        right /= np.linalg.norm(right)
        upv = np.cross(d, right)
        a, b, depth = np.abs(corners @ right), np.abs(corners @ upv), corners @ d
        dist = float(np.max(np.maximum(a / (tv * aspect), b / tv) + depth)) * margin
        out[name] = dict(eye=(c + d * dist).tolist(), target=c.tolist(), up=upv.tolist(), fov=fov)
    return out


def render(v, f, n, out, views=None, count=46.0, size=(1600, 900)):
    import pyvista as pv
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    n = vertex_normals(v, f) if n is None else n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-30)
    mesh = pv.PolyData(v, np.c_[np.full(len(f), 3), f].astype(np.int64))
    directions = {'a': (0.35, 0.25, 0.90), 'b': (0.75, 0.60, 0.28)}
    for key, d in directions.items():
        mesh['zebra_' + key] = stripes(n, d, count)
    cams = default_views(v, size[0] / size[1])
    written = []
    for name in (views or ['front34', 'rear34']):
        cam = cams[name]
        for key in directions:
            pl = pv.Plotter(off_screen=True, window_size=size)
            pl.set_background('white')
            pl.add_mesh(mesh, scalars='zebra_' + key, cmap=['#101418', '#e8edf2'], clim=(-1.0, 1.0), interpolate_before_map=True,
                        show_scalar_bar=False, lighting=False, smooth_shading=False)
            pl.camera.position, pl.camera.focal_point = cam['eye'], cam['target']
            pl.camera.up, pl.camera.view_angle = cam['up'], cam['fov']
            path = out / f'zebra_{name}_{key}.png'
            pl.screenshot(str(path))
            pl.close()
            written.append(path)
            print(path)
    return written


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('mesh')
    ap.add_argument('--out', default='zebra')
    ap.add_argument('--scale', type=float, default=1.0, help='multiply coordinates, for example 0.001 for a millimetre STL')
    ap.add_argument('--views', nargs='*', help='front34 rear34 side top front_low rear_low (X is taken as rearward, Z up)')
    ap.add_argument('--stripes', type=float, default=46.0, help='stripe frequency; lower it for small or tightly curved parts')
    a = ap.parse_args()
    v, f, n = load(a.mesh, a.scale)
    render(v, f, n, a.out, a.views, a.stripes)
