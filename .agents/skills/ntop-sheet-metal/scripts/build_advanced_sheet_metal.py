"""Advanced sheet-metal recipes: exact sections and radial-distance remapping.

All dimensions are authored study choices in mm. These are geometric targets,
not predictions of the plastic forming process. Uses adjacent sheet-metal core.
"""
import argparse,json,math
from pathlib import Path
import build_sheet_metal as api
from miter_geometry import Field,simpson

ROOT=Path.cwd()/'.local'/'sheet-metal-study'/'advanced'
KEYS=['mounting_hat','louver_panel','bead_panel','dimple_plate','drawn_tray']
def val(x):return x.value if isinstance(x,api.S) else x
def pair(p):return [val(v) for v in p]
def turn(u,a):return (u[0]*math.cos(a)-u[1]*math.sin(a),u[0]*math.sin(a)+u[1]*math.cos(a))

def strip(start,tangent,steps,t):
    """Exact offsets of a tangent chain with any fixed signed turn below 180 deg."""
    sides=[[],[]];p=start;u=tangent
    for kind,item in steps:
        n=api.left(u)
        if kind=='straight':
            assert val(item)>0
            end=api.addv(p,u,item)
            for edges,d in zip(sides,[t/2,-t/2]):edges.append(('line',[api.addv(p,n,d),api.addv(end,n,d)]))
            p=end;continue
        radius,deg=item;assert 0<abs(deg)<180;a=math.radians(deg);sign=1 if a>0 else -1
        center=api.addv(p,n,radius*sign);un=turn(u,a);nn=api.left(un);end=api.addv(center,nn,-radius*sign)
        for edges,d in zip(sides,[t/2,-t/2]):
            begin=api.addv(p,n,d);finish=api.addv(end,nn,d)
            rv=turn((begin[0]-center[0],begin[1]-center[1]),a/2)
            edges.append(('arc',[begin,api.addv(center,rv),finish]))
        p=end;u=un
    a,b=sides
    edges=a+[('line',[a[-1][1][-1],b[-1][1][-1]])]+[(kind,list(reversed(pts))) for kind,pts in reversed(b)]+[('line',[b[0][1][0],a[0][1][0]])]
    return edges,p

def section_integrals(edges):
    """Independent Green integrals: area and first radial moment of exact arcs."""
    area=moment=0.
    for kind,ps in edges:
        pts=[pair(p) for p in ps]
        if kind=='line':
            (x,y),(xx,yy)=pts;dy=yy-y
            area+=dy*(x+xx)/2;moment+=dy*(x*x+x*xx+xx*xx)/6
        else:
            (x1,y1),(x2,y2),(x3,y3)=pts
            d=2*(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2));assert abs(d)>1e-10
            q1=x1*x1+y1*y1;q2=x2*x2+y2*y2;q3=x3*x3+y3*y3
            cx=(q1*(y2-y3)+q2*(y3-y1)+q3*(y1-y2))/d;cy=(q1*(x3-x2)+q2*(x1-x3)+q3*(x2-x1))/d
            radius=math.hypot(x1-cx,y1-cy);angles=[math.atan2(y-cy,x-cx) for x,y in pts]
            a=angles[0];sweep=(angles[2]-a)%(2*math.pi)
            if (angles[1]-a)%(2*math.pi)>sweep:sweep-=2*math.pi
            area+=simpson(lambda v:(cx+radius*math.cos(a+sweep*v))*radius*math.cos(a+sweep*v)*sweep,0,1)
            moment+=simpson(lambda v:.5*(cx+radius*math.cos(a+sweep*v))**2*radius*math.cos(a+sweep*v)*sweep,0,1)
    return abs(area),abs(moment)

def basic(key,title,t0,ri0):
    r=api.Recipe(key,title);t=r.param('Thickness',t0);ri=r.param('Inside bend radius',ri0)
    ro=r.named_scalar('Outside bend radius',ri+t);rm=r.named_scalar('Midsurface radius',ri+t/2)
    return r,t,ri,ro,rm

