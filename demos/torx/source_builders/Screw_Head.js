'use strict';
const path=require('path');
// Generic cylindrical screw-head geometry. Dimensions remain explicit runtime inputs.
// Both circular rounds are represented by actual arcs in a single revolved section.
function build(K){
  const q=K.lit,b=K.bloc([
    ['Head radius','real',{length:1},q.L(.00275),'Radius of cylindrical head envelope.'],
    ['Head height','real',{length:1},q.L(.003),'Distance above the seating plane.'],
    ['Shank radius','real',{length:1},q.L(.0015),'Neck radius below the seating plane.'],
    ['Top round','real',{length:1},q.L(.0003),'Circular rounding of top outside edge. Positive, less than head height/radius.'],
    ['Underhead fillet','real',{length:1},q.L(.0001),'Positive circular shank-to-seating-plane fillet.'],
    ['Neck length','real',{length:1},q.L(.001),'Neck length including underhead fillet, along +Z.']
  ]),G=K.geo(b);
  const R=b.inp('Head radius'),h=b.inp('Head height'),s=b.inp('Shank radius'),r=b.inp('Top round'),f=b.inp('Underhead fillet'),n=b.inp('Neck length');
  b.sec('Axial section','Head above z=0; shank below, along +Z.');
  const pt=(name,x,z)=>b.once(G.pt(x,0,z),name,'point');
  const a=pt('Axis at top',b.L(0),b.neg(h));
  const bb=pt('Top tangent',b.sub(R,r),b.neg(h));
  const c=pt('Side tangent',R,b.add(b.neg(h),r));
  const d=pt('Head seating edge',R,b.L(0));
  const e=pt('Fillet seating tangent',b.add(s,f),b.L(0));
  const ff=pt('Fillet shank tangent',s,f);
  const g=pt('Neck end',s,n),i=pt('Axis at neck end',b.L(0),n);
  const k=Math.SQRT1_2;
  const mTop=pt('Top arc midpoint',b.sub(R,b.mul(r,b.R(1-k))),b.add(b.neg(h),b.mul(r,b.R(1-k))));
  const mFillet=pt('Fillet midpoint',b.add(s,b.mul(f,b.R(1-k))),b.mul(f,b.R(1-k)));
  const line=(x,y)=>b.F('two_point_line<point,point>',[x,y]);
  const arc=(x,y,z)=>b.F('three_point_arc<point,point,point>',[x,y,z]);
  const profile=b.F('profile_from_curves<list<curve_interface>,vector>[5.20.0]',[b.LIST('curve_interface',[
    line(a,bb),arc(bb,mTop,c),line(c,d),line(d,e),arc(e,mFillet,ff),line(ff,g),line(g,i),line(i,a)]),b.V(0,1,0)]);
  b.VAR('result','Cylindrical screw head','implicit',G.revolve(profile,G.axisZ()));
  return {b,name:'Screw_Head',displayname:'Screw Head',outId:'result',dir:path.resolve(__dirname,'..'),
    description:'Parametric cylindrical head with circular top edge and underhead fillet. Seating plane z=0, neck along +Z. Input dimensions select a CAD design; no tolerance-class conformity claim.',
    spec:{bbox:[[-.00275,-.00275,-.003],[.00275,.00275,.001]],tolSample:1e-7,points:[
      ['head side',.00275,0,-.0015,0],['top',.001,0,-.003,0],['seat',.002,0,0,0],
      ['top round',.00275-.0003*(1-k),0,-.003+.0003*(1-k),0],
      ['underhead fillet',.0015+.0001*(1-k),0,.0001*(1-k),0],['neck',.0015,0,.0005,0]]}};
}
module.exports={build};
