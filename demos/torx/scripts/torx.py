"""The Torx graph: eight blocks, one complete recipe.

`graph()` is the single description of the geometry. It is a port of the source
project's eight JavaScript builders onto `torx_backend`, keeping the same
construction, the same declared CAD choices and the same source facts, so the
port can be compared entry by entry against nTop's own recorded recipe for the
same graph (`check_recipe.py`).

Block chain, dependencies first:

    Countersunk Head 2013   revolved 90-degree cone, flat rim
    Torx Internal           six alternating tangent arcs, extruded
    Screw Head              revolved cylindrical head, two circular rounds
    Pan Head                revolved spherical crown, cylindrical side
    Metric Thread Kernel    analytic helical field, flat crest and root
    Torx Local Development  source-row selection, validity gate, assembly
    Place Screw             rigid placement into a surface frame
    Torx                    the public block: four native Choice Lists

Every dimensional value comes from `torx_catalogue`, which reads the three ISO
row tables in `inputs/source_tables/`. No dimension is written twice.
"""

import json
import math
from pathlib import Path

import torx_catalogue as cat
from torx_backend import (A, B, CHOICE, E, I, L, P3, R, T, V, X, Recipe,
                          SQRT1_2, TWO_PI, flatten, signature)

DEMO = Path(__file__).resolve().parents[1]
IDENTITIES = json.loads((DEMO / "inputs" / "recorded" / "identities.json")
                        .read_text(encoding="utf8"))["identifiers"]

COS30 = math.sqrt(3) / 2


def _define(recipe_context, displayname, description, output_id, deps=()):
    """Close a block into an importable definition under its recorded uuid."""
    definition = recipe_context.envelope(
        IDENTITIES[displayname], displayname, description, output_id,
        imports=None, cb_refs=None)
    if deps:
        definition["_deps"] = list(deps)
        definition["cbRefs"] = []          # rewritten to root indices by flatten()
    definition["_sections"] = recipe_context.sections_json()
    return definition


# --------------------------------------------------------------------------
# 1. Torx Internal: the recess kernel
# --------------------------------------------------------------------------
def torx_internal():
    """Alternating tangent circular arcs preserving A, B and a chosen lobe radius.

    Geometric kernel only. Source selection and screw assembly belong to the
    public block. The contour is not approximated by a six-lobed sine wave: the
    convex arc radius is chosen (informative Annex A, 0.1 A) and the concave
    radius is solved so the two arcs are externally tangent.
    """
    b = Recipe([
        ("Outer radius", "real", {"length": 1}, L(0.001975),
         "Half the recess major diameter A."),
        ("Inner radius", "real", {"length": 1}, L(0.001425),
         "Half the recess minor diameter B."),
        ("Lobe radius", "real", {"length": 1}, L(0.000395),
         "Chosen convex arc radius. Default derives from informative ISO 10664:1999 "
         "Annex A, not a normative nominal radius."),
        ("Depth", "real", {"length": 1}, L(0.0018),
         "Positive extrusion depth along local +Z."),
    ])
    b.sec("Tangent contour",
          "Exact tangent circular-arc construction from three independent dimensions.")
    O, In, Rl = b.inp("Outer radius"), b.inp("Inner radius"), b.inp("Lobe radius")
    er = b.once(b.div(Rl, O), "Normalised lobe radius")
    br = b.once(b.div(In, O), "Normalised valley radius")
    c = b.once(b.sub(R(1), er), "Lobe centre radius")
    numerator = b.sub(b.sub(b.add(b.mul(br, br), b.mul(c, c)),
                            b.mul(b.mul(br, c), R(2 * COS30))), b.mul(er, er))
    denominator = b.mul(R(2), b.sub(b.add(er, b.mul(c, R(COS30))), br))
    ir = b.once(b.div(numerator, denominator), "Derived concave radius")
    d = b.once(b.add(br, ir), "Valley centre radius")
    fraction = b.once(b.div(er, b.add(er, ir)), "Tangency fraction")
    tx = b.once(b.mul(O, b.add(c, b.mul(b.sub(b.mul(d, R(COS30)), c), fraction))),
                "Junction X")
    ty = b.once(b.mul(O, b.mul(b.mul(d, R(0.5)), fraction)), "Junction Y")

    def rotated(x, y, theta, label):
        x = b.once(x, label + " X")
        y = b.once(y, label + " Y")
        cp, sp = math.cos(theta), math.sin(theta)
        return b.once(b.PT(b.sub(b.mul(x, R(cp)), b.mul(y, R(sp))),
                           b.add(b.mul(x, R(sp)), b.mul(y, R(cp))), L(0)),
                      label, "point")

    pts = []
    for k in range(6):
        t = k * math.pi / 3
        pts.append({"lo": rotated(tx, b.neg(ty), t, "Junction %d lower" % k),
                    "hi": rotated(tx, ty, t, "Junction %d upper" % k),
                    "tip": rotated(O, L(0), t, "Lobe %d" % k),
                    "valley": rotated(In, L(0), t + math.pi / 6, "Valley %d" % k)})
    arcs = []
    for k in range(6):
        arcs.append(b.arc(pts[k]["lo"], pts[k]["tip"], pts[k]["hi"]))
        arcs.append(b.arc(pts[k]["hi"], pts[k]["valley"], pts[(k + 1) % 6]["lo"]))
    profile = b.profile_from_curves(arcs, V(0, 0, 1))
    body = b.extrude(profile, b.inp("Depth"), V(0, 0, 1), symmetric=False, draft=A(0))
    b.VAR("result", "Torx internal cutting body", "implicit", body)
    return _define(b, "Torx Internal",
                   "Parametric tangent-arc kernel. Default CAD contour uses ISO 10664:1999 "
                   "Table 1 dimensions and an informative Annex A radius choice. Not a "
                   "unique standard-mandated contour. Local origin at mouth; +Z into recess.",
                   "result")


