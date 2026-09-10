"""Parameter table for the inline-six engine.

Every number the notebook uses lives here, once, with its unit. Two
consumers read it:

  demos/i6/scripts/make_engine_recipe.py   writes the literals as an nTop recipe, in
                                SI with explicit units, because the
                                Notebook API cannot author a dimensioned
                                literal (it speaks the display unit, and
                                this notebook displays inches).
  demos/i6/scripts/engine.py         builds the geometry, referencing every
                                literal by name and deriving all placement
                                arithmetic with live math blocks.

Lengths are millimetres, angles degrees. `expected()` evaluates the same
kinematics in plain Python so the notebook can be checked against a
number that was not produced by the notebook.
"""

import math

# --- lengths, mm -----------------------------------------------------------
# name: (value, description)
LENGTHS = {
    # core layout
    "Bore": (86.0, "Cylinder bore diameter"),
    "Stroke": (86.0, "Piston stroke; crank radius is half of this"),
    "Rod Length": (145.0, "Connecting rod centre to centre"),
    "Bore Pitch": (91.0, "Cylinder centre spacing along the crank axis"),
    "Compression Height": (30.0, "Wrist pin centre to piston crown"),
    # piston
    "Piston Length": (62.0, "Crown to skirt bottom"),
    "Piston Clearance": (0.1, "Radial clearance between piston and bore"),
    "Crown Thickness": (8.0, "Solid crown above the hollow interior"),
    "Piston Wall": (5.0, "Skirt wall thickness"),
    "Dish Depth": (3.0, "Depth of the spherical crown dish"),
    "Dish Sphere Radius": (120.0, "Radius of the sphere that cuts the dish"),
    "Top Land": (5.0, "Crown to top of first ring groove"),
    "Ring Land": (4.0, "Land between ring grooves"),
    "Compression Ring Width": (1.2, "Axial width of the two compression ring grooves"),
    "Oil Ring Width": (2.5, "Axial width of the oil control ring groove"),
    "Ring Groove Depth": (3.5, "Radial depth of every ring groove"),
    "Valve Relief Depth": (1.5, "Depth of the four valve pockets in the crown"),
    "Valve Relief Margin": (1.5, "Radial clearance of a valve pocket around its valve"),
    "Skirt Relief Width": (9.0, "Radial depth of the slipper skirt cutouts at the pin ends"),
    "Skirt Relief Top": (17.0, "Distance below the pin axis where the skirt cutouts start"),
    "Pin Diameter": (22.0, "Wrist pin diameter"),
    "Pin Length": (66.0, "Wrist pin length"),
    "Pin Boss Radius": (17.0, "Radius of the pin bosses inside the piston"),
    # crankshaft
    "Main Journal Diameter": (60.0, ""),
    "Main Journal Width": (24.0, ""),
    "Rod Journal Diameter": (50.0, ""),
    "Rod Journal Width": (26.0, "Axial width of a crank pin, clears the rod big end"),
    "Bearing Shell Thickness": (2.0, "Main bearing bore = journal radius + this"),
    "Web Arm Radius": (36.0, "Web radius around the main axis"),
    "Pin Eye Radius": (32.0, "Web radius around the crank pin"),
    "Counterweight Radius": (62.0, "Counterweight outer radius from the crank axis"),
    "Counterweight Half Width": (46.0, "Counterweight half width across the engine"),
    "Counterweight Top": (12.0, "Counterweight starts this far below the crank axis"),
    "Crank Nose Diameter": (38.0, ""),
    "Crank Nose Length": (70.0, "Nose length beyond the front main journal"),
    "Pulley Diameter": (150.0, ""),
    "Pulley Width": (28.0, ""),
    "Pulley Groove Radius": (2.5, "Tube radius of the three belt grooves"),
    "Pulley Groove Pitch": (8.0, "Axial spacing of the belt grooves"),
    "Pulley Offset": (12.0, "Gap between block front face and pulley"),
    "Rear Flange Diameter": (110.0, ""),
    "Rear Flange Thickness": (16.0, ""),
    "Flywheel Diameter": (280.0, ""),
    "Flywheel Thickness": (28.0, ""),
    "Ring Gear Tooth Height": (8.0, "Radial height of a starter ring gear tooth"),
    "Ring Gear Tooth Width": (6.0, "Tangential width of a ring gear tooth"),
    "Ring Gear Width": (24.0, "Axial width of the ring gear"),
    "Flywheel Bolt Circle Radius": (40.0, ""),
    "Flywheel Bolt Head Diameter": (16.0, ""),
    "Flywheel Bolt Head Height": (8.0, ""),
    # connecting rod
    "Rod Big End Radius": (34.0, ""),
    "Rod Big End Width": (24.0, "Along the pin axis"),
    "Rod Small End Radius": (17.0, ""),
    "Rod Small End Width": (22.0, ""),
    "Rod Bearing Clearance": (0.5, "Rod bore radius minus journal radius, shells included"),
    "Rod Shank Width": (20.0, "Shank size along the pin axis"),
    "Rod Shank Thickness": (16.0, "Shank size in the swing plane"),
    "Rod Web Thickness": (6.0, "I-beam web, along the pin axis"),
    "Rod Flange Thickness": (3.0, "I-beam flange, in the swing plane"),
    "Rod Bolt Diameter": (9.0, ""),
    "Rod Bolt Spacing": (64.0, "Centre to centre across the big end"),
    "Rod Bolt Head Diameter": (14.0, ""),
    "Rod Bolt Head Height": (7.0, ""),
    "Rod Cap Boss Half Width": (38.0, ""),
    "Rod Cap Boss Bottom": (22.0, "Boss extends this far below the big end centre"),
    "Rod Cap Boss Top": (10.0, "Boss extends this far above the big end centre"),
    # block
    "Block Width": (150.0, "Upper block, around the bores and jacket"),
    "Crankcase Width": (190.0, "Lower block, bedplate and pan; clears rod swing and counterweights"),
    "Head Bolt Boss Diameter": (22.0, "Solid boss around each head bolt through the water jacket"),
    "Block End Wall": (30.0, "Material beyond the outer cylinder half pitch"),
    "Block Side Wall": (8.0, "Crankcase side wall"),
    "Bore Overrun": (5.0, "Bore extends this far below the skirt at BDC"),
    "Bore Wall": (5.0, "Liner wall between bore and water jacket"),
    "Jacket Width": (10.0, "Radial width of the water jacket"),
    "Jacket Top Offset": (12.0, "Jacket starts this far below the deck"),
    "Jacket Depth": (120.0, ""),
    "Bulkhead Thickness": (22.0, "Main bearing bulkheads"),
    "Crankcase Roof Offset": (12.0, "Crankcase cavity ends this far above the bore bottom"),
    "Bedplate Depth": (55.0, ""),
    "Oil Pan Depth": (70.0, ""),
    "Oil Pan Wall": (4.0, ""),
    "Head Bolt Diameter": (12.0, ""),
    "Head Bolt Offset": (63.0, "Head bolt row offset from the bore axis"),
    "Head Bolt Depth": (110.0, "Below the deck"),
    # head
    "Head Width": (175.0, ""),
    "Head Height": (150.0, ""),
    "Chamber Diameter": (80.0, ""),
    "Chamber Depth": (6.0, "Combustion chamber depth above the deck"),
    "Intake Valve Diameter": (33.0, ""),
    "Exhaust Valve Diameter": (28.0, ""),
    "Valve Stem Diameter": (6.0, ""),
    "Valve Length": (95.0, "Seat plane to stem tip"),
    "Valve Head Thickness": (4.0, ""),
    "Valve Head Margin": (3.0, "Head face radius is smaller by this"),
    "Valve Fillet Height": (12.0, "Head to stem transition cone"),
    "Valve Spacing": (38.0, "Between the two valves of a pair, along the crank axis"),
    "Valve Offset": (17.0, "Valve axis offset from the bore axis at the seat"),
    "Keeper Groove Radius": (0.8, ""),
    "Keeper Groove Offset": (8.0, "Below the stem tip"),
    "Retainer Radius": (12.5, ""),
    "Retainer Thickness": (5.0, ""),
    "Retainer Offset": (12.0, "Retainer bottom below the stem tip"),
    "Bucket Diameter": (33.0, ""),
    "Bucket Height": (22.0, ""),
    "Bucket Wall": (3.0, ""),
    "Bucket Floor": (6.0, "Bucket crown thickness above the stem tip"),
    "Spring Mean Radius": (10.0, "Coil centreline radius of the valve spring"),
    "Spring Wire Diameter": (3.2, "Spring wire diameter (thicken_implicit takes the full thickness)"),
    "Spring Seat Height": (42.0, "Spring seat above the valve seat plane, along the valve axis"),
    "Throat Length": (45.0, "Valve throat length along the valve axis"),
    "Guide Bore Diameter": (6.6, ""),
    "Guide Start": (30.0, "Guide bore starts this far above the seat"),
    "Guide End Offset": (15.0, "Guide bore ends this far below the stem tip"),
    "Bucket Bore Diameter": (34.0, ""),
    "Bucket Bore Start Offset": (12.0, "Bucket bore starts this far below the stem tip"),
    "Bucket Bore Length": (55.0, ""),
    "Runner Diameter": (40.0, "Siamesed port runner"),
    "Runner Start": (40.0, "Runner starts this far up the valve axis"),
    "Runner Rise": (35.0, "Runner exit is this much higher than its start"),
    "Spark Plug Diameter": (14.0, ""),
    "Spark Plug Depth": (40.0, ""),
    "Plug Well Diameter": (24.0, ""),
    # camshafts
    "Cam Base Radius": (16.0, ""),
    "Cam Nose Radius": (5.0, ""),
    "Cam Lift": (9.5, "Maximum valve lift"),
    "Cam Lobe Width": (14.0, ""),
    "Cam Journal Diameter": (30.0, ""),
    "Cam Journal Width": (18.0, ""),
    "Cam Shaft Diameter": (26.0, ""),
    "Cam Bearing Clearance": (0.2, ""),
    "Cam Sprocket Diameter": (100.0, ""),
    "Cam Sprocket Width": (10.0, ""),
    "Cam Sprocket Tooth Height": (6.0, ""),
    "Cam Sprocket Tooth Width": (5.0, ""),
    "Cam Sprocket Offset": (12.0, "Gap between head front face and sprocket"),
    "Cam Pocket Depth": (30.0, "Cam pocket floor below the cam axis"),
    "Cam Tower Thickness": (20.0, ""),
    "Cam Pocket Margin": (28.0, "Pocket extends this far outboard of the cam axis"),
    # helpers
    "Zero Length": (0.0, "A zero with length units, for vector components"),
    "One Millimetre": (1.0, "Divide by this to read a length as a plain number"),
    "Overrun": (1.0, "Small extension so cuts break cleanly through faces"),
    "Big": (1000.0, "Half size of the cutaway box"),
    "Cutaway Y": (-1000.0, "Static parts are kept where y > this; -1000 shows everything, 0 halves the engine"),
    "Mesh Tolerance Fine": (0.6, "STL surface tolerance for the small parts"),
    "Mesh Tolerance Coarse": (1.5, "STL surface tolerance for block, head, bedplate, pan"),
    "Mesh Tolerance Medium": (1.0, "STL surface tolerance for the valves; at 0.6 the mesher dropped the valve core"),
}

