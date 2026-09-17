'use strict';
// Stable identifiers and source facts. Values are millimetres unless stated otherwise.
// Geometry builders consume these facts; no geometry is evaluated in this catalogue.
const drives = [[6,1.75,1.27],[8,2.4,1.75],[10,2.8,2.05],[15,3.35,2.4],[20,3.95,2.85],[25,4.5,3.25],[30,5.6,4.05],[40,6.75,4.85],[45,7.93,5.64],[50,8.95,6.45],[55,11.35,8.05],[60,13.45,9.6],[70,15.7,11.2],[80,17.75,12.8],[90,20.2,14.4],[100,22.4,16]].map(([size,A,B])=>({size,A,B,source:'ISO 10664:1999, Table 1; supplied full PDF',role:'nominal recess A and B',contour:'Annex A informative convex radius 0.1 A chosen; concave radius solved for tangency'}));
const families=[{id:0,label:'Internal Torx',implemented:true,source:'ISO 10664:1999, Table 1 and informative Annex A'},{id:1,label:'Tamper-resistant Torx',implemented:true,source:'Camcar TMH-642A, round post D REF; derived custom screw'}];
const series=[{id:0,label:'Cylindrical / ISO 14579:2011',source:'ISO 14579:2011'},{id:1,label:'Pan / ISO 14583:2011',source:'ISO 14583:2011'},{id:2,label:'Countersunk / ISO 14581:2013',source:'ISO 14581:2013, historical'}];
const screwSource=require('../reference/series_expansion/ISO14579_rows.json');
const screws=screwSource.rows.map((row,id)=>({...row,id,label:'M'+row.d+' x '+row.P+(row.nonpreferred?' (non-preferred)':''),source:screwSource.source.title+', printed page '+row.source_printed_page}));
const panSource=require('../reference/series_expansion/ISO14583_rows.json');
const countersunkSource=require('../reference/series_expansion/ISO14581_2013_rows.json');
for(const r of panSource.rows)if(!screws.some(s=>s.d===r.d))screws.push({...r,id:screws.length,label:'M'+r.d+' x '+r.P+' (pan/countersunk)',source:panSource.source.title});
const pan=panSource.rows.map(r=>({...r,id:screws.find(s=>s.d===r.d).id}));
const countersunk=countersunkSource.rows.map(r=>({...r,id:screws.find(s=>s.d===r.d).id}));
// Each post belongs to its source drive size, never to a gauge-hole diameter.
const posts=[[8,.584],[10,.762],[15,1.016],[25,1.778],[40,2.642],[45,3.175],[55,4.572]].map(([size,diameter])=>({size,diameter,source:'Camcar TMH-642A, PDF page 102, D REF',role:'reference round post diameter',heightPolicy:'Top approximately at head top; CAD choice flush',adaptation:'Original sheet is button head; reused as an explicit custom cylindrical-head derivative'}));
for(const [size,inch] of [[20,.055],[50,.140],[60,.211]])posts.push({size,diameter:inch*25.4,source:'Camcar TXH-203B, PDF page 18, D REF',sourceInches:inch,role:'reference round post diameter',heightPolicy:'Top approximately at head top; CAD choice flush',adaptation:'Original sheet is button head; custom cylindrical-head derivative'});
posts.push({size:30,diameter:2.29,source:'Camcar TMH-603B, PDF page 86, C DIA REF',role:'reference round post diameter',heightPolicy:'Top approximately at head top; CAD choice flush',adaptation:'Source post reused in a custom cylindrical-head derivative'});
posts.sort((a,b)=>a.size-b.size);
module.exports={schemaVersion:1,drives,families,series,posts,screws,pan,countersunk,cylindrical:screwSource.rows.map(r=>({...r,id:screws.find(s=>s.d===r.d).id}))};
