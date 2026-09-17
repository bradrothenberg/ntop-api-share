'use strict';
const path=require('path');
const catalogue=require('./catalogue');
const DRIVE=catalogue.drives.map(r=>[r.size,r.A,r.B]);
// ISO source bounds and declared CAD choices, mm: d,p,dk,k,v,r,2P,t,drive,b,short-limit,web.
// Quarter-round=vmax and short neck=2P are explicit design choices, not prescribed profiles.
const SCREW=catalogue.cylindrical.map(r=>[r.d,r.P,r.dk_max_plain,r.k_max,r.v_max,r.r_min,2*r.P,r.t_max,r.drive,r.b_ref,r.full_thread_preferred_length_max,r.w_min]);
const SOURCE_ROWS=[...catalogue.cylindrical.map(r=>[r.id,r.d,r.P,r.dk_max_plain,r.k_max,r.v_max,r.r_min,2*r.P,r.t_max,r.drive,r.b_ref,r.full_thread_preferred_length_max,r.w_min,r.dk_max_plain]),
 ...catalogue.pan.map(r=>[100+r.id,r.d,r.P,r.dk_max,r.k_max,r.r_min,r.r_min,r.a_max,r.t_max,r.drive,0,0,0,r.rf_approx]),
 ...catalogue.countersunk.map(r=>[200+r.id,r.d,r.P,r.dk_actual_max,r.k_max,.1*r.k_max,.05*r.P,r.a_max,r.t_max,r.drive,0,0,0,r.dk_actual_max])];
