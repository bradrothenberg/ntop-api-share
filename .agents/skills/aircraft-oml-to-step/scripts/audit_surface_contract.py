"""Inventory actual STEP representations and measure explicit smooth joins.

Read-only. Degrees describe stored geometry. Join results are bidirectional
samples, not certified maxima, G2 checks, or a complete adjacency search.
"""
import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from importlib.metadata import version

from OCP.BRep import BRep_Tool
from OCP.GeomAPI import GeomAPI_ProjectPointOnCurve
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_REVERSED
from OCP.TopExp import TopExp
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt, gp_Vec
try:
    from OCP.collections import IndexedMap_TopoDS_Shape_TopTools_ShapeMapHasher as ShapeMap
except ImportError:
    from OCP.TopTools import TopTools_IndexedMapOfShape as ShapeMap


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unique(shape, kind, name):
    mapping = ShapeMap()
    TopExp.MapShapes_s(shape, kind, mapping)
    cast = getattr(TopoDS, name, None) or getattr(TopoDS, name + '_s')
    return [cast(mapping.FindKey(i)) for i in range(1, mapping.Extent() + 1)]


def description(geometry):
    """Include wrapped bases so an offset/trim cannot hide a higher degree."""
    name = type(geometry).__name__
    row = {'type': name}
    if hasattr(geometry, 'UDegree'):
        row.update(degrees=[geometry.UDegree(), geometry.VDegree()],
                   poles=[geometry.NbUPoles(), geometry.NbVPoles()])
        if hasattr(geometry, 'NbUKnots'):
            row['knots'] = [geometry.NbUKnots(), geometry.NbVKnots()]
            row['maximum_interior_multiplicities'] = [
                max((geometry.UMultiplicity(i) for i in range(2, geometry.NbUKnots())), default=0),
                max((geometry.VMultiplicity(i) for i in range(2, geometry.NbVKnots())), default=0)]
        row['rational'] = bool(geometry.IsURational() or geometry.IsVRational())
    elif hasattr(geometry, 'Degree'):
        row.update(degrees=[geometry.Degree()], poles=geometry.NbPoles(),
                   rational=bool(geometry.IsRational()))
        if hasattr(geometry, 'NbKnots'):
            row['knots'] = geometry.NbKnots()
    elif hasattr(geometry, 'BasisSurface'):
        row['basis'] = description(geometry.BasisSurface())
    elif hasattr(geometry, 'BasisCurve'):
        row['basis'] = description(geometry.BasisCurve())
    else:
        row['analytic'] = name in {
            'Geom_Plane', 'Geom_CylindricalSurface', 'Geom_ConicalSurface',
            'Geom_SphericalSurface', 'Geom_ToroidalSurface',
            'Geom_Line', 'Geom_Circle', 'Geom_Ellipse', 'Geom_Hyperbola', 'Geom_Parabola',
            'Geom2d_Line', 'Geom2d_Circle', 'Geom2d_Ellipse', 'Geom2d_Hyperbola', 'Geom2d_Parabola'}
    return row


def degrees(row):
    return row.get('degrees', []) + (degrees(row['basis']) if 'basis' in row else [])


def understood(row):
    return bool(row.get('degrees') or row.get('analytic') or ('basis' in row and understood(row['basis'])))


def parameters(curve, lo, hi, count):
    result = {lo + (hi-lo)*i/(count-1) for i in range(count)}
    base = curve
    while hasattr(base, 'BasisCurve'):
        base = base.BasisCurve()
    knots = [lo, hi]
    if hasattr(base, 'NbKnots'):
        knots += [base.Knot(i) for i in range(1, base.NbKnots()+1) if lo < base.Knot(i) < hi]
    knots = sorted(set(knots))
    result.update(knots)
    for a, b in zip(knots[:-1], knots[1:]):
        result.update(a+(b-a)*f for f in (.0001, .25, .5, .75, .9999))
    return sorted(result)


