# Potential future engineering skills

Status: proposed briefs for discussion with Jan and George. These are not installed skills or validated engineering capabilities.

The briefs describe what each skill could contain. Existing scripts provide starting examples, but they do not establish the complete proposed capability.

## Shared design contract

Each skill should use the same versioned aircraft definition. This contract should contain:

- Mission requirements, configuration identity, operating cases, and acceptance criteria.
- Native geometry references, coordinate frames, units, stations, interfaces, and parameter ranges.
- Materials, process assumptions, loads, mass properties, and analysis fidelity.
- Sources and assumptions, with an explicit distinction between supplied values, inferred values, and measurements.
- Input and output schemas, source hashes, solver or tool versions, and verification receipts.
- Proposed changes, affected disciplines, unresolved inputs, and limits on use.

An agent should submit a change set against this contract. It should preserve the accepted design until dependent checks pass. A drawing, a solver result, and a manufacturing approval should have separate status fields.

## 1. George Irving configurator

**Proposed ID:** `george-irving-configurator`

**Purpose:** Convert George's reviewed configuration practices into repeatable aircraft layout rules. This proposal does not assume those practices have already been captured.

**Inputs:** Mission, payload, design envelope, propulsion options, packaging constraints, and configuration rules supplied or approved by George.

**Potential contents:** A library of reviewed layouts; station and volume allocation; wing and tail placement; primary structure topology; access and interface rules. Each rule would retain its source, scope, rationale, exceptions, and unresolved cases.

**Outputs:** Candidate configuration graphs, editable nTop layout parameters, envelope and interference checks, and a list of decisions requiring expert review.

**Validation gate:** Reproduce a small set of George-approved examples. Test rule conflicts and changes at design-range boundaries. Ask George to review the rules before labeling the skill with his expertise.

## 2. Expert airframing

**Proposed ID:** `expert-airframing`

**Purpose:** Turn an aircraft layout into a coordinated structural arrangement.

**Inputs:** Outer geometry, wing planform, load introduction points, material and process choices, systems zones, and removable-panel requirements.

**Potential contents:** Spar and carry-through arrangement; frames, ribs, longerons and stringers; bulkhead shoulders; integral lugs and fork joints; fastener and access planning. The skill would coordinate intersecting members and explain their intended load transfer.

**Outputs:** Separate editable part families, an assembly graph, joint interface contracts, connection diagrams, and a ledger of unresolved structural details.

**Validation gate:** Check continuity, alignment, clearance, load introduction, and access. Confirm that contact between solids represents the intended joint. Pass the arrangement to loads and structural sizing before claiming adequate strength.

## 3. Propulsion and installation

**Proposed ID:** `propulsion-integration`

**Purpose:** Match an engine or propulsor to the mission and its installation.

**Inputs:** Required thrust or power, operating conditions, component maps, fuel or electrical limits, installation geometry, and source uncertainty.

**Potential contents:** Cycle and shaft matching; propeller or fan operating points; inlet and exhaust losses; thermal and cooling requirements; thrust lines and attachment loads. Separate reduced models from resolved CFD. Add acoustic methods only after their source and validation are defined.

**Outputs:** Operating maps, thrust and power schedules, fuel or energy use, installation loads, rejected operating points, and geometry change requests.

**Validation gate:** Check mass and energy balances, map interpolation limits, units, and installation conventions. Compare selected conditions with trusted component data or test results. Label uncalibrated predictions explicitly.

## 4. Weights and mass properties

**Proposed ID:** `weights-mass-properties`

**Purpose:** Maintain a traceable mass, center-of-gravity, and inertia model.

**Inputs:** Part volumes, material densities, purchased equipment, fasteners, fluids, payloads, installation allowances, and loading cases.

**Potential contents:** A hierarchical mass ledger; exclusions and growth allowances; fuel and payload sequencing; coordinate transformations; uncertainty propagation. Separate mass from force units. Preserve the source and confidence of every ledger item.

**Outputs:** Component and assembly mass, center of gravity, inertia tensors, loading envelopes, mass changes by revision, and uncertainty ranges.

**Validation gate:** Reconcile assembly totals against component sums. Check transforms with analytical examples. Detect duplicate items and missing systems. Compare model estimates with measured hardware where available.

## 5. Stability and control

**Proposed ID:** `stability-control`

**Purpose:** Evaluate trim, stability, response modes, and control authority across selected operating cases.

**Inputs:** Aerodynamic derivatives or response tables, control definitions, mass properties, propulsion effects, flight conditions, and evaluation criteria.

**Potential contents:** Trim solutions; static margins; longitudinal and lateral-directional modes; control effectiveness; actuator limits; loading-envelope sensitivity. Track model fidelity and the range where each derivative model applies.

**Outputs:** Trim and control schedules, stability summaries, mode characteristics, limiting cases, and geometry or control-sizing requests.

**Validation gate:** Check sign conventions, axes, derivative units, and equilibrium residuals. Reproduce a reference model and compare independent formulations. Require appropriate higher-fidelity analysis or testing before making handling-quality or flight-readiness claims.

## 6. Loads and aeroelasticity

**Proposed ID:** `loads-aeroelasticity`

