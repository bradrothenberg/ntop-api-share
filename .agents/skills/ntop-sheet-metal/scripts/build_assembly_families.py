"""Reusable native sheet and nominal hardware families for three study assemblies."""
import argparse,json,math
from pathlib import Path
import build_sheet_metal as api
import build_advanced_sheet_metal as a
import build_drafted_sheet_metal as d
ROOT=Path.cwd()/'.local'/'sheet-metal-study'/'assemblies/families'
KEYS=['folded_lid','support_rail','adapter_plate','socket_screw','hex_nut','spacer']
v=a.val

def complete(r,body,t,ri,volume,outside,openings,description):
    body=r.hold('Final '+r.title,'implicit',body)
    return r,body,a.base_meta(t,ri,volume,outside_mm=outside,through_openings=openings,summary=description,source_id='authored-assembly-family',developed_blank=False)

def hexagon(r,name,af,z,height):
    radius=af/math.sqrt(3);edges=api.polygon_edges([(radius*math.cos(i*math.pi/3),radius*math.sin(i*math.pi/3)) for i in range(6)])
    p=r.profile(name+' section',edges,lambda x,y:(x,y,z),(0,0,1))
    return r.extrude(name,p,height,(0,0,1))

def folded_lid():
    r,t,ri,ro,rm=a.basic('folded_lid','Folded enclosure lid',1.2,2)
    L=r.param('Base length',220);W=r.param('Lid width',150);H=r.param('Roof underside height',31.2);gap=r.param('End bend clearance',.5)
    q=L/2+gap;start=(-q-rm,t);steps=[d.S(H-ro),d.B(rm,-90),d.S(2*q),d.B(rm,-90),d.S(H-ro)]
    edges,end=a.strip(start,(0,1),steps,t);p=r.profile('Two bend lid section',edges,lambda x,z:(x,-W/2,z),(0,1,0));body=r.extrude('Lid stock',p,W,(0,1,0));area,_=a.section_integrals(edges);volume=area*v(W)
    # This datum is calculated from the matching 3-degree chassis flange.
    mountY=55+2*2.6*d.SB+d.v(d.wall_leg(30,2.6))*d.CB+8
    body,cut=d.holes(r,body,[(L*.38*s,mountY*sy) for s in [-1,1] for sy in [-1,1]],5,t,H);volume-=cut
    body,cut=d.slots(r,body,[(x,y) for x in [-60,-20,20,60] for y in [-20,20]],18,4,t,H);volume-=cut
    tool=r.hold('Cable entry drill','cylinder',r.node('cylinder<point,point,real>','cylinder',[r.pt([q-1,0,10]),r.pt([q+ro+1,0,10]),api.real(8,1)]))
    body=r.boolean('subtract','Cable entry in lid',[tool],base=body);volume-=math.pi*8**2*v(t)
    for z,label,ex in [(H,'roof lower','zero'),(H+t/2,'roof stock','negative'),(H+t,'roof upper','zero')]:a.check(r,body,label,[0,0,z],ex)
    a.check(r,body,'end entry',[q+rm,0,10],'positive')
    a.check(r,body,'end wall stock',[q+rm,30,10],'negative')
    return complete(r,body,t,ri,volume,[2*v(q+ro),v(W),v(H)],13,'Two free 90-degree press-brake bends; roof mounting and vent openings, end cable port. Vertical end walls are free bends, not a drawn cup.')

def support_rail():
    r,t,ri,ro,rm=a.basic('support_rail','Cable cassette support rail',1.5,1.5)
    L=r.param('Rail length',160);H=r.param('Crown rise',18);crown=r.param('Crown tangent width',18);foot=r.param('Foot tangent',10)
    edgeleg=(15-.6-2.2*(1-d.CB)-.6*d.CB)/d.SB
    mount=r.param('Panel mount half pitch',70-2.2*d.SB-edgeleg*d.CB-.6*d.SB-10)
    half=[d.S(crown/2),d.B(rm,-d.BETA),d.S(d.wall_leg(H,rm)),d.B(rm,d.BETA),d.S(foot)]
    _,end=a.strip((0,-t/2),(1,0),half,t);steps=list(reversed(half))+half
    edges,_=a.strip((-end[0],end[1]),(1,0),steps,t);p=r.profile('Four bend rail section',edges,lambda x,z:(x,-L/2,z),(0,1,0));body=r.extrude('Rail stock',p,L,(0,1,0));area,_=a.section_integrals(edges);volume=area*v(L)
    body,cut=d.holes(r,body,[(0,-mount),(0,mount)],4,t,-t);volume-=cut
    body,cut=d.slots(r,body,[(sign*(end[0]-foot/2),y) for sign in [-1,1] for y in [-55,55]],7,4,t,-H-t);volume-=cut
    for z,label,ex in [(-t,'crown lower','zero'),(-t/2,'crown stock','negative'),(0,'crown top','zero')]:a.check(r,body,label,[0,0,z],ex)
    a.check(r,body,'rail cavity',[0,0,-H/2],'positive')
    return complete(r,body,t,ri,volume,[2*v(end[0]),v(L),v(H+t)],6,'Four 87-degree bends, two crown holes, four foot slots. Crown top is the panel mating datum Z=0.')

