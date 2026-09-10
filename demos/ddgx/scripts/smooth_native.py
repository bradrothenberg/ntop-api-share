"""Smooth native surface helpers. Section control points vary along spline guides."""
import math
import numpy as np
from scipy.interpolate import PchipInterpolator, BSpline
from recipe import Recipe
from guide_fit import fit,fair_fit

SPLINE='spline_implicit<list<vector_field_2d>,integer,vector_field_2d>[5.53.0]'
CONIC='conic_implicit<vector_field_2d,vector_field_2d,vector_field_2d,real_field,vector_field_2d>[5.31.0]'
BEZIER='cubic_bezier<vector_field_2d,vector_field_2d,vector_field_2d,vector_field_2d,vector_field_2d>[5.31.0]'

class Smooth(Recipe):
    def __init__(self,config=None):
        super().__init__();self.guides={};self.controls={};self.config=config or {}
        self.x,self.y,self.z=[self.field(a) for a in 'xyz']
        self.ay=self.v('Absolute span station',self.abs(self.y),'Coordinates')
        self.axis=self.var('Longitudinal guide axis','axis',self.call('axis<point,vector>','axis',self.point([0,0,0]),self.vec([1,0,0])),'Guide curves')
    def v(self,name,value,section='Loft fields',t='real_field'):return self.var(name,t,value,section)
    def control(self,name,value,section,units=False):
        value=self.config.get('controls',{}).get(name,value)
        self.controls[name]={'default':value,'unit':'m' if units else 'ratio','section':section}
        return self.var(name,'real',self.length(value) if units else self.real(value),section)
    def abs(self,a):return self.call('abs<real_field>','real_field',a)
    def remap(self,a,x=None,y=None,z=None):return self.call('remap<real_field,real_field,real_field,real_field>','real_field',a,x or self.x,y or self.y,z or self.z)
    def guide(self,name,rows,coord=None,n=12):
        settings=self.config.get('guides',{}).get(name,{})
        rows=settings.get('stations',rows);n=settings.get('count',n)
        rows=np.array(rows,float);xs=np.linspace(rows[0,0],rows[-1,0],801)
        ys=np.interp(xs,rows[:,0],rows[:,1]) if settings.get('interpolation')=='linear' else PchipInterpolator(rows[:,0],rows[:,1])(xs)
        fair=settings.get('fair',name in self.config.get('fair_guides',[]))
        if 'control_points' in settings:
            gx,gy=np.asarray(settings['control_points'],float).T;n=len(gx)
            knots=np.r_[np.zeros(4),np.arange(1,n-3)/(n-3),np.ones(4)]
            pred=BSpline(knots,gy,3)((xs-xs[0])/(xs[-1]-xs[0]))
        else:
            gx,gy,pred=fair_fit(xs,ys,n,settings.get('penalty',1e-8)) if fair else fit(xs,ys,n)
        # Axis distance is nonnegative. Offset all ordinates, then restore sign.
        offset=max(1.,-float(min(gy))+1.)
        pts=self.var(name+' control points','list<point>',self.list('point',[self.point([xx,yy+offset,0]) for xx,yy in zip(gx,gy)]),'Guide curves')
        curve=self.var(name+' spline','spline',self.call('spline_by_control_points<list<point>,integer>[5.20.0]','spline',pts,self.literal('integer',{'val':3})),'Guide curves')
        field=self.call('curve_axis_distance<curve_interface,axis,vector>[5.30.0]','real_field',curve,self.axis,self.vec([0,1,0]))
        field=self.sub(field,self.length(offset))
        if coord is not None:field=self.remap(field,x=coord)
        self.guides[name]={'stations':rows.tolist(),'control_points':list(zip(gx.tolist(),gy.tolist())),'ordinate_offset':offset,'maximum_fit_error':float(np.max(abs(pred-ys))),'degree':3,'fair_fit':fair}
        return self.v(name,field)
    def conic_loft(self,name,width,top,center,bottom,xstart,xend,bounds,rho=None,transverse=None,lower_transverse=None,rho_lower=None):
        transverse=self.ay if transverse is None else transverse
        space=self.v(name+' section coordinates',self.xy(transverse,self.sub(self.z,center)),'Coordinates','vector_field_2d')
        rho=rho or self.real(math.sqrt(2)-1)
        up=self.v(name+' upper conic',self.call(CONIC,'implicit',self.xy(self.length(0),top),self.xy(width,top),self.xy(width,self.length(0)),rho,space),'Native surfaces','implicit')
        lowspace=space if lower_transverse is None else self.xy(lower_transverse,self.sub(self.z,center))
        low=self.v(name+' lower conic',self.call(CONIC,'implicit',self.xy(width,self.length(0)),self.xy(width,self.neg(bottom)),self.xy(self.length(0),self.neg(bottom)),rho_lower or rho,lowspace),'Native surfaces','implicit')
        widthbound=self.sub(transverse,width) if lower_transverse is None else self.sub(self.either(transverse,lower_transverse),width)
        shape=self.both(self.neg(up),self.neg(low),widthbound,self.sub(self.length(xstart),self.x),self.sub(self.x,self.length(xend)))
        return self.v(name,self.bound(shape,*bounds),'Component solids','implicit')
    def foil(self,name,le,te,station,normal,datum,thickness,station_lo,station_hi,bounds,twist=None):
        chord=self.v(name+' chord',self.sub(te,le))
        if twist is not None:
            datum=self.add(datum,self.mul(self.sub(self.sub(self.x,le),self.mul(chord,self.real(.25))),twist))
        space=self.v(name+' section coordinates',self.xy(self.sub(self.x,le),self.sub(normal,datum)),'Coordinates','vector_field_2d')
        # Reparameterize with sqrt(x/c) to resolve the round leading edge.
        tt=np.linspace(0,1,801);uu=tt*tt
        hh=5*(.2969*tt-.126*uu-.3516*uu**2+.2843*uu**3-.1036*uu**4)
        _,cx,px=fit(tt,uu,12);_,cz,pz=fit(tt,hh,12)
        sections=[]
        for sign in [1,-1]:
            cps=[self.xy(self.mul(chord,self.real(a)),self.mul(thickness,self.real(sign*b))) for a,b in zip(cx,cz)]
            if sign<0:cps.reverse()
            sections.append(self.v(name+(' upper' if sign>0 else ' lower')+' spline surface',self.call(SPLINE,'implicit',self.list('vector_field_2d',cps),self.literal('integer',{'val':3}),space),'Native surfaces','implicit'))
        # This is a volumetric airfoil. Thickness is the total thickness/span.
        half_edge=self.mul(getattr(self,'edge_control',self.real(0)),self.length(.5))
        shape=self.both(*[self.sub(s,half_edge) for s in sections],self.sub(le,self.x),self.sub(self.x,te),self.sub(self.length(station_lo),station),self.sub(station,self.length(station_hi)))
        self.guides[name+' airfoil fit']={'section':'symmetric NACA four-digit thickness family','control_points':12,'maximum_x_error_chord':float(np.max(abs(px-uu))),'maximum_half_thickness_error_per_t':float(np.max(abs(pz-hh)))}
        return self.v(name,self.bound(shape,*bounds),'Component solids','implicit')
