# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "cadquery-ocp==8.0.1.0.0", "numpy==2.5.3", "trimesh==5.1.0",
#   "pyvista==0.49.0", "manifold3d==3.5.3", "scipy>=1.14,<2"
# ]
# ///
"""Compare a supplied nTop mesh with the one-solid original STEP reference.

This host script does not run nTop or establish the candidate mesh's authoring history.
It records whether the candidate hash matches the recorded native export.
"""
from pathlib import Path
import argparse
import hashlib
import json
import time
from importlib.metadata import version

import numpy as np
import trimesh
import pyvista as pv
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location

DEMO = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def explore(shape, kind):
    iterator = TopExp_Explorer(shape, kind)
    while iterator.More():
        yield iterator.Current()
        iterator.Next()


def tessellate(path, deflection):
    reader = STEPControl_Reader()
    if int(reader.ReadFile(str(path))) != 1 or reader.TransferRoots() < 1:
        raise ValueError('Could not read the STEP reference')
    solids = list(explore(reader.OneShape(), TopAbs_SOLID))
    if len(solids) != 1 or not BRepCheck_Analyzer(solids[0]).IsValid():
        raise ValueError('The reference must contain exactly one valid solid')
    BRepMesh_IncrementalMesh(solids[0], deflection, False, .05, True)
    vertices, triangles = [], []
    for raw in explore(solids[0], TopAbs_FACE):
        face = TopoDS.Face(raw)
        location = TopLoc_Location()
        mesh = BRep_Tool.Triangulation_s(face, location)
        if mesh is None:
            raise ValueError('Missing source face tessellation')
        offset = len(vertices)
        for i in range(1, mesh.NbNodes() + 1):
            p = mesh.Node(i).Transformed(location.Transformation())
            vertices.append([p.X(), p.Y(), p.Z()])
        for i in range(1, mesh.NbTriangles() + 1):
            triangle = [mesh.Triangle(i).Value(k) - 1 + offset for k in (1, 2, 3)]
            if face.Orientation() == TopAbs_REVERSED:
                triangle.reverse()
            triangles.append(triangle)
    return trimesh.Trimesh(vertices, triangles, process=True)


def distances(source, target, count, seed):
    points, _ = trimesh.sample.sample_surface(source, count, seed=seed)
    points = np.vstack([points, source.vertices])
    cells = np.column_stack([np.full(len(target.faces), 3), target.faces]).ravel()
    surface = pv.PolyData(target.vertices, cells)
    values = np.abs(pv.PolyData(points).compute_implicit_distance(surface)['implicit_distance'])
    return dict(samples=len(values), max_mm=float(values.max()),
                p99_mm=float(np.percentile(values, 99)), p95_mm=float(np.percentile(values, 95)),
                rms_mm=float(np.sqrt(np.mean(values * values))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, default=DEMO / 'output/native.stl')
    parser.add_argument('--source', type=Path, default=DEMO / 'inputs/Corner_block_source.step')
    parser.add_argument('--out', type=Path, default=DEMO / 'output/comparison.json')
    parser.add_argument('--samples', type=int, default=6000)
    parser.add_argument('--deflection', type=float, default=.005)
    args = parser.parse_args()
    if args.samples < 1 or not np.isfinite(args.deflection) or args.deflection <= 0:
        parser.error('Samples and deflection must be positive')
    # Keep generated evidence out of the checked-in reference collection.
    if not args.out.resolve().is_relative_to((DEMO / 'output').resolve()):
        parser.error('Write comparison results under this demo output directory')
    start = time.perf_counter()
    source_hash, candidate_hash = digest(args.source), digest(args.native)
    recorded = json.loads((DEMO / 'evidence/validation.json').read_text(encoding='utf-8'))
    source = tessellate(args.source, args.deflection)
    candidate = trimesh.load_mesh(args.native, process=True)
    if not isinstance(candidate, trimesh.Trimesh):
        raise ValueError('Candidate must be a triangle mesh')
    for name, mesh in [('source', source), ('candidate', candidate)]:
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
            raise ValueError(name + ' is not a closed, consistently oriented positive-volume mesh')
    intersection = float(trimesh.boolean.intersection([source, candidate], engine='manifold', check_volume=True).volume)
    union = float(source.volume + candidate.volume - intersection)
    iou = intersection / union
    result = dict(
        scope='New host mesh comparison; nTop was not executed by this script',
        source_step_sha256=source_hash, candidate_mesh_sha256=candidate_hash,
        matches_recorded_native_export=candidate_hash == recorded['native_mesh_sha256'],
        matches_bundled_reference=source_hash == recorded['extracted_step_sha256'],
        source_tessellation_deflection_mm=args.deflection, source_angular_deflection_rad=.05,
        area_samples_each_direction=args.samples, area_sample_seeds=[123, 321], include_every_vertex=True,
        source_faces=len(source.faces), native_faces=len(candidate.faces),
        source_volume_mm3=float(source.volume), native_volume_mm3=float(candidate.volume),
        intersection_mm3=intersection, union_mm3=union, volume_iou=iou, volume_iou_pct=100 * iou,
        missing_volume_mm3=float(source.volume - intersection), excess_volume_mm3=float(candidate.volume - intersection),
        source_to_native=distances(source, candidate, args.samples, 123),
        native_to_source=distances(candidate, source, args.samples, 321),
        source_bounds_mm=source.bounds.tolist(), native_bounds_mm=candidate.bounds.tolist(),
        volume_target_pct=99.5, passed_volume_target=iou >= .995,
        topology='Both meshes closed, consistently oriented and positive volume; this does not prove no self-intersections',
        limits='Surface extrema are sampled VTK closest-polygon distances, not certified Hausdorff bounds. No separate numeric surface threshold was specified.',
        libraries={key: version(key) for key in ['cadquery-ocp', 'numpy', 'trimesh', 'pyvista', 'manifold3d']},
        elapsed_s=time.perf_counter() - start,
    )
    if digest(args.source) != source_hash or digest(args.native) != candidate_hash:
        raise RuntimeError('An input changed during comparison')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0 if result['passed_volume_target'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
