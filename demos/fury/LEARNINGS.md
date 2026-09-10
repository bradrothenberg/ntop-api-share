# Current finite-edge handoff

The primary saved notebook is `models/Fury_RC_TE_0p5in.ntop`. Its wing, horizontal tail, and fin have 0.5 inch full trailing-edge controls. The earlier builder and records below describe a distinct appearance baseline.

The finite-edge construction uses a C2 transition over the aft chord region. Convert full physical thickness to the half-thickness contribution and guide coordinates explicitly. Keep the RC scale conversion in the dependency graph. A finite section does not guarantee a clean exported surface.

[Current mesh evidence](../../reports/Fury-RC.html) retains the raw and sharpened comparisons, inlet knife-edge findings, fragments, and volume-mesh limitations. Do not replace those findings with a claim based on smooth shading. New meshing runs require their own receipts.

# Recorded lessons

This is an edited record of prior work. Its native results apply to those recorded revisions.
Local machine paths and omitted artifact links were removed for this public handoff.
Historical tool and artifact names below describe the source work. Use README.md for the runnable commands and files in this checkout.

> Historical source snapshot. Use the local AGENTS.md and README.md for portable setup.

# Native RC model and initial aero study

## Files

- Editable exterior
- Internal arrangement
- Deployed gear illustration
- Photo comparison view
- Verification notebook
- Engineering report

## Historical appearance revision: candidate thirteen

The splitter/cowl attachment closes farther forward, ahead of the wing-root blend. A native C2 Ramp varies the wing blend from **0.978016 inch at the leading edge to 0.125 inch at the trailing edge**. Both endpoints are editable in **Root blend controls**. These values control the blend field; they are not measured fillet radii.

**Verification state:** Native Ramp, junction, root, and placement checks pass. Current captures and headless evaluation pass. The original fixed-offset corridor criterion remains unmet. The replacement 40-section native cavity check is running. The main HTML remains candidate twelve until that check passes.

The user requests a non-combat RC appearance model with native conics and implicit splines. The supplied span is 16 ft (4.8768 m). The initial aero speed is 200 mph (89.408 m/s). Primary surfaces do not depend on imported meshes. The public demo contains its own complete native construction source.

### Junction and blend controls

Exterior closure, buried attachment, slot end, and splitter aft station move forward together by **255.128515 mm at RC scale**. The inlet mouth, accepted wing placement, lifting profiles, and outlet remain fixed. This is an RC appearance choice. Gear and shadow partly hide the exact photographic junction.

| Feature | Source longitudinal coordinate |
|---|---:|
| Splitter start | -2.60 |
| Splitter aft station | -1.590267946311034 |
| Roof closure start | -1.770267946311034 |
| Roof closure end | -1.570267946311034 |
| Side-slot end | -1.560267946311034 |
| Buried cowl attachment end | -1.240267946311034 |
| Wing blend support start | -1.164267946311034 |

The 0.076-source-unit interval between the last two stations is a construction allowance, not a measured surface clearance. The source coordinates and expected closure checks are in _agent/rc_junction_revision.json. Actual evaluated closure values are in _agent/rc_native_checks.json.

**Wing root blend size** retains its previous leading-edge default. **Wing TE root blend size** sets the new 1/8-inch trailing endpoint. The **Wing root blend ramp RC** field uses the native Ramp function with C2 continuity. Its coordinate follows the live wing offset. The local root-chord interval is source x=-1.26 to +1.24. The ramp clamps outside this interval and retains the existing compact root support. Tailplane and fin blend functions are unchanged.

Native samples at chord fractions 0, 0.25, 0.5, 0.75, and 1 read 0.978016, 0.889716, 0.551508, 0.213300, and 0.125000 inch. Endpoint and effective-field residuals are below 7e-17 inch. The maximum sampled increase is zero. The verified input order, continuity, units, and controls are in _agent/rc_root_blend_construction.json.

### Preserved construction

The user calls the pointed center-gap feature the **splitter**. It joins the fuselage underside and inlet roof and exists only between them. The upper-wall feature is the **inlet lip**. Legacy field names can retain older terminology. Keep lateral passages beside the splitter. Its half-width uses the editable cubic fraction 0.15u + 0.75uÃƒâ€šÃ‚Â² + 0.10uÃƒâ€šÃ‚Â³.

