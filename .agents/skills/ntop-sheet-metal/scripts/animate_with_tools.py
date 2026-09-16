"""Transparent matched-envelope tooling around the native sheet animation.

Tool shells are sampled vertical envelopes of the final native geometry, with
0.6 mm nominal vertical display clearance and 1 mm grid spacing. They are
visual concepts, not designed tooling. No contact or release check is implied.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import pyvista as pv
import trimesh
from PIL import Image
from scipy.spatial import cKDTree
import animate_advanced as anim
from build_complex_sheet_metal import LABELS,KEYS as COMPLEX_KEYS
ROOT=Path.cwd()/'.local'/'sheet-metal-study'

def chain(spec,anchor=True):return anim.Chain(spec['start'],spec['steps'],anchor_end=anchor,start_angle=spec.get('start_angle',0))
def complex_motion(vertices,m):
    v=vertices.copy();c=chain(m['chain']);kind=m['kind'];feature_ops=[]
    if kind=='section':
        bind=c.bind(v[:,1:3]);delta=c.endpoint(c.final)[0]-c.start[0]
        def base(points,p,binding=None):
            out=points.copy();b=bind if binding is None else binding;q=c.move(b,p);out[:,1:3]=q
            now=c.endpoint(c.segments(p))[0]-c.start[0];out[:,1]-=(now-delta)/2;return out
    elif kind=='symmetric':
        bind=c.bind(np.column_stack([abs(v[:,1]),v[:,2]]));sign=np.where(v[:,1]<0,-1,1)
        def base(points,p,binding=None):
            out=points.copy();q=c.move(bind if binding is None else binding,p);out[:,1]=q[:,0]*sign;out[:,2]=q[:,1];return out
    else:
        if kind=='rounded':origins=np.column_stack([np.clip(v[:,0],-m['core'][0],m['core'][0]),np.clip(v[:,1],-m['core'][1],m['core'][1])])
        else:origins=np.zeros_like(v[:,:2])
        dv=v[:,:2]-origins;rho=np.linalg.norm(dv,axis=1);parent_direction=dv/np.maximum(rho[:,None],1e-15);bind=c.bind(np.column_stack([rho,v[:,2]]))
        def base(points,p,binding=None):
            out=points.copy();q=c.move(bind if binding is None else binding,p);out[:,:2]=origins+parent_direction*q[:,0,None];out[:,2]=q[:,1];return out
    # Local features remain referenced to their native parent flats. Applying
    # their local displacement after the base transformation preserves the
    # animated parent datum, while keeping the final native state exact.
    for f in m['features']:
        fc=chain(f['chain']);ft=f['kind']
        if ft in ['beads','dimples']:
            centers=np.array(f['centers'],dtype=float);which=((v[:,:2,None]-centers.T[None,:,:])**2).sum(axis=1).argmin(axis=1);orig=centers[which].copy()
            if ft=='beads':orig[:,0]+=np.clip(v[:,0]-orig[:,0],-f['straight']/2,f['straight']/2)
            diff=v[:,:2]-orig;rho=np.linalg.norm(diff,axis=1);direction=diff/np.maximum(rho[:,None],1e-15)
            # Nearby vertices on other levels must not bind to this patch.
            idx=np.where((rho<f['support'][1])&(abs(v[:,2]-fc.endpoint(fc.final)[1])<15))[0]
            fb=fc.bind(np.column_stack([rho[idx],v[idx,2]]));weight=np.clip((f['support'][1]-rho[idx])/(f['support'][1]-f['support'][0]),0,1)
            feature_ops.append((ft,fc,idx,fb,(orig[idx],rho[idx],direction[idx],weight),f))
        else:
            for x,y in f['centers']:
                end=fc.endpoint(fc.final)[0];start=fc.start[0]
                idx=np.where((abs(v[:,0]-x)<f['span']/2+.002)&(v[:,1]>=y+start-.002)&(v[:,1]<=y+end+.002))[0]
                fb=fc.bind(np.column_stack([v[idx,1]-y,v[idx,2]]));inside=fb[3]<(f['chain']['thickness']/2+.004)**2
                idx=idx[inside];fb=tuple(z[inside] for z in fb);feature_ops.append((ft,fc,idx,fb,y,f))
    def move(p):
        qbase=np.clip((p-.25)/.75,0,1) if feature_ops else p;out=base(v,qbase)
        localp=min(1,p/.72)
        for ft,fc,idx,fb,extra,f in feature_ops:
            q=fc.move(fb,localp)
            if ft in ['beads','dimples']:
                orig,rho,direction,weight=extra;delta=(q[:,0]-rho)*weight
                out[idx,:2]+=direction*delta[:,None];out[idx,2]+=q[:,1]-v[idx,2]
            else:
                if ft=='bridges':
                    # Compress the unfolding's longitudinal span to keep both
                    # roots on their parent datums. This prescribed in-plane
                    # deformation is expressly not an inextensible fold model.
                    opening=f['opening'];last=fc.endpoint(fc.segments(localp))[0]-2*f['chain']['thickness']
                    q[:,0]=np.where(q[:,0]<0,q[:,0],np.where(q[:,0]>last,opening+q[:,0]-last,q[:,0]*opening/last))
                out[idx,1]+=q[:,0]+extra-v[idx,1];out[idx,2]+=q[:,1]-v[idx,2]
        return out
    assert abs(move(1)-v).max()<1e-7,('native endpoint',abs(move(1)-v).max())
    return move

def solid_heightfield(X,Y,lo,hi):
    ny,nx=X.shape;n=nx*ny;points=np.vstack([np.column_stack([X.ravel(),Y.ravel(),lo.ravel()]),np.column_stack([X.ravel(),Y.ravel(),hi.ravel()])]);faces=[]
    for j in range(ny-1):
        for i in range(nx-1):
            k=j*nx+i;a,b,c,d=k,k+1,k+nx+1,k+nx
            faces.extend([[4,d,c,b,a],[4,a+n,b+n,c+n,d+n]])
    border=[*range(nx),*[j*nx+nx-1 for j in range(1,ny)],*range((ny-1)*nx+nx-2,(ny-1)*nx-1,-1),*[j*nx for j in range(ny-2,0,-1)]]
    for a,b in zip(border,border[1:]+border[:1]):faces.append([4,a,b,b+n,a+n])
    return pv.PolyData(points,np.array(faces).ravel()).triangulate().compute_normals(auto_orient_normals=True)

def tool_shells(mesh,root,key,sha):
    cached=root/'.local'/(key+'.tool-heightfield-1mm.npz')
    if cached.exists():
        stored=np.load(cached);assert str(stored['sha'])==sha;X,Y,top,bottom=[stored[k] for k in ['X','Y','top','bottom']]
    else:
        bounds=np.array(mesh.bounds).reshape(3,2);pitch=1.;nx=math.ceil((bounds[0,1]-bounds[0,0]+10)/pitch);ny=math.ceil((bounds[1,1]-bounds[1,0]+10)/pitch);center=bounds.mean(axis=1);scale=max(nx,ny)*pitch
        xs=center[0]+(np.arange(nx)+.5-nx/2)*pitch;ys=center[1]+(ny/2-np.arange(ny)-.5)*pitch;X,Y=np.meshgrid(xs,ys);xy=np.column_stack([X.ravel(),Y.ravel()])
        sampler=pv.Plotter(off_screen=True,window_size=(nx,ny));sampler.add_mesh(mesh);sampler.camera.parallel_projection=True;sampler.camera.parallel_scale=ny*pitch/2
        eye=center[2]+scale*2;sampler.camera_position=[(center[0],center[1],eye),center,(0,1,0)];sampler.show(auto_close=False);top=(eye+sampler.get_image_depth()).ravel()
        eye=center[2]-scale*2;sampler.camera_position=[(center[0],center[1],eye),center,(0,1,0)];sampler.render();bottom=np.fliplr(eye-sampler.get_image_depth()).ravel();sampler.close()
        good=np.isfinite(top);assert good.sum()>200
        for values in [top,bottom]:
            valid=np.isfinite(values);assert valid.sum()>200
            nearest=cKDTree(xy[valid]).query(xy[~valid])[1];values[~valid]=values[valid][nearest]
        top=top.reshape(X.shape);bottom=bottom.reshape(X.shape);np.savez_compressed(cached,X=X,Y=Y,top=top,bottom=bottom,sha=sha)
        print(key,'tool envelope samples',len(xy),'native hits',int(good.sum()),flush=True)
    # Repair an earlier cache with mismatched silhouette masks in opposite
    # camera views. Each height field must fill from its own valid samples.
    xy=np.column_stack([X.ravel(),Y.ravel()])
    for values in [top,bottom]:
        flat=values.ravel();valid=np.isfinite(flat)
        if not valid.all():flat[~valid]=flat[valid][cKDTree(xy[valid]).query(xy[~valid])[1]]
    assert np.isfinite(top).all() and np.isfinite(bottom).all()
    np.savez_compressed(cached,X=X,Y=Y,top=top,bottom=bottom,sha=sha)
    upper=solid_heightfield(X,Y,top+.6,np.full(X.shape,top.max()+7));lower=solid_heightfield(X,Y,np.full(X.shape,bottom.min()-7),bottom-.6)
    return upper,lower,{'grid_spacing_max_mm':1.,'samples':int(X.size),'vertical_display_clearance_mm':.6,'native_mesh_sha256':sha,'sampling':'opposed orthographic native-mesh depth buffers; independent silhouette masks','hole_treatment':'nearest sampled sheet height fills holes for forming visualization; no piercing tools','scope':'sampled vertical upper/lower envelopes, not qualified tooling; no release or contact analysis'}

def make(root,key,preview=False):
    print(key,'loading native mesh',flush=True)
    path=root/'.local'/(key+'.stl');sha=hashlib.sha256(path.read_bytes()).hexdigest();evidence=json.loads((root/'evidence'/(key+'.mesh-validation.json')).read_text());assert evidence['passed'] and evidence['mesh_sha256']==sha
    mesh=trimesh.load_mesh(path,process=True);v=mesh.vertices.copy();native=pv.PolyData(v,np.column_stack([np.full(len(mesh.faces),3),mesh.faces]).ravel())
    if key in COMPLEX_KEYS:
        metadata=json.loads((root/'evidence'/(key+'.design.json')).read_text())['metadata'];move=complex_motion(v,metadata['motion'])
        anim.KEYS=COMPLEX_KEYS;anim.TITLES=[LABELS[k] for k in COMPLEX_KEYS];anim.SUBTITLES=['Compound sheet geometry / translucent concept tooling']*6
    else:move=anim.setup(key,v)
    print(key,'sampling concept tooling',flush=True)
    upper,lower,toolrecord=tool_shells(native,root,key,sha)
    flat=move(0);total=np.vstack([flat,v,upper.points,lower.points]);center=(total.max(axis=0)+total.min(axis=0))/2;scale=float(np.ptp(total,axis=0).max());travel=max(18,float(np.ptp(total,axis=0)[2])*.75)
    plot=pv.Plotter(off_screen=True,window_size=(960,465));plot.set_background(anim.BG);plot.remove_all_lights()
    sheet=pv.PolyData(v,native.faces.copy());plot.add_mesh(sheet,color='#7694ad',smooth_shading=False,specular=.20,ambient=.30,diffuse=.70)
    up=plot.add_mesh(upper,color='#248aff',opacity=.19,smooth_shading=True,specular=.20,ambient=.4);down=plot.add_mesh(lower,color='#56b2e8',opacity=.16,smooth_shading=True,specular=.15,ambient=.4)
    plot.enable_depth_peeling(number_of_peels=8,occlusion_ratio=.0)
    plot.camera_position=[center+np.array([1.1,-1.6,1.45])*scale,center,[0,0,1]];plot.camera.parallel_projection=True;plot.camera.parallel_scale=scale*.51
    plot.add_light(pv.Light(position=center+np.array([-2,-1,4])*scale,focal_point=center,intensity=.9));plot.add_light(pv.Light(position=center+np.array([2,1,1])*scale,focal_point=center,intensity=.35))
    timeline=[(0.,1.,'start')]+[(anim.ease(j/60),1-anim.ease(j/60),'form') for j in range(1,61)]+[(1.,anim.ease(j/12)*.55,'retract') for j in range(1,13)]+[(1.,.55,'hold')]
    if preview:timeline=[(0.,1.,'start'),(.5,.5,'form'),(1.,0.,'closed'),(1.,.55,'hold')]
    frames=[];sampledir=root/'.local/tooling-frames'/key;sampledir.mkdir(parents=True,exist_ok=True)
    for n,(p,offset,phase) in enumerate(timeline):
        sheet.points=v if p==1 else move(p);up.SetPosition(0,0,travel*offset);down.SetPosition(0,0,-travel*offset);plot.render();shot=plot.screenshot(return_img=True)
        if np.std(shot.astype(float),axis=(0,1)).mean()<3:
            plot.disable_depth_peeling();plot.render();shot=plot.screenshot(return_img=True)
        assert np.std(shot.astype(float),axis=(0,1)).mean()>3,'Empty tooling render'
        frame=anim.decorate(shot,key,p,phase,tooling=True);frames.append(frame)
        if n in [0,len(timeline)//2,len(timeline)-2,len(timeline)-1]:frame.save(sampledir/f'{n:03}.png')
        if n%20==0:print(key,'tools frame',n,'/',len(timeline),flush=True)
    plot.close();contact=Image.new('RGB',(960,2160))
    for n,i in enumerate([0,len(frames)//2,len(frames)-1]):contact.paste(frames[i],(0,n*720))
    contact.save(root/'reports/assets'/(key+'-tools-contact.png'))
    if preview:return
    palette=contact.resize((480,1080)).quantize(colors=240,method=Image.Quantize.MEDIANCUT);indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames];duration=[600]+[70]*72+[1400]
    target=root/'share'/(key+'-forming-tools.gif');target.parent.mkdir(exist_ok=True);indexed[0].save(target,save_all=True,append_images=indexed[1:],duration=duration,loop=0,optimize=True,disposal=1)
    with Image.open(target) as gif:
        count=gif.n_frames;ms=sum((gif.seek(i) or gif.info['duration']) for i in range(count));gif.seek(count-1);gif.convert('RGB').save(root/'reports/assets'/(key+'-tools-poster.png'))
    record={'file':target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':960,'height':720,'frames':count,'duration_ms':ms,'loop':True,'source_mesh_sha256':sha,'native_triangles':len(mesh.faces),'endpoint_max_coordinate_error_mm':float(abs(move(1)-v).max()),'endpoint_uses_unmodified_native_vertices':True,'tooling':toolrecord,'scope':'Illustrative prescribed geometry and translucent concept tooling. No material/contact solver. Geometric preforms are not released cutting blanks.'}
    (root/'evidence'/(key+'.tooling-animation.json')).write_text(json.dumps(record,indent=2));print(key,'GIF bytes',record['bytes'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--study',choices=['advanced','complex'],default='advanced');ap.add_argument('--case',default='all');ap.add_argument('--preview',action='store_true');ap.add_argument('--root',type=Path);args=ap.parse_args()
    keys=anim.KEYS if args.study=='advanced' else COMPLEX_KEYS
    for k in keys if args.case=='all' else args.case.split(','):make(args.root.resolve() if args.root else ROOT/args.study,k,args.preview)
