"""The yardstick: a closed-form mirror of the Torx, with no nTop import.

Written before any native execution and frozen. `check_spec.py` checks it
against itself first. Never change a predicted value to match a measurement; if
the two disagree, one of them is wrong and it must be said which.

What this mirror predicts, and what it deliberately does not
-----------------------------------------------------------
It predicts the SURFACE: the exact (r, z, theta) of points that lie on the
boundary of the assembled screw, where any correct field reads zero, and the
SIGN of the field a short distance either side of each of them along the outward
normal direction.

It does not predict interior distance values. The composed field is not a
Euclidean signed distance and never claimed to be: `revolve` carries the section
distance in the (r, z) half plane, the thread kernel carries a radial residual
with axial caps, and the [5.44.0] sharp booleans are exactly min, max and
max(f, -g) (measured; rule G3/G4). A number quoted against a Euclidean distance
here would measure the wrong thing.

So the deciding quantity is the boundary residual, and the deciding floor is the
source, not the instrument: the supplied informative Annex A ratios are
approximate and carry no certified error bound, and the ISO tables give exact
declared nominal dimensions, not metrology of one sample. The 0.1 micrometre
gate used below verifies the declared CAD construction only. It is not a
tolerance certification and not a claim of manufacturing conformity.

The offset used for the sign probes is 2 micrometres, which is 20x the boundary
gate and far below any source dimension, so a sign test cannot be satisfied by
numerical noise at the gate.
"""

import json
import math

import torx_catalogue as cat

GATE_M = 1e-7          # boundary residual accepted, metres (0.1 micrometre)
SIGN_OFFSET_M = 2e-6   # distance either side of a surface for a sign probe
MM = 1e-3

COS30 = math.sqrt(3) / 2
SQRT1_2 = math.sqrt(0.5)
ISO68_MINOR_FACTOR = 5 * math.sqrt(3) / 16   # basic profile: minor = major - P*5*sqrt3/16


# --------------------------------------------------------------------------
# the recess contour, from the supplied ISO 10664:1999 Table 1 nominals
# --------------------------------------------------------------------------
def concave_radius(A, B, re):
    """The concave arc radius that makes the two arcs externally tangent.

    A and B are the declared nominal major and minor diameters; `re` is the
    chosen convex lobe radius. Solving for tangency is what keeps A, B and the
    chosen radius all exact at once.
    """
    c = A / 2 - re
    b = B / 2
    return (b * b + c * c - 2 * b * c * COS30 - re * re) / (2 * (re + c * COS30 - b))


def contour_radius(theta, A, B, re):
    """Boundary radius of the recess at one angle, sixfold symmetric.

    Exact circle intersections, not a sampled approximation and not a six-lobed
    sine wave. The convex centre sits at c = A/2 - re on the lobe axis; the
    adjacent concave centre sits at angle pi/6 and distance d = B/2 + ri.
    """
    ri = concave_radius(A, B, re)
    c = A / 2 - re
    d = B / 2 + ri
    px = c + re / (re + ri) * (d * COS30 - c)
    py = re / (re + ri) * d / 2
    transition = math.atan2(py, px)
    a = abs((theta + math.pi / 6) % (math.pi / 3) - math.pi / 6)
    if a <= transition:
        return c * math.cos(a) + math.sqrt(max(0.0, re * re - (c * math.sin(a)) ** 2))
    a = math.pi / 6 - a
    return d * math.cos(a) - math.sqrt(max(0.0, ri * ri - (d * math.sin(a)) ** 2))


def contour_transition_angle(A, B, re):
    """The angle at which the convex arc hands over to the concave arc."""
    ri = concave_radius(A, B, re)
    c = A / 2 - re
    d = B / 2 + ri
    return math.atan2(re / (re + ri) * d / 2, c + re / (re + ri) * (d * COS30 - c))


