"""Constrained geometric fairing of the inferred forward keel guide."""
import json
import numpy as np
from scipy.interpolate import BSpline, PchipInterpolator
from scipy.optimize import minimize, LinearConstraint
from guide_fit import fit
from recipe import ROOT

def optimize_keel(rows,n=24):
    rows=np.asarray(rows,float)
    x=np.linspace(0,1,801)
    gx,base,_=fit(x,PchipInterpolator(rows[:,0],rows[:,1])(x),n)
    knots=np.r_[np.zeros(4),np.arange(1,n-3)/(n-3),np.ones(4)]
    basis=BSpline(knots,np.eye(n),3)
    # Free control points have no support aft of x/L = 0.55.
    free=np.array([i for i in range(1,n-1) if knots[i]>=.55])
    sample=np.linspace(.55,1,1201)
    A=basis(sample);D=basis.derivative()(sample);D2=basis.derivative(2)(sample)
    scale=.05
    c0=base/scale;fixed=c0.copy();fixed[free]=0
    B=D2[:,free];offset=D2@fixed
    H=B.T@B/len(sample);q=B.T@offset/len(sample)
    norm=max(float(np.mean((D2@c0)**2)),1.)
    candidates=[]
    for limit in [.00025,.0005,.001]:
        target=A@c0
        constraints=[LinearConstraint(A[:,free],target-limit/scale-A@fixed,target+limit/scale-A@fixed),
                     LinearConstraint(D[:,free],-D@fixed,np.inf)]
        res=minimize(lambda v:(v@H@v+2*q@v)/norm,c0[free],
                     jac=lambda v:2*(H@v+q)/norm,method='SLSQP',constraints=constraints,
                     options={'ftol':1e-12,'maxiter':600})
        if not res.success:raise RuntimeError(res.message)
        c=fixed.copy();c[free]=res.x;c*=scale
        dense=np.linspace(.55,1,10001);old=BSpline(knots,base,3);new=BSpline(knots,c,3)
        before=float(np.trapezoid(old.derivative(2)(dense)**2,dense))
        after=float(np.trapezoid(new.derivative(2)(dense)**2,dense))
        drift=float(np.max(abs(new(dense)-old(dense))))
        unchanged=float(np.max(abs(new(np.linspace(0,.55,1001))-old(np.linspace(0,.55,1001)))))
        record={'maximum_allowed_shift_L':limit,'maximum_measured_shift_L':drift,
                'guide_bending_before':before,'guide_bending_after':after,
                'bending_reduction_percent':100*(1-after/before),
                'maximum_aft_shift_L':unchanged,'minimum_forward_slope':float(new.derivative()(dense).min()),
                'control_points':list(map(list,zip(gx.tolist(),c.tolist())))}
        assert drift<=limit*1.002 and unchanged<1e-12 and after<before
        candidates.append(record)
    result={'objective':'Integral of squared second derivative of keel height over 0.55 <= x/L <= 1',
            'interpretation':'Guide fairness only; not a hydrodynamic or reference-fidelity score',
            'selected_maximum_shift_L':.0005,'candidates':candidates,
            'selected':next(c for c in candidates if c['maximum_allowed_shift_L']==.0005)}
    (ROOT/'output/validation/loft_optimization.json').write_text(json.dumps(result,indent=2))
    return result
