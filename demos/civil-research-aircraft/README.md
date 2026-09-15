# Civil research aircraft: Revision G and design studies

**Built with Astra.**

An editable civilian research-aircraft structure with Revision G as the primary delivery. The bundle contains 78 native notebooks and ten engineering reports. It includes the complete saved assemblies, separate station parts, hat longerons, forked spars, cover splices, and nominal pin hardware.

![Revision G native structure](cover.png)

## Start here

1. Download or clone the complete repository. Read [the report catalogue](reports/index.html) and [the Revision G review](reports/revision-g-lug-attachments.html).
2. Prepare a separate Revision G working copy from the repository root:

```powershell
uv run --locked python demos/civil-research-aircraft/scripts/prepare_models.py
```

3. Open `output/models/civil-research-aircraft-rev-g.ntop` under this demo in licensed nTop **6.1.0-rc build 42926**.
4. Inspect or edit the relevant structural section. Rebuild and verify both mating parts after a joint change.
5. Save a separate assembly revision and verify its embedded part definitions.

The preparation script copies the four airfoil reference files into `output/inputs/` and resolves the notebooks' portable paths to those working files. It does not start nTop. The published models and inputs remain unchanged.

Prepare Revision H or the complete collection with:

```powershell
uv run --locked python demos/civil-research-aircraft/scripts/prepare_models.py --model rev-h-aircraft-h.ntop
uv run --locked python demos/civil-research-aircraft/scripts/prepare_models.py --all
```

The native files preserve their saved geometry, view states, and embedded definitions. Opening the prepared copies in nTop has not been re-tested for this publication. Compatibility with a public nTop release is unverified.

## Revision G

The assembly uses upper and lower integral bulkhead eyes, forked spar roots, eight nominal pins, and a separate cover-splice load path. The 14 changed structural part notebooks and the pin family are included. Assembly, forward-joint, aft-joint, and frame-only presentations preserve their saved visibility states.

The recorded source checks report 1,997 geometry probes passed, 174 embedded assembly definitions, and 128 GUI variables with `e_OK` states. These establish the stated geometry and graph checks. They do not establish structural capacity. The local fork stress screens fail, and the complete Revision G aircraft analysis remains open. No new Revision G STEP is claimed.

## Revision H follow-up

Revision H is a separate later study. It broadens the lower side sections of both primary bulkheads while retaining the Revision G pin centers, bores, spar forks, and longeron routes. The complete assembly, both primaries, and a lower-joint presentation are included.

The recorded final check reports 1,396 changed-primary probes, 208 fork-clearance probes, 720 source-envelope probes, and 128 assembly variables with `e_OK` states. The earlier fork stress screen remains unresolved. See the [lower-bulkhead review](reports/revision-h-lower-bulkheads.html) and [current design overview](reports/current-design-review.html).

## Inputs and outputs

| Item | Editable data | Result and limit |
|---|---|---|
| Revision G assembly | Embedded part definitions, placements, and visibility groups | Complete saved structural assembly with the aircraft reference |
| Revision G primaries and spars | Native variables within each complete part expression | Finished bulkhead eyes and matching forked roots; joint interfaces are nominal |
| Pin family | Pin diameter input | Nominal pin body; changing it alone does not resize mating bores |
| Earlier D/E/F assemblies | Frame thickness, primary thickness, and residual-web controls | Earlier geometry revisions with their own recorded checks |
| Section studies | I, flat, and hat section dimensions | Native section coupons for the earlier buckling comparison |

Parts already use aircraft world coordinates. Do not apply a second placement. Imported custom blocks are embedded snapshots. Saving a standalone part does not update its assembly. A changed interface requires coordinated edits and an explicit assembly refresh.

## Reports

- [Revision G: local lug attachments](reports/revision-g-lug-attachments.html): Primary review. Integral bulkhead eyes, forked spar roots, nominal pins, native checks, and failed local fork stress screens.
- [Revision F: pad-to-flange ribs](reports/revision-f-design.html): Earlier installed structure with pad support ties, native geometry checks, and independent STEP mass results.
- [Revision E: hat longerons](reports/revision-e-design.html): Earlier hat longerons, conformal station parts, and revised primary passages.
- [Revision D: modular fitted structure](reports/revision-d-design.html): Earlier modular assembly, pocket corrections, part input contracts, and fit checks.
- [Edge-aligned comparison: sizing audit](reports/edge-aligned-sizing-audit.html): Measured spar directions, corrected coupling-mass accounting, and unresolved sizing assumptions.
- [Wing-root trade](reports/wing-root-trade.html): Recorded layout, station, gauge, mass, and sensitivity comparisons. Failed primary stress screens remain visible.
- [Cranked-wing review](reports/cranked-wing-review.html): Earlier spar route comparisons and their local load-path implications.
- [Buckling and thin sections](reports/buckling-review.html): Earlier assumed-load study with editable I, flat, and hat section coupons.