# --------------------------------------------------------------------------
# 2. Screw Head: the cylindrical head
# --------------------------------------------------------------------------
def screw_head():
    """Generic cylindrical screw head. Both circular rounds are actual arcs in a
    single revolved section; neither is approximated by a chamfer."""
    b = Recipe([
        ("Head radius", "real", {"length": 1}, L(.00275),
         "Radius of cylindrical head envelope."),
        ("Head height", "real", {"length": 1}, L(.003),
         "Distance above the seating plane."),
        ("Shank radius", "real", {"length": 1}, L(.0015),
         "Neck radius below the seating plane."),
        ("Top round", "real", {"length": 1}, L(.0003),
         "Circular rounding of top outside edge. Positive, less than head height/radius."),
        ("Underhead fillet", "real", {"length": 1}, L(.0001),
         "Positive circular shank-to-seating-plane fillet."),
        ("Neck length", "real", {"length": 1}, L(.001),
         "Neck length including underhead fillet, along +Z."),
    ])
    Rh, h = b.inp("Head radius"), b.inp("Head height")
    s, r = b.inp("Shank radius"), b.inp("Top round")
    f, n = b.inp("Underhead fillet"), b.inp("Neck length")
    b.sec("Axial section", "Head above z=0; shank below, along +Z.")
    pt = lambda name, x, z: b.once(b.pt(x, 0, z), name, "point")
    a = pt("Axis at top", L(0), b.neg(h))
    bb = pt("Top tangent", b.sub(Rh, r), b.neg(h))
    c = pt("Side tangent", Rh, b.add(b.neg(h), r))
    d = pt("Head seating edge", Rh, L(0))
    e = pt("Fillet seating tangent", b.add(s, f), L(0))
    ff = pt("Fillet shank tangent", s, f)
    g = pt("Neck end", s, n)
    i = pt("Axis at neck end", L(0), n)
    k = SQRT1_2
    m_top = pt("Top arc midpoint", b.sub(Rh, b.mul(r, R(1 - k))),
               b.add(b.neg(h), b.mul(r, R(1 - k))))
    m_fillet = pt("Fillet midpoint", b.add(s, b.mul(f, R(1 - k))), b.mul(f, R(1 - k)))
    profile = b.profile_from_curves(
        [b.line(a, bb), b.arc(bb, m_top, c), b.line(c, d), b.line(d, e),
         b.arc(e, m_fillet, ff), b.line(ff, g), b.line(g, i), b.line(i, a)], V(0, 1, 0))
    b.VAR("result", "Cylindrical screw head", "implicit", b.revolve(profile, b.axisZ()))
    return _define(b, "Screw Head",
                   "Parametric cylindrical head with circular top edge and underhead fillet. "
                   "Seating plane z=0, neck along +Z. Input dimensions select a CAD design; "
                   "no tolerance-class conformity claim.", "result")