The underside is one signed-span conic: A=(-w,0), B=(0,-2d), C=(w,0), rho=0.5. Longitudinal guides set width, depth, and chine height. Preserve the lower lip's swept center point. The user withdrew the straight lower-edge request. The lip and cheeks form one rounded shell. The lower cowl guide limits buried forebody overlap.

Subtract the cavity after additive root and splitter geometry. The passage continues to the existing outlet without a back disk. The entry roof now directly uses the same guarded roof as the previous zero-weight closure branch. At 200 identical diagnostic points, old and current native cavity fields differ by **0.0 m**. This sampled comparison is separate from the algebraic branch review.

The internal arrangement has 13 editable allocations: generic engine, non-combat payload, avionics, electrical battery, propulsion energy storage, five actuators, and three stowed gear bays. Three wheel and three strut bodies form a separate deployed illustration. Read _agent/rc_internal_layout.json for concept dimensions and placement. No specific hardware is selected.

The engine allocation deliberately occupies the duct. Exterior passage checks exclude internal allocations. The layout does not establish installed flow, hardware fit, thermal clearance, structure, mass, CG, retraction, or flight readiness.

### Current native evidence

The verification model has **373 variables and 4,226 nodes**, four displayed exterior bodies, zero mesh imports, and zero graph errors. Pruning removes six dense-check roots and 844 nodes. The interactive model retains **367 variables and 3,382 nodes**. Retained output graphs and literals match the verification companion.

- Recipe SHA-256: ff1e30b82d768134169b8b9d7763d3f6245623fa45727eee6f6ec8d59b3be7e0
- Interactive SHA-256: 0dbdebdb7051f48fc9d3b497caad8638dbfeb0fb51b5cc92809bd65215ee5829
- Verification SHA-256: dfbf9bbd17a9ea005016eabbc0ef60bee04ae9faf0d6832da7cd273290020e05

Fresh _agent/rc_native_checks.json results verify span, surface signs, live placement controls, Ramp values, closure fields, and internal-envelope centers. All 30 final-assembly passage probes are open. All three roots have positive added-material witnesses. The sampled outside-support field difference is zero. The saved interactive model passes nTop Automate with exit code 0 and a matching hash.

Fresh candidate-thirteen inlet evidence includes:

- Exact gap dependency fixture: requested 1.1 change ratio and exact reset pass. This is not a full-model live reset.
- Upstream gap: all 78 transverse probes pass. Conic placement and signs pass; the maximum surface residual is 1.279e-12 m.
- Splitter arrangement: all ten categories pass. Four stations use fractions 0.2, 0.4, 0.6, and 0.8 of the current open interval, before closure.
- Native-section smoke: one station passes all 12 criteria. The full check uses the same method with 40 stations.
- Original fixed-offset diagnostic: the criterion remains **not met**. Of 200 body probes, 198 are open. The two upper points lie outside the actual cavity at source x=-0.93974359 and -0.74871795. Both are outside the splitter. All 40 center, 80 lateral, and 40 lower probes are open.

Preserve the failed diagnostic in _agent/corridor_diagnostic_results.json. Do not change the cavity or hide that criterion to claim a pass. The replacement method finds actual native cavity intersections. Across 40 stations it uses 200 cross probes plus 160 surface, 160 inward, and 160 outward probes. Acceptance requires the current full native result. Finite field checks do not establish continuous clearance or airflow.

The earlier _agent/rc_unchanged_evidence.json is historical. It does not authorize the candidate-thirteen inlet geometry. Current source and fixture hashes are required. The host internal-layout screen covers 78 bounding-box pairs and gross sampled containment, not hardware or skin fit.

### Photographic and visual review

The accepted **Wing longitudinal offset** remains 154.104300 mm aft. The **HStab span multiplier** remains 0.919057. Wing and tail allocations follow those controls. Both values are RC appearance inputs.

The 1024-by-676-pixel flight photograph supplies manually picked visible nose and tail landmarks. The camera RMS residual is 5.981 pixels. The near wing-root leading edge is occluded and excluded. The earlier wing-point improvement from 15.178 to 8.111 pixels belongs to candidate twelve, not this junction change.

