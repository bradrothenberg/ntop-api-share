"""Host-rendered forming illustrations derived from the evaluated native meshes.

Unbend an analytic midsurface chain, preserving its segment lengths and each
vertex's local normal offset. Closed ends change circumferential length. This
is prescribed geometry, NOT a material/contact/strain or springback solver.
The final state retains every native vertex and triangle without modification.
"""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import trimesh
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

ROOT=Path.cwd()/'.local'/'sheet-metal-study'/'advanced'
KEYS=['mounting_hat','louver_panel','bead_panel','dimple_plate','drawn_tray']
TITLES=['Slotted mounting rail','Louvered panel','Closed bead panel','Dimpled mounting plate','Continuous drawn tray']
SUBTITLES=['Four circular bends / slotted feet / pierced crown','Six lanced flaps / 30 degree forms / edge flanges','Three closed beads / rounded ends / hollow underside','Six pierced dimples / 45 degree cones / rounded roots','Continuous corners / floor and rim bends / slotted flange']
BLUE='#248AFF';INK='#193048';BG='#f2f5f8'
OUT=ROOT/'share'

def turn(u,a):
    c,s=np.cos(a),np.sin(a)
    return np.array([c*u[0]-s*u[1],s*u[0]+c*u[1]])

class Chain:
    def __init__(self,start,steps,anchor_end=False,start_angle=0):
        self.start=np.array(start,dtype=float);self.steps=steps;self.anchor_end=anchor_end;self.start_angle=start_angle
        self.final=self.segments(1)
    def segments(self,p):
        xy=self.start.copy();u=np.array([math.cos(math.radians(self.start_angle)*p),math.sin(math.radians(self.start_angle)*p)]);out=[]
        for length,angle in self.steps:
            a=math.radians(angle)*p
            seg={'xy':xy.copy(),'u':u.copy(),'length':length,'a':a}
            out.append(seg)
            if abs(a)<1e-8:xy=xy+u*length
            else:
                n=np.array([-u[1],u[0]]);R=length/a
                xy=xy+R*(math.sin(a)*u+(1-math.cos(a))*n)
                u=turn(u,a)
        if self.anchor_end:
            # Keep the outer flat at its final height while the center moves.
            if hasattr(self,'final'):target=self.endpoint(self.final)[1]
            else:target=xy[1]
            dz=target-xy[1]
            for seg in out:seg['xy'][1]+=dz
        return out
    @staticmethod
    def endpoint(segs):
        seg=segs[-1];return Chain.sample(seg,np.array([1.]))[0][0]
    @staticmethod
    def sample(seg,q):
        q=np.asarray(q);u=seg['u'];n=np.array([-u[1],u[0]]);a=seg['a']
        if abs(a)<1e-8:
            pt=seg['xy']+q[:,None]*seg['length']*u
            tang=np.broadcast_to(u,pt.shape)
        else:
            v=q*a;R=seg['length']/a
            pt=seg['xy']+R*(np.sin(v)[:,None]*u+(1-np.cos(v))[:,None]*n)
            tang=np.cos(v)[:,None]*u+np.sin(v)[:,None]*n
        return pt,tang
    def bind(self,points):
        best=np.full(len(points),np.inf);ids=np.zeros(len(points),dtype=int);qq=np.zeros(len(points));rr=np.zeros((len(points),2))
        for i,seg in enumerate(self.final):
            u=seg['u'];n=np.array([-u[1],u[0]]);a=seg['a'];v=points-seg['xy']
            if abs(a)<1e-8:q=np.clip(v@u/seg['length'],0,1)
            else:
                R=seg['length']/a;v=v-R*n
                angle=np.arctan2(v@u/R,-(v@n)/R)
                q=np.clip(angle/a,0,1)
            pt,tang=self.sample(seg,q);res=points-pt;dist=np.sum(res*res,axis=1);take=dist<best
            normal=np.column_stack([-tang[:,1],tang[:,0]])
            ids[take]=i;qq[take]=q[take];rr[take,0]=np.sum(res*tang,axis=1)[take];rr[take,1]=np.sum(res*normal,axis=1)[take];best[take]=dist[take]
        return ids,qq,rr,best
    def move(self,binding,p):
        ids,qq,res,_=binding;out=np.zeros((len(ids),2))
        for i,seg in enumerate(self.segments(p)):
            take=ids==i;pt,tang=self.sample(seg,qq[take]);normal=np.column_stack([-tang[:,1],tang[:,0]])
            out[take]=pt+tang*res[take,0,None]+normal*res[take,1,None]
        return out

def arc(r,deg):return (r*abs(math.radians(deg)),deg)