def rail(faces, selection):
    if type(selection['face']) is not int or not 0<=selection['face']<len(faces):
        raise ValueError('Invalid zero-based face index')
    face = faces[selection['face']]
    edges=unique(face, TopAbs_EDGE, 'Edge')
    if type(selection['edge']) is not int or not 0<=selection['edge']<len(edges):
        raise ValueError('Invalid zero-based local edge index')
    edge = edges[selection['edge']]
    if BRep_Tool.Degenerated_s(edge):
        raise ValueError('An explicit smooth join contains a degenerate edge')
    curve = BRep_Tool.Curve_s(edge, 0., 0.)
    pc = BRep_Tool.CurveOnSurface_s(edge, face, 0., 0.)
    bounds = BRep_Tool.Range_s(edge)
    pbounds = BRep_Tool.Range_s(edge, face)
    if curve is None or pc is None or not all(math.isfinite(x) for x in (*bounds, *pbounds)):
        raise ValueError('A join has no finite 3D curve or pcurve')
    scale = max(1., *(abs(x) for x in bounds))
    if max(abs(a-b) for a,b in zip(bounds,pbounds)) > 1e-12*scale:
        raise ValueError('Curve/pcurve ranges differ; explicit correspondence is required')
    return face, edge, curve, pc, bounds


def point_normal(rail_data, parameter):
    face, _, curve, pc, _ = rail_data
    uv = pc.Value(parameter)
    p, du, dv = gp_Pnt(), gp_Vec(), gp_Vec()
    BRep_Tool.Surface_s(face).D1(uv.X(), uv.Y(), p, du, dv)
    if not all(math.isfinite(x)for x in (*uv.Coord(),*p.Coord(),*du.Coord(),*dv.Coord())):
        raise ValueError('Nonfinite boundary point or derivative')
    normal = du.Crossed(dv)
    if normal.Magnitude() <= 1e-20:
        raise ValueError('Singular boundary normal')
    normal.Normalize()
    if face.Orientation() == TopAbs_REVERSED:
        normal.Reverse()
    return p, normal, p.Distance(curve.Value(parameter)), uv.Coord()


def measure_join(faces, plan, count):
    a, b = rail(faces, plan['left']), rail(faces, plan['right'])
    witnesses = []
    errors = []
    for direction, source, target in [('left_to_right',a,b), ('right_to_left',b,a)]:
        for t in parameters(source[2], *source[4], count):
            try:
                p, n, gap_a, uv = point_normal(source,t)
                project = GeomAPI_ProjectPointOnCurve(p,target[2],*target[4])
                if not project.NbPoints():
                    raise ValueError('Bounded curve projection found no point')
                q_t = project.LowerDistanceParameter()
                q, m, gap_b, q_uv = point_normal(target,q_t)
                dot = max(-1.,min(1.,n.Dot(m)))
                witnesses.append(dict(direction=direction,parameter=t,target_parameter=q_t,
                    point_mm=p.Coord(),target_mm=q.Coord(),uv=uv,target_uv=q_uv,
                    position_gap_mm=p.Distance(q),tangent_plane_angle_deg=math.degrees(math.acos(abs(dot))),
                    oriented_normal_angle_deg=math.degrees(math.acos(dot)),
                    source_edge_support_gap_mm=gap_a,target_edge_support_gap_mm=gap_b))
            except Exception as exc:
                errors.append(dict(direction=direction,parameter=t,error=str(exc)))
    result = dict(name=plan['name'],left=plan['left'],right=plan['right'],samples=len(witnesses),
        errors=errors,witnesses=witnesses,requirements_passed=None)
    for field in ['position_gap_mm','tangent_plane_angle_deg','oriented_normal_angle_deg',
                  'source_edge_support_gap_mm','target_edge_support_gap_mm']:
        result['maximum_'+field] = max((r[field] for r in witnesses),default=None)
    checks=[]
    for key,field in [('max_position_mm','position_gap_mm'),('max_tangent_deg','tangent_plane_angle_deg'),
                      ('max_oriented_normal_deg','oriented_normal_angle_deg')]:
        if key in plan:
            if not math.isfinite(plan[key]) or plan[key]<0:
                raise ValueError('Invalid join acceptance limit: '+key)
            checks.append(bool(witnesses and result['maximum_'+field]<=plan[key]))
    if checks or errors:
        result['requirements_passed'] = bool(checks and all(checks) and not errors)
    return result


