"""Check measured LE lines and chord angles from an SI section CSV."""
import argparse
import csv
import json
import math
from pathlib import Path


def check(rows):
    keys = ['y_m', 'x_le_m', 'z_le_m', 'x_te_m', 'z_te_m', 'twist_deg']
    rows = [{k: float(r[k]) for k in keys} for r in rows]
    if any(not math.isfinite(v) for r in rows for v in r.values()):
        raise ValueError('All measurements must be finite')
    sides = []
    for sign in [-1, 1]:
        data = sorted([r for r in rows if sign*r['y_m'] >= 0], key=lambda r: abs(r['y_m']))
        if len(data) < 2:
            continue
        points = [(r['x_le_m'], r['y_m'], r['z_le_m']) for r in data]
        start, end = points[0], points[-1]
        vec = [b-a for a,b in zip(start,end)]
        length2 = sum(v*v for v in vec)
        if length2 == 0 or abs(data[-1]['y_m']) == abs(data[0]['y_m']):
            raise ValueError('Each side needs distinct span stations')
        residuals, angle_errors = [], []
        for r, pt in zip(data, points):
            d = [p-a for p,a in zip(pt,start)]
            q = sum(a*b for a,b in zip(d,vec))/length2
            residuals.append(math.sqrt(sum((a-q*b)**2 for a,b in zip(d,vec))))
            dx, dz = r['x_te_m']-r['x_le_m'], r['z_te_m']-r['z_le_m']
            if math.hypot(dx,dz) == 0:
                raise ValueError('A zero-length chord has no twist angle')
            actual = math.degrees(math.atan2(dz,dx))
            angle_errors.append(abs((actual-r['twist_deg']+180)%360-180))
        sides.append({'side': sign, 'samples': len(data),
            'max_line_distance_m': max(residuals),
            'max_twist_error_deg': max(angle_errors)})
    if not sides:
        raise ValueError('Need at least two stations on one side')
    return {'sides': sides,
            'max_line_distance_m': max(s['max_line_distance_m'] for s in sides),
            'max_twist_error_deg': max(s['max_twist_error_deg'] for s in sides)}


def self_test():
    rows=[]
    for y in [1, 1.5, 2]:
        angle=y/50
        x,z=2+1.5*y,.1+.02*y
        rows.append(dict(y_m=y,x_le_m=x,z_le_m=z,
            x_te_m=x+math.cos(angle),z_te_m=z+math.sin(angle),
            twist_deg=math.degrees(angle)))
    assert check(rows)['max_line_distance_m'] < 1e-12
    assert check(rows)['max_twist_error_deg'] < 1e-12
    bad=[dict(r) for r in rows];bad[1]['z_le_m']+=.01
    assert check(bad)['max_line_distance_m'] > .005
    bad=[dict(r) for r in rows];bad[1]['twist_deg']+=1
    assert check(bad)['max_twist_error_deg'] > .99
    try:
        check([dict(rows[0], x_le_m=float('nan')),rows[-1]])
    except ValueError:
        pass
    else:
        raise AssertionError('Non-finite data accepted')
    print('Straight, displaced, mistwisted, and non-finite fixtures passed')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv',nargs='?',type=Path)
    parser.add_argument('--line-tolerance-m',type=float)
    parser.add_argument('--angle-tolerance-deg',type=float)
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:
        self_test()
    elif args.csv:
        with args.csv.open(newline='',encoding='utf-8-sig') as stream:
            result=check(list(csv.DictReader(stream)))
        print(json.dumps(result,indent=2))
        failed=(args.line_tolerance_m is not None and result['max_line_distance_m']>args.line_tolerance_m) or (args.angle_tolerance_deg is not None and result['max_twist_error_deg']>args.angle_tolerance_deg)
        raise SystemExit(1 if failed else 0)
    else:
        parser.error('Provide a measurement CSV or --self-test')
