"""Study 04: 3-degree drafted compound sheet-metal geometry, exact normal offsets.

Dimensions are authored study choices. Fixed feature counts and angles are
builder choices; dimensions are named native inputs. No forming solver.
"""
import argparse,json,math
from pathlib import Path
import build_sheet_metal as api
import build_advanced_sheet_metal as a
from miter_geometry import Field
ROOT=Path.cwd()/'.local'/'sheet-metal-study'/'drafted'
KEYS=['vent_chassis','beaded_crossmember','stepped_housing','annular_cover','corrugated_shield','cable_panel']
LABELS={'vent_chassis':'Return-flange ventilation chassis','beaded_crossmember':'Beaded joggle crossmember','stepped_housing':'Stepped drawn housing','annular_cover':'Collared annular cover','corrugated_shield':'Corrugated mounting shield','cable_panel':'Bridge-lance cable panel'}
v=a.val
DRAFT=3.0
BETA=90-DRAFT
SB=math.sin(math.radians(BETA))
CB=math.cos(math.radians(BETA))
def wall_leg(height,rm):return (height-2*rm*(1-CB))/SB

def S(length):return ('straight',length)
def B(radius,angle):return ('bend',(radius,angle))
def coords(r):
    # Compound features share one native coordinate-field set. Reusing a name
    # by authoring a second variable with that ID fails Notebook API import.
    if not hasattr(r,'_complex_coords'):
        r._complex_coords=r._cut_coords if hasattr(r,'_cut_coords') else a.coords(r)
        r._cut_coords=r._complex_coords
    return r._complex_coords
def anim_chain(start,tangent,steps,t):
    return {'start':a.pair(start),'start_angle':math.degrees(math.atan2(tangent[1],tangent[0])),'steps':[(v(q),0) if k=='straight' else (v(q[0])*abs(math.radians(q[1])),q[1]) for k,q in steps],'thickness':v(t)}
def profile_samples(start,tangent,steps):
    p=a.pair(start);u=tangent;out=[]
    for kind,q in steps:
        if kind=='straight':
            length=v(q);out.append((api.addv(p,u,length/2),u,'tangent'));p=api.addv(p,u,length)
        else:
            r,deg=q;r=v(r);alpha=math.radians(deg);sgn=1 if alpha>0 else -1
            center=api.addv(p,api.left(u),r*sgn);mid_u=a.turn(u,alpha/2);u=a.turn(u,alpha)
            out.append((api.addv(center,api.left(mid_u),-r*sgn),mid_u,'bend'));p=api.addv(center,api.left(u),-r*sgn)
    return out
def probe_section(r,body,start,tangent,steps,t,L):
    for i,(p,u,kind) in enumerate(profile_samples(start,tangent,steps)):
        if kind!='bend' and i%3:continue
        for d,label,ex in [(-v(t)/2,'face A','zero'),(0,'stock','negative'),(v(t)/2,'face B','zero')]:
            y,z=api.addv(p,api.left(u),d);a.check(r,body,f'section {i} {label}',[-v(L)/2+3,y,z],ex)
def extruded(r,name,start,tangent,steps,t,L):
    edges,end=a.strip(start,tangent,steps,t)
    profile=r.profile(name+' section',edges,lambda y,z:(-L/2,y,z),(1,0,0))
    body=r.extrude(name,profile,L,(1,0,0));area,_=a.section_integrals(edges)
    r.motion={'kind':'section','chain':anim_chain(start,tangent,steps,t),'length':v(L),'features':[]}
    return body,area*v(L),end,(start,tangent,steps)
def symmetric(r,name,start,half,t,L):
    _,end=a.strip(start,(1,0),half,t);angle=sum(q[1] for kind,q in half if kind=='bend')
    u=(math.cos(math.radians(angle)),-math.sin(math.radians(angle)))
    body,vol,_,check=extruded(r,name,(-end[0],end[1]),u,list(reversed(half))+half,t,L)
    r.motion={'kind':'symmetric','chain':anim_chain(start,(1,0),half,t),'length':v(L),'features':[]}
    return body,vol,end,check
