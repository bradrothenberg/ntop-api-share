"""Native guide loft plus editable exterior features for the 2022 concept.

All dimensions below are inferred normalized reconstruction controls. They are
not DDG(X) engineering dimensions. The hull length is one metre by convention.
"""
import argparse, json, math
import numpy as np
from recipe import ROOT
from smooth_native import Smooth, SPLINE
from fair_forward_guides import optimize_keel

GREY=[0.58,0.63,0.66,1]
LIGHT=[0.67,0.71,0.73,1]
DARK=[0.19,0.24,0.26,1]
RED=[0.36,0.085,0.075,1]
GLASS=[0.085,0.16,0.19,1]
WHITE=[0.86,0.87,0.84,1]

class Ship(Smooth):
    def __init__(self):
        super().__init__();self.components=[];self.parameters={};self.parameter_refs={}
    def param(self,name,value):
        self.parameters[name]=value
        ref=self.control(name,value,'01 | Reconstruction controls',True);self.parameter_refs[name]=ref;return ref
    def union(self,bodies):
        return self.call('boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]','implicit',self.enum('blend_enum',0),self.length(0),self.list('implicit',bodies))
    def show(self,name,body,color=GREY):
        v=self.var(name,'implicit',body,'06 | Exterior display');self.final[name]=color;self.components.append(v);return v
    def box(self,center,size):
        return self.call('box<point,real,real,real>','box',self.point(center),*[self.length(v) for v in size])
    def cyl(self,a,b,r):
        return self.call('cylinder<point,point,real>','cylinder',self.point(a),self.point(b),self.length(r))
    def sphere(self,p,r):
        return self.call('sphere<point,real>','sphere',self.point(p),self.length(r))
    def smoothstep(self,name,a,b):
        t=self.var(name+' parameter','real_field',self.both(self.real(0),self.either(self.real(1),self.div(self.sub(self.x,self.length(a)),self.length(b-a)))),'03 | Hull loft')
        return self.var(name,'real_field',self.mul(self.mul(self.mul(t,t),t),self.add(self.real(10),self.mul(t,self.add(self.real(-15),self.mul(self.real(6),t))))),'03 | Hull loft')
    def tube(self,name,points,radius):
        curve=self.var(name+' path','polycurve',self.call('polyline<list<point>>[5.20.0]','polycurve',self.list('point',[self.point(p) for p in points])),'05 | Detail paths')
        body=self.var(name+' distance','implicit',self.prop(curve,'scalar field'),'05 | Detail paths')
        return self.call('thicken_implicit<implicit,real_field>','implicit',body,self.length(2*radius))
    def tapered(self,name,x0,x1,w,z0,z1,inset,clip=.18,shift=0):
        """Native plane intersection, chamfered eight-sided deckhouse."""
        height=self.param(name+' height',z1-z0)
        base=self.param(name+' base height',z0)
        q=self.div(self.sub(self.z,base),height)
        left=self.add(self.length(x0),self.mul(q,self.length(inset+shift)))
        right=self.add(self.length(x1),self.mul(q,self.length(-inset+shift)))
        width=self.sub(self.length(w),self.mul(q,self.length(inset)))
        a=self.sub(left,self.x);b=self.sub(self.x,right);c=self.sub(self.ay,width)
        field=self.both(a,b,c,self.add(self.add(a,c),self.length(clip*w)),self.add(self.add(b,c),self.length(clip*w)),self.sub(base,self.z),self.sub(self.z,self.add(base,height)))
        return self.var(name,'implicit',self.bound(field,[x0-.01,-w-.01,z0-.001],[x1+.01,w+.01,z1+.002]),'04 | Superstructure')

