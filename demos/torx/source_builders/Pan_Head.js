'use strict';
const path=require('path');
function build(K){
 const q=K.lit,b=K.bloc([
  ['Head radius','real',{length:1},q.L(.0028),'Maximum outside radius.'],
  ['Head height','real',{length:1},q.L(.0024),'Apex above the underhead seating plane.'],
  ['Shank radius','real',{length:1},q.L(.0015),'Neck radius.'],
  ['Crown radius','real',{length:1},q.L(.005),'Spherical cap radius; source rf is approximate. Must exceed head radius.'],
  ['Underhead fillet','real',{length:1},q.L(.0001),'Circular underhead fillet.'],
  ['Neck length','real',{length:1},q.L(.001),'Seating plane to end of plain neck.']
 ]),G=K.geo(b);
 b.sec('Pan head section','Spherical crown, cylindrical side and circular underhead fillet. The unspecified microscopic crown-to-side rounding is omitted.');
 const R=b.inp('Head radius'),h=b.inp('Head height'),s=b.inp('Shank radius'),rf=b.inp('Crown radius'),f=b.inp('Underhead fillet'),n=b.inp('Neck length');
 const ratio=b.once(b.div(R,rf),'Crown normalised radius'),cos=b.once(b.sqrt(b.sub(b.R(1),b.mul(ratio,ratio))),'Crown edge cosine');
 const half=b.once(b.div(b.atan2(ratio,cos),b.R(2)),'Half crown sweep');
 const pt=(label,x,z)=>b.once(G.pt(x,0,z),label,'point');
 const a=pt('Apex',b.L(0),b.neg(h)),c=pt('Crown edge',R,b.add(b.neg(h),b.mul(rf,b.sub(b.R(1),cos))));
 const m=pt('Crown midpoint',b.mul(rf,b.sin(half)),b.add(b.neg(h),b.mul(rf,b.sub(b.R(1),b.cos(half)))));
 const d=pt('Seat outer edge',R,b.L(0)),e=pt('Seat fillet start',b.add(s,f),b.L(0));
 const g=pt('Neck fillet end',s,f),k=Math.SQRT1_2,mf=pt('Fillet midpoint',b.add(s,b.mul(f,b.R(1-k))),b.mul(f,b.R(1-k)));
 const ne=pt('Neck end',s,n),ax=pt('Axis at neck end',b.L(0),n);
 const line=(x,y)=>b.F('two_point_line<point,point>',[x,y]),arc=(x,y,z)=>b.F('three_point_arc<point,point,point>',[x,y,z]);
 const profile=b.F('profile_from_curves<list<curve_interface>,vector>[5.20.0]',[b.LIST('curve_interface',[arc(a,m,c),line(c,d),line(d,e),arc(e,mf,g),line(g,ne),line(ne,ax),line(ax,a)]),b.V(0,1,0)]);
 b.VAR('result','Pan head','implicit',G.revolve(profile,G.axisZ()));
 const topAt=r=>-.0024+.005-Math.sqrt(.005**2-r*r);
 return {b,name:'Pan_Head',displayname:'Pan Head',outId:'result',dir:path.resolve(__dirname,'..'),description:'Parametric pan-head CAD kernel. ISO14583 approximate rf represented by a spherical crown, with cylindrical side and exact circular underhead fillet. Small unspecified outer-edge round omitted. Underhead plane z=0; head -Z, neck +Z.',spec:{bbox:[[-.0028,-.0028,-.0024],[.0028,.0028,.001]],tolSample:1e-7,points:[['crown',.001,0,topAt(.001),0],['crown edge',.0028,0,topAt(.0028),0],['side',.0028,0,-.0005,0],['seat',.002,0,0,0],['neck',.0015,0,.0005,0],['inside',.001,0,-.0005,{sign:-1}]]}};
}
module.exports={build};