def audit(path, max_degree=None, joins_path=None, samples=129, max_curve_degree=None):
    start=time.perf_counter();initial=sha(path)
    reader=STEPControl_Reader()
    if int(reader.ReadFile(str(path))) != 1:
        raise ValueError('STEP read failed')
    reader.SetSystemLengthUnit(1.)
    if reader.TransferRoots()<1:
        raise ValueError('STEP has no transferable roots')
    shape=reader.OneShape();faces=unique(shape,TopAbs_FACE,'Face');edges=unique(shape,TopAbs_EDGE,'Edge')
    rows=[];violations=[];unknown=[]
    def append(location,geometry):
        data=dict(**location,geometry=description(geometry));rows.append(data)
        limit=max_degree if location['kind']=='surface'else max_curve_degree
        if limit is not None and any(d>limit for d in degrees(data['geometry'])):
            violations.append(location)
        if not understood(data['geometry']):unknown.append(location)
    for i,face in enumerate(faces):
        append(dict(kind='surface',face=i),BRep_Tool.Surface_s(face))
        for j,edge in enumerate(unique(face,TopAbs_EDGE,'Edge')):
            pc=BRep_Tool.CurveOnSurface_s(edge,face,0.,0.)
            if pc is not None:append(dict(kind='pcurve',face=i,edge=j),pc)
            else:unknown.append(dict(kind='pcurve',face=i,edge=j,reason='No stored face pcurve'))
    for i,edge in enumerate(edges):
        if BRep_Tool.Degenerated_s(edge):continue
        curve=BRep_Tool.Curve_s(edge,0.,0.)
        if curve is not None:append(dict(kind='curve3d',edge=i),curve)
        else:unknown.append(dict(kind='curve3d',edge=i,reason='No stored 3D curve'))
    join_results=[]
    if joins_path:
        plan=json.loads(Path(joins_path).read_text())
        if plan['step_sha256']!=initial:raise ValueError('Join plan belongs to a different STEP')
        join_results=[measure_join(faces,row,samples) for row in plan['joins']]
    final=sha(path)
    if final!=initial:raise ValueError('STEP changed during its read-only audit')
    has_requirement=max_degree is not None or max_curve_degree is not None or any(r['requirements_passed']is not None for r in join_results)
    passed=None if not has_requirement else not(violations or unknown or any(r['requirements_passed']is False for r in join_results))
    return dict(schema=1,step=str(Path(path).resolve()),step_sha256=initial,unchanged=True,units='mm',
       faces=len(faces),unique_edges=len(edges),max_degree_contract=max_degree,degree_violations=violations,
       max_curve_degree_contract=max_curve_degree,
       unknown_representations=unknown,representations=rows,joins=join_results,
       join_plan_sha256=sha(joins_path)if joins_path else None,requirements_passed=passed,
       cadquery_ocp_version=version('cadquery-ocp'),script_sha256=sha(__file__),seconds=time.perf_counter()-start,
       scope='Stored degree/type inventory and explicit bidirectional sampled joins. No automatic adjacency, continuous maximum, G2, retained-domain, self-intersection, fit or fairness proof.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('step',type=Path)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--max-degree',type=int,help='Maximum supporting-surface degree only')
    ap.add_argument('--max-curve-degree',type=int,help='Optional separate cap for stored 3D boundary curves and pcurves')
    ap.add_argument('--joins',type=Path);ap.add_argument('--samples',type=int,default=129)
    a=ap.parse_args()
    if a.samples<3 or any(d is not None and d<1 for d in[a.max_degree,a.max_curve_degree]):ap.error('Invalid sample count or degree')
    if a.output.resolve()==a.step.resolve():ap.error('Output must not overwrite the STEP')
    if a.joins and a.output.resolve()==a.joins.resolve():ap.error('Output must not overwrite the join plan')
    result=audit(a.step,a.max_degree,a.joins,a.samples,a.max_curve_degree);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items()if k not in('representations','joins')},indent=2))
    return 2 if result['requirements_passed']is False else 0

if __name__=='__main__':raise SystemExit(main())