def build(detail=True,stem_override=None,aft_blend=.0015):
    r=Ship()
    r.param('Normalized hull length',1)
    rows=[(0,.055,.027,-.008),(.055,.061,.029,-.028),(.16,.064,.031,-.038),(.32,.065,.033,-.042),(.50,.062,.034,-.042),(.64,.054,.035,-.04),(.76,.044,.038,-.034),(.86,.029,.044,-.022),(.94,.014,.049,-.006),(1,.0003,.052,.049)]
    widths=[[a,b] for a,b,c,d in rows];decks=[[a,c] for a,b,c,d in rows];keels=[[a,d] for a,b,c,d in rows]
    fairing=optimize_keel(keels)
    r.config={'guides':{'Hull keel profile':{'control_points':fairing['selected']['control_points']}}}
    width=r.guide('Hull sheer half breadth',widths,n=24)
    deck=r.guide('Hull deck sheer',decks,n=24)
    keel=r.guide('Hull keel profile',keels,n=24)
    rail_rows=[(0,-.008),(.055,-.028),(.16,-.038),(.32,-.042),(.50,-.042),
               (.64,-.040),(.76,-.0375),(.86,-.0358),(.935,-.0342),
               (.961,-.0328),(.975,-.0320),(.984,-.0315),(1,-.031)]
    r.config['guides']['Shared forefoot lower rail']={'fair':True,'penalty':1e-9}
    rail=r.guide('Shared forefoot lower rail',rail_rows,n=32)
    rail_entry=r.smoothstep('Forefoot rail entry',.62,.72)
    stem_return=r.smoothstep('Stem return transition',.90,.985)
    rail_weight=r.var('Forefoot rail weight','real_field',r.mul(rail_entry,r.sub(r.real(1),stem_return)),'03 | Hull loft')
    keel=r.var('Hull keel with shared forefoot','real_field',r.add(keel,r.mul(rail_weight,r.sub(rail,keel))),'03 | Hull loft')
    depth=r.sub(deck,keel)
    space=r.v('Transverse hull coordinates',r.xy(r.ay,r.z),'Coordinates','vector_field_2d')
    profile=[(0,0),(.24,0),(.57,.025),(.78,.15),(.88,.40),(.94,.65),(1,.87),(1,1)]
    forward_profile=[(0,0),(.15,0),(.42,.025),(.66,.15),(.86,.40),(.94,.65),(1,.87),(1,1)]
    t=r.var('Forward section parameter','real_field',r.both(r.real(0),r.either(r.real(1),r.div(r.sub(r.x,r.length(.55)),r.length(.40)))),'03 | Hull loft')
    weight=r.var('Forward section fair transition','real_field',r.mul(r.mul(r.mul(t,t),t),r.add(r.real(10),r.mul(t,r.add(r.real(-15),r.mul(r.real(6),t))))),'03 | Hull loft')
    cps=[]
    for (q,h),(fq,fh) in reversed(list(zip(profile,forward_profile))):
        qf=r.add(r.real(q),r.mul(weight,r.real(fq-q)))
        hf=r.add(r.real(h),r.mul(weight,r.real(fh-h)))
        cps.append(r.xy(r.mul(width,qf),r.add(keel,r.mul(depth,hf))))
    skin=r.var('Continuous hull transverse spline','implicit',r.call(SPLINE,'implicit',r.list('vector_field_2d',cps),r.literal('integer',{'val':3}),space),'03 | Hull loft')
    shape=r.both(skin,r.sub(r.z,deck),r.neg(r.x),r.sub(r.x,r.length(1)))
    main=r.var('Main hull loft','implicit',r.bound(shape,[-.001,-.069,-.046],[1.001,.069,.055]),'03 | Hull loft')
    # The aft sections overlap the forefoot. The original constant-height bulb
    # left a narrow neck beneath the rising keel and a visible union crease.
    bulb_rows=[(.74,.004,-.014,-.026),(.80,.018,-.007,-.0345),
               (.86,.019,.007,-.0355),(.905,.016,.010,-.036),
               (.935,.014,.008,-.035),(.961,.0105,-.010,-.033),
               (.975,.007,-.017,-.031),(.979,.0059,-.0181,-.0299),
               (.984,.0001,-.024,-.0242)]
    bulb_width=r.guide('Bulb breadth',[[x,w] for x,w,t,b in bulb_rows],n=24)
    bulb_top=r.guide('Bulb upper rail',[[x,t] for x,w,t,b in bulb_rows],n=24)
    bulb_tip_lower=r.guide('Bulb tip lower rail',[[x,b] for x,w,t,b in bulb_rows],n=24)
    tip_return=r.smoothstep('Bulb tip rail return',.935,.970)
    bulb_lower=r.var('Bulb shared lower rail','real_field',r.add(rail,r.mul(tip_return,r.sub(bulb_tip_lower,rail))),'03 | Hull loft')
    bulb_center=r.var('Bulb center profile','real_field',r.mul(r.add(bulb_top,bulb_lower),r.real(.5)),'03 | Hull loft')
    bulb_height=r.var('Bulb section height','real_field',r.mul(r.sub(bulb_top,bulb_lower),r.real(.5)),'03 | Hull loft')
    bulb=r.conic_loft('Bulbous bow',bulb_width,bulb_height,bulb_center,bulb_height,
                     .74,.984,[[.74,-.022,-.044],[.985,.022,.014]])
    rounded=r.var('Rounded bulb tip','implicit',r.blend([bulb,r.sphere([.978,0,-.024],.006)],r.length(.0015)),'03 | Hull loft')
    aft_r=r.mul(r.smoothstep('Aft bulb blend',.74,.82),r.length(aft_blend))
    blend_r=r.add(aft_r,r.mul(r.smoothstep('Forward bulb blend',.90,.96),r.length(.009-aft_blend)))
    hull=r.var('Hull with bulbous bow','implicit',r.blend([main,rounded],blend_r),'03 | Hull loft')
    def hullband(name,low,high,color):
        upper=r.sub(deck,r.length(.0006)) if name=='Hull topsides' else r.length(high)
        body=r.both(hull,r.sub(r.length(low),r.z),r.sub(r.z,upper))
        return r.show(name,r.bound(body,[-.001,-.069,max(low,-.046)],[1.001,.069,min(high,.055)]),color)
    hullband('Underwater hull',-.046,-.003,RED)
    hullband('Waterline boot stripe',-.003,.002,DARK)
    hullband('Hull topsides',.002,.056,GREY)
    deckbody=r.both(main,r.sub(r.sub(deck,r.length(.0006)),r.z))
    r.show('Weather deck',r.bound(deckbody,[0,-.068,.025],[1.001,.068,.055]),[.38,.42,.43,1])
    checks=[]
    for name,p,inside in [('hull center',[.50,0,0],True),('hull outside beam',[.50,.09,0],False),('above deck',[.50,0,.06],False),('lower bilge',[.50,.035,-.018],True)]:
        checks.append((name,r.var('CHECK '+name,'real',r.call('evaluate_field<real_field,point>','real',main,r.point(p)),'07 | Verification'),inside,p))
    for name,p,inside in [('bow root lower',[.93,0,-.02],True),
                         ('bow root neck',[.93,0,-.01],True),
                         ('bow root upper',[.93,0,0],True),
                         ('bow tip interior',[.975,0,-.024],True),
                         ('below bulb',[.94,0,-.041],False)]:
        checks.append((name,r.var('CHECK '+name,'real',r.call('evaluate_field<real_field,point>','real',hull,r.point(p)),'07 | Verification'),inside,p))
    # Check the native loft against independent parametric section evaluation.
    from scipy.interpolate import BSpline
    def guide_value(name,x):
        cp=np.asarray(r.guides[name]['control_points']);n=len(cp)
        k=np.r_[np.zeros(4),np.arange(1,n-3)/(n-3),np.ones(4)]
        return float(BSpline(k,cp[:,1],3)(x))
    section_knots=np.r_[np.zeros(4),np.arange(1,5)/5,np.ones(4)]
    for x in [.65,.75,.85,.92]:
        blend_t=np.clip((x-.55)/.40,0,1);weight_host=blend_t**3*(10-15*blend_t+6*blend_t**2)
        net=np.asarray(profile)+(np.asarray(forward_profile)-np.asarray(profile))*weight_host
        q,h=BSpline(section_knots,net,3)(.35)
        w=guide_value('Hull sheer half breadth',x);d=guide_value('Hull deck sheer',x);k=guide_value('Hull keel profile',x)
        smooth=lambda t:np.clip(t,0,1)**3*(10-15*np.clip(t,0,1)+6*np.clip(t,0,1)**2)
        weight_rail=smooth((x-.62)/.10)*(1-smooth((x-.90)/.085))
        k+=weight_rail*(guide_value('Shared forefoot lower rail',x)-k)
        for delta,inside in [(-.001,True),(.001,False)]:
            p=[x,float(w*q+delta),float(k+(d-k)*h)]
            name=f'forward section {x:.2f} '+('inside' if inside else 'outside')
            checks.append((name,r.var('CHECK '+name,'real',r.call('evaluate_field<real_field,point>','real',main,r.point(p)),'07 | Verification'),inside,p))
    if detail:
        aft=r.tapered('Aft hangar block',.10,.28,.055,.03,.080,.007)
        afttower=r.tapered('Aft upper deckhouse',.14,.245,.042,.077,.140,.010)
        fwd=r.tapered('Forward deckhouse',.35,.55,.053,.033,.105,.012,clip=.34)
        bridge=r.tapered('Forward bridge',.426,.56,.048,.046,.071,.003,clip=.30)
        mastbase=r.tapered('Integrated mast tower',.395,.452,.022,.102,.163,.012,clip=.2)
        stack=r.tapered('Forward uptake',.304,.362,.029,.049,.113,.009)
        r.show('Deckhouses',r.union([aft,afttower,fwd,bridge,mastbase,stack]),LIGHT)
        bulwarks=[]
        for s in [-1,1]:
            for lo,hi in [(.25,.345),(.56,.62)]:
                bulwarks.append(r.box([(lo+hi)/2,s*.048,.044],[hi-lo,.002,.021]))
        r.show('Midship bulwarks',r.union(bulwarks),GREY)
        furniture=[]
        for x,y,z in [(.155,.029,.142),(.216,.027,.140),(.382,-.025,.108),(.398,.030,.110),(.49,-.020,.107),(.515,.020,.105)]:
            furniture+=[r.cyl([x,y,z-.004],[x,y,z+.006],.005),r.sphere([x,y,z+.006],.005)]
        for x,y,z in [(.175,-.025,.146),(.211,-.026,.145),(.472,-.026,.113)]:
            furniture+=[r.cyl([x,y,z-.004],[x,y,z+.003],.002),r.cyl([x-.004,y,z+.004],[x+.004,y,z+.004],.004)]
        r.show('External domes and fittings',r.union(furniture),LIGHT)
        # Exterior gun-shaped cover is a visual feature only.
        gun=r.tapered('Foredeck external cover',.65,.684,.012,.036,.056,.003,clip=.35)
        r.show('Foredeck cover',r.union([gun,r.cyl([.666,0,.052],[.712,0,.055],.0013)]),LIGHT)
        masts=[r.cyl([.422,0,.155],[.422,0,.229],.0013)]
        for h,span in [(.18,.033),(.201,.021),(.215,.01)]:
            masts.append(r.cyl([.422,-span/2,h],[.422,span/2,h],.001))
        masts+=[r.cyl([.414,0,.222],[.429,0,.222],.0013),r.cyl([.422,0,.229],[.422,0,.239],.0005)]
        for y in [-.035,.035]:
            masts.append(r.cyl([.178,y,.106],[.173,y,.163],.0005))
        r.show('Masts and yardarms',r.union(masts),DARK)
        windows=[]
        for s in [-1,1]:
            for x in np.linspace(.446,.537,9):
                windows.append(r.box([x,s*.04632,.060],[.007,.0013,.0045]))
            for x in np.linspace(.157,.217,5):
                windows.append(r.box([x,s*.03359,.13],[.009,.0015,.006]))
        for y in np.linspace(-.026,.026,7):
            windows.append(r.box([.55832,y,.060],[.0018,.006,.0045]))
        r.show('Bridge glazing',r.union(windows),GLASS)
        panels=[]
        # Thin octagonal surface patches follow the sloped deckhouse faces.
        q=r.div(r.sub(r.z,r.parameter_refs['Forward deckhouse base height']),r.parameter_refs['Forward deckhouse height'])
        sideface=r.sub(r.length(.053),r.mul(q,r.length(.012)))
        frontface=r.sub(r.length(.55),r.mul(q,r.length(.012)))
        az=r.abs(r.sub(r.z,r.length(.085)))
        for coordinate,face_distance,center in [(r.x,r.sub(r.ay,sideface),.463),(r.y,r.sub(r.x,frontface),0)]:
            ax=r.abs(r.sub(coordinate,r.length(center)))
            shape=r.both(r.sub(ax,r.length(.014)),r.sub(az,r.length(.014)),r.sub(r.add(ax,az),r.length(.022)),r.sub(r.abs(face_distance),r.length(.00045)))
            panels.append(r.bound(shape,[.44,-.06,.07],[.552,.06,.100]))
        for s in [-1,1]:panels.append(r.box([.126,s*.053,.05],[.026,.0008,.020]))
        r.show('Exterior panel faces',r.union(panels),[.50,.55,.59,1])
        gratings=[]
        for x0,x1,y0,y1 in [(.584,.621,-.020,.020),(.277,.302,-.03,.03)]:
            gratings.append(r.box([(x0+x1)/2,0,.036],[x1-x0,y1-y0,.001]))
        r.show('Deck panel backgrounds',r.union(gratings),DARK)
        lids=[]
        for x0,x1,y0,y1,nx,ny in [(.584,.621,-.020,.020,8,8),(.277,.302,-.03,.03,5,10)]:
            dx=(x1-x0)/nx;dy=(y1-y0)/ny
            seed=r.box([x0+dx/2,y0+dy/2,.0366],[dx*.80,dy*.82,.0005])
            spacing=r.literal('vector',{'units':{'length':1},'value':[{'isFinite':True,'val':v} for v in [dx,dy,0]]})
            lids.append(r.call('array_implicit<implicit,vector,vector>[1.1.0]','implicit',seed,r.vec([nx,ny,1]),spacing))
        r.show('Deck panel pattern',r.union(lids),[.74,.77,.78,1])
        exhaust=[]
        for x,y,z in [(.188,-.014,.140),(.188,.004,.140),(.332,-.01,.113),(.332,.008,.113)]:
            exhaust.append(r.cyl([x,y,z-.001],[x,y,z+.0007],.004))
        r.show('Uptake tops',r.union(exhaust),DARK)
        rails=[];posts_a=[];posts_b=[]
        xs=np.linspace(.005,.979,91)
        for s in [-1,1]:
            pts=[]
            for x in xs:
                w=float(np.interp(x,*np.array(widths).T));z=float(np.interp(x,*np.array(decks).T))
                pts.append([float(x),s*(w-.001),z])
                posts_a.append([float(x),s*(w-.001),z]);posts_b.append([float(x),s*(w-.001),z+.006])
            for h in [.003,.006]:rails.append(r.tube(f'Rail {s} {h}',[[a[0],a[1],a[2]+h] for a in pts],.00018))
        postlist=r.var('Guardrail post list','list<cylinder>',r.call('cylinder<point,point,real>','list<cylinder>',r.list('point',[r.point(p) for p in posts_a]),r.list('point',[r.point(p) for p in posts_b]),r.length(.0003)),'05 | Detail paths')
        rails.append(r.call('boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]','implicit',r.enum('blend_enum',0),r.length(0),postlist))
        r.show('Deck guardrails',r.union(rails),LIGHT)
        marks=[]
        def line(a,b,rad=.00042):marks.append(r.cyl(a,b,rad))
        for y in [-.042,.042]:line([.002,y,.0282],[.063,y,.0304])
        for x in [.009,.047]:line([x,-.031,.0306],[x,.031,.0306])
        line([.010,0,.0307],[.063,0,.0307])
        for y in [-.012,.012]:line([.022,y,.0308],[.044,y,.0308],.00065)
        line([.033,-.012,.0308],[.033,.012,.0308],.00065)
        marks.append(r.tube('Aviation circle',[[.033+.021*math.cos(a),.021*math.sin(a),.0307] for a in np.linspace(0,2*math.pi,65)],.00042))
        r.show('Aviation deck markings',r.union(marks),WHITE)
    assembled=r.var('DDGX complete exterior','implicit',r.union(r.components),'08 | Complete model')
    output=r.var('Verification sample values','list<real>',r.list('real',[v for _,v,_,_ in checks]),'07 | Verification')
    stem=stem_override or ('ddgx' if detail else 'pilot')
    r.write(stem,output)
    record={'units':'normalized length ratio; CAD hull length convention 1 m','stations':rows,'transverse_control_net':profile,'evidence_class':'Inferred controls fitted by visual interpretation of one perspective concept; not measured ship offsets','guides':r.guides,'parameters':r.parameters,'variables':len(r.body),'display_bodies':list(r.final),'checks':[{'name':n,'point':p,'expected_inside':i} for n,v,i,p in checks]}
    record['forward_transverse_control_net']=forward_profile
    record['section_transition']={'start_x_L':.55,'end_x_L':.95,'law':'quintic smoothstep; zero first and second derivatives at both ends'}
    record['keel_fairing']=fairing['selected']
    record['shared_forefoot']={'rail_entry_x_L':[.62,.72],'stem_return_x_L':[.90,.985],'bulb_tip_return_x_L':[.935,.970],'aft_blend_radius_L':aft_blend,'aft_blend_transition_x_L':[.74,.82],'forward_blend_radius_L':.009,'blend_transition_x_L':[.90,.96]}
    (ROOT/'output/build'/f'{stem}_geometry.json').write_text(json.dumps(record,indent=2))
    print(json.dumps({'recipe':stem,'variables':len(r.body),'display_bodies':len(r.final)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--stem');a=p.parse_args();build(not a.pilot,a.stem)
