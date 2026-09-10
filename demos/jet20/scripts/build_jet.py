"""Build original parametric native geometry, using SI Notebook API recipes.

The reference notebooks informed vane organization and camber controls.
Their geometry and private custom blocks are not copied into this graph.
"""
from pathlib import Path
import sys,json,math
from native_graph import Graph,real,literal,IDS
ROOT=Path(__file__).resolve().parents[1]
IDS['plane']=('plane_from_normal<point,vector>[1.1.0]','plane')

class Jet(Graph):
    def __init__(self):super().__init__();self.section='01 Design inputs'
    def uid(self):self.k+=1;return 'jet_%06d'%self.k
    def calc(self,name,op,*args):return self.var(name,self.math(op,*args),'real')
    def f(self,op,*a):return self.math(op,*a,field=True)
    def field(self,name,axis):
        pl=self.var(name+' plane',self.node('plane',self.pt((0,0,0)),self.vec(axis,False)),'plane')
        return self.var(name,self.prop(pl,'body'),'real_field')
    def ring(self,z0,z1,ro,ri):return self.sub(self.cyl((0,0,z0),(0,0,z1),ro),self.cyl((0,0,self.math('subtract',z0,real(1))),(0,0,self.math('add',z1,real(1))),ri))
    def recipe(self,body=None):
        d=json.loads(json.dumps(super().recipe(body)))
        if body is None:
            from shared_expressions import compact,expanded_hashes
            before=expanded_hashes(d);d,sharing=compact(d,6);after=expanded_hashes(d)
            assert all(before[k]==after[k] for k in before),'Expression sharing changed geometry'
            for b in d['body']:
                if b['name'].startswith('SHARED '):self.layout['variables'][b['name']]='09 Assembly structures'
            (ROOT/'output/results/expression_sharing_verification.json').write_text(json.dumps(sharing|{'base_variables':len(before),'native_variables':len(d['body']),'unchanged_expanded_variables':len(before)},indent=2))
        # Detailing can add dependencies to earlier parts. Import each variable
        # after its dependencies instead of relying on forward-reference handling.
        by={b['id']:b for b in d['body']};ordered=[];done=set();active=set()
        def refs(x):
            if isinstance(x,dict):
                if 'ref' in x:yield x['ref']['id']
                else:
                    for v in x.values():yield from refs(v)
            elif isinstance(x,list):
                for v in x:yield from refs(v)
        def visit(k):
            if k in done:return
            if k in active:raise ValueError('Cyclic native dependency: '+k)
            active.add(k)
            for dep in refs(by[k]['contents']):visit(dep)
            active.remove(k);done.add(k);ordered.append(by[k])
        for b in d['body']:visit(b['id'])
        d['body']=ordered
        # Reused unnamed expressions need independent occurrence IDs. Only named
        # variables are shared by reference, per the Notebook API fan-out rule.
        seq=[0]
        def unique(x):
            if isinstance(x,dict):
                if 'func' in x:
                    seq[0]+=1;x['id']='jet_expression_%06d'%seq[0]
                for v in x.values():unique(v)
            elif isinstance(x,list):
                for v in x:unique(v)
        unique(d)
        d.update(displayname='Jet20 | Parametric preliminary turbojet',description='Native parametric geometry. 20 lbf flight sizing study. Unvalidated hardware design.',name='user_func_jet20_preliminary');return d

