"""P3 matched case sleeves, terminal pockets, and receiver geometry."""
from native_graph import real

def detail_interfaces(g,ctx,helpers):
    extend,drill=helpers
    d=ctx['p3'];cr=ctx['cr'];R=ctx['Rout'];p=d['radial']
    A=lambda a,b:g.math('add',a,b if isinstance(b,dict) else real(b))
    S=lambda a,b:g.math('subtract',a,b if isinstance(b,dict) else real(b))
    # Fluid passages use the same station and azimuth as the straight tubes.
    z=ctx['fuelPortZ']
    fp=ctx['fuel_point']
    extend('CASE Front barrel',g.cyl(fp(S(cr,1)),fp(A(R,3)),3.2))
    drill('CASE Front barrel',[g.cyl(fp(S(cr,3)),fp(A(R,5)),1.8)])
    for z,phi,ro,bore in [(d['front_z'],d['front_phi'],2.5,1.05),(d['pressure_z'],d['pressure_phi'],2.5,1.2)]:
        extend('CASE Front barrel',g.cyl(p(S(cr,1),z,phi),p(A(R,3),z,phi),ro))
        drill('CASE Front barrel',[g.cyl(p(S(cr,4),z,phi),p(A(R,5),z,phi),bore)])
    # F02 discharges into the housing cavity just behind the front bearing.
    z=d['front_z'];phi=d['front_phi'];end=d['front_end']
    extend('SHAFT Bearing tunnel',g.cyl(p(real(10),z,phi),p(A(end,2),z,phi),2.3))
    drill('SHAFT Bearing tunnel',[g.cyl(p(S(end,.05),z,phi),p(A(end,3),z,phi),.95),g.cyl(p(real(8),z,phi),p(A(end,.05),z,phi),.5)])
    # The union needs room in both members of the inlet flange stack.
    service=ctx['service']
    drill('CASE Front barrel',[g.cyl((service,0,real(11.8)),(service,0,real(15.3)),3.45)])
    drill('CASE Inlet bell',[g.cyl((service,0,real(7.8)),(service,0,real(12.2)),2.15)])
    drill('FUEL Pump envelope',[g.cyl((service,0,real(7.8)),(service,0,real(9.2)),2.15)])
    # Electrical leads stop in exterior terminal pockets, outside the pressure wall.
    drill('IGNITER Boss',[g.cyl((8,A(R,2),ctx['igniter_z']),(8,A(R,10),ctx['igniter_z']),1.6)])
    drill('SENSOR Exhaust probe',[g.cyl((-8,A(R,3.5),ctx['probe_z']),(-8,A(R,10),ctx['probe_z']),1.3)])
    sz=d['starter_z']
    extend('STARTER Motor envelope',g.cyl((0,9,sz),(0,15,sz),3.5))
    drill('STARTER Motor envelope',[g.cyl((0,8,sz),(0,17,sz),2.2)])
    # E04 crosses the cool front plenum through a matched sleeve.
    sz=d['speed_z']
    extend('CASE Front barrel',g.cyl((15,S(cr,4),sz),(15,A(R,3),sz),2.6))
    drill('CASE Front barrel',[g.cyl((15,S(cr,6),sz),(15,A(R,5),sz),1.3)])