def plate(r,name,L,W,t,z=0):
    p=r.profile(name+' outline',api.polygon_edges([(-L/2,-W/2),(L/2,-W/2),(L/2,W/2),(-L/2,W/2)]),lambda x,y:(x,y,z),(0,0,1))
    return r.extrude(name,p,t,(0,0,1))

def rect_cut(r,name,x0,x1,y0,y1,z0,z1):
    # Native coordinate fields are exact for these axis-aligned rectangular cuts.
    # Reuse them to avoid many redundant CAD profile evaluations in the lances.
    if not hasattr(r,'_cut_coords'):r._cut_coords=coords(r)
    X,Y,Z=r._cut_coords
    fx=(X-(x0+x1)/2).abs()-(x1-x0)/2
    fy=(Y-(y0+y1)/2).abs()-(y1-y0)/2
    fz=(Z-(z0+z1)/2).abs()-(z1-z0)/2
    return bound(r,name,fx.maximum(fy).maximum(fz),[x0,y0,z0],[x1,y1,z1])

def slot(r,name,x,y,length,width,z0,z1):
    rad=width/2;s=(length-width)/2
    edges=[('line',[(x-s,y-rad),(x+s,y-rad)]),('arc',[(x+s,y-rad),(x+s+rad,y),(x+s,y+rad)]),('line',[(x+s,y+rad),(x-s,y+rad)]),('arc',[(x-s,y+rad),(x-s-rad,y),(x-s,y-rad)])]
    p=r.profile(name+' profile',edges,lambda a,b:(a,b,z0),(0,0,1))
    return r.extrude(name,p,z1-z0,(0,0,1))

def hole(r,name,x,y,diam,z0,z1):
    return r.hold(name,'cylinder',r.node('cylinder<point,point,real>','cylinder',[r.pt([x,y,z0]),r.pt([x,y,z1]),(diam/2).wire if isinstance(diam,api.S) else api.real(diam/2,1)]))

def revolve(r,name,edges):
    p=r.profile(name+' meridian',edges,lambda rad,z:(rad,0,z),(0,-1,0))
    axis=r.node('axis<point,vector>','axis',[api.literal_point([0,0,0]),api.vector([0,0,1])])
    angle={'type':'real','value':{'isFinite':True,'units':{'angle':1},'val':2*math.pi}}
    return r.hold(name,'implicit',r.node('revolve<new_profile,axis,real>[5.20.0]','implicit',[p,axis,angle]))

def coords(r):
    out=[]
    for i,name in enumerate('XYZ'):
        n=[0,0,0];n[i]=1
        p=r.hold(name+' plane','plane',r.node('plane_from_normal<point,vector>[1.1.0]','plane',[api.literal_point([0,0,0]),api.vector(n)]),'Calculations')
        out.append(Field(r,api,r.hold(name+' field','real_field',api.ref(p['ref']['id'],'scalar field'),'Calculations')))
    return out

def bound(r,name,field,low,high):
    box=r.node('create_bounding_box<point,point>','bounding_box',[r.pt(low),r.pt(high)])
    return r.hold(name,'implicit',r.node('set_bounding_box<implicit,bounding_box>','implicit',[field.wire,box]))

def mapped(r,name,master,rho,Z,low,high):
    zero=Field(r,api,api.real(0,1))
    field=Field(r,api,r.node('remap<real_field,real_field,real_field,real_field>','real_field',[api.ref(master['ref']['id'],'scalar field'),rho.wire,zero.wire,Z.wire]))
    return bound(r,name,field,low,high)

def check(r,body,name,p,expectation):r.check('CHECK '+name,body,[val(x) for x in p],expectation)
def base_meta(t,ri,volume,**kw):return {'thickness_mm':val(t),'inside_radius_mm':val(ri),'analytic_formed_volume_mm3':volume,'forming_simulated':False,**kw}

