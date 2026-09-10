"""Original I6 Astra geometry. All shapes are native nTop recipe blocks.

Host dimensions are millimeters; the recipe encoder writes SI. This generator
does not import the reference engine, its scripts, or any reference meshes.
"""
from pathlib import Path
import json, math, hashlib
from native_graph import Graph, real, literal

ROOT=Path(__file__).resolve().parents[1]
AL=(.64,.69,.74); DARK=(.16,.19,.23); STEEL=(.39,.45,.50)
BRIGHT=(.79,.83,.86); ORANGE=(.949,.42,.263); BLUE=(.086,.282,.616)
BRONZE=(.56,.36,.19); RUBBER=(.055,.06,.067)
P={'bore_mm':86.,'stroke_mm':92.,'pitch_mm':102.,'rod_mm':154.,
   'compression_height_mm':32.,'deck_mm':233.,'review_angle_deg':30.,
   'main_diameter_mm':56.,'rod_journal_diameter_mm':48.,'valve_angle_deg':12.}

def circle(x,y,z,r,n=40):
    return [(x,y+r*math.cos(2*math.pi*i/n),z+r*math.sin(2*math.pi*i/n)) for i in range(n)]

def build():
    g=Graph(); g.section='00 Design inputs'
    bore=g.param('Bore',86); stroke=g.param('Stroke',92); pitch=g.param('Cylinder pitch',102)
    rod=g.param('Connecting rod centers',154); ch=g.param('Compression height',32)
    angle=g.param('Crank angle',30,'angle'); deck=g.param('Deck height',233)
    g.param('Intake valve diameter',32);g.param('Exhaust valve diameter',28)
    g.param('Valve inclination',12,'angle');g.param('Gear module',2)
    g.param('Gear pressure angle',20,'angle');g.param('Timing belt pitch',5)
    g.param('Nominal cold diametral piston clearance',.08)
    g.section='01 Mechanism and checks'
    radius=g.var('Crank radius',g.math('multiply',stroke,real(.5,'')),'real')
    r_bore=g.var('Bore radius',g.math('multiply',bore,real(.5,'')),'real')
    disp=g.math('multiply',g.math('multiply',bore,bore),g.math('multiply',stroke,real(6*math.pi/4,'')))
    g.var('CHECK swept volume',disp,'real')
    stations=[]; phases=[0,240,120,120,240,0]; kinetics=[]
    for i,phase in enumerate(phases):
        x=g.var('Cylinder %d station'%(i+1),g.math('multiply',pitch,real(i-2.5,'')),'real'); stations.append(x)
        theta=g.var('Cylinder %d throw angle'%(i+1),g.math('add',angle,real(phase,'angle')),'real')
        yy=g.var('Cylinder %d crank Y'%(i+1),g.math('multiply',radius,g.math('sin',theta)),'real')
        zz=g.var('Cylinder %d crank Z'%(i+1),g.math('multiply',radius,g.math('cos',theta)),'real')
        pinz=g.var('CHECK cylinder %d pin Z'%(i+1),g.math('add',zz,g.math('sqrt',g.math('subtract',g.math('multiply',rod,rod),g.math('multiply',yy,yy)))),'real')
        beta=g.var('CHECK cylinder %d rod tilt'%(i+1),g.math('asin',g.math('divide',yy,rod)),'real')
        kinetics.append((yy,zz,pinz,beta))
    xs=[(i-2.5)*102 for i in range(6)]; mains=[-306+i*102 for i in range(7)]
    fast=[]
    def fasten(x,y,z,size,length,axis='z',system='fasteners'):
        fast.append(dict(x=x,y=y,z=z,size=size,length=length,axis=axis,system=system))

    # Cylinder block: crankcase shell, deck, six separate wet-liner pockets,
    # seven bulkheads, oil gallery and structural ribs.
    g.section='02 Cylinder block'
    shell=g.sub(g.box((-318,-94,-40),(318,94,233)),
                g.box((-301,-79,-44),(301,79,85)))
    pockets=[]; jacket=[]; blockholes=[]
    for x in xs:
        pockets.append(g.cyl((x,0,63),(x,0,237),46.8))
        jacket.append(g.sub(g.cyl((x,0,100),(x,0,224),52.5),g.cyl((x,0,98),(x,0,227),48.7)))
    ribs=[]
    for x in mains:
        ribs.extend([g.box((x-6,-104,-28),(x+6,-92,193)),g.box((x-6,92,-28),(x+6,104,193))])
        # Bulkheads retain both sides of the split main bearing tunnel.
        ribs.append(g.sub(g.box((x-10,-80,0),(x+10,80,91)),g.cyl((x-11,0,0),(x+11,0,0),30.05)))
        for y in [-66,66]:
            blockholes.append(g.cyl((x,y,179),(x,y,237),5.2))
    blockholes.append(g.cyl((-320,70,61),(320,70,61),4))
    # Side core-plug bores are physically cut through the outer wall.
    for x in xs:
        blockholes.extend([g.cyl((x,-110,153),(x,-74,153),16),g.cyl((x,74,153),(x,110,153),16)])
    block=g.sub(g.union(shell,*ribs),*pockets,*jacket,*blockholes)
    g.part('Cylinder block with water jackets',block,AL,'02 Cylinder block',count=1,cuttable=True)
    liners=g.array(g.tube((0,0,66),(0,0,233),46.75,r_bore),[6,1,1],[pitch,0,0])
    g.part('Six cylinder liners',g.move(liners,[-255,0,0]),STEEL,'02 Cylinder block',count=6,cuttable=True)
    plugs=[]
    for x in xs:
        for s in [-1,1]:
            plugs.append(g.sub(g.cyl((x,s*94,153),(x,s*97,153),16),g.cyl((x,s*96,153),(x,s*99,153),12.5)))
    g.part('Twelve recessed core plugs',g.union(*plugs),BRONZE,'02 Cylinder block',count=12)
    mounts=[]
    for x in [-193,193]:
        for y in [-1,1]:
            m=g.union(g.box((x-35,min(y*94,y*151),-10),(x+35,max(y*94,y*151),22)),
                      g.box((x-8,min(y*94,y*139),18),(x+8,max(y*94,y*139),70)))
            mounts.append(g.sub(m,*[g.cyl((x+dx,y*132,-13),(x+dx,y*132,25),5.3) for dx in [-21,21]]))
            for dx in [-21,21]:fasten(x+dx,y*132,24,10,32,system='engine mounts')
    g.part('Four engine mounting feet',g.union(*mounts),AL,'02 Cylinder block',count=4)

    # Split bedplate, seven caps, sump and windage tray.
    bed=g.sub(g.box((-319,-96,-67),(319,96,-40)),g.box((-292,-72,-69),(292,72,-38)))
    caps=[]
    for x in mains:
        caps.append(g.sub(g.box((x-12,-62,-47),(x+12,62,0)),g.cyl((x-13,0,0),(x+13,0,0),30.05)))
        for y in [-47,47]:fasten(x,y,-49,12,57,'-z','main caps')
    bed=g.union(bed,*caps)
    g.part('Bedplate and seven main caps',bed,DARK,'03 Lower case and lubrication',count=1,cuttable=True)
    sump=g.sub(g.union(g.box((-314,-92,-137),(314,92,-64)),g.box((-321,-98,-70),(321,98,-64))),
               g.box((-307,-85,-131),(307,85,-62)))
    sribs=[g.box((x-3,-94,-129),(x+3,94,-75)) for x in range(-290,300,29)]
    sump=g.union(sump,*sribs)
    sump=g.sub(sump,g.cyl((261,75,-119),(261,105,-119),7))
    g.part('Ribbed oil sump',sump,AL,'03 Lower case and lubrication',count=1,cuttable=True)
    for x in range(-300,301,60):
        for y in [-94,94]:fasten(x,y,-72,6,18,'-z','sump flange')
    for y in [-55,0,55]:
        for x in [-317,317]:fasten(x,y,-72,6,18,'-z','sump flange')
    tray=g.sub(g.box((-289,-72,-72),(289,72,-69)),*[g.box((x-19,-52,-74),(x+19,52,-67)) for x in xs])
    g.part('Windage tray and oil pickup',g.union(tray,g.pipe([(-240,-30,-71),(-160,-30,-107),(-60,-30,-117)],9,6.8),g.tube((-60,-30,-125),(-60,-30,-118),29,24)),BRIGHT,'03 Lower case and lubrication',count=2)
    g.part('Oil filter and cooler package',g.union(g.cyl((-230,-97,52),(-230,-160,52),30),g.cyl((-230,-98,52),(-230,-108,52),36),
          *[g.box((-260,-117-i*5,24),(-200,-115-i*5,80)) for i in range(6)]),DARK,'03 Lower case and lubrication',count=1)
    fasten(261,101,-119,14,18,'y','sump drain')

    # Crankshaft constructed in the phase-zero frame, then driven by Crank angle.
    crank=[]
    for x in mains:crank.append(g.cyl((x-12,0,0),(x+12,0,0),28))
    for x,phase in zip(xs,phases):
        a=math.radians(phase); y=46*math.sin(a);z=46*math.cos(a)
        crank.append(g.cyl((x-19,y,z),(x+19,y,z),24))
        for dx in [-29,29]:
            web=g.union(g.cyl((x+dx-11,0,0),(x+dx+11,0,0),37),
                        g.cyl((x+dx-11,0,46),(x+dx+11,0,46),31),g.box((x+dx-11,-30,-1),(x+dx+11,30,47)),
                        g.inter(g.cyl((x+dx-11,0,0),(x+dx+11,0,0),69),g.box((x+dx-13,-80,-80),(x+dx+13,80,-15))))
            crank.append(g.rot(web,-phase))
    crank.extend([g.cyl((-422,0,0),(-344,0,0),8.95),g.cyl((-346,0,0),(-312,0,0),16),g.cyl((312,0,0),(348,0,0),34),g.cyl((339,0,0),(350,0,0),58)])
    crank=g.sub(g.union(*crank),g.cyl((-423,0,0),(351,0,0),5))
    # Positive crank angles use +Y crank throw motion, hence negative X rotation.
    neg_angle=g.math('multiply',angle,real(-1,''))
    g.part('Crankshaft with twelve counterweights',g.rot(crank,neg_angle),STEEL,'04 Crankshaft and bearings',count=1)
    bearings=[g.tube((x-11,0,0),(x+11,0,0),30,28.1) for x in mains]
    g.part('Seven main bearing shells',g.union(*bearings),BRONZE,'04 Crankshaft and bearings',count=7)
    fly=g.sub(g.cyl((350,0,0),(376,0,0),137),g.cyl((349,0,0),(365,0,0),104),g.cyl((349,0,0),(378,0,0),22),
              *[g.cyl((349,42*math.sin(k*math.pi/4),42*math.cos(k*math.pi/4)),(378,42*math.sin(k*math.pi/4),42*math.cos(k*math.pi/4)),5.3) for k in range(8)])
    g.part('Flywheel with machined recess',fly,BRIGHT,'04 Crankshaft and bearings',count=1)
    ring=g.gear(144,2,12,137)
    g.part('144-tooth involute starter ring',g.move(ring,(360,0,0)),STEEL,'04 Crankshaft and bearings',count=1,gear_teeth=144)
    for k in range(8):fasten(377,42*math.sin(k*math.pi/4),42*math.cos(k*math.pi/4),10,27,'x','flywheel')

    # One detailed piston and one rod template, then six kinematic placements.
    g.section='05 Pistons and connecting rods'
    piston=g.sub(g.cyl((0,0,-26),(0,0,32),42.96),g.cyl((0,0,-28),(0,0,24),36.5),
                  g.sphere((0,0,174),145),g.cyl((-46,0,0),(46,0,0),11.1),
                  g.box((-48,-48,-29),(-30,48,5)),g.box((30,-48,-29),(48,48,5)))
    bosses=[g.sub(g.cyl((s*21,0,0),(s*40,0,0),18),g.cyl((s*19,0,0),(s*43,0,0),11.1)) for s in [-1,1]]
    piston=g.union(piston,*bosses)
    for z,w in [(25,1.7),(20.3,1.7),(14.6,3.0)]:
        piston=g.sub(piston,g.sub(g.cyl((0,0,z),(0,0,z+w),44),g.cyl((0,0,z-1),(0,0,z+w+1),40.5)))
    for xx in [-19,19]:
        for yy in [-19,19]:piston=g.sub(piston,g.cyl((xx,yy,30.5),(xx,yy,36),11))
    ptemp=g.var('Piston template',piston,'implicit')
    rings=g.var('Ring pack template',g.union(*[g.sub(g.tube((0,0,z+.15),(0,0,z+w-.15),43,40.7),g.box((-1,-45,z-1),(1,-38,z+w+1))) for z,w in [(25,1.7),(20.3,1.7),(14.6,3.)]]),'implicit')
    pin=g.var('Hollow wrist pin template',g.tube((-38,0,0),(38,0,0),11,7),'implicit')
    # Rod local bottom center is 0, top center is 154.
    rod_body=g.union(g.tube((-12,0,0),(12,0,0),33,24.15),g.tube((-10,0,154),(10,0,154),17,11.15),
                     g.box((-5,-10,23),(5,10,145)),g.box((-11,-13,27),(-6,13,141)),g.box((6,-13,27),(11,13,141)))
    rod_body=g.sub(rod_body,g.box((-14,-36,-2),(14,36,-1.4)),g.cyl((-14,0,154),(14,0,154),11.15))
    rtemp=g.var('I-section split rod template',rod_body,'implicit')
    placedp=[];placedr=[];placedrings=[];placedpins=[];rodbolts=[]
    for i,(x,kin) in enumerate(zip(stations,kinetics)):
        yy,zz,pinz,beta=kin
        placedp.append(g.move(ptemp,[x,0,pinz])); placedrings.append(g.move(rings,[x,0,pinz]));placedpins.append(g.move(pin,[x,0,pinz]))
        placedr.append(g.move(g.rot(rtemp,beta),[x,yy,zz]))
        for sy in [-1,1]:
            socket=g.prism([(3.5*math.cos(k*math.pi/3),sy*28+3.5*math.sin(k*math.pi/3),-21) for k in range(6)],5,(0,0,1))
            bolt=g.sub(g.union(g.cyl((0,sy*28,-14),(0,sy*28,21),4),g.cyl((0,sy*28,-20),(0,sy*28,-13),7)),socket)
            rodbolts.append(g.move(g.rot(bolt,beta),[x,yy,zz]))
    g.part('Six hollow pistons with reliefs',g.union(*placedp),BRIGHT,'05 Pistons and connecting rods',count=6)
    g.part('Eighteen split piston rings',g.union(*placedrings),DARK,'05 Pistons and connecting rods',count=18)
    g.part('Six hollow wrist pins',g.union(*placedpins),STEEL,'05 Pistons and connecting rods',count=6)
    g.part('Six split I-section connecting rods',g.union(*placedr),STEEL,'05 Pistons and connecting rods',count=6)
    g.part('Twelve connecting rod bolts',g.union(*rodbolts),DARK,'05 Pistons and connecting rods',count=12,fastener_count=12)

    # Cylinder head, open cam gallery, inlet and exhaust port passages.
    head=g.sub(g.box((-318,-98,233.8),(318,98,336)),g.box((-304,-78,306),(304,78,340)))
    cam_y=22+100*math.sin(math.radians(12));cam_z=240+100*math.cos(math.radians(12))
    firing=[0,480,240,600,120,360]
    valve_motion={}
    htools=[];valves=[];seats=[];guides=[];buckets=[];springplacements=[];plugs=[]
    for ci,x in enumerate(xs):
        htools.append(g.sphere((x,0,162),84))
        htools.append(g.cyl((x,0,242),(x,0,368),9))
        for side in [-1,1]:
            for dx in [-18,18]:
                a=12 if side==-1 else -12
                seat=(x+dx,side*22,240)
                # The open timing belt makes both cams rotate with the crank.
                # Mirroring phi preserves follower lift while fixing direction.
                phi=180-(P['review_angle_deg']-firing[ci]-(470 if side==-1 else 250))/2
                lift=max(0.,-17*math.cos(math.radians(phi))-9)
                valve_motion[(ci,side)]=(phi,lift)
                htools.append(g.move(g.rot(g.cyl((0,0,-3),(0,0,87),5),a),seat))
                htools.append(g.move(g.rot(g.cyl((0,0,-5),(0,0,35),14 if side==-1 else 12),a),seat))
                # Forked ports join at one exterior opening per cylinder and side.
                htools.append(g.path([(x+dx,side*25,261),(x+dx,side*51,274),(x,side*103,280)],14 if side==-1 else 12))
                headrad=16 if side==-1 else 14
                v=g.union(g.cone((0,0,0),(0,0,3),headrad,headrad-2),g.cyl((0,0,3),(0,0,79),3.5),
                          g.cyl((0,0,72),(0,0,76),12))
                valves.append(g.move(g.rot(g.move(v,(0,0,-lift)),a),seat))
                seats.append(g.move(g.rot(g.tube((0,0,-.3),(0,0,3.3),headrad+1,headrad-2),a),seat))
                guides.append(g.move(g.rot(g.tube((0,0,33),(0,0,61),6,3.65),a),seat))
                buckets.append(g.move(g.rot(g.move(g.sub(g.cyl((0,0,75),(0,0,82),15),g.cyl((0,0,74),(0,0,80),12)),(0,0,-lift)),a),seat))
                springplacements.append((seat,a,lift))
        # Six plug bodies and ceramic insulators remain visible through the cover.
        plugs.extend([g.cyl((x,0,248),(x,0,269),7),g.cyl((x,0,269),(x,0,302),5.5)])
    for x in mains:
        for y in [-66,66]:
            htools.append(g.cyl((x,y,231),(x,y,340),5.5));fasten(x,y,307,10,115,system='head bolts')
        for y in [-cam_y,cam_y]:
            tower=g.sub(g.box((x-9,y-24,298),(x+9,y+24,350)),g.cyl((x-11,y,cam_z),(x+11,y,cam_z),12.7))
            head=g.union(head,tower)
    g.part('Cylinder head with chambers and ports',g.sub(head,*htools),AL,'06 Cylinder head',count=1,cuttable=True)
    gasket=g.sub(g.box((-317,-96,233),(317,96,233.8)),*[g.cyl((x,0,232),(x,0,235),43.5) for x in xs],
                 *[g.cyl((x,y,232),(x,y,235),5.6) for x in mains for y in [-66,66]])
    g.part('Head gasket with six fire rings',gasket,DARK,'06 Cylinder head',count=1,cuttable=True)
    g.part('Twenty-four valve seats',g.union(*seats),BRONZE,'07 Valvetrain',count=24)
    g.part('Twenty-four valves and retainers',g.union(*valves),BRIGHT,'07 Valvetrain',count=24)
    g.part('Twenty-four valve guides',g.union(*guides),BRONZE,'07 Valvetrain',count=24)
    g.part('Twenty-four bucket tappets',g.union(*buckets),STEEL,'07 Valvetrain',count=24)
    g.part('Six spark plugs',g.union(*plugs),BRIGHT,'08 Covers and ignition',count=6)
    # Analytic helix distance field, used once and rigidly repeated.
    g.section='07 Valvetrain'
    fields=[]
    for ax in [(1,0,0),(0,1,0),(0,0,1)]:
        plane={'func':'plane_from_normal<point,vector>[1.1.0]','id':g.uid(),'inputs':[g.pt((0,0,0)),g.vec(ax,False)],'name':'Coordinate plane','type':'plane'}
        pref=g.var('Spring coordinate plane '+str(len(fields)),plane,'plane')
        # Plane's body scalar field: variable holder with explicit native input.
        fields.append(g.var('Spring coordinate '+str(len(fields)),g.prop(pref,'body'),'real_field'))
    fx,fy,fz=fields
    fm=lambda op,*a:g.math(op,*a,field=True)
    radial=g.var('Spring radial distance',fm('subtract',fm('sqrt',fm('add',fm('multiply',fx,fx),fm('multiply',fy,fy))),real(10)),'real_field')
    az=g.var('Spring azimuth',fm('divide',fm('atan2',fy,fx),real(360,'angle')),'real_field')
    # Every spring keeps six turns as its installed length follows the retainer.
    spring_templates={};springs=[]
    for seat,a,lift in springplacements:
        key=round(lift,7)
        if key not in spring_templates:
            length=36-lift;active=length-3;pp=active/6;tag='Spring lift %.7f'%key
            w=g.var(tag+' axial distance',fm('subtract',fm('mod',fm('add',fm('subtract',fz,fm('multiply',az,real(pp))),real(pp/2)),real(pp)),real(pp/2)),'real_field')
            field=fm('subtract',fm('sqrt',fm('add',fm('multiply',radial,radial),fm('multiply',w,w))),real(1.5))
            helixvar=g.var(tag+' field',field,'implicit')
            helix=g.move(g.inter(helixvar,g.cyl((0,0,0),(0,0,active),12)),(0,0,1.5))
            closed=g.union(helix,g.torus((0,0,1.5),(0,0,1),10,1.5),g.torus((0,0,length-1.5),(0,0,1),10,1.5))
            spring_templates[key]=g.var(tag+' coil',closed,'implicit')
        springs.append(g.move(g.rot(g.move(spring_templates[key],(0,0,36)),a),seat))
    g.part('Twenty-four helical valve springs',g.union(*springs),STEEL,'07 Valvetrain',count=24)

    # Two camshafts with sampled convex-support lobes. Valve positions represent
    # a static packaging pose; their contact law is not claimed as validated motion.
    cams=[]
    for side in [-1,1]:
        bits=[g.cyl((-350,side*cam_y,cam_z),(325,side*cam_y,cam_z),10.5)]
        for x in mains:bits.append(g.cyl((x-11,side*cam_y,cam_z),(x+11,side*cam_y,cam_z),12.5))
        for i,x in enumerate(xs):
            for dx in [-18,18]:
                # convex hull of offset circles creates smooth base/nose tangency.
                from shapely.geometry import MultiPoint
                coords=[(18*math.cos(t),18*math.sin(t)) for t in [2*math.pi*k/64 for k in range(64)]]
                coords += [(9*math.cos(t),17+9*math.sin(t)) for t in [2*math.pi*k/48 for k in range(48)]]
                hull=list(MultiPoint(coords).convex_hull.exterior.coords)[:-1]
                lobe=g.prism([(x+dx-6,y,z) for y,z in hull],12)
                phi,lift=valve_motion[(i,side)]
                lobe=g.rot(lobe,phi+(12 if side==-1 else -12),center=(x+dx,0,0))
                bits.append(g.move(lobe,(0,side*cam_y,cam_z)))
        cams.append(g.union(*bits))
    g.part('Two camshafts with twenty-four lobes',g.union(*cams),STEEL,'07 Valvetrain',count=2,cam_lobes=24)
    camcaps=[]
    for x in mains:
        for y in [-cam_y,cam_y]:
            camcaps.append(g.sub(g.box((x-10,y-23,cam_z-1),(x+10,y+23,357)),g.cyl((x-12,y,cam_z),(x+12,y,cam_z),12.65)))
            for yy in [y-18,y+18]:fasten(x,yy,359,6,34,system='cam caps')
    g.part('Fourteen cam bearing caps',g.union(*camcaps),AL,'07 Valvetrain',count=14)
    cover=g.union(g.box((-320,-101,354),(320,101,367)),g.cyl((-316,-44,366),(316,-44,366),32),g.cyl((-316,44,366),(316,44,366),32))
    cover=g.sub(cover,g.box((-311,-91,349),(311,91,365)),g.cyl((-312,-44,366),(312,-44,366),28),g.cyl((-312,44,366),(312,44,366),28),
                *[g.cyl((x,0,348),(x,0,404),16) for x in xs])
    g.part('Twin cam cover',cover,BLUE,'08 Covers and ignition',count=1,cuttable=True)
    coils=[]
    for x in xs:
        coils.extend([g.cyl((x,0,302),(x,0,379),11),g.box((x-16,-22,375),(x+16,22,389)),g.box((x+12,-10,380),(x+30,10,388))])
        fasten(x-24,0,374,6,16,system='ignition coils')
    g.part('Six coil-on-plug ignition units',g.union(*coils),DARK,'08 Covers and ignition',count=6)
    covertrim=[g.box((-277,-69,392),(-120,-62,396)),g.box((-277,62,392),(-120,69,396))]
    g.part('Cam cover identification ribs',g.union(*covertrim),ORANGE,'08 Covers and ignition',count=2)
    for x in [-305,-204,-102,0,102,204,305]:
        for y in [-94,94]:fasten(x,y,369,6,20,system='cam cover')

    # Six independent intake runners feed one plenum. All runners are hollow.
    runners=[];exhaust=[];flanges=[];fuel=[];intake_bolts=[]
    for i,x in enumerate(xs):
        points=[(x,-98,280),(x,-132,286),(x,-163,311),(x,-193,334),(x,-225,338)]
        runners.append(g.pipe(points,21,17.5))
        flange=g.sub(g.box((x-34,-107,249),(x+34,-98,310)),g.cyl((x,-110,280),(x,-95,280),18))
        flanges.append(flange)
        for dx in [-27,27]:fasten(x+dx,-109,280,8,28,'-y','intake flange')
        # Separate 6-into-2 collectors keep bank routing readable.
        collector_x=-156 if i<3 else 156
        epoints=[(x,98,280),(x,131,280),(x,176,270),
                 (x*.62+collector_x*.38,207,211),(collector_x,223,180),(collector_x,223,150)]
        g.section='10 Exhaust system'
        exhaust.append(g.spline_route('Exhaust primary %d'%(i+1),epoints,19,16))
        flange=g.sub(g.box((x-32,98,251),(x+32,107,309)),g.cyl((x,95,280),(x,110,280),16))
        flanges.append(flange)
        for dx in [-25,25]:fasten(x+dx,110,280,8,28,'y','exhaust flange')
        fuel.append(g.cyl((x,-112,301),(x,-150,322),5))
    g.part('Six hollow intake runners',g.union(*runners),AL,'09 Intake and fuel system',count=6)
    plenum=g.sub(g.capsule((-266,-242,338),(270,-242,338),47),g.capsule((-262,-242,338),(266,-242,338),42),
                 *[g.cyl((x,-218,338),(x,-186,338),17.5) for x in xs],g.cyl((-321,-242,338),(-266,-242,338),31))
    g.part('Hollow intake plenum',plenum,DARK,'09 Intake and fuel system',count=1,cuttable=True)
    throttle=g.union(g.tube((-347,-242,338),(-308,-242,338),38,31),g.box((-331,-291,327),(-307,-274,350)))
    g.part('Throttle housing and butterfly',g.union(throttle,g.cyl((-329,-268,338),(-329,-216,338),3),g.cyl((-330,-242,338),(-328,-242,338),30.5)),AL,'09 Intake and fuel system',count=1)
    for t in [45,135,225,315]:fasten(-350,-242+33*math.sin(math.radians(t)),338+33*math.cos(math.radians(t)),6,18,'-x','throttle')
    fuel.extend([g.cyl((-284,-149,325),(284,-149,325),7.5)])
    g.part('Fuel rail and six injectors',g.union(*fuel),BRIGHT,'09 Intake and fuel system',count=7)
    g.part('Intake and exhaust mounting flanges',g.union(*flanges),STEEL,'10 Exhaust system',count=12)
    g.part('Six hollow exhaust primaries',g.union(*exhaust),BRONZE,'10 Exhaust system',count=6)
    collectors=[]
    for x in [-156,156]:
        collectors.append(g.spline_route('Exhaust collector '+str(x),[(x,223,170),(x,223,151),(x,237,132),(x,237,99),(x,237,74)],33,29))
        collectors.append(g.sub(g.box((x-46,194,76),(x+46,280,85)),g.cyl((x,237,74),(x,237,88),29)))
        for dx in [-35,35]:fasten(x+dx,237,87,10,25,system='exhaust collector')
    g.part('Two exhaust collectors',g.union(*collectors),BRONZE,'10 Exhaust system',count=2)

    # Real involute auxiliary gear pair: 24/36 teeth, m=2, 20 degree pressure
    # angle. Centers have 60 mm spacing. 5 degree phase centers a gap at contact.
    gears=g.union(g.move(g.gear(24,2,14,16.05),(-340,0,0)),
                  g.move(g.rot(g.gear(36,2,14,8),5),(-340,60,0)))
    g.part('24-36T involute oil pump drive gears',gears,BRIGHT,'11 Timing and accessory drive',count=2,gear_teeth=60)
    pump=g.union(g.cyl((-326,60,0),(-300,60,0),43),g.box((-325,23,-38),(-312,100,40)))
    pump=g.sub(pump,g.cyl((-328,60,0),(-315,60,0),8))
    g.part('Oil pump body and drive shaft',g.union(pump,g.cyl((-349,60,0),(-310,60,0),7.9)),AL,'03 Lower case and lubrication',count=1)
    for t in [45,135,225,315]:fasten(-329,60+35*math.sin(math.radians(t)),35*math.cos(math.radians(t)),6,23,'-x','oil pump')

    # Timing pulleys share the actual cam axes at y +/-44,z338.
    # The 5 mm pitch gives clearance between the two 48-tooth pulleys.
    # An explicit phase aligns the tooth center at the first belt wrap sample.
    pitchbelt=5.; pulley_centers=[(0.,0.,24),(-cam_y,cam_z,48),(cam_y,cam_z,48)]
    from shapely.geometry import MultiPoint,Polygon
    from shapely.ops import nearest_points
    def disc_hull(centers,x,width,offset):
        # Exact circular arcs plus a small tangent polygon. This has the same
        # convex support as the circle hull, without hundreds of profile edges.
        cs=[(y,z,r+offset) for y,z,r in centers];tangent_points=[]
        for i,(y,z,r) in enumerate(cs):
            for j,(Y,Z,R) in enumerate(cs):
                if j<=i:continue
                dy,dz=Y-y,Z-z;dist=math.hypot(dy,dz)
                delta=(r-R)/dist
                if abs(delta)>=1:continue
                ey,ez=dy/dist,dz/dist;h=math.sqrt(1-delta*delta)
                for sign in [-1,1]:
                    ny=delta*ey-sign*h*ez;nz=delta*ez+sign*h*ey
                    support=y*ny+z*nz+r
                    if all(yy*ny+zz*nz+rr<=support+1e-7 for yy,zz,rr in cs):
                        tangent_points.extend([(y+r*ny,z+r*nz),(Y+R*ny,Z+R*nz)])
        poly=list(MultiPoint(tangent_points).convex_hull.exterior.coords)[:-1]
        return g.union(*[g.cyl((x,y,z),(x+width,y,z),r) for y,z,r in cs],g.prism([(x,y,z) for y,z in poly],width))
    def timing_path(extra_y):
        circles=[]
        for y,z,n in pulley_centers+[(extra_y,155.,24)]:
            rp=n*pitchbelt/(2*math.pi)
            circles.extend([(y+rp*math.cos(2*math.pi*k/360),z+rp*math.sin(2*math.pi*k/360)) for k in range(360)])
        return MultiPoint(circles).convex_hull.exterior
    target_length=math.ceil(timing_path(112).length/5)*5
    lo,hi=112.,155.
    for _ in range(50):
        mid=(lo+hi)/2
        if timing_path(mid).length<target_length:lo=mid
        else:hi=mid
    tensioner_y=(lo+hi)/2;path=timing_path(tensioner_y)
    pulley_centers.append((tensioner_y,155.,24))
    belt_length=path.length
    # A solved idler station closes the loop at an integer number of 5 mm pitches.
    backing_outer=Polygon(path).buffer(3.5,quad_segs=24)
    backing_inner=Polygon(path).buffer(-.85,quad_segs=24)
    def beltpr(poly,x,width):return g.prism([(x,y,z) for y,z in list(poly.exterior.coords)[:-1]],width)
    tc=[(y,z,n*pitchbelt/(2*math.pi)) for y,z,n in pulley_centers]
    belt=g.sub(disc_hull(tc,-377,26,3.5),disc_hull(tc,-378,28,-.85))
    tooth_count=round(belt_length/pitchbelt); belt_teeth=[]
    belt_stations=[]
    for k in range(tooth_count):
        s=k*belt_length/tooth_count; p=path.interpolate(s); pn=path.interpolate((s+.1)%belt_length)
        tangent=(pn.x-p.x,pn.y-p.y); L=math.hypot(*tangent)
        # exterior hull is clockwise; interior lies to the right.
        inward=(tangent[1]/L,-tangent[0]/L)
        yy=p.x+inward[0]*.9; zz=p.y+inward[1]*.9
        belt_teeth.append(g.cyl((-377,yy,zz),(-351,yy,zz),1.1));belt_stations.append((p.x,p.y))
    g.part('Toothed timing belt with %d teeth'%tooth_count,g.union(belt,*belt_teeth),RUBBER,'11 Timing and accessory drive',count=1,belt_teeth=tooth_count)
    pulleys=[];hubbridges=[]
    for y,z,n in pulley_centers:
        rp=n*pitchbelt/(2*math.pi)
        holes=g.polar(g.cyl((-378,0,rp-.4),(-350,0,rp-.4),1.9),n)
        wheel=g.sub(g.cyl((-376,0,0),(-352,0,0),rp-.85),holes,g.cyl((-380,0,0),(-349,0,0),9))
        wheel=g.union(wheel,g.tube((-378,0,0),(-376,0,0),rp+3,9),g.tube((-352,0,0),(-350,0,0),rp+3,9))
        if n==48:
            wheel=g.sub(wheel,*[g.cyl((-380,rp*.57*math.sin(k*math.pi/3),rp*.57*math.cos(k*math.pi/3)),(-348,rp*.57*math.sin(k*math.pi/3),rp*.57*math.cos(k*math.pi/3)),7) for k in range(6)])
        contact=min(belt_stations,key=lambda p:abs(math.hypot(p[0]-y,p[1]-z)-rp))
        phase=math.degrees(math.atan2(-(contact[0]-y),contact[1]-z))
        pulleys.append(g.move(g.rot(wheel,phase),(0,y,z)))
        fasten(-382,y,z,12,35,'-x','timing pulleys')
        if n==48:
            # Both extensions are coaxial with the cam journals.
            hubbridges.append(g.cyl((-352,y,z),(-321,y,z),11))
    g.part('24-48-48T pulleys and 24T idler',g.union(*pulleys),STEEL,'11 Timing and accessory drive',count=4,timing_teeth=144)
    g.part('Timing pulley shaft extensions',g.union(*hubbridges),BRIGHT,'11 Timing and accessory drive',count=2)
    g.part('Timing belt idler bracket',g.union(g.box((-347,80,124),(-333,tensioner_y+16,185)),g.cyl((-354,tensioner_y,155),(-330,tensioner_y,155),11)),AL,'11 Timing and accessory drive',count=1)
    for z in [134,174]:fasten(-350,88,z,8,28,'-x','idler bracket')

    # Accessory six-rib belt: crank, alternator, water pump and tensioner.
    accessory=[(0.,0.,67.),(-137.,107.,39.),(95.,164.,45.)]
    cv=[]
    for y,z,r in accessory:cv.extend([(y+r*math.cos(2*math.pi*k/240),z+r*math.sin(2*math.pi*k/240)) for k in range(240)])
    apath=MultiPoint(cv).convex_hull
    abelt=g.sub(disc_hull(accessory,-414,21,3),disc_hull(accessory,-415,23,-.2))
    abelt=g.union(abelt,*[g.sub(disc_hull(accessory,-412+i*3.5,1.7,.1),disc_hull(accessory,-413+i*3.5,3.7,-1.0)) for i in range(6)])
    g.part('Continuous six-rib accessory belt',abelt,RUBBER,'11 Timing and accessory drive',count=1)
    aps=[]
    for y,z,r in accessory:
        pp=g.cyl((-414,0,0),(-391,0,0),r)
        grooves=[g.torus((-411+i*3.5,0,0),(1,0,0),r,1.25) for i in range(6)]
        pp=g.sub(pp,*grooves,g.cyl((-416,0,0),(-389,0,0),9))
        pp=g.union(pp,g.cyl((-393,0,0),(-387,0,0),r+2))
        if z:
            pp=g.sub(pp,*[g.cyl((-416,r*.55*math.sin(k*math.pi/3),r*.55*math.cos(k*math.pi/3)),(-385,r*.55*math.sin(k*math.pi/3),r*.55*math.cos(k*math.pi/3)),r*.13) for k in range(6)])
        aps.append(g.move(pp,(0,y,z)))
        fasten(-418,y,z,12,36,'-x','accessory pulleys')
    g.part('Three grooved accessory pulleys',g.union(*aps),DARK,'11 Timing and accessory drive',count=3)
    alt=g.union(g.cyl((-391,-137,107),(-294,-137,107),44),g.cyl((-390,-137,107),(-381,-137,107),48),g.cyl((-307,-137,107),(-296,-137,107),48))
    alt=g.sub(alt,*[g.move(g.rot(g.box((-385,-5,29),(-302,5,51)),k*30),[0,-137,107]) for k in range(12)])
    g.part('Vented alternator housing',alt,AL,'12 Ancillaries',count=1)
    g.part('Alternator stator and rear cap',g.union(g.cyl((-376,-137,107),(-309,-137,107),35),g.cyl((-295,-137,107),(-281,-137,107),38)),BRONZE,'12 Ancillaries',count=1)
    for y,z in [(-165,78),(-109,135)]:fasten(-395,y,z,8,95,'-x','alternator tie rods')
    water=g.union(g.cyl((-390,95,164),(-325,95,164),36),g.pipe([(-338,95,164),(-320,130,164),(-260,141,171)],17,13))
    g.part('Water pump and outlet',water,AL,'12 Ancillaries',count=1)
    cradle=g.union(g.box((329,95,166),(394,112,186)),g.box((380,99,-38),(394,113,180)),
                   g.box((377.5,104,-39),(381,200,39)))
    cradle=g.sub(cradle,g.cyl((375,162,0),(383,162,0),28))
    starter=g.union(g.cyl((377,162,0),(466,162,0),31),g.cyl((390,162,43),(441,162,43),16),
                    g.cyl((369,162,0),(384,162,0),5.9),cradle)
    g.part('Starter motor and solenoid',starter,DARK,'12 Ancillaries',count=1)
    g.part('Starter pinion with eighteen involute teeth',g.move(g.gear(18,2,12,6),(360,162,0)),STEEL,'12 Ancillaries',count=1,gear_teeth=18)
    for y,z in [(136,0),(188,0)]:fasten(375.5,y,z,10,30,'-x','starter mounts')
    # Rear seal and bellhousing flange retain an unobstructed flywheel cavity.
    rear=g.sub(g.box((319,-103,-68),(333,103,220)),g.cyl((318,0,0),(334,0,0),54))
    g.part('Rear seal carrier',rear,AL,'12 Ancillaries',count=1)
    for y,z in [(-84,-45),(84,-45),(-84,55),(84,55),(-84,175),(84,175)]:fasten(336,y,z,8,24,'x','rear seal carrier')

    # Smooth service routes. Cubic centerlines remain editable native spline
    # variables. Solid-wire radii and hollow-tube wall sizes are explicit offsets.
    g.section='14 Electrical routing'
    loom=g.spline_route('Ignition harness trunk',[(-293,-76,409),(-160,-76,409),(30,-76,409),(238,-76,409),(287,-63,406),(310,-38,390)],4.2,trim=False)
    branches=[];connectors=[];supports=[];clamps=[]
    for i,x in enumerate(xs):
        branches.append(g.spline_route('Coil branch %d'%(i+1),[(x+27,-10,384),(x+37,-15,391),(x+37,-40,409),(x+27,-62,409),(x+20,-76,409)],2.6,trim=False))
        connectors.append(g.union(g.box((x+23,-15,379),(x+36,-5,389)),g.box((x+27,-16,383),(x+32,-14,387))))
    for x in [-225,-75,75,225]:
        clamps.append(g.torus((x,-76,409),(1,0,0),5.3,1.15))
        supports.append(g.union(g.box((x-5,-83,394),(x+5,-79,409)),g.box((x-7,-87,392),(x+7,-68,395))))
        fasten(x,-84,396,6,15,system='harness supports')
    power=g.spline_route('Alternator charge cable',[(-282,-137,107),(-266,-163,110),(-240,-181,172),(-85,-180,203),(171,-170,205),(312,-131,197),(343,-104,176)],4.3,trim=False)
    sensor=g.spline_route('Crank sensor cable',[(-315,-89,13),(-330,-121,21),(-329,-170,100),(-237,-186,180),(-108,-187,204)],2.2,trim=False)
    ground=g.spline_route('Head ground strap',[(289,-81,338),(313,-112,336),(327,-132,292),(318,-126,242),(303,-107,229)],3.3,trim=False)
    g.part('Ignition harness and six coil branches',g.union(loom,*branches),DARK,'14 Electrical routing',count=7)
    g.part('Charge cable ground strap and sensor lead',g.union(power,sensor,ground),(.18,.22,.26),'14 Electrical routing',count=3)
    g.part('Six harness connectors and four supports',g.union(*connectors,*supports),DARK,'14 Electrical routing',count=10)
    g.part('Four harness retaining clips',g.union(*clamps),BRIGHT,'14 Electrical routing',count=4)

    g.section='15 Fluid routing'
    hoses=[];lines=[];fittings=[];hosebands=[]
    coolant_routes=[('Upper coolant bypass',[(-260,141,171),(-295,162,190),(-338,135,244),(-342,5,276),(-335,-114,287),(-309,-123,288),(-293,-105,288)],14,10.5),
                    ('Lower coolant return',[(-326,95,164),(-342,68,151),(-343,-40,125),(-311,-118,94),(-264,-130,92),(-220,-106,99)],12,9)]
    fuel_routes=[('Fuel supply',[(284,-149,325),(308,-149,325),(325,-171,305),(330,-178,257),(332,-151,221),(318,-125,210)],5,3.5),
                 ('Fuel return',[(-284,-149,325),(-301,-153,325),(-308,-187,291),(-289,-197,242),(-245,-179,212),(-227,-158,199)],4,2.6)]
    oil_routes=[('Oil cooler feed',[(-230,-146,76),(-230,-169,85),(-191,-179,111),(-105,-169,121),(-68,-113,113)],5.5,3.5),
                ('Oil cooler return',[(-230,-146,27),(-205,-174,15),(-137,-174,25),(-96,-160,54),(-82,-111,61)],5.5,3.5)]
    for name,pts,ro,ri in coolant_routes+fuel_routes+oil_routes:
        item=g.spline_route(name,pts,ro,ri)
        (hoses if name.startswith(('Upper','Lower')) else lines).append(item)
        for p,q in [(pts[0],pts[1]),(pts[-1],pts[-2])]:
            v=[q[i]-p[i] for i in range(3)];L=math.sqrt(sum(t*t for t in v));v=[t/L for t in v]
            end=[p[i]+12*v[i] for i in range(3)]
            fittings.append(g.tube(p,end,ro+2.2,ri))
            c=[p[i]+7*v[i] for i in range(3)]
            hosebands.append(g.torus(c,v,ro+2.4,.9))
    g.part('Two smooth coolant hoses',g.union(*hoses),(.12,.18,.21),'15 Fluid routing',count=2)
    g.part('Fuel and oil hard lines',g.union(*lines),BRIGHT,'15 Fluid routing',count=4)
    g.part('Twelve fluid-line end fittings',g.union(*fittings),(.45,.5,.57),'15 Fluid routing',count=12)
    g.part('Twelve hose and line retaining bands',g.union(*hosebands),BRIGHT,'15 Fluid routing',count=12)

    # All fixed fasteners are individually placed native solids. Simplified
    # cosmetic thread rings are intentionally omitted; shank sizes are explicit.
    # A hex profile gives six actual flats, with a conical crown chamfer.
    g.section='13 Assembly fasteners'
    bysize={}; fastparts={}
    for f in fast:
        key=(f['size'],f['length'])
        if key not in bysize:
            d,L=key; across={6:10,8:13,10:17,12:19,14:22}[d]; rr=across/math.sqrt(3); hh=.65*d
            hx=[(rr*math.cos(k*math.pi/3),rr*math.sin(k*math.pi/3),0) for k in range(6)]
            head=g.prism(hx,hh,(0,0,1))
            head=g.inter(head,g.cone((0,0,0),(0,0,hh+.1),rr+hh*.6,rr-.65))
            bolt=g.union(head,g.cyl((0,0,-L),(0,0,0),d/2),g.tube((0,0,-1.5),(0,0,0),across*.68,d*.51))
            bysize[key]=g.var('M%d x %g bolt template'%(d,L),bolt,'implicit')
        b=bysize[key]; axis=f['axis']
        if axis=='-z':b=g.rot(b,180,axis=(1,0,0))
        elif axis=='x':b=g.rot(b,90,axis=(0,1,0))
        elif axis=='-x':b=g.rot(b,-90,axis=(0,1,0))
        elif axis=='y':b=g.rot(b,-90)
        elif axis=='-y':b=g.rot(b,90)
        fastparts.setdefault(f['system'],[]).append(g.move(b,(f['x'],f['y'],f['z'])))
    for name,parts in fastparts.items():
        g.part('Fasteners - '+name,g.union(*parts),DARK,'13 Assembly fasteners',count=len(parts),fastener_count=len(parts))
    # Store the exact coordinate contract for independent audits.
    spec={**P,'phases_deg':phases,'cylinder_stations_mm':xs,'main_stations_mm':mains,
          'timing_pitch_length_mm':belt_length,'timing_belt_teeth':tooth_count,
          'timing_actual_pitch_mm':belt_length/tooth_count,'fasteners':fast,
          'timing_tensioner_y_mm':tensioner_y,'cam_y_mm':cam_y,'cam_z_mm':cam_z,
          'valve_pose':[{'cylinder':ci+1,'side':side,'cam_angle_deg':v[0],'lift_mm':v[1]} for (ci,side),v in valve_motion.items()],
          'static_valvetrain':True,'design_units':'mm, degrees','spline_routes':g.routes}
    return g,spec

