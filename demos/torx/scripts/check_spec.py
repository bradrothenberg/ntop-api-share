"""Check the yardstick against itself, before anything native runs.

A mirror that agrees with the notebook proves nothing if it was never checked on
its own terms. Every test here is independent of nTop and of the recipe: it
recomputes a mirror value a second way, or asserts an invariant the construction
must satisfy whatever the numbers are.

Run it with `python check_spec.py`. It exits non-zero on the first failure.
"""

import json
import math
import sys
from pathlib import Path

import torx_catalogue as cat
import torx_spec as spec

TOL = 1e-12          # agreement required between two exact routes to the same value
GEOMETRY_TOL = 1e-9  # agreement required for a numerically solved cross-check


class Checks:
    def __init__(self):
        self.rows = []

    def close(self, name, got, want, tol=TOL, units=""):
        delta = abs(got - want)
        self.rows.append({"check": name, "got": got, "want": want,
                          "delta": delta, "tolerance": tol, "units": units,
                          "pass": delta <= tol})

    def true(self, name, value, detail=""):
        self.rows.append({"check": name, "pass": bool(value), "detail": detail})

    def report(self):
        failed = [r for r in self.rows if not r["pass"]]
        worst = max((r["delta"] for r in self.rows if "delta" in r), default=0.0)
        return {"checks": len(self.rows), "failed": len(failed),
                "worst_delta": worst, "failures": failed[:10], "rows": self.rows}


# --------------------------------------------------------------------------
def check_contour(c):
    """The recess contour: exact A and B, tangency, and sixfold symmetry."""
    for drive in cat.DRIVES:
        A, Bm = drive["A"], drive["B"]
        re = 0.1 * A
        ri = spec.concave_radius(A, Bm, re)
        tag = "T%d" % drive["size"]

        # 1. the declared nominal dimensions come back exactly
        c.close("%s lobe tip is A/2" % tag, spec.contour_radius(0.0, A, Bm, re),
                A / 2, units="mm")
        c.close("%s valley is B/2" % tag,
                spec.contour_radius(math.pi / 6, A, Bm, re), Bm / 2, units="mm")

        # 2. external tangency: the centre distance equals the sum of the radii
        cc = A / 2 - re
        d = Bm / 2 + ri
        centre_distance = math.sqrt(cc * cc + d * d - 2 * cc * d * spec.COS30)
        c.close("%s arcs are externally tangent" % tag, centre_distance, re + ri,
                tol=GEOMETRY_TOL, units="mm")

        # 3. the two arcs return the same radius at the handover angle
        t = spec.contour_transition_angle(A, Bm, re)
        convex, concave = spec.contour_branches(t, A, Bm, re)
        c.close("%s contour is continuous at the junction" % tag, convex, concave,
                tol=GEOMETRY_TOL, units="mm")

        # 4. sixfold rotational and mirror symmetry
        for theta in (0.07, 0.19, 0.31, 0.47):
            r0 = spec.contour_radius(theta, A, Bm, re)
            c.close("%s sixfold symmetry at %.2f rad" % (tag, theta),
                    spec.contour_radius(theta + math.pi / 3, A, Bm, re), r0,
                    tol=GEOMETRY_TOL, units="mm")
            c.close("%s mirror symmetry at %.2f rad" % (tag, theta),
                    spec.contour_radius(-theta, A, Bm, re), r0,
                    tol=GEOMETRY_TOL, units="mm")

        # 5. the contour stays between B/2 and A/2 everywhere
        radii = [spec.contour_radius(k * math.pi / 3000, A, Bm, re)
                 for k in range(1001)]
        c.true("%s contour stays within B/2 .. A/2" % tag,
               min(radii) >= Bm / 2 - 1e-12 and max(radii) <= A / 2 + 1e-12,
               "min %.9f max %.9f" % (min(radii), max(radii)))

        # 6. the concave radius solved numerically agrees with the closed form
        def gap(x):
            dd = Bm / 2 + x
            return math.sqrt(cc * cc + dd * dd - 2 * cc * dd * spec.COS30) - (re + x)
        lo, hi = ri * 0.5, ri * 1.5
        if gap(lo) * gap(hi) < 0:
            for _ in range(200):
                mid = (lo + hi) / 2
                if gap(lo) * gap(mid) <= 0:
                    hi = mid
                else:
                    lo = mid
            c.close("%s concave radius by bisection" % tag, (lo + hi) / 2, ri,
                    tol=GEOMETRY_TOL, units="mm")