def mounting_hat():
    r,t,ri,ro,rm=basic('mounting_hat','06 - Slotted hat mounting rail',1.5,2)
    L=r.param('Length',180);rise=r.param('Crown rise',25);foot=r.param('Foot tangent width',16);crown=r.param('Crown tangent width',34);K=r.param('K factor',.42,0)
    h=r.named_scalar('Wall tangent height',rise-2*rm);W=r.named_scalar('Outside width',2*foot+crown+4*rm)
    steps=[('straight',foot),('bend',(rm,90)),('straight',h),('bend',(rm,-90)),('straight',crown),('bend',(rm,-90)),('straight',h),('bend',(rm,90)),('straight',foot)]
    edges,_=strip((-W/2,t/2),(1,0),steps,t);p=r.profile('Four bend hat section',edges,lambda y,z:(-L/2,y,z),(1,0,0));stock=r.extrude('Rail stock',p,L,(1,0,0))
    sw=r.param('Slot width',5);sl=r.param('Slot length',18);dh=r.param('Crown hole diameter',8);tools=[]
    for sx in [-1,1]:
        for sy in [-1,1]:tools.append(slot(r,f'Foot slot {sx} {sy}',L*.3*sx,(W/2-foot/2)*sy,sl,sw,-t,2*t))
    for i,f in enumerate([-.33,-.11,.11,.33]):tools.append(hole(r,f'Crown hole {i}',L*f,0,dh,-t,rise+2*t))
    body=r.boolean('subtract','Formed mounting rail',tools,base=stock)
    ba=r.named_scalar('90 degree allowance',(ri+K*t)*(math.pi/2));fw=r.named_scalar('Flat width',2*foot+2*h+crown+4*ba)
    flatstock=plate(r,'Flat stock',L,fw,t);ftools=tools[4:]
    for sx in [-1,1]:
        for sy in [-1,1]:ftools.append(slot(r,f'Flat foot slot {sx} {sy}',L*.3*sx,(fw/2-foot/2)*sy,sl,sw,-t,2*t))
    flat=r.boolean('subtract','Flat mounting rail',ftools,base=flatstock)
    check(r,body,'crown stock',[0,0,rise+t/2],'negative');check(r,body,'crown top',[0,0,rise+t],'zero');check(r,body,'crown bottom',[0,0,rise],'zero')
    check(r,body,'cavity',[0,0,rise/2],'positive');check(r,body,'foot',[0,W/2-foot/2,t/2],'negative')
    for sx in [-1,1]:
        for sy in [-1,1]:
            check(r,body,f'slot {sx} {sy}',[L*.3*sx,(W/2-foot/2)*sy,t/2],'positive')
            check(r,flat,f'flat slot {sx} {sy}',[L*.3*sx,(fw/2-foot/2)*sy,t/2],'positive')
    for i,f in enumerate([-.33,-.11,.11,.33]):check(r,body,f'crown hole {i}',[L*f,0,rise+t/2],'positive')
    # Sample a full 90-degree root across its thickness.
    cy=-W/2+foot;cz=t/2+rm
    for rho,label,ex in [(ri,'inner','zero'),(rm,'middle','negative'),(ro,'outer','zero')]:check(r,body,'root '+label,[0,cy+rho/math.sqrt(2),cz-rho/math.sqrt(2)],ex)
    check(r,flat,'flat stock',[0,0,t/2],'negative');check(r,flat,'flat edge',[0,fw/2,t/2],'zero')
    area,_=section_integrals(edges);cuts=4*((sl.value-sw.value)*sw.value+math.pi*(sw.value/2)**2)+4*math.pi*(dh.value/2)**2
    volume=area*L.value-cuts*t.value
    return r,body,base_meta(t,ri,volume,outside_mm=[L.value,W.value,rise.value+t.value],flat_body='Flat mounting rail',flat_extents_mm=[L.value,fw.value],analytic_flat_volume_mm3=(L.value*fw.value-cuts)*t.value,K=K.value,bend_count=4,summary='Four signed 90-degree bends, four rounded foot slots and four crown holes.',source_id='protolabs-bends')

