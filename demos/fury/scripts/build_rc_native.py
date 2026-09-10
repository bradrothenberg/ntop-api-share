"""Native conic/implicit-spline RC exterior. No mesh imports in the graph."""
import hashlib,json
import numpy as np
from scipy.interpolate import BSpline, CubicSpline, PchipInterpolator
from make_notebook import Recipe, ROOT

S=.1
# Photo-guided RC placement choice from the measured camera trial. This is not
# a released Fury dimension. Positive X moves the wing toward the tail.
DEFAULT_WING_LONGITUDINAL_OFFSET_RC_M=.15410430019173585
DEFAULT_HSTAB_SPAN_MULTIPLIER=.919057
PHOTO_GUIDED_PLACEMENT={
    'basis':'Parent photo-camera trial with the corrected fin leading-edge corner',
    'fin_leading_edge_corner_px':[257,194],
    'wing_longitudinal_offset_source':.235732053688966,
    'wing_longitudinal_offset_rc_m':DEFAULT_WING_LONGITUDINAL_OFFSET_RC_M,
    'hstab_span_multiplier':DEFAULT_HSTAB_SPAN_MULTIPLIER,
    'wing_point_fit_rms_px_before':15.18,
    'wing_point_fit_rms_px_after':8.11,
    'residual_scope':'Fitted-image diagnostic with the camera held after HStab span alignment; not independent validation',
    'dimension_scope':'Photo-guided RC appearance choices; not production Fury dimensions'}
source=json.loads((ROOT/'inputs/source_profiles.json').read_text())
samples=np.array(source['sections']);st=np.array(source['stations'])

def fit(x,y,n=20,degree=3):
    a,b=x[0],x[-1];u=(x-a)/(b-a)
    knots=np.r_[np.zeros(degree+1),np.arange(1,n-degree)/(n-degree),np.ones(degree+1)]
    A=BSpline.design_matrix(u,knots,degree).toarray()
    c=np.zeros(n);c[0]=y[0];c[-1]=y[-1]
    c[1:-1]=np.linalg.lstsq(A[:,1:-1],y-A[:,0]*c[0]-A[:,-1]*c[-1],rcond=None)[0]
    grev=np.array([knots[i+1:i+degree+1].mean() for i in range(n)])
    return a+(b-a)*grev,c,BSpline(knots,c,degree)(u)

class Native(Recipe):
    def mul(self,a,b):return self.call('multiply<real_field,real_field>','real_field',a,b)
    def add(self,a,b):return self.call('add<real_field,real_field>','real_field',a,b)
    def sub(self,a,b):return self.call('subtract<real_field,real_field>','real_field',a,b)
    def neg(self,a):return self.mul(a,self.real(-1))
    def vec(self,v):return self.literal('vector',{'units':{},'value':[{'isFinite':True,'val':v0} for v0 in v]})
    def xy(self,a,b):return self.call('vector_field_2d_from_components<real_field,real_field>[5.31.0]','vector_field_2d',a,b)
    def field(self,axis):
        plane=self.var('Global '+axis.upper()+' plane','plane',self.call('plane_from_normal<point,vector>[1.1.0]','plane',self.point([0,0,0]),self.vec([int(a==axis) for a in 'xyz'])),'Coordinates')
        return self.var('Global '+axis.upper(),'real_field',self.prop(plane,'scalar field'),'Coordinates')
    def bound(self,f,lo,hi):
        return self.call('set_bounding_box<implicit,bounding_box>','implicit',f,self.call('create_bounding_box<point,point>','bounding_box',self.point(np.array(lo)*S),self.point(np.array(hi)*S)))
    def both(self,*f):return self.call('max<list<real_field>>','real_field',self.list('real_field',f))
    def either(self,*f):return self.call('min<list<real_field>>','real_field',self.list('real_field',f))
    def coord(self,name,a,b):return self.var(name,'vector_field_2d',self.xy(a,b),'Coordinates')

