"""ISO 10664:1999 user-supplied source: independent, sampled CAD diagnostic.

Table 1 nominal values and Table 3 GO gauge limits transcribed from PDF pages
4 and 6, then checked visually. Millimetres throughout. This is not a proof
of standard conformity, a current-standard claim, or a manufacturing gauge.
"""
import json
import math
import numpy as np

# size, nominal A, nominal B
NOMINAL = [
    (6,1.75,1.27),(8,2.4,1.75),(10,2.8,2.05),(15,3.35,2.4),
    (20,3.95,2.85),(25,4.5,3.25),(30,5.6,4.05),(40,6.75,4.85),
    (45,7.93,5.64),(50,8.95,6.45),(55,11.35,8.05),(60,13.45,9.6),
    (70,15.7,11.2),(80,17.75,12.8),(90,20.2,14.4),(100,22.4,16.)]
# A min/max, B min/max, Ri min/max, Re min/max. H is axial gauge
# length and is intentionally not used to infer recess penetration depth.
GO = [
    (1.695,1.709,1.210,1.224,.371,.396,.130,.134),
    (2.335,2.349,1.672,1.686,.498,.523,.188,.193),
    (2.761,2.776,1.979,1.993,.585,.609,.227,.231),
    (3.295,3.309,2.353,2.367,.704,.728,.265,.269),
    (3.879,3.893,2.764,2.778,.846,.871,.303,.307),
    (4.451,4.465,3.170,3.185,.907,.932,.371,.378),
    (5.543,5.557,3.958,3.972,1.182,1.206,.448,.454),
    (6.673,6.687,4.766,4.780,1.415,1.440,.544,.548),
    (7.841,7.856,5.555,5.570,1.784,1.808,.572,.576),
    (8.857,8.872,6.366,6.380,1.804,1.828,.773,.777),
    (11.245,11.259,7.930,7.945,2.657,2.682,.765,.769),
    (13.302,13.317,9.490,9.504,2.871,2.895,1.065,1.069),
    (15.588,15.603,11.085,11.099,3.465,3.489,1.192,1.196),
    (17.619,17.635,12.646,12.661,3.625,3.629,1.524,1.529),
    (20.021,20.035,14.232,14.246,4.456,4.480,1.527,1.534),
    (22.231,22.245,15.820,15.834,4.913,4.937,1.718,1.724)]

def inner_radius(A,B,re):
    c=A/2-re
    b=B/2
    q=math.sqrt(3)/2
    return (b*b+c*c-2*b*c*q-re*re)/(2*(re+c*q-b))

def radial(theta,A,B,re):
    """Boundary radius from a convex lobe at theta=0, sixfold symmetry.

    Exact circle intersections evaluated at requested angular samples.
    Convex centre c=A/2-re. Adjacent concave centre at angle pi/6,
    distance d=B/2+ri. ri is solved from external circle tangency.
    """
    ri=inner_radius(A,B,re)
    c=A/2-re
    d=B/2+ri
    px=c+re/(re+ri)*(d*math.sqrt(3)/2-c)
    py=re/(re+ri)*d/2
    transition=math.atan2(py,px)
    angle=np.abs((np.asarray(theta)+math.pi/6)%(math.pi/3)-math.pi/6)
    out=np.empty_like(angle,dtype=float)
    mask=angle<=transition
    a=angle[mask]
    out[mask]=c*np.cos(a)+np.sqrt(np.maximum(0,re*re-c*c*np.sin(a)**2))
    a=math.pi/6-angle[~mask]
    out[~mask]=d*np.cos(a)-np.sqrt(np.maximum(0,ri*ri-d*d*np.sin(a)**2))
    return out

def audit(grid_count=9,angle_count=3601):
    angle=np.linspace(0,math.pi/6,angle_count)
    result=[]
    for (size,A,B),limits in zip(NOMINAL,GO):
        candidate=radial(angle,A,B,.1*A)
        feasible=[]
        for ga in np.linspace(limits[0],limits[1],grid_count):
            for gb in np.linspace(limits[2],limits[3],grid_count):
                for ge in np.linspace(limits[6],limits[7],grid_count):
                    gi=inner_radius(ga,gb,ge)
                    if limits[4]<=gi<=limits[5]:
                        clearance=candidate-radial(angle,ga,gb,ge)
                        k=int(np.argmin(clearance))
                        feasible.append((float(clearance[k]),float(ga),float(gb),float(gi),float(ge),float(angle[k]*180/math.pi)))
        worst=min(feasible) if feasible else None
        result.append(dict(size=size,A=A,B=B,re=.1*A,ri=inner_radius(A,B,.1*A),
            feasible_sampled_go_profiles=len(feasible),
            worst_sampled_aligned_radial_clearance_mm=worst[0] if worst else None,
            worst_go_A_B_Ri_Re_and_angle_deg=list(worst[1:]) if worst else None,
            conclusion='sampled GO interference' if worst and worst[0]<0 else 'no sampled aligned GO interference' if worst else 'no feasible sampled GO profile'))
    return dict(source='supplied ISO 10664:1999(E) PDF (not redistributed), Tables 1 and 3',
        method='9 points per A/B/Re dimension, retain derived tangent Ri within limits; 3601 angular samples per half-sector; coaxial aligned profiles',
        limitations='Discrete parameters and angles only. No continuum proof, floating-gauge positioning, orientation optimisation, axial/fallaway or NOT GO test. No ntopcl measurement.',results=result)

if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