def build(probe=False):
    d=json.loads((ROOT/'output/results/design.json').read_text());c=d['inputs'];r=d['design'];s=d['geometry'];g=Jet()
    P={}
    def param(name,v,unit='length'):
        p=g.param(name,v,unit);P[name]=p;return p
    def gm(name,k):return param(name,s[k]*1000)
    ro=gm('Compressor exit radius','impeller_radius_m');eye=gm('Compressor eye radius','eye_tip_radius_m');eh=gm('Compressor eye hub radius','eye_hub_radius_m');bw=gm('Compressor exit width','impeller_exit_width_m')
    tr=gm('Turbine tip radius','turbine_tip_radius_m');hr=gm('Turbine hub radius','turbine_hub_radius_m');mr=gm('Turbine mean radius','turbine_mean_radius_m')
    cr=gm('Case radius','case_radius_m');length=gm('Case length','case_length_m');sh=gm('Shaft radius','shaft_radius_m')
    nr=param('Nozzle exit radius',r['nozzle_diameter_m']*500)
    wall=param('Case wall',c['case_wall_m']*1000);clear=param('Rotor tip clearance',c['rotor_tip_clearance_m']*1000)
    cb=param('Compressor blade thickness',c['compressor_blade_thickness_m']*1000);tb=param('Turbine blade thickness',c['turbine_blade_thickness_m']*1000)
    nc=param('Compressor full blade count',c['compressor_full_blades'],'');ns=param('Compressor splitter count',c['compressor_splitter_blades'],'');nt=param('Turbine rotor blade count',c['turbine_rotor_blades'],'');nv=param('Turbine stator vane count',c['turbine_stator_vanes'],'')
    back=param('Compressor backsweep',c['compressor_backsweep_deg'],'angle');tw=param('Compressor inducer twist',25,'angle');split=param('Splitter radial start fraction',c['compressor_splitter_start'],'')
    b1=param('Rotor inlet angle',s['rotor_inlet_angle_deg'],'angle');b2=param('Rotor exit angle',s['rotor_exit_angle_deg'],'angle');a2=param('Stator exit angle',s['stator_exit_angle_deg'],'angle');span_twist=param('Rotor spanwise twist',0,'angle')
    chord=param('Turbine axial chord',c['turbine_axial_chord_m']*1000)
    pipeOD=param('Fuel pipe OD',c['fuel_pipe_OD_m']*1000);pipeID=param('Fuel pipe ID',c['fuel_pipe_ID_m']*1000);wireOD=param('Wire bundle OD',c['wire_bundle_OD_m']*1000);stand=param('Route standoff',c['route_standoff_m']*1000)
    param('Cycle target thrust lbf',c['target_thrust_lbf'],'');param('Cycle compressor pressure ratio',c['compressor_pressure_ratio'],'');param('Cycle turbine inlet temperature K',c['turbine_inlet_K'],'');param('Shaft speed rpm',c['shaft_rpm'],'')
    z0=param('Impeller inlet station',20);z1=param('Impeller backplate station',55)
    zburn=param('Combustor start station',90);zt=param('Turbine rotor station',s['case_length_m']*1000*.73)
    # Live scalar dimensions: one native reference feeds all dependent geometry.
    compL=g.calc('CHECK impeller length','subtract',z1,z0)
    zsh=g.calc('Impeller shroud end','subtract',z1,bw)
    zafter=g.calc('Backplate end','add',z1,real(3))
    Rout=g.calc('Case outer radius','add',cr,wall)
    shr=g.calc('CHECK compressor diameter','multiply',ro,real(2,''))
    g.calc('CHECK turbine tip diameter','multiply',tr,real(2,''))
    g.calc('CHECK nozzle area m2','multiply',g.math('multiply',nr,nr),real(math.pi,''))
    g.calc('CHECK tip clearance','subtract',g.math('add',tr,clear),tr)
    g.section='02 Coordinate fields'
    xf=g.field('Field X',(1,0,0));yf=g.field('Field Y',(0,1,0));zf=g.field('Field Z',(0,0,1))
    rho=g.var('Field radius',g.f('sqrt',g.f('add',g.f('multiply',xf,xf),g.f('multiply',yf,yf))),'real_field')
    theta=g.var('Field azimuth',g.f('atan2',yf,xf),'real_field')
    g.section='03 Compressor'
    hub=g.var('Compressor hub blank',g.cone((0,0,z0),(0,0,z1),eh,ro),'implicit')
    outer=g.var('Compressor shroud domain',g.union(g.cone((0,0,z0),(0,0,zsh),eye,ro),g.cyl((0,0,zsh),(0,0,z1),ro)),'implicit')
    domain=g.var('Compressor passage domain',g.sub(outer,hub),'implicit')
    zz=g.var('Compressor axial fraction',g.f('divide',g.f('subtract',zf,z0),compL),'real_field')
    rr=g.var('Compressor radial fraction',g.f('divide',rho,ro),'real_field')
    phase=g.var('Compressor camber angle',g.f('add',g.f('multiply',back,g.f('multiply',rr,rr)),g.f('multiply',tw,g.f('subtract',real(1,''),zz))),'real_field')
    def blades(name,count,phase,thickness,domain):
        # Periodic camber surface with finite thickness, then exact solid clipping.
        q=g.var(name+' phase',g.f('multiply',g.f('subtract',theta,phase),g.math('multiply',count,real(.5,''))),'real_field')
        sn=g.var(name+' sine',g.f('sin',q),'real_field')
        dist=g.f('subtract',g.f('multiply',g.f('divide',g.f('multiply',rho,real(2,'')),count),g.f('sqrt',g.f('multiply',sn,sn))),g.math('multiply',thickness,real(.5,'')))
        field=g.var(name+' surface field',dist,'implicit')
        return g.inter(field,domain)
    full=blades('Full blade',nc,phase,cb,domain)
    if probe:
        part=g.part('Probe compressor blades',full,(.7,.72,.76),'03 Compressor')
        m=g.node('mesh',part,real(.6))
        g.var('Probe export',g.node('export',literal('file_path',{'val':str(ROOT/'output/results/probe_blades.stl')}),m,literal('unit_length_enum',{'id':'mm'})))
        ids=[g.body[-1]['id']];recipe=g.recipe(g.closure(ids));(ROOT/'output/build').mkdir(exist_ok=True);(ROOT/'output/build/probe_recipe.json').write_text(json.dumps(recipe,indent=1));return g
    splitterPhase=g.var('Splitter phase offset',g.f('add',phase,g.math('divide',real(180,'angle'),ns)),'real_field')
    splitterDomain=g.var('Splitter domain',g.sub(domain,g.cyl((0,0,real(0)),(0,0,real(100)),g.math('multiply',ro,split))),'implicit')
    secondary=blades('Splitter blade',ns,splitterPhase,cb,splitterDomain)
    disk=g.ring(z1,zafter,ro,sh)
    imp=g.part('COMP Impeller',g.sub(g.union(full,secondary,hub,disk),g.cyl((0,0,real(0)),(0,0,real(100)),sh)),(.70,.74,.80),'03 Compressor')
    shroud=g.part('COMP Shroud',g.sub(g.node('offset',outer,wall),outer),(.63,.66,.7),'03 Compressor')
    # Diffuser vanes occupy the radial passage outside the impeller.
    diffOuter=g.calc('Diffuser outer radius','multiply',ro,real(1.42,''));diffInner=g.calc('Diffuser inner radius','multiply',ro,real(1.06,''))
    diffDomain=g.var('Diffuser domain',g.ring(zsh,z1,diffOuter,diffInner),'implicit')
    diffPhase=g.var('Diffuser camber angle',g.f('multiply',real(35,'angle'),g.f('divide',rho,diffOuter)),'real_field')
    diffuser=g.part('COMP Diffuser vanes',blades('Diffuser vane',real(17,''),diffPhase,real(1),diffDomain),(.48,.53,.60),'03 Compressor')
    g.part('COMP Diffuser backplate',g.ring(z1,zafter,diffOuter,ro),(.5,.54,.6),'03 Compressor')
    g.section='04 Combustor'
    zo=g.calc('Combustor end','subtract',zt,real(18));burnOR=g.calc('Combustor outer radius','multiply',cr,real(.83,''));burnIR=g.calc('Combustor inner radius','multiply',cr,real(.42,''))
    linerOuter=g.ring(zburn,zo,burnOR,g.math('subtract',burnOR,wall));linerInner=g.ring(zburn,zo,g.math('add',burnIR,wall),burnIR)
    # List processing via native polar arrays keeps the hole family compact.
    holes=[];hole_areas=[]
    hole_scale=param('Liner hole radius scale',c.get('liner_hole_radius_scale',1),'')
    for frac,radius,count in [(0.2,1.3,18),(.48,2.5,12),(.76,3.5,12)]:
        z=g.calc('Combustor hole row '+str(frac),'add',zburn,g.math('multiply',g.math('subtract',zo,zburn),real(frac,'')))
        hole_radius=g.calc('CHECK liner row '+str(frac)+' radius','multiply',real(radius),hole_scale)
        hole_areas.append(g.math('multiply',g.math('multiply',hole_radius,hole_radius),real(math.pi*count,'')))
        hole=g.cyl((real(0),g.math('subtract',burnOR,real(3)),z),(real(0),g.math('add',burnOR,real(3)),z),hole_radius)
        holes.append(g.polar(hole,count,axis=(0,0,1)))
    g.calc('CHECK total liner hole open area','add',g.math('add',hole_areas[0],hole_areas[1]),hole_areas[2])
    fuelPortZ=g.calc('Fuel penetration station','add',zburn,real(9))
    fuel_phi=param('Main fuel entry azimuth',-15,'angle')
    def fuel_point(rad):return (g.math('multiply',rad,g.math('cos',fuel_phi)),g.math('multiply',rad,g.math('sin',fuel_phi)),fuelPortZ)
    fuelPort=g.cyl(fuel_point(g.math('multiply',cr,real(.6,''))),fuel_point(g.math('add',cr,real(12))),g.math('multiply',pipeOD,real(.6,'')))
    igniter_z=param('Igniter station',107)
    ignitionPort=g.cyl((real(8),g.math('subtract',burnOR,real(5)),igniter_z),(real(8),g.math('add',cr,real(9)),igniter_z),real(3.4))
    g.part('BURN Outer liner',g.sub(linerOuter,*holes,fuelPort,ignitionPort),(.65,.59,.52),'04 Combustor')
    g.part('BURN Inner liner',linerInner,(.60,.54,.48),'04 Combustor')
    g.part('BURN Dome',g.ring(zburn,g.math('add',zburn,real(2)),burnOR,burnIR),(.65,.59,.52),'04 Combustor')
    manifoldR=g.calc('Fuel manifold radius','multiply',cr,real(.67,''));manifoldZ=g.calc('Fuel manifold station','add',zburn,real(9))
    fuelRing=g.sub(g.torus((0,0,manifoldZ),(0,0,1),manifoldR,g.math('multiply',pipeOD,real(.5,''))),g.torus((0,0,manifoldZ),(0,0,1),manifoldR,g.math('multiply',pipeID,real(.5,''))))
    g.part('FUEL Manifold',fuelRing,(.949,.42,.263),'06 Pipes and wiring')
    nozzle=g.ring(g.math('add',manifoldZ,real(1)),g.math('add',manifoldZ,real(10)),real(1.8),real(.65))
    nozzle=g.move(nozzle,(manifoldR,0,0));g.part('FUEL Injector envelopes',g.polar(nozzle,12,axis=(0,0,1)),(.72,.5,.3),'04 Combustor')
    g.section='05 Turbine and shaft'
    zte=g.calc('Turbine rotor exit','add',zt,chord);sv0=g.calc('Turbine stator inlet','subtract',zt,real(15));sv1=g.calc('Turbine stator exit','subtract',zt,real(3))
    rotorDomain=g.var('Rotor annulus',g.ring(zt,zte,tr,hr),'implicit')
    tv=g.var('Rotor axial fraction',g.f('divide',g.f('subtract',zf,zt),chord),'real_field')
    t1=g.calc('Rotor inlet tangent','tan',b1);t2=g.calc('Rotor exit tangent','tan',b2)
    camber=g.f('multiply',g.math('divide',chord,mr),g.f('add',g.f('multiply',t1,tv),g.f('multiply',g.math('multiply',g.math('subtract',t2,t1),real(.5,'')),g.f('multiply',tv,tv))))
    # arc length / radius is radians. real(..., 'angle') takes degrees.
    radians_to_angle=real(180/math.pi,'angle')
    phase_t=g.var('Rotor camber angle',g.f('add',g.f('multiply',camber,radians_to_angle),g.f('multiply',span_twist,g.f('divide',g.f('subtract',rho,mr),g.math('subtract',tr,hr)))),'real_field')
    rotorblades=blades('Turbine rotor blade',nt,phase_t,tb,rotorDomain)
    rotorDisk=g.ring(g.math('subtract',zt,real(2)),g.math('add',zte,real(2)),hr,sh)
    g.part('TURB Rotor blisk',g.union(rotorblades,rotorDisk),(.6,.64,.72),'05 Turbine and shaft')
    statDomain=g.var('Stator annulus',g.ring(sv0,sv1,tr,hr),'implicit')
    ts=g.var('Stator axial fraction',g.f('divide',g.f('subtract',zf,sv0),g.math('subtract',sv1,sv0)),'real_field')
    phase_s=g.var('Stator camber angle',g.f('multiply',g.f('multiply',g.f('multiply',ts,ts),g.math('multiply',g.math('tan',a2),real(.5,''))),g.math('multiply',g.math('divide',g.math('subtract',sv1,sv0),mr),radians_to_angle)),'real_field')
    g.part('TURB Nozzle guide vanes',g.union(blades('Turbine stator vane',nv,phase_s,tb,statDomain),g.ring(sv0,sv1,g.math('add',tr,real(1.5)),tr)),(.53,.57,.63),'05 Turbine and shaft')
    g.part('TURB Tip shroud',g.ring(zt,zte,g.math('add',g.math('add',tr,clear),wall),g.math('add',tr,clear)),(.52,.55,.60),'05 Turbine and shaft')
    g.part('SHAFT Common shaft',g.cyl((0,0,real(9)),(0,0,g.math('add',zte,real(8))),sh),(.5,.54,.6),'05 Turbine and shaft')
    for name,z in [('Front',75),('Rear',s['case_length_m']*1000*.64)]:
        bp=param(name+' bearing station',z)
        g.part('BEARING '+name+' cartridge',g.ring(bp,g.math('add',bp,real(9)),real(9),sh),(.34,.4,.5),'05 Turbine and shaft')
    g.part('SHAFT Bearing tunnel',g.ring(real(74),g.math('subtract',zt,real(17)),real(12),real(10)),(.42,.45,.5),'05 Turbine and shaft')
    g.section='07 Case and nozzle'
    probe_z=g.calc('Exhaust probe station','add',zte,real(5))
    probePort=g.cyl((real(-8),g.math('subtract',tr,real(5)),probe_z),(real(-8),g.math('add',cr,real(9)),probe_z),real(1.1))
    pressure_phi=param('Pressure tap azimuth',-55,'angle')
    pressure_z=g.calc('Pressure tap station','multiply',g.math('add',zsh,z1),real(.5,''))
    def pressure_point(rad):return (g.math('multiply',rad,g.math('cos',pressure_phi)),g.math('multiply',rad,g.math('sin',pressure_phi)),pressure_z)
    pressurePort=g.cyl(pressure_point(g.math('subtract',cr,real(3))),pressure_point(g.math('add',cr,real(10))),real(1.2))
    case=g.part('CASE Full casing',g.sub(g.ring(real(12),g.math('add',zte,real(12)),Rout,cr),fuelPort,ignitionPort,probePort,pressurePort),(.72,.74,.78),'07 Case and nozzle')
    g.layout['final_bodies']['CASE Full casing'][-1]=.16
    nose=g.sub(g.cone((0,0,real(0)),(0,0,real(20)),eye,cr),g.cone((0,0,real(-1)),(0,0,real(21)),g.math('subtract',eye,wall),g.math('subtract',cr,wall)))
    g.part('CASE Inlet bell',nose,(.64,.67,.73),'07 Case and nozzle')
    nz=g.calc('Nozzle start','add',zte,real(12))
    slope=g.calc('Nozzle radius slope','divide',g.math('subtract',cr,nr),g.math('subtract',length,nz))
    overrun=g.calc('Nozzle bore overrun radius','multiply',slope,real(1))
    nozzleBody=g.sub(g.cone((0,0,nz),(0,0,length),Rout,g.math('add',nr,wall)),g.cone((0,0,g.math('subtract',nz,real(1))),(0,0,g.math('add',length,real(1))),g.math('add',cr,overrun),g.math('subtract',nr,overrun)))
    g.part('NOZZLE Convergent duct',nozzleBody,(.68,.69,.72),'07 Case and nozzle')
    g.part('NOZZLE Center cone',g.cone((0,0,g.math('add',zte,real(3))),(0,0,g.math('subtract',length,real(13))),hr,real(.8)),(.6,.62,.68),'07 Case and nozzle')
    g.part('STARTER Motor envelope',g.cyl((0,0,real(-17)),(0,0,real(12)),real(11)),(.3,.35,.43),'07 Case and nozzle')
    g.section='06 Pipes and wiring'
    # Routes use native cubic splines and live endpoint coordinates.
    service=g.calc('Service radius','add',Rout,stand)
    pR=g.calc('Fuel pipe radius','multiply',pipeOD,real(.5,''));iR=g.calc('Fuel pipe bore radius','multiply',pipeID,real(.5,''));wR=g.calc('Wire bundle radius','multiply',wireOD,real(.5,''))
    def route(name,points,outer,inner=0,color=(.949,.42,.263),segments=None):
        if len(points)==3:
            mid=tuple(g.math('multiply',g.math('add',a,b),real(.5,'')) for a,b in zip(points[0],points[1]))
            points=[points[0],mid,*points[1:]]
        curve=g.spline_curve(name+' centerline',points)
        field=g.var(name+' distance',g.prop(curve,'scalar field'),'implicit')
        if segments:
            fields=[field]
            for i,segment in enumerate(segments):
                segment_curve=g.spline_curve(name+' segment '+str(i+2),segment)
                fields.append(g.var(name+' segment distance '+str(i+2),g.prop(segment_curve,'scalar field'),'implicit'))
            field=g.var(name+' joined distance',g.union(*fields),'implicit')
        body=g.node('offset',field,outer)
        if inner:
            bore=g.node('offset',field,inner)
            # Extend bores through both endpoint caps with short cylinders.
            caps=[]
            end=segments[-1] if segments else points
            for a,b in [(points[0],points[1]),(end[-1],end[-2])]:
                delta=[g.math('subtract',v,u) for u,v in zip(a,b)]
                norm=g.math('sqrt',g.math('add',g.math('add',g.math('multiply',delta[0],delta[0]),g.math('multiply',delta[1],delta[1])),g.math('multiply',delta[2],delta[2])))
                normal=g.node('vector',*[g.math('divide',x,norm) for x in delta])
                pl=g.var(name+' end trim '+str(len(caps)),g.node('plane',g.pt(a),normal),'plane')
                caps.append(g.inter(g.sphere(a,g.math('multiply',outer,real(1.05,''))),g.prop(pl,'body')))
            body=g.sub(body,bore,*caps)
        ref=g.part(name,body,color,'06 Pipes and wiring');g.routes.append({'name':name,'points':points,'curve':curve,'hollow':bool(inner),**({'segments':[points,*segments]} if segments else {})});return ref
    # Separate cubic spans keep the bend local and the entire long run straight.
    feed_phi=param('Rear feed azimuth',-10,'angle')
    feed_r=param('Rear feed axial radius',15)
    feed_z=param('Rear feed entry station',64)
    feed_bend=param('Rear feed bend radius',6)
    feed_or=param('Rear feed outer radius',.9)
    feed_ir=param('Rear feed bore radius',.5)
    feed_gap=param('Rear feed guide clearance',.15)
    feed_end=g.calc('Rear feed receiver station','subtract',P['Rear bearing station'],real(5))
    def feed_point(r,z):
        return (g.math('multiply',r,g.math('cos',feed_phi)),g.math('multiply',r,g.math('sin',feed_phi)),z)
    add=lambda a,b:g.math('add',a,b)
    sub=lambda a,b:g.math('subtract',a,b)
    mul=lambda a,b:g.math('multiply',a,real(b,''))
    bend_start=add(feed_r,feed_bend);bend_end=add(feed_z,feed_bend)
    bend_tangent=mul(feed_bend,4*(math.sqrt(2)-1)/3)
    radial=[feed_point(service,feed_z),feed_point(add(mul(service,2/3),mul(bend_start,1/3)),feed_z),feed_point(add(mul(service,1/3),mul(bend_start,2/3)),feed_z),feed_point(bend_start,feed_z)]
    elbow=[feed_point(bend_start,feed_z),feed_point(sub(bend_start,bend_tangent),feed_z),feed_point(feed_r,sub(bend_end,bend_tangent)),feed_point(feed_r,bend_end)]
    axial=[feed_point(feed_r,bend_end),feed_point(feed_r,add(mul(bend_end,2/3),mul(feed_end,1/3))),feed_point(feed_r,add(mul(bend_end,1/3),mul(feed_end,2/3))),feed_point(feed_r,feed_end)]
    route('F03 Rear bearing feed',radial,feed_or,feed_ir,segments=[elbow,axial])
    hardware_seed=json.loads((ROOT/'inputs/hardware.json').read_text())['design_seeds_mm']
    from service_routes import build_routes
    p3=build_routes(g,locals())
    # Sensor and service envelopes are explicit parts with editable stations.
    g.part('ECU Service envelope',g.box((real(-19),g.math('add',service,real(3)),real(10)),(real(19),g.math('add',service,real(18)),real(48))),(.25,.3,.4),'06 Pipes and wiring')
    g.part('FUEL Pump envelope',g.cyl((service,real(0),real(-9)),(service,real(0),real(12)),real(6)),(.45,.5,.58),'06 Pipes and wiring')
    g.part('IGNITER Boss',g.cyl((real(8),g.math('subtract',burnOR,real(2)),igniter_z),(real(8),g.math('add',Rout,real(6)),igniter_z),real(3.2)),(.47,.50,.55),'06 Pipes and wiring')
    probe_stem=g.cyl((real(-8),real(26),probe_z),(real(-8),g.math('add',Rout,real(3)),probe_z),real(.8))
    probe_head=g.cyl((real(-8),g.math('add',Rout,real(2)),probe_z),(real(-8),g.math('add',Rout,real(7)),probe_z),real(2.5))
    g.part('SENSOR Exhaust probe',g.union(probe_stem,probe_head),(.47,.50,.55),'06 Pipes and wiring')
    from assembly_detail import detail
    assembly=detail(g,locals())
    # Bounding box readbacks for inexpensive native dimension checks.
    g.section='08 Verification'
    for name,part in [('Impeller',imp),('Casing',case)]:
        bb=g.var('CHECK '+name+' box',g.prop(part,'bounding box'),'bounding_box')
        for suffix in ['min','max']:
            raw=g.var('MEASURE '+name+' '+suffix+' property',g.prop(bb,suffix+' point'),'point')
            pt=g.var('CHECK '+name+' '+suffix,raw,'point')
            for axis in 'xyz':g.var('CHECK '+name+' '+suffix+' '+axis,g.math('multiply',g.prop(pt,axis),real(1,'')),'real')
    (ROOT/'output/build').mkdir(exist_ok=True);g.write(ROOT/'output/build/jet20_recipe.json')
    (ROOT/'output/build/layout.json').write_text(json.dumps(g.layout,indent=2))
    (ROOT/'output/build/parts.json').write_text(json.dumps(g.parts,indent=2))
    (ROOT/'output/build/routes.json').write_text(json.dumps(g.routes,indent=2))
    (ROOT/'output/build/joints_native.json').write_text(json.dumps(g.joints,indent=2))
    # Full-model validation uses dependency closures to avoid unnecessary rendering.
    print('Base variables:',len(g.body),'Parts:',len(g.parts),'Routes:',len(g.routes))
    return g

if __name__=='__main__':build('--probe' in sys.argv)