def build():
    r=Native();metrics={};guide_info={}
    span=r.var('RC wingspan','real',r.length(4.8768),'RC scale')
    scale=r.var('RC scale factor','real',r.call('divide<real,real>','real',span,r.length(.746)),'RC scale')
    widthscale=r.var('Fuselage width multiplier','real',r.real(1),'Shape controls')
    heightscale=r.var('Fuselage height multiplier','real',r.real(1),'Shape controls')
    inletdepth=r.var('Inlet lower depth multiplier','real',r.real(1),'Shape controls')
    rhoshift=r.var('Upper conic rho adjustment','real',r.real(0),'Shape controls')
    wingtip=r.var('Wing tip chord multiplier','real',r.real(1),'Wing controls')
    twist=r.var('Wing tip twist','real',r.real(0,{'angle':1}),'Wing controls')
    thickness=r.var('Wing thickness multiplier','real',r.real(1),'Wing controls')
    tail_span=r.var('HStab span multiplier','real',
                    r.real(DEFAULT_HSTAB_SPAN_MULTIPLIER),'Tail controls')
    wing_offset_rc=r.var('Wing longitudinal offset','real',
                         r.length(DEFAULT_WING_LONGITUDINAL_OFFSET_RC_M),'Wing controls')
    wing_offset=r.var('Wing longitudinal offset in guide coordinates','real',
                      r.call('divide<real,real>','real',wing_offset_rc,scale),'Coordinates')
    wing_translation=r.var('Wing translation in guide coordinates','vector',
                           r.call('vector<real,real,real>','vector',wing_offset,
                                  r.length(0),r.length(0)),'Coordinates')
    wing_offset_source_default=DEFAULT_WING_LONGITUDINAL_OFFSET_RC_M/(4.8768/7.46)
    x,y,z=[r.field(a) for a in 'xyz']
    ay=r.var('Absolute span station','real_field',r.call('abs<real_field>','real_field',y),'Coordinates')
    axis=r.var('Longitudinal axis','axis',r.call('axis<point,vector>','axis',r.point([0,0,0]),r.vec([1,0,0])),'Coordinates')
    def guide(name,xv,yv,n=20):
        gx,gy,pred=fit(xv,yv,n)
        pts=r.var(name+' control points','list<point>',r.list('point',[r.point([a*S,b*S,0]) for a,b in zip(gx,gy)]),'Guide curves')
        curve=r.var(name+' spline','spline',r.call('spline_by_control_points<list<point>,integer>[5.20.0]','spline',pts,r.literal('integer',{'val':3})),'Guide curves')
        result=r.var(name+' field','real_field',r.call('curve_axis_distance<curve_interface,axis,vector>[5.30.0]','real_field',curve,axis,r.vec([0,1,0])),'Loft fields')
        metrics[name]={'max_fit_error_source_units':float(np.max(np.abs(pred-yv))),'rms_fit_error_source_units':float(np.sqrt(np.mean((pred-yv)**2))),'control_points':n}
        guide_info[name]={'x':gx.tolist(),'y':gy.tolist()}
        return result
    xv=samples[:,0]
    w=r.var('Fuselage half width','real_field',r.mul(guide('Half width',xv,samples[:,1]),widthscale),'Loft fields')
    h=r.var('Crown height','real_field',r.mul(guide('Crown',xv,samples[:,2]),heightscale),'Loft fields')
    chine=guide('Chine datum',xv,samples[:,4]+1)
    chine=r.var('Chine height','real_field',r.sub(chine,r.length(S)),'Loft fields')
    localz=r.var('Height above chine','real_field',r.sub(z,chine),'Coordinates')
    space=r.coord('Section YZ',y,localz);halfspace=r.coord('Section absolute YZ',ay,localz)
    ease=lambda t:np.clip(t,0,1)**3*(10-15*np.clip(t,0,1)+6*np.clip(t,0,1)**2)
    rnd=guide('Tail roundness',xv,ease((xv-2.9)/1.55)+1)
    rnd=r.var('Aft section roundness','real_field',r.mul(r.sub(rnd,r.length(S)),r.real(1/S,{'length':-1})),'Loft fields')
    apex=r.mul(w,r.add(r.real(.5),r.mul(rnd,r.real(.5))))
    rho=r.add(r.add(r.real(.5),r.mul(rnd,r.real(np.sqrt(2)-1-.5))),rhoshift)
    topconic=r.var('Upper conic surface','implicit',r.call('conic_implicit<vector_field_2d,vector_field_2d,vector_field_2d,real_field,vector_field_2d>[5.31.0]','implicit',r.xy(r.length(0),h),r.xy(apex,h),r.xy(w,r.length(0)),rho,halfspace),'Native surfaces')
    def bottom(name,depth,width=w):
        if 'ref' not in depth:depth=r.var(name+' depth','real_field',depth,'Loft fields')
        if 'ref' not in width:width=r.var(name+' width','real_field',width,'Loft fields')
        q=np.linspace(1,-1,401);t=np.maximum(0,(abs(q)-.60)/.40);flat=1-2*t*t+t*t*t
        g,c,_=fit(np.linspace(0,1,len(q)),flat,16)
        _,roundc,_=fit(np.linspace(0,1,len(q)),np.sqrt(np.maximum(0,1-q*q)),16)
        cps=[]
        for yy,zz,rz in zip(1-2*g,c,roundc):
            factor=r.add(r.real(zz),r.mul(rnd,r.real(rz-zz)))
            cps.append(r.xy(r.mul(width,r.real(yy)),r.neg(r.mul(depth,factor))))
        return r.var(name,'implicit',r.call('spline_implicit<list<vector_field_2d>,integer,vector_field_2d>[5.53.0]','implicit',r.list('vector_field_2d',cps),r.literal('integer',{'val':3}),space),'Native surfaces')
    # Forebody follows the source underside, then forms the inlet roof.
    roof=np.interp(xv,st[:,0],st[:,3])
    roof_fun=CubicSpline(st[:,0],st[:,3],bc_type='natural')
    roof=roof_fun(xv)
    a=-3.14;b=-1.6;t=np.clip((xv-a)/(b-a),0,1);d=float(roof_fun(a));slope=float(roof_fun(a,1))
    roof=np.where(xv>a,(2*t**3-3*t**2+1)*d+(t**3-2*t**2+t)*(b-a)*slope+(-2*t**3+3*t**2)*.235,roof)
    roof=np.where(xv>b,.235+(samples[:,3]-.235)*ease((xv-b)/.8),roof)
    foredepth=r.var('Forebody lower depth','real_field',r.mul(guide('Forebody underside',xv,roof,32),heightscale),'Loft fields')
    # A single symmetric conic replaces the broad flat section and shoulders.
    # Its center tangent is horizontal; it rises continuously to each chine.
    forelower=r.var('Forebody lower conic','implicit',r.call(
        'conic_implicit<vector_field_2d,vector_field_2d,vector_field_2d,real_field,vector_field_2d>[5.31.0]',
        'implicit',r.xy(r.neg(w),r.length(0)),
        r.xy(r.length(0),r.mul(foredepth,r.real(-2))),
        r.xy(w,r.length(0)),r.real(.5),space),'Native surfaces')
    cowlrows=np.array([[-5.65,.642],[-3.16,.642],[-2.72,.649],[-2.1,.666],[-1.1,.670],[0,.655],[1.4,.585],[2.65,.495],[3.55,.406],[4.45,.310]])
    cdepth=PchipInterpolator(cowlrows[:,0],cowlrows[:,1])(xv)
    depth=r.var('Cowl depth','real_field',r.mul(guide('Smooth inlet lower guide',xv,cdepth,28),inletdepth),'Loft fields')
    lower=bottom('Cowl implicit spline',depth)
    trimx=r.both(r.sub(r.length(-5.65*S),x),r.sub(x,r.length(4.45*S)))
    trimx=r.var('Longitudinal end caps','real_field',trimx,'Loft fields')
    sides=r.var('Chine width limit','real_field',r.sub(ay,w),'Loft fields')
    # Raked mouth is one native plane across the continuously lofted lower surface.
    mouth=r.var('Raked inlet mouth','real_field',r.neg(r.add(r.add(x,localz),r.length(3.14*S))),'Loft fields')
    # The cowl owns the aft lower envelope. Clip the forebody's buried overlap
    # to that envelope so it cannot emerge as a small ventral union bump.
    fore=r.var('Forebody','implicit',r.bound(r.both(r.neg(topconic),forelower,lower,sides,trimx),[-5.65,-1,-1],[4.45,1,1]),'Native surfaces')
    from native_inlet_duct import build_inlet
    wing_root_thickness=abs(float(source['wingRows'][0][4]))
    wing_blend_start=max(-1.4,float(source['wingRows'][0][1])-2*wing_root_thickness)+wing_offset_source_default
    # Finish the outer cowl transition one source root thickness ahead of the
    # current wing blend support. This is an explicit visual design allowance.
    cowl_buried_end=wing_blend_start-wing_root_thickness
    cowl_forward_shift=-.85-cowl_buried_end
    junction_metadata={
        'basis':'Photo review identifies an overlapping outer cowl shoulder and wing-root leading-edge blend.',
        'dimension_scope':'RC appearance construction; the photographic closure endpoint is obscured.',
        'forward_shift_source':cowl_forward_shift,
        'forward_shift_rc_m':cowl_forward_shift*(4.8768/7.46),
        'closure_start_source':-1.38-cowl_forward_shift,
        'closure_end_source':-1.18-cowl_forward_shift,
        'buried_end_source':cowl_buried_end,
        'splitter_aft_source':-1.20-cowl_forward_shift,
        'slot_end_source':-1.17-cowl_forward_shift,
        'wing_blend_start_source':wing_blend_start,
        'shoulder_interval_source':wing_root_thickness,
        'previous_closure_source':[-1.38,-1.18],
        'previous_buried_overlap_source':[-1.18,-.85],
        'previous_splitter_aft_source':-1.20,
        'previous_slot_end_source':-1.17,
        'native_scalar_checks':{
            'CHECK rear closure start':0.0,'CHECK rear closure midpoint':0.5,
            'CHECK rear closure end':1.0,'CHECK buried cowl start':0.0,
            'CHECK buried cowl end':1.0},
        'native_scalar_check_units':'dimensionless',
        'native_scalar_check_absolute_tolerance':1e-10,
        'fixed_features':['Inlet swept mouth location','Leading-edge conic and lip thickness','Outlet center and end plane','Wing and tail placement and lifting profiles'],
        'cavity_preservation':'Old clamped roof samples at x<=-1.6 precede old closure onset -1.38. Their closure weight is zero. The new remap directly uses the same guarded roof.',
        'wing_position_changed':False}
    body,cavity,exhaust,diverter,lip_roof,plate_thickness,duct_center,uncut_body,gap_splitter=build_inlet(
        r,x=x,y=y,z=z,ay=ay,w=w,chine=chine,localz=localz,topconic=topconic,
        forelower=forelower,foredepth=foredepth,lower=lower,depth=depth,sides=sides,
        trimx=trimx,mouth=mouth,fore=fore,scale=scale,guide=guide,bottom=bottom,xv=xv,S=S,
        rear_join_forward_shift_source=cowl_forward_shift)
    def scaled(name,obj,visible=True):
        box=r.var(name+' source bounds','bounding_box',r.prop(obj,'bounding box'),'Native exterior')
        difference=r.call('boolean_subtract<blend_enum,real_field,implicit,list<implicit>>[5.44.0]',
                    'implicit',r.enum('blend_enum',0),r.length(0),obj,r.list('implicit',[cavity,diverter]))
        if name in ('RC fuselage and inlet','RC blended airframe'):
            # Apply display stabilization after the final cavity subtraction.
            # The positive factor preserves the zero surface and body signs.
            difference=r.mul(difference,r.real(.25))
        cut=r.var(name+' duct clearance','implicit',r.call('set_bounding_box<implicit,bounding_box>',
                    'implicit',difference,box),'Native exterior')
        final=r.var(name,'implicit',r.call('scale_object<spatial3d,real,point>[1.2.0]',
                    'implicit',cut,scale,r.point([0,0,0])),'RC exterior')
        if visible:r.final[name]=[.47,.51,.54,1]
        return final
    rc_fuselage=scaled('RC fuselage and inlet',body,False)
    rc_splitter=scaled('RC gap splitter',gap_splitter,False)
    scaled('RC forebody inspection',fore,False)
    final=[]
    panels={}
    def interp(name,coord,rows,col,dim=True):
        return r.var(name,'real_field',r.call('transfer_function<real_field,list<real>,list<real_field>,interpolation_enum,extrapolation_enum>','real_field',coord,r.list('real',[r.length(a[0]*S) for a in rows]),r.list('real_field',[r.length(a[col]*S) if dim else r.real(a[col]) for a in rows]),r.enum('interpolation_enum',0),r.enum('extrapolation_enum',1)),'Lifting surface fields')
    # Cubic implicit splines approximate the supplied visual section equation.
    tt=np.linspace(0,1,601);u=tt*tt
    fv=(.2969*tt-.126*u-.3516*u*u+.2843*u**3-.1036*u**4)/.1
    _,cx,px=fit(tt,u,14);_,cz,pz=fit(tt,fv,14)
    metrics['Foil section']={'max_x_error_chord':float(max(abs(px-u))),'max_z_error_thickness_parameter':float(max(abs(pz-fv)))}
    for name,rows,vertical in [('Wing',source['wingRows'],False),('Tailplane',source['tailRows'],False),('Fin',source['finRows'],True)]:
        rows=[list(a) for a in rows];coord=z if vertical else ay;cross=y if vertical else z
        le=interp(name+' leading edge',coord,rows,1);te=interp(name+' trailing edge',coord,rows,2)
        chord=r.var(name+' chord','real_field',r.sub(te,le),'Lifting surface fields')
        if name=='Wing':
            weight=interp('Wing tip weighting',coord,[[rows[0][0],0],[rows[-1][0],1]],1,False)
            chord=r.var('Wing edited chord','real_field',r.mul(chord,r.add(r.real(1),r.mul(weight,r.sub(wingtip,r.real(1))))),'Lifting surface fields')
        center=interp(name+' centerline',coord,rows,3);th=interp(name+' thickness',coord,rows,4)
        if name=='Wing':
            th=r.var('Wing edited thickness','real_field',r.mul(th,thickness),'Lifting surface fields')
            tangent=r.call('tan<real_field>','real_field',r.mul(weight,twist))
            center=r.var('Wing twisted centerline','real_field',r.sub(center,r.mul(r.sub(r.sub(x,le),r.mul(chord,r.real(.25))),tangent)),'Lifting surface fields')
        spacefoil=r.coord(name+' local XZ',r.sub(x,le),r.sub(cross,center))
        curves=[]
        for sign in [1,-1]:
            cps=[r.xy(r.mul(chord,r.real(a)),r.mul(th,r.real(b*sign))) for a,b in zip(cx,cz)]
            if sign<0:cps.reverse()
            curve=r.var(name+(' upper' if sign>0 else ' lower')+' implicit spline','implicit',r.call('spline_implicit<list<vector_field_2d>,integer,vector_field_2d>[5.53.0]','implicit',r.list('vector_field_2d',cps),r.literal('integer',{'val':3}),spacefoil),'Native surfaces')
            curves.append(curve)
        # Fin embeds below the crown at its forward and rear root.
        lo=rows[0][0] if not vertical else .30
        shape=r.both(*curves,r.sub(r.length(lo*S),coord),r.sub(coord,r.length(rows[-1][0]*S)),r.sub(le,x),r.sub(x,r.add(le,chord)))
        bounds=([-2,-4,-.5],[4.6,4,.5]) if not vertical else ([2.5,-.2,.25],[4.6,.2,1.72])
        if name=='Wing':
            # LE plus the edited chord is quadratic on each span interval.
            # Its Bernstein control values bound every intermediate station.
            # Keep the previous Y/Z envelope and avoid the old tail-sized X box.
            def real_call(op,*values):
                return r.call(op+'<'+','.join('real' for _ in values)+'>','real',*values)
            multipliers=[]
            for index,row in enumerate(rows):
                fraction=(row[0]-rows[0][0])/(rows[-1][0]-rows[0][0])
                multipliers.append(r.var('Wing bounds chord multiplier '+str(index),'real',
                    real_call('add',r.real(1),real_call('multiply',r.real(fraction),
                              real_call('subtract',wingtip,r.real(1)))),'Lifting surface fields'))
            te_bounds=[]
            for index,(left,right) in enumerate(zip(rows,rows[1:])):
                l0,l1=left[1]*S,right[1]*S
                c0,c1=(left[2]-left[1])*S,(right[2]-right[1])*S
                m0,m1=multipliers[index:index+2]
                te_bounds.extend([
                    real_call('add',r.length(l0),real_call('multiply',r.length(c0),m0)),
                    real_call('add',r.length((l0+l1)/2),real_call('multiply',r.real(.5),
                        real_call('add',real_call('multiply',r.length(c0),m1),
                                       real_call('multiply',r.length(c1),m0)))),
                    real_call('add',r.length(l1),real_call('multiply',r.length(c1),m1))])
            wing_max_x=r.var('Wing unshifted upper X bound','real',
                r.call('max<list<real>>','real',r.list('real',
                    [r.length(max(row[1] for row in rows)*S),*te_bounds])),'Lifting surface fields')
            wing_bounds=r.var('Wing unshifted source bounds','bounding_box',
                r.call('create_bounding_box<point,point>','bounding_box',
                    r.point([min(row[1] for row in rows)*S,-4*S,-.5*S]),
                    r.call('point<real,real,real>','point',wing_max_x,
                           r.length(4*S),r.length(.5*S))),'Native exterior')
            original=r.var('Wing unshifted native loft','implicit',
                r.call('set_bounding_box<implicit,bounding_box>','implicit',shape,wing_bounds),'Native exterior')
            obj=r.var('Wing native loft','implicit',
                r.call('translate<spatial3d,vector>','implicit',original,wing_translation),'Native exterior')
        elif name=='Tailplane':
            # A span-only remap keeps the source X/chord and foil sections.
            original=r.var('Tailplane original span native loft','implicit',
                r.bound(shape,[min(row[1] for row in rows),-rows[-1][0],-.5],
                              [max(row[2] for row in rows),rows[-1][0],.5]),'Native exterior')
            obj=r.var('Tailplane native loft','implicit',r.call(
                'remap_non_uniform_implicit<implicit,real,real,real>','implicit',
                original,r.real(1),tail_span,r.real(1)),'Native exterior')
        else:
            obj=r.var(name+' native loft','implicit',r.bound(shape,*bounds),'Native exterior')
        panels[name]=obj
        scaled('RC '+name.lower(),obj,False)
        if name=='Wing':
            for label,p in [('inside',[0,1.5,.0]),('above',[0,1.5,.3]),('below',[0,1.5,-.3])]:
                pt=r.call('point<real,real,real>','point',
                    r.call('add<real,real>','real',r.length(p[0]*S),wing_offset),
                    r.length(p[1]*S),r.length(p[2]*S))
                r.var('CHECK wing '+label,'real',r.call('evaluate_field<real_field,point>','real',obj,pt),'Checks')
            r.var('CHECK wing tip chord','real',r.call('evaluate_field<real_field,point>','real',chord,r.point([0,3.73*S,0])),'Checks')
            paired=[]
            for station in (rows[1][0],(rows[1][0]+rows[-1][0])/2):
                leading,trailing,center_z,half_scale=[float(np.interp(station,
                    [row[0] for row in rows],[row[column] for row in rows])) for column in range(1,5)]
                for sign in (-1,1):
                    for fraction,dz in ((.2,0),(.5,half_scale),(.8,-half_scale)):
                        px=(leading+fraction*(trailing-leading))*S
                        raw_point=r.point([px,sign*station*S,(center_z+dz)*S])
                        moved_point=r.call('point<real,real,real>','point',
                            r.call('add<real,real>','real',r.length(px),wing_offset),
                            r.length(sign*station*S),r.length((center_z+dz)*S))
                        raw_value=r.call('evaluate_field<real_field,point>','real',original,raw_point)
                        moved_value=r.call('evaluate_field<real_field,point>','real',obj,moved_point)
                        paired.append(r.call('abs<real>','real',
                            r.call('subtract<real,real>','real',moved_value,raw_value)))
            r.var('CHECK wing translation field residual','real',
                  r.call('max<list<real>>','real',r.list('real',paired)),'Checks')
            r.var('CHECK Wing longitudinal offset','real',wing_offset_rc,'Checks')
        elif name=='Tailplane':
            groups={'interior':[],'exterior':[],'tip boundary':[]}
            def tail_point(px,py,pz):
                return r.call('point<real,real,real>','point',r.length(px*S),
                    r.call('multiply<real,real>','real',r.length(py*S),tail_span),r.length(pz*S))
            tip_step=abs(rows[-1][4])*.5
            for station in (rows[1][0],(rows[1][0]+rows[-1][0])/2,rows[-1][0]-tip_step):
                leading,trailing,center_z,half_scale=[float(np.interp(station,
                    [row[0] for row in rows],[row[column] for row in rows])) for column in range(1,5)]
                for sign in (-1,1):
                    groups['interior'].append(tail_point((leading+trailing)/2,sign*station,center_z))
                    if station==rows[1][0]:
                        for dz in (-half_scale,half_scale):
                            groups['exterior'].append(tail_point((leading+trailing)/2,sign*station,center_z+dz))
            tip=rows[-1]
            for sign in (-1,1):
                groups['tip boundary'].append(tail_point((tip[1]+tip[2])/2,sign*tip[0],tip[3]))
                groups['exterior'].append(tail_point((tip[1]+tip[2])/2,sign*(tip[0]+tip_step),tip[3]))
            for group,points in groups.items():
                values=[r.call('evaluate_field<real_field,point>','real',obj,point) for point in points]
                if group=='tip boundary':
                    values=[r.call('abs<real>','real',value) for value in values]
                operation='min' if group=='exterior' else 'max'
                check_name=('CHECK HStab tip boundary residual' if group=='tip boundary'
                            else 'CHECK HStab span '+group)
                r.var(check_name,'real',r.call(operation+'<list<real>>','real',
                      r.list('real',values)),'Checks')
            r.var('CHECK HStab span multiplier','real',tail_span,'Checks')
    from native_root_blends import build_root_blends
    blends=build_root_blends(r,fuselage=uncut_body,panels=panels,x=x,y=y,z=z,
                            half_width=w,crown_height=h,chine=chine,scale=scale,
                            S=S,source=source,cutters=(cavity,diverter),
                            wing_offset=wing_offset,wing_offset_source=wing_offset_source_default,
                            tail_span_multiplier=DEFAULT_HSTAB_SPAN_MULTIPLIER)
    final.append(scaled('RC blended airframe',blends['body']))
    from native_root_blend_checks import add_root_blend_checks
    root_checks=add_root_blend_checks(r,blends,guide_info,source,S,
                                    wing_offset_source=wing_offset_source_default,
                                    tail_span_multiplier=DEFAULT_HSTAB_SPAN_MULTIPLIER)
    (ROOT/'output/_agent/rc_root_blend_construction.json').write_text(json.dumps(blends['construction'],indent=2))
    rods=[]
    for a,b,radius in [([-5.65,0,0],[-6.33,0,.026],.010),([-6.33,0,.026],[-6.78,0,.04],.0045),([-6.31,0,-.045],[-6.31,0,.105],.0035)]:
        rods.append(r.call('cylinder<point,point,real>','cylinder',r.point(np.array(a)*S),r.point(np.array(b)*S),r.length(radius*S)))
    probe=r.var('Native nose probe','implicit',r.call('boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]','implicit',r.enum('blend_enum',0),r.length(0),r.list('implicit',rods)),'Native exterior')
    final.append(scaled('RC nose probe',probe));r.final['RC nose probe']=[.25,.29,.32,1]
    fairingspace=r.coord('Dorsal fairing XZ',x,r.sub(localz,h))
    fairingcurve=r.var('Dorsal fairing spline','implicit',r.call('spline_implicit<list<vector_field_2d>,integer,vector_field_2d>[5.53.0]','implicit',r.list('vector_field_2d',[r.xy(r.length(a*S),r.length(b*S)) for a,b in [(-3.98,0),(-3.97,.10),(-3.84,.095),(-3.58,0)]]),r.literal('integer',{'val':3}),fairingspace),'Native surfaces')
    fairing=r.var('Dorsal fairing native','implicit',r.bound(r.both(fairingcurve,r.sub(r.length(-.01*S),r.sub(localz,h)),r.sub(ay,r.length(.0775*S)),r.sub(r.length(-3.98*S),x),r.sub(x,r.length(-3.58*S))),[-3.99,-.09,.4],[-3.57,.09,.8]),'Native exterior')
    final.append(scaled('RC dorsal fairing',fairing));r.final['RC dorsal fairing']=[.25,.29,.32,1]
    rim=r.var('Exhaust rim native','implicit',r.bound(r.both(r.call('cylinder<point,point,real>','cylinder',r.point([4.05*S,0,0]),r.point([4.49*S,0,0]),r.length(.348*S)),r.neg(exhaust)),[4.04,-.35,-.35],[4.5,.35,.35]),'Native exterior')
    final.append(scaled('RC exhaust rim',rim));r.final['RC exhaust rim']=[.3,.34,.36,1]
    assembly=r.var('RC exterior assembly','implicit',r.call('boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]','implicit',r.enum('blend_enum',0),r.length(0),r.list('implicit',final)),'Output')
    assembly_bounds=r.var('RC assembly bounds','bounding_box',r.prop(assembly,'bounding box'),'Inspection')
    # Isolate the fuselage and sleeve for passage inspection. A positive field
    # scale preserves its zero surface and stabilizes the clipped-wall display.
    passage_shell=r.var('RC passage shell','implicit',r.either(rc_fuselage,final[-1]),'Inspection')
    r.var('RC passage cutaway','implicit',r.call('set_bounding_box<implicit,bounding_box>','implicit',
          r.mul(r.both(passage_shell,r.neg(y)),r.real(.25)),assembly_bounds),'Inspection')
    r.var('RC duct volume','implicit',r.call('scale_object<spatial3d,real,point>[1.2.0]',
          'implicit',cavity,scale,r.point([0,0,0])),'Inspection')
    r.var('RC arrangement cutaway','implicit',r.call('set_bounding_box<implicit,bounding_box>','implicit',
          r.mul(r.both(final[0],r.neg(y)),r.real(.25)),assembly_bounds),'Inspection')
    # Body signs at the lip, gap, and main duct are evaluated in native nTop.
    def guide_at(name,xx):
        d=guide_info[name];n=len(d['y']);knots=np.r_[np.zeros(4),np.arange(1,n-3)/(n-3),np.ones(4)]
        return float(BSpline(knots,d['y'],3)((xx-d['x'][0])/(d['x'][-1]-d['x'][0])))
    sx=-3.3
    roof_z=guide_at('Chine datum',sx)-1-guide_at('Forebody underside',sx)-.075
    for label,p0 in [('inside',[sx,0,roof_z-.009]),('gap',[sx,0,roof_z+.030]),('below',[sx,0,roof_z-.07])]:
        r.var('CHECK splitter '+label,'real',r.call('evaluate_field<real_field,point>',
                    'real',body,r.point(np.array(p0)*S)),'Checks')
    # A finite-radius corridor is checked, not just an isolated centerline.
    path_checks=[]
    for i,xx in enumerate(np.linspace(-2.85,4.6,40)):
        center_z=guide_at('Duct center height',xx)-1
        for j,(dy,dz) in enumerate([(0,0),(.04,0),(-.04,0),(0,.04),(0,-.04)]):
            pt=r.point(np.array([xx,dy,center_z+dz])*S)
            path_checks.append(r.call('evaluate_field<real_field,point>','real',body,pt))
    r.var('CHECK minimum open duct corridor','real',r.call('min<list<real>>','real',
                    r.list('real',path_checks)),'Checks')
    # The final RC union is also checked where wings and tail cross the duct.
    final_checks=[]
    for xx in np.linspace(-2.4,4.6,30):
        center_z=guide_at('Duct center height',xx)-1
        pt=r.point(np.array([xx,0,center_z])*(4.8768/7.46))
        final_checks.append(r.call('evaluate_field<real_field,point>','real',assembly,pt))
    r.var('CHECK final assembly passage','real',r.call('min<list<real>>','real',r.list('real',final_checks)),'Checks')
    for xx in [-4.65,-2.35,0,2.65]:
        r.var('CHECK half width '+str(xx),'real',r.call('evaluate_field<real_field,point>','real',w,r.point([xx*S,0,0])),'Checks')
    r.var('CHECK RC span','real',span,'Checks')
    from native_internal_layout import build_internal_layout
    arrangement=build_internal_layout(r,x=x,y=y,z=z,scale=scale,guide_info=guide_info,source=source,S=S,
        wing_offset=wing_offset,wing_offset_rc_m=DEFAULT_WING_LONGITUDINAL_OFFSET_RC_M,
        tail_span=tail_span,tail_span_multiplier=DEFAULT_HSTAB_SPAN_MULTIPLIER)
    arrangement['metadata']['photo_guided_derivation']=PHOTO_GUIDED_PLACEMENT
    (ROOT/'output/_agent/rc_internal_layout.json').write_text(json.dumps(arrangement['metadata'],indent=2))
    (ROOT/'output/_agent/rc_internal_layout_colors.json').write_text(json.dumps(arrangement['colors'],indent=2))
    (ROOT/'output/_agent/rc_internal_gear_colors.json').write_text(json.dumps(arrangement['gear_colors'],indent=2))
    layout_center_checks=[]
    for item in arrangement['metadata']['components']:
        layout_center_checks.append(r.call('evaluate_field<real_field,point>','real',
            arrangement['components'][item['body_name']]['body'],r.point(item['center_m_nominal'])))
    r.var('CHECK internal envelope centers','real',r.call('max<list<real>>','real',r.list('real',layout_center_checks)),'Checks')
    r.write('rc_native_recipe')
    p=ROOT/'output/_agent/rc_native_recipe.json';doc=json.loads(p.read_text());doc.update(displayname='Fury-inspired RC - Native Loft',description='Non-combat RC appearance reconstruction from the supplied normalized Three.js drawing. Native longitudinal guide splines drive conic and implicit-spline surfaces. RC span 16 ft. Photo-guided integrated inlet lip and diverter slot. One continuous native cavity opens the inlet to the exhaust. Internal stations are editable RC concept geometry, not production Fury data. No imported mesh source bodies. Geometry is preliminary and does not define structure, mass, CG, propulsion, or flight readiness.')
    p.write_text(json.dumps(doc,indent=2))
    recipe_hash=hashlib.sha256(p.read_bytes()).hexdigest()
    junction_metadata['source_recipe_sha256']=recipe_hash
    (ROOT/'output/_agent/rc_junction_revision.json').write_text(json.dumps(junction_metadata,indent=2))
    arrangement['metadata']['source_recipe_sha256']=recipe_hash
    (ROOT/'output/_agent/rc_internal_layout.json').write_text(json.dumps(arrangement['metadata'],indent=2))
    (ROOT/'output/_agent/rc_root_blend_construction.json').write_text(json.dumps({'source_recipe_sha256':recipe_hash,'surfaces':blends['construction']},indent=2))
    root_checks['metadata']['source_recipe_sha256']=recipe_hash
    (ROOT/'output/_agent/rc_root_blend_check_metadata.json').write_text(json.dumps(root_checks['metadata'],indent=2))
    layout={'sections':['RC scale','Shape controls','Inlet lip controls','Gap splitter controls','Root blend controls','Duct controls','Wing controls','Tail controls','Internal layout controls','Guide curves','Coordinates','Loft fields','Splitter fields','Gap splitter fields','Root blend fields','Duct fields','Lifting surface fields','Native surfaces','Native root blends','Native exterior','RC exterior','Internal layout','Landing gear illustration','Output','Inspection','Checks'],'variables':r.variables,'final_bodies':r.final}
    (ROOT/'output/_agent/rc_native_recipe_layout.json').write_text(json.dumps(layout,indent=2))
    (ROOT/'output/_agent/rc_fit_metrics.json').write_text(json.dumps(metrics,indent=2));(ROOT/'output/_agent/rc_guides.json').write_text(json.dumps(guide_info,indent=2))
    print(json.dumps(metrics,indent=2))
if __name__=='__main__':build()