def main():
    g,spec=build()
    g.layout['sections'].sort()
    (ROOT/'output/evidence'/'engine_recipe.json').write_text(json.dumps(g.recipe(),indent=1))
    (ROOT/'output/evidence'/'layout.json').write_text(json.dumps(g.layout,indent=2))
    (ROOT/'output/evidence'/'parts.json').write_text(json.dumps(g.parts,indent=2))
    (ROOT/'output/design.json').write_text(json.dumps(spec,indent=2))
    wanted=[b['id'] for b in g.body if b['name'].startswith('CHECK')]
    (ROOT/'output/evidence'/'kinematic_recipe.json').write_text(json.dumps(g.recipe(g.closure(wanted)),indent=1))
    # Each export evaluates the dependency closure of one colored subsystem.
    # This avoids keeping export blocks active in the final presentation notebook.
    edir=ROOT/'output/evidence'/'export_recipes';edir.mkdir(exist_ok=True)
    manifest=[]
    for i,p in enumerate(g.parts):
        if p['name'].startswith('Fasteners - '):continue
        safe='%02d_'%i+''.join(c if c.isalnum() else '_' for c in p['name']).strip('_')
        out=ROOT/'output/exports'/(safe+'.stl')
        body=g.closure([p['id']])
        ref={'props':[],'ref':{'id':p['id']}}
        tol=.4 if ('gear' in p['name'].lower() or 'pinion' in p['name'].lower() or 'ring' in p['name'].lower() or 'spring' in p['name'].lower() or 'belt' in p['name'].lower() or 'pulleys' in p['name'].lower()) else .9
        if 'involute oil pump' in p['name']:tol=.08
        if p['system'].startswith(('14','15')) or 'exhaust' in p['name'].lower():tol=.45
        final_mesh=g.sharp_mesh(ref,tol)
        mesher='AT + Sharpen Mesh, one iteration, no remesh'
        if 'helical valve springs' in p['name']:
            # Native AT produces 32 tiny closed islands at this field's seams.
            # Measured max island volume: 0.000112 mm^3. Keep the 24 full coils.
            threshold={'type':'real','value':{'isFinite':True,'units':{'length':3},'val':1e-11}}
            final_mesh=g.node('merge_meshes',g.node('filter_meshes',g.node('split_mesh',final_mesh),threshold))
            mesher+='; native split/filter/merge, volume threshold 0.01 mm^3'
        export=g.node('export',literal('file_path',{'val':str(out)}),final_mesh,literal('unit_length_enum',{'id':'mm'}))
        body=body+[{'contents':export,'id':g.uid(),'name':'Export '+p['name'],'type':'mesh_file_data','variable':True}]
        fn=edir/(safe+'.json');fn.write_text(json.dumps(g.recipe(body),indent=1))
        manifest.append({**p,'recipe':str(fn),'mesh':str(out),'tolerance_mm':tol,'mesher':mesher})
    # One combined fastener export retains the colors of its one material group.
    fps=[p for p in g.parts if p['name'].startswith('Fasteners - ')]
    body=g.closure([p['id'] for p in fps]); name='All fixed assembly fasteners';safe='90_All_fixed_assembly_fasteners'
    union=g.union(*[{'props':[],'ref':{'id':p['id']}} for p in fps])
    fixedid=g.uid();body.append({'contents':union,'id':fixedid,'name':'Fixed fastener export body','type':'implicit','variable':True})
    out=ROOT/'output/exports'/(safe+'.stl');export=g.node('export',literal('file_path',{'val':str(out)}),g.sharp_mesh({'props':[],'ref':{'id':fixedid}},.6),literal('unit_length_enum',{'id':'mm'}))
    body.append({'contents':export,'id':g.uid(),'name':'Export fasteners','type':'mesh_file_data','variable':True})
    fn=edir/(safe+'.json');fn.write_text(json.dumps(g.recipe(body),indent=1))
    manifest.append({'name':name,'color':DARK,'system':'13 Assembly fasteners','recipe':str(fn),'mesh':str(out),'tolerance_mm':.6,'count':sum(x['count'] for x in fps),'mesher':'AT + Sharpen Mesh, one iteration, no remesh'})
    (ROOT/'output/evidence'/'export_manifest.json').write_text(json.dumps(manifest,indent=2))
    # Validate the native identifiers and reference graph before importing.
    catalog=set(json.loads((ROOT/'inputs/initial_state.json').read_text())['blocks'])
    identifiers=set();ids=[];refs=[];empty=[]
    def walk(x):
        if isinstance(x,dict):
            if 'func' in x:identifiers.add(x['func'])
            if 'id' in x and 'ref' not in x:ids.append(x['id'])
            if 'ref' in x:refs.append(x['ref']['id']);return
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(g.recipe())
    missing=sorted(identifiers-catalog)
    assert not missing,missing
    assert not (set(refs)-set(ids)),set(refs)-set(ids)
    assert len(ids)==len(set(ids)),'Reused raw block: wrap it in a variable'
    evidence={'native_nodes':len(ids),'variables':len(g.body),'native_block_types':len(identifiers),'render_groups':len(g.parts),
              'export_groups':len(manifest),'fixed_fasteners':len(spec['fasteners']),'rod_fasteners':12,
              'identifiers_verified':not missing,'duplicate_ids':False}
    (ROOT/'output/evidence'/'graph_audit.json').write_text(json.dumps(evidence,indent=2));print(json.dumps(evidence,indent=2))

if __name__=='__main__':main()
