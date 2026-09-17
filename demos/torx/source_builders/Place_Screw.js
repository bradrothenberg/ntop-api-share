'use strict';
/* Rigid placement of a source body from local XYZ into a right-handed surface frame.
 * Local +Z follows Axis; local +X follows projected Tangent Reference before Clocking Angle.
 * No fallback is defined for a zero Axis or parallel/zero Tangent Reference. */
function build(K){
 const source=K.lit.F('box<point,real,real,real>',[K.lit.P3(0,0,0.005),K.lit.L(0.006),K.lit.L(0.004),K.lit.L(0.010)]);
 const b=K.bloc([
  ['Implicit Body','implicit',null,source,'Source geometry in its local XYZ frame.'],
  ['Insertion Point','point',{length:1},K.lit.P3(0,0,0),'World location of the source local origin.'],
  ['Axis','vector',{},K.lit.V(0,0,1),'Nonzero direction of local +Z; magnitude is normalised.'],
  ['Tangent Reference','vector',{},K.lit.V(1,0,0),'Nonzero reference projected perpendicular to Axis; must not be parallel to Axis.'],
  ['Clocking Angle','real',{angle:1},K.lit.A(0),'Right-handed rotation around Axis, SI radians.'],
 ]),g=K.geo(b);
 const {F,VAR,ref,inp,R,L,X,add,sub,mul,div,fadd,fsub,fmul}=b;
 const sum=v=>v.reduce(add),fsum=v=>v.reduce(fadd);
 const cross=(a,c)=>F('cross_product<vector,vector>',[a,c]);
 const vector=(x,y,z)=>F('vector<real,real,real>',[x,y,z]);
 b.sec('Surface frame','Normalise Axis and project Tangent Reference. The frame requires nonzero independent axes.');
 VAR('pl_z','Normalised axis','vector',inp('Axis',['unit vector']));
 VAR('pl_yraw','Perpendicular tangent','vector',cross(ref('pl_z'),inp('Tangent Reference')));
 VAR('pl_y0','Normalised transverse direction','vector',ref('pl_yraw',['unit vector']));
 VAR('pl_x0','Projected tangent direction','vector',cross(ref('pl_y0'),ref('pl_z')));
 VAR('pl_cos','Clocking cosine','real',b.cos(inp('Clocking Angle')));
 VAR('pl_sin','Clocking sine','real',b.sin(inp('Clocking Angle')));
 VAR('pl_x','Clocked tangent','vector',vector(...['x','y','z'].map(a=>add(mul(ref('pl_x0',[a]),ref('pl_cos')),mul(ref('pl_y0',[a]),ref('pl_sin'))))));
 VAR('pl_y','Clocked transverse direction','vector',cross(ref('pl_z'),ref('pl_x')));
 VAR('pl_frame','Placement frame','frame',g.frame(inp('Insertion Point'),ref('pl_x'),ref('pl_y')));
 b.sec('Inverse coordinate map','Evaluate the unchanged source body at dot(world-origin, frame axes).');
 for(const a of ['x','y','z'])VAR('pl_d'+a,'World displacement '+a,'real_field',fsub(X(a,{length:1}),inp('Insertion Point',[a])));
 for(const a of ['x','y','z'])VAR('pl_q'+a,'Local '+a,'real_field',fsum(['x','y','z'].map(c=>fmul(ref('pl_d'+c),ref('pl_frame',[a+' axis',c])))));
 VAR('pl_mapped','Placed field','real_field',b.REMAP(inp('Implicit Body'),ref('pl_qx'),ref('pl_qy'),ref('pl_qz')));
 b.sec('Driven bounds','Rigidly transform the source bounding-box centre and project its half-extents.');
 for(const a of ['x','y','z']){
  VAR('pl_c'+a,'Source bounds centre '+a,'real',div(add(inp('Implicit Body',['bounding box','min point',a]),inp('Implicit Body',['bounding box','max point',a])),R(2)));
  VAR('pl_h'+a,'Source bounds half span '+a,'real',div(sub(inp('Implicit Body',['bounding box','max point',a]),inp('Implicit Body',['bounding box','min point',a])),R(2)));
 }
 for(const a of ['x','y','z']){
  VAR('pl_wc'+a,'Placed bounds centre '+a,'real',add(inp('Insertion Point',[a]),sum(['x','y','z'].map(c=>mul(ref('pl_c'+c),ref('pl_frame',[c+' axis',a]))))));
  VAR('pl_wh'+a,'Placed bounds half span '+a,'real',sum(['x','y','z'].map(c=>mul(ref('pl_h'+c),b.abs(ref('pl_frame',[c+' axis',a]))))));
 }
 VAR('pl_bounds','Placed bounds','bounding_box',g.bbox(g.pt(...['x','y','z'].map(a=>sub(ref('pl_wc'+a),ref('pl_wh'+a)))),g.pt(...['x','y','z'].map(a=>add(ref('pl_wc'+a),ref('pl_wh'+a))))));
 VAR('Placed','Placed Body','implicit',b.SBB(ref('pl_mapped'),ref('pl_bounds')));
 return {b,outId:'Placed',recipe:b.recipe('Place Screw','Rigid placement. Local +Z follows Axis; local +X follows the perpendicular projection of Tangent Reference then Clocking Angle. Insertion Point places local origin. Axis and projected tangent must be nonzero.','Placed')};
}
module.exports={build};