Candidate-twelve baseline and candidate-thirteen native captures use the identical camera. Their source, capture, image, and camera hashes are in _agent/rc_photo_comparison.json. Preserve original RGBA pixels. Fury_RC_Photo_Comparison.ntop saves the current matched-camera view.

All 17 current standard views and both photo captures are reviewed. The slot closes ahead of the wing. Both sides retain connected inlet cheeks, the smooth underside arc, and the pointed lower lip. No new detached sliver or belly protrusion is visible. A small sharp trailing-root finish, thin-edge steps, and shading bands remain. The bounded review is linked to 19 image hashes in _agent/rc_visual_review.json.

Do not claim exact or 95% photographic likeness. The photos do not establish full-surface error, tangency, manufactured-edge quality, or hardware fit.

### Retained aero study

Candidate thirteen does **not** rerun AVL or XFOIL. The current _agent/rc_aero_unchanged_evidence.json checks exact retention against sealed candidate twelve. All six AVL input/command/reference sets and 30 parsed points match. XFOIL input profiles, commands, logs, and polars are unchanged. Preserve the original solver provenance and its original recipe hash.

The previous AVL study has four tip-chord/twist combinations, baseline, and refined baseline, each at five angles. At 2 degrees, baseline CL is 0.14823 and induced-drag coefficient is 0.0016679. XFOIL retains 32 converged points of 36 requested in four cases. Keep missing points explicit.

The assumed ISA sea-level condition gives Mach 0.262738. AVL uses lifting surfaces and NACA 0006 sections. Its fixed moment reference [0,0,0] m is not a specified CG. XFOIL uses isolated visual wing profiles. These solvers exclude fuselage/root blending, inlet flow, internal layout, gear, and propulsion. The retained results do not measure this revision's aerodynamic effect.

### Report and reproduction

The report generator requires current geometry, native, visual, photo, and aero evidence. The candidate-thirteen browser preview is unavailable. The local server refused the connection, and browser policy blocked file-URL navigation. Use direct static HTML, embedded-image, link, and anchor checks. Record browser_preview_verified=false. Do not claim JavaScript, layout, or theme verification for this revision. Candidate-twelve browser QA is historical.

Host Python uses uv run --no-project --python with FuryModel/.venv/Scripts/python.exe. The build_rc_native.py, run_rc_native.py, finish_rc_native.py, and prune_interactive_checks.py tools generate the delivery. Separate gap, span, arrangement, diagnostic, and section runners generate native evidence. Verify a small fixture before the full section run. Scale only the station count.

Use owned nTop processes and unique console markers. Recheck process ownership before later GUI actions. Capture preparation, batch/single runners, photo records, and visual-review scripts preserve source and image hashes. Generate the main report only after its current acceptance gates pass.

Candidate twelve is sealed in revisions/before_junction_candidate12_20260907/, with native files, report, evidence, scripts, solver artifacts, and a SHA-256 manifest. Preserve earlier archives and the original mesh-based Fury_Editable.ntop.

## Candidate-eleven baseline (historical)

Candidate eleven is archived in `revisions/before_proportions_candidate11_20260907/`, including source recipe, native evidence, model files, scripts, and the prior aerodynamic study. It had 326 recipe variables and 3,734 verification nodes. Its interactive model had 320 variables and 2,890 nodes. Six roots and 844 diagnostic nodes were pruned with output equivalence preserved. Native and headless checks passed. Its final report/capture acceptance was interrupted by the proportion request.

Its recipe hash was `257c24b441d393ba0fbf78d1c766ef970e7f65d7cd2e42722ebc7edd0f47219b`; its interactive hash was `4c5416367b355b4fa436b81aea481fdcb0c6a8fa1639d91e8a22aeb40253ff80`. Only the explicitly verified unchanged inlet scopes apply to candidate twelve. The original archived details and failed diagnostic remain available.

## Previous candidate-ten delivery

The following candidate-ten construction, measurements, and browser results are historical. They do not verify candidate eleven.

Status: **candidate ten geometry revision complete**. Native checks, both gap fixtures, pruning comparisons, nTop Automate, and the nine-view visual review pass with current hashes. The forebody has one smooth conic underside. The splitter is separated from it and joins the cheeks through rounded returns. The original swept lower lip remains. The lower cowl has no visible oval protrusion in the reviewed views. The HTML report is generated and browser-checked.