def louver_panel():
    r,t,ri,ro,rm=basic('louver_panel','07 - Louvered panel with edge flanges',1,1.5)
    L=r.param('Length',180);W=r.param('Outside width',120);H=r.param('Edge flange height',12);K=r.param('K factor',.42,0)
    B=r.named_scalar('Floor half width',W/2-ro);h=H-ro;fw=2*B+2*h+2*(ri+K*t)*(math.pi/2)
    uedges,_=strip((-W/2+t/2,H),(0,-1),[('straight',h),('bend',(rm,90)),('straight',2*B),('bend',(rm,90)),('straight',h)],t)
    p=r.profile('Flanged panel section',uedges,lambda y,z:(-L/2,y,z),(1,0,0));base=r.extrude('Panel stock',p,L,(1,0,0))
    width=r.param('Louver span',56);leg=r.param('Louver tangent length',12);kerf=r.param('Lance clearance',.3);theta=math.pi/6
    dev=r.named_scalar('Louver developed length',(ri+K*t)*theta+leg)
    opening=r.named_scalar('Lance opening length',rm*theta+leg+kerf)
    centers=[(L*sx/4,W*row) for sx in [-1,1] for row in [-.32,-.09,.14]]
    cut=[];flaps=[];flatcuts=[];flaparea=0
    for i,(x,y) in enumerate(centers):
        cut.append(rect_cut(r,f'Louver opening {i}',x-width/2-kerf,x+width/2+kerf,y,y+opening,-t,2*t))
        edges,_=strip((-2*t,t/2),(1,0),[('straight',2*t),('bend',(rm,30)),('straight',leg)],t)
        p=r.profile(f'Louver section {i}',edges,lambda q,z,x=x,y=y:(x-width/2,y+q,z),(1,0,0));flaps.append(r.extrude(f'Louver flap {i}',p,width,(1,0,0)))
        flaparea=section_integrals(edges)[0]
        flatcuts.append(rect_cut(r,f'Lance left {i}',x-width/2-kerf,x-width/2,y,y+opening,-t,2*t))
        flatcuts.append(rect_cut(r,f'Lance right {i}',x+width/2,x+width/2+kerf,y,y+opening,-t,2*t))
        flatcuts.append(rect_cut(r,f'Lance front {i}',x-width/2-kerf,x+width/2+kerf,y+dev,y+opening,-t,2*t))
    openings=r.boolean('subtract','Panel with openings',cut,base=base);joined=r.boolean('union','Formed louver stock',[openings,*flaps])
    dh=r.param('Mounting hole diameter',4);mounts=[(sx*(L/2-10),sy*(B-10)) for sx in [-1,1] for sy in [-1,1]]
    holes=[hole(r,f'Mounting hole {i}',x,y,dh,-t,2*t) for i,(x,y) in enumerate(mounts)]
    body=r.boolean('subtract','Formed louver panel',holes,base=joined)
    flatstock=plate(r,'Developed panel stock',L,fw,t);flat=r.boolean('subtract','Flat louver panel',[*flatcuts,*holes],base=flatstock)
    check(r,body,'floor stock',[0,0,t/2],'negative');check(r,body,'side wall',[0,W/2-t/2,H/2],'negative');check(r,body,'side top',[0,W/2-t/2,H],'zero')
    for i,(x,y) in enumerate(centers):
        q=rm*math.sin(theta)+leg*.55*math.cos(theta);z=t/2+rm*(1-math.cos(theta))+leg*.55*math.sin(theta)
        check(r,body,f'louver {i} stock',[x,y+q,z],'negative');check(r,body,f'louver {i} airflow',[x,y+q,z/2],'positive')
        for sign in [-1,1]:check(r,body,f'louver {i} face {sign}',[x,y+q-t/2*math.sin(theta)*sign,z+t/2*math.cos(theta)*sign],'zero')
        check(r,flat,f'flat flap {i}',[x,y+dev/2,t/2],'negative');check(r,flat,f'flat lance {i}',[x,y+dev+kerf/2,t/2],'positive')
    for i,(x,y) in enumerate(mounts):check(r,body,f'mount {i}',[x,y,t/2],'positive')
    ar,_=section_integrals(uedges);holearea=4*math.pi*(dh.value/2)**2
    removed=(width.value+2*kerf.value)*opening.value*t.value
    added=flaparea*width.value-2*t.value*t.value*width.value
    volume=ar*L.value+6*(added-removed)-holearea*t.value
    slitarea=2*kerf.value*opening.value+width.value*(opening.value-dev.value)
    return r,body,base_meta(t,ri,volume,outside_mm=[L.value,W.value,H.value],flat_body='Flat louver panel',flat_extents_mm=[L.value,val(fw)],analytic_flat_volume_mm3=(L.value*val(fw)-6*slitarea-holearea)*t.value,K=K.value,louver_angle_degrees=30,louver_count=6,lance_opening_length_mm=opening.value,flat_front_clearance_mm=opening.value-dev.value,summary='Six 30-degree open-ended louvers in a panel with two 90-degree edge flanges.',source_id='mate-louvers')

