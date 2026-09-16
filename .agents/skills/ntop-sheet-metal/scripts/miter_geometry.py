"""Four 45-degree mitered flanges, with an explicit developed solid.

The seam is a physical through-thickness bevel. Flat flanges evaluate the SAME
formed fields under an analytic fold map, retaining the bevel and corner relief.
"""
import math

class Field:
    def __init__(self,r,api,wire,dim=1):self.r,self.api,self.wire,self.dim=r,api,wire,dim
    def other(self,x,dim=None):
        if isinstance(x,Field):return x
        if isinstance(x,self.api.S):return Field(self.r,self.api,x.wire,x.dim)
        return Field(self.r,self.api,self.api.real(x,self.dim if dim is None else dim),self.dim if dim is None else dim)
    def binary(self,x,op):
        x=self.other(x,0 if op in ('multiply','divide') else self.dim)
        dim=self.dim if op not in ('multiply','divide') else self.dim+(x.dim if op=='multiply' else -x.dim)
        return Field(self.r,self.api,self.r.node(op+'<real_field,real_field>','real_field',[self.wire,x.wire]),dim)
    def __add__(self,x):return self.binary(x,'add')
    __radd__=__add__
    def __sub__(self,x):return self.binary(x,'subtract')
    def __rsub__(self,x):return -self+x
    def __mul__(self,x):return self.binary(x,'multiply')
    __rmul__=__mul__
    def __truediv__(self,x):return self.binary(x,'divide')
    def __neg__(self):return self*-1
    def minimum(self,x):return self.binary(x,'min')
    def maximum(self,x):return self.binary(x,'max')
    def unary(self,op,dim=None):return Field(self.r,self.api,self.r.node(op+'<real_field>','real_field',[self.wire]),self.dim if dim is None else dim)
    def abs(self):return self.unary('abs')
    def sqrt(self):return self.unary('sqrt',self.dim//2)
    def named(self,name,section='Calculations'):
        return Field(self.r,self.api,self.r.hold(name,'real_field',self.wire,section),self.dim)

def simpson(fn,a,b,tol=1e-9):
    def part(a,b,fa,fm,fb,whole,tol,depth):
        m=(a+b)/2;l=(a+m)/2;r=(m+b)/2;fl,fr=fn(l),fn(r)
        left=(m-a)*(fa+4*fl+fm)/6;right=(b-m)*(fm+4*fr+fb)/6;delta=left+right-whole
        if depth<=0 or abs(delta)<15*tol:return left+right+delta/15
        return part(a,m,fa,fl,fm,left,tol/2,depth-1)+part(m,b,fm,fr,fb,right,tol/2,depth-1)
    fa,fm,fb=fn(a),fn((a+b)/2),fn(b)
    return part(a,b,fa,fm,fb,(b-a)*(fa+4*fm+fb)/6,tol,22)

def analytic_volumes(A,B,H,t,ri,gap,rr,K,hole_diameter):
    ro=ri+t;delta=gap/math.sqrt(2);rn=ri+K*t
    base=t*(4*A*B-math.pi*rr*rr-4*math.pi*(hole_diameter/2)**2)
    straight=4*(H-ro)*(t*(A+B-2*delta)+(ro*ro-ri*ri))
    bend=4*((A+B-2*delta)*math.pi/4*(ro*ro-ri*ri)+2*(ro**3-ri**3)/3)
    flat_bend=4*rn*((A+B-2*delta)*math.pi/2*t+(ro*ro-ri*ri))
    def removed(q):
        half=math.sqrt(max(0,rr*rr-q*q))
        return max(0,min(q-delta,half)+half)
    breaks=[0,rr]
    disc=2*rr*rr-delta*delta
    if disc>0:breaks += [q for q in ((delta-math.sqrt(disc))/2,(delta+math.sqrt(disc))/2) if 0<q<rr]
    breaks=sorted(breaks)
    def integral(fn):return sum(simpson(fn,a,b) for a,b in zip(breaks,breaks[1:]))
    formed_loss=8*integral(lambda q:removed(q)*(math.sqrt(ro*ro-q*q)-math.sqrt(ri*ri-q*q)))
    flat_loss=8*rn*integral(lambda q:removed(q)*(math.log(ro/ri) if q<1e-12 else math.acosh(ro/q)-math.acosh(ri/q)))
    return {'formed_volume_mm3':base+straight+bend-formed_loss,'flat_volume_mm3':base+straight+flat_bend-flat_loss,'base_volume_mm3':base,'straight_wall_volume_mm3':straight,'formed_bend_volume_mm3':bend-formed_loss,'flat_bend_volume_mm3':flat_bend-flat_loss,'method':'Closed-form flat/straight and annular-strip integrals; adaptive Simpson integration of circular root clipping, 1e-9 mm3 absolute integration target.'}

def enclosure_miter(api):
    r=api.Recipe('enclosure','03 - Enclosure with 45 degree miter seams')
    t,ri,k,ro,rm,ba=api.common(r,1.016,1.5)
    L=r.param('Outside length',152.4);W=r.param('Outside width',101.6);H=r.param('Outside height',50.8)
    gap=r.param('Diagonal seam gap',.5);rr=r.param('Relief root radius',.5);dh=r.param('Mounting hole diameter',3.2)
    assert 0<gap.value/math.sqrt(2)<rr.value<ri.value
    lf=r.named_scalar('Base tangent length',L-2*ro);wf=r.named_scalar('Base tangent width',W-2*ro);h=r.named_scalar('Wall tangent height',H-ro)
    A=lf/2;B=wf/2;delta=r.named_scalar('Miter plane offset',gap/math.sqrt(2));f=r.named_scalar('Blank wing extension',h+ba)
    coords=[]
    for i,axis in enumerate('XYZ'):
        normal=[0,0,0];normal[i]=1
        plane=r.hold(axis+' coordinate plane','plane',r.node('plane_from_normal<point,vector>[1.1.0]','plane',[api.literal_point([0,0,0]),api.vector(normal)]),'Calculations')
        coords.append(Field(r,api,r.hold(axis+' coordinate','real_field',api.ref(plane['ref']['id'],'scalar field'),'Calculations')))
    X,Y,Z=coords;AX=X.abs().named('Absolute X');AY=Y.abs().named('Absolute Y')
    DX=(AX-A).named('Corner X');DY=(AY-B).named('Corner Y')
    root_void=(rr.value*0-(DX*DX+DY*DY).sqrt()+rr).named('Circular root exclusion')
    def bounded(name,field,flat=False):
        low=[-A-f,-B-f,0] if flat else [-L/2,-W/2,0]
        high=[A+f,B+f,t] if flat else [L/2,W/2,H]
        box=r.node('create_bounding_box<point,point>','bounding_box',[r.pt(low),r.pt(high)])
        return r.hold(name,'implicit',r.node('set_bounding_box<implicit,bounding_box>','implicit',[field.wire,box]))
    base_profile=r.profile('Planar floor outline',api.polygon_edges([(-A,-B),(A,-B),(A,B),(-A,B)]),lambda x,y:(x,y,0),(0,0,1))
    base=r.extrude('Floor stock',base_profile,t,(0,0,1))
    basefield=Field(r,api,api.ref(base['ref']['id'],'scalar field')).maximum(root_void)
    base=bounded('Relieved planar floor',basefield)
    formed_parts=[base];flat_parts=[base]
    angle=Field(r,api,{'type':'real','value':{'isFinite':True,'units':{'angle':1},'val':math.pi/2}},0)
    flat_fields=[];formed_fields=[]
    for axis,datum,across,depth,other in [('Y',B,A,L,'X'),('X',A,B,W,'Y')]:
        for sign in [-1,1]:
            name=f'{axis} {sign:+d}'
            edges=api.strip_edges((datum-2*t,t/2),(1,0),[('straight',2*t),('bend',(rm,1)),('straight',h)],t)
            mapping=(lambda q,z,sign=sign:(-L/2,sign*q,z)) if axis=='Y' else (lambda q,z,sign=sign:(sign*q,-W/2,z))
            prof=r.profile(name+' flange section',edges,mapping,(1,0,0) if axis=='Y' else (0,1,0))
            stock=r.extrude(name+' flange stock',prof,depth,(1,0,0) if axis=='Y' else (0,1,0))
            q=(Y*sign-datum) if axis=='Y' else (X*sign-datum)
            cross=AX if axis=='Y' else AY
            trim=((cross-across-q+delta)/math.sqrt(2)).named(name+' 45 degree trim')
            field=Field(r,api,api.ref(stock['ref']['id'],'scalar field')).maximum(trim).maximum(root_void).named(name+' formed field')
            formed_fields.append(field);formed_parts.append(bounded(name+' mitered flange',field))
            s=(Y*sign-datum) if axis=='Y' else (X*sign-datum)
            theta=((s/ba).maximum(0).minimum(1)*angle).named(name+' fold angle')
            radius=-Z+ro
            mapped_q=(radius*theta.unary('sin',0)+s.minimum(0)+datum)*sign
            mapped_z=(-radius*theta.unary('cos',0)+ro+(s-ba).maximum(0)).named(name+' folded height')
            mapped_x=X if axis=='Y' else mapped_q
            mapped_y=mapped_q if axis=='Y' else Y
            flat=Field(r,api,r.node('remap<real_field,real_field,real_field,real_field>','real_field',[field.wire,mapped_x.wire,mapped_y.wire,mapped_z.wire])).maximum(-Z).maximum(Z-t).named(name+' developed field')
            flat_fields.append(flat);flat_parts.append(bounded(name+' developed flange',flat,True))
    joined=r.boolean('union','Mitered enclosure stock',formed_parts)
    flat_joined=r.boolean('union','Developed miter stock',flat_parts)
    holes=[(sx*(A-10),sy*(B-10)) for sx in [-1,1] for sy in [-1,1]]
    formed=r.drill('Formed enclosure',holes,t,dh,joined)
    flat=r.drill('Flat enclosure blank',holes,t,dh,flat_joined)
    r.named_scalar('Flat blank X extent',lf+2*f);r.named_scalar('Flat blank Y extent',wf+2*f)
    a,b=A.value,B.value;tv=t.value;rv=ri.value;rov=ro.value;gv=gap.value;dv=delta.value;rrv=rr.value
    checks=[('floor stock',[0,0,tv/2],'negative'),('floor top',[0,0,tv],'zero'),('floor bottom',[0,0,0],'zero'),('cavity',[0,0,20],'positive'),('long wall',[0,W.value/2-tv/2,25],'negative'),('short wall',[L.value/2-tv/2,0,25],'negative')]
    for i,(x,y) in enumerate(holes):checks.append((f'hole {i}',[x.value,y.value,tv/2],'positive'))
    for degrees in [15,45,75]:
        th=math.radians(degrees)
        for rho,label,ex in [(rv,'inner','zero'),(rm.value,'mid','negative'),(rov,'outer','zero')]:checks.append((f'bend {degrees} {label}',[0,b+rho*math.sin(th),rov-rho*math.cos(th)],ex))
    for sx in [-1,1]:
        for sy in [-1,1]:
            for degrees in [30,60,90]:
                th=math.radians(degrees);q=rm.value*math.sin(th);z=rov-rm.value*math.cos(th) if degrees<90 else 25
                checks.extend([(f'seam {sx} {sy} {degrees} center',[sx*(a+q),sy*(b+q),z],'positive'),(f'seam {sx} {sy} {degrees} Y edge',[sx*(a+q-dv),sy*(b+q),z],'zero'),(f'seam {sx} {sy} {degrees} Y stock',[sx*(a+q-dv-.2),sy*(b+q),z],'negative'),(f'seam {sx} {sy} {degrees} X edge',[sx*(a+q),sy*(b+q-dv),z],'zero')])
            checks.extend([(f'root {sx} {sy} void',[sx*a,sy*b,tv/2],'positive'),(f'root {sx} {sy} edge',[sx*(a-rrv/math.sqrt(2)),sy*(b-rrv/math.sqrt(2)),tv/2],'zero'),(f'root {sx} {sy} stock',[sx*(a-(rrv+.2)/math.sqrt(2)),sy*(b-(rrv+.2)/math.sqrt(2)),tv/2],'negative')])
    for name,p,ex in checks:r.check('CHECK '+name,formed,p,ex)
    analytic=analytic_volumes(a,b,H.value,tv,rv,gv,rrv,k.value,dh.value)
    return r,formed,{'kind':'enclosure','revision':3,'corner_style':'45 degree through-thickness miter','outside_mm':[L.value,W.value,H.value],'thickness_mm':tv,'inside_radius_mm':rv,'seam_gap_mm':gv,'miter_plane_offset_mm':dv,'relief_root_radius_mm':rrv,'hole_diameter_mm':dh.value,'base_tangent_mm':[2*a,2*b],'wall_tangent_mm':h.value,'bend_allowance_mm':ba.value,'bend_deduction_mm':2*rov-ba.value,'flat_extents_mm':[2*(a+f.value),2*(b+f.value)],'analytic_formed_volume_mm3':analytic['formed_volume_mm3'],'flat_volume_mm3':analytic['flat_volume_mm3'],'analytic_integration':analytic,'K':k.value,'bend_count':4,'developed_method':'Native scalar-field evaluation under explicit piecewise analytic fold map; retains through-thickness miter bevels.','flat_requires_bevel_edge_preparation':True}
