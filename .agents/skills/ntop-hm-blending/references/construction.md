# Construction and mathematical limits

## Field convention and source

Use negative values inside and positive values outside. Let F and W be compatible
length-valued fuselage and wing fields. A length unit does not establish the
signed-distance property. Rescaling either field changes the blend even if its
own zero surface stays fixed.

The averaging operator is from Yildiz, Krishnamurthy, and Akleman,
*Holder-Minkowski transcendental operators for associative averaging in implicit
modeling*, Computer-Aided Design 202 (2027), 104159, available online
28 September 2026: [DOI](https://doi.org/10.1016/j.cad.2026.104159).
Eq.20 supplies the weighted operator. The compact union, width taper, and
crown/keel correction below are separate engineering constructions.

## Compact union and longitudinal support

For k>0, define

~~~text
h = max(1 - abs(F-W)/k, 0)
U_k = min(F,W) - k*h^3*(4-h)/16
~~~

For k=0, use exactly min(F,W). Reject negative widths.

For smooth inputs and positive width, the correction cancels the min cusp through
second derivatives. It vanishes when abs(F-W)>=k. The width is a field parameter,
not a measured fillet radius.

Define a quintic ramp using t=clamp(s,0,1):

~~~text
S(s) = t^3*(10 - 15*t + 6*t^2)
a(x) = 1 - S((x-x_start)/(x_end-x_start))
k_i(x) = base_width_i * a(x)
~~~

Require x_end>x_start. Inspect the region where k reaches zero. A smooth taper
does not prove continuity at a surviving F=W source intersection.

## Crown and keel anchoring

Let z_plus(x) and z_minus(x) be actual source surface heights on the centerplane
y=0, with z_plus>z_minus. Build a separate correction for each candidate U_i:

~~~text
E_plus_i(x)  = U_i(x, 0, z_plus(x))
E_minus_i(x) = U_i(x, 0, z_minus(x))
t(x,z) = S((z-z_minus(x))/(z_plus(x)-z_minus(x)))
A(y) = exp(-(y/sigma)^2), sigma>0
C_i(x,y,z) = U_i(x,y,z)
             - A(y) * (t*E_plus_i + (1-t)*E_minus_i)
~~~

At either anchor, A=1 and t is 1 or 0, so C_i=0. If all candidates share these
zeros, HM preserves them. This fixes anchor curves, not the whole crown surface.
Check off-center heights, slopes, and curvature independently.

Evaluate E_plus and E_minus by substitution into the source field expressions or
a verified field-composition operation. Evaluating one fixed point produces a
scalar, not an x-dependent anchor field.

Do not divide by a vanishing crown-to-keel gap at a fuselage end. Define a valid
anchor domain and a transition appropriate to the actual end geometry. The
example uses a positive radicand floor for finite evaluation; that floor is not
a true fuselage surface outside its domain.

The Gaussian has no finite support boundary. Its correction can be very small
outboard but is not exactly zero. If exact preservation is required, use a
sufficiently broad smooth compact support and recheck its transition shoulders.
Anchoring can cut into the original wing or fuselage and can change the ordering
of the candidate fields. Do not call them nested enclosing envelopes without
checking.

## HM Eq.20

For candidate fields C_i, positive reference length L, finite log weights w_i,
and p!=0:

~~~text
f_i = C_i/L
H = L/p * (LSE(p*(f_i+w_i)) - LSE(p*w_i))
LSE(v) = max(v) + log(sum(exp(v-max(v))))
~~~

For p=0 with fixed finite w_i, H=mean(C_i). All exponential and logarithm inputs
must be dimensionless. Do not silently approximate a broad neighborhood of p=0
with the mean. Measure small-p cancellation and use expm1/log1p, higher precision,
or a stated supported parameter range if needed. The portable reference uses
expm1/log1p when the centered field logits are small.

Equivalently, alpha_i=exp(p*w_i)/sum(exp(p*w_j)) are positive mixing weights.
At each spatial point:

~~~text
min(C_i) <= H <= max(C_i)
H(C,C,...,C) = C
~~~

Thus common zeros and a common field outside a support region survive. This does
not prove that the zero surface encloses the original primitives. With equal
log weights, p controls the bias toward the smaller or larger candidate values.
With unequal log weights, p also changes alpha.

The matched linear control is sum(alpha_i*C_i), using the same alpha, not an
arbitrary 50/50 average. In the example w=[0, 0.75*S_aft] and p=-4, so the broad
candidate's alpha=1/(1+exp(3*S_aft)).

For hierarchical accumulation at a fixed spatial point and the same p, retain
both log numerator and log denominator:

~~~text
N_group = LSE(p*(f_i+w_i))
D_group = LSE(p*w_i)
N_combined = LSE(N_group_1, N_group_2, ...)
D_combined = LSE(D_group_1, D_group_2, ...)
~~~

Averaging already normalized group outputs with equal group weights loses group
mass and generally changes the result. At p=0, retain sums and counts.

## Continuity versus fairness

Eq.20 permits spatial p and log weights. Smooth variation is required if smooth
derivatives are required. Their derivatives enter the resulting gradient and
curvature. The constant-parameter gradient argument in paper section 5.2 does
not directly establish a bound for this spatial construction.

A C2 field with nonzero gradient has a locally C2 zero surface. It can still have
a smooth hump or a concentrated curvature peak. Check surface-normal curvature,
not just the field Hessian, which depends on the field's scale. None of these
mathematical properties establishes aerodynamic performance.