def holes(r,base,points,diam,t,z,name='Mount'):
    tools=[]
    for i,(x,y) in enumerate(points):tools.append(a.hole(r,f'{name} {i}',x,y,diam,z-t,z+2*t))
    body=r.boolean('subtract',name+' pierced stock',tools,base=base)
    for i,(x,y) in enumerate(points):a.check(r,body,f'{name} void {i}',[x,y,z+t/2],'positive')
    return body,len(points)*math.pi*(v(diam)/2)**2*v(t)
def slots(r,base,points,length,width,t,z):
    tools=[a.slot(r,f'Mount slot {i}',x,y,length,width,z-t,z+2*t) for i,(x,y) in enumerate(points)]
    body=r.boolean('subtract','Slotted stock',tools,base=base)
    for i,(x,y) in enumerate(points):a.check(r,body,f'slot void {i}',[x,y,z+t/2],'positive')
    return body,len(points)*((v(length)-v(width))*v(width)+math.pi*(v(width)/2)**2)*v(t)
def beads(r,base,centers,straight,top,H,t,rm,z=0):
    steps=[S(top),B(rm,-BETA),S(wall_leg(H,rm)),B(rm,BETA),S(3*t)]
    # For the elevated t=1.5 mm bead, build 42926's CAD Revolve produced wrong
    # cavity/far-field signs. Use an extruded analytic meridian as a 2D field,
    # then map it radially. Clamp only within the known flat crown to avoid
    # the meridian's artificial cap at rho=0. This retains the same zero set.
    local_z=0 if v(z)!=0 else z
    edges,end=a.strip((0,local_z+H+t/2),(1,0),steps,t);rend=end[0];root=rend-3*t
    if v(z)!=0:
        profile=r.profile('Closed bead master meridian',edges,lambda rad,zz:(rad,-20,zz),(0,1,0))
        master=r.extrude('Closed bead master',profile,40,(0,1,0))
    else:master=a.revolve(r,'Closed bead master',edges)
    X,Y,Z=coords(r);cuts=[];patch=[]
    bead_Z=Z-z if v(z)!=0 else Z
    for i,(cx,cy) in enumerate(centers):
        dx=((X-cx).abs()-straight/2).maximum(0);dy=Y-cy;rho=(dx*dx+dy*dy).sqrt()
        cuts.append(a.bound(r,f'Bead floor opening {i}',rho-(root+t/2),[cx-straight/2-rend,cy-rend,z-t],[cx+straight/2+rend,cy+rend,z+2*t]))
        mapped_rho=rho.maximum(top/2) if v(z)!=0 else rho
        patch.append(a.mapped(r,f'Closed bead {i}',master,mapped_rho,bead_Z,[cx-straight/2-rend,cy-rend,z],[cx+straight/2+rend,cy+rend,z+H+t]))
    opened=r.boolean('subtract','Opened bead stock',cuts,base=base);body=r.boolean('union','Beaded stock',[opened,*patch])
    area,moment=a.section_integrals(edges);delta=2*math.pi*moment+2*area*v(straight)-(math.pi*v(rend)**2+2*v(rend)*v(straight))*v(t)
    for i,(cx,cy) in enumerate(centers):
        for zz,label,ex in [(z+H,'underside','zero'),(z+H+t/2,'stock','negative'),(z+H+t,'top','zero'),(z+H/2,'cavity','positive')]:a.check(r,body,f'bead {i} {label}',[cx,cy,zz],ex)
        a.check(r,body,f'bead {i} closed end',[cx+straight/2+top/2,cy,z+H+t/2],'negative')
    r.motion['features'].append({'kind':'beads','centers':[a.pair(c) for c in centers],'straight':v(straight),'chain':anim_chain((0,z+H+t/2),(1,0),steps,t),'support':[v(rend),v(rend)+3]})
    return body,len(centers)*delta
