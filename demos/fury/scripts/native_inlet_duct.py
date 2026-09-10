"""Photo-guided RC inlet exterior and a continuous conceptual internal passage.

The internal stations are editable RC concept choices, not production Fury data.
The geometry follows the guide-loft pattern: native section fields, a C2 shape
transition, and one cavity subtraction from the exterior assembly.
"""
import numpy as np


def build_inlet(r, *, x, y, z, ay, w, chine, localz, topconic, forelower,
                foredepth, lower, depth, sides, trimx, mouth, fore, scale,
                guide, bottom, xv, S, rear_join_forward_shift_source=0.0):
    def v(name, value, kind='real_field', section='Duct fields'):
        return r.var(name, kind, value, section)

    def div(a, b):
        return r.call('divide<real_field,real_field>', 'real_field', a, b)

    def clamp(a, lo=0, hi=1):
        return r.call('min<real_field,real_field>', 'real_field', r.real(hi),
                      r.call('max<real_field,real_field>', 'real_field', r.real(lo), a))

    def transition(name, start, end):
        u = v(name+' coordinate', clamp(r.mul(r.sub(x, r.length(start*S)),
                         r.real(1/((end-start)*S), {'length':-1}))))
        return v(name, r.mul(r.mul(u, r.mul(u,u)),
                    r.add(r.real(10),r.mul(u,r.add(r.real(-15),r.mul(u,r.real(6)))))))

    def mix(a,b,t):
        return r.call('mix<real_field,real_field,real_field>','real_field',a,b,t)

    def rounded(name, fields, radius):
        return v(name,r.call('boolean_intersect<blend_enum,real_field,list<implicit>>[5.44.0]',
                    'implicit',r.enum('blend_enum',4),radius,r.list('implicit',fields)), 'implicit')

    rc_unit = 4.8768/7.46
    projection_rc = r.var('Inlet lip forward projection','real',r.length(.28*rc_unit),'Inlet lip controls')
    thickness_rc = r.var('Inlet lip thickness','real',r.length(.018*rc_unit),'Inlet lip controls')
    gap_rc = r.var('Inlet lip center gap','real',r.length(.075*rc_unit),'Inlet lip controls')
    for name,field in [('Projection',projection_rc),('Thickness',thickness_rc),('Gap',gap_rc)]:
        locals_value = r.call('divide<real,real>','real',field,scale)
        if name=='Projection': projection=v('Splitter projection in guide coordinates',locals_value,'real','Splitter fields')
        elif name=='Thickness': thickness=v('Splitter thickness in guide coordinates',locals_value,'real','Splitter fields')
        else: gap=v('Splitter gap in guide coordinates',locals_value,'real','Splitter fields')
    outlet_rc=r.var('Duct outlet radius','real',r.length(.326*rc_unit),'Duct controls')
    outlet=v('Duct outlet radius in guide coordinates',r.call('divide<real,real>','real',outlet_rc,scale),'real')
    wall_rc=r.var('Duct wall allowance','real',r.length(.035*rc_unit),'Duct controls')
    wall=v('Duct wall allowance in guide coordinates',r.call('divide<real,real>','real',wall_rc,scale),'real')
    corner_rc=r.var('Inlet corner radius','real',r.length(.075*rc_unit),'Duct controls')
    corner=v('Inlet corner radius in guide coordinates',r.call('divide<real,real>','real',corner_rc,scale),'real')

    cheek_width=v('Inlet cheek half width',r.mul(w,r.real(.94)))
    leading=v('Splitter swept leading edge',r.add(r.sub(r.length(-3.14*S),projection),
               r.mul(projection,div(ay,cheek_width))))
    # Move the closure, buried overlap, slot end, and splitter aft end together.
    # The selected RC appearance trial finishes the buried overlap ahead of
    # the wing-root blend. It is not an inferred production dimension.
    shift=float(rear_join_forward_shift_source)
    if not np.isfinite(shift) or not 0 <= shift < .8:
        raise ValueError('The forward-only cowl junction trial is outside its supported range.')
    close=transition('Diverter rear closure',-1.38-shift,-1.18-shift)
    clearance=v('Splitter local clearance',r.mul(gap,r.sub(r.real(1),close)))
    lip_depth=v('Splitter roof center depth',r.add(foredepth,gap))
    # A shallow transverse conic gives a nearly straight rise toward the cheeks.
    # The previous flat-to-steep spline sheet caused a visible corner here.
    lip_conic=v('Splitter transverse conic',r.call(
        'conic_implicit<vector_field_2d,vector_field_2d,vector_field_2d,real_field,vector_field_2d>[5.31.0]',
        'implicit',r.xy(r.length(0),r.neg(lip_depth)),
        r.xy(r.mul(cheek_width,r.real(.5)),r.neg(r.sub(lip_depth,r.mul(foredepth,r.real(.32))))),
        r.xy(cheek_width,r.neg(r.add(r.mul(foredepth,r.real(.2)),gap))),
        r.real(.5),r.xy(ay,localz)),'implicit')
    # Translate the actual underside downward. A C2 lower envelope keeps the
    # desired conic below this clearance surface over the complete span.
    clear_roof=v('Full span underside clearance surface',r.call(
        'remap<real_field,real_field,real_field,real_field>','real_field',
        forelower,x,y,r.add(z,gap)))
    blend_k=r.length(.02*S)
    blend_h=v('Roof clearance blend overlap',r.call('max<real_field,real_field>',
        'real_field',r.length(0),r.sub(blend_k,r.call('abs<real_field>',
        'real_field',r.sub(lip_conic,clear_roof)))))
    guarded_roof=v('Clearance constrained splitter conic',r.sub(
        r.call('min<real_field,real_field>','real_field',lip_conic,clear_roof),
        div(r.mul(blend_h,r.mul(blend_h,blend_h)),r.real(6*(.02*S)**2,{'length':2}))))
    lip_roof=v('Integrated splitter roof field',mix(guarded_roof,forelower,close))

    rake=r.var('Inlet face rake','real',r.real(2.3),'Duct controls')
    # Positive normalization preserves the swept zero surface and reduces
    # ray-march overshoot when the rake raises the field gradient.
    mouth_raw=v('Raked inlet mouth numerator',r.add(r.sub(leading,x),r.mul(rake,
                      r.call('max<real_field,real_field>','real_field',lip_roof,r.length(0)))))
    inlet_mouth=v('Integrated raked inlet mouth',div(mouth_raw,r.add(r.real(1),
                  r.call('abs<real_field>','real_field',rake))))
    buried=transition('Buried cowl attachment transition',-1.18-shift,-.85-shift)
    for label,field,xx in [
        ('rear closure start',close,-1.38-shift),
        ('rear closure midpoint',close,-1.28-shift),
        ('rear closure end',close,-1.18-shift),
        ('buried cowl start',buried,-1.18-shift),
        ('buried cowl end',buried,-.85-shift)]:
        r.var('CHECK '+label,'real',r.call('evaluate_field<real_field,point>',
            'real',field,r.point([xx*S,0,0])),'Checks')
    outer_roof=v('Outer roof with buried aft overlap',mix(lip_roof,topconic,buried))
    upper_cheeks=rounded('Rounded outer roof and cheeks',
                        [r.neg(outer_roof),sides],corner)
    rounded_mouth=rounded('Rounded continuous inlet leading edge',
                         [upper_cheeks,lower,inlet_mouth],r.mul(thickness,r.real(.8)))
    raw_outer=v('Raked outer cowl',r.bound(r.both(rounded_mouth,trimx),
                      [-3.6,-1,-1],[4.45,1,1]),'implicit','Native surfaces')
    solid=v('Integrated cowl and forebody',r.bound(r.either(fore,raw_outer),
                     [-5.65,-1,-1],[4.45,1,1]),'implicit','Native surfaces')

    # A separate subtractive slot leaves the splitter integral with the cheeks.
    # It widens laterally behind the mouth to provide side openings.
    slot_width=v('Diverter half width',r.add(r.mul(w,r.real(1.06)),r.length(.025*S)))
    slot=rounded('Diverter slot section',[r.neg(forelower),lip_roof,r.sub(ay,slot_width)],
                 r.length(.014*S))
    slot=v('Open diverter gap',r.bound(r.both(slot,r.sub(r.sub(leading,r.length(.12*S)),x),
                     r.sub(x,r.length((-1.17-shift)*S))),[-3.8,-1.2,-.5],[-1.16,1.2,.2]),'implicit','Native surfaces')

    from native_gap_divider import build_gap_splitter
    divider=build_gap_splitter(r,x=x,y=y,z=z,ay=ay,w=w,forelower=forelower,
                             lip_roof=lip_roof,scale=scale,S=S,aft_station_source=-1.20-shift)
    solid=v('Cowl forebody and gap splitter',r.bound(r.either(solid,divider),
                   [-5.65,-1,-1],[4.45,1,1]),'implicit','Native surfaces')
    slot=v('Diverter side passages',r.bound(r.both(slot,r.neg(divider)),
                   [-3.8,-1.2,-.5],[-1.16,1.2,.2]),'implicit','Native surfaces')

    # Keep the existing entry roof independent of the exterior rear closure.
    # Previously min(x,-1.6) was always ahead of closure onset -1.38, so the
    # sampled mixed roof was exactly the guarded roof. Refer to that branch
    # directly to preserve the conceptual cavity during this exterior change.
    freeze_x=v('Inlet roof station clamp',r.call('min<real_field,real_field>','real_field',x,r.length(-1.6*S)))
    roof=v('Duct entry roof field',r.call('remap<real_field,real_field,real_field,real_field>',
                         'real_field',guarded_roof,freeze_x,y,r.add(z,thickness)))
    floor=bottom('Duct entry floor spline',r.sub(depth,wall),r.sub(w,wall))
    top_width=v('Duct entry upper half width',r.sub(w,wall))
    bottom_width=v('Duct entry lower half width',r.mul(top_width,r.real(.70)))
    ceiling_z=v('Duct nominal ceiling',r.neg(r.add(r.call('min<real_field,real_field>','real_field',foredepth,r.length(.235*S)),thickness)))
    floor_z=v('Duct nominal floor',r.neg(r.sub(depth,wall)))
    height_fraction=v('Duct side height fraction',clamp(div(r.sub(localz,floor_z),r.sub(ceiling_z,floor_z))))
    width_z=v('Duct sloped side half width',r.add(bottom_width,r.mul(r.sub(top_width,bottom_width),height_fraction)))
    inner_corner=v('Inner inlet corner radius',r.call('max<real_field,real_field>',
        'real_field',r.length(.005*S),r.sub(corner,r.mul(r.add(wall,thickness),r.real(.5)))))
    trap=rounded('Rounded inlet profile',[r.neg(roof),floor,r.sub(ay,width_z)],inner_corner)

    # Native spline guides describe an open RC concept passage. They are not an
    # inference of the production engine installation from photographs.
    center_rows=np.array([[-5.65,-.45],[-3.4,-.45],[-1.6,-.43],[-.5,-.26],
                          [.8,-.10],[2.1,-.015],[2.9,0],[4.7,0]])
    radius_rows=np.array([[-5.65,.21],[-3.4,.21],[-1.6,.21],[-.5,.255],
                          [.8,.30],[2.9,.30],[4.1,.326],[4.7,.326]])
    from scipy.interpolate import PchipInterpolator
    cx=np.linspace(-5.65,4.7,700)
    center_raw=guide('Duct center height',cx,PchipInterpolator(center_rows[:,0],center_rows[:,1])(cx)+1,28)
    center=v('Duct centerline height',r.sub(center_raw,r.length(S)))
    radius_raw=guide('Duct round section radius',cx,PchipInterpolator(radius_rows[:,0],radius_rows[:,1])(cx),28)
    radius=v('Duct circular radius',r.mul(radius_raw,div(outlet,r.length(.326*S))))
    dz=v('Height from duct centerline',r.sub(z,center))
    circle=v('Circular duct section',r.sub(r.call('sqrt<real_field>','real_field',
                     r.add(r.mul(y,y),r.mul(dz,dz))),radius))
    morph=transition('Inlet to round duct transition',-1.6,.8)
    loft=v('Continuous section loft',mix(trap,circle,morph))
    # Finish at the existing outlet's exact constant section.
    exit_mix=transition('Outlet straightening',3.55,4.1)
    exit_field=v('Exact outlet circular field',r.sub(r.call('sqrt<real_field>','real_field',
                             r.add(r.mul(y,y),r.mul(z,z))),outlet))
    loft=v('Through duct loft field',mix(loft,exit_field,exit_mix))
    cavity=v('Continuous inlet to exhaust cavity',r.bound(r.both(loft,
                    r.sub(r.length(-3.8*S),x),r.sub(x,r.length(4.7*S))),
                    [-3.8,-1,-1],[4.7,1,1]),'implicit','Native surfaces')
    body=v('Fuselage native loft',r.bound(r.both(solid,r.neg(slot),r.neg(cavity)),
                         [-5.65,-1,-1],[4.45,1,1]),'implicit','Native exterior')
    exhaust=v('Through exhaust outlet',r.call('cylinder<point,point,real>','cylinder',
             r.point([4.05*S,0,0]),r.point([4.7*S,0,0]),outlet),'cylinder','Native surfaces')

    for name,field,point in [('splitter leading edge',leading,[-3.3,0,0]),
                            ('splitter clearance',clearance,[-3.3,0,0])]:
        r.var('CHECK '+name,'real',r.call('evaluate_field<real_field,point>','real',field,
                    r.point(np.array(point)*S)),'Checks')
    return body,cavity,exhaust,slot,lip_roof,thickness,center,solid,divider