# --------------------------------------------------------------------------
# 3. Pan Head
# --------------------------------------------------------------------------
def pan_head():
    """Spherical crown, cylindrical side, circular underhead fillet.

    The source rf is explicitly approximate; representing it by an exact
    spherical crown is a declared CAD choice, not a source prescription. The
    unspecified microscopic crown-to-side round is omitted.
    """
    b = Recipe([
        ("Head radius", "real", {"length": 1}, L(.0028), "Maximum outside radius."),
        ("Head height", "real", {"length": 1}, L(.0024),
         "Apex above the underhead seating plane."),
        ("Shank radius", "real", {"length": 1}, L(.0015), "Neck radius."),
        ("Crown radius", "real", {"length": 1}, L(.005),
         "Spherical cap radius; source rf is approximate. Must exceed head radius."),
        ("Underhead fillet", "real", {"length": 1}, L(.0001), "Circular underhead fillet."),
        ("Neck length", "real", {"length": 1}, L(.001),
         "Seating plane to end of plain neck."),
    ])
    b.sec("Pan head section",
          "Spherical crown, cylindrical side and circular underhead fillet. The "
          "unspecified microscopic crown-to-side rounding is omitted.")
    Rh, h = b.inp("Head radius"), b.inp("Head height")
    s, rf = b.inp("Shank radius"), b.inp("Crown radius")
    f, n = b.inp("Underhead fillet"), b.inp("Neck length")
    ratio = b.once(b.div(Rh, rf), "Crown normalised radius")
    cos = b.once(b.sqrt(b.sub(R(1), b.mul(ratio, ratio))), "Crown edge cosine")
    half = b.once(b.div(b.atan2(ratio, cos), R(2)), "Half crown sweep")
    pt = lambda label, x, z: b.once(b.pt(x, 0, z), label, "point")
    a = pt("Apex", L(0), b.neg(h))
    c = pt("Crown edge", Rh, b.add(b.neg(h), b.mul(rf, b.sub(R(1), cos))))
    m = pt("Crown midpoint", b.mul(rf, b.sin(half)),
           b.add(b.neg(h), b.mul(rf, b.sub(R(1), b.cos(half)))))
    d = pt("Seat outer edge", Rh, L(0))
    e = pt("Seat fillet start", b.add(s, f), L(0))
    g = pt("Neck fillet end", s, f)
    k = SQRT1_2
    mf = pt("Fillet midpoint", b.add(s, b.mul(f, R(1 - k))), b.mul(f, R(1 - k)))
    ne = pt("Neck end", s, n)
    ax = pt("Axis at neck end", L(0), n)
    profile = b.profile_from_curves(
        [b.arc(a, m, c), b.line(c, d), b.line(d, e), b.arc(e, mf, g),
         b.line(g, ne), b.line(ne, ax), b.line(ax, a)], V(0, 1, 0))
    b.VAR("result", "Pan head", "implicit", b.revolve(profile, b.axisZ()))
    return _define(b, "Pan Head",
                   "Parametric pan-head CAD kernel. ISO14583 approximate rf represented by a "
                   "spherical crown, with cylindrical side and exact circular underhead "
                   "fillet. Small unspecified outer-edge round omitted. Underhead plane z=0; "
                   "head -Z, neck +Z.", "result")


# --------------------------------------------------------------------------
# 4. Countersunk Head 2013
# --------------------------------------------------------------------------
def countersunk_head():
    """Historical ISO 14581:2013 envelope: flat rim, 90-degree included cone.

    Deliberately short. A longer revolved neck misclassified exterior points in
    a measured failure; the assembly carries the shoulder with a native cylinder
    instead, leaving this kernel unchanged.
    """
    b = Recipe([
        ("Head radius", "real", {"length": 1}, L(.00275),
         "Actual maximum head radius, not theoretical sharp-cone radius."),
        ("Head height", "real", {"length": 1}, L(.00165), "Maximum axial head height."),
        ("Shank radius", "real", {"length": 1}, L(.0015), "Cone ends at this radius."),
        ("Neck length", "real", {"length": 1}, L(.001),
         "Plain shoulder below cone before full thread."),
    ])
    b.sec("Historical countersunk section",
          "ISO14581:2013 candidate envelope: 90-degree included cone, flat rim, sharp "
          "cone-to-shank junction.")
    Rh, h = b.inp("Head radius"), b.inp("Head height")
    s, n = b.inp("Shank radius"), b.inp("Neck length")
    pt = lambda label, x, z: b.once(b.pt(x, 0, z), label, "point")
    ps = [pt("Top centre", L(0), b.neg(h)),
          pt("Top rim", Rh, b.neg(h)),
          pt("Cone outer edge", Rh, b.neg(b.sub(Rh, s))),
          pt("Cone end", s, L(0)),
          pt("Neck end", s, n),
          pt("Axis at neck", L(0), n)]
    edges = [b.line(p, ps[(i + 1) % len(ps)]) for i, p in enumerate(ps)]
    profile = b.profile_from_curves(edges, V(0, 1, 0))
    b.VAR("result", "Countersunk head", "implicit", b.revolve(profile, b.axisZ()))
    return _define(b, "Countersunk Head 2013",
                   "Historical ISO14581:2013 derived CAD head envelope; flat rim and "
                   "90-degree included cone. Cone-to-neck round omitted. Local cone end z=0, "
                   "head -Z, neck +Z. Public assembly moves the top face to insertion datum "
                   "and includes the head in total length.", "result")


