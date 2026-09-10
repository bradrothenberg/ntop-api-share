"""P1 bolted architecture, native fasteners, mating holes, and assembly ledger."""
from pathlib import Path
import math,json
from native_graph import real,literal
ROOT=Path(__file__).resolve().parents[1]
METAL=(.57,.62,.67); HARD=(.30,.34,.39); SEAL=(.27,.31,.28)

def detail(g,ctx):
    c=ctx['c'];s=ctx['s'];P=ctx['P'];par=ctx['param'];H=json.loads((ROOT/'inputs/hardware.json').read_text())
    def A(a,b):return g.math('add',a,b if isinstance(b,dict) else real(b))
    def S(a,b):return g.math('subtract',a,b if isinstance(b,dict) else real(b))
    def M(a,k):return g.math('multiply',a,real(k,''))
    def ref(name):return {'props':[],'ref':{'id':next(b['id'] for b in g.body if b['name']==name)}}
    def replace(name,body):next(b for b in g.body if b['name']==name)['contents']=body
    def old(name):return next(b for b in g.body if b['name']==name)['contents']
    def drill(name,holes):replace(name,g.sub(old(name),*holes))
    def extend(name,*bodies):replace(name,g.union(old(name),*bodies))
    def part(name,body,system='09 Assembly structures',**kw):return g.part(name,body,METAL,system,**kw)
    def rename(a,b):
        row=next(x for x in g.body if x['name']==a);row['name']=b
        next(x for x in g.parts if x['name']==a)['name']=b
        g.layout['variables'][b]=g.layout['variables'].pop(a)
        g.layout['final_bodies'][b]=g.layout['final_bodies'].pop(a)
    def ring(z0,z1,ro,ri):return g.ring(z0,z1,ro,ri)
    def hexprism(af,z0,z1):
        rr=af/math.sqrt(3)
        return g.prism([(rr*math.cos(k*math.pi/3),rr*math.sin(k*math.pi/3),z0) for k in range(6)],z1-z0,(0,0,1))
    def orient(b,axis):
        if axis=='-z':return g.rot(b,180,axis=(1,0,0))
        if axis=='x':return g.rot(b,90,axis=(0,1,0))
        if axis=='y':return g.rot(b,-90,axis=(1,0,0))
        if axis=='-y':return g.rot(b,90,axis=(1,0,0))
        return b
    def polar(body,count,phase=0):return g.rot(g.polar(body,count,axis=(0,0,1)),phase,axis=(0,0,1))
    templates={};ledger=[];joints=[]
    def hardware(d,L,grip,tapped=False):
        # Stack origin is the start of the joint. Screw insertion is +local Z.
        h=H['sizes'][str(d)];w=h['washer_thickness_mm'];n=h['nut_height_mm']
        key=(d,L)
        if key not in templates:
            shank=g.cyl((0,0,0),(0,0,L),d/2)
            head=g.cyl((0,0,-h['head_height_mm']),(0,0,0),h['head_diameter_mm']/2)
            socket=hexprism(h['socket_af_mm'],-h['head_height_mm']-.05,-h['head_height_mm']+h['socket_depth_mm'])
            templates[key]=g.var(f'HW M{d}x{L} socket screw',g.sub(g.union(shank,head),socket),'implicit')
        washer=ring(real(0),real(w),real(h['washer_od_mm']/2),real(h['washer_id_mm']/2))
        # Variables are reused by reference; placement expressions stay native.
        members=[g.move(templates[key],(0,0,-w)),g.move(washer,(0,0,-w))]
        if not tapped:
            nut=g.sub(hexprism(h['nut_af_mm'],0,n),g.cyl((0,0,-1),(0,0,n+1),d/2))
            members+=[g.move(washer,(0,0,grip)),g.move(nut,(0,0,A(grip,w)))]
        return g.union(*members)
    def axial_joint(jid,label,d,L,radius,z0,z1,count,plates,phase=0):
        grip=S(z1,z0);holeR=H['sizes'][str(d)]['clearance_hole_mm']/2
        pattern=polar(g.cyl((radius,0,S(z0,1)),(radius,0,A(z1,1)),holeR),count,phase)
        for p in plates:drill(p,[pattern])
        fast=polar(g.move(hardware(d,L,grip),(radius,0,z0)),count,phase)
        part('FAST '+jid+' '+label,fast,'10 Fasteners',count=count,fastener_count=count,hardware_group=jid)
        joints.append({'id':jid,'name':label,'size':d,'length_mm':L,'count':count,'pattern':'axial circle','radius':radius,'z0':z0,'z1':z1,'phase_deg':phase,'parts':plates,'hole_diameter_mm':holeR*2,'tapped':False})
    def cart_joint(jid,label,d,L,points,axis,grip,plates,tapped=False):
        h=H['sizes'][str(d)];clearance=h['clearance_hole_mm']/2
        holes=[g.move(orient(g.cyl((0,0,-1),(0,0,A(grip,1)),clearance),axis),p) for p in points]
        for index,p in enumerate(plates):
            if tapped and index==len(plates)-1:
                threadholes=[g.move(orient(g.cyl((0,0,S(grip,.1)),(0,0,real(L-h['washer_thickness_mm']+.5)),d/2),axis),pt) for pt in points]
                drill(p,threadholes)
            else:drill(p,holes)
        fast=[g.move(orient(hardware(d,L,grip,tapped),axis),p) for p in points]
        part('FAST '+jid+' '+label,g.union(*fast),'10 Fasteners',count=len(points),fastener_count=len(points),hardware_group=jid)
        joints.append({'id':jid,'name':label,'size':d,'length_mm':L,'count':len(points),'pattern':'cartesian','points':points,'axis':axis,'grip':grip,'parts':plates,'hole_diameter_mm':clearance*2,'tapped':tapped})
    def radial_joint(jid,label,d,L,z,count,receiver,case_name,phase=0):
        # Nominal thread envelopes in the receiver; external case clearance hole.
        start=ctx['Rout'];receiverDepth=real(L-H['sizes'][str(d)]['washer_thickness_mm']-c['case_wall_m']*1000)
        clearhole=polar(g.cyl((S(ctx['cr'],.1),0,z),(A(start,1),0,z),H['sizes'][str(d)]['clearance_hole_mm']/2),count,phase)
        taphole=polar(g.cyl((S(ctx['cr'],A(receiverDepth,.5)),0,z),(A(ctx['cr'],.1),0,z),d/2),count,phase)
        drill(case_name,[clearhole]);drill(receiver,[taphole])
        b=g.rot(hardware(d,L,ctx['wall'],True),-90,axis=(0,1,0))
        part('FAST '+jid+' '+label,polar(g.move(b,(start,0,z)),count,phase),'10 Fasteners',count=count,fastener_count=count,hardware_group=jid)
        joints.append({'id':jid,'name':label,'size':d,'length_mm':L,'count':count,'pattern':'radial','radius':start,'z0':z,'phase_deg':phase,'parts':[case_name,receiver],'hole_diameter_mm':H['sizes'][str(d)]['clearance_hole_mm'],'tapped':True,'engagement':receiverDepth})

    g.section='09 Assembly structures'
    cr=ctx['cr'];Rout=ctx['Rout'];wall=ctx['wall'];ro=ctx['ro'];eye=ctx['eye'];tr=ctx['tr'];hr=ctx['hr'];sh=ctx['sh'];zt=ctx['zt'];zte=ctx['zte'];nz=ctx['nz'];zsh=ctx['zsh'];z1=ctx['z1'];zafter=ctx['zafter'];burnOR=ctx['burnOR'];burnIR=ctx['burnIR'];zburn=ctx['zburn'];zo=ctx['zo'];sv0=ctx['sv0'];sv1=ctx['sv1'];service=ctx['service']
    seeds=H['design_seeds_mm'];FR=par('Assembly flange outer radius',seeds['flange_radius']);BC=par('Assembly flange bolt radius',seeds['flange_pcd']/2);ft=par('Assembly flange thickness',seeds['flange_thickness']);split=par('Case split station',seeds['case_split_z']);gasket=par('Case gasket thickness',seeds['gasket_thickness']);gap=par('Compressor running gap',seeds['compressor_running_gap'])
    # The casing is split across Z, with external bolt circles outside the gas path.
    original=old('CASE Full casing')
    replace('CASE Full casing',g.union(g.inter(original,g.cyl((0,0,real(12)),(0,0,split),A(FR,2))),ring(real(12),A(real(12),ft),FR,cr),ring(S(split,ft),split,FR,cr)))
    rename('CASE Full casing','CASE Front barrel')
    part('CASE Rear barrel',g.union(g.inter(original,g.cyl((0,0,A(split,gasket)),(0,0,nz),A(FR,2))),ring(A(split,gasket),A(A(split,gasket),ft),FR,cr),ring(S(nz,ft),nz,FR,cr)))
    part('SEAL Case split gasket',ring(split,A(split,gasket),FR,A(cr,.1)),'09 Assembly structures')
    # An open inlet neck meets the shroud. It replaces the broad P0 envelope.
    inlet=g.union(ring(real(0),real(12),A(eye,wall),eye),ring(S(real(12),ft),real(12),FR,eye))
    replace('CASE Inlet bell',inlet)
    # Trim both axial caps from the offset shroud and leave the radial exit open.
    envelope=g.node('offset',ctx['outer'],gap)
    shell=g.inter(g.sub(g.node('offset',envelope,wall),envelope),g.cyl((0,0,ctx['z0']),(0,0,zsh),A(cr,2)))
    frontplate=ring(S(zsh,wall),zsh,cr,A(ro,gap))
    shell=g.union(shell,ring(real(12),ctx['z0'],A(A(eye,gap),wall),A(eye,gap)),frontplate)
    replace('COMP Shroud',shell)
    # P2: leave an annular turn around the vane-radius edge. Only local lugs reach case.
    replace('COMP Diffuser backplate',ring(z1,zafter,ctx['diffOuter'],A(ro,gap)))
    g.calc('CHECK diffuser outlet radial gap','subtract',cr,ctx['diffOuter'])
    # Six local standoffs make the diffuser a removable clamped module.
    postR=par('Diffuser bolt radius',52)
    postPhase=g.math('multiply',real(35,'angle'),g.math('divide',postR,ctx['diffOuter']))
    postXY=[]
    for k in [0,3,6,9,12,14]:
        angle=g.math('add',postPhase,real((k+.5)*360/17,'angle'))
        postXY.append((g.math('multiply',postR,g.math('cos',angle)),g.math('multiply',postR,g.math('sin',angle))))
    posts=g.union(*[g.cyl((x,y,zsh),(x,y,z1),2.6) for x,y in postXY])
    extend('COMP Shroud',posts)
    axial_joint('J01','Inlet module',4,16,BC,S(real(12),ft),A(real(12),ft),12,['CASE Inlet bell','CASE Front barrel'],15)
    axial_joint('J02','Case split',4,16,BC,S(split,ft),A(A(split,gasket),ft),12,['CASE Front barrel','CASE Rear barrel','SEAL Case split gasket'],15)
    extend('NOZZLE Convergent duct',ring(nz,A(nz,ft),FR,cr))
    axial_joint('J03','Exhaust module',4,16,BC,S(nz,ft),A(nz,ft),12,['CASE Rear barrel','NOZZLE Convergent duct'],15)
    cart_joint('J04','Diffuser module',3,16,[(x,y,S(zsh,wall)) for x,y in postXY],'z',S(zafter,S(zsh,wall)),['COMP Shroud','COMP Diffuser backplate'])
    diffuserLugs=polar(g.box((S(cr,8),real(-4),S(z1,2)),(cr,real(4),A(zafter,3))),3,30)
    extend('COMP Diffuser backplate',diffuserLugs)
    radial_joint('J24','Diffuser carrier to case',3,8,A(z1,1.5),3,'COMP Diffuser backplate','CASE Front barrel',30)
    # Bearing outer-race housing, removable retainers, and stationary supports.
    front=P['Front bearing station'];rear=P['Rear bearing station'];rearEnd=A(rear,9);tubeEnd=A(rearEnd,1)
    housinggap=par('Bearing housing radial clearance',seeds['bearing_housing_radial_gap'])
    tube=ring(real(74),tubeEnd,real(12),A(real(9),housinggap))
    tube=g.union(tube,ring(real(74),real(77),real(19),A(real(9),housinggap)),ring(S(tubeEnd,3),tubeEnd,real(19),A(real(9),housinggap)))
    replace('SHAFT Bearing tunnel',tube)
    part('BEARING Front retainer',g.union(ring(real(72),real(74),real(19),real(4.3)),ring(real(74),front,real(8.9),real(6.1))))
    part('BEARING Rear retainer',g.union(ring(tubeEnd,A(tubeEnd,2),real(19),real(4.3)),ring(rearEnd,tubeEnd,real(8.9),real(6.1))))
    axial_joint('J07','Front bearing retainer',3,10,real(15),real(72),real(77),4,['BEARING Front retainer','SHAFT Bearing tunnel'],45)
    spider=g.union(ring(real(74),real(82),cr,S(cr,8)),polar(g.box((real(11),real(-1.5),real(75)),(cr,real(1.5),real(78))),3,30))
    extend('SHAFT Bearing tunnel',spider)
    radial_joint('J05','Front spider to case',3,8,real(78),3,'SHAFT Bearing tunnel','CASE Front barrel',30)
    # Guide-vane frame also supports the rear bearing inside the gas-path hub.
    innerband=ring(sv0,sv1,hr,S(hr,2));outerframe=ring(sv0,A(sv0,6),cr,A(tr,1.5))
    innerweb=g.sub(ring(A(tubeEnd,2),A(tubeEnd,5),hr,real(9.05)),polar(g.cyl((real(19),0,A(tubeEnd,1)),(real(19),0,A(tubeEnd,6)),1.5),3,30))
    extend('TURB Nozzle guide vanes',innerband,outerframe,innerweb)
    radial_joint('J06','Guide vane frame to case',3,8,A(sv0,3),6,'TURB Nozzle guide vanes','CASE Rear barrel',30)
    axial_joint('J08','Rear bearing and vane frame',3,14,real(15),S(tubeEnd,3),A(tubeEnd,5),4,['BEARING Rear retainer','SHAFT Bearing tunnel','TURB Nozzle guide vanes'],45)
    shroudPosts=polar(g.cyl((real(54.5),0,A(sv0,6)),(real(54.5),0,S(zt,1)),3),6)
    extend('TURB Tip shroud',ring(S(zt,1),zt,cr,A(tr,ctx['clear'])),shroudPosts)
    axial_joint('J22','Turbine shroud carrier',3,20,real(54.5),sv0,zt,6,['TURB Nozzle guide vanes','TURB Tip shroud'])
    # Liner transition shells close the former P0 gap before the guide vanes.
    outerTrans=g.sub(g.cone((0,0,zo),(0,0,sv0),burnOR,A(tr,1.5)),g.cone((0,0,S(zo,.1)),(0,0,A(sv0,.1)),S(burnOR,wall),tr))
    innerTrans=g.sub(g.cone((0,0,zo),(0,0,sv0),A(burnIR,wall),hr),g.cone((0,0,S(zo,.1)),(0,0,A(sv0,.1)),burnIR,S(hr,2)))
    extend('BURN Outer liner',outerTrans,ring(A(zburn,2),A(zburn,4),real(56),S(burnOR,wall)))
    extend('BURN Inner liner',innerTrans,ring(A(zburn,2),A(zburn,4),A(burnIR,wall),real(18)))
    outerTabs=polar(g.cyl((real(52.5),0,zburn),(real(52.5),0,A(zburn,2)),5),6,0)
    extend('BURN Dome',outerTabs,ring(zburn,A(zburn,2),A(burnIR,wall),real(18)))
    axial_joint('J09','Outer liner tabs',3,10,real(52.5),zburn,A(zburn,4),6,['BURN Dome','BURN Outer liner'])
    axial_joint('J10','Inner liner lip',3,10,real(22),zburn,A(zburn,4),4,['BURN Dome','BURN Inner liner'],45)
    linerLugs=polar(g.box((S(burnOR,wall),real(-4),A(zburn,2)),(cr,real(4),A(zburn,10))),3,30)
    extend('BURN Outer liner',linerLugs)
    radial_joint('J23','Liner carrier to case',3,8,A(zburn,6),3,'BURN Outer liner','CASE Front barrel',30)
    # Manifold saddles are split across the pipe center plane.
    mr=ctx['manifoldR'];mz=ctx['manifoldZ'];saddle=g.sub(g.box((S(mr,7),real(-3),A(zburn,2)),(A(mr,7),real(3),mz)),g.cyl((mr,real(-4),mz),(mr,real(4),mz),1.65))
    cap=g.sub(g.box((S(mr,7),real(-3),mz),(A(mr,7),real(3),A(mz,3))),g.cyl((mr,real(-4),mz),(mr,real(4),mz),1.65))
    part('FUEL Manifold saddles',polar(saddle,3,45));part('FUEL Manifold clamp caps',polar(cap,3,45))
    injectorPorts=polar(g.cyl((mr,0,S(mz,1)),(mr,0,A(mz,11)),.65),12)
    drill('FUEL Manifold',[injectorPorts,g.cyl(ctx['fuel_point'](S(mr,.05)),ctx['fuel_point'](A(mr,4)),1.65)])
    pts=[]
    for phi in [45,165,285]:
        for delta in [-4,4]:pts.append((M(A(mr,delta),math.cos(math.radians(phi))),M(A(mr,delta),math.sin(math.radians(phi))),zburn))
    cart_joint('J11','Manifold clamps',3,20,pts,'z',S(A(mz,3),zburn),['BURN Dome','FUEL Manifold saddles','FUEL Manifold clamp caps'])
    # Rotor clamping stack: one central shaft land permits end assembly.
    replace('SHAFT Common shaft',g.union(g.cyl((0,0,real(9)),(0,0,A(zte,13)),sh),g.cyl((0,0,real(100)),(0,0,real(105)),real(6))))
    sleeves=[ring(zafter,front,real(6),real(4.05)),ring(A(front,9),real(100),real(6),real(4.05)),ring(real(105),rear,real(6),real(4.05)),ring(rearEnd,S(zt,2),real(6),real(4.05))]
    part('SHAFT Inner race spacer sleeves',g.union(*sleeves),count=4)
    h8=H['sizes']['8'];nut=g.sub(hexprism(h8['nut_af_mm'],0,h8['nut_height_mm']),g.cyl((0,0,-1),(0,0,8),4))
    washer=ring(real(0),real(1.6),real(8),real(4.2))
    retention=g.union(g.move(nut,(0,0,real(11.9))),g.move(washer,(0,0,real(18.4))),g.move(washer,(0,0,A(zte,2))),g.move(nut,(0,0,A(zte,3.6))))
    part('FAST R01 Rotor retention nuts and washers',retention,'10 Fasteners',count=2,fastener_count=2,hardware_group='R01')
    joints.append({'id':'R01','name':'Rotor retention','size':8,'count':2,'pattern':'shaft nuts','parts':['SHAFT Common shaft','COMP Impeller','TURB Rotor blisk','SHAFT Inner race spacer sleeves'],'tapped':False,'note':'M8 x 1.25 nominal thread zones. Locking method, balance, and torque remain open.'})
    # Hollow stationary tail cone clears the rear nut; three exhaust struts hold it.
    cone0=A(zte,3);cone1=S(ctx['length'],13)
    tail=g.sub(g.cone((0,0,cone0),(0,0,cone1),hr,real(.8)),g.cone((0,0,S(cone0,.1)),(0,0,S(cone1,2)),S(hr,1.5),real(.4)))
    support=polar(g.box((M(hr,.68),real(-1),nz),(cr,real(1),A(nz,2.5))),3,30)
    replace('NOZZLE Center cone',g.union(tail,support))
    # Starter carrier attaches at the front module, clear of the retaining nut.
    replace('STARTER Motor envelope',g.cyl((0,0,real(-20)),(0,0,real(7)),real(11)))
    extend('STARTER Motor envelope',ring(real(5),real(7),real(18),real(4.3)))
    carrier=g.union(ring(real(7),real(9),real(18),real(4.3)),polar(g.box((real(17),real(-1.5),real(7)),(eye,real(1.5),real(10))),3,30))
    part('MOUNT Starter carrier',carrier)
    axial_joint('J12','Starter flange',3,10,real(15),real(5),real(9),3,['STARTER Motor envelope','MOUNT Starter carrier'],30)
    # Service tray and ECU backplate are integral sheet-metal bracket envelopes.
    fuel_service=service;service=ctx['p3']['cable']
    tray=g.union(g.box((real(-36),real(59),real(12)),(real(36),A(service,27),real(15))),g.box((real(-29),A(service,24),real(12)),(real(29),A(service,27),real(50))))
    tray=g.sub(tray,g.box((real(-16.1),S(service,4.1),real(10)),(real(25.1),A(service,4.1),real(20))))
    part('MOUNT Service tray and ECU bracket',tray)
    replace('ECU Service envelope',g.box((real(-19),A(service,9),real(10)),(real(19),A(service,24),real(48))))
    ecutabs=[]
    for x in [-23,23]:
        for z in [16,42]:ecutabs.append(g.box((real(x-4),A(service,20),real(z-4)),(real(x+4),A(service,24),real(z+4))))
    extend('ECU Service envelope',*ecutabs)
    cart_joint('J13','ECU mounting tabs',3,12,[(real(x),A(service,20),real(z)) for x in [-23,23] for z in [16,42]],'y',real(7),['ECU Service envelope','MOUNT Service tray and ECU bracket'])
    traypts=[(real(x),real(y),real(9)) for x in [-28,28] for y in [62,79]]
    extend('CASE Inlet bell',*[g.box((real(x-5),real(58),real(9)),(real(x+5),real(84),real(12))) for x in [-28,28]])
    extend('CASE Inlet bell',*[g.cyl((p[0],p[1],real(9)),(p[0],p[1],real(12)),5) for p in traypts])
    cart_joint('J14','Service tray to inlet module',3,12,[(x,y,real(9)) for x,y,z in traypts],'z',real(6),['CASE Inlet bell','MOUNT Service tray and ECU bracket'])
    # Pump foot is attached to the inlet flange; fuel supply remains external.
    service=fuel_service
    pumpfoot=g.box((S(service,13),real(-7),real(5)),(A(service,13),real(7),real(9)))
    replace('FUEL Pump envelope',g.union(g.cyl((service,real(0),real(-9)),(service,real(0),real(5)),real(6)),pumpfoot))
    pumppts=[(A(service,x),real(0),real(5)) for x in [-9,9]]
    extend('CASE Inlet bell',g.box((S(service,13),real(-7),real(9)),(A(service,13),real(7),real(12))))
    cart_joint('J15','Pump foot',3,12,pumppts,'z',real(7),['FUEL Pump envelope','CASE Inlet bell'])
    # Two split clamps capture the straight part of the main fuel line.
    clampHoles=[];caps=[];bases=[]
    for z in [30,60]:
        blank=g.box((S(service,4),real(-7.5),real(z-4.5)),(A(service,4),real(7.5),real(z+4.5)))
        cut=g.cyl((service,real(0),real(z-5.5)),(service,real(0),real(z+5.5)),1.65)
        base=g.inter(g.sub(blank,cut),g.box((S(service,4),real(-7.5),real(z-5.5)),(service,real(7.5),real(z+5.5))))
        cap=g.inter(g.sub(blank,cut),g.box((service,real(-7.5),real(z-5.5)),(A(service,4),real(7.5),real(z+5.5))))
        bases.append(g.union(base,g.box((A(Rout,1),real(-7.5),real(z-4.5)),(S(service,4),real(7.5),real(z+4.5)))))
        extend('CASE Front barrel',g.box((S(cr,1),real(-7.5),real(z-4.5)),(A(Rout,1),real(7.5),real(z+4.5))))
        caps.append(cap)
        for y in [-4.25,4.25]:clampHoles.append((S(cr,1),real(y),real(z)))
    part('MOUNT Main fuel clamp bases',g.union(*bases),count=2);part('MOUNT Main fuel clamp caps',g.union(*caps),count=2)
    cart_joint('J16','Fuel split clamps and case mounts',3,20,clampHoles,'x',S(A(service,4),S(cr,1)),['CASE Front barrel','MOUNT Main fuel clamp bases','MOUNT Main fuel clamp caps'])
    # A split cable guide supports all four bundles at the service connector bay.
    service=ctx['p3']['cable']
    wireholes=[g.cyl((real(x),service,real(10)),(real(x),service,real(20)),2.2) for x in [-8,0,8,15]]
    part('MOUNT Cable guide lower',g.sub(g.box((real(-16),S(service,4),real(11)),(real(25),service,real(19))),*wireholes))
    part('MOUNT Cable guide upper',g.sub(g.box((real(-16),service,real(11)),(real(25),A(service,4),real(19))),*wireholes))
    cart_joint('J19','Cable guide split',3,14,[(real(x),S(service,4),real(15)) for x in [-12,4,21]],'y',real(8),['MOUNT Cable guide lower','MOUNT Cable guide upper'])
    extend('MOUNT Cable guide lower',g.box((real(-24),S(service,6),real(15)),(real(-16),A(service,11),real(18))))
    extend('MOUNT Cable guide upper',g.box((real(25),service,real(15)),(real(33),A(service,6),real(18))))
    cart_joint('J20','Cable guide to tray',3,12,[(real(-20),A(service,7),real(12)),(real(29),A(service,3),real(12))],'z',real(6),['MOUNT Cable guide lower','MOUNT Cable guide upper','MOUNT Service tray and ECU bracket'])
    connectors=[]
    portz=ctx['p3']['connector_z']
    for name,x,rr in [('E01 Starter harness',0,2),('E02 Ignition lead',8,1.4),('E03 Temperature harness',-8,1.1),('E04 Speed pickup lead',15,1.1)]:
        extend(name,g.cyl((real(x),service,portz),(real(x),A(service,9),portz),rr))
        connectors.append(g.cyl((real(x),A(service,5),portz),(real(x),A(service,9),portz),rr+.5))
    part('ECU Connector plate',g.union(*connectors,g.box((real(-19),A(service,7),real(10)),(real(19),A(service,9),real(39)))))
    drill('ECU Connector plate',[g.cyl((x,A(service,4),portz),(x,A(service,10),portz),rr+.2) for x,rr in [(0,2),(8,1.4),(-8,1.1),(15,1.1)]])
    cart_joint('J21','Connector plate to ECU',3,8,[(real(x),A(service,7),real(35)) for x in [-14,14]],'y',real(2),['ECU Connector plate','ECU Service envelope'],True)
    service=fuel_service
    union=g.sub(g.union(g.move(hexprism(5.5,12,15),(service,0,0)),g.cyl((service,0,real(8)),(service,0,real(12)),2)),g.cyl((service,real(0),real(7)),(service,real(0),real(16)),1))
    part('FUEL Pump outlet union',union)
    drill('CASE Inlet bell',[g.cyl((service,0,real(8)),(service,0,real(13)),2)])
    drill('FUEL Pump envelope',[g.cyl((service,0,real(4)),(service,0,real(10)),1)])
    # P2: match the case entry, support passages, and receiver to the live feed axes.
    fr=ctx['feed_r'];fz=ctx['feed_z'];fe=ctx['feed_end'];fo=ctx['feed_or'];fi=ctx['feed_ir'];fg=ctx['feed_gap'];fp=ctx['feed_point'];phi=ctx['feed_phi']
    def radial_body(body):return g.rot(body,phi,axis=(0,0,1))
    entry=radial_body(g.cyl((S(cr,2),0,fz),(A(Rout,3),0,fz),2.5))
    extend('CASE Front barrel',entry)
    entryBore=g.cyl(fp(S(cr,3),fz),fp(A(Rout,4),fz),A(fo,fg))
    drill('CASE Front barrel',[entryBore])
    frontPassage=g.cyl(fp(fr,real(71)),fp(fr,real(79)),A(fo,fg))
    drill('BEARING Front retainer',[frontPassage])
    drill('SHAFT Bearing tunnel',[frontPassage])
    guides=[]
    for z in [110,145]:
        blank=radial_body(g.box((real(11),real(-2.5),real(z-2)),(A(fr,2),real(2.5),real(z+2))))
        bore=g.cyl(fp(fr,real(z-3)),fp(fr,real(z+3)),A(fo,fg))
        guides.append(g.sub(blank,bore))
    receiver=radial_body(g.box((real(11),real(-2.5),S(fe,3)),(A(fr,2),real(2.5),A(fe,4))))
    # Tube seats in a counterbore; axial feed then turns into the housing cavity.
    socket=g.cyl(fp(fr,S(fe,4)),fp(fr,fe),A(fo,real(.05)))
    axialBore=g.cyl(fp(fr,S(fe,.1)),fp(fr,A(fe,2)),fi)
    crossBore=g.cyl(fp(real(8),A(fe,2)),fp(fr,A(fe,2)),fi)
    extend('SHAFT Bearing tunnel',*guides,receiver)
    drill('SHAFT Bearing tunnel',[socket,axialBore,crossBore])
    from service_interfaces import detail_interfaces
    detail_interfaces(g,ctx,(extend,drill))
    g.calc('CHECK rear feed inner liner clearance','subtract',burnIR,A(fr,fo))
    for name,count in [('COMP Diffuser vanes',17),('FUEL Injector envelopes',12),('FUEL Manifold saddles',3),('FUEL Manifold clamp caps',3)]:next(p for p in g.parts if p['name']==name)['count']=count
    # Flat gasket envelopes at removable end flanges are separate inventory items.
    # The two end joints use metal-to-metal locating faces; seal selection is open.
    g.joints=joints;g.hardware=H
    return {'flange_radius':FR,'case_split':split,'gasket':gasket,'running_gap':gap,'joints':joints}
