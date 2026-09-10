"""Bounded native root blends for the RC appearance model.

Pass the unscaled source fields. Do not pass the fuselage's 0.25 display field.
The returned body replaces the displayed fuselage, wing, and tail combination;
their original named source variables can remain editable and hidden.

The length controls set a cosmetic blend amount, not a certified fillet radius.
No distance-field normalization or aerodynamic inference is performed here.
"""
from __future__ import annotations


CONIC_UNION = "boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]"
SHARP_SUBTRACT = "boolean_subtract<blend_enum,real_field,implicit,list<implicit>>[5.44.0]"
SET_BOUNDS = "set_bounding_box<implicit,bounding_box>"
WING_RAMP = "ramp<real_field,real_field,real_field,real_field,real_field,continuity_enum>"
WING_TRAILING_BLEND_RC_M = .003175


def build_root_blends(r, *, fuselage, panels, x, y, z, half_width,
                      crown_height, chine, scale, S, source, cutters=(),
                      wing_offset=None, wing_offset_source=0.0,
                      tail_span_multiplier=1.0):
    """Return a locally blended source airframe and inspection references.

    ``panels`` maps any subset of Wing, Tailplane, and Fin to native bodies.
    One panel is sufficient for a small fixture. ``cutters`` should contain
    both the complete duct cavity and the diverter slot. They are subtracted
    after every additive blend. Caller adds remaining details and final cuts.

    Default amounts equal half the root section's source thickness parameter
    at the user's 16 ft reference span. The effective source amount is limited
    to one root thickness parameter. Root support extends at most three such
    parameters from the side or crown guide and local panel center plane.
    These are bounded design choices derived from the supplied source rows.
    """
    allowed = {"Wing": "wingRows", "Tailplane": "tailRows", "Fin": "finRows"}
    unknown = set(panels) - set(allowed)
    if not panels or unknown:
        raise ValueError("Provide a nonempty subset of Wing, Tailplane, and Fin.")
    if S <= 0:
        raise ValueError("Source coordinate scale must be positive.")
    reference_span = 2 * max(float(row[0]) for row in source["wingRows"])
    if reference_span <= 0:
        raise ValueError("The source wing span must be positive.")
    rc_metres_per_source_unit = 4.8768 / reference_span

    def var(name, value, kind="real_field", section="Root blend fields"):
        return r.var(name, kind, value, section)

    def maximum(a, b):
        return r.call("max<real_field,real_field>", "real_field", a, b)

    def minimum(a, b):
        return r.call("min<real_field,real_field>", "real_field", a, b)

    def absolute(a):
        return r.call("abs<real_field>", "real_field", a)

    def divide(a, b):
        return r.call("divide<real_field,real_field>", "real_field", a, b)

    taper_count = 0

    def c2(a):
        nonlocal taper_count
        taper_count += 1
        u = var("Root blend taper coordinate " + str(taper_count),
                minimum(r.real(1), maximum(r.real(0), a)))
        return r.mul(r.mul(u, r.mul(u, u)),
                     r.add(r.real(10), r.mul(u, r.add(r.real(-15), r.mul(u, r.real(6))))))

    def ramp(coordinate, start, end):
        if end <= start:
            raise ValueError("A root support transition must have positive length.")
        return c2(r.mul(r.sub(coordinate, r.length(start * S)),
                       r.real(1 / ((end - start) * S), {"length": -1})))

    def distance_support(distance, full_radius, zero_radius):
        return r.sub(r.real(1), ramp(distance, full_radius, zero_radius))

    base = var("Root blend original airframe", r.call(CONIC_UNION, "implicit",
               r.enum("blend_enum", 0), r.length(0), r.list("implicit", [fuselage, *panels.values()])), "implicit")
    bounds = var("Root blend source bounds", r.prop(base, "bounding box"), "bounding_box")
    ay = var("Root blend absolute span", absolute(y))
    side_distance = var("Root blend distance from side guide", absolute(r.sub(ay, half_width)))
    crown_distance = var("Root blend distance from crown guide", absolute(r.sub(z, r.add(crown_height, chine))))
    wing_x = (var("Wing root longitudinal coordinate", r.sub(x, wing_offset))
              if wing_offset is not None and "Wing" in panels else x)
    pairs, controls, supports, effective_amounts, construction = {}, {}, {}, {}, {}
    wing_ramp = None

    for name, panel in panels.items():
        rows = source[allowed[name]]
        root = [float(value) for value in rows[0]]
        thickness_parameter = abs(root[4])
        if thickness_parameter <= 0:
            raise ValueError(name + " root thickness parameter must be positive.")
        leading, trailing = root[1], root[2]
        if trailing <= leading:
            raise ValueError(name + " root chord must be positive.")

        # The support follows actual side/crown guides, not buried root caps.
        # In particular, Fin's artificial z=.30 cap does not locate its blend.
        longitudinal_start = leading - 2 * thickness_parameter
        longitudinal_end = min(4.45, trailing + 2 * thickness_parameter)
        if name == "Wing":
            longitudinal_start = max(-1.4, longitudinal_start)
        full_start = max(leading, longitudinal_start + thickness_parameter * 0.1)
        full_end = min(trailing, longitudinal_end - thickness_parameter * 0.1)
        if full_start >= full_end:
            raise ValueError(name + " root support is too short for this source geometry.")
        support_coordinate = wing_x if name == "Wing" else x
        x_support = r.mul(ramp(support_coordinate, longitudinal_start, full_start),
                          r.sub(r.real(1), ramp(support_coordinate, full_end, longitudinal_end)))
        if name == "Wing":
            # The wing taper moves with its panel. These global gates keep
            # the inlet and fuselage end excluded even after a large edit.
            # At the chosen aft offset both gates leave the local taper intact.
            x_support = minimum(x_support, ramp(x, -1.4, -1.26))
            x_support = minimum(x_support, r.sub(r.real(1),
                ramp(x, 4.45-2*thickness_parameter, 4.45)))
        root_distance = crown_distance if name == "Fin" else side_distance
        cross_coordinate = y if name == "Fin" else z
        cross_distance = absolute(r.sub(cross_coordinate, r.length(root[3] * S)))
        reach_full, reach_zero = 2 * thickness_parameter, 3 * thickness_parameter
        support = var(name + " root compact support", r.mul(x_support,
                      r.mul(distance_support(root_distance, reach_full, reach_zero),
                            distance_support(cross_distance, reach_full, reach_zero))))
        supports[name] = support

        amount_rc = var(name + " root blend size", r.length(0.5 * thickness_parameter * rc_metres_per_source_unit),
                        "real", "Root blend controls")
        size_field_rc = amount_rc
        if name == "Wing":
            # Preserve the existing control name and value as the LE endpoint.
            # icitk_RampImplicit.h orders inputs as field, inMin, inMax,
            # outMin, outMax, continuity. ContinuityLevel::e_C2 is enum 2.
            # Its clamped quintic supports a descending output range.
            trailing_rc = var("Wing TE root blend size", r.length(WING_TRAILING_BLEND_RC_M),
                              "real", "Root blend controls")
            size_field_rc = var("Wing root blend ramp RC", r.call(WING_RAMP, "real_field",
                wing_x, r.length(leading * S), r.length(trailing * S),
                amount_rc, trailing_rc, r.enum("continuity_enum", 2)))
            wing_ramp = {"rc_field": size_field_rc, "leading_control": amount_rc,
                         "trailing_control": trailing_rc, "scale": scale,
                         "offset": wing_offset if wing_offset is not None else r.length(0),
                         "leading_source": leading, "trailing_source": trailing}
        # Keep the operation local even if the editable length is set too large.
        amount = var(name + " root effective blend amount", minimum(r.length(thickness_parameter * S),
                     maximum(r.length(0), divide(size_field_rc, scale))))
        controls[name], effective_amounts[name] = amount_rc, amount
        if name == "Wing":
            wing_ramp["effective_field"] = amount

        # C2 polynomial smooth-min: min(a,b)-max(k-|a-b|,0)^3/(6*k^2).
        # k=6*amount makes the largest field correction equal to amount.
        # Its compact support makes the hard union exact outside the root box.
        # A numerical denominator floor handles zero amount/support safely.
        # Below that floor the correction smoothly tends to zero; it is not
        # a physical minimum blend size or a claimed manufacturing tolerance.
        k = var(name + " root local smoothing width", r.mul(r.mul(amount, r.real(6)), support))
        k_safe = var(name + " root safe smoothing width", maximum(k, r.length(S * 1e-9)))
        overlap = var(name + " root field overlap", maximum(r.length(0), r.sub(k, absolute(r.sub(fuselage, panel)))))
        correction = var(name + " root additive field correction",
                         divide(r.mul(overlap, r.mul(overlap, overlap)), r.mul(r.real(6), r.mul(k_safe, k_safe))))
        pair = var(name + " native root blend", r.call(SET_BOUNDS, "implicit",
                   r.sub(minimum(fuselage, panel), correction), bounds), "implicit", "Native root blends")
        pairs[name] = pair
        construction[name] = {
            "source_row": root, "x_support_source": [longitudinal_start, longitudinal_end],
            "x_full_support_source": [full_start, full_end],
            "full_reach_from_guide_source": reach_full, "zero_reach_from_guide_source": reach_zero,
            "guide": "crown height plus chine" if name == "Fin" else "fuselage half width",
            "cross_center_source": root[3], "default_blend_size_rc_m": 0.5 * thickness_parameter * rc_metres_per_source_unit,
            "effective_max_source_amount": thickness_parameter,
        }
        if name == "Wing":
            construction[name].update(
                x_support_local_source=[longitudinal_start, longitudinal_end],
                x_full_support_local_source=[full_start, full_end],
                x_support_source=[max(-1.4, longitudinal_start+wing_offset_source),
                                  min(4.45, longitudinal_end+wing_offset_source)],
                x_full_support_source=[max(-1.26, full_start+wing_offset_source),
                    min(4.45-2*thickness_parameter, full_end+wing_offset_source)],
                longitudinal_offset_source_default=wing_offset_source,
                placement_basis="Photo-guided RC wing placement; not a production Fury dimension",
                guide_coordinates="Global fuselage X; only the wing longitudinal taper is translated")
            construction[name]["chordwise_ramp"] = {
                "function": WING_RAMP,
                "argument_order": ["Scalar Field", "In Min", "In Max", "Out Min", "Out Max", "Continuity"],
                "continuity_enum": 2, "continuity": "C2 clamped quintic smootherstep",
                "coordinate": "Wing root longitudinal coordinate = Global X minus live wing offset",
                "input_range_source": [leading, trailing],
                "leading_control": "Wing root blend size",
                "leading_control_role": "Leading-edge size; prior control name and default retained",
                "trailing_control": "Wing TE root blend size",
                "leading_default_rc_m": 0.5 * thickness_parameter * rc_metres_per_source_unit,
                "trailing_default_rc_m": WING_TRAILING_BLEND_RC_M,
                "trailing_default_rc_in": .125,
                "rc_field": "Wing root blend ramp RC",
                "effective_field": "Wing root effective blend amount",
                "effective_rule": "Clamp(RC ramp / live scale, 0, root thickness parameter * S)",
                "compact_support_unchanged": True,
                "source_references": [
                    "Measured native Ramp input order and C2 endpoint checks",
                    "Measured native Ramp input order and C2 endpoint checks",
                    "Measured native Ramp input order and C2 endpoint checks"],
                "scope": "Editable RC appearance blend-size field. The endpoint values are not measured fillet radii or aerodynamic data."}
        elif name == "Tailplane":
            construction[name]["span_multiplier_default"] = tail_span_multiplier
            construction[name]["placement_basis"] = "Photo-guided RC HStab span ratio; not a production Fury dimension"

    uncut = var("Root blended airframe before passage cuts", r.call(SET_BOUNDS, "implicit",
                r.either(base, *pairs.values()), bounds), "implicit", "Native root blends")
    result = uncut
    if cutters:
        result = r.call(SHARP_SUBTRACT, "implicit", r.enum("blend_enum", 0), r.length(0),
                        uncut, r.list("implicit", list(cutters)))
    result = var("Root blended airframe native", r.call(SET_BOUNDS, "implicit", result, bounds),
                 "implicit", "Native root blends")
    return {"body": result, "uncut": uncut, "base": base, "pairs": pairs,
            "controls": controls, "supports": supports, "effective_amounts": effective_amounts,
            "bounds": bounds, "construction": construction, "wing_ramp": wing_ramp}