def contour_branches(theta, A, B, re):
    """Both arc branches evaluated at one angle, without choosing between them.

    At the transition angle the two must return the same radius. Evaluating them
    separately is the continuity test; sampling either side of the transition is
    not, because the contour has a non-zero slope there and the difference would
    only measure the step size.
    """
    ri = concave_radius(A, B, re)
    c = A / 2 - re
    d = B / 2 + ri
    a = abs((theta + math.pi / 6) % (math.pi / 3) - math.pi / 6)
    convex = c * math.cos(a) + math.sqrt(max(0.0, re * re - (c * math.sin(a)) ** 2))
    a2 = math.pi / 6 - a
    concave = d * math.cos(a2) - math.sqrt(max(0.0, ri * ri - (d * math.sin(a2)) ** 2))
    return convex, concave


# --------------------------------------------------------------------------
# the thread kernel
# --------------------------------------------------------------------------
def thread_radius(z, theta, major, minor, pitch, crest_width, slope):
    """The exact zero-set radius of the helical thread at (z, theta).

    Right-handed: the crest centre follows z = pitch * theta / (2 pi) + k * pitch.
    """
    t = z / pitch - theta / (2 * math.pi)
    phase = abs(t - round(t)) * pitch
    return max(minor, major - max(phase - crest_width / 2, 0.0) * slope)


