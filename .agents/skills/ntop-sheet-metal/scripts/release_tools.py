"""Conservative opposing release envelopes for full native triangular meshes.

Every triangle contributes its extrema to every cell overlapped by its XY
bounding box. One-cell dilation and incident-cell vertex extrema give a
piecewise linear envelope with a provable separation lower bound. These are
clearance envelopes, not contact dies: tunnels and returns are excluded from
the matched tool face. Closing/forming contact is not solved.
"""
import hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.ndimage import maximum_filter,minimum_filter,distance_transform_edt
from animate_with_tools import solid_heightfield

def tool_shells(mesh,root,key,sha):
    pitch=1.;vertical=.75;lateral=.5
    points=np.asarray(mesh.points);faces=mesh.faces.reshape(-1,4)[:,1:]
    tri=points[faces];minimum=tri.min(axis=1);maximum=tri.max(axis=1)
    origin=np.floor(points[:,:2].min(axis=0))-5
    size=np.ceil((points[:,:2].max(axis=0)+5-origin)/pitch).astype(int)
    nx,ny=map(int,size)
    low=np.full((ny,nx),np.inf);high=np.full((ny,nx),-np.inf)
    ij0=np.floor((minimum[:,:2]-origin)/pitch).astype(int)
    ij1=np.floor((maximum[:,:2]-origin)/pitch).astype(int)
    assert (ij0>=0).all() and (ij1<size).all()
    spans=ij1-ij0;coverage=np.zeros(len(faces),dtype=np.int64)
    for dy in range(int(spans[:,1].max())+1):
        for dx in range(int(spans[:,0].max())+1):
            selected=np.where((spans[:,0]>=dx)&(spans[:,1]>=dy))[0]
            if not len(selected):continue
            ids=(ij0[selected,1]+dy)*nx+ij0[selected,0]+dx
            np.maximum.at(high.ravel(),ids,maximum[selected,2])
            np.minimum.at(low.ravel(),ids,minimum[selected,2])
            coverage[selected]+=1
    assert np.array_equal(coverage,(spans[:,0]+1)*(spans[:,1]+1))
    native_cells=np.isfinite(high)
    nearest=distance_transform_edt(~native_cells,return_distances=False,return_indices=True)
    high[~native_cells]=high[tuple(nearest[:,~native_cells])]
    low[~native_cells]=low[tuple(nearest[:,~native_cells])]
    high=maximum_filter(high,size=3,mode='nearest')
    low=minimum_filter(low,size=3,mode='nearest')
    def nodes(cells,upper):
        pad=np.pad(cells,1,mode='edge')
        four=np.stack([pad[:-1,:-1],pad[1:,:-1],pad[:-1,1:],pad[1:,1:]])
        return (four.max(axis=0) if upper else four.min(axis=0))
    top=nodes(high,True)+vertical;bottom=nodes(low,False)-vertical
    assert np.isfinite(top).all() and np.isfinite(bottom).all() and (top>bottom).all()
    # Independently verify each covered facet-cell rectangle against all four
    # heightfield corner values; any interpolation within that cell is bounded.
    topcell=np.minimum.reduce([top[:-1,:-1],top[1:,:-1],top[:-1,1:],top[1:,1:]])
    botcell=np.maximum.reduce([bottom[:-1,:-1],bottom[1:,:-1],bottom[:-1,1:],bottom[1:,1:]])
    upper_gap=math.inf;lower_gap=math.inf
    for dy in range(int(spans[:,1].max())+1):
        for dx in range(int(spans[:,0].max())+1):
            sel=np.where((spans[:,0]>=dx)&(spans[:,1]>=dy))[0]
            if not len(sel):continue
            i=ij0[sel,0]+dx;j=ij0[sel,1]+dy
            upper_gap=min(upper_gap,float((topcell[j,i]-maximum[sel,2]).min()))
            lower_gap=min(lower_gap,float((minimum[sel,2]-botcell[j,i]).min()))
    assert min(upper_gap,lower_gap)>=vertical-1e-10
    X,Y=np.meshgrid(origin[0]+np.arange(nx+1)*pitch,origin[1]+np.arange(ny+1)*pitch)
    upper=solid_heightfield(X,Y,top,np.full(top.shape,top.max()+7))
    lower=solid_heightfield(X,Y,np.full(bottom.shape,bottom.min()-7),bottom)
    assert upper.n_open_edges==lower.n_open_edges==0
    np.savez_compressed(root/'.local'/(key+'.release-envelope.npz'),X=X,Y=Y,top=top,bottom=bottom,source_sha256=sha)
    record={'passed':True,'native_mesh_sha256':sha,'native_triangles':len(faces),'facet_cell_assignments':int(coverage.sum()),
      'all_facets_covered':True,'native_occupied_cells':int(native_cells.sum()),'grid_spacing_mm':pitch,
      'vertical_clearance_mm':vertical,'lateral_clearance_lower_bound_mm':lateral,'spatial_separation_lower_bound_mm':min(vertical,lateral),
      'measured_conservative_upper_gap_mm':upper_gap,'measured_conservative_lower_gap_mm':lower_gap,
      'release_checks':[{'offset_mm':d,'upper_gap_lower_bound_mm':upper_gap+d,'lower_gap_lower_bound_mm':lower_gap+d,'passed':True} for d in [0,2,5,10]],
      'release_axes':{'upper':[0,0,1],'lower':[0,0,-1]},'tool_shells_closed':True,
      'method':'Full triangle XY-AABB extrema, one-cell max/min dilation, incident-cell nodal extrema; 0.75 mm vertical allowance. Bounds checked for every triangle/cell assignment.',
      'proof_scope':'Relative to accepted native tessellation. One-cell dilation covers every XY point within 0.5 mm of each triangle bounding box; nodal extrema bound both triangles of each tool cell. Other XY points are at least 0.5 mm away. Outward Z translation monotonically increases vertical separation.',
      'scope':'Conservative release envelopes only. Return and bridge interiors are not reproduced as contact die faces. No forming-stroke contact, production die design, strain or force analysis.'}
    (root/'evidence'/(key+'.release-validation.json')).write_text(json.dumps(record,indent=2))
    print(key,'release envelope passed',len(faces),'facets; closed clearance >=',min(vertical,lateral),'mm',flush=True)
    return upper,lower,record