# --------------------------------------------------------------------------
# 5. Metric Thread Kernel
# --------------------------------------------------------------------------
THREAD_DEFAULTS = {"Major Radius": 0.003, "Minor Radius": 0.0025, "Pitch": 0.001,
                   "Crest Width": 0.000125, "Length": 0.010,
                   "Flank Slope": math.sqrt(3)}


def metric_thread():
    """Generic flat-root external helical thread. No standard or tolerance claim.

    The radius law is an exact zero-set construction, not a Euclidean signed
    distance: an analytic periodic phase, so graph size is independent of turn
    count. Right-handed crest at z = Pitch*theta/(2*pi) + k*Pitch.
    """
    inputs = []
    for name, value in THREAD_DEFAULTS.items():
        slope = name == "Flank Slope"
        inputs.append((name, "real", {} if slope else {"length": 1},
                       R(value) if slope else L(value),
                       "Positive radial change per axial change on a flank. Candidate "
                       "default sqrt(3)." if slope else
                       "Positive SI length. Demonstration default only; no thread-standard "
                       "conformance claimed."))
    b = Recipe(inputs)
    inp, ref = b.inp, b.ref
    b.sec("Helical coordinates",
          "An analytic periodic phase; graph size is independent of turn count.")
    b.VAR("th_theta", "Polar angle", "real_field",
          b.F("atan2<real_field,real_field>", [X("y"), X("x")]))
    b.VAR("th_angle", "Helical phase", "real_field",
          b.fsub(b.fmul(b.fdiv(X("z"), inp("Pitch")), A(TWO_PI)), ref("th_theta")))
    b.VAR("th_cos", "Periodic cosine", "real_field",
          b.F("cos<real_field>", [ref("th_angle")]))
    b.VAR("th_phase", "Axial distance from crest centre", "real_field",
          b.fmul(b.fdiv(b.F("acos<real_field>", [ref("th_cos")]), A(TWO_PI)), inp("Pitch")))
    b.sec("Axial profile",
          "Flat crest and flat root joined by straight flanks; generic profile parameters.")
    b.VAR("th_drop", "Flank radial drop", "real_field",
          b.fmul(b.fmax(b.fsub(ref("th_phase"), b.div(inp("Crest Width"), R(2))), L(0)),
                 inp("Flank Slope")))
    b.VAR("th_radius", "Thread surface radius", "real_field",
          b.fmax(inp("Minor Radius"), b.fsub(inp("Major Radius"), ref("th_drop"))))
    b.VAR("th_r", "Cylindrical radius", "real_field",
          b.F("sqrt<real_field>", [b.fadd(b.fmul(X("x"), X("x")), b.fmul(X("y"), X("y")))]))
    b.VAR("th_radial", "Radial residual", "real_field",
          b.fsub(ref("th_r"), ref("th_radius")))
    b.sec("Length and bounds",
          "Flat ends at z=0 and z=Length. No runout or lead-in is implied.")
    b.VAR("th_capped", "Capped field", "real_field",
          b.fmax(ref("th_radial"),
                 b.fmax(b.fmul(X("z"), R(-1)), b.fsub(X("z"), inp("Length")))))
    b.VAR("th_box", "Driven bounds", "bounding_box",
          b.bbox(b.pt(b.neg(inp("Major Radius")), b.neg(inp("Major Radius")), L(0)),
                 b.pt(inp("Major Radius"), inp("Major Radius"), inp("Length"))))
    b.VAR("Thread", "Thread", "implicit", b.SBB(ref("th_capped"), ref("th_box")))
    return _define(b, "Metric Thread Kernel",
                   "Generic parametric external thread with straight flanks and flat "
                   "root/crest, along local +Z. Exact helical zero set; field is radial "
                   "residual with axial caps, not Euclidean distance. No standards "
                   "conformance claimed. No runout or lead-in.", "Thread")