# --------------------------------------------------------------------------
# resolving one configuration, mirroring the graph's own selection chain
# --------------------------------------------------------------------------
class Configuration:
    """One resolved screw: every derived quantity the graph computes.

    Mirrors `torx_local` exactly, in millimetres, so a disagreement is a
    disagreement about the construction and not about a unit.
    """

    def __init__(self, family=0, series=0, size_id=2, drive_size=0, length_mm=10.0,
                 override_shank=False, shank_radius_mm=1.5,
                 override_torx=False, torx_radius_mm=1.4, label=None):
        rows = {r[0]: r for r in cat.SOURCE_ROWS}
        key = series * 100 + size_id
        # An unsupported series/size pair is not an exception here. The graph's
        # selector returns -1 mm for a key no row owns, which drives the nominal
        # radius negative and makes the gate refuse the configuration. The mirror
        # reproduces that sentinel rather than raising, so the case can be
        # predicted, dispatched and measured like any other.
        self.row_exists = key in rows
        row = rows.get(key, [key] + [-1.0] * 13)
        self.family, self.series, self.size_id = family, series, size_id
        self.row = row
        self.label = label or "family%d series%d size%d" % (family, series, size_id)

        self.nominal_radius = row[1] / 2
        self.shank_radius = shank_radius_mm if override_shank else self.nominal_radius
        self.scale = self.shank_radius / self.nominal_radius
        val = lambda col: row[col] * self.scale
        self.pitch = val(2)
        self.head_radius = val(3) / 2
        self.head_height = val(4)
        self.top_round = val(5)
        self.fillet = val(6)
        self.short_neck = val(7)
        self.depth = val(8)
        self.thread_length = val(10)
        self.short_length_max = val(11)
        self.web = val(12)
        self.crown = val(13)
        self.length = length_mm
        self.tip = length_mm - self.head_height if series == 2 else length_mm
        long_cylinder = (series == 0) and (self.short_length_max < self.tip)
        self.neck = (self.tip - self.thread_length) if long_cylinder else self.short_neck
        self.long_cylinder = long_cylinder

        self.drive_size = row[9] if drive_size == 0 else drive_size
        drive = {r[0]: r for r in cat.DRIVE_ROWS}.get(self.drive_size,
                                                      [self.drive_size, -1.0, -1.0])
        self.drive_A, self.drive_B = drive[1], drive[2]
        self.recess_radius = torx_radius_mm if override_torx else self.drive_A / 2
        self.recess_inner = self.recess_radius * self.drive_B / self.drive_A
        self.lobe_radius = self.recess_radius * 0.2
        posts = {r[0]: r[1] for r in cat.POST_ROWS}
        self.post_nominal = posts.get(self.drive_size, -1.0)
        self.post_radius = (self.recess_radius * self.post_nominal / self.drive_A
                            if family == 1 else self.recess_inner * 0.1)
        self.minor_radius = self.shank_radius - self.pitch * ISO68_MINOR_FACTOR
        self.crest_width = self.pitch / 8
        self.datum_shift = self.head_height if series == 2 else 0.0

        # The graph's validity gate, mirrored condition by condition.
        checks = {
            "family_has_post": family == 0 or self.post_nominal > 0,
            "floor_wall": (self.recess_radius < self.shank_radius
                           + self.head_height - self.depth) if series == 2 else True,
            "nominal_radius_positive": self.nominal_radius > 0,
            "shank_radius_positive": self.shank_radius > 0,
            "recess_radius_positive": self.recess_radius > 0,
            "recess_inside_head": self.recess_radius < self.head_radius - self.top_round,
            "neck_before_tip": self.neck < self.tip,
            "neck_positive": self.neck > 0,
            "post_inside_recess": self.post_radius < self.recess_inner,
            "web_under_recess": self.web < self.head_height - self.depth,
        }
        self.checks = checks
        self.valid = all(checks.values())

    # -- geometry of the assembled screw, in the local frame ---------------
    # z = 0 is the underhead seating plane; the head lies at z < 0; the tip at
    # z = tip. For countersunk the whole screw is then shifted by +head_height so
    # the top face sits on the insertion datum.
    def recess_span(self):
        """(mouth z, floor z) of the recess in local coordinates before the shift."""
        return (-self.head_height, -self.head_height + self.depth)

    def contour(self, theta):
        return contour_radius(theta, self.recess_radius * 2,
                              self.recess_inner * 2, self.lobe_radius)

    def thread(self, z_local, theta):
        """Thread surface radius at a local z (the assembly frame, not the kernel's)."""
        return thread_radius(z_local - self.neck, theta, self.shank_radius,
                             self.minor_radius, self.pitch, self.crest_width,
                             math.sqrt(3))

    def summary(self):
        return {
            "label": self.label, "valid": self.valid,
            "family": cat.FAMILIES[self.family]["label"],
            "series": cat.SERIES[self.series]["label"],
            "metric": cat.SCREWS[self.size_id]["label"],
            "drive": "T%d" % self.drive_size,
            "d_mm": self.row[1], "pitch_mm": self.pitch,
            "shank_radius_mm": self.shank_radius, "head_radius_mm": self.head_radius,
            "head_height_mm": self.head_height, "top_round_mm": self.top_round,
            "fillet_mm": self.fillet, "neck_mm": self.neck, "tip_mm": self.tip,
            "recess_depth_mm": self.depth,
            "recess_A_mm": self.drive_A, "recess_B_mm": self.drive_B,
            "recess_radius_mm": self.recess_radius,
            "recess_inner_mm": self.recess_inner, "lobe_radius_mm": self.lobe_radius,
            "concave_radius_mm": concave_radius(self.recess_radius * 2,
                                                self.recess_inner * 2, self.lobe_radius),
            "minor_radius_mm": self.minor_radius, "crest_width_mm": self.crest_width,
            "post_radius_mm": self.post_radius, "datum_shift_mm": self.datum_shift,
            "long_cylinder": self.long_cylinder,
            "checks": self.checks,
        }


# --------------------------------------------------------------------------
# placement
# --------------------------------------------------------------------------
def frame(axis, tangent, clocking=0.0):
    """The right-handed frame the placement block builds. Returns (x, y, z) axes.

    No fallback is defined for a zero axis or a tangent parallel to it: both
    raise here, exactly as the graph refuses them.
    """
    z = _unit(axis)
    y_raw = _cross(z, tangent)
    if _norm(y_raw) < 1e-12:
        raise ValueError("Tangent Reference is parallel to Axis")
    y0 = _unit(y_raw)
    x0 = _cross(y0, z)
    c, s = math.cos(clocking), math.sin(clocking)
    x = tuple(x0[i] * c + y0[i] * s for i in range(3))
    y = _cross(z, x)
    return x, y, z