VOLUMES = {
    "One Cubic Centimetre": (1.0, "Divide by this to read a volume in cc"),
}

# --- angles, deg -----------------------------------------------------------
FIRING_ORDER = [1, 5, 3, 6, 2, 4]
_FIRE_AT = {cyl: 120.0 * k for k, cyl in enumerate(FIRING_ORDER)}
PHASES = {cyl: (720.0 - _FIRE_AT[cyl]) % 720.0 for cyl in range(1, 7)}

ANGLES = {
    "Crank Angle": (0.0, "THE motion parameter. 0 = cylinder 1 at firing TDC"),
    "Valve Tilt": (15.0, "Valve axis lean from vertical, about the crank axis"),
    "Intake Centerline": (235.0, "Cam degrees after firing TDC at peak intake lift (470 crank)"),
    "Exhaust Centerline": (125.0, "Cam degrees after firing TDC at peak exhaust lift (250 crank)"),
    "Half Turn": (180.0, ""),
    "Ring Gear Tooth Pitch": (360.0 / 120, ""),
    "Sprocket Tooth Pitch": (360.0 / 40, ""),
    "Flywheel Bolt Pitch": (360.0 / 8, ""),
    "Spring Turns Angle": (6 * 360.0, "Six active coils"),
}
for _c in range(1, 7):
    ANGLES["Phase Cyl %d" % _c] = (PHASES[_c], "Crank phase of cylinder %d relative to cylinder 1" % _c)

