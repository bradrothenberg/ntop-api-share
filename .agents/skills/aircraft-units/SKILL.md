---
name: aircraft-units
description: "Present airplane numbers in US customary units. Use whenever sizing, modeling, rendering, tabulating, captioning or reporting on an aircraft: span and other large lengths in feet, small dimensions in inches, areas in square feet."
---

# Aircraft units

Present every airplane in US customary units. The rule applies to tables, captions,
labels on renders, film cards, chart axes, notebook comments and reports.
It applies to every aircraft project, new or revised.

## The rule

- **Span and other large lengths: feet (ft).** Span, overall length, height, chord,
  wheelbase, wheel track, turn radius.
- **Small dimensions: inches (in).** Panel gaps, skin thickness, lip and edge radii,
  duct and tyre diameters, clearances, door and bay openings.
- **Areas: square feet (ft2).** Reference area, wetted area, control-surface area,
  planform area.

Use feet when the value is about 2 ft or more, and inches below that.
Keep one unit within one column or one series of labels.

## Related quantities

The rule above names length and area. Use the same system for the rest unless the
user says otherwise:

| Quantity | Unit |
|---|---|
| Weight, mass, fuel | lb |
| Thrust, force | lbf |
| Wing loading | lb/ft2 |
| Speed | kt, with Mach number where it defines the condition |
| Altitude | ft |
| Range, radius of action | nmi |
| Volume | ft3, or US gal for fuel |
| Angles, load factor, coefficients | deg, g, dimensionless (unchanged) |

## Convert at presentation, keep the source

A notebook, a solver or a simulation keeps the units it was built in, often
millimetres or SI. Do not rescale a working model to change its display units.
Convert the stored full-precision value where the number is shown.

Exact factors:

| From | To | Divide by |
|---|---|---|
| m | ft | 0.3048 |
| mm | in | 25.4 |
| m2 | ft2 | 0.09290304 |
| kg | lb | 0.45359237 |
| N | lbf | 4.4482216152605 |
| m/s | kt | 0.514444 (1852/3600) |
| m | nmi | 1852 |

- Convert first, then round. Never convert a rounded value.
- Round span and lengths to 0.1 ft, areas to the nearest ft2, small dimensions to 0.1 in
  (0.01 in for gaps and thicknesses).
- A condition defined by a round metric number keeps its definition in the source record.
  Show the converted value: 10,000 m is 32,800 ft.
- Dimensionless results (CL, CD, Cm, L/D, aspect ratio) do not change. The reference area
  and chord printed beside them follow the rule.
- Add the SI value in parentheses only when the reader asks for it or a cited source is in SI.

Example: span 15.2 m is 49.9 ft; reference area 95.0 m2 is 1,023 ft2; wheelbase 5.38 m is
17.7 ft; a 10 mm panel gap is 0.39 in; a 0.27 m wheel spacing is 10.6 in.

## Check before delivery

- Search the delivered text and labels for metric unit strings: ` m`, `m2`, `mm`, `kg`,
  `kN`, `km`, `m/s`. Each remaining one needs a reason.
- Recompute one length, one area and one small dimension by hand from the source values.
- Check chart axes, legends, on-frame overlays and file captions, not only the tables.
- State in the record which values are stored in SI and where they are converted.
