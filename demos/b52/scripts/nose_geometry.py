import json,sys
from pathlib import Path
import numpy as np
from scipy.interpolate import BSpline
from shapely.geometry import Polygon,box
from shapely import points,distance,contains_xy
ROOT=Path(__file__).resolve().parents[1];d=json.loads((ROOT/'inputs/public_loft.json').read_text());cap=json.loads((ROOT/'inputs/cap.json').read_text());net=np.array(d['controls_m']);L=d['length_m'];ts=np.linspace(0,1,100001);xs=BSpline(d['guide_knots'],d['guide_control_x_normalized'],3)(ts)*L;long=BSpline(d['guide_knots'],net,3)
def original_section(x,nu=1025):
 cp=long(np.interp(x,xs,ts));s=BSpline(d['transverse_knots'],cp,3)(np.linspace(0,1,nu));p=Polygon(np.r_[s,s[::-1]*[-1,1]]);p=p.intersection(box(-cp[:,0].max(),cp[-1,1],cp[:,0].max(),cp[0,1]));return cp,p

def weight(x):
 t=np.clip((x-cap['full_cap_end_m'])/(cap['blend_end_m']-cap['full_cap_end_m']),0,1);return t**3*(10+t*(-15+6*t))

def cap_field(x,y,z):
 R=cap['radius_m'];q=y*y+(z-cap['centerline_tilt']*x-cap['centerline_quadratic_per_m']*x*x)**2;return ((q-cap['radial_quadratic']*x*x)/(2*R)-x)/np.sqrt(1+q/R**2)

def old_field(x,y,z,p):
 a=distance(points(y,z),p.exterior);a=np.where(contains_xy(p,y,z),-a,a);return np.maximum(a,-x)

def blended(x,y,z,p):
 w=weight(x);return (1-w)*cap_field(x,y,z)+w*old_field(x,y,z,p)

def new_section(x,nu=257):
 cp,p=original_section(x);u=np.linspace(0,np.pi,nu);datum=(cp[0,1]+cp[-1,1])/2;lo=np.zeros(nu);hi=np.full(nu,.5)
 for _ in range(40):
  mid=(lo+hi)/2;y=mid*np.sin(u);z=datum+mid*np.cos(u);f=blended(x,y,z,p);lo=np.where(f<0,mid,lo);hi=np.where(f>=0,mid,hi)
 r=(lo+hi)/2;s=np.c_[r*np.sin(u),datum+r*np.cos(u)];return s,p

def make_checks():
 checks=[c for c in json.loads((ROOT/'inputs/base_checks.json').read_text())['checks'] if not c['name'].startswith('CHECK 0.005')];extra=[]
 for x in [.000001,.00001,.0001,.0005,.002,.007,.015,.025,.035,.05,.065,.075,.09,.10,.115,.12,.122,.123,.13,.15]:
  s,p=new_section(x,9)
  for j,(y,z) in enumerate(s):extra.append({'name':f'NOSE x={x:.6f} u={j}','point_m':[x,float(y),float(z)],'expected_m':0})
 for name,p in [('tip',[0,0,0]),('ahead',[-.0001,0,0]),('behind',[.0001,0,0]),('lateral',[0,.0001,0]),('vertical',[0,0,.0001])]:extra.append({'name':'POLE '+name,'point_m':p,'expected_m':float(cap_field(*p))})
 checks+=extra;(ROOT/'output/build/checks.json').write_text(json.dumps({'checks':checks},indent=2));print('Native checks',len(checks));
if __name__=='__main__':make_checks()