SPRING_POINTS = 151  # samples along the helix polyline, 25 per turn

INTEGERS = {
    "Ring Gear Teeth": (120, ""),
    "Sprocket Teeth": (40, ""),
    "Flywheel Bolts": (8, ""),
}

DIMENSIONLESS = {
    "Cam Ratio": (0.5, "Camshaft turns at half crank speed"),
    "Spring Turns": (6.0, "Active coils per valve spring"),
    "Displacement Factor": (6.0 * math.pi / 4.0, "cylinders x pi/4"),
    "Main Index": (-3.0, "Rearmost main bearing is at this many pitches"),
}
for _c in range(1, 7):
    DIMENSIONLESS["Cyl Index %d" % _c] = (3.5 - _c, "Cylinder %d centre in bore pitches; positive is the front" % _c)

# Where per-part STL exports go. Part name -> file name.
# Part -> (file name, tolerance literal). Exports are added after the build
# (engine.exports) because meshing the big parts dominates the import time.
EXPORT_PARTS = {
    "Piston": ("piston.stl", "Mesh Tolerance Fine"),
    "Connecting Rod": ("connecting_rod.stl", "Mesh Tolerance Fine"),
    "Crankshaft at TDC": ("crankshaft.stl", "Mesh Tolerance Fine"),
    "Intake Valve": ("intake_valve.stl", "Mesh Tolerance Medium"),
    "Exhaust Valve": ("exhaust_valve.stl", "Mesh Tolerance Medium"),
    "Cam Lobe": ("cam_lobe.stl", "Mesh Tolerance Fine"),
    "Valve Spring": ("valve_spring.stl", "Mesh Tolerance Fine"),
    "Intake Camshaft static": ("intake_camshaft.stl", "Mesh Tolerance Fine"),
    "Exhaust Camshaft static": ("exhaust_camshaft.stl", "Mesh Tolerance Fine"),
    "Cylinder Block solid": ("cylinder_block.stl", "Mesh Tolerance Coarse"),
    "Cylinder Head solid": ("cylinder_head.stl", "Mesh Tolerance Coarse"),
    "Bedplate solid": ("bedplate.stl", "Mesh Tolerance Coarse"),
    "Oil Pan solid": ("oil_pan.stl", "Mesh Tolerance Coarse"),
}