def setup(key,vertices):
    v=vertices.copy();movers=[]
    if key=='mounting_hat':
        chain=Chain((0,25.75),[(17,0),arc(2.75,-90),(19.5,0),arc(2.75,90),(16,0)],True)
        b=chain.bind(np.column_stack([abs(v[:,1]),v[:,2]]));sgn=np.where(v[:,1]<0,-1,1)
        def move(p):
            out=v.copy();q=chain.move(b,p);out[:,1]=q[:,0]*sgn;out[:,2]=q[:,1];return out
    elif key=='louver_panel':
        chain=Chain((0,.5),[(57.5,0),arc(2,90),(9.5,0)])
        binding=chain.bind(np.column_stack([abs(v[:,1]),v[:,2]]));sgn=np.where(v[:,1]<0,-1,1)
        flap=Chain((0,.5),[arc(2,30),(12,0)])
        for x in [-45,45]:
            for y in [-38.4,-10.8,16.8]:
                idx=np.where((abs(v[:,0]-x)<28.001)&(v[:,1]>=y-.001)&(v[:,1]<y+13.1))[0]
                b=flap.bind(np.column_stack([v[idx,1]-y,v[idx,2]]));take=b[3]<.251
                idx=idx[take];b=tuple(a[take] for a in b);movers.append((idx,b,y))
        def move(p):
            out=v.copy();edge=np.clip((p-.35)/.65,0,1);q=chain.move(binding,edge);out[:,1]=q[:,0]*sgn;out[:,2]=q[:,1]
            for idx,b,y in movers:
                q=flap.move(b,min(1,p/.7));out[idx,1]=q[:,0]+y;out[idx,2]=q[:,1]
            return out
    else:
        if key=='bead_panel':
            chain=Chain((0,5.5),[(4,0),arc(2,-90),(1,0),arc(2,90),(3,0)],True)
            cy=np.array([-28.05,0,28.05]);which=abs(v[:,1,None]-cy).argmin(axis=1)
            origins=np.column_stack([np.clip(v[:,0],-35,35),cy[which]])
            support=(11.,14.0)
        elif key=='dimple_plate':
            length=(3-3.2*(1-math.cos(math.pi/4)))/math.sin(math.pi/4)
            chain=Chain((4,-2.4),[(1.5,0),arc(1.6,45),(length,0),arc(1.6,-45),(3.6,0)],True)
            centers=np.array([(x,y) for x in [-42,0,42] for y in [-26.4,26.4]])
            which=((v[:,:2,None]-centers.T[None,:,:])**2).sum(axis=1).argmin(axis=1);origins=centers[which]
            support=(float(Chain.endpoint(chain.final)[0]),19.)
        else:
            chain=Chain((0,.6),[(12,0),arc(2.6,90),(12.8,0),arc(2.6,-90),(10,0)],True)
            origins=np.column_stack([np.clip(v[:,0],-52.8,52.8),np.clip(v[:,1],-32.8,32.8)])
            support=None
        diff=v[:,:2]-origins;rho=np.linalg.norm(diff,axis=1);direction=diff/np.maximum(rho[:,None],1e-15)
        b=chain.bind(np.column_stack([rho,v[:,2]]))
        def move(p):
            out=v.copy();q=chain.move(b,p)
            if support:
                # Fade outer planar displacement to zero between neighboring
                # features. This is geometric accommodation, not solved draw-in.
                weight=np.clip((support[1]-rho)/(support[1]-support[0]),0,1)
                q[:,0]=rho+(q[:,0]-rho)*weight
            out[:,:2]=origins+direction*q[:,0,None];out[:,2]=q[:,1]
            return out
    assert np.max(abs(move(1)-v))<1e-8,(key,'endpoint mismatch')
    return move

def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',size)
def ease(t):return t*t*(3-2*t)

def decorate(render,key,p,phase,tooling=False):
    i=KEYS.index(key);im=Image.new('RGB',(960,720),BG);im.paste(Image.fromarray(render).convert('RGB'),(0,115));d=ImageDraw.Draw(im)
    d.text((38,20),'nTop  /  SHEET METAL',font=font(17,True),fill=BLUE)
    d.text((38,49),TITLES[i],font=font(34,True),fill=INK)
    d.text((39,94),SUBTITLES[i],font=font(15),fill='#506579')
    d.rounded_rectangle((38,574,922,624),radius=8,fill='white')
    label=('GEOMETRIC PREFORM' if p<.002 else 'NATIVE nTop GEOMETRY' if p>.999 else 'ILLUSTRATIVE FORMING')
    d.text((55,588),label,font=font(17,True),fill=INK)
    d.text((846,588),f'{round(p*100):3d}%',font=font(17,True),fill=BLUE)
    d.rounded_rectangle((38,642,922,648),radius=3,fill='#d6dfe8')
    if p>.001:d.rounded_rectangle((38,642,38+884*p,648),radius=3,fill=BLUE)
    d.text((38,671),'Prescribed geometry animation. No material-forming simulation.',font=font(17),fill='#425c73')
    if tooling:
        d.rectangle((38,666,930,705),fill=BG)
        d.text((38,671),'Concept tools / prescribed motion / no material-forming solver',font=font(17),fill='#425c73')
        d.text((38,128),'TRANSLUCENT UPPER + LOWER TOOLS',font=font(12,True),fill=BLUE)
        return im
    # A deliberately separate schematic avoids implying fitted production dies.
    x,y=825,145;d.text((x-45,y-24),'STROKE SCHEMATIC',font=font(10,True),fill='#62788b')
    d.line((x-30,y,x-30,y+74),fill='#b5c5d5',width=2);d.line((x+45,y,x+45,y+74),fill='#b5c5d5',width=2)
    stroke=(math.sin(math.pi*p/2) if phase!='hold' else .05)
    py=y+8+stroke*33
    d.rounded_rectangle((x-24,py,x+39,py+9),radius=2,fill=BLUE)
    d.line((x-20,y+62,x+2,y+70,x+35,y+62),fill='#637d94',width=4)
    return im

