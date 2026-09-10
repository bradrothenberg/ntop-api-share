"""P3 service routes with straight crossings and shared interface coordinates."""
import math,json
from pathlib import Path
from native_graph import real

def build_routes(g,ctx):
    p=ctx['param'];route=ctx['route'];R=ctx['service'];cr=ctx['cr'];outer=ctx['Rout']
    A=lambda a,b:g.math('add',a,b if isinstance(b,dict) else real(b))
    S=lambda a,b:g.math('subtract',a,b if isinstance(b,dict) else real(b))
    M=lambda a,k:g.math('multiply',a,real(k,''))
    def line(a,b):
        return [a,tuple(A(M(x,2/3),M(y,1/3)) for x,y in zip(a,b)),tuple(A(M(x,1/3),M(y,2/3)) for x,y in zip(a,b)),b]
    def radial(r,z,phi):return (g.math('multiply',r,g.math('cos',phi)),g.math('multiply',r,g.math('sin',phi)),z)
    def emit(name,segments,ro,ri=0,color=(.949,.42,.263)):
        return route(name,segments[0],ro,ri,color,segments=segments[1:])
    k=4*(math.sqrt(2)-1)/3
    cable=p('Cable routing radius',json.loads((Path(__file__).resolve().parents[1]/'inputs/design.json').read_text())['cable_routing_radius_m']*1000)
    bend=p('Service local bend radius',6)
    connector_z=p('Connector port station',24)
    zfuel=ctx['fuelPortZ'];fuelR=ctx['manifoldR']
    phi=ctx['fuel_phi'];fp=lambda r,z:radial(r,z,phi)
    fuel=[line((R,real(0),real(15)),(R,real(0),real(65))),
        [(R,real(0),real(65)),(R,real(0),real(75)),fp(R,real(77)),fp(R,real(87))],
        line(fp(R,real(87)),fp(R,S(zfuel,bend))),
        [fp(R,S(zfuel,bend)),fp(R,S(zfuel,M(bend,1-k))),fp(A(S(R,bend),M(bend,k)),zfuel),fp(S(R,bend),zfuel)],
        line(fp(S(R,bend),zfuel),fp(fuelR,zfuel))]
    emit('F01 Main fuel feed',fuel,ctx['pR'],ctx['iR'])
    ffz=p('Front feed entry station',86);ffphi=p('Front feed azimuth',15,'angle');ffend=p('Front feed receiver radius',13)
    emit('F02 Front bearing feed',[line(radial(R,ffz,ffphi),radial(ffend,ffz,ffphi))],real(.9),real(.5))
    pz=ctx['pressure_z'];pphi=ctx['pressure_phi'];pend=S(cr,2)
    pressure=[line(radial(R,real(25),pphi),radial(R,S(pz,bend),pphi)),
        [radial(R,S(pz,bend),pphi),radial(R,S(pz,M(bend,1-k)),pphi),radial(A(S(R,bend),M(bend,k)),pz,pphi),radial(S(R,bend),pz,pphi)],
        line(radial(S(R,bend),pz,pphi),radial(pend,pz,pphi))]
    emit('P01 Pressure sense',pressure,real(1),real(.6),(.47,.52,.58))
    wire=(.086,.28,.615)
    def wire_y(name,x,z,yend,radius,reverse=False):
        x=real(x);dy=bend;entry=A(z,dy) if reverse else S(z,dy)
        tang=A(entry,M(dy,-k if reverse else k))
        spans=[line((x,cable,connector_z if reverse else real(15)),(x,cable,entry)),
            [(x,cable,entry),(x,cable,tang),(x,A(S(cable,dy),M(dy,k)),z),(x,S(cable,dy),z)],
            line((x,S(cable,dy),z),(x,yend,z))]
        emit(name,spans,radius,color=wire)
    starter_z=p('Starter terminal station',-13);starter_y=p('Starter terminal radius',12)
    wire_y('E01 Starter harness',0,starter_z,starter_y,ctx['wR'],True)
    ignition_y=g.calc('Ignition terminal radius','add',outer,real(5))
    probe_y=g.calc('Probe terminal radius','add',outer,real(5))
    wire_y('E02 Ignition lead',8,ctx['igniter_z'],ignition_y,real(1.4))
    wire_y('E03 Temperature harness',-8,ctx['probe_z'],probe_y,real(1.1))
    speed_z=p('Speed lead entry station',68);speed_y=p('Speed lead endpoint radius',12)
    wire_y('E04 Speed pickup lead',15,speed_z,speed_y,real(1.1))
    return dict(cable=cable,bend=bend,connector_z=connector_z,front_z=ffz,front_phi=ffphi,front_end=ffend,
                pressure_z=pz,pressure_phi=pphi,radial=radial,starter_z=starter_z,starter_y=starter_y,
                ignition_y=ignition_y,probe_y=probe_y,speed_z=speed_z,speed_y=speed_y)