def export_file(part):
    return EXPORT_PARTS[part][0]


def export_path_var(part):
    return "Export Path " + part


# --- plain Python model of the same kinematics -----------------------------

def L(name):
    return LENGTHS[name][0]


def A(name):
    return ANGLES[name][0]


def expected(theta_deg):
    """Kinematics for every cylinder at crank angle theta, in mm and deg."""
    r = L("Stroke") / 2.0
    rod = L("Rod Length")
    z_deck = r + rod + L("Compression Height")
    z_seat = z_deck + L("Chamber Depth")
    R, rn, lift = L("Cam Base Radius"), L("Cam Nose Radius"), L("Cam Lift")
    d = R + lift - rn
    out = {
        "deck_height": z_deck,
        "displacement_cc": 6 * math.pi / 4 * L("Bore") ** 2 * L("Stroke") / 1000.0,
        "cylinders": {},
    }
    for cyl in range(1, 7):
        th = math.radians(theta_deg + PHASES[cyl])
        q = r * math.sin(th)
        z_pin = r * math.cos(th)
        z_p = z_pin + math.sqrt(rod ** 2 - q ** 2)
        beta = math.degrees(math.asin(q / rod))
        psi = math.degrees(th) / 2.0
        lifts = {}
        for kind, cl in (("intake", A("Intake Centerline")), ("exhaust", A("Exhaust Centerline"))):
            u = math.radians(psi - cl)
            lifts[kind] = max(0.0, d * math.cos(u) + rn - R)
        out["cylinders"][cyl] = {
            "x": (3.5 - cyl) * L("Bore Pitch"),
            "y_pin": -q,
            "z_pin": z_pin,
            "z_pin_piston": z_p,
            "crown_z": z_p + L("Compression Height"),
            "rod_angle_deg": -beta,
            "lift_intake": lifts["intake"],
            "lift_exhaust": lifts["exhaust"],
        }
    out["z_seat"] = z_seat
    return out