def place(point_local, origin, axis, tangent, clocking=0.0):
    """World point of a local point, under the same frame the graph builds."""
    x, y, z = frame(axis, tangent, clocking)
    return tuple(origin[i] + point_local[0] * x[i] + point_local[1] * y[i]
                 + point_local[2] * z[i] for i in range(3))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _norm(a):
    return math.sqrt(sum(v * v for v in a))


def _unit(a):
    n = _norm(a)
    if n < 1e-12:
        raise ValueError("zero vector")
    return tuple(v / n for v in a)


# --------------------------------------------------------------------------
# the sample set
# --------------------------------------------------------------------------
class Samples:
    """Collects boundary points and their two sign probes."""

    def __init__(self):
        self.rows = []

    def boundary(self, sample_id, where, point_mm, outward_mm, config,
                 placement=None, note=""):
        """One surface point, plus a probe 2 micrometres either side of it.

        `outward_mm` is a unit direction pointing out of the solid at that point.
        """
        n = _norm(outward_mm)
        if abs(n - 1.0) > 1e-9:
            raise ValueError("%s: outward direction is not a unit vector (%.6f)"
                             % (sample_id, n))
        step = SIGN_OFFSET_M / MM
        trio = [("%s" % sample_id, point_mm, 0.0, "boundary"),
                ("%s-in" % sample_id,
                 tuple(point_mm[i] - outward_mm[i] * step for i in range(3)), -1, "inside"),
                ("%s-out" % sample_id,
                 tuple(point_mm[i] + outward_mm[i] * step for i in range(3)), +1, "outside")]
        for sid, p, expect, kind in trio:
            self.rows.append(self._row(sid, where, p, expect, kind, config,
                                       placement, note))

    def sign(self, sample_id, where, point_mm, expect, config, placement=None, note=""):
        """One point whose sign alone is predicted: -1 solid, +1 air."""
        self.rows.append(self._row(sample_id, where, point_mm, expect,
                                   "solid" if expect < 0 else "air", config,
                                   placement, note))

    @staticmethod
    def _row(sample_id, where, point_mm, expect, kind, config, placement, note):
        local = tuple(float(v) for v in point_mm)
        world = place(local, *placement) if placement else local
        return {"id": sample_id, "configuration": config, "where": where,
                "kind": kind, "expect": expect,
                "local_mm": [round(v, 12) for v in local],
                "point_mm": [round(v, 12) for v in world],
                "point_m": [round(v * MM, 15) for v in world],
                "tolerance_m": GATE_M if kind == "boundary" else None,
                "note": note}


IDENTITY_PLACEMENT = ((0.0, 0.0, 0.0), (0, 0, 1), (1, 0, 0), 0.0)
# An oblique placement chosen so no component of the frame is zero and the
# clocking is not a multiple of the sixfold recess symmetry.
OBLIQUE_AXIS = (0.3, -0.5, 0.8)
OBLIQUE_TANGENT = (1.0, 0.25, 0.0)
OBLIQUE_CLOCKING = 37.0 * math.pi / 180.0
OBLIQUE_PLACEMENT = ((12.0, -7.5, 4.25), OBLIQUE_AXIS, OBLIQUE_TANGENT, OBLIQUE_CLOCKING)
# The same oblique frame with the insertion point at the origin, and at a hundred
# times the distance. Three placements sharing one rotation separate a rotation
# cost from a translation cost, which one oblique case alone cannot do.
ROTATED_PLACEMENT = ((0.0, 0.0, 0.0), OBLIQUE_AXIS, OBLIQUE_TANGENT, OBLIQUE_CLOCKING)
FARFIELD_PLACEMENT = ((1200.0, -750.0, 425.0), OBLIQUE_AXIS, OBLIQUE_TANGENT,
                      OBLIQUE_CLOCKING)


