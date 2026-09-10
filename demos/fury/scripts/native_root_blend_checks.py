"""Append finite baseline checks for the native RC root blends.

Only four scalar roots own the dense evaluations. Their point lists and batch
calls stay embedded, so removing those roots also removes the heavy probes.
No notebook execution or filesystem writes occur in this module.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import BSpline


def add_root_blend_checks(r, blends, guide_info, source, S, *,
                         wing_offset_source=0.0, tail_span_multiplier=1.0):
    """Return dense root names, references, and reproducible probe metadata.

    Positive added-material results prove at least one sampled point lies
    outside the original union and inside the blended union. They do not
    establish surface smoothness or passage clearance. The independent main
    model passage checks must cover the final cavity and diverter subtraction.
    These fixed grids describe the baseline source and guide control values.
    """
    if S <= 0:
        raise ValueError("Source coordinate scale must be positive.")
    if not np.isfinite(wing_offset_source) or not np.isfinite(tail_span_multiplier) or tail_span_multiplier <= 0:
        raise ValueError("Baseline wing offset and positive HStab span multiplier must be finite.")
    before, after = blends["base"], blends["uncut"]
    surfaces = {"Wing": "wingRows", "Tailplane": "tailRows", "Fin": "finRows"}
    names = [name for name in surfaces if name in blends["pairs"]]
    if not names:
        raise ValueError("No native root blends are available to check.")

    curves = {}
    for name in ("Half width", "Crown", "Chine datum"):
        data = guide_info[name]
        gx, gy = np.asarray(data["x"], dtype=float), np.asarray(data["y"], dtype=float)
        if len(gx) != len(gy) or len(gx) < 4 or not np.all(np.diff(gx) > 0):
            raise ValueError("Invalid fitted guide metadata: " + name)
        n = len(gx)
        knots = np.r_[np.zeros(4), np.arange(1, n - 3) / (n - 3), np.ones(4)]
        curves[name] = (BSpline(knots, np.column_stack([gx, gy]), 3), gx[0], gx[-1])

    def guide(name, xx):
        curve, start, end = curves[name]
        u = (xx - start) / (end - start)
        if not 0 <= u <= 1:
            raise ValueError("Root probe is outside a fitted guide: " + name)
        point = curve(u)
        if not np.isclose(point[0], xx, rtol=1e-12, atol=1e-12):
            raise ValueError("Guide X no longer has the assumed affine parameterization.")
        return float(point[1])

    def panel_value(rows, station, column):
        # The baseline panel rows feed the builder's linear transfer functions.
        return float(np.interp(station, [row[0] for row in rows], [row[column] for row in rows]))

    root_grids, outer_points, outer_labels = {}, [], []
    for name in names:
        rows = [[float(value) for value in row] for row in source[surfaces[name]]]
        root = rows[0]
        thickness = abs(root[4])
        leading, trailing = root[1:3]
        if thickness <= 0 or trailing <= leading:
            raise ValueError(name + " has an invalid baseline root section.")
        grid = []
        for chord_fraction in (0.2, 0.5, 0.8):
            xx = leading + chord_fraction * (trailing - leading)
            if name == "Wing":
                xx += wing_offset_source
            if name == "Fin":
                # The actual crown intersection, not the artificial z=.30 cap.
                crown_z = guide("Crown", xx) + guide("Chine datum", xx) - 1
                for sign in (-1, 1):
                    for span_offset in (0.5, 0.8, 1.1, 1.4):
                        for height_offset in (0.25, 0.6, 1.0, 1.4):
                            grid.append([xx, root[3] + sign * span_offset * thickness,
                                         crown_z + height_offset * thickness])
            else:
                width = guide("Half width", xx)
                for sign in (-1, 1):
                    for side_offset in (-0.4, -0.05, 0.3, 0.65):
                        station = width + side_offset * thickness
                        foil_station = station / tail_span_multiplier if name == "Tailplane" else station
                        center = panel_value(rows, foil_station, 3)
                        for height_offset in (-1.0, -0.6, 0.6, 1.0):
                            grid.append([xx, sign * station, center + height_offset * thickness])
        if len(grid) != 96:
            raise RuntimeError("Unexpected root probe count for " + name)
        root_grids[name] = grid

        # Real outer-panel stations from the source, beyond the root support.
        stations = [0.5 * (rows[0][0] + rows[-1][0])]
        if name == "Fin":
            stations.append(rows[0][0] + 0.75 * (rows[-1][0] - rows[0][0]))
        for station in stations:
            le, te = panel_value(rows, station, 1), panel_value(rows, station, 2)
            center, half_scale = panel_value(rows, station, 3), abs(panel_value(rows, station, 4))
            physical_station = station * tail_span_multiplier if name == "Tailplane" else station
            for fraction in (0.2, 0.5, 0.8):
                xx = le + fraction * (te - le)
                if name == "Wing":
                    xx += wing_offset_source
                for height_offset in (-1.0, 0.0, 1.0):
                    if name == "Fin":
                        outer_points.append([xx, center + height_offset * half_scale, station])
                        outer_labels.append(name)
                    else:
                        for sign in (-1, 1):
                            outer_points.append([xx, sign * physical_station, center + height_offset * half_scale])
                            outer_labels.append(name)

    # Root support is identically zero in this forward inlet section.
    inlet_x = -2.8
    inlet_width = guide("Half width", inlet_x)
    for span_fraction in (-0.9, 0.0, 0.9):
        for zz in (-0.8, -0.3, 0.3):
            outer_points.append([inlet_x, span_fraction * inlet_width, zz])
            outer_labels.append("Inlet")

    dense_roots, references = [], {}

    def maximum_check(name, field, points_source):
        # Leave both the batch call and the point list inside the scalar root.
        # No additional named evaluation variable can survive scalar pruning.
        points = r.list("point", [r.point(np.asarray(point) * S) for point in points_source])
        values = r.call("evaluate_field<real_field,list<point>>", "list<real>", field, points)
        result = r.var(name, "real", r.call("max<list<real>>", "real", values), "Checks")
        dense_roots.append(name)
        references[name] = result

    for name in names:
        witness = r.call("min<real_field,real_field>", "real_field", before, r.neg(after))
        maximum_check("CHECK " + name + " root added material", witness, root_grids[name])
    difference = r.call("abs<real_field>", "real_field", r.sub(after, before))
    unchanged_name = "CHECK root blends unchanged outside support"
    maximum_check(unchanged_name, difference, outer_points)

    # These lightweight checks follow the live translated root coordinate.
    # Keep them separate from the dense material witnesses so they remain in
    # the interactive notebook after heavy probe roots are pruned.
    ramp_metadata = None
    ramp = blends.get("wing_ramp")
    if ramp is not None:
        def scalar(operation, *values):
            return r.call(operation + "<" + ",".join("real" for _ in values) + ">", "real", *values)

        def reduce_scalar(operation, values):
            return r.call(operation + "<list<real>>", "real", r.list("real", values))

        def check_scalar(name, value):
            result = r.var(name, "real", value, "Checks")
            references[name] = result
            return result

        check_definitions, sample_records, sampled_rc, effective_residuals = [], [], [], []
        for label, endpoint in (("LE", "leading_control"), ("TE", "trailing_control")):
            name = "CHECK Wing " + label + " root blend size"
            check_scalar(name, ramp[endpoint])
            check_definitions.append({"name": name, "expected": "positive", "units": "RC length"})
        chord = ramp["trailing_source"] - ramp["leading_source"]
        fractions = (-.1, 0.0, .25, .5, .75, 1.0, 1.1)
        for index, fraction in enumerate(fractions):
            local_x = (ramp["leading_source"] + fraction * chord) * S
            point = r.call("point<real,real,real>", "point",
                scalar("add", r.length(local_x), ramp["offset"]), r.length(0), r.length(0))
            point_ref = r.var("Wing root ramp sample point " + str(index), "point", point, "Checks")
            sample_name = "CHECK Wing root ramp RC sample " + str(index)
            sample = check_scalar(sample_name, r.call("evaluate_field<real_field,point>",
                                  "real", ramp["rc_field"], point_ref))
            sampled_rc.append(sample)
            effective = r.call("evaluate_field<real_field,point>", "real", ramp["effective_field"], point_ref)
            effective_residuals.append(scalar("abs", scalar("subtract",
                scalar("multiply", effective, ramp["scale"]), sample)))
            sample_records.append({"index": index, "chord_fraction": fraction,
                "local_x_source": local_x / S, "point": "Live wing offset plus local X, Y=Z=0",
                "check_name": sample_name})
            check_definitions.append({"name": sample_name, "expected": "positive", "units": "RC length"})
        endpoint_residuals = [scalar("abs", scalar("subtract", sampled_rc[index], ramp[endpoint]))
                             for index, endpoint in ((0, "leading_control"), (1, "leading_control"),
                                                     (5, "trailing_control"), (6, "trailing_control"))]
        aggregates = (
            ("CHECK Wing root ramp endpoint residual", reduce_scalar("max", endpoint_residuals), "near_zero"),
            ("CHECK Wing root ramp maximum increase", reduce_scalar("max", [
                scalar("subtract", b, a) for a, b in zip(sampled_rc[:-1], sampled_rc[1:])]), "nonpositive"),
            ("CHECK Wing root ramp minimum RC size", reduce_scalar("min", sampled_rc), "positive"),
            ("CHECK Wing root ramp effective residual", reduce_scalar("max", effective_residuals), "near_zero"),
        )
        for name, value, expected in aggregates:
            check_scalar(name, value)
            check_definitions.append({"name": name, "expected": expected, "units": "RC length"})
        construction = blends["construction"]["Wing"]["chordwise_ramp"]
        ramp_metadata = {
            "field": "Wing root blend ramp RC", "effective_field": "Wing root effective blend amount",
            "leading_control": construction["leading_control"], "trailing_control": construction["trailing_control"],
            "leading_default_rc_m": construction["leading_default_rc_m"],
            "trailing_default_rc_m": construction["trailing_default_rc_m"],
            "trailing_default_rc_in": .125, "continuity_enum": 2,
            "continuity": "C2 clamped native Ramp", "samples": sample_records,
            "check_definitions": check_definitions,
            "numerical_tolerance_rc_m": max(construction["leading_default_rc_m"],
                                             construction["trailing_default_rc_m"]) * 1e-6,
            "tolerance_scope": "Relative numerical check on field values, not a physical fillet tolerance",
            "acceptance": "All values finite and positive; endpoints and outside clamps equal live controls; sampled values do not increase; effective RC values match the ramp at the uncapped baseline.",
            "live_edit_limits": "The decreasing and uncapped checks describe LE >= TE > 0 below the effective source-size cap. Deliberately reversed or capped controls require different acceptance conditions.",
            "geometry_sign_checks": dense_roots,
            "scope": "Native size-field verification and existing finite material/support checks. It does not establish geometric tangency, actual fillet radius, or aerodynamic performance."}

    metadata = {
        "coordinate_units": "normalized source coordinates; multiply by S for native metres",
        "source_unit_to_native_m": S,
        "guide_method": "Actual fitted cubic guide control points; clamped uniform knots; affine X verified at every probe station.",
        "panel_method": "Baseline source-row linear interpolation. Wing X includes its default translation. Tailplane foil station is physical Y divided by the default HStab span multiplier.",
        "wing_longitudinal_offset_source_default": wing_offset_source,
        "hstab_span_multiplier_default": tail_span_multiplier,
        "placement_basis": "Photo-guided RC placement and span choices; not production Fury dimensions.",
        "before_field": "Root blend original airframe",
        "after_field": "Root blended airframe before passage cuts",
        "added_material_expression": "max over root grid of min(before, -after)",
        "added_material_acceptance": "Strictly positive proves a sampled added-material witness for each enabled baseline root blend.",
        "unchanged_expression": "max over outer-panel and inlet points of abs(after-before)",
        "unchanged_numerical_tolerance_native_m": S * 1e-9,
        "tolerance_scope": "Numerical field-equality criterion, not a physical distance or manufacturing tolerance.",
        "root_grids_source": root_grids,
        "root_grid_counts": {name: len(points) for name, points in root_grids.items()},
        "unchanged_points_source": outer_points,
        "unchanged_point_labels": outer_labels,
        "unchanged_point_count": len(outer_points),
        "dense_check_roots": dense_roots,
        "expected_enabled_blends": names,
        "wing_ramp": ramp_metadata,
        "scope": "Finite baseline appearance-geometry checks. Added witnesses do not establish smoothness, fillet radius, aerodynamics, or final passage clearance. Existing main-model checks must cover the final cavity and diverter cuts.",
    }
    return {"dense_roots": dense_roots, "references": references, "metadata": metadata}