def dimples(r,base,centers,rh,H,t,rm,z=0):
    lip=r.param('Dimple lip width',1.5);alpha=math.pi/4;leg=(H-2*rm*(1-math.cos(alpha)))/math.sin(alpha)
    steps=[S(lip),B(rm,45),S(leg),B(rm,-45),S(3*t)]
    edges,end=a.strip((rh,z+t/2-H),(1,0),steps,t);rend=end[0];root=rend-3*t
    master=a.revolve(r,'Dimple master',edges);X,Y,Z=coords(r);cuts=[];patch=[]
    for i,(cx,cy) in enumerate(centers):
        dx=X-cx;dy=Y-cy;rho=(dx*dx+dy*dy).sqrt();cr=root+t/2
        cuts.append(a.bound(r,f'Dimple opening {i}',rho-cr,[cx-cr,cy-cr,z-t],[cx+cr,cy+cr,z+2*t]))
        patch.append(a.mapped(r,f'Dimple {i}',master,rho,Z,[cx-rend,cy-rend,z-H],[cx+rend,cy+rend,z+t]))
    opened=r.boolean('subtract','Dimple openings',cuts,base=base);body=r.boolean('union','Dimpled stock',[opened,*patch]);_,moment=a.section_integrals(edges)
    delta=2*math.pi*moment-math.pi*v(rend)**2*v(t)
    for i,(cx,cy) in enumerate(centers):
        a.check(r,body,f'dimple {i} bore',[cx,cy,z-H+t/2],'positive')
        for zz,label,ex in [(z-H,'underside','zero'),(z-H+t/2,'lip','negative'),(z-H+t,'top','zero')]:a.check(r,body,f'dimple {i} {label}',[cx+rh+lip/2,cy,zz],ex)
    r.motion['features'].append({'kind':'dimples','centers':[a.pair(c) for c in centers],'chain':anim_chain((rh,z+t/2-H),(1,0),steps,t),'support':[v(rend),v(rend)+4]})
    return body,len(centers)*delta
def louvers(r,base,centers,span,leg,t,rm):
    gap=r.param('Lance clearance',.4);opening=rm*(math.pi/6)+leg+gap;cuts=[];patches=[]
    steps=[S(2*t),B(rm,30),S(leg)]
    edges,end=a.strip((-2*t,t/2),(1,0),steps,t);area,_=a.section_integrals(edges)
    for i,(x,y) in enumerate(centers):
        cuts.append(a.rect_cut(r,f'Lance opening {i}',x-span/2-gap,x+span/2+gap,y,y+opening,-t,2*t))
        p=r.profile(f'Louver {i} section',edges,lambda q,z,x=x,y=y:(x-span/2,y+q,z),(1,0,0));patches.append(r.extrude(f'Louver {i}',p,span,(1,0,0)))
    opened=r.boolean('subtract','Lanced stock',cuts,base=base);body=r.boolean('union','Louvered stock',[opened,*patches])
    for i,(x,y) in enumerate(centers):
        q=rm*.5+leg*.55*math.cos(math.pi/6);z=t/2+rm*(1-math.cos(math.pi/6))+leg*.55*.5
        a.check(r,body,f'louver {i} stock',[x,y+q,z],'negative');a.check(r,body,f'louver {i} airflow',[x,y+q,z/2],'positive')
        for sign in [-1,1]:a.check(r,body,f'louver {i} face {sign}',[x,y+q-sign*t*.25,z+sign*t/2*math.cos(math.pi/6)],'zero')
    r.motion['features'].append({'kind':'louvers','centers':[a.pair(c) for c in centers],'span':v(span),'chain':anim_chain((-2*t,t/2),(1,0),steps,t)})
    return body,len(centers)*((area-2*v(t)**2)*v(span)-(v(span)+2*v(gap))*v(opening)*v(t))