`Fury_RC_Native.ntop` is the current candidate-ten editable native RC notebook for the nTop 6.0.0 prototype build. Its saved-file native, headless, and visual checks pass. This acceptance covers the RC geometry revision and the recorded tests, not flight readiness or validated internal flow.

The HTML report is `rc_report/Fury_RC_Engineering_Report.html`. Its eight figures include the supplied inlet close-up, current native views, a full-length cutaway, and the initial aero results. Browser review confirmed that all eight images load, no verification rows are pending or failed, and the page has no horizontal overflow. Keep the folder structure for the relative model and CSV links.

## Candidate-ten geometry (historical)

The model uses native longitudinal spline guides, conic surfaces, and implicit-spline section fields. The candidate-ten interactive notebook has 196 named variables and 1,904 graph nodes. Its full verification companion has 198 variables and 2,370 nodes. The organized graph shows seven bodies, zero mesh imports, zero errors, and no missing final bodies.

RC wingspan is 192 inches. Fuselage width, height, inlet depth, conic shape, wing tip chord, twist, and thickness are editable. Guide control-point lists are exposed in the Guide curves section.

The forebody underside uses one signed-Y conic across its full width. Its control triangle is A=(-w,0), B=(0,-2d), C=(w,0), with rho=0.5. Here, w is local half-width and d is underside depth. Existing longitudinal width, depth, and chine guides position each section. The symmetric arc replaces the previous broad flat middle and steep shoulder transitions.

The inlet retains its original swept, pointed lower edge and continuous lower guide. The splitter forms the cowl's upper wall. The roof, cheeks, and rounded leading edge form one native shell. There is no separate lip blank or span cap. A conservative C2 smooth-min guards the splitter conic against the new underside translated downward by the gap. Lateral checks verify separation at the sampled locations against the current recipe.

Candidate ten intersects the forebody solid with the existing `Cowl implicit spline` lower field. The cowl therefore limits the buried overlap, removing its narrow oval protrusion. The forward conic and splitter gap remain defined by their existing fields. A guide comparison found excess forebody depth from source x = -0.88242 to +0.07746, with a peak excess of 0.034288 at x = -0.68567. These normalized guide values diagnose the overlap; they do not measure wall thickness or general surface clearance.

The user's front markup is `reference/inlet_photos/forebody_conic_markup.png`. It defines the intended smooth underside arc. `reference/inlet_photos/flight_underside.png` supports the general appearance but does not establish an exact transverse section or production dimensions.

The diverter slot is cut after the shell is added and opens laterally. The roof closes toward the fuselage aft of the open gap. A further aft transition buries the cowl roof inside the fuselage to form its attachment. This intentional overlap starts behind the gap closure. The Splitter controls section exposes forward projection, thickness, and gap in RC dimensions.

A single native cavity extends from the inlet to the exhaust. Its rounded inlet profile transitions into a circular outlet through spline-driven sections. The former exhaust back disk is removed. The cavity is subtracted from every exterior component, including intersecting wing and tail geometry.

The Duct controls section exposes the outlet radius, wall allowance, Inlet corner radius, and Inlet face rake. The corner control sets the rounded roof-to-cheek return. The rake uses a dimensionless concept factor of 2.3; it is not an angle. The raked mouth follows the swept roof. A rounded intersection forms its continuous leading edge, with a rounding input of 0.8 times the splitter thickness.

The model rescales the raked-mouth field by one plus the absolute rake factor. This preserves the unblended zero boundary; rounded blends can change locally. A positive factor of 0.25 scales the final fuselage field after cavity subtraction to reduce ray-marching artifacts. It preserves the zero surface and material signs. Neither rescaling creates a certified distance field.

The outlet sleeve extends into the rear fuselage and geometrically closes the junction by overlap. The sampled checks do not certify minimum wall thickness.

Guide curves contains the duct center-height and radius splines. Inspection contains `RC passage cutaway` and `RC duct volume`; these are hidden in the default exterior view. The cutaway isolates the fuselage and exhaust sleeve and includes the full inlet-to-outlet path. A positive 0.25 factor scales its clipped inspection field without changing the zero surface or delivered geometry.