# --------------------------------------------------------------------------
# 6. Torx Local Development: source-row selection and assembly
# --------------------------------------------------------------------------
def torx_local(head, pan, countersunk, thread, drive):
    """Select a source row, gate the inputs, and assemble one screw.

    Selection is a chain of `core.if` on an exact integer key of series and size
    identifier, so a value is only ever read from the row that owns it. The gate
    is `sqrt(+1 or -1)`: an invalid configuration makes the whole assembly refuse
    to evaluate rather than build a plausible wrong screw.
    """
    b = Recipe([
        ("Drive family", "integer", {}, I(0),
         "0=internal; 1=tamper-resistant custom derivative with sourced round post."),
        ("Screw series", "integer", {}, I(0),
         "0=cylindrical2011, 1=pan2011, 2=countersunk2013 historical."),
        # A description belongs to the block's content key (rule I4), so this
        # string is preserved verbatim from the recorded block and still names
        # the source project's `catalogue.js`. `torx_catalogue.py` is its port.
        ("Metric size index", "integer", {}, I(2),
         "Stable source-row identifier from catalogue.js; M2 through M20."),
        ("Drive size", "integer", {}, I(0),
         "0=automatic for metric size; otherwise one of the sixteen supplied "
         "ISO 10664:1999 size numbers."),
        ("Length", "real", {"length": 1}, L(.010),
         "Raised heads: underhead to tip. Countersunk: total length including head."),
        ("Override shank", "bool", {}, B(False),
         "Enable custom scaling from the selected metric envelope."),
        ("Shank radius", "real", {"length": 1}, L(.0015),
         "Used only with override; scales pitch and head dimensions proportionally."),
        ("Override Torx", "bool", {}, B(False),
         "Enable independent recess radius scaling."),
        ("Torx radius", "real", {"length": 1}, L(.0014),
         "Maximum recess radius, independently controlled."),
    ])
    once = b.once
    rows = cat.SOURCE_ROWS

    def select(table, key, col, units=True):
        x = L(-1) if units else R(-1)
        for row in reversed(table):
            x = b.IF(b.eq(key, row[0]),
                     L(row[col] / 1000) if units else R(row[col]), x)
        return once(x, "Selected source column %d" % col)

    b.sec("Source size selection",
          "ISO 10664:1999 drive sizes; ISO 14579:2011 head bounds. Development CAD "
          "choices within the cited bounds.")
    series = b.inp("Screw series")
    idx = once(b.add(b.mul(series, R(100)), b.inp("Metric size index")), "Series size key")
    nominal_r = once(b.div(select(rows, idx, 1), R(2)), "Nominal shank radius")
    sr = once(b.IF(b.inp("Override shank"), b.inp("Shank radius"), nominal_r),
              "Selected shank radius")
    scale = once(b.div(sr, nominal_r), "Custom shank scale")
    val = lambda col: once(b.mul(select(rows, idx, col), scale),
                           "Scaled source column %d" % col)
    pitch = val(2)
    head_r = once(b.div(val(3), R(2)), "Head radius")
    height, top, fillet = val(4), val(5), val(6)
    short_neck, depth = val(7), val(8)
    thread_length, short_length_max, web = val(10), val(11), val(12)
    crown = val(13)
    tip = once(b.IF(b.eq(series, 2), b.sub(b.inp("Length"), height), b.inp("Length")),
               "Tip from cone-end or underhead plane")
    long_cylinder = b.AND(b.eq(series, 0), b.lt(short_length_max, tip))
    neck = once(b.IF(long_cylinder, b.sub(tip, thread_length), short_neck),
                "Thread start: short neck or long l minus b")
    ds = once(b.IF(b.eq(b.inp("Drive size"), 0), select(rows, idx, 9, units=False),
                   b.inp("Drive size")), "Selected drive size")
    nominal_a = select(cat.DRIVE_ROWS, ds, 1)
    nominal_b = select(cat.DRIVE_ROWS, ds, 2)
    dr = once(b.IF(b.inp("Override Torx"), b.inp("Torx radius"), b.div(nominal_a, R(2))),
              "Drive major radius")
    inner = once(b.mul(dr, b.div(nominal_b, nominal_a)), "Drive minor radius")
    is_internal = b.eq(b.inp("Drive family"), 0)
    is_tamper = b.eq(b.inp("Drive family"), 1)
    post_nominal = select(cat.POST_ROWS, ds, 1)
    post_radius = once(b.IF(b.eq(b.inp("Drive family"), 1),
                            b.mul(dr, b.div(post_nominal, nominal_a)),
                            b.mul(inner, R(.1))), "Post radius scaled with recess")
    valid = b.OR(is_internal, b.AND(is_tamper, b.lt(L(0), post_nominal)))
    floor_wall = b.IF(b.eq(series, 2), b.lt(dr, b.add(sr, b.sub(height, depth))), B(True))
    valid = b.AND(valid, floor_wall)
    for condition in [b.lt(L(0), nominal_r), b.lt(L(0), sr), b.lt(L(0), dr),
                      b.lt(dr, b.sub(head_r, top)), b.lt(neck, tip), b.lt(L(0), neck),
                      b.lt(post_radius, inner), b.lt(web, b.sub(height, depth))]:
        valid = b.AND(valid, condition)
    gate = once(b.sqrt(b.IF(valid, R(1), R(-1))),
                "CHECK FAMILY POST SIZE HEAD WALL AND LENGTH")

    b.sec("Referenced components",
          "One call per component. Basic-profile thread pending actual design-root "
          "specification.")
    cylindrical = b.call(head, [head_r, height, sr, top, fillet, short_neck])
    pan_body = b.call(pan, [head_r, height, sr, crown, fillet, short_neck])
    # Keep the revolved countersunk component short; the native cylinder carries
    # the prescribed shoulder. Longer revolved necks misclassify exterior points.
    csk_body = b.call(countersunk, [head_r, height, sr, b.mul(pitch, R(.25))])
    head_body = b.once(b.IF(b.eq(series, 0), cylindrical,
                            b.IF(b.eq(series, 1), pan_body, csk_body)),
                       "Selected head", "implicit")
    stem = b.once(b.cyl(b.pt(0, 0, 0), b.pt(L(0), L(0), neck), sr),
                  "Plain shank extension", "implicit")
    minor = once(b.sub(sr, b.mul(pitch, R(5 * math.sqrt(3) / 16))),
                 "ISO 68-1 basic minor radius")
    thread_body = b.once(b.call(thread, [sr, minor, pitch, b.div(pitch, R(8)),
                                         b.mul(b.sub(tip, neck), gate), R(math.sqrt(3))]),
                         "Basic thread", "implicit")
    placed_thread = b.once(b.translate(thread_body, b.vector(L(0), L(0), neck)),
                           "Thread at neck", "implicit")
    cutter = b.once(b.call(drive, [dr, inner, b.mul(dr, R(.2)), depth]),
                    "Recess cutting body", "implicit")
    pin = b.cyl(b.pt(0, 0, 0), b.pt(L(0), L(0), depth), post_radius)
    family_cutter = b.once(b.IF(b.eq(b.inp("Drive family"), 1),
                                b.subtractS(cutter, [pin]), cutter),
                           "Family recess", "implicit")
    placed_cutter = b.once(b.translate(family_cutter, b.vector(L(0), L(0), b.neg(height))),
                           "Recess in head", "implicit")
    local_body = b.once(b.subtractS(b.unionS([head_body, stem, placed_thread]),
                                    [placed_cutter]),
                        "Screw at head-end plane", "implicit")
    b.VAR("result", "Complete local screw", "implicit",
          b.translate(local_body,
                      b.vector(L(0), L(0), b.IF(b.eq(series, 2), height, L(0)))))
    return _define(b, "Torx Local Development",
                   "DEVELOPMENT screw assembly: cylindrical ISO14579:2011, pan "
                   "ISO14583:2011, countersunk ISO14581:2013 historical. Dimensional bounds "
                   "plus declared representative CAD profiles. Derived ISO10664:1999 "
                   "internal contour; Camcar round posts create custom tamper-resistant "
                   "derivatives. Basic ISO68-1 thread; root/runout/tip simplified. Native "
                   "cylindrical extension avoids the measured long revolved-neck error. "
                   "Countersunk datum is top face, length includes head; other series use "
                   "underhead datum.",
                   "result", deps=[countersunk, drive, head, pan, thread])