def finish(r,body,volume,t,ri,outside,holes,summary,source):
    body=r.hold('Final '+LABELS[r.key],'implicit',body)
    meta=a.base_meta(t,ri,volume,outside_mm=outside,through_openings=holes,summary=summary,source_id=source,developed_blank=False,motion=r.motion)
    meta['revision']='draft-and-release-r1'
    meta['formed_wall_draft_deg']=30.0 if r.key=='corrugated_shield' else DRAFT
    meta['draft_scope']='Formerly vertical formed straight walls and closed-bead flanks; exact normal thickness. Existing 30/45-degree features retained. Cut edges and bend tangent transitions are not minimum-draft walls.'
    meta['tool_access_limit']={
      'vent_chassis':'Downturned returns require separate bending operations or segmented access; vertical envelope tools do not contact the undercut interiors.',
      'beaded_crossmember':'Closed beads require draw/material-flow assessment; geometric draft does not qualify strain or springback.',
      'stepped_housing':'Two draw levels and floor beads need draw sequence, blank-holder and material-flow assessment.',
      'annular_cover':'Neck opens toward +Z; outer skirt opens toward -Z. Opposed envelope release does not qualify the neck forming sequence.',
      'corrugated_shield':'Existing walls are 30 degrees off vertical. Rebuilt identical CAD; new release-envelope tools and animation.',
      'cable_panel':'Two-ended bridge tunnels require separate lance/form tooling and tool access; vertical envelopes do not reproduce tunnel contact faces.'}[r.key]
    # Native probe points on each drafted straight flank at two separated stations.
    chain=r.motion['chain'];start=chain['start'];angle=math.radians(chain.get('start_angle',0));u=(math.cos(angle),math.sin(angle));point=start
    drafted=[]
    for idx,(length,deg) in enumerate(chain['steps']):
        if deg:
            radius=length/abs(math.radians(deg));sgn=1 if deg>0 else -1;center=api.addv(point,api.left(u),radius*sgn);u=a.turn(u,math.radians(deg));point=api.addv(center,api.left(u),-radius*sgn)
        else:
            actual=math.degrees(math.atan2(abs(u[0]),abs(u[1])))
            if abs(actual-DRAFT)<1e-7:
                stations=[]
                for frac in [.25,.75]:
                    q=api.addv(point,u,length*frac);stations.append(q)
                    for sign in [-1,0,1]:
                        qface=api.addv(q,api.left(u),sign*v(t)/2)
                        if r.motion['kind'] in ['section','symmetric']:xyz=[-outside[0]/2+2,qface[0],qface[1]]
                        elif r.motion['kind']=='rounded':xyz=[r.motion['core'][0]+qface[0],0,qface[1]]
                        else:xyz=[qface[0],0,qface[1]]
                        a.check(r,body,f'draft flank {idx} station {frac} face {sign}',xyz,'negative' if sign==0 else 'zero')
                drafted.append({'segment':idx,'angle_from_vertical_deg':actual,'midsurface_stations_mm':stations,'normal_thickness_mm':v(t)})
            point=api.addv(point,u,length)
    meta['drafted_parent_flanks']=drafted
    return r,body,meta

def vent_chassis():
    r,t,ri,ro,rm=a.basic('vent_chassis',LABELS['vent_chassis'],1.2,2)
    L=r.param('Length',220);floor=r.param('Floor tangent width',110);H=r.param('Flange rise',30);flange=r.param('Mounting flange tangent',16);ret=r.param('Return tangent',7)
    half=[S(floor/2),B(rm,BETA),S(wall_leg(H,rm)),B(rm,-BETA),S(flange),B(rm,-BETA),S(ret)]
    body,volume,end,profile=symmetric(r,'Chassis stock',(0,t/2),half,t,L)
    probe_section(r,body,*profile,t,L)
    span=r.param('Louver span',58);leg=r.param('Louver tangent',12)
    body,dv=louvers(r,body,[(L*s/4,floor*y) for s in [-1,1] for y in [-.34,-.09,.16]],span,leg,t,rm);volume+=dv
    dh=r.param('Mount hole diameter',5);body,dv=holes(r,body,[(L*.38*s,(floor/2+2*rm*SB+wall_leg(H,rm)*CB+flange/2)*sy) for s in [-1,1] for sy in [-1,1]],dh,t,H);volume-=dv
    return finish(r,body,volume,t,ri,[v(L),2*v(end[0])+v(t)*SB,v(H+t)],10,'Six perimeter bends combine mounting ledges, downturned returns and six 30-degree lanced vents.','protolabs-forms')

