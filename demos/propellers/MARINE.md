# Marine loop screw and separate aft cap

This is a recorded native geometry study for a nominal 3.048 m screw. It is not a released vessel or gearbox interface.

Three identical loops use one uninterrupted native Sweep along Two Rails, repeated at 120 degrees. Smooth cubic guides control chord and section rotation. The closed spline profile is a NACA 66-derived CST section with 14% thickness and 2% camber. The outer return has no joined sweep ends or radial clipping.

The fuller revision uses a 914.4 mm barrel diameter and a 1463.04 mm barrel length. Both complete root sections lie inside the barrel. These proportions are authored choices guided by the civilian Sharrow product photograph. They do not establish strength, efficiency, or acoustic performance.

The separate aft cover has:

- Eight M24 x 3 x 70 socket-head screws on a 762 mm bolt circle.
- A 24 mm flange, 26 mm clearance holes, and authored 50 x 26 x 5 mm washers.
- A 12 mm locating lip with 1 mm radial clearance.
- 41 mm nominal screw engagement in 50 mm deep sockets.
- A hollow dome with a nominal 20 mm wall.

The screws retain the cover only. The internally splined drive cartridge and positive axial propeller retainer remain pending a selected shaft drawing. Thread flanks, preload, locking, sealing, material pairing, and safe shaft speed are not qualified.

The recorded mesh uses native Adaptive Tetrahedral Meshing with Remesh enabled, followed by Sharpen Mesh. Any detached-fragment removal requires a measured distance bound and unchanged retained vertices. See the adjacent evidence files. Host spline derivative checks do not prove global curvature continuity of the complete implicit union.

Prepare the complete saved graph with:

```powershell
uv run --locked python demos/propellers/scripts/replay.py --case marine_prop
```

The recipe exports the screw, cap, and one screw and washer reference. Native evaluation needs the licensed build. The public package contains recorded nTop views and dimensions; large native caches and STL files stay in local output.

Sources:

- [User-supplied article with the civilian Sharrow photo](https://boattest.com/article/us-navy-modernizes-torpedoes-sharrow-prop-design).
- [Sharrow Marine product photograph](https://www.sharrowmarine.com/).
- [ITTC Propulsor Committee, DTMB 4119 dimensions and section ordinates](https://ittc.info/media/2388/report-of-the-propulsor-committee.pdf).
- [ISO 4762 socket-head dimensions](https://torqbolt.com/iso-4762-socket-head-cap-screws-dimensions-standards-specifications).
- [SOLAS splined-hub assembly reference](https://www.solas.com/proimages/download/RBX_203.pdf).

The public package excludes the reference photographs. Their proportions are not manufacturing dimensions for this study.