def _head_samples(s, cfg, config_name, placement, shift):
    """Boundary points on the cylindrical head, from the revolved section."""
    if cfg.series != 0:
        return
    R, h, sr = cfg.head_radius, cfg.head_height, cfg.shank_radius
    r_round, f = cfg.top_round, cfg.fillet
    k = SQRT1_2
    z = lambda v: v + shift
    # cylindrical side, safely between the top round and the seating plane
    s.boundary("%s-head-side" % config_name, "head cylindrical side",
               (R, 0.0, z(-h / 2)), (1, 0, 0), config_name, placement)
    # flat head top, outside the recess mouth and inside the top round
    r_top = (cfg.recess_radius + (R - r_round)) / 2
    s.boundary("%s-head-top" % config_name, "flat head top face",
               (r_top, 0.0, z(-h)), (0, 0, -1), config_name, placement,
               "between the recess mouth and the start of the top round")
    # the top round, at its 45 degree point: the arc centre is (R-r, -h+r)
    s.boundary("%s-head-round" % config_name, "top edge round, 45 degrees",
               (R - r_round * (1 - k), 0.0, z(-h + r_round * (1 - k))),
               (k, 0.0, -k), config_name, placement)
    # underhead seating plane
    r_seat = (sr + f + R) / 2
    s.boundary("%s-head-seat" % config_name, "underhead seating plane",
               (r_seat, 0.0, z(0.0)), (0, 0, 1), config_name, placement)
    # underhead fillet, at its 45 degree point: arc centre (sr+f, f). The fillet
    # is concave, so the material lies OUTSIDE its arc circle and the outward
    # normal points at the centre: away from the axis and away from the head.
    s.boundary("%s-head-fillet" % config_name, "underhead fillet, 45 degrees",
               (sr + f * (1 - k), 0.0, z(f * (1 - k))), (k, 0.0, k),
               config_name, placement)


def _shank_samples(s, cfg, config_name, placement, shift):
    z = lambda v: v + shift
    z_plain = (cfg.fillet + cfg.neck) / 2 if cfg.series == 0 else cfg.neck / 2
    if z_plain > cfg.fillet and z_plain < cfg.neck:
        s.boundary("%s-shank" % config_name, "plain shank between fillet and thread",
                   (cfg.shank_radius, 0.0, z(z_plain)), (1, 0, 0), config_name, placement)