def beaded_crossmember():
    r,t,ri,ro,rm=a.basic('beaded_crossmember',LABELS['beaded_crossmember'],1.5,2)
    L=r.param('Length',240);H=r.param('Crown rise',28);crown=r.param('Crown tangent width',52);foot=r.param('Inner foot tangent',20);offset=r.param('Foot joggle rise',4);tip=r.param('Outer foot tangent',12)
    leg=(offset-2*rm*(1-math.cos(math.pi/4)))/math.sin(math.pi/4)
    half=[S(crown/2),B(rm,-BETA),S(wall_leg(H,rm)),B(rm,BETA),S(foot),B(rm,45),S(leg),B(rm,-45),S(tip)]
    body,volume,end,profile=symmetric(r,'Joggled rail stock',(0,H+t/2),half,t,L);probe_section(r,body,*profile,t,L)
    bh=r.param('Bead rise',6);br=r.param('Bead midsurface radius',2.25);bt=r.param('Bead crown half width',3);bl=r.param('Bead straight length',110)
    body,dv=beads(r,body,[(0,-crown*.23),(0,crown*.23)],bl,bt,bh,t,br,H);volume+=dv
    sl=r.param('Slot length',16);sw=r.param('Slot width',5);body,dv=slots(r,body,[(L*.30*s,(end[0]-tip/2)*sy) for s in [-1,1] for sy in [-1,1]],sl,sw,t,offset);volume-=dv
    dh=r.param('Crown hole diameter',8);body,dv=holes(r,body,[(-L*.42,0),(L*.42,0)],dh,t,H);volume-=dv
    return finish(r,body,volume,t,ri,[v(L),2*v(end[0]),v(H+bh+t)],6,'Eight bends create raised outer feet; two closed beads stiffen the broad crown geometrically.','mate-forms')

def stepped_housing():
    r,t,ri,ro,rm=a.basic('stepped_housing',LABELS['stepped_housing'],1.2,2)
    L=r.param('Outside length',210);W=r.param('Outside width',155);h1=r.param('First step rise',10);h2=r.param('Second step rise',24);fr=r.param('Floor plan radius',10);shelf=r.param('Intermediate shelf tangent',12);flange=r.param('Flange tangent',12)
    steps=[S(fr),B(rm,BETA),S(wall_leg(h1,rm)),B(rm,-BETA),S(shelf),B(rm,BETA),S(wall_leg(h2,rm)),B(rm,-BETA),S(flange)]
    edges,end=a.strip((0,t/2),(1,0),steps,t);rend=end[0];A=r.named_scalar('Core half length',L/2-rend);Bcore=r.named_scalar('Core half width',W/2-rend);H=h1+h2
    master=a.revolve(r,'Two-level meridian',edges);X,Y,Z=coords(r);dx=(X.abs()-A).maximum(0);dy=(Y.abs()-Bcore).maximum(0);rho=(dx*dx+dy*dy).sqrt()
    body=a.mapped(r,'Stepped housing stock',master,rho,Z,[-L/2,-W/2,0],[L/2,W/2,H+t]);area,moment=a.section_integrals(edges);volume=4*v(A)*v(Bcore)*v(t)+4*(v(A)+v(Bcore))*area+2*math.pi*moment
    r.motion={'kind':'rounded','core':[v(A),v(Bcore)],'chain':anim_chain((0,t/2),(1,0),steps,t),'features':[]}
    for i,(p,u,kind) in enumerate(profile_samples((0,t/2),(1,0),steps)):
        for d,label,ex in [(-v(t)/2,'bottom','zero'),(0,'stock','negative'),(v(t)/2,'top','zero')]:
            rr,z=api.addv(p,api.left(u),d);a.check(r,body,f'meridian {i} {label}',[A+rr/math.sqrt(2),Bcore+rr/math.sqrt(2),z],ex)
    bh=r.param('Floor bead rise',6);bt=r.param('Bead crown half width',3);bl=r.param('Bead straight length',80)
    body,dv=beads(r,body,[(0,-24),(0,0),(0,24)],bl,bt,bh,t,rm);volume+=dv
    sl=r.param('Slot length',12);sw=r.param('Slot width',4);body,dv=slots(r,body,[(x,(W/2-flange/2)*sy) for x in [-45,0,45] for sy in [-1,1]],sl,sw,t,H);volume-=dv
    return finish(r,body,volume,t,ri,[v(L),v(W),v(H+t)],6,'Two continuous rounded wall levels, a mounting flange, three hollow floor beads and six slots.','beckwood-drawing')

