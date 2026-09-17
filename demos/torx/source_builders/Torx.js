'use strict';
const path=require('path');
const localBuilder=require('./Torx_Local');
const catalogue=require('./catalogue');
const choice=(labels,selected=0)=>({type:'choice',value:{choices:labels,selected}});
function build(K){
  const q=K.lit,base=localBuilder.build(K);
  const b=K.bloc([
    ['Drive family','choice',{},choice(catalogue.families.map(r=>r.label)),'Native Choice List. Tamper-resistant is a custom cylindrical-head derivative using sourced Camcar post dimensions.'],
    ['Screw series','choice',{},choice(catalogue.series.map(r=>r.label)),'Native Choice List. Additional source-backed head series can be added without changing the placement interface.'],
    ['Metric size','choice',{},choice(catalogue.screws.map(r=>r.label),2),'Native Choice List: nominal diameter and coarse pitch.'],
    ['Drive size','choice',{},choice(['Automatic',...catalogue.drives.map(r=>'T'+r.size)]),'Native Choice List. Automatic uses the metric source row. Tamper-resistant requires a sourced post for the selected drive.'],
    ...base.b.IN.filter(([n])=>!['Drive family','Screw series','Metric size index','Drive size'].includes(n)),
    ['Insertion Point','point',{length:1},q.P3(0,0,0),'Raised heads: centre of underhead seating plane. Countersunk: top-face centre, flush datum.'],
    ['Axis','vector',{},q.V(0,0,1),'Direction towards screw tip. Non-zero; magnitude is ignored.'],
    ['Tangent Reference','vector',{},q.V(1,0,0),'Projected into seating plane to define lobe orientation; cannot be parallel to Axis.'],
    ['Clocking Angle','real',{angle:1},q.A(0),'Additional right-handed rotation about Axis.']
  ]);
  const local=K.cb(path.join(__dirname,'cb_Torx_Local.json')),place=K.cb(path.join(__dirname,'cb_Place_Screw.json'));
  b.sec('Dropdown selections','Native Choice List inputs select stable source identifiers; sizes never require numeric code entry.');
  const select=(name,values)=>b.once(b.F('core.select_by_choice<choice,list_interface>',[b.inp(name),b.LIST('integer',values.map(b.I))]),name+' selection','integer');
  const family=select('Drive family',catalogue.families.map(r=>r.id));
  const series=select('Screw series',catalogue.series.map(r=>r.id));
  const size=select('Metric size',catalogue.screws.map(r=>r.id));
  const drive=select('Drive size',[0,...catalogue.drives.map(r=>r.size)]);
  b.sec('Referenced screw','A single local assembly call, followed by an independent placement call.');
  const mapped={'Drive family':family,'Screw series':series,'Metric size index':size,'Drive size':drive};
  const args=base.b.IN.map(([name])=>mapped[name]||b.inp(name));
  const screw=b.once(K.call(b,local,args),'Local screw','implicit');
  b.VAR('result','Torx','implicit',K.call(b,place,[screw,b.inp('Insertion Point'),b.inp('Axis'),b.inp('Tangent Reference'),b.inp('Clocking Angle')]));
  return {b,name:'Torx',displayname:'Torx',outId:'result',dir:path.resolve(__dirname,'..'),
    description:'DEVELOPMENT COMPLETE SCREW. Native Choice List family, series, metric and drive size. Internal and tamper-resistant derived drives. Cylindrical ISO14579:2011 M2-M20, pan ISO14583:2011 M2-M10, historical countersunk ISO14581:2013 M2-M10. Basic ISO68-1 thread; actual root/runout and tip remain simplified. Independent radius overrides. Raised heads use underhead datum/length; countersunk uses flush top datum and total length. No manufacturing conformity claim.',
    spec:{imports:K.flatten([local,place]),bbox:base.spec.bbox,tolSample:1e-7,points:base.spec.points}};
}
module.exports={build};
