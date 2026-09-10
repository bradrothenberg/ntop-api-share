"""Native RC appearance splitter fitted to the user's planform annotation.

The annotation determines the visible planform. It provides no flow or engine
performance data. A negative roof offset embeds the splitter in the existing lip.
"""


def build_gap_splitter(r, *, x, y, z, ay, w, forelower, lip_roof, scale, S,
                       aft_station_source=-1.20):
    def v(name, value, kind='real_field'):
        return r.var(name, kind, value, 'Gap splitter fields')

    def control(name, source_value):
        rc = r.var(name, 'real', r.length(source_value * (4.8768 / 7.46)), 'Gap splitter controls')
        return v(name + ' in guide coordinates', r.call('divide<real,real>', 'real', rc, scale), 'real')

    start = control('Gap splitter start station', -2.60)
    end = control('Gap splitter aft station', aft_station_source)
    offset = control('Gap splitter inlet-roof offset', -.003)
    width_factor = r.var('Gap splitter aft width multiplier', 'real', r.real(1.0), 'Gap splitter controls')
    raw_u = v('Splitter longitudinal coordinate', r.call('divide<real_field,real_field>',
                'real_field', r.sub(x, start), r.sub(end, start)))
    u = v('Splitter bounded coordinate', r.either(r.real(1), r.both(r.real(0), raw_u)))
    # Cubic width progression with Bezier ordinates 0, .05, .35, 1. The X
    # ordinates are uniformly spaced, so this is an explicit cubic spline.
    # It tracks the annotation-derived narrow nose and progressively wider aft.
    profile = v('Splitter cubic width fraction', r.mul(u,
                r.add(r.real(.15), r.mul(u, r.add(r.real(.75), r.mul(u, r.real(.10)))))))
    width = v('Splitter local half width', r.mul(r.mul(w, width_factor), profile))
    planform = v('Splitter curved planform field', r.both(r.sub(ay, width),
                  r.sub(start, x), r.sub(x, end)))
    # Top overlap is entirely inside the existing forebody. A small negative
    # lower offset similarly makes a robust bridge into the existing inlet roof.
    # Positive offsets give a hanging splitter with an explicit lower clearance.
    top = v('Splitter fuselage attachment limit', r.sub(r.neg(forelower), r.length(.003 * S)))
    bottom = v('Splitter lower attachment limit', r.call(
        'remap<real_field,real_field,real_field,real_field>', 'real_field',
        lip_roof, x, y, r.sub(z, offset)))
    splitter = v('Gap center splitter', r.bound(r.both(planform, top, bottom),
                [-2.65, -1.1, -.55], [-1.15, 1.1, .2]), 'implicit')
    return splitter
