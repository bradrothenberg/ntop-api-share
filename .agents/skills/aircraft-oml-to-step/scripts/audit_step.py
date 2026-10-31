"""Read-only STEP topology audit. This does not certify source fit or fairness."""
import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from importlib.metadata import version

from OCP.BRep import BRep_Tool
from OCP.BRepAlgoAPI import BRepAlgoAPI_Check
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.Bnd import Bnd_Box
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopoDS import TopoDS
try:
    from OCP.collections import IndexedMap_TopoDS_Shape_TopTools_ShapeMapHasher as ShapeMap
except ImportError:
    from OCP.TopTools import TopTools_IndexedMapOfShape as ShapeMap


def cast(name, shape):
    method = getattr(TopoDS, name, None) or getattr(TopoDS, name + '_s')
    return method(shape)


def shape_map(shape, kind):
    result = ShapeMap()
    TopExp.MapShapes_s(shape, kind, result)
    return result


def items(mapping):
    return [mapping.FindKey(i) for i in range(1, mapping.Extent() + 1)]


def edge_uses(shape):
    edges = shape_map(shape, TopAbs_EDGE)
    counts = [0] * edges.Extent()
    for face in items(shape_map(shape, TopAbs_FACE)):
        exp = TopExp_Explorer(face, TopAbs_EDGE)
        while exp.More():
            counts[edges.FindIndex(exp.Current()) - 1] += 1
            exp.Next()
    active = [(i + 1, n) for i, n in enumerate(counts)
              if not BRep_Tool.Degenerated_s(cast('Edge', edges.FindKey(i + 1)))]
    return {str(n): sum(k == n for _, k in active) for n in sorted({k for _, k in active})}


def audit(path, kernel=True):
    started = time.perf_counter()
    path = Path(path)
    initial_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise ValueError('STEP read failed')
    reader.SetSystemLengthUnit(1.0)  # Millimeters, explicitly set after the model loads.
    roots = reader.NbRootsForTransfer()
    transferred = reader.TransferRoots()
    shape = reader.OneShape()
    if shape.IsNull() or transferred == 0:
        raise ValueError('STEP contains no transferred shape')
    kinds = {'solids': TopAbs_SOLID, 'shells': TopAbs_SHELL, 'faces': TopAbs_FACE,
             'edges': TopAbs_EDGE, 'vertices': TopAbs_VERTEX}
    maps = {name: shape_map(shape, kind) for name, kind in kinds.items()}
    shells = []
    for shell in items(maps['shells']):
        shells.append({'closed_flag': bool(cast('Shell', shell).Closed()),
                       'nondegenerate_edge_uses': edge_uses(shell)})
    solid_faces = ShapeMap()
    for solid in items(maps['solids']):
        TopExp.MapShapes_s(solid, TopAbs_FACE, solid_faces)
    edge_vertices = ShapeMap()
    for edge in items(maps['edges']):
        TopExp.MapShapes_s(edge, TopAbs_VERTEX, edge_vertices)
    tolerances = {}
    for name, kind in [('faces', 'Face'), ('edges', 'Edge'), ('vertices', 'Vertex')]:
        tolerances[name] = max((BRep_Tool.Tolerance_s(cast(kind, item))
                                for item in items(maps[name])), default=0.0)
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, box, False, False)
    bounds = None if box.IsVoid() else [list(box.CornerMin().Coord()), list(box.CornerMax().Coord())]
    volume, integration_error = None, None
    if maps['solids'].Extent() and all(s['closed_flag'] for s in shells):
        props = GProp_GProps()
        integration_error = BRepGProp.VolumeProperties_s(shape, props, 1e-6, True)
        volume = props.Mass()
    check = {'status': 'skipped'}
    if kernel:
        start = time.perf_counter()
        op = BRepAlgoAPI_Check()
        op.SetData(shape, True, True)
        op.SetRunParallel(True)
        op.SetUseOBB(True)
        op.Perform()
        check = {'status': 'pass' if op.IsValid() else 'fail',
                 'seconds': time.perf_counter() - start,
                 'faults': [str(item.GetCheckStatus()) for item in op.Result()]}
    final_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if final_sha != initial_sha:
        raise ValueError('STEP changed during its read-only audit')
    return {
        'step': str(path.resolve()), 'sha256': initial_sha, 'unchanged': True,
        'cadquery_ocp_version': version('cadquery-ocp'), 'units': 'mm',
        'roots_available': roots, 'roots_transferred': transferred,
        'valid': bool(BRepCheck_Analyzer(shape).IsValid()),
        'topology': {name: value.Extent() for name, value in maps.items()},
        'shells': shells, 'nondegenerate_edge_uses': edge_uses(shape),
        'faces_outside_solids': sum(not solid_faces.Contains(f) for f in items(maps['faces'])),
        'vertices_outside_edges': sum(not edge_vertices.Contains(v) for v in items(maps['vertices'])),
        'bounds_mm': bounds, 'closed_solid_volume_mm3': volume,
        'volume_integration_relative_error': integration_error,
        'max_topology_tolerance_mm': tolerances, 'kernel_check': check,
        'scope': 'Topology only. Source fit, shape fairness and design constraints need separate checks.',
        'seconds': time.perf_counter() - started,
    }


def failures(report, expected_solids=None, require_closed=False, max_tolerance=None):
    errors = []
    if not report['valid']:
        errors.append('Invalid transferred shape')
    if report['roots_transferred'] != report['roots_available']:
        errors.append('Not all STEP roots transferred')
    if report['kernel_check']['status'] == 'fail':
        errors.append('Kernel intersection check failed')
    if expected_solids is not None and report['topology']['solids'] != expected_solids:
        errors.append('Unexpected solid count')
    if require_closed:
        if not report['topology']['solids'] or not report['shells']:
            errors.append('Closed solid required')
        if report['faces_outside_solids']:
            errors.append('Faces exist outside solids')
        if report['nondegenerate_edge_uses'].get('0', 0):
            errors.append('Loose edges exist outside faces')
        if report['vertices_outside_edges']:
            errors.append('Loose vertices exist outside edges')
        for index, shell in enumerate(report['shells']):
            if not shell['closed_flag'] or any(k != '2' for k in shell['nondegenerate_edge_uses']):
                errors.append(f'Shell {index} is open or has irregular edge uses')
    if max_tolerance is not None and max(report['max_topology_tolerance_mm'].values()) > max_tolerance:
        errors.append('Topology tolerance exceeds the specified limit')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--expected-solids', type=int)
    parser.add_argument('--require-closed', action='store_true')
    parser.add_argument('--max-topology-tolerance-mm', type=float)
    parser.add_argument('--skip-kernel', action='store_true')
    args = parser.parse_args()
    if args.output.resolve() == args.step.resolve():
        parser.error('Output must not overwrite the input STEP')
    if args.expected_solids is not None and args.expected_solids < 0:
        parser.error('Expected solid count must be nonnegative')
    limit = args.max_topology_tolerance_mm
    if limit is not None and (not math.isfinite(limit) or limit <= 0):
        parser.error('Topology tolerance must be finite and positive')
    try:
        report = audit(args.step, kernel=not args.skip_kernel)
        report['failures'] = failures(report, args.expected_solids, args.require_closed, limit)
        report['requirements_passed'] = not report['failures']
    except Exception as exc:
        report = {'step': str(args.step), 'requirements_passed': False,
                  'failures': [f'{type(exc).__name__}: {exc}']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps({'output': str(args.output), 'requirements_passed': report['requirements_passed'],
                      'failures': report['failures']}))
    return 0 if report['requirements_passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