# --------------------------------------------------------------------------
# 7. Place Screw: rigid placement into a surface frame
# --------------------------------------------------------------------------
def place_screw():
    """Rigid placement from local XYZ into a right-handed surface frame.

    The body is never rebuilt. The source field is evaluated at the inverse
    coordinate map, and the bounding box is transformed rigidly and reprojected,
    so the placed body keeps driven bounds. No fallback is defined for a zero
    Axis or a Tangent Reference parallel to it: both are refused, not guessed.
    """
    source = {"func": "box<point,real,real,real>", "id": "d1", "name": "d1",
              "inputs": [P3(0, 0, 0.005), L(0.006), L(0.004), L(0.010)]}
    b = Recipe([
        ("Implicit Body", "implicit", None, source,
         "Source geometry in its local XYZ frame."),
        ("Insertion Point", "point", {"length": 1}, P3(0, 0, 0),
         "World location of the source local origin."),
        ("Axis", "vector", {}, V(0, 0, 1),
         "Nonzero direction of local +Z; magnitude is normalised."),
        ("Tangent Reference", "vector", {}, V(1, 0, 0),
         "Nonzero reference projected perpendicular to Axis; must not be parallel to Axis."),
        ("Clocking Angle", "real", {"angle": 1}, A(0),
         "Right-handed rotation around Axis, SI radians."),
    ])
    inp, ref = b.inp, b.ref
    axes = ["x", "y", "z"]
    b.sec("Surface frame",
          "Normalise Axis and project Tangent Reference. The frame requires nonzero "
          "independent axes.")
    b.VAR("pl_z", "Normalised axis", "vector", inp("Axis", ["unit vector"]))
    b.VAR("pl_yraw", "Perpendicular tangent", "vector",
          b.cross(ref("pl_z"), inp("Tangent Reference")))
    b.VAR("pl_y0", "Normalised transverse direction", "vector", ref("pl_yraw", ["unit vector"]))
    b.VAR("pl_x0", "Projected tangent direction", "vector", b.cross(ref("pl_y0"), ref("pl_z")))
    b.VAR("pl_cos", "Clocking cosine", "real", b.cos(inp("Clocking Angle")))
    b.VAR("pl_sin", "Clocking sine", "real", b.sin(inp("Clocking Angle")))
    b.VAR("pl_x", "Clocked tangent", "vector",
          b.vector(*[b.add(b.mul(ref("pl_x0", [a]), ref("pl_cos")),
                           b.mul(ref("pl_y0", [a]), ref("pl_sin"))) for a in axes]))
    b.VAR("pl_y", "Clocked transverse direction", "vector", b.cross(ref("pl_z"), ref("pl_x")))
    b.VAR("pl_frame", "Placement frame", "frame",
          b.frame(inp("Insertion Point"), ref("pl_x"), ref("pl_y")))
    b.sec("Inverse coordinate map",
          "Evaluate the unchanged source body at dot(world-origin, frame axes).")
    for a in axes:
        b.VAR("pl_d" + a, "World displacement " + a, "real_field",
              b.fsub(X(a), inp("Insertion Point", [a])))
    for a in axes:
        total = None
        for c in axes:
            term = b.fmul(ref("pl_d" + c), ref("pl_frame", [a + " axis", c]))
            total = term if total is None else b.fadd(total, term)
        b.VAR("pl_q" + a, "Local " + a, "real_field", total)
    b.VAR("pl_mapped", "Placed field", "real_field",
          b.REMAP(inp("Implicit Body"), ref("pl_qx"), ref("pl_qy"), ref("pl_qz")))
    b.sec("Driven bounds",
          "Rigidly transform the source bounding-box centre and project its half-extents.")
    for a in axes:
        b.VAR("pl_c" + a, "Source bounds centre " + a, "real",
              b.div(b.add(inp("Implicit Body", ["bounding box", "min point", a]),
                          inp("Implicit Body", ["bounding box", "max point", a])), R(2)))
        b.VAR("pl_h" + a, "Source bounds half span " + a, "real",
              b.div(b.sub(inp("Implicit Body", ["bounding box", "max point", a]),
                          inp("Implicit Body", ["bounding box", "min point", a])), R(2)))
    for a in axes:
        total = None
        for c in axes:
            term = b.mul(ref("pl_c" + c), ref("pl_frame", [c + " axis", a]))
            total = term if total is None else b.add(total, term)
        b.VAR("pl_wc" + a, "Placed bounds centre " + a, "real",
              b.add(inp("Insertion Point", [a]), total))
        total = None
        for c in axes:
            term = b.mul(ref("pl_h" + c), b.abs(ref("pl_frame", [c + " axis", a])))
            total = term if total is None else b.add(total, term)
        b.VAR("pl_wh" + a, "Placed bounds half span " + a, "real", total)
    b.VAR("pl_bounds", "Placed bounds", "bounding_box",
          b.bbox(b.pt(*[b.sub(ref("pl_wc" + a), ref("pl_wh" + a)) for a in axes]),
                 b.pt(*[b.add(ref("pl_wc" + a), ref("pl_wh" + a)) for a in axes])))
    b.VAR("Placed", "Placed Body", "implicit", b.SBB(ref("pl_mapped"), ref("pl_bounds")))
    return _define(b, "Place Screw",
                   "Rigid placement. Local +Z follows Axis; local +X follows the "
                   "perpendicular projection of Tangent Reference then Clocking Angle. "
                   "Insertion Point places local origin. Axis and projected tangent must be "
                   "nonzero.", "Placed")