def adapter_plate():
    r=api.Recipe('adapter_plate','Raised pod adapter plate');t=r.param('Thickness',1.5);L=r.param('Outside length',210);W=r.param('Outside width',155);rad=r.param('Corner radius',10);bore=r.param('Center opening diameter',100)
    # A rounded rectangle made from exact tangent lines and quarter-circle arcs.
    points=[];edges=[]
    for cx,cy,start in [(L/2-rad,W/2-rad,0),(-L/2+rad,W/2-rad,90),(-L/2+rad,-W/2+rad,180),(L/2-rad,-W/2+rad,270)]:
        angles=[math.radians(start+x) for x in [0,45,90]]
        points.append([(cx+rad*math.cos(q),cy+rad*math.sin(q)) for q in angles])
    for i,pts in enumerate(points):edges.extend([('arc',pts),('line',[pts[-1],points[(i+1)%4][0]])])
    p=r.profile('Rounded perimeter',edges,lambda x,y:(x,y,0),(0,0,1));body=r.extrude('Adapter stock',p,t,(0,0,1));volume=(v(L)*v(W)-(4-math.pi)*v(rad)**2)*v(t)
    body,cut=d.holes(r,body,[(0,0)],bore,t,0,'Center opening');volume-=cut
    body,cut=d.holes(r,body,[(x,sign*(W/2-6)) for x in [-45,0,45] for sign in [-1,1]],4,t,0,'Housing mounts');volume-=cut
    # Compute the flange pattern from the revised analytic cover, not old CAD.
    cover_meta=json.loads((ROOT.parents[1]/'drafted/evidence/annular_cover.design.json').read_text())['metadata']
    bolt=r.param('Cover bolt circle radius',cover_meta['outside_mm'][0]/2-7)
    body,cut=d.holes(r,body,[(bolt*math.cos(i*math.pi/4),bolt*math.sin(i*math.pi/4)) for i in range(8)],5,t,0,'Cover mounts');volume-=cut
    for z,label,ex in [(0,'bottom','zero'),(t/2,'stock','negative'),(t,'top','zero')]:a.check(r,body,label,[90,0,z],ex)
    return complete(r,body,t,0,volume,[v(L),v(W),v(t)],15,'Rounded flat adapter with six housing mounts, eight cover mounts and a central opening. The stand-off gap is open and vented.')

def socket_screw():
    r=api.Recipe('socket_screw','Socket screw envelope');diam=r.param('Shank diameter',4);L=r.param('Under-head length',8);hd=r.param('Head diameter',7);H=r.param('Head height',3);af=r.param('Socket across flats',2.5)
    shank=a.hole(r,'Smooth shank',0,0,diam,-L,H*.1);head=a.hole(r,'Head',0,0,hd,0,H);body=r.boolean('union','Screw stock',[shank,head])
    socket=hexagon(r,'Blind hex socket',af,H*.45,H);body=r.boolean('subtract','Recessed screw',[socket],base=body)
    volume=math.pi*(v(diam)/2)**2*v(L)+math.pi*(v(hd)/2)**2*v(H)-math.sqrt(3)/2*v(af)**2*v(H)*.55
    for p,label,ex in [([0,0,-L/2],'shank stock','negative'),([diam/2,0,-L/2],'shank radius','zero'),([0,0,H*.8],'socket void','positive'),([hd*.4,0,H*.5],'head stock','negative')]:a.check(r,body,label,p,ex)
    return complete(r,body,0,0,volume,[v(hd),v(hd),v(L+H)],0,'Nominal smooth shank/head envelope with blind hex socket; no helical threads or engagement-strength model.')

def hex_nut():
    r=api.Recipe('hex_nut','Hex nut envelope');D=r.param('Nominal diameter',4);af=r.param('Across flats',7);H=r.param('Height',3.2)
    body=hexagon(r,'Hex stock',af,-H,H);body,cut=d.holes(r,body,[(0,0)],D+.2,H,-H,'Smooth bore');volume=math.sqrt(3)/2*v(af)**2*v(H)-cut
    a.check(r,body,'bore',[0,0,-H/2],'positive');a.check(r,body,'ring stock',[(D+.2+af)/4,0,-H/2],'negative');a.check(r,body,'top face',[(D+.2+af)/4,0,0],'zero')
    return complete(r,body,0,0,volume,[2*v(af)/math.sqrt(3),v(af),v(H)],1,'Nominal hex nut with smooth diameter +0.2 mm bore. Top face is its assembly mating datum.')

def spacer():
    r=api.Recipe('spacer','Tubular stand-off');OD=r.param('Outside diameter',7);ID=r.param('Bore diameter',3.5);H=r.param('Height',6)
    body=a.hole(r,'Tube stock',0,0,OD,0,H);body,cut=d.holes(r,body,[(0,0)],ID,H,0,'Tube bore');volume=math.pi*(v(OD)/2)**2*v(H)-cut
    a.check(r,body,'tube bore',[0,0,H/2],'positive');a.check(r,body,'tube wall',[(OD+ID)/4,0,H/2],'negative');a.check(r,body,'top face',[(OD+ID)/4,0,H],'zero')
    return complete(r,body,0,0,volume,[v(OD),v(OD),v(H)],1,'Plain hollow spacer, with native height input shared by all six identical placements.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',default='all');p.add_argument('--out',type=Path,default=ROOT);args=p.parse_args();ROOT=args.out.resolve();api.ROOT=ROOT
    for folder in ['models','evidence','inputs','reports/assets','.local']:(ROOT/folder).mkdir(parents=True,exist_ok=True)
    records=[api.write_case(*globals()[key]()) for key in KEYS if args.case=='all' or key in args.case.split(',')]
    (ROOT/'evidence/design-summary.json').write_text(json.dumps(records,indent=2));print([(x['case'],x['nodes'],x['checks']) for x in records])
