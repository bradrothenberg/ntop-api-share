"""Reusable high-order gmsh-mesh rendering helpers for pyvista.

Import into a case-specific shots script:

    from ho_mesh_render import (read_msh, build_linear_grid, build_ho_wall,
                                build_wall_wireframe, build_prism_surfaces,
                                add_wire)

Covers order-3 gmsh v2.2 elements as written by NekMesh OutputGmsh:
tri10 (type 21), tet20 (29), prism40 (90), pyramid30 (118).
See references/pyvista_ho_meshes.md for the recipe and gotchas.
"""
import numpy as np
import pyvista as pv

VTK_TRIANGLE, VTK_TETRA, VTK_WEDGE, VTK_PYRAMID = 5, 10, 13, 14
VTK_LAGRANGE_TRIANGLE = 69
# gmsh etype -> (vtk linear celltype, n corner nodes)
CORNERS = {21: (VTK_TRIANGLE, 3), 29: (VTK_TETRA, 4),
           90: (VTK_WEDGE, 6), 118: (VTK_PYRAMID, 5)}

# gmsh prism40 (type 90, cubic wedge) node parametric coordinates, derived
# EMPIRICALLY: one linear unit prism through gmsh 4.15 `SetOrder 3`, node
# coordinates read back (on a straight unit prism, coords == params).
PRISM40 = np.array([
    (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (0, 1, 1),
    (1/3, 0, 0), (2/3, 0, 0), (0, 1/3, 0), (0, 2/3, 0),
    (0, 0, 1/3), (0, 0, 2/3), (2/3, 1/3, 0), (1/3, 2/3, 0),
    (1, 0, 1/3), (1, 0, 2/3), (0, 1, 1/3), (0, 1, 2/3),
    (1/3, 0, 1), (2/3, 0, 1), (0, 1/3, 1), (0, 2/3, 1),
    (2/3, 1/3, 1), (1/3, 2/3, 1), (1/3, 1/3, 0), (1/3, 1/3, 1),
    (1/3, 0, 1/3), (2/3, 0, 1/3), (2/3, 0, 2/3), (1/3, 0, 2/3),
    (0, 1/3, 1/3), (0, 1/3, 2/3), (0, 2/3, 2/3), (0, 2/3, 1/3),
    (2/3, 1/3, 1/3), (1/3, 2/3, 1/3), (1/3, 2/3, 2/3), (2/3, 1/3, 2/3),
    (1/3, 1/3, 1/3), (1/3, 1/3, 2/3),
])


def read_msh(path):
    """Parse a gmsh v2.2 ASCII mesh: returns (points (N,3),
    elems [(etype, phys_tag, [0-based node indices]), ...])."""
    with open(path) as f:
        lines = f.readlines()
    ns = lines.index("$Nodes\n")
    nn = int(lines[ns + 1])
    pts = np.empty((nn, 3))
    idmap = {}
    for k in range(nn):
        p = lines[ns + 2 + k].split()
        idmap[int(p[0])] = k
        pts[k] = (float(p[1]), float(p[2]), float(p[3]))
    es = lines.index("$Elements\n")
    ne = int(lines[es + 1])
    elems = []
    for k in range(ne):
        p = lines[es + 2 + k].split()
        etype = int(p[1])
        ntags = int(p[2])
        phys = int(p[3])
        nodes = [idmap[int(x)] for x in p[3 + ntags:]]
        elems.append((etype, phys, nodes))
    return pts, elems


def build_linear_grid(pts, elems, etypes=None, phys=None):
    """Linear corner-node UnstructuredGrid (gmsh and VTK corner orderings
    coincide for tri/tet/wedge/pyramid - no permutation needed)."""
    cells, celltypes = [], []
    for etype, p, nodes in elems:
        if etype not in CORNERS:
            continue
        if etypes is not None and etype not in etypes:
            continue
        if phys is not None and p not in phys:
            continue
        vtk_t, nc = CORNERS[etype]
        cells.append(nc)
        cells.extend(nodes[:nc])
        celltypes.append(vtk_t)
    return pv.UnstructuredGrid(np.array(cells), np.array(celltypes), pts)


def build_ho_wall(pts, elems, subdivision=3):
    """True curved wall: gmsh tri10 -> VTK Lagrange triangles (all 10
    nodes; orderings coincide), tessellated by nonlinear subdivision."""
    cells, celltypes = [], []
    for etype, p, nodes in elems:
        if etype != 21:
            continue
        cells.append(10)
        cells.extend(nodes)
        celltypes.append(VTK_LAGRANGE_TRIANGLE)
    grid = pv.UnstructuredGrid(np.array(cells), np.array(celltypes), pts)
    return grid.extract_surface(nonlinear_subdivision=subdivision)


def _cubic_curve_matrix(nsamp):
    tn = np.array([0.0, 1/3, 2/3, 1.0])

    def basis(t):
        return np.array([
            np.prod([(t - tn[j]) / (tn[i] - tn[j])
                     for j in range(4) if j != i]) for i in range(4)])

    return np.array([basis(t) for t in np.linspace(0, 1, nsamp)])


def build_wall_wireframe(pts, elems, nsamp=7):
    """Curved element-boundary wireframe for tri10 walls: each unique edge
    is the cubic Lagrange curve through its 4 nodes, sampled at nsamp
    points. Draws true element boundaries, not subdivision fragments."""
    B = _cubic_curve_matrix(nsamp)
    seen = set()
    all_pts, lines = [], []
    for etype, p, nodes in elems:
        if etype != 21:
            continue
        c, e = nodes[:3], nodes[3:9]
        for a, b, m0, m1 in ((c[0], c[1], e[0], e[1]),
                             (c[1], c[2], e[2], e[3]),
                             (c[2], c[0], e[4], e[5])):
            key = (min(a, b), max(a, b))
            if key in seen:
                continue
            seen.add(key)
            xyz = B @ np.array([pts[a], pts[m0], pts[m1], pts[b]])
            base = len(all_pts)
            all_pts.extend(xyz)
            lines.append([nsamp] + list(range(base, base + nsamp)))
    # lines passed in the constructor: PolyData(points) alone auto-creates
    # vertex cells that render as square dots over the wireframe
    return pv.PolyData(np.array(all_pts), lines=np.hstack(lines))


def _mono_tri(p):
    u, v = p[:, 0], p[:, 1]
    return np.stack([np.ones_like(u), u, v, u*u, u*v, v*v,
                     u**3, u*u*v, u*v*v, v**3], axis=1)


def _mono_quad(p):
    u, w = p[:, 0], p[:, 1]
    return np.stack([u**i * w**j for i in range(4) for j in range(4)],
                    axis=1)


def _tri_grid(n):
    pts, tris, idx = [], [], {}
    for i in range(n + 1):
        for j in range(n + 1 - i):
            idx[(i, j)] = len(pts)
            pts.append((i / n, j / n))
    for i in range(n):
        for j in range(n - i):
            a, b, c = idx[(i, j)], idx[(i + 1, j)], idx[(i, j + 1)]
            tris.append((a, b, c))
            if j < n - i - 1:
                tris.append((b, idx[(i + 1, j + 1)], c))
    return np.array(pts), np.array(tris)


def _quad_grid(n):
    pts = [(i / n, j / n) for i in range(n + 1) for j in range(n + 1)]
    tris = []
    for i in range(n):
        for j in range(n):
            a = i * (n + 1) + j
            b, c, d = a + n + 1, a + 1, a + n + 2
            tris.extend([(a, b, d), (a, d, c)])
    return np.array(pts), np.array(tris)


def _prism_topology(subdiv=6):
    """Classify the 5 faces and 9 edges of the cubic prism from PRISM40 and
    precompute Vandermonde sampling operators (samples = S @ node_xyz)."""
    P, tol = PRISM40, 1e-4
    faces = []
    tri_pts, tri_conn = _tri_grid(subdiv)
    quad_pts, quad_conn = _quad_grid(subdiv)
    for mask, cols in [(np.abs(P[:, 2]) < tol, (0, 1)),        # w=0 tri
                       (np.abs(P[:, 2] - 1) < tol, (0, 1))]:   # w=1 tri
        ids = np.where(mask)[0]
        A = _mono_tri(P[ids][:, cols])
        S = _mono_tri(tri_pts) @ np.linalg.inv(A)
        faces.append((ids, S, tri_conn))
    for mask, cols in [(np.abs(P[:, 1]) < tol, (0, 2)),            # v=0
                       (np.abs(P[:, 0]) < tol, (1, 2)),            # u=0
                       (np.abs(P[:, 0] + P[:, 1] - 1) < tol, (0, 2))]:
        ids = np.where(mask)[0]
        A = _mono_quad(P[ids][:, cols])
        S = _mono_quad(quad_pts) @ np.linalg.inv(A)
        faces.append((ids, S, quad_conn))
    edges = []
    for a, b in [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3),
                 (0, 3), (1, 4), (2, 5)]:
        m = []
        for t in (1/3, 2/3):
            tgt = P[a] + t * (P[b] - P[a])
            m.append(int(np.argmin(np.linalg.norm(P - tgt, axis=1))))
        edges.append((a, m[0], m[1], b))
    return faces, edges


