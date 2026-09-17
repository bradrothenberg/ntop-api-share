'use strict';
const path=require('path');
function build(K){
 const q=K.lit,b=K.bloc([
  ['Head radius','real',{length:1},q.L(.00275),'Actual maximum head radius, not theoretical sharp-cone radius.'],
  ['Head height','real',{length:1},q.L(.00165),'Maximum axial head height.'],
  ['Shank radius','real',{length:1},q.L(.0015),'Cone ends at this radius.'],
  ['Neck length','real',{length:1},q.L(.001),'Plain shoulder below cone before full thread.']
 ]),G=K.geo(b);
 b.sec('Historical countersunk section','ISO14581:2013 candidate envelope: 90-degree included cone, flat rim, sharp cone-to-shank junction.');
 const R=b.inp('Head radius'),h=b.inp('Head height'),s=b.inp('Shank radius'),n=b.inp('Neck length');
 const pt=(label,x,z)=>b.once(G.pt(x,0,z),label,'point');
 const ps=[pt('Top centre',b.L(0),b.neg(h)),pt('Top rim',R,b.neg(h)),pt('Cone outer edge',R,b.neg(b.sub(R,s))),pt('Cone end',s,b.L(0)),pt('Neck end',s,n),pt('Axis at neck',b.L(0),n)];
 const edges=ps.map((p,i)=>b.F('two_point_line<point,point>',[p,ps[(i+1)%ps.length]]));
 const profile=b.F('profile_from_curves<list<curve_interface>,vector>[5.20.0]',[b.LIST('curve_interface',edges),b.V(0,1,0)]);
 b.VAR('result','Countersunk head','implicit',G.revolve(profile,G.axisZ()));
 return {b,name:'Countersunk_Head',displayname:'Countersunk Head 2013',outId:'result',dir:path.resolve(__dirname,'..'),description:'Historical ISO14581:2013 derived CAD head envelope; flat rim and 90-degree included cone. Cone-to-neck round omitted. Local cone end z=0, head -Z, neck +Z. Public assembly moves the top face to insertion datum and includes the head in total length.',spec:{bbox:[[-.00275,-.00275,-.00165],[.00275,.00275,.001]],tolSample:1e-7,points:[['top',.001,0,-.00165,0],['rim',.00275,0,-.0015,0],['cone',.002,0,-.0005,0],['neck',.0015,0,.0005,0],['inside',.001,0,-.0005,{sign:-1}],['outside cone',.0021,0,-.0005,{sign:1}]]}};
}
module.exports={build};
