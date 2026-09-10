"""Editable conceptual RC internal arrangement made from native primitives.

All sizes are design placeholders or fractions of the reconstructed envelope.
They are not selected hardware, verified installation clearances, production
Fury data, or a mass model. The engine envelope occupies the conceptual duct.
The helper returns separate inspection bodies and never changes the exterior.
"""

import numpy as np
from scipy.interpolate import BSpline


NOMINAL_SPAN_M = 4.8768
SOURCE_SPAN = 7.46


def _guide_at(guides, name, station):
    data = guides[name]
    count = len(data['y'])
    knots = np.r_[np.zeros(4), np.arange(1, count - 3) / (count - 3), np.ones(4)]
    parameter = (station - data['x'][0]) / (data['x'][-1] - data['x'][0])
    return float(BSpline(knots, data['y'], 3)(parameter))


def layout_defaults(guide_info, source, *, wing_offset_rc_m=0.0, tail_span_multiplier=1.0):
    """Return explicit placeholder allocations in normalized source coordinates.

    Source station choices establish a rough arrangement. Section dimensions
    come from the current fitted guides or the supplied lifting-surface rows.
    These allocations have no inferred hardware dimensions or specifications.
    """
    if not np.isfinite(wing_offset_rc_m) or not np.isfinite(tail_span_multiplier) or tail_span_multiplier <= 0:
        raise ValueError('Placement requires a finite wing offset and positive HStab span multiplier.')
    allocations = []

    def g(name, xx):
        return _guide_at(guide_info, name, xx)

    def add(name, role, center, size, color, basis, shape='box'):
        allocations.append(dict(name=name, role=role, shape=shape,
                                center_source=list(map(float, center)),
                                dimensions_source=list(map(float, size)),
                                color=color, concept_basis=basis))

    gold = [.86, .57, .20, 1.]
    cyan = [.18, .68, .68, 1.]
    blue = [.25, .49, .84, 1.]
    battery_blue = [.38, .61, .77, 1.]
    orange = [.91, .40, .19, 1.]
    purple = [.64, .43, .78, 1.]
    green = [.35, .68, .43, 1.]

    # Place the generic engine entirely in the circular portion of the passage.
    body_start = float(source['stations'][0][0])
    body_end = float(source['stations'][-1][0])
    body_length = body_end - body_start
    engine_length = .20 * body_length
    engine_center = body_end - .18 * body_length
    engine_stations = np.linspace(engine_center - engine_length / 2,
                                  engine_center + engine_length / 2, 81)
    engine_axis_z = float(np.mean([g('Duct center height', a) - 1 for a in engine_stations]))
    minimum_radius = min(g('Duct round section radius', a) for a in engine_stations)
    engine_radius = .70 * minimum_radius
    add('Engine envelope', 'Generic propulsion envelope',
        [engine_center, 0, engine_axis_z],
        [engine_length, engine_radius * 2, engine_radius * 2], gold,
        'Placeholder cylinder: length is 20% of source fuselage length; center is '
        '18% of that length forward of the aft station. Radius is 70% of the '
        'smallest fitted round-duct radius over this interval. Its straight '
        'axis uses the mean fitted duct center height. No engine is selected.',
        'cylinder_x')

    xx = -4.35
    add('Non-combat payload envelope', 'Camera or instrumentation allocation',
        [xx, 0, g('Chine datum', xx) - 1 + .40 * g('Crown', xx)],
        [.65, .70 * g('Half width', xx), .45 * g('Crown', xx)], cyan,
        'Placeholder forward station -4.35 and source length 0.65. Width is '
        '70% of local half-width; height is 45% of local crown height. Center '
        'is 40% of local crown height above the chine. Non-combat payload only.')

    xx = -2.60
    add('Avionics envelope', 'Receiver and flight electronics allocation',
        [xx, 0, g('Chine datum', xx) - 1 + .42 * g('Crown', xx)],
        [.55, .50 * g('Half width', xx), .28 * g('Crown', xx)], blue,
        'Placeholder station -2.60 and source length 0.55. Width is 50% of '
        'local half-width; height is 28% of crown height. Center is 42% of '
        'crown height above the chine. No electronics or mounting is selected.')

    xx = -1.40
    add('Electrical battery envelope', 'Electrical energy allocation',
        [xx, 0, g('Chine datum', xx) - 1 + .38 * g('Crown', xx)],
        [.65, .55 * g('Half width', xx), .30 * g('Crown', xx)], battery_blue,
        'Placeholder station -1.40 and source length 0.65. Width is 55% of '
        'local half-width; height is 30% of crown height. Center is 38% of '
        'crown height above the chine. Capacity and cell format are unspecified.')

    xx = 0.
    add('Propulsion energy-storage envelope', 'Generic energy-storage allocation',
        [xx, 0, g('Chine datum', xx) - 1 + .50 * g('Crown', xx)],
        [.85, .85 * g('Half width', xx), .43 * g('Crown', xx)], orange,
        'Placeholder station 0 and source length 0.85. Width is 85% of local '
        'half-width; height is 43% of crown height. Center is 50% of crown '
        'height above the chine. Storage technology and capacity are unspecified.')

    # Actuator blocks show only allocation volumes. They include no linkages,
    # hinge geometry, stroke, torque, redundancy, or control-system design.
    for label, rows_key, span_station, chord_fraction, length_fraction in [
            ('Wing', 'wingRows', 1.04, .72, .17),
            ('HStab', 'tailRows', .66, .67, .18)]:
        rows = np.array(source[rows_key], dtype=float)
        le, te, center_z, th = [float(np.interp(span_station, rows[:, 0], rows[:, i]))
                               for i in range(1, 5)]
        chord = te - le
        center_x = le + chord_fraction * chord
        dimensions = [length_fraction * chord, .12 * chord, .46 * th]
        for side, sign in [('left', -1), ('right', 1)]:
            add(label + ' actuator ' + side + ' envelope',
                label + ' actuator allocation',
                [center_x, sign * span_station, center_z], dimensions, purple,
                'Placeholder allocation at source span station ' + str(span_station) +
                '. Center uses ' + str(chord_fraction * 100) +
                '% of interpolated local chord and the supplied surface centerline. '
                'Box length, width, and height are ' + str(length_fraction * 100) +
                '% of chord, 12% of chord, and 46% of the source thickness parameter. '
                'No actuator or linkage is selected.')

    rows = np.array(source['finRows'], dtype=float)
    zz = float(rows[0, 0]) + .06 * float(rows[-1, 0] - rows[0, 0])
    le, te, cy, th = [float(np.interp(zz, rows[:, 0], rows[:, i])) for i in range(1, 5)]
    add('VStab actuator envelope', 'Vertical stabilizer actuator allocation',
        [le + .62 * (te - le), cy, zz],
        [.17 * (te - le), .46 * th, .10 * (rows[-1, 0] - rows[0, 0])], purple,
        'Placeholder near fin root, 6% up the supplied fin span. Center is 62% '
        'of local chord. Box length is 17% of chord, width is 46% of the '
        'source thickness parameter, and height is 10% of fin span.')

    xx = -3.60
    add('Nose gear stowed envelope', 'Nose landing gear bay allocation',
        [xx, 0, g('Chine datum', xx) - 1 + .04],
        [.70, .28 * g('Half width', xx), .34 * g('Crown', xx)], green,
        'Placeholder stowed bay at source station -3.60, length 0.70, centered '
        '0.04 above the chine. Width is 28% of local half-width; height is '
        '34% of local crown height. Wheel, strut, doors, and retraction motion '
        'are not defined.')

    xx = .65
    for side, sign in [('left', -1), ('right', 1)]:
        add('Main gear ' + side + ' stowed envelope', 'Main landing gear bay allocation',
            [xx, sign * .66 * g('Half width', xx), -.12],
            [.72, .23 * g('Half width', xx), .48 * g('Smooth inlet lower guide', xx)], green,
            'Placeholder stowed bay at source station 0.65, length 0.72 and '
            'height center -0.12. Spanwise center is 66% of local half-width. '
            'Width is 23% of local half-width; height is 48% of cowl depth. '
            'Wheel, strut, doors, and retraction motion are not defined.')

    rc_unit = NOMINAL_SPAN_M / SOURCE_SPAN
    for item in allocations:
        center = np.array(item['center_source'])
        dims = np.array(item['dimensions_source'])
        assert np.all(dims > 0), item['name']
        item['center_control_m_nominal'] = (center * rc_unit).tolist()
        item['center_reference_source'] = center.tolist()
        if item['name'].startswith('Wing actuator '):
            center[0] += wing_offset_rc_m / rc_unit
            item['attachment_transform'] = 'Wing longitudinal offset, applied after nominal center conversion'
            item['concept_basis'] += (' Center follows the photo-guided RC wing longitudinal offset. '
                                      'The offset is not a production Fury dimension.')
        elif item['name'].startswith('HStab actuator '):
            center[1] *= tail_span_multiplier
            item['attachment_transform'] = 'HStab span multiplier applied to center Y only'
            item['concept_basis'] += (' Center Y follows the photo-guided RC HStab span multiplier. '
                                      'The allocation dimensions remain independently editable.')
        item['center_source'] = center.tolist()
        item['center_m_nominal'] = (center * rc_unit).tolist()
        item['dimensions_m_nominal'] = (dims * rc_unit).tolist()
        item['bbox_m_nominal'] = {'min': ((center - dims / 2) * rc_unit).tolist(),
                                  'max': ((center + dims / 2) * rc_unit).tolist()}
        item['bbox_source'] = {'min': (center - dims / 2).tolist(),
                              'max': (center + dims / 2).tolist()}
        item['status'] = 'Editable conceptual allocation; installation not verified'
    return allocations