_PRISM_FACES, _PRISM_EDGES = _prism_topology()


def build_prism_surfaces(pts, elems, skip_wall_corners=None, edge_nsamp=8):
    """True curved rendering of prism40 elements: each cubic face is
    sampled through its Vandermonde interpolant (all face nodes used).
    Returns (surface PolyData, curved element-edge wireframe PolyData).
    skip_wall_corners: set of node indices - faces whose corners all lie
    in it (i.e. wall-coincident faces) are dropped to avoid z-fighting
    with a separately-rendered curved wall."""
    prisms = [nodes for etype, p, nodes in elems if etype == 90]
    all_xyz, all_tris = [], []
    for ids, S, conn in _PRISM_FACES:
        face_nodes, corner_locals = [], [i for i in ids if i < 6]
        for nodes in prisms:
            if skip_wall_corners is not None and all(
                    nodes[i] in skip_wall_corners for i in corner_locals):
                continue
            face_nodes.append([nodes[i] for i in ids])
        if not face_nodes:
            continue
        fn = np.array(face_nodes)                       # (nf, nnodes)
        xyz = np.einsum("sn,fnd->fsd", S, pts[fn])      # (nf, nsamp, 3)
        base = sum(len(x) for x in all_xyz) if all_xyz else 0
        nsamp = xyz.shape[1]
        offs = base + nsamp * np.arange(xyz.shape[0])[:, None, None]
        all_tris.append((conn[None, :, :] + offs).reshape(-1, 3))
        all_xyz.append(xyz.reshape(-1, 3))
    surf_pts = np.vstack(all_xyz)
    tris = np.vstack(all_tris)
    surf = pv.PolyData(surf_pts,
                       np.hstack([np.full((len(tris), 1), 3), tris]))
    B = _cubic_curve_matrix(edge_nsamp)
    seen, wpts, wlines = set(), [], []
    for nodes in prisms:
        for a, m1, m2, b in _PRISM_EDGES:
            ga, gb = nodes[a], nodes[b]
            key = (min(ga, gb), max(ga, gb))
            if key in seen:
                continue
            seen.add(key)
            xyz = B @ pts[[ga, nodes[m1], nodes[m2], gb]]
            base = len(wpts)
            wpts.extend(xyz)
            wlines.append([edge_nsamp] + list(range(base, base + edge_nsamp)))
    wire = pv.PolyData(np.array(wpts), lines=np.hstack(wlines))
    return surf, wire


