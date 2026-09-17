'use strict';
// Geometric kernel only. Source selection and screw assembly belong to the public Torx block.
// Alternating tangent circular arcs preserve A, B and a chosen convex lobe radius exactly.
const path = require('path');
function build(K) {
  const q = K.lit;
  const b = K.bloc([
    ['Outer radius','real',{length:1},q.L(0.001975),'Half the recess major diameter A.'],
    ['Inner radius','real',{length:1},q.L(0.001425),'Half the recess minor diameter B.'],
    ['Lobe radius','real',{length:1},q.L(0.000395),'Chosen convex arc radius. Default derives from informative ISO 10664:1999 Annex A, not a normative nominal radius.'],
    ['Depth','real',{length:1},q.L(0.0018),'Positive extrusion depth along local +Z.']
  ]);
  b.sec('Tangent contour','Exact tangent circular-arc construction from three independent dimensions.');
  const O=b.inp('Outer radius'), I=b.inp('Inner radius'), R=b.inp('Lobe radius');
  const once=(x,n)=>b.once(x,n);
  const er=once(b.div(R,O),'Normalised lobe radius');
  const br=once(b.div(I,O),'Normalised valley radius');
  const c=once(b.sub(b.R(1),er),'Lobe centre radius');
  const cos30=Math.sqrt(3)/2;
  const numerator=b.sub(b.sub(b.add(b.mul(br,br),b.mul(c,c)),b.mul(b.mul(br,c),b.R(2*cos30))),b.mul(er,er));
  const denominator=b.mul(b.R(2),b.sub(b.add(er,b.mul(c,b.R(cos30))),br));
  const ir=once(b.div(numerator,denominator),'Derived concave radius');
  const d=once(b.add(br,ir),'Valley centre radius');
  const fraction=once(b.div(er,b.add(er,ir)),'Tangency fraction');
  const tx=once(b.mul(O,b.add(c,b.mul(b.sub(b.mul(d,b.R(cos30)),c),fraction))),'Junction X');
  const ty=once(b.mul(O,b.mul(b.mul(d,b.R(0.5)),fraction)),'Junction Y');
  const pts=[];
  function rotated(x,y,theta,label) {
    x=once(x,label+' X'); y=once(y,label+' Y');
    const cp=Math.cos(theta),sp=Math.sin(theta);
    return b.once(b.PT(b.sub(b.mul(x,b.R(cp)),b.mul(y,b.R(sp))),
      b.add(b.mul(x,b.R(sp)),b.mul(y,b.R(cp))),b.L(0)),label,'point');
  }
  for(let k=0;k<6;k++) {
    const t=k*Math.PI/3;
    pts.push({lo:rotated(tx,b.neg(ty),t,'Junction '+k+' lower'),
      hi:rotated(tx,ty,t,'Junction '+k+' upper'),
      tip:rotated(O,b.L(0),t,'Lobe '+k),
      valley:rotated(I,b.L(0),t+Math.PI/6,'Valley '+k)});
  }
  const arcs=[];
  for(let k=0;k<6;k++) {
    arcs.push(b.F('three_point_arc<point,point,point>',[pts[k].lo,pts[k].tip,pts[k].hi]));
    arcs.push(b.F('three_point_arc<point,point,point>',[pts[k].hi,pts[k].valley,pts[(k+1)%6].lo]));
  }
  const profile=b.F('profile_from_curves<list<curve_interface>,vector>[5.20.0]',[b.LIST('curve_interface',arcs),b.V(0,0,1)]);
  const body=b.F('extrude<new_profile,real,real,bool,vector>[5.20.0]',[profile,b.inp('Depth'),b.A(0),b.B(false),b.V(0,0,1)]);
  b.VAR('result','Torx internal cutting body','implicit',body);
  return {b,name:'Torx_Internal',displayname:'Torx Internal',outId:'result',dir:path.resolve(__dirname,'..'),
    description:'Parametric tangent-arc kernel. Default CAD contour uses ISO 10664:1999 Table 1 dimensions and an informative Annex A radius choice. Not a unique standard-mandated contour. Local origin at mouth; +Z into recess.',
    spec:{bbox:[[-.001975,-.001975,0],[.001975,.001975,.0018]],tolSample:1e-7,
      points:[['major',.001975,0,.0009,0],['minor',.001425*Math.cos(Math.PI/6),.001425*.5,.0009,0],['mouth',0,0,0,0],['floor',0,0,.0018,0],['centre',0,0,.0009,-.0009]]}};
}
module.exports={build};