def annular_cover():
    r,t,ri,ro,rm=a.basic('annular_cover',LABELS['annular_cover'],1.2,1.6)
    rh=r.param('Neck midsurface radius',12);neck=r.param('Neck tangent height',8);deck=r.param('Upper deck tangent',18);drop=r.param('Cone drop',8);shelf=r.param('Shoulder shelf tangent',8);lower=r.param('Lower wall drop',12);flange=r.param('Flange tangent',14)
    H=drop+lower;start=(rh,H+rm*(1+CB)+neck+t/2);tangent=(-CB,-SB);leg=(drop-2*rm*(1-math.cos(math.pi/4)))/math.sin(math.pi/4)
    steps=[S(neck/SB),B(rm,90+DRAFT),S(deck),B(rm,-45),S(leg),B(rm,45),S(shelf),B(rm,-BETA),S(wall_leg(lower,rm)),B(rm,BETA),S(flange)]
    edges,end=a.strip(start,tangent,steps,t);body=a.revolve(r,'Collared cover stock',edges);_,moment=a.section_integrals(edges);volume=2*math.pi*moment
    r.motion={'kind':'round','chain':anim_chain(start,tangent,steps,t),'features':[]}
    for i,(p,u,kind) in enumerate(profile_samples(start,tangent,steps)):
        for d,label,ex in [(-v(t)/2,'face A','zero'),(0,'stock','negative'),(v(t)/2,'face B','zero')]:
            rr,z=api.addv(p,api.left(u),d);a.check(r,body,f'cover profile {i} {label}',[rr,0,z],ex)
    dh=r.param('Flange hole diameter',5);boltR=end[0]-flange/2;points=[(boltR*math.cos(i*math.pi/4),boltR*math.sin(i*math.pi/4)) for i in range(8)]
    body,dv=holes(r,body,points,dh,t,0);volume-=dv
    dh2=r.param('Upper deck hole diameter',4);pr=rh-neck*CB/SB+rm*SB+deck/2
    body,dv=holes(r,body,[(pr*math.cos(math.pi/4+i*math.pi/2),pr*math.sin(math.pi/4+i*math.pi/2)) for i in range(4)],dh2,t,H,'Upper deck');volume-=dv
    a.check(r,body,'central neck bore',[0,0,v(start[1])-2],'positive')
    return finish(r,body,volume,t,ri,[2*v(end[0]),2*v(end[0]),v(start[1]+t/2*CB)],13,'An integral upright neck joins two stepped annular decks, a 45-degree cone, and a pierced outer flange.','mate-forms')

def corrugated_shield():
    r,t,ri,ro,rm=a.basic('corrugated_shield',LABELS['corrugated_shield'],1.2,1.6)
    L=r.param('Length',200);foot=r.param('Foot tangent',14);slope=r.param('Slope tangent',6);crest=r.param('Crest tangent',6);valley=r.param('Valley tangent',6)
    cycle=[B(rm,60),S(slope),B(rm,-60),S(crest),B(rm,-60),S(slope),B(rm,60)]
    steps=[S(foot)]
    for i in range(5):steps+=cycle+([S(valley)] if i<4 else [])
    steps+=[S(foot)];_,end0=a.strip((0,t/2),(1,0),steps,t);W=end0[0]
    body,volume,end,profile=extruded(r,'Corrugated stock',(-W/2,t/2),(1,0),steps,t,L);probe_section(r,body,*profile,t,L)
    sl=r.param('Slot length',16);sw=r.param('Slot width',5);body,dv=slots(r,body,[(x,(W/2-foot/2)*sy) for x in [-70,0,70] for sy in [-1,1]],sl,sw,t,0);volume-=dv
    cycleWidth=4*rm*math.sin(math.pi/3)+2*slope*math.cos(math.pi/3)+crest;rise=2*rm*(1-math.cos(math.pi/3))+slope*math.sin(math.pi/3)
    dh=r.param('Crest hole diameter',4);points=[(0,-W/2+foot+cycleWidth/2+i*(cycleWidth+valley)) for i in range(5)]
    body,dv=holes(r,body,points,dh,t,rise,'Crest');volume-=dv
    return finish(r,body,volume,t,ri,[v(L),v(W),v(rise+t)],11,'Five trapezoidal corrugations use twenty 60-degree circular bends, with pierced crests and mounting feet.','mate-ribs')