def _mono_prism_vol(p):
    """Complete-cubic (u,v) x cubic (w) monomials - the 40-term prism40
    volume basis (10 triangle terms x 4 through-thickness terms)."""
    u, v, w = p[:, 0], p[:, 1], p[:, 2]
    cols = []
    for a in range(4):
        for b in range(4 - a):
            for c in range(4):
                cols.append(u**a * v**b * w**c)
    return np.stack(cols, axis=1)


def build_prism_cut(pts, elems, origin=(0, 0, 0), normal=(0, 1, 0), m=5,
                    boundary_subdiv=4, select_box=None):
    """TRUE curved plane cut through prism40 elements: returns
    (band PolyData, element-boundary-line PolyData).

    Each cut prism is evaluated through its exact 40-node cubic volume
    interpolant on an m-resolution sub-wedge grid, then sliced - so the
    cross-section renders as ONE smooth face per element (no linear-slice
    triangle diagonals). Boundary lines come from slicing the curved
    prism-face tessellation of the cut subset, i.e. they are the true
    element-to-element boundaries in the cut plane.

    Draw with: pl.add_mesh(band, color=...) (NO show_edges) +
    add_wire(pl, blines, edgecolor, ~1.1)."""
    o = np.asarray(origin, float)
    n = np.asarray(normal, float)
    Minv = np.linalg.inv(_mono_prism_vol(PRISM40))
    tri_pts, tri_conn = _tri_grid(m)
    npl = len(tri_pts)
    samp = np.array([(u, v, w) for w in np.linspace(0, 1, m + 1)
                     for u, v in tri_pts])
    S = _mono_prism_vol(samp) @ Minv
    cells1, ct1 = [], []
    for lay in range(m):
        o0, o1 = lay * npl, (lay + 1) * npl
        for (a, b, c) in tri_conn:
            cells1.append([6, a + o0, b + o0, c + o0, a + o1, b + o1, c + o1])
            ct1.append(13)
    cells1 = np.array(cells1)
    ct1 = np.array(ct1, dtype=np.uint8)

    cut = []
    for etype, ph, nodes in elems:
        if etype != 90:
            continue
        d = (pts[nodes] - o) @ n
        if d.min() < 0.0 < d.max():
            if select_box is not None:
                cx = pts[nodes[:6], 0].mean()
                if not (select_box[0] <= cx <= select_box[1]):
                    continue
            cut.append(nodes)
    if not cut:
        return pv.PolyData(), pv.PolyData()
    coords = pts[np.array(cut)]
    xyz = np.einsum("sn,fnd->fsd", S, coords)
    nsamp = xyz.shape[1]
    allc = np.concatenate([cells1 + np.array([0] + [i * nsamp] * 6)
                           for i in range(len(cut))])
    allt = np.tile(ct1, len(cut))
    fine = pv.UnstructuredGrid(allc.ravel(), allt, xyz.reshape(-1, 3))
    band = fine.slice(normal=tuple(n), origin=tuple(o))

    global _PRISM_FACES, _PRISM_EDGES
    saved = (_PRISM_FACES, _PRISM_EDGES)
    _PRISM_FACES, _PRISM_EDGES = _prism_topology(boundary_subdiv)
    try:
        psurf, _ = build_prism_surfaces(pts, [(90, 0, list(nd)) for nd in cut],
                                        edge_nsamp=4)
    finally:
        _PRISM_FACES, _PRISM_EDGES = saved
    blines = psurf.slice(normal=tuple(n), origin=tuple(o))
    return band, blines


def add_wire(pl, wire, color, line_width):
    """Thin opaque wireframe with the line depth-offset VTK's own
    show_edges uses, so surface-coincident edges render crisp - no
    geometric displacement (that causes silhouette halos), no tubes,
    no opacity."""
    actor = pl.add_mesh(wire, color=color, line_width=line_width)
    actor.mapper.SetResolveCoincidentTopologyToPolygonOffset()
    actor.mapper.SetRelativeCoincidentTopologyLineOffsetParameters(-4, -4)
    return actor