def bead_panel():
    r,t,ri,ro,rm=basic('bead_panel','08 - Panel with three closed stiffening beads',1,1.5)
    L=r.param('Length',160);W=r.param('Width',110);H=r.param('Bead rise',5);top=r.param('Bead top half width',4);straight=r.param('Bead straight length',70)
    edges,end=strip((0,H+t/2),(1,0),[('straight',top),('bend',(rm,-90)),('straight',H-2*rm),('bend',(rm,90)),('straight',3*t)],t)
    master=revolve(r,'Circular emboss master',edges);rend=end[0];root=top+2*rm;cutrad=root+t/2
    X,Y,Z=coords(r);base=plate(r,'Panel stock',L,W,t);cutters=[];patches=[]
    for i,cy in enumerate([-W*.255,0,W*.255]):
        dx=(X.abs()-straight/2).maximum(0);dy=Y-cy;rho=(dx*dx+dy*dy).sqrt().named(f'Bead {i} radius')
        cutters.append(bound(r,f'Bead core cut {i}',rho-cutrad,[-L/2,-W/2,-t],[L/2,W/2,2*t]))
        patches.append(mapped(r,f'Closed bead {i}',master,rho,Z,[-straight/2-rend,cy-rend,0],[straight/2+rend,cy+rend,H+t]))
    opened=r.boolean('subtract','Panel openings',cutters,base=base);joined=r.boolean('union','Beaded stock',[opened,*patches])
    dh=r.param('Mounting hole diameter',4);holes=[hole(r,f'Mount {i}',sx*(L/2-8),sy*(W/2-8),dh,-t,2*t) for i,(sx,sy) in enumerate(((-1,-1),(-1,1),(1,-1),(1,1)))]
    body=r.boolean('subtract','Formed bead panel',holes,base=joined)
    for i,cy in enumerate([-W*.255,0,W*.255]):
        check(r,body,f'bead {i} top stock',[0,cy,H+t/2],'negative');check(r,body,f'bead {i} cavity',[0,cy,H/2],'positive')
        check(r,body,f'bead {i} top',[0,cy,H+t],'zero');check(r,body,f'bead {i} underside',[0,cy,H],'zero')
        # Closed end and straight side are made from the same meridian.
        radial=top+rm/math.sqrt(2);zz=H+t/2-rm+rm/math.sqrt(2)
        for rho,label,ex in [(ri,'inner','zero'),(rm,'mid','negative'),(ro,'outer','zero')]:
            rr=top+rho/math.sqrt(2);z=H+t/2-rm+rho/math.sqrt(2)
            check(r,body,f'bead {i} side {label}',[0,cy+rr,z],ex)
            check(r,body,f'bead {i} end {label}',[straight/2+rr,cy,z],ex)
    check(r,body,'inter-bead floor',[0,W*.1275,t/2],'negative');check(r,body,'panel edge',[L/2,0,t/2],'zero')
    area,moment=section_integrals(edges);patchvolume=2*math.pi*moment+2*area*straight.value;footprint=math.pi*val(rend)**2+2*val(rend)*straight.value
    volume=L.value*W.value*t.value+3*(patchvolume-footprint*t.value)-4*math.pi*(dh.value/2)**2*t.value
    return r,body,base_meta(t,ri,volume,outside_mm=[L.value,W.value,H.value+t.value],bead_count=3,bead_rise_mm=H.value,developed_blank=False,summary='Three closed capsule beads with exact root/crown radii and a hollow underside.',source_id='mate-emboss')