def check_thread(c):
    """The thread law: crest, root, flank slope and helical periodicity."""
    cfg = spec.Configuration()
    major, minor = cfg.shank_radius, cfg.minor_radius
    pitch, crest, slope = cfg.pitch, cfg.crest_width, math.sqrt(3)
    f = lambda z, th: spec.thread_radius(z, th, major, minor, pitch, crest, slope)

    c.close("ISO 68-1 basic minor radius", minor,
            major - pitch * 5 * math.sqrt(3) / 16, units="mm")
    c.close("crest at an integer turn", f(3 * pitch, 0.0), major, units="mm")
    c.close("root at a half turn", f(3.5 * pitch, 0.0), minor, units="mm")
    c.close("axial period is the pitch", f(3.137 * pitch, 0.0), f(4.137 * pitch, 0.0),
            units="mm")
    c.close("angular period is 2 pi", f(3.137 * pitch, 0.4),
            f(3.137 * pitch, 0.4 + 2 * math.pi), units="mm")
    # the crest follows z = P theta / (2 pi) + k P
    for theta in (0.0, 0.7, 2.1, 4.9):
        c.close("crest follows the helix at theta = %.2f" % theta,
                f(3 * pitch + pitch * theta / (2 * math.pi), theta), major, units="mm")
    # the flank is straight with the declared slope
    phase_a, phase_b = crest / 2 + 0.01 * pitch, crest / 2 + 0.02 * pitch
    ra = f(3 * pitch + phase_a, 0.0)
    rb = f(3 * pitch + phase_b, 0.0)
    c.close("flank slope is the declared one", (ra - rb) / (phase_b - phase_a), slope)
    c.true("the profile never exceeds the major radius",
           all(f(z / 997.0 * pitch * 3, 0.3) <= major + 1e-15 for z in range(998)))
    c.true("the profile never falls below the minor radius",
           all(f(z / 997.0 * pitch * 3, 0.3) >= minor - 1e-15 for z in range(998)))


def check_placement(c):
    """The placement frame is orthonormal, right-handed and rigid."""
    origin, axis, tangent, clock = spec.OBLIQUE_PLACEMENT
    x, y, z = spec.frame(axis, tangent, clock)
    for name, v in (("x", x), ("y", y), ("z", z)):
        c.close("placement %s axis is a unit vector" % name, spec._norm(v), 1.0,
                tol=GEOMETRY_TOL)
    c.close("placement x . y", sum(x[i] * y[i] for i in range(3)), 0.0, tol=GEOMETRY_TOL)
    c.close("placement y . z", sum(y[i] * z[i] for i in range(3)), 0.0, tol=GEOMETRY_TOL)
    c.close("placement z . x", sum(z[i] * x[i] for i in range(3)), 0.0, tol=GEOMETRY_TOL)
    cross = spec._cross(x, y)
    c.close("the frame is right-handed", sum(cross[i] * z[i] for i in range(3)), 1.0,
            tol=GEOMETRY_TOL)
    c.close("local +Z follows Axis", sum(z[i] * spec._unit(axis)[i] for i in range(3)),
            1.0, tol=GEOMETRY_TOL)

    # rigidity: every pairwise distance survives the map
    pts = [(1.0, 2.0, 3.0), (-4.0, 0.5, 7.25), (0.0, 0.0, 0.0), (2.5, -3.5, -1.0)]
    placed = [spec.place(p, origin, axis, tangent, clock) for p in pts]
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d0 = math.dist(pts[i], pts[j])
            d1 = math.dist(placed[i], placed[j])
            c.close("placement preserves distance %d-%d" % (i, j), d1, d0,
                    tol=GEOMETRY_TOL, units="mm")
    c.close("the insertion point carries the local origin",
            math.dist(spec.place((0, 0, 0), origin, axis, tangent, clock), origin), 0.0,
            tol=GEOMETRY_TOL, units="mm")
    # zero clocking on the identity frame must be the identity map
    p = (1.5, -2.5, 4.0)
    c.close("the identity placement is the identity map",
            math.dist(spec.place(p, *spec.IDENTITY_PLACEMENT), p), 0.0, units="mm")
    # a tangent parallel to the axis is refused, not guessed
    try:
        spec.frame((0, 0, 1), (0, 0, 2), 0.0)
        c.true("a parallel tangent is refused", False, "it was accepted")
    except ValueError:
        c.true("a parallel tangent is refused", True)
    try:
        spec.frame((0, 0, 0), (1, 0, 0), 0.0)
        c.true("a zero axis is refused", False, "it was accepted")
    except ValueError:
        c.true("a zero axis is refused", True)