def _recess_samples(s, cfg, config_name, placement, shift):
    """Boundary points on the recess wall, and the two signed points inside it."""
    mouth, floor = cfg.recess_span()
    z_wall = (mouth + floor) / 2 + shift
    A, Bm = cfg.recess_radius * 2, cfg.recess_inner * 2
    transition = contour_transition_angle(A, Bm, cfg.lobe_radius)
    angles = [("lobe", 0.0), ("junction", transition),
              ("mid", (transition + math.pi / 6) / 2), ("valley", math.pi / 6),
              ("sector2", math.pi / 3), ("sector2-valley", math.pi / 2)]
    for name, theta in angles:
        r = cfg.contour(theta)
        p = (r * math.cos(theta), r * math.sin(theta), z_wall)
        # the outward normal of the SOLID at the recess wall points into the recess
        outward = _recess_outward(cfg, theta, r)
        s.boundary("%s-recess-%s" % (config_name, name),
                   "recess wall at %.3f deg" % (theta * 180 / math.pi),
                   p, outward, config_name, placement,
                   "radius %.6f mm from the exact tangent-arc contour" % r)
    # A tamper-resistant recess keeps a round post on the axis, so neither the
    # floor sample nor the void sample may sit on the axis: both move into the
    # annulus between the post and the nearest point of the contour.
    post = cfg.post_radius if cfg.family == 1 else 0.0
    r_open = (post + cfg.recess_inner) / 2
    s.boundary("%s-recess-floor" % config_name, "recess floor",
               (r_open, 0.0, floor + shift), (0, 0, -1), config_name, placement)
    s.sign("%s-recess-void" % config_name, "inside the recess opening",
           (r_open, 0.0, (mouth + floor) / 2 + shift), +1, config_name, placement,
           "air: the recess is a subtraction")
    s.sign("%s-under-recess" % config_name, "head metal below the recess floor",
           (0.0, 0.0, (floor + 0.0) / 2 + shift), -1, config_name, placement,
           "the web between the recess floor and the seating plane")
    if cfg.family == 1:
        s.boundary("%s-post-side" % config_name, "tamper-resistant post, cylindrical side",
                   (post, 0.0, (mouth + floor) / 2 + shift), (1, 0, 0),
                   config_name, placement,
                   "Camcar reference post diameter %.4f mm, scaled with the recess"
                   % cfg.post_nominal)
        s.boundary("%s-post-top" % config_name, "tamper-resistant post, top face",
                   (post / 2, 0.0, mouth + shift), (0, 0, -1), config_name, placement,
                   "the CAD choice is a post flush with the head top")
        s.sign("%s-post-core" % config_name, "inside the post",
               (0.0, 0.0, (mouth + floor) / 2 + shift), -1, config_name, placement,
               "the same point that is air for the internal family")


def _recess_outward(cfg, theta, r, eps=1e-7):
    """Unit outward normal of the SOLID at a recess wall point.

    The recess is subtracted, so leaving the solid means going into the recess,
    towards the axis in the radial sense of the contour. Taken from the contour's
    own slope so it is exact on the concave arcs too.
    """
    dr = (cfg.contour(theta + eps) - cfg.contour(theta - eps)) / (2 * eps)
    # tangent of the planar curve r(theta) in Cartesian terms
    tx = dr * math.cos(theta) - r * math.sin(theta)
    ty = dr * math.sin(theta) + r * math.cos(theta)
    n = math.hypot(tx, ty)
    # rotate the tangent by -90 degrees to point towards the axis
    return (ty / n * -1.0, -tx / n * -1.0, 0.0)


