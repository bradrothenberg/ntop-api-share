'use strict';
const path=require('path');
module.exports=(series,family,name,metric=2)=>({build(K){
 const def=K.cb(path.join(__dirname,'cb_Torx.json')),b=K.bloc([]);
 const args=def.inputs.map(i=>{
  const value=structuredClone(i.contents);
  if(i.name==='Screw series')value.value.selected=series;
  if(i.name==='Drive family')value.value.selected=family;
  if(i.name==='Metric size')value.value.selected=metric;
  return value;
 });
 b.VAR('result',name,'implicit',K.call(b,def,args));
 const main={...def};delete main.imports;
 const radius=metric===4?.005:.0031;
 return {b,name,displayname:name,outId:'result',dir:path.resolve(__dirname,'..'),description:'Visual inspection example calling the final Torx custom block unchanged; 10 mm length, chosen native dropdowns.',spec:{imports:[...(def.imports||[]),main],bbox:[[-radius,-radius,-.0033],[radius,radius,.0103]],tolSample:1e-7}};
}});