# --------------------------------------------------------------------------
# 8. Torx: the public block
# --------------------------------------------------------------------------
TORX_DESCRIPTION = (
    "DEVELOPMENT COMPLETE SCREW. Native Choice List family, series, metric and drive size. "
    "Internal and tamper-resistant derived drives. Cylindrical ISO14579:2011 M2-M20, pan "
    "ISO14583:2011 M2-M10, historical countersunk ISO14581:2013 M2-M10. Basic ISO68-1 "
    "thread; actual root/runout and tip remain simplified. Independent radius overrides. "
    "Raised heads use underhead datum/length; countersunk uses flush top datum and total "
    "length. No manufacturing conformity claim.")


SELECTED = ("Drive family", "Screw series", "Metric size index", "Drive size")


def _input_rows(definition):
    """The (name, type, dimension, default, description) rows a definition declares.

    The public block reuses the local assembly's own rows for everything it does
    not replace with a Choice List, so no dimension, default or description is
    written a second time.
    """
    return [(i["name"], i["type"], i.get("dimension", {}), i.get("contents"),
             i.get("description", "")) for i in definition["inputs"]]


def torx(local, place):
    """The public block. Four native Choice Lists select stable source identifiers.

    A size is never entered as a numeric code. Each Choice List maps its selected
    label to the identifier the local assembly expects, through
    `core.select_by_choice`, so the public interface and the source tables can
    change independently.
    """
    local_inputs = _input_rows(local)
    passthrough = [row for row in local_inputs if row[0] not in SELECTED]
    b = Recipe([
        ("Drive family", "choice", {}, CHOICE([r["label"] for r in cat.FAMILIES]),
         "Native Choice List. Tamper-resistant is a custom cylindrical-head derivative "
         "using sourced Camcar post dimensions."),
        ("Screw series", "choice", {}, CHOICE([r["label"] for r in cat.SERIES]),
         "Native Choice List. Additional source-backed head series can be added without "
         "changing the placement interface."),
        ("Metric size", "choice", {}, CHOICE([r["label"] for r in cat.SCREWS], 2),
         "Native Choice List: nominal diameter and coarse pitch."),
        ("Drive size", "choice", {},
         CHOICE(["Automatic"] + ["T%d" % r["size"] for r in cat.DRIVES]),
         "Native Choice List. Automatic uses the metric source row. Tamper-resistant "
         "requires a sourced post for the selected drive."),
        *passthrough,
        ("Insertion Point", "point", {"length": 1}, P3(0, 0, 0),
         "Raised heads: centre of underhead seating plane. Countersunk: top-face centre, "
         "flush datum."),
        ("Axis", "vector", {}, V(0, 0, 1),
         "Direction towards screw tip. Non-zero; magnitude is ignored."),
        ("Tangent Reference", "vector", {}, V(1, 0, 0),
         "Projected into seating plane to define lobe orientation; cannot be parallel to Axis."),
        ("Clocking Angle", "real", {"angle": 1}, A(0),
         "Additional right-handed rotation about Axis."),
    ])
    b.sec("Dropdown selections",
          "Native Choice List inputs select stable source identifiers; sizes never require "
          "numeric code entry.")

    def select(name, values):
        return b.once(b.F("core.select_by_choice<choice,list_interface>",
                          [b.inp(name), b.LIST("integer", [I(v) for v in values])]),
                      name + " selection", "integer")

    mapped = {
        "Drive family": select("Drive family", [r["id"] for r in cat.FAMILIES]),
        "Screw series": select("Screw series", [r["id"] for r in cat.SERIES]),
        "Metric size index": select("Metric size", [r["id"] for r in cat.SCREWS]),
        "Drive size": select("Drive size", [0] + [r["size"] for r in cat.DRIVES]),
    }
    b.sec("Referenced screw",
          "A single local assembly call, followed by an independent placement call.")
    args = [mapped.get(row[0]) or b.inp(row[0]) for row in local_inputs]
    screw = b.once(b.call(local, args), "Local screw", "implicit")
    b.VAR("result", "Torx", "implicit",
          b.call(place, [screw, b.inp("Insertion Point"), b.inp("Axis"),
                         b.inp("Tangent Reference"), b.inp("Clocking Angle")]))
    return b