The internal path is an RC concept. The photographs show the exterior and do not reveal the production duct or engine installation. An open geometric passage does not establish airflow, pressure recovery, flow splitting, or propulsion performance.

The chine remains an intentional edge; the inlet leading edge and cheek return are rounded. The small fairing, probe, and exhaust rim reproduce visible features only. This is an RC appearance model. The requested 95% likeness is a visual target, not a measured match. Prior revisions are preserved in `revisions/before_splitter_20260907/`, `revisions/before_photo_duct_20260907/`, and `revisions/before_gap_fillet_20260907/`.

## Candidate-ten verification (historical)

The candidate-ten transverse gap fixture passes all 78 gap samples at source x = -3.05 and -2.8, through 99% of forebody half-width. All surface-placement, guarded-roof boundary, and above/below sign checks pass. The largest underside field residual is 1.279e-12 m against a 1.875e-5 m placement tolerance. `_agent/span_gap_check_results.json` records matching current recipe and fixture hashes.

The exact gap-field dependency fixture passes the requested 1.1 change ratio and exact reset against the candidate-ten recipe hash. It does not establish a live change and reset of the complete model.

Positive probe values indicate sampled points outside material. They do not certify wall thickness, physical clearance, flow performance, or the complete space between probes. The transformed fields are not certified distance fields. Fit errors in the report apply to guides, not the full exterior.

Candidate-ten full native readback passes the 192-inch span and wing and splitter sign checks. All 200 native-body corridor probes and 30 final-union passage probes are positive. `_agent/rc_native_checks.json` links the results to the current source recipe.

The saved candidate-ten interactive file passes nTop Automate with exit code 0 and a matching file hash. Nine current views pass visual review: both underside obliques, front inlet, elevated, grazing, cutaway, cutaway detail, overview, and inlet close-up.

`validation/Fury_RC_Native_Verification.ntop` retains the dense passage probes. The interactive delivery omits their two roots to avoid recalculating them during each edit. Candidate-ten pruning removes 466 diagnostic nodes and preserves the retained output graph and literal hashes. `_agent/rc_interactive_prune.json` records both file hashes and matching structural comparisons. Its native execution flag is true for the current interactive file.

`_agent/rc_visual_review.json` records the passing visual review with current recipe, notebook, and image hashes. The front view shows one smooth underside arc. Both underside views retain the swept, pointed lower lip, visible diverter gap, and continuous cheek returns. The lower cowl and detail section show no residual oval protrusion. The cutaway shows the modeled cavity continuing to the outlet without a visible back disk or belly breakthrough.

Small trailing-edge ripples remain in the implicit viewport display. An export-tolerance study is still required before manufacturing geometry is accepted.

## Earlier verification

Candidate nine passed native readback, all 78 lateral gap samples, 200 corridor probes, and 30 final-union passage probes. Its conic placement residual was at most 1.279e-12 m against a 1.875e-5 m tolerance. Its gap-field dependency fixture measured a 1.1 change ratio and exact reset. These checks describe candidate nine only.

Candidate nine had 196 variables and 1,904 nodes in the interactive copy, and 198 variables and 2,370 nodes in the full verification copy. It had seven displayed bodies, zero mesh imports, and zero graph errors. Pruning removed 466 diagnostic nodes and preserved the output graph and literal hashes. Its saved interactive notebook passed nTop Automate with exit code 0 and matching hash.

Candidate-nine front and right-underside views showed the requested smooth arc and improved cheek return. They also revealed a small oval protrusion below the cowl. The guide comparison identified a buried forebody overlap extending beyond the cowl. Visual acceptance was withheld, leading to candidate ten.

Candidate seven's separate gap fixture passed 54 of 54 body samples and all 18 roof-boundary checks. Its lateral positions stopped at 90% of half-width. Its first reviewed underside image removed the visible contact patch and exterior shelf, but the upper cheek crest remained too pointed. These results do not verify candidate nine.

Candidate eight introduced a straight lower mouth and flat central cowl and duct floors. The user withdrew that direction and requested the original swept, pointed lower lip. Candidate nine removes those straightening changes and replaces the forebody underside with one conic. It retains the softer leading-edge rounding and positive final-field scaling.

