'use strict';
/* Generic flat-root external helical thread kernel. No standard or tolerance-class claim.
 * The radius law is an exact zero-set construction, not Euclidean signed distance.
 * Local axis +Z; 0 <= z <= Length; right-handed crest z = Pitch*theta/(2*pi) + k*Pitch.
 * Valid inputs: Major Radius > Minor Radius > 0, Pitch/Length/Flank Slope > 0,
 * 0 <= Crest Width < Pitch, (Major-Minor)/Slope <= (Pitch-Crest Width)/2.
 * All coefficients remain runtime inputs. Demonstration defaults are candidates only. */
const DEFAULTS = {
  'Major Radius': 0.003, 'Minor Radius': 0.0025, Pitch: 0.001,
  'Crest Width': 0.000125, Length: 0.010, 'Flank Slope': Math.sqrt(3),
};
function build(K) {
  const inputs = Object.entries(DEFAULTS).map(([name, value]) => [name, 'real',
    name === 'Flank Slope' ? {} : {length: 1},
    name === 'Flank Slope' ? K.lit.R(value) : K.lit.L(value),
    name === 'Flank Slope' ? 'Positive radial change per axial change on a flank. Candidate default sqrt(3).' :
      'Positive SI length. Demonstration default only; no thread-standard conformance claimed.']);
  const b = K.bloc(inputs), G = K.geo(b);
  const {F, VAR, ref, inp, R, L, A, X, fmul, fadd, fsub, fdiv} = b;
  const fmin = (a,c) => F('min<real_field,real_field>',[a,c]);
  const fmax = (a,c) => F('max<real_field,real_field>',[a,c]);
  b.sec('Helical coordinates', 'An analytic periodic phase; graph size is independent of turn count.');
  VAR('th_theta','Polar angle','real_field',F('atan2<real_field,real_field>',[X('y',{length:1}),X('x',{length:1})]));
  VAR('th_angle','Helical phase','real_field',fsub(fmul(fdiv(X('z',{length:1}),inp('Pitch')),A(2*Math.PI)),ref('th_theta')));
  VAR('th_cos','Periodic cosine','real_field',F('cos<real_field>',[ref('th_angle')]));
  VAR('th_phase','Axial distance from crest centre','real_field',fmul(fdiv(F('acos<real_field>',[ref('th_cos')]),A(2*Math.PI)),inp('Pitch')));
  b.sec('Axial profile', 'Flat crest and flat root joined by straight flanks; generic profile parameters.');
  VAR('th_drop','Flank radial drop','real_field',fmul(fmax(fsub(ref('th_phase'),b.div(inp('Crest Width'),R(2))),L(0)),inp('Flank Slope')));
  VAR('th_radius','Thread surface radius','real_field',fmax(inp('Minor Radius'),fsub(inp('Major Radius'),ref('th_drop'))));
  VAR('th_r','Cylindrical radius','real_field',F('sqrt<real_field>',[fadd(fmul(X('x',{length:1}),X('x',{length:1})),fmul(X('y',{length:1}),X('y',{length:1})))]));
  VAR('th_radial','Radial residual','real_field',fsub(ref('th_r'),ref('th_radius')));
  b.sec('Length and bounds', 'Flat ends at z=0 and z=Length. No runout or lead-in is implied.');
  VAR('th_capped','Capped field','real_field',fmax(ref('th_radial'),fmax(fmul(X('z',{length:1}),R(-1)),fsub(X('z',{length:1}),inp('Length')))));
  VAR('th_box','Driven bounds','bounding_box',G.bbox(G.pt(b.neg(inp('Major Radius')),b.neg(inp('Major Radius')),L(0)),G.pt(inp('Major Radius'),inp('Major Radius'),inp('Length'))));
  VAR('Thread','Thread','implicit',b.SBB(ref('th_capped'),ref('th_box')));
  const recipe = b.recipe('Metric Thread Kernel',
    'Generic parametric external thread with straight flanks and flat root/crest, along local +Z. Exact helical zero set; field is radial residual with axial caps, not Euclidean distance. No standards conformance claimed. No runout or lead-in.', 'Thread');
  return {b, recipe, outId:'Thread', defaults:DEFAULTS};
}
function radius(z,theta,d=DEFAULTS) {
  const p=d.Pitch, t=z/p-theta/(2*Math.PI);
  const phase=Math.abs(t-Math.round(t))*p;
  return Math.max(d['Minor Radius'],d['Major Radius']-Math.max(phase-d['Crest Width']/2,0)*d['Flank Slope']);
}
function field(x,y,z,d=DEFAULTS) {
  return Math.max(Math.hypot(x,y)-radius(z,Math.atan2(y,x),d),-z,z-d.Length);
}
module.exports={build,DEFAULTS,radius,field};
