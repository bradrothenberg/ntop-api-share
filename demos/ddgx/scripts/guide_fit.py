import numpy as np
from scipy.interpolate import BSpline
from scipy.optimize import minimize,LinearConstraint

def fit(x, y, n=16):
    a, b = x[0], x[-1]
    u = (x-a)/(b-a)
    knots = np.r_[np.zeros(4), np.arange(1,n-3)/(n-3), np.ones(4)]
    A = BSpline.design_matrix(u, knots, 3).toarray()
    c = np.zeros(n)
    c[0], c[-1] = y[0], y[-1]
    c[1:-1] = np.linalg.lstsq(A[:,1:-1], y-A[:,0]*c[0]-A[:,-1]*c[-1], rcond=None)[0]
    greville = np.array([knots[i+1:i+4].mean() for i in range(n)])
    return a+(b-a)*greville, c, BSpline(knots,c,3)(u)

def fair_fit(x,y,n=16,penalty=1e-8,monotone=True):
    """C2 cubic fit with bending penalty and source-directed slope constraints."""
    a,b=x[0],x[-1];u=(x-a)/(b-a);amp=max(float(np.ptp(y)),1e-5)
    knots=np.r_[np.zeros(4),np.arange(1,n-3)/(n-3),np.ones(4)]
    basis=BSpline(knots,np.eye(n),3);A=basis(u);D2=basis.derivative(2)(u)
    fixed=np.zeros(n);fixed[[0,-1]]=np.array(y)[[0,-1]]/amp
    Y=np.asarray(y)/amp
    af=A[:,1:-1];bf=Y-A@fixed;df=D2[:,1:-1];ef=-(D2@fixed)
    H=(af.T@af+penalty*df.T@df)/len(u);q=(af.T@bf+penalty*df.T@ef)/len(u)
    initial=np.linalg.solve(H,q)
    constraints=[]
    if monotone:
        us=np.linspace(0,1,601);D=basis.derivative()(us);slope=np.interp(us,u,np.gradient(Y,u));tol=1e-8
        # A source plateau need not become an exactly constant polynomial span.
        # Extend adjacent slope signs through it. Opposite signs meet once at
        # its midpoint, so a broad crown can remain smooth without ripples.
        nz=abs(slope)>tol
        direction=np.interp(us,us[nz],np.sign(slope[nz])) if np.any(nz) else np.zeros_like(us)
        low=np.where(direction>=0,-tol,-np.inf);high=np.where(direction<=0,tol,np.inf)
        constraints=[LinearConstraint(D[:,1:-1],low-D@fixed,high-D@fixed)]
    res=minimize(lambda c:c@H@c-2*q@c,initial,jac=lambda c:2*(H@c-q),method='SLSQP',constraints=constraints,options={'ftol':1e-12,'maxiter':1000})
    if not res.success:raise RuntimeError('Fair guide fit failed: '+res.message)
    c=fixed;c[1:-1]=res.x;c*=amp
    greville=np.array([knots[i+1:i+4].mean() for i in range(n)])
    return a+(b-a)*greville,c,BSpline(knots,c,3)(u)