# --------------------------------------------------------------------------
# the whole recipe
# --------------------------------------------------------------------------
def graph():
    """Build every block and return the complete public recipe."""
    head = screw_head()
    pan = pan_head()
    csk = countersunk_head()
    thread = metric_thread()
    drive = torx_internal()
    local = torx_local(head, pan, csk, thread, drive)
    place = place_screw()
    b = torx(local, place)
    imports = flatten([local, place])
    recipe = b.envelope(IDENTITIES["Torx"], "Torx", TORX_DESCRIPTION, "result",
                        imports=imports)
    return recipe, b, {"Screw Head": head, "Pan Head": pan,
                       "Countersunk Head 2013": csk, "Metric Thread Kernel": thread,
                       "Torx Internal": drive, "Torx Local Development": local,
                       "Place Screw": place}


if __name__ == "__main__":
    from torx_backend import count_nodes, validate
    recipe, ctx, blocks = graph()
    print(json.dumps({
        "name": recipe["name"], "inputs": len(recipe["inputs"]),
        "root_body": len(recipe["body"]), "imports": len(recipe["imports"]),
        "import_order": [d["displayname"] for d in recipe["imports"]],
        "cbRefs": recipe["cbRefs"],
        "func_nodes": count_nodes(recipe),
        "problems": validate(recipe)}, indent=2))