function build(K){
  const q=K.lit,b=K.bloc([
    ['Drive family','integer',{},q.I(0),'0=internal; 1=tamper-resistant custom derivative with sourced round post.'],
    ['Screw series','integer',{},q.I(0),'0=cylindrical2011, 1=pan2011, 2=countersunk2013 historical.'],
    ['Metric size index','integer',{},q.I(2),'Stable source-row identifier from catalogue.js; M2 through M20.'],
    ['Drive size','integer',{},q.I(0),'0=automatic for metric size; otherwise one of the sixteen supplied ISO 10664:1999 size numbers.'],
    ['Length','real',{length:1},q.L(.010),'Raised heads: underhead to tip. Countersunk: total length including head.'],
    ['Override shank','bool',{},q.B(false),'Enable custom scaling from the selected metric envelope.'],
    ['Shank radius','real',{length:1},q.L(.0015),'Used only with override; scales pitch and head dimensions proportionally.'],
    ['Override Torx','bool',{},q.B(false),'Enable independent recess radius scaling.'],
    ['Torx radius','real',{length:1},q.L(.0014),'Maximum recess radius, independently controlled.']
  ]),G=K.geo(b);
  const head=K.cb(path.join(__dirname,'cb_Screw_Head.json'));
  const panHead=K.cb(path.join(__dirname,'cb_Pan_Head.json'));
  const countersunkHead=K.cb(path.join(__dirname,'cb_Countersunk_Head.json'));
  const thread=K.cb(path.join(__dirname,'cb_Metric_Thread.json'));
  const drive=K.cb(path.join(__dirname,'cb_Torx_Internal.json'));
  const once=(x,n)=>b.once(x,n);
  const choose=(cond,a,c)=>b.F('core.if<bool,any,1>',[cond,a,c]);
  const eq=(x,y)=>b.F('equals<real,real>',[x,b.R(y)]);
  function select(rows,key,col,units=true){
    let x=units?b.L(-1):b.R(-1);
    for(let k=rows.length-1;k>=0;k--)x=choose(eq(key,rows[k][0]),units?b.L(rows[k][col]/1000):b.R(rows[k][col]),x);
    return once(x,'Selected source column '+col);
  }
  b.sec('Source size selection','ISO 10664:1999 drive sizes; ISO 14579:2011 head bounds. Development CAD choices within the cited bounds.');
  const series=b.inp('Screw series'),idx=once(b.add(b.mul(series,b.R(100)),b.inp('Metric size index')),'Series size key'),rows=SOURCE_ROWS;
  const nominalR=once(b.div(select(rows,idx,1),b.R(2)),'Nominal shank radius');
  const sr=once(choose(b.inp('Override shank'),b.inp('Shank radius'),nominalR),'Selected shank radius');
  const scale=once(b.div(sr,nominalR),'Custom shank scale');
  const val=(col)=>once(b.mul(select(rows,idx,col),scale),'Scaled source column '+col);
  const pitch=val(2),headR=once(b.div(val(3),b.R(2)),'Head radius'),height=val(4),top=val(5),fillet=val(6),shortNeck=val(7),depth=val(8);
  const threadLength=val(10),shortLengthMax=val(11),web=val(12);
  const crown=val(13),tip=once(choose(eq(series,2),b.sub(b.inp('Length'),height),b.inp('Length')),'Tip from cone-end or underhead plane');
  const longCylinder=b.F('and<bool,bool>',[eq(series,0),b.lt(shortLengthMax,tip)]);
  const neck=once(choose(longCylinder,b.sub(tip,threadLength),shortNeck),'Thread start: short neck or long l minus b');
  const ds=once(choose(eq(b.inp('Drive size'),0),select(rows,idx,9,false),b.inp('Drive size')),'Selected drive size');
  const nominalA=select(DRIVE,ds,1),nominalB=select(DRIVE,ds,2);
  const dr=once(choose(b.inp('Override Torx'),b.inp('Torx radius'),b.div(nominalA,b.R(2))),'Drive major radius');
  const inner=once(b.mul(dr,b.div(nominalB,nominalA)),'Drive minor radius');
  const isInternal=eq(b.inp('Drive family'),0),isTamper=eq(b.inp('Drive family'),1);
  const postNominal=select(catalogue.posts.map(r=>[r.size,r.diameter]),ds,1);
  const postRadius=once(choose(eq(b.inp('Drive family'),1),b.mul(dr,b.div(postNominal,nominalA)),b.mul(inner,b.R(.1))),'Post radius scaled with recess');
  const and=(a,c)=>b.F('and<bool,bool>',[a,c]),or=(a,c)=>b.F('or<bool,bool>',[a,c]);
  let valid=or(isInternal,and(isTamper,b.lt(b.L(0),postNominal)));
  const floorWall=choose(eq(series,2),b.lt(dr,b.add(sr,b.sub(height,depth))),b.B(true));
  valid=and(valid,floorWall);
  for(const condition of [b.lt(b.L(0),nominalR),b.lt(b.L(0),sr),b.lt(b.L(0),dr),b.lt(dr,b.sub(headR,top)),b.lt(neck,tip),b.lt(b.L(0),neck),b.lt(postRadius,inner),b.lt(web,b.sub(height,depth))])valid=and(valid,condition);
  const gate=once(b.sqrt(choose(valid,b.R(1),b.R(-1))),'CHECK FAMILY POST SIZE HEAD WALL AND LENGTH');
  b.sec('Referenced components','One call per component. Basic-profile thread pending actual design-root specification.');
  const cylindrical=K.call(b,head,[headR,height,sr,top,fillet,shortNeck]);
  const pan=K.call(b,panHead,[headR,height,sr,crown,fillet,shortNeck]);
  // Keep the revolved countersunk component short; the native cylinder carries the
  // prescribed shoulder. Longer revolved necks misclassify exterior points in nTop.
  const countersunk=K.call(b,countersunkHead,[headR,height,sr,b.mul(pitch,b.R(.25))]);
  const headBody=b.once(choose(eq(series,0),cylindrical,choose(eq(series,1),pan,countersunk)),'Selected head','implicit');
  const stem=b.once(G.cyl(G.pt(0,0,0),G.pt(b.L(0),b.L(0),neck),sr),'Plain shank extension','implicit');
  const minor=once(b.sub(sr,b.mul(pitch,b.R(5*Math.sqrt(3)/16))),'ISO 68-1 basic minor radius');
  const threadBody=b.once(K.call(b,thread,[sr,minor,pitch,b.div(pitch,b.R(8)),b.mul(b.sub(tip,neck),gate),b.R(Math.sqrt(3))]),'Basic thread','implicit');
  const placedThread=b.once(G.translate(threadBody,b.F('vector<real,real,real>',[b.L(0),b.L(0),neck])),'Thread at neck','implicit');
  const cutter=b.once(K.call(b,drive,[dr,inner,b.mul(dr,b.R(.2)),depth]),'Recess cutting body','implicit');
  const pin=G.cyl(G.pt(0,0,0),G.pt(b.L(0),b.L(0),depth),postRadius);
  const familyCutter=b.once(choose(eq(b.inp('Drive family'),1),G.subtractS(cutter,[pin]),cutter),'Family recess','implicit');
  const placedCutter=b.once(G.translate(familyCutter,b.F('vector<real,real,real>',[b.L(0),b.L(0),b.neg(height)])),'Recess in head','implicit');
  const localBody=b.once(G.subtractS(G.unionS([headBody,stem,placedThread]),[placedCutter]),'Screw at head-end plane','implicit');
  b.VAR('result','Complete local screw','implicit',G.translate(localBody,b.F('vector<real,real,real>',[b.L(0),b.L(0),choose(eq(series,2),height,b.L(0))])));
  return {b,name:'Torx_Local',displayname:'Torx Local Development',outId:'result',dir:path.resolve(__dirname,'..'),
    description:'DEVELOPMENT screw assembly: cylindrical ISO14579:2011, pan ISO14583:2011, countersunk ISO14581:2013 historical. Dimensional bounds plus declared representative CAD profiles. Derived ISO10664:1999 internal contour; Camcar round posts create custom tamper-resistant derivatives. Basic ISO68-1 thread; root/runout/tip simplified. Native cylindrical extension avoids the measured long revolved-neck error. Countersunk datum is top face, length includes head; other series use underhead datum.',
    spec:{imports:K.flatten([head,panHead,countersunkHead,thread,drive]),bbox:[[-.00275,-.00275,-.003],[.00275,.00275,.010]],tolSample:1e-7,
      points:[['head outside',.00275,0,-.0015,0],['top ring',.002,0,-.003,0],['recess void',.0001,0,-.0025,{sign:1}],['solid under recess',.0001,0,-.001,{sign:-1}],['thread crest',.0015,0,.005,0],['thread root',.0015-5*Math.sqrt(3)*.0005/16,0,.00525,0],['tip',.001,0,.010,0]]}};
}
module.exports={build,DRIVE,SCREW};