def check_source_fidelity(c):
    """The resolved configuration equals the printed source row, exactly."""
    m3 = next(r for r in cat.CYLINDRICAL if r["d"] == 3)
    cfg = spec.Configuration()          # the block's own defaults
    c.close("M3 nominal shank radius", cfg.shank_radius, m3["d"] / 2, units="mm")
    c.close("M3 coarse pitch", cfg.pitch, m3["P"], units="mm")
    c.close("M3 head radius", cfg.head_radius, m3["dk_max_plain"] / 2, units="mm")
    c.close("M3 head height", cfg.head_height, m3["k_max"], units="mm")
    c.close("M3 top round", cfg.top_round, m3["v_max"], units="mm")
    c.close("M3 underhead fillet", cfg.fillet, m3["r_min"], units="mm")
    c.close("M3 short neck is 2P", cfg.short_neck, 2 * m3["P"], units="mm")
    c.close("M3 recess depth", cfg.depth, m3["t_max"], units="mm")
    c.true("M3 automatic drive is the source row's", cfg.drive_size == m3["drive"],
           "got T%d, source says T%d" % (cfg.drive_size, m3["drive"]))
    t10 = next(r for r in cat.DRIVES if r["size"] == 10)
    c.close("T10 recess major radius", cfg.recess_radius, t10["A"] / 2, units="mm")
    c.close("T10 recess minor radius", cfg.recess_inner, t10["B"] / 2, units="mm")
    c.close("the recess keeps the source A/B ratio",
            cfg.recess_inner / cfg.recess_radius, t10["B"] / t10["A"])

    # an override rescales the envelope, and only the envelope
    over = spec.Configuration(override_shank=True, shank_radius_mm=2.0)
    c.close("override scales the pitch", over.pitch, m3["P"] * 2.0 / 1.5, units="mm")
    c.close("override scales the head radius", over.head_radius,
            m3["dk_max_plain"] / 2 * 2.0 / 1.5, units="mm")
    c.close("override leaves the recess alone", over.recess_radius, cfg.recess_radius,
            units="mm")
    both = spec.Configuration(override_shank=True, shank_radius_mm=2.0,
                              override_torx=True, torx_radius_mm=1.55)
    c.close("the two overrides are independent", both.recess_radius, 1.55, units="mm")
    c.close("the recess ratio survives an override",
            both.recess_inner / both.recess_radius, t10["B"] / t10["A"])

    # the long-shank regime switches thread start from 2P to l minus b
    # M8 carries a 35 mm full-thread preferred-length limit, so the regime
    # changes between 30 mm and 45 mm, not at some round number.
    short = spec.Configuration(size_id=6, length_mm=30.0)
    long_ = spec.Configuration(size_id=6, length_mm=45.0)
    c.true("a short M8 uses the 2P neck", not short.long_cylinder)
    c.true("a long M8 uses l minus b", long_.long_cylinder)
    c.close("the long neck is l minus b", long_.neck,
            long_.tip - long_.thread_length, units="mm")

    # the countersunk datum moves to the top face and its length includes the head
    csk = spec.Configuration(series=2, size_id=2, length_mm=10.0)
    c.close("countersunk length includes the head", csk.tip,
            10.0 - csk.head_height, units="mm")
    c.close("countersunk shifts to a flush datum", csk.datum_shift, csk.head_height,
            units="mm")
    raised = spec.Configuration(series=0, size_id=2, length_mm=10.0)
    c.close("a raised head keeps the underhead datum", raised.datum_shift, 0.0, units="mm")


def check_rejections(c):
    """Every input the graph must refuse is refused here, for the named reason."""
    for row in spec.rejections():
        c.true("%s is rejected" % row["name"], not row["valid"],
               "failing checks: %s" % ", ".join(row["failing_checks"]))
        c.true("%s fails on %s" % (row["name"], row["expected_failing_check"]),
               row["expected_failing_check"] in row["failing_checks"],
               "actually failed: %s" % ", ".join(row["failing_checks"]))
    for entry in spec.configurations():
        c.true("%s is accepted" % entry["name"], entry["resolved"]["valid"],
               "failing checks: %s"
               % ", ".join(k for k, v in entry["resolved"]["checks"].items() if not v))


