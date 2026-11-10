"""Illustrative three-height wing example, evaluated one point at a time.

All coordinates and returned fields use mm. These fields are not signed distance.
This is a reference for native graph verification, not a notebook generator.
"""
from __future__ import annotations

import math

from blend_reference import (
    anchor_correction, compact_union, hm_average, linear_average, smootherstep,
)

OFFSETS_MM = {"mid": 0.0, "upper": 10.5, "lower": -10.5}
REFERENCE_LENGTH_MM = 10.0


def primitive_fields(point, offset_mm=0.0):
    x, y, z = point
    smooth_span = math.sqrt(y*y+2.0**2)-2.0
    chord = 70.0/(1.0+(1.0/0.55-1.0)*(y/110.0)**2)
    leading_edge = -25.0+smooth_span*math.tan(math.radians(20.0))
    u = (x-leading_edge)/chord
    decay = (1.0-2.0*0.3)/(0.3*0.7)
    qmax = 0.3*0.7*math.exp(-decay*0.3)
    local_scale = 0.06/math.sqrt(qmax)*chord
    q = u*(1.0-u)*math.exp(-decay*u)
    base = ((z-offset_mm)/local_scale)**2-q+qmax*(y/110.0)**16
    wing = base*local_scale/(2.0*math.sqrt(qmax))*math.exp(decay*(u-0.3))
    fuselage = ((x/92.5)**8+(y*y+z*z)/17.5**2-1.0)*17.5/2.0
    return fuselage, wing


def candidate(point, offset_mm, width_mm):
    x, y, z = point
    f, w = primitive_fields(point, offset_mm)
    width = width_mm*(1.0-smootherstep((x-25.0)/40.0))
    crown = 17.5*math.sqrt(max(1.0-(x/92.5)**8, 1e-10))
    wt = primitive_fields((x, 0.0, crown), offset_mm)[1]
    wb = primitive_fields((x, 0.0, -crown), offset_mm)[1]
    # This matches the historical native graph, including its end-domain guard.
    # Zero is the fuselage anchor value only in the true crown/keel domain.
    return anchor_correction(
        compact_union(f, w, width),
        compact_union(0.0, wt, width), compact_union(0.0, wb, width),
        y, z, crown, -crown, 8.0,
    )


def fields(point, offset_mm=0.0, p=-4.0):
    f, w = primitive_fields(point, offset_mm)
    small = candidate(point, offset_mm, 4.0)
    large = candidate(point, offset_mm, 9.0)
    weights = (0.0, 0.75*smootherstep((point[0]-25.0)/40.0))
    return {
        "fuselage": f, "wing": w, "small": small, "large": large,
        "single": candidate(point, offset_mm, 6.5),
        "linear": linear_average((small, large), p, weights),
        "hm": hm_average((small, large), p, weights, REFERENCE_LENGTH_MM),
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--position", choices=OFFSETS_MM, default="upper")
    parser.add_argument("--point", nargs=3, type=float, default=(0, 18, 8),
                        metavar=("X_MM", "Y_MM", "Z_MM"))
    parser.add_argument("--p", type=float, default=-4.0)
    args = parser.parse_args()
    print(json.dumps({
        "position": args.position, "point_mm": args.point,
        "field_units": "mm",
        "fields": fields(args.point, OFFSETS_MM[args.position], args.p),
    }, indent=2))