def make(key,preview=False):
    OUT.mkdir(parents=True,exist_ok=True)
    path=ROOT/'.local'/(key+'.stl');sourcehash=hashlib.sha256(path.read_bytes()).hexdigest()
    evidence=json.loads((ROOT/'evidence'/(key+'.mesh-validation.json')).read_text());assert sourcehash==evidence['mesh_sha256'] and evidence['passed']
    mesh=trimesh.load_mesh(path,process=True);v=mesh.vertices.copy();move=setup(key,v)
    flat=move(0);allbounds=np.vstack([flat,v]);center=(allbounds.max(axis=0)+allbounds.min(axis=0))/2
    scale=float(np.ptp(allbounds,axis=0).max());data=pv.PolyData(v,np.column_stack([np.full(len(mesh.faces),3),mesh.faces]).ravel())
    plot=pv.Plotter(off_screen=True,window_size=(960,465));plot.set_background(BG)
    plot.remove_all_lights()
    plot.add_mesh(data,color='#a6bbcc',smooth_shading=False,specular=.24,ambient=.23,diffuse=.70)
    plot.camera_position=[center+np.array([1.1,-1.6,1.65])*scale,center,[0,0,1]];plot.camera.parallel_projection=True;plot.camera.parallel_scale=scale*.47
    plot.add_light(pv.Light(position=center+np.array([-2,-1,4])*scale,focal_point=center,intensity=.9))
    plot.add_light(pv.Light(position=center+np.array([2,1,1])*scale,focal_point=center,intensity=.35))
    frames=[];sampledir=ROOT/'.local/animation-frames'/key;sampledir.mkdir(parents=True,exist_ok=True)
    timeline=[(0.,'start')]+[(ease(j/60),'form') for j in range(1,61)]+[(1.,'hold')]
    if preview:timeline=[(0.,'start'),(.5,'form'),(1.,'hold')]
    for n,(p,phase) in enumerate(timeline):
        data.points=v if p==1 else move(p);plot.render();shot=plot.screenshot(return_img=True)
        frame=decorate(shot,key,p,phase);frames.append(frame)
        if n in [0,len(timeline)//2,len(timeline)-1]:frame.save(sampledir/f'{n:03}.png')
        if n%15==0:print(key,'frame',n,'/',len(timeline),flush=True)
    plot.close()
    sheet=Image.new('RGB',(960,720*3),'white')
    for j,idx in enumerate([0,len(frames)//2,len(frames)-1]):sheet.paste(frames[idx],(0,j*720))
    sheet.save(ROOT/'reports/assets'/(key+'-forming-contact.png'))
    if preview:return
    # One palette derived from start/middle/end avoids temporal color flicker.
    palette=sheet.resize((480,1080)).quantize(colors=224,method=Image.Quantize.MEDIANCUT)
    indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    durations=[600]+[70]*60+[1400]
    target=OUT/(key+'-forming.gif');indexed[0].save(target,save_all=True,append_images=indexed[1:],duration=durations,loop=0,optimize=True,disposal=1)
    with Image.open(target) as gif:
        count=gif.n_frames;duration=sum((gif.seek(i) or gif.info['duration']) for i in range(count));assert count>=60 and gif.size==(960,720)
    record={'file':target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':960,'height':720,'frames':count,'duration_ms':duration,'loop':True,'source_mesh_sha256':sourcehash,'native_triangles':len(mesh.faces),'endpoint_max_coordinate_error_mm':float(np.max(abs(move(1)-v))),'endpoint_uses_unmodified_native_vertices':True,'animation_method':'Prescribed analytic bend-chain unforming and radial mapping; fixed segment lengths, local offset coordinates, tapered planar accommodation for closed features. No material, contact, draw-in, thinning or springback solver. Schematic stroke inset is not production tooling.','starting_preform_is_released_cut_pattern':False}
    (ROOT/'evidence'/(key+'.animation.json')).write_text(json.dumps(record,indent=2));print(json.dumps(record),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--case',default='all');ap.add_argument('--preview',action='store_true');ap.add_argument('--root',type=Path,default=ROOT);a=ap.parse_args()
    ROOT=a.root.resolve();OUT=ROOT/'share'
    for key in KEYS if a.case=='all' else a.case.split(','):make(key,a.preview)