- [Revision H: lower bulkhead sections](reports/revision-h-lower-bulkheads.html): Added pocketed lower sides, preserved interfaces, recorded native checks, and remaining analysis limits.
- [Current design overview](reports/current-design-review.html): Current source overview, retained separately from the archived Revision F review.

## Native model catalogue

The filenames identify each revision. Candidate C and the edge-aligned model are separate comparison assemblies. Earlier D/E/F assemblies remain separate from Revision G.

### Revision H follow-up

- [Revision H complete assembly](models/rev-h-aircraft-h.ntop)
- [Revision H forward primary](models/rev-h-c-fwd.ntop)
- [Revision H aft primary](models/rev-h-c-aft.ntop)
- [Revision H lower joint](models/rev-h-front-lower-joint.ntop)

### Revision G assembly

- [civil-research-aircraft-rev-g.ntop](models/civil-research-aircraft-rev-g.ntop)

### Revision G parts and presentations

- [rev-g-aft-lug-joint.ntop](models/rev-g-aft-lug-joint.ntop)
- [rev-g-c-aft.ntop](models/rev-g-c-aft.ntop)
- [rev-g-c-fwd.ntop](models/rev-g-c-fwd.ntop)
- [rev-g-forward-lug-joint.ntop](models/rev-g-forward-lug-joint.ntop)
- [rev-g-frames-g.ntop](models/rev-g-frames-g.ntop)
- [rev-g-p-front-spar.ntop](models/rev-g-p-front-spar.ntop)
- [rev-g-p-lower-inner-splice.ntop](models/rev-g-p-lower-inner-splice.ntop)
- [rev-g-p-lower-outer-splice.ntop](models/rev-g-p-lower-outer-splice.ntop)
- [rev-g-p-rear-spar.ntop](models/rev-g-p-rear-spar.ntop)
- [rev-g-p-upper-inner-splice.ntop](models/rev-g-p-upper-inner-splice.ntop)
- [rev-g-p-upper-outer-splice.ntop](models/rev-g-p-upper-outer-splice.ntop)
- [rev-g-s-front-spar.ntop](models/rev-g-s-front-spar.ntop)
- [rev-g-s-lower-inner-splice.ntop](models/rev-g-s-lower-inner-splice.ntop)
- [rev-g-s-lower-outer-splice.ntop](models/rev-g-s-lower-outer-splice.ntop)
- [rev-g-s-rear-spar.ntop](models/rev-g-s-rear-spar.ntop)
- [rev-g-s-upper-inner-splice.ntop](models/rev-g-s-upper-inner-splice.ntop)
- [rev-g-s-upper-outer-splice.ntop](models/rev-g-s-upper-outer-splice.ntop)
- [rev-g-root-pin.ntop](models/rev-g-root-pin.ntop)

### Revision F

- [rev-f-aircraft-structure.ntop](models/rev-f-aircraft-structure.ntop)
- [rev-f-forward-primary-bulkhead.ntop](models/rev-f-forward-primary-bulkhead.ntop)
- [rev-f-aft-primary-bulkhead.ntop](models/rev-f-aft-primary-bulkhead.ntop)
- [rev-f-f01-frame.ntop](models/rev-f-f01-frame.ntop)
- [rev-f-f02-frame.ntop](models/rev-f-f02-frame.ntop)
- [rev-f-f03-frame.ntop](models/rev-f-f03-frame.ntop)
- [rev-f-f04-frame.ntop](models/rev-f-f04-frame.ntop)
- [rev-f-f05-frame.ntop](models/rev-f-f05-frame.ntop)
- [rev-f-f07-frame.ntop](models/rev-f-f07-frame.ntop)
- [rev-f-f09-frame.ntop](models/rev-f-f09-frame.ntop)
- [rev-f-f10-frame.ntop](models/rev-f-f10-frame.ntop)
- [rev-f-f11-frame.ntop](models/rev-f-f11-frame.ntop)
- [rev-f-f12-frame.ntop](models/rev-f-f12-frame.ntop)

### Revision E

- [rev-e-aircraft-structure.ntop](models/rev-e-aircraft-structure.ntop)
- [rev-e-forward-primary-bulkhead.ntop](models/rev-e-forward-primary-bulkhead.ntop)
- [rev-e-aft-primary-bulkhead.ntop](models/rev-e-aft-primary-bulkhead.ntop)
- [rev-e-f01-frame.ntop](models/rev-e-f01-frame.ntop)
- [rev-e-f02-frame.ntop](models/rev-e-f02-frame.ntop)
- [rev-e-f03-frame.ntop](models/rev-e-f03-frame.ntop)
- [rev-e-f04-frame.ntop](models/rev-e-f04-frame.ntop)
- [rev-e-f05-frame.ntop](models/rev-e-f05-frame.ntop)
- [rev-e-f07-frame.ntop](models/rev-e-f07-frame.ntop)
- [rev-e-f09-frame.ntop](models/rev-e-f09-frame.ntop)
- [rev-e-f10-frame.ntop](models/rev-e-f10-frame.ntop)
- [rev-e-f11-frame.ntop](models/rev-e-f11-frame.ntop)
- [rev-e-f12-frame.ntop](models/rev-e-f12-frame.ntop)