def _thread_samples(s, cfg, config_name, placement, shift):
    """Crest, root and a flank point, each on the exact helical zero set."""
    if cfg.tip - cfg.neck <= 2 * cfg.pitch:
        return
    z = lambda v: v + shift
    # choose a turn safely inside the threaded length
    turns = int((cfg.tip - cfg.neck) / cfg.pitch)
    k = max(1, turns // 2)
    base = cfg.neck + k * cfg.pitch

    s.boundary("%s-thread-crest" % config_name, "thread crest, theta = 0",
               (cfg.shank_radius, 0.0, z(base)), (1, 0, 0), config_name, placement)
    root_z = base + cfg.pitch / 2
    s.boundary("%s-thread-root" % config_name, "thread root, theta = 0",
               (cfg.minor_radius, 0.0, z(root_z)), (1, 0, 0), config_name, placement,
               "ISO 68-1 basic minor radius, major - P * 5 sqrt(3) / 16")
    # a flank point: phase chosen strictly between the crest flat and the root flat
    flank_phase = (cfg.crest_width / 2
                   + (cfg.shank_radius - cfg.minor_radius) / math.sqrt(3)) / 2
    flank_z = base + flank_phase
    r_flank = cfg.thread(flank_z, 0.0)
    s.boundary("%s-thread-flank" % config_name, "thread flank, theta = 0",
               (r_flank, 0.0, z(flank_z)), (1, 0, 0), config_name, placement,
               "radius %.6f mm at axial phase %.6f mm" % (r_flank, flank_phase))
    # the helix itself: a crest at theta = 90 degrees sits a quarter pitch higher
    theta = math.pi / 2
    helix_z = cfg.neck + (k + theta / (2 * math.pi)) * cfg.pitch
    s.boundary("%s-thread-helix" % config_name, "thread crest, theta = 90 degrees",
               (0.0, cfg.shank_radius, z(helix_z)), (0, 1, 0), config_name, placement,
               "the crest follows z = P theta / 2 pi + k P")
    s.sign("%s-thread-gap" % config_name, "air in the thread groove",
           (cfg.shank_radius - 1e-4, 0.0, z(root_z)), +1, config_name, placement,
           "outside the thread surface but inside the major radius envelope")


def _tip_samples(s, cfg, config_name, placement, shift):
    z = lambda v: v + shift
    s.boundary("%s-tip" % config_name, "flat tip face",
               (cfg.minor_radius / 2, 0.0, z(cfg.tip)), (0, 0, 1), config_name, placement,
               "the kernel declares no runout and no lead-in; the tip is flat")


def _far_samples(s, cfg, config_name, placement, shift):
    z = lambda v: v + shift
    s.sign("%s-air" % config_name, "clear air beside the head",
           (cfg.head_radius * 3, 0.0, z(-cfg.head_height / 2)), +1, config_name, placement)
    s.sign("%s-core" % config_name, "solid shank core",
           (0.0, 0.0, z(cfg.neck / 2)), -1, config_name, placement)


CONFIGURATIONS = [
    ("default", dict(family=0, series=0, size_id=2, drive_size=0, length_mm=10.0),
     IDENTITY_PLACEMENT,
     "the block's own defaults: internal Torx, cylindrical ISO 14579:2011 M3, "
     "automatic drive, 10 mm underhead length, placed at the origin"),
    ("oblique", dict(family=0, series=0, size_id=2, drive_size=0, length_mm=10.0),
     OBLIQUE_PLACEMENT,
     "the same screw under an oblique frame and a 37 degree clocking, to separate "
     "the placement layer from the geometry"),
    ("rotated", dict(family=0, series=0, size_id=2, drive_size=0, length_mm=10.0),
     ROTATED_PLACEMENT,
     "the oblique rotation alone, with the insertion point back at the origin"),
    ("farfield", dict(family=0, series=0, size_id=2, drive_size=0, length_mm=10.0),
     FARFIELD_PLACEMENT,
     "the same rotation a hundred times further out, so a residual that scales with "
     "the insertion distance can be told from one that does not"),
    ("m8", dict(family=0, series=0, size_id=6, drive_size=0, length_mm=45.0),
     IDENTITY_PLACEMENT,
     "cylindrical M8 at 45 mm: past the 35 mm full-thread limit of its source row, so "
     "the thread starts at l minus b instead of at 2P"),
    ("t25", dict(family=0, series=0, size_id=4, drive_size=25, length_mm=16.0),
     IDENTITY_PLACEMENT,
     "cylindrical M5 with the drive size chosen by hand rather than automatically"),
    ("tamper", dict(family=1, series=0, size_id=4, drive_size=25, length_mm=16.0),
     IDENTITY_PLACEMENT,
     "the tamper-resistant derivative: the same recess with a sourced Camcar round post"),
    ("custom", dict(family=0, series=0, size_id=2, drive_size=0, length_mm=12.0,
                    override_shank=True, shank_radius_mm=2.0,
                    override_torx=True, torx_radius_mm=1.55),
     IDENTITY_PLACEMENT,
     "independent shank and recess overrides: a custom size that no longer carries a "
     "standard metric thread designation"),
]

# Inputs the graph must refuse. Each names the gate condition it breaks.
REJECTIONS = [
    ("tamper-t6", dict(family=1, series=0, size_id=2, drive_size=6, length_mm=10.0),
     "family_has_post", "T6 has no sourced tamper-resistant post"),
    ("recess-too-large", dict(family=0, series=0, size_id=2, drive_size=0,
                              length_mm=10.0, override_torx=True, torx_radius_mm=2.6),
     "recess_inside_head", "the recess would break through the head side"),
    ("too-short", dict(family=0, series=0, size_id=2, drive_size=0, length_mm=0.5),
     "neck_before_tip", "no threaded length is left below the neck"),
    ("csk-too-short", dict(family=0, series=2, size_id=2, drive_size=0, length_mm=1.0),
     "neck_before_tip", "the countersunk head alone exceeds the total length"),
    ("pan-m12", dict(family=0, series=1, size_id=8, drive_size=0, length_mm=20.0),
     "nominal_radius_positive",
     "M12 has no pan row: the source table stops at M10, so the selector returns "
     "its sentinel instead of a dimension"),
    ("csk-thin-floor", dict(family=0, series=2, size_id=2, drive_size=0,
                            length_mm=12.0, override_torx=True, torx_radius_mm=2.4),
     "floor_wall",
     "a countersunk recess deep enough to break out through the cone"),
]


def configurations():
    """Every valid configuration the verification band builds, resolved."""
    out = []
    for name, kwargs, placement, why in CONFIGURATIONS:
        cfg = Configuration(label=name, **kwargs)
        out.append({"name": name, "why": why, "kwargs": kwargs,
                    "placement": {"origin_mm": list(placement[0]),
                                  "axis": list(placement[1]),
                                  "tangent": list(placement[2]),
                                  "clocking_rad": placement[3]},
                    "resolved": cfg.summary(), "config": cfg})
    return out


def rejections():
    out = []
    for name, kwargs, gate, why in REJECTIONS:
        cfg = Configuration(label=name, **kwargs)
        out.append({"name": name, "why": why, "expected_failing_check": gate,
                    "kwargs": kwargs, "valid": cfg.valid,
                    "failing_checks": [k for k, v in cfg.checks.items() if not v]})
    return out


def predictions():
    """The frozen prediction table. Written before any native execution."""
    s = Samples()
    resolved = configurations()
    for entry in resolved:
        cfg, name = entry["config"], entry["name"]
        placement = None if entry["placement"]["origin_mm"] == [0.0, 0.0, 0.0] and \
            entry["placement"]["clocking_rad"] == 0.0 and \
            entry["placement"]["axis"] == [0, 0, 1] else \
            (tuple(entry["placement"]["origin_mm"]), tuple(entry["placement"]["axis"]),
             tuple(entry["placement"]["tangent"]), entry["placement"]["clocking_rad"])
        shift = cfg.datum_shift
        _head_samples(s, cfg, name, placement, shift)
        _shank_samples(s, cfg, name, placement, shift)
        _recess_samples(s, cfg, name, placement, shift)
        _thread_samples(s, cfg, name, placement, shift)
        _tip_samples(s, cfg, name, placement, shift)
        _far_samples(s, cfg, name, placement, shift)

    boundary = [r for r in s.rows if r["kind"] == "boundary"]
    return {
        "gate_m": GATE_M,
        "sign_offset_m": SIGN_OFFSET_M,
        "frozen": "predictions computed with no nTop import; see the module docstring "
                  "for what is and is not claimed",
        "configurations": [{k: v for k, v in e.items() if k != "config"}
                           for e in resolved],
        "rejections": rejections(),
        "samples": s.rows,
        "counts": {"total": len(s.rows), "boundary": len(boundary),
                   "sign": len(s.rows) - len(boundary),
                   "configurations": len(resolved)},
    }


if __name__ == "__main__":
    p = predictions()
    print(json.dumps({"counts": p["counts"], "gate_m": p["gate_m"],
                      "configurations": [{"name": c["name"],
                                          "drive": c["resolved"]["drive"],
                                          "valid": c["resolved"]["valid"]}
                                         for c in p["configurations"]],
                      "rejections": [{"name": r["name"], "valid": r["valid"],
                                      "failing": r["failing_checks"]}
                                     for r in p["rejections"]]}, indent=2))
