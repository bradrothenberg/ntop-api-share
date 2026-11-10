"""Scalar reference formulas. No nTop imports; lengths share one explicit unit."""
from __future__ import annotations

import math
from collections.abc import Sequence


def smootherstep(value: float) -> float:
    """Clamped C2 ramp from zero to one."""
    t = min(max(value, 0.0), 1.0)
    return t**3 * (10.0 - 15.0*t + 6.0*t*t)


def compact_union(first: float, second: float, width: float) -> float:
    """Quartic compact smooth minimum, with exact minimum at zero width."""
    if not all(math.isfinite(v) for v in (first, second, width)) or width < 0:
        raise ValueError("Fields must be finite and width must be nonnegative")
    if width == 0:
        return min(first, second)
    h = max(1.0 - abs(first-second)/width, 0.0)
    return min(first, second) - width*h**3*(4.0-h)/16.0


def anchor_correction(candidate: float, crown_residual: float,
                      keel_residual: float, y: float, z: float,
                      crown: float, keel: float, sigma: float) -> float:
    """Correct one candidate using residuals evaluated at its true anchors.

    Residuals are values of THIS candidate at (x,0,crown) and (x,0,keel).
    Anchor substitution and the x-dependent geometry remain the caller's job.
    """
    if not all(math.isfinite(v) for v in (
        candidate, crown_residual, keel_residual, y, z, crown, keel, sigma
    )) or sigma <= 0 or crown <= keel:
        raise ValueError("Require finite inputs, sigma>0, and crown>keel")
    t = smootherstep((z-keel)/(crown-keel))
    lateral = math.exp(-(y/sigma)**2)
    return candidate - lateral*(t*crown_residual + (1.0-t)*keel_residual)


def _parameters(fields: Sequence[float], p: float,
                log_weights: Sequence[float] | None, length: float):
    values = tuple(float(v) for v in fields)
    weights = ((0.0,)*len(values) if log_weights is None
               else tuple(float(w) for w in log_weights))
    if not values or len(values) != len(weights):
        raise ValueError("Require nonempty fields and one log weight per field")
    if not all(math.isfinite(v) for v in (*values, *weights, p, length)):
        raise ValueError("All fields and parameters must be finite")
    if length <= 0:
        raise ValueError("Reference length must be positive")
    return values, weights


def effective_weights(p: float, log_weights: Sequence[float]) -> tuple[float, ...]:
    """Positive Eq.20 weights after normalization; p=0 gives equal weights."""
    weights = tuple(log_weights)
    _parameters((0.0,)*len(weights), p, weights, 1.0)
    logits = [p*w for w in weights]
    if not all(math.isfinite(v) for v in logits):
        raise ValueError("Weight logits exceed the floating-point range")
    maximum = max(logits)
    terms = [math.exp(v-maximum) for v in logits]
    total = math.fsum(terms)
    return tuple(v/total for v in terms)


def _lse(logits: Sequence[float]) -> float:
    maximum = max(logits)
    return maximum + math.log(math.fsum(math.exp(v-maximum) for v in logits))


def hm_average(fields: Sequence[float], p: float,
               log_weights: Sequence[float] | None = None,
               length: float = 1.0) -> float:
    """Eq.20 with length-valued fields and dimensionless p and log weights.

    The exact p=0 limit assumes finite log weights held fixed. The small-logit
    branch uses expm1/log1p to avoid cancellation; it is not a mean approximation.
    Extremely large, unrepresentable intermediate logits raise ValueError.
    """
    values, weights = _parameters(fields, p, log_weights, length)
    if min(values) == max(values):
        return values[0]
    center = math.fsum(v/len(values) for v in values)
    if p == 0:
        return center
    delta = [p*((v-center)/length) for v in values]
    weight_logits = [p*w for w in weights]
    if not all(math.isfinite(v) for v in (*delta, *weight_logits)):
        raise ValueError("Field or weight logits exceed the floating-point range")
    if max(abs(v) for v in delta) <= 0.5:
        alpha = effective_weights(p, weights)
        change = math.fsum(a*math.expm1(d) for a, d in zip(alpha, delta))
        return center + length*(math.log1p(change)/p)
    shift = max(weight_logits)
    denominator = [v-shift for v in weight_logits]
    numerator = [w+d for w, d in zip(denominator, delta)]
    if not all(math.isfinite(v) for v in (*numerator, *denominator)):
        raise ValueError("Shifted logits exceed the floating-point range")
    return center + length*((_lse(numerator)-_lse(denominator))/p)


def linear_average(fields: Sequence[float], p: float,
                   log_weights: Sequence[float] | None = None) -> float:
    """Control average using the same effective weights as Eq.20."""
    values, weights = _parameters(fields, p, log_weights, 1.0)
    return math.fsum(a*v for a, v in zip(effective_weights(p, weights), values))