def dimple_plate():
    r,t,ri,ro,rm=basic('dimple_plate','09 - Plate with six dimpled holes',1.2,1)
    L=r.param('Length',150);W=r.param('Width',110);H=r.param('Dimple depth',3);rh=r.param('Hole radius',4);lip=r.param('Inner lip width',1.5)
    a=math.pi/4;rise=r.named_scalar('Cone tangent rise',H-2*rm*(1-math.cos(a)));cone=rise/math.sin(a)
    edges,end=strip((rh,t/2-H),(1,0),[('straight',lip),('bend',(rm,45)),('straight',cone),('bend',(rm,-45)),('straight',3*t)],t)
    master=revolve(r,'Dimple master',edges);rend=end[0];root=rend-3*t;cutrad=root+t/2
    X,Y,Z=coords(r);base=plate(r,'Panel stock',L,W,t);cutters=[];patches=[];centers=[(L*fx,W*fy) for fx in [-.28,0,.28] for fy in [-.24,.24]]
    for i,(cx,cy) in enumerate(centers):
        dx=X-cx;dy=Y-cy;rho=(dx*dx+dy*dy).sqrt().named(f'Dimple {i} radius')
        cutters.append(bound(r,f'Dimple core cut {i}',rho-cutrad,[cx-cutrad,cy-cutrad,-t],[cx+cutrad,cy+cutrad,2*t]))
        patches.append(mapped(r,f'Dimple {i}',master,rho,Z,[cx-rend,cy-rend,-H],[cx+rend,cy+rend,t]))
    opened=r.boolean('subtract','Pierced panel',cutters,base=base);joined=r.boolean('union','Dimpled stock',[opened,*patches])
    dh=r.param('Mounting hole diameter',4);holes=[hole(r,f'Mount {i}',sx*(L/2-8),sy*(W/2-8),dh,-t,2*t) for i,(sx,sy) in enumerate(((-1,-1),(-1,1),(1,-1),(1,1)))]
    body=r.boolean('subtract','Formed dimple plate',holes,base=joined)
    for i,(cx,cy) in enumerate(centers):
        check(r,body,f'hole {i}',[cx,cy,-H+t/2],'positive');check(r,body,f'lip {i}',[cx+rh+lip/2,cy,-H+t/2],'negative')
        rad=rh+lip+rm*math.sin(a)+cone/2*math.cos(a);z=t/2-H+rm*(1-math.cos(a))+cone/2*math.sin(a)
        check(r,body,f'cone {i} stock',[cx+rad,cy,z],'negative')
        for sign in [-1,1]:check(r,body,f'cone {i} face {sign}',[cx+rad-t/2*math.sin(a)*sign,cy,z+t/2*math.cos(a)*sign],'zero')
    check(r,body,'floor stock',[0,0,t/2],'negative');check(r,body,'bottom lip',[rh+lip/2,W*.24,-H],'zero')
    area,moment=section_integrals(edges);patchvolume=2*math.pi*moment
    volume=L.value*W.value*t.value+6*(patchvolume-math.pi*val(rend)**2*t.value)-4*math.pi*(dh.value/2)**2*t.value
    return r,body,base_meta(t,ri,volume,outside_mm=[L.value,W.value,H.value+t.value],dimple_count=6,dimple_depth_mm=H.value,cone_angle_degrees=45,hole_diameter_mm=2*rh.value,developed_blank=False,summary='Six pierced 45-degree dimples with circular root blends, inner lips and four mounting holes.',source_id='mate-emboss')