def check_samples(c):
    """Every predicted sample is well formed, and the sign probes straddle a surface."""
    pred = spec.predictions()
    ids = [r["id"] for r in pred["samples"]]
    c.true("every sample id is unique", len(ids) == len(set(ids)),
           "%d ids, %d unique" % (len(ids), len(set(ids))))
    c.true("a boundary sample carries the gate",
           all(r["tolerance_m"] == spec.GATE_M
               for r in pred["samples"] if r["kind"] == "boundary"))
    c.true("a sign sample carries no tolerance",
           all(r["tolerance_m"] is None
               for r in pred["samples"] if r["kind"] != "boundary"))
    by_id = {r["id"]: r for r in pred["samples"]}
    pairs = 0
    for r in pred["samples"]:
        if r["kind"] != "boundary":
            continue
        inside, outside = by_id.get(r["id"] + "-in"), by_id.get(r["id"] + "-out")
        c.true("%s has both sign probes" % r["id"], inside is not None and outside is not None)
        if inside and outside:
            pairs += 1
            d = math.dist(inside["point_m"], outside["point_m"])
            # the sample table rounds each coordinate at 1e-12 mm so it stays a
            # stable, diffable artefact, which moves a separation by up to a few
            # times 1e-15 m. Nothing here is claimed below that.
            c.close("%s probes straddle the surface" % r["id"], d,
                    2 * spec.SIGN_OFFSET_M, tol=1e-14, units="m")
            c.true("%s probes have opposite expectations" % r["id"],
                   inside["expect"] < 0 < outside["expect"])
    c.true("every boundary sample was paired", pairs == pred["counts"]["boundary"])

    # The placed configurations are the SAME screw, moved: their local points
    # must match the default set exactly, and their world points must not.
    default_local = {r["id"].replace("default-", ""): tuple(r["local_mm"])
                     for r in pred["samples"] if r["configuration"] == "default"}
    for name in ("oblique", "rotated", "farfield"):
        rows = [r for r in pred["samples"] if r["configuration"] == name]
        c.true("%s is the same screw as the default" % name,
               all(default_local.get(r["id"].replace(name + "-", "")) == tuple(r["local_mm"])
                   for r in rows),
               "%d samples" % len(rows))
        moved = sum(1 for r in rows if math.dist(r["local_mm"], r["point_mm"]) > 1e-9)
        c.true("%s is actually displaced" % name, moved == len(rows),
               "%d of %d samples moved" % (moved, len(rows)))
    # the three share one rotation, so their world points differ by a pure shift
    trio = {n: {r["id"].replace(n + "-", ""): r["point_mm"]
                for r in pred["samples"] if r["configuration"] == n}
            for n in ("oblique", "rotated", "farfield")}
    keys = sorted(trio["rotated"])
    shifts = [tuple(round(trio["oblique"][k][i] - trio["rotated"][k][i], 9) for i in range(3))
              for k in keys]
    c.true("oblique and rotated differ by one constant shift",
           len(set(shifts)) == 1, "%d distinct shifts" % len(set(shifts)))
    c.true("the shift is the oblique insertion point",
           shifts[0] == tuple(round(v, 9) for v in spec.OBLIQUE_PLACEMENT[0]),
           "got %s" % (shifts[0],))
    far = [tuple(round(trio["farfield"][k][i] - trio["rotated"][k][i], 9) for i in range(3))
           for k in keys]
    c.true("farfield sits a hundred times further out",
           len(set(far)) == 1
           and far[0] == tuple(round(v * 100, 9) for v in spec.OBLIQUE_PLACEMENT[0]),
           "got %s" % (far[0],))


def main():
    c = Checks()
    check_contour(c)
    check_thread(c)
    check_placement(c)
    check_source_fidelity(c)
    check_rejections(c)
    check_samples(c)
    report = c.report()
    summary = {"checks": report["checks"], "failed": report["failed"],
               "worst_delta": report["worst_delta"],
               "worst_delta_units": "mm or dimensionless, per row",
               "predictions": spec.predictions()["counts"],
               "scope": "the mirror checked against itself; no nTop, no recipe"}
    if report["failed"]:
        summary["failures"] = report["failures"]
    out = Path(__file__).resolve().parents[1] / "output" / "check_spec.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(summary, rows=report["rows"]), indent=2), encoding="utf8")
    print(json.dumps(summary, indent=2))
    return 1 if report["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