Revision five had 188 named variables, 2,017 graph nodes, and seven displayed bodies in the interactive copy. Its full verification companion had 190 named variables and 2,483 graph nodes. Its wing, integrated splitter, and 16 ft span checks passed. All 200 native-body corridor probes and 30 final-union passage probes were positive. Its saved interactive notebook passed nTop Automate with exit code 0 and a matching file hash. These results describe revision five only.

Earlier full-model tests checked 5% width and 10% tip-chord changes with exact reset. The photo revision's full-model live gap test was canceled because evaluation was too slow. Its separate ten-variable gap-field fixture measured a 1.1 change ratio and exact reset. That earlier result does not establish a candidate-nine reset or a completed full-model gap reset. Accept fixture evidence only when its saved recipe hash matches the current recipe.

Revision-five front, close-up, overview, and cutaway images were reviewed. Its front view showed no projecting lip shoulders, and its cutaway showed the connected rear sleeve. The later underside user view revealed off-center splitter intersection and a sharp cheek return. Those earlier views and tests did not detect these defects. The model omits the photographed red inlet cover, so opposite aperture edges can remain visible in the close-up.

## Aerodynamics: candidate-twelve update (historical)

The user supplied 16 ft span and 200 mph. The study assumes ISA sea-level conditions, giving Mach 0.262738.

- AVL reran **30 operating points** with the current wing translation and HStab span. Four tip-chord/twist combinations, baseline, and refined baseline each use five angles. Main-wing reference area, chord, and span remain unchanged. At 2 degrees, baseline CL is 0.14823 and induced-drag coefficient is 0.0016679.
- XFOIL was **not rerun**. The four prior root/tip and thickness cases retain 32 converged points out of 36 requested. Section inputs and all 16 raw input, profile, log, and polar files retain matching hashes. Baseline root angles 0, 5, and 6 degrees and thickened-tip angle 0 degrees remain missing.
- `rc_aero/results.json` and `summary.json` link the current geometry controls and source recipe. `rc_aero/trade_summary.csv` contains the updated comparison. Raw solver output remains in each case directory. The prior study is archived with candidate eleven.

AVL uses lifting surfaces and NACA 0006 sections. Its moment reference remains [0,0,0] m, not a specified CG. XFOIL retains the drawing's isolated visual wing sections. These results are not a coupled whole-aircraft viscous analysis. The fuselage, inlet/splitter flow, root blends, internal layout, gear, and propulsion are excluded. No trim, static margin, stall limit, inlet recovery, structural capacity, or flight readiness is established.

## Baseline rebuild notes (historical)

Host scripts use uv with the task virtual environment. `tools/build_rc_native.py` writes the recipe and uses `tools/native_inlet_duct.py` for the integrated inlet. Execute `tools/run_rc_native.py` in the owned nTop Python Console. Then run `tools/finish_rc_native.py` on the host to organize and save the final notebook. `tools/prune_interactive_checks.py` preserves the full verification notebook and removes its two dense-check roots from the interactive copy. Preserve prior verification artifacts separately before rebuilding a new revision. `tools/make_rc_views.py` creates fixed exterior and passage inspection views.

`tools/prepare_gap_fixture.py` extracts the gap-field dependency fixture from the current recipe. Execute `tools/run_gap_fixture.py` in the owned nTop Python Console. The saved result includes its scope and source recipe hash.

`tools/prepare_span_gap_check.py` extracts the actual conic underside and native body dependencies for the transverse gap fixture. It records the source recipe hash and sample locations. Execute `tools/run_span_gap_check.py` in an owned scratch nTop notebook. Its results include body signs, native placement checks, guarded-roof boundary checks, and fixture hashes. This fixture supplements full-model verification; it does not replace it.

`tools/record_rc_execution.py` checks the current headless result and file hash, then records native execution verification in the pruning manifest.


`tools/run_rc_aero.py --smoke` checks both solvers. The full script runs the study. `tools/plot_rc_results.py` plots solver results. `tools/make_rc_report.py` regenerates the HTML report after final native images and verification evidence are ready. The earlier contour-comparison scripts and plot remain historical; the current report uses a front inlet view instead.

The earlier mesh-based `Fury_Editable.ntop` and `visual_review/` report remain historical artifacts. They are superseded for the current RC task.