def drawn_tray():
    r,t,ri,ro,rm=basic('drawn_tray','10 - Continuous rounded tray with mounting flange',1.2,2)
    L=r.param('Outside length',160);W=r.param('Outside width',120);H=r.param('Flange rise',18);floorR=r.param('Floor plan radius',12);flange=r.param('Flange tangent width',10)
    edges,end=strip((0,t/2),(1,0),[('straight',floorR),('bend',(rm,90)),('straight',H-2*rm),('bend',(rm,-90)),('straight',flange)],t)
    master=revolve(r,'Round tray meridian master',edges);rend=end[0];A=r.named_scalar('Core half length',L/2-rend);B=r.named_scalar('Core half width',W/2-rend)
    X,Y,Z=coords(r);dx=(X.abs()-A).maximum(0);dy=(Y.abs()-B).maximum(0);rho=(dx*dx+dy*dy).sqrt().named('Rounded rectangle radial distance')
    stock=mapped(r,'Continuous tray stock',master,rho,Z,[-L/2,-W/2,0],[L/2,W/2,H+t])
    sw=r.param('Slot width',3.5);sl=r.param('Slot length',12);cuts=[]
    for sx in [-1,1]:
        for sy in [-1,1]:cuts.append(slot(r,f'Flange slot {sx} {sy}',A*.62*sx,(W/2-flange/2)*sy,sl,sw,H-t,H+2*t))
    body=r.boolean('subtract','Formed drawn tray',cuts,base=stock)
    check(r,body,'floor stock',[0,0,t/2],'negative');check(r,body,'floor top',[0,0,t],'zero');check(r,body,'cavity',[0,0,H/2],'positive')
    check(r,body,'straight wall',[0,B+floorR+rm,H/2+t/2],'negative');check(r,body,'flange top',[0,W/2-flange/2,H+t],'zero')
    for sx in [-1,1]:
        for sy in [-1,1]:
            check(r,body,f'corner wall {sx} {sy}',[sx*(A+(floorR+rm)/math.sqrt(2)),sy*(B+(floorR+rm)/math.sqrt(2)),H/2+t/2],'negative')
            check(r,body,f'slot {sx} {sy}',[A*.62*sx,(W/2-flange/2)*sy,H+t/2],'positive')
    for phi in [0,math.pi/4]:
        for rho,label,ex in [(ri,'inner','zero'),(rm,'middle','negative'),(ro,'outer','zero')]:
            rad=floorR+rho/math.sqrt(2);z=t/2+rm-rho/math.sqrt(2)
            check(r,body,f'root {phi} {label}',[A+rad*math.cos(phi),B+rad*math.sin(phi),z],ex)
    area,moment=section_integrals(edges);corearea=4*A.value*B.value;perimeter=4*(A.value+B.value)
    slotarea=4*((sl.value-sw.value)*sw.value+math.pi*(sw.value/2)**2)
    volume=corearea*t.value+perimeter*area+2*math.pi*moment-slotarea*t.value
    return r,body,base_meta(t,ri,volume,outside_mm=[L.value,W.value,H.value+t.value],flange_rise_mm=H.value,floor_plan_radius_mm=floorR.value,developed_blank=False,summary='Continuous rounded corners, true bottom and rim bends, an outward flange and four mounting slots.',source_id='drawn-trays')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',choices=['all',*KEYS],default='all');ap.add_argument('--out',type=Path,default=ROOT);a=ap.parse_args();api.ROOT=a.out.resolve()
    for d in ['models','evidence','inputs','reports/assets','.local']:(api.ROOT/d).mkdir(parents=True,exist_ok=True)
    records=[]
    for key in KEYS if a.case=='all' else [a.case]:
        r,body,meta=globals()[key]();records.append(api.write_case(r,body,meta))
    (api.ROOT/'evidence/design-summary.json').write_text(json.dumps(records,indent=2))
    print(json.dumps([{k:v for k,v in row.items() if k!='metadata'} for row in records],indent=2))
if __name__=='__main__':main()