### Revision D

- [rev-d-aircraft-structure.ntop](models/rev-d-aircraft-structure.ntop)
- [rev-d-forward-primary-bulkhead.ntop](models/rev-d-forward-primary-bulkhead.ntop)
- [rev-d-aft-primary-bulkhead.ntop](models/rev-d-aft-primary-bulkhead.ntop)
- [rev-d-f01-frame.ntop](models/rev-d-f01-frame.ntop)
- [rev-d-f02-frame.ntop](models/rev-d-f02-frame.ntop)
- [rev-d-f03-frame.ntop](models/rev-d-f03-frame.ntop)
- [rev-d-f04-frame.ntop](models/rev-d-f04-frame.ntop)
- [rev-d-f05-frame.ntop](models/rev-d-f05-frame.ntop)
- [rev-d-f07-frame.ntop](models/rev-d-f07-frame.ntop)
- [rev-d-f09-frame.ntop](models/rev-d-f09-frame.ntop)
- [rev-d-f10-frame.ntop](models/rev-d-f10-frame.ntop)
- [rev-d-f11-frame.ntop](models/rev-d-f11-frame.ntop)
- [rev-d-f12-frame.ntop](models/rev-d-f12-frame.ntop)

### Edge-aligned comparison

- [edge-aligned-aircraft-c.ntop](models/edge-aligned-aircraft-c.ntop)
- [edge-aligned-c-fwd.ntop](models/edge-aligned-c-fwd.ntop)
- [edge-aligned-c-aft.ntop](models/edge-aligned-c-aft.ntop)

### Candidate C comparison

- [candidate-c-aircraft-c.ntop](models/candidate-c-aircraft-c.ntop)

### Hat longerons

- [hat-longerons-l01-longeron-path.ntop](models/hat-longerons-l01-longeron-path.ntop)
- [hat-longerons-l02-longeron-path.ntop](models/hat-longerons-l02-longeron-path.ntop)
- [hat-longerons-l03-longeron-path.ntop](models/hat-longerons-l03-longeron-path.ntop)
- [hat-longerons-l04-longeron-path.ntop](models/hat-longerons-l04-longeron-path.ntop)
- [hat-longerons-l05-longeron-path.ntop](models/hat-longerons-l05-longeron-path.ntop)
- [hat-longerons-l06-longeron-path.ntop](models/hat-longerons-l06-longeron-path.ntop)
- [hat-longerons-l07-longeron-path.ntop](models/hat-longerons-l07-longeron-path.ntop)
- [hat-longerons-l08-longeron-path.ntop](models/hat-longerons-l08-longeron-path.ntop)

### Buckling section studies

- [buckling-thin-sections-study.ntop](models/buckling-thin-sections-study.ntop)
- [buckling-i-section-generator.ntop](models/buckling-i-section-generator.ntop)
- [buckling-flat-section-generator.ntop](models/buckling-flat-section-generator.ntop)
- [buckling-hat-section-generator.ntop](models/buckling-hat-section-generator.ntop)

## Scope of this package

This is a native-model and report handoff. It includes recorded numerical summaries and source workflow notes. It does not include the original execution harness, rebuild scripts, STEP exports, raw meshes, solver work directories, or reference photographs and sketches. Report links to omitted scripts or STEP files lead here. The original reports identify those operations and their original revision scope.

The HTML reports use the adjacent asset folder and work offline. They retain the recorded calculations, native views, engineering limits, and failed studies. Source reference images and screenshots containing workstation paths are omitted. Native family colors are retained; report highlights use nTop blue.

## Publication checks

See [publication record](evidence/publication.json) for source and published hashes, exact native function preservation, portable airfoil paths, and report-image provenance. [manifest.json](manifest.json) binds each notebook and report to its final published hash. The final [source validation record](evidence/rev-g-final-validation.json) describes the original native run. Its hashes refer to the source files before publication changes. Other evidence files also retain their original revision and sample scope.

The [offline verification summary](evidence/offline-verification.json) records the package audit, browser checks, and regression results.

New checks are offline packaging checks. No new native execution, geometry certification, load validation, or weight optimization is claimed. Earlier structural failures remain part of the review.

## Offline verification

```powershell
uv run --locked python demos/civil-research-aircraft/scripts/check_example.py
```

This checks file hashes, native container round trips, function payloads, and report integrity. It does not run the original geometry construction or solvers.

## License and credits

MIT for Brad Rothenberg's original model and report work. See [LICENSE](LICENSE). Built with Astra.

The aircraft source retains its embedded custom-block attribution, including the bounded triangular-prism method credited to [Inigo Quilez](https://iquilezles.org/articles/distfunctions/). The NACA 64A010 and PW1211 coordinate tables retain their profile names. See the [UIUC Airfoil Coordinates Database](https://m-selig.ae.illinois.edu/ads/coord_database.html) for airfoil reference data. The package license does not replace third-party rights or attribution.
