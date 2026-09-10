import math,json
from pathlib import Path
from shapely.geometry import Point,Polygon
from shapely.affinity import rotate,translate
from shapely.ops import unary_union

def gear(n,m):
    rp=m*n/2;rb=rp*math.cos(math.radians(20));ra=rp+m;rf=rp-1.25*m
    inv=lambda a:math.tan(a)-a
    half=math.pi/(2*n)-.12/(2*rp);points=[]
    for sign,reverse in [(-1,False),(1,True)]:
        radii=[max(rb,rf)+(ra-max(rb,rf))*i/14 for i in range(15)];flank=[]
        for r in radii:
            a=half+inv(math.radians(20))-inv(math.acos(min(1,rb/r)))
            flank.append((r*math.sin(sign*a),r*math.cos(sign*a)))
        aa=half+inv(math.radians(20));flank=[((rf-.3)*math.sin(sign*aa),(rf-.3)*math.cos(sign*aa))]+flank
        points.extend(reversed(flank) if reverse else flank)
    tooth=Polygon(points)
    return unary_union([Point(0,0).buffer(rf,resolution=1000)]+[rotate(tooth,k*360/n,origin=(0,0)) for k in range(n)])

g1,g2=gear(24,2),gear(36,2)
rows=[]
for theta in [i/4 for i in range(61)]:
    a=rotate(g1,theta,origin=(0,0));b=translate(rotate(g2,5-theta*24/36,origin=(0,0)),60,0)
    rows.append({'angle_deg':theta,'intersection_mm2':a.intersection(b).area,'minimum_gap_mm':a.distance(b)})
out={'max_intersection_mm2':max(r['intersection_mm2'] for r in rows),'min_gap_mm':min(r['minimum_gap_mm'] for r in rows),'rows':rows}
Path(__file__).resolve().parents[1].joinpath('output/evidence/gear_engagement.json').write_text(json.dumps(out,indent=2))
print({k:v for k,v in out.items() if k!='rows'})