**Purpose:** Create consistent loads and evaluate selected interactions between stiffness and aerodynamic response.

**Inputs:** Operating envelopes, aerodynamic distributions, mass and inertia, stiffness models, ground cases, control motions, and governing criteria.

**Potential contents:** Maneuver, gust, landing and other declared load cases; inertial relief; load transfer between meshes or beam stations; deformation feedback; divergence and flutter screening at a declared fidelity.

**Outputs:** A versioned load-case database, interface forces and moments, load envelopes, stiffness requirements, and aeroelastic sensitivities.

**Validation gate:** Check force and moment balance before and after every transfer. Run stiffness and resolution studies. Verify the selected aeroelastic formulation against reference cases. Keep screening results separate from qualification.

## 7. Structural sizing and joints

**Proposed ID:** `structural-sizing-joints`

**Purpose:** Size structural members and connections against a declared set of failure modes.

**Inputs:** Geometry, loads, material allowables, boundary conditions, joint definitions, process limits, and uncertainty assumptions.

**Potential contents:** Beam, shell, or solid analysis as appropriate; local and member buckling; bearing and bypass loads; fastener groups; fatigue and damage checks where adequate data exist. Maintain a failure-mode coverage matrix.

**Outputs:** Thicknesses and section dimensions, margins by load case and failure mode, proposed joint changes, mass changes, and unresolved checks.

**Validation gate:** Use analytical benchmarks and resolution studies. Test sensitivity to boundary conditions and assumed skin support. Retain allowable provenance and explicitly identify excluded modes. Existing aircraft buckling studies are starting examples, not complete validation of this skill.

## 8. Aerodynamics and mission

**Proposed ID:** `aerodynamics-mission`

**Purpose:** Connect aerodynamic models to mission-level performance and configuration trades.

**Inputs:** Geometry, flight conditions, propulsion maps, mass properties, mission segments, atmospheric assumptions, and performance constraints.

**Potential contents:** Model-fidelity selection; aerodynamic polars; trim drag; installed performance; takeoff, climb, cruise and landing estimates; range and endurance calculations. Record where a model lacks separation, compressibility, or interference effects.

**Outputs:** Performance envelopes, mission fuel or energy, aerodynamic sensitivities, design comparisons, and cases requiring additional CFD or test data.

**Validation gate:** Check reference area, axes and force conventions. Compare simple cases against trusted results. Separate numerical convergence from model accuracy. Do not rank candidates with inconsistent fidelity or assumptions.

## 9. Manufacturing and assembly

**Proposed ID:** `manufacturing-assembly`

**Purpose:** Relate geometry and structural intent to explicit manufacturing and assembly proposals.

**Inputs:** Process and supplier constraints, materials, part geometry, joint definitions, tolerances, inspection needs, and maintenance requirements.

**Potential contents:** Machining access; forging and forming allowances; additive orientation and support rules; tool and fastener access; assembly sequence; removable panels; tolerance accumulation. Keep process-specific knowledge separate from generic geometry checks.

**Outputs:** Manufacturing constraints, proposed part changes, assembly sequence diagrams, tolerance budgets, inspection plans, and cost or lead-time estimates with sources.

**Validation gate:** Review representative details with the relevant process expert or supplier. Test access and tolerance assumptions. Distinguish a geometric screen from a qualified manufacturing process.

## 10. Verification and trade studies

**Proposed ID:** `engineering-verification-trades`

**Purpose:** Coordinate evidence and compare designs under consistent multidisciplinary constraints.

**Inputs:** The shared design contract, requirements, skill outputs, parameter bounds, model fidelity, uncertainty, and acceptance rules.

**Potential contents:** Dependency tracking; input-change invalidation; benchmark selection; reproducible studies; uncertainty and sensitivity analysis; constraint enforcement; candidate ranking. Preserve failed trials and reasons for exclusions.

**Outputs:** A traceable verification matrix, experiment manifests, trade plots, candidate comparisons, evidence gaps, and explicit decisions for review.

**Validation gate:** Reproduce a baseline and an intentionally failing case. Prove that changed geometry invalidates affected results. Use independent checks for critical calculations. Require equal assumptions and constraints for comparisons.

## Suggested development sequence

This sequence is a proposal, not a measured estimate of development effort.

1. Define the shared contract and a small benchmark aircraft. Establish the mass ledger and evidence checks first.
2. Capture a bounded set of George's configuration rules. Connect them to the existing modeling and assembly skills.
3. Extract the existing beam, buckling, cycle and CFD methods into explicit interfaces. Retain their present limits.
4. Add loads, aerodynamic performance, propulsion and S&C in a coordinated loop. Check each interface before scaling the design space.
5. Add manufacturing and qualification-oriented checks with suitable expert review and test evidence.

## Connection to current skills

The future skills would use the existing Notebook API, CSG and assembly skills to implement geometry. nTop CL skills would execute prepared notebooks. Meshing and CFD skills would provide declared analysis routes. Reporting skills would present results and evidence.

The future layer should not hide those execution details or erase their build-specific limits. It should select a method, record why it is suitable, and check its outputs before updating the accepted design.