def build_internal_layout(r, *, x, y, z, scale, guide_info, source, S,
                          wing_offset=None, wing_offset_rc_m=0.0,
                          tail_span=None, tail_span_multiplier=1.0):
    """Return independent component bodies, colors, an aggregate, and metadata.

    Call after building the exterior. Add the returned component colors only
    to dedicated layout views, not to the normal exterior visibility map.
    Position and size controls use metres at the nominal 16 ft span. The
    base layout scales uniformly when the main RC wingspan changes. Wing
    actuator X additionally follows the absolute RC wing offset. HStab
    actuator center Y follows its dimensionless span multiplier.
    """
    del x, y, z  # Native primitive bodies do not need explicit coordinate fields.
    allocations = layout_defaults(guide_info, source, wing_offset_rc_m=wing_offset_rc_m,
                                   tail_span_multiplier=tail_span_multiplier)
    if wing_offset is None and wing_offset_rc_m != 0:
        raise ValueError('A nonzero wing offset requires the live source-native offset node.')
    if tail_span is None and tail_span_multiplier != 1:
        raise ValueError('A changed HStab span requires its live multiplier node.')
    nominal_scale = (NOMINAL_SPAN_M / SOURCE_SPAN) / S
    components = {}
    controls = []
    variable_count_before = len(r.body)

    def source_real(value):
        return r.call('divide<real,real>', 'real', value, r.real(nominal_scale))

    def center_point(center, dx=None, dy=None, dz=None, y_multiplier=None):
        values = []
        offsets = dict(x=dx, y=dy, z=dz)
        for axis in 'xyz':
            value = source_real(r.prop(center, axis))
            if axis == 'y' and y_multiplier is not None:
                value = r.call('multiply<real,real>', 'real', value, y_multiplier)
            if offsets[axis] is not None:
                value = r.call('add<real,real>', 'real', value, offsets[axis])
            values.append(value)
        return r.call('point<real,real,real>', 'point', *values)

    centers = {}
    for item in allocations:
        label = item['name']
        center_name = 'Layout ' + label + ' center'
        center = r.var(center_name, 'point', r.point(item['center_control_m_nominal']),
                       'Internal layout controls')
        centers[label] = center
        controls.append(center_name)
        if item['shape'] == 'cylinder_x':
            length_name = 'Layout engine envelope length'
            radius_name = 'Layout engine envelope radius'
            length = r.var(length_name, 'real', r.length(item['dimensions_m_nominal'][0]),
                           'Internal layout controls')
            radius = r.var(radius_name, 'real', r.length(item['dimensions_m_nominal'][1] / 2),
                           'Internal layout controls')
            controls.extend([length_name, radius_name])
            start = center_point(center, r.call('multiply<real,real>', 'real',
                                               source_real(length), r.real(-.5)))
            end = center_point(center, r.call('multiply<real,real>', 'real',
                                             source_real(length), r.real(.5)))
            primitive = r.call('cylinder<point,point,real>', 'cylinder',
                               start, end, source_real(radius))
        else:
            size_name = 'Layout ' + label + ' size'
            size = r.var(size_name, 'vector', r.vector(item['dimensions_m_nominal']),
                         'Internal layout controls')
            controls.append(size_name)
            primitive = r.call('box<point,real,real,real>', 'box',
                               center_point(center,
                                   dx=wing_offset if label.startswith('Wing actuator ') else None,
                                   y_multiplier=tail_span if label.startswith('HStab actuator ') else None),
                               *[source_real(r.prop(size, axis)) for axis in 'xyz'])
        body_name = 'RC layout ' + label
        body = r.var(body_name, 'implicit', r.call(
            'scale_object<spatial3d,real,point>[1.2.0]', 'implicit',
            primitive, scale, r.point([0, 0, 0])), 'Internal layout')
        item['body_name'] = body_name
        item['center_control'] = center_name
        item['size_controls'] = [length_name, radius_name] if item['shape'] == 'cylinder_x' else [size_name]
        components[body_name] = dict(body=body, color=item['color'], role=item['role'])

    aggregate_name = 'RC conceptual internal arrangement'
    aggregate = r.var(aggregate_name, 'implicit', r.call(
        'boolean_union<blend_enum,real_field,list<implicit>>[5.44.0]', 'implicit',
        r.enum('blend_enum', 0), r.length(0),
        r.list('implicit', [c['body'] for c in components.values()])), 'Inspection')

    # Separate deployed geometry illustrates wheel and strut locations. It is
    # not included in the stowed arrangement or the aircraft exterior output.
    # The common ground height and all hardware dimensions are placeholders.
    gear_components = {}
    gear_metadata = []
    gear_controls = []
    rc_unit = NOMINAL_SPAN_M / SOURCE_SPAN
    main_depth = _guide_at(guide_info, 'Smooth inlet lower guide', .65)
    nose_depth = _guide_at(guide_info, 'Smooth inlet lower guide', -3.60)
    ground_source = -2.05 * main_depth
    radii_source = {'Nose': .22 * nose_depth, 'Main': .30 * main_depth}
    wheel_radius_controls = {}
    for kind, radius_source in radii_source.items():
        name = 'Layout deployed ' + kind.lower() + ' wheel radius'
        wheel_radius_controls[kind] = r.var(name, 'real', r.length(radius_source * rc_unit),
                                          'Internal layout controls')
        gear_controls.append(name)
    strut_radius_source = .03 * main_depth
    strut_radius_name = 'Layout deployed gear strut radius'
    strut_radius = r.var(strut_radius_name, 'real', r.length(strut_radius_source * rc_unit),
                         'Internal layout controls')
    gear_controls.append(strut_radius_name)

    def gear_body(name, primitive, color):
        result = r.var(name, 'implicit', r.call(
            'scale_object<spatial3d,real,point>[1.2.0]', 'implicit', primitive,
            scale, r.point([0, 0, 0])), 'Landing gear illustration')
        gear_components[name] = dict(body=result, color=color,
                                    role='Deployed landing gear illustration only')

    def cylinder_bbox(a, b, radius):
        a, b = np.array(a), np.array(b)
        axis = (b - a) / np.linalg.norm(b - a)
        radial_extent = radius * np.sqrt(np.maximum(0, 1 - axis * axis))
        return {'min': ((np.minimum(a, b) - radial_extent) * rc_unit).tolist(),
                'max': ((np.maximum(a, b) + radial_extent) * rc_unit).tolist()}

    allocation_map = {c['name']: c for c in allocations}
    for label, allocation_label, kind, sign in [
            ('Nose', 'Nose gear stowed envelope', 'Nose', 0),
            ('Main left', 'Main gear left stowed envelope', 'Main', -1),
            ('Main right', 'Main gear right stowed envelope', 'Main', 1)]:
        upper = np.array(allocation_map[allocation_label]['center_source'])
        wheel_radius = radii_source[kind]
        wheel_center = np.array([
            upper[0], sign * _guide_at(guide_info, 'Half width', upper[0]),
            ground_source + wheel_radius])
        wheel_width = .55 * wheel_radius
        control_name = 'Layout deployed ' + label.lower() + ' wheel center'
        wheel_center_control = r.var(control_name, 'point', r.point(wheel_center * rc_unit),
                                    'Internal layout controls')
        gear_controls.append(control_name)
        radius = wheel_radius_controls[kind]
        endpoint_a = center_point(wheel_center_control, dy=r.call(
            'multiply<real,real>', 'real', source_real(radius), r.real(-.275)))
        endpoint_b = center_point(wheel_center_control, dy=r.call(
            'multiply<real,real>', 'real', source_real(radius), r.real(.275)))
        wheel_name = 'RC layout deployed ' + label.lower() + ' wheel'
        gear_body(wheel_name, r.call('cylinder<point,point,real>', 'cylinder',
                                   endpoint_a, endpoint_b, source_real(radius)),
                  [.20, .23, .25, 1.])
        strut_name = 'RC layout deployed ' + label.lower() + ' strut'
        gear_body(strut_name, r.call('cylinder<point,point,real>', 'cylinder',
                                   center_point(centers[allocation_label]),
                                   center_point(wheel_center_control),
                                   source_real(strut_radius)), [.70, .76, .80, 1.])
        wheel_a = wheel_center + [0, -wheel_width / 2, 0]
        wheel_b = wheel_center + [0, wheel_width / 2, 0]
        gear_metadata.extend([
            dict(body_name=wheel_name, role='Wheel location illustration',
                 center_control=control_name,
                 center_m_nominal=(wheel_center * rc_unit).tolist(),
                 radius_m_nominal=wheel_radius * rc_unit,
                 axial_width_m_nominal=wheel_width * rc_unit,
                 bbox_m_nominal=cylinder_bbox(wheel_a, wheel_b, wheel_radius),
                 concept_basis=('Placeholder wheel radius is ' + ('22%' if kind == 'Nose' else '30%') +
                     ' of the local fitted cowl depth. Width is 55% of radius. '
                     'Main-wheel spanwise centers use local fuselage half-width; '
                     'the nose wheel uses centerline. Ground height is 2.05 times '
                     'main-station cowl depth below source zero. No tire or wheel is selected.')),
            dict(body_name=strut_name, role='Strut location illustration',
                 attachment_m_nominal=(upper * rc_unit).tolist(),
                 wheel_center_m_nominal=(wheel_center * rc_unit).tolist(),
                 radius_m_nominal=strut_radius_source * rc_unit,
                 bbox_m_nominal=cylinder_bbox(upper, wheel_center, strut_radius_source),
                 concept_basis='Placeholder cylinder joins the stowed-bay center to the '
                     'illustrated wheel center. Radius is 3% of main-station cowl depth. '
                     'No mounting, shock travel, retraction motion, steering, load, or '
                     'ground-stability design is provided.')])

    metadata = dict(
        schema='rc_concept_internal_arrangement_v1', nominal_span_m=NOMINAL_SPAN_M,
        coordinate_system='X nose-to-tail; Y span; Z up; origin follows source reconstruction',
        units='metres at nominal 16 ft span; model bodies follow RC wingspan scale',
        wing_longitudinal_offset_rc_m_nominal=wing_offset_rc_m,
        wing_longitudinal_offset_source_default=wing_offset_rc_m / (NOMINAL_SPAN_M / SOURCE_SPAN),
        hstab_span_multiplier_default=tail_span_multiplier,
        placement_basis='Photo-guided RC wing placement and HStab span choices; not production Fury dimensions',
        scope='Non-combat RC packaging sketch with native editable allocation envelopes',
        verified_installation=False, hardware_selected=False, mass_model=False,
        engine_occupies_conceptual_duct=True,
        exterior_open_duct_check_excludes_internal_layout=True,
        limitations=[
            'All hardware allocations are placeholders. No specific engine, servo, payload, battery, or landing gear is selected.',
            'Envelope dimensions and bounding boxes describe this layout only. They are not hardware clearances or manufacturing dimensions.',
            'Landing gear bodies are stowed bay allocations. Doors, support structure, and retraction kinematics are absent.',
            'The engine envelope intentionally occupies part of the conceptual passage. Exterior open-duct checks do not describe an installed propulsion system.',
            'No internal flow, thermal, structure, mass, balance, access, wiring, or flight-readiness validation is included.',
            'Center and size controls are referenced to the nominal 16 ft span. Wing actuator X also follows the absolute RC wing offset; HStab actuator center Y follows its span multiplier. Allocation dimensions are not changed by these attachment transforms.'
        ],
        component_count=len(components), named_variables_added=len(r.body)-variable_count_before,
        aggregate_name=aggregate_name, components=allocations,
        deployed_gear_illustration=dict(
            component_count=len(gear_components), excluded_from_internal_aggregate=True,
            excluded_from_exterior=True, ground_height_m_nominal=ground_source * rc_unit,
            status='Optional native geometric illustration, not an installed gear design',
            components=gear_metadata))
    return dict(components=components, aggregate=aggregate, aggregate_name=aggregate_name,
                colors={name: value['color'] for name, value in components.items()},
                controls=controls, gear_components=gear_components,
                gear_colors={name: value['color'] for name, value in gear_components.items()},
                gear_controls=gear_controls, metadata=metadata)
