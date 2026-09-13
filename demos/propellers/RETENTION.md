# Spinner retention design

The spinner uses a central M3 x 12 button-head screw. The screw clamps an
internal boss against a custom extension nut. The extension nut replaces the
previous M5 prop nut and still clamps the propeller through the existing washer.

## Assembly sequence

1. Install the propeller and washer on the existing M5 adapter shaft.
2. Tighten the custom extension nut against the washer with an 8 mm wrench.
3. Place the spinner's locating socket over the nut's 6 mm spigot.
4. Seat the internal spinner boss on the nut shoulder.
5. Install the central M3 x 12 screw with a 2 mm hex key.

The spinner lifts off after removal of the M3 screw. The propeller nut remains
in place. The spinner base has a nominal 0.255 mm gap to the flat hub face.

## Nominal dimensions

| Feature | Dimension |
|---|---:|
| Custom nut rear thread | M5 x 0.8 |
| Custom nut front thread | M3 x 0.5 |
| Nut wrench flats | 8 mm |
| Nut base / shoulder z | 5.445 / 19.445 mm |
| Locating spigot diameter / top z | 6.00 / 21.445 mm |
| Spinner locating socket diameter | 6.10 mm |
| Socket end z | 21.595 mm |
| Spinner boss outside diameter | 8.8 mm |
| M3 clearance through boss | 3.4 mm |
| Screw underside z | 27.0 mm |
| Screw end z | 15.0 mm |
| Nominal M3 engagement | 6.445 mm |
| Nominal M5 engagement | 7.0 mm |
| Screw head / counterbore diameter | 5.7 / 6.2 mm |

The nut has a connected stepped bore. Its M5 recess ends at z = 14.445 mm.
The M3 bore opens into that recess. The motor shaft and retaining screw have
a nominal 2.555 mm axial gap between their ends.

## Sources and limits

The central screw mechanism has a documented precedent in Horizon Hobby's
PKZ5180 installation manual. The selected M3 x 12 ISO 7380-1 screw dimensions
come from Accu. Links are retained in `evidence/sources.json` and the report.
The custom adapter and spinner boss dimensions are design choices.

Thread flanks are not modeled. The adapter STL is a reference for machining,
not a ready-to-print threaded nut. Machine and tap M5 x 0.8 from the rear and
M3 x 0.5 from the front. Specify thread tolerances, lead, runout, and chamfers
in a manufacturing drawing. Nominal engagement does not include those allowances.

The design assumes a machined steel adapter. Material grades, screw torque,
removable locking treatment, balance, and rotational qualification need engineering
release. The geometric checks do not establish a safe operating speed.