def cable_panel():
    r,t,ri,ro,rm=a.basic('cable_panel',LABELS['cable_panel'],1.2,1.6)
    L=r.param('Length',200);W=r.param('Outside width',140);H=r.param('Edge flange height',15);edgeleg=(H-t/2-rm*(1-CB)-t/2*CB)/SB;floor=W/2-rm*SB-edgeleg*CB-t/2*SB
    half=[S(floor),B(rm,BETA),S(edgeleg)]
    body,volume,end,profile=symmetric(r,'Cable panel stock',(0,t/2),half,t,L);probe_section(r,body,*profile,t,L)
    bh=r.param('Bridge rise',6);top=r.param('Bridge crown tangent',10);span=r.param('Bridge span',10);gap=r.param('Bridge clearance',.4);leg=(bh-2*rm*(1-math.cos(math.pi/4)))/math.sin(math.pi/4)
    steps=[S(2*t),B(rm,45),S(leg),B(rm,-45),S(top),B(rm,-45),S(leg),B(rm,45),S(2*t)]
    edges,bendend=a.strip((-2*t,t/2),(1,0),steps,t);opening=bendend[0]-2*t;area,_=a.section_integrals(edges);cuts=[];patch=[];centers=[]
    for i,(cx,cy) in enumerate([(x,y) for x in [-50,50] for y in [-38,38]]):
        y=cy-opening/2;centers.append((cx,y))
        cuts.append(a.rect_cut(r,f'Bridge window {i}',cx-span/2-gap,cx+span/2+gap,y,y+opening,-t,2*t))
        p=r.profile(f'Bridge {i} section',edges,lambda q,z,cx=cx,y=y:(cx-span/2,y+q,z),(1,0,0));patch.append(r.extrude(f'Bridge {i}',p,span,(1,0,0)))
    opened=r.boolean('subtract','Bridge windows',cuts,base=body);body=r.boolean('union','Bridged panel',[opened,*patch]);volume+=4*((area-4*v(t)**2)*v(span)-(v(span)+2*v(gap))*v(opening)*v(t))
    for i,(cx,y) in enumerate(centers):
        a.check(r,body,f'bridge {i} crown',[cx,y+opening/2,bh+t/2],'negative');a.check(r,body,f'bridge {i} tunnel',[cx,y+opening/2,bh/2],'positive')
        for z,label in [(bh,'underside'),(bh+t,'top')]:a.check(r,body,f'bridge {i} {label}',[cx,y+opening/2,z],'zero')
    r.motion['features'].append({'kind':'bridges','centers':[a.pair(c) for c in centers],'span':v(span),'opening':v(opening),'chain':anim_chain((-2*t,t/2),(1,0),steps,t)})
    rh=r.param('Cable port radius',6);dep=r.param('Cable dimple depth',3)
    body,dv=dimples(r,body,[(-50,0),(0,0),(50,0)],rh,dep,t,rm);volume+=dv
    dh=r.param('Mounting hole diameter',4);body,dv=holes(r,body,[(sx*(L/2-10),sy*(floor-10)) for sx in [-1,1] for sy in [-1,1]],dh,t,0);volume-=dv
    return finish(r,body,volume,t,ri,[v(L),v(W),v(H+dep)],15,'Four two-ended 45-degree bridges, three pierced cable dimples, edge flanges and mounting holes share one sheet.','mate-bridges')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',default='all',choices=['all',*KEYS]);ap.add_argument('--out',type=Path,default=ROOT);args=ap.parse_args();api.ROOT=args.out.resolve()
    for folder in ['models','evidence','inputs','reports/assets','.local','share']:(api.ROOT/folder).mkdir(parents=True,exist_ok=True)
    records=[]
    for key in KEYS if args.case=='all' else [args.case]:
        r,body,meta=globals()[key]();records.append(api.write_case(r,body,meta))
    (api.ROOT/'evidence/design-summary.json').write_text(json.dumps(records,indent=2));print(json.dumps([{'case':x['case'],'nodes':x['nodes'],'checks':x['checks']} for x in records]))
if __name__=='__main__':main()
