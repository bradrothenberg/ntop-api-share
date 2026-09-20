# Paper captions: 16 September inventory

The figures retain the original 18-skill research scope. The repository additionally includes sheet-metal and engineering-html skills.
See the [current package catalog](README.md). The figures show workflow roles, not proof that every experiment used every skill.

**Figure X. Current skills and supporting methods for agent-assisted nTop engineering experiments.** Eighteen named skills cover native notebook authoring, solid reconstruction, assemblies, notebook execution, CFD, and reporting. Lofting and two-rail sweeps are explicit modeling methods within the Notebook API workflow and its project references. Project analysis scripts support section and beam models, finite-element and buckling screens, engine-cycle matching, and propeller studies. The arrows show functional workflow and feedback. They do not imply a single executable pipeline or a required sequence. Verification occurs at each stage.

**Figure Y. Proposed engineering skills connected through a shared aircraft design contract.** Ten candidate skills would coordinate configuration, airframing, propulsion, mass properties, stability and control, loads, structural sizing, aerodynamics, manufacturing, and verification. Each would read a versioned design state and return proposed changes, assumptions, results, and validation evidence. The George Irving configurator would encode rules that George supplies and approves. Dashed boxes identify proposals rather than installed or validated capabilities.

## Interpretation notes

- Blue names in the current map identify existing named skills. Gray method panels identify supporting guides and project implementations.
- There are 18 distinct named skills in this scoped engineering inventory. Copies and project variants do not increase that count.
- Five current skills cover CFD and meshing: AFLR3 Mesh Generator, Fun3D CFD Runner, fun3d-gcp, ntop-nektar-cfd, and run-lava.
- The engineering-report skill covers scientific visualization and reporting. It does not itself perform every structural analysis shown in the methods panel.
- No standalone lofting, propulsion-analysis, weights, S&C, or general structural-analysis SKILL.md was found in the inspected experiment and installed-skill roots. Related methods exist in references and project scripts.
- The public native loft path is documented in [LOFTING.md](../LOFTING.md). It uses guide-driven conic and spline surfaces. Two-rail blade methods are recorded in the build 42926 notes and propeller examples.
- Structural screening is not automatically a full three-dimensional FEA model or a release approval. Each case retains its own model fidelity and validation limits.
- The future briefs are a proposed organization of engineering expertise. They were not installed, executed, or validated as part of this handoff.
- Current skills retain different build and deployment assumptions. The public API documentation uses build 42926. Earlier experiment evidence retains its original build label.
- The source files were inspected on 16 September 2026. This task did not rerun the original engineering experiments.
- The inventory covers the nTop modeling and engineering experiment workflow. Generic assistant-development tools and unrelated office or application plugins are outside its scope.

## Suggested methods paragraph

The workflow combines reusable agent skills with project-specific engineering methods. The Notebook API skill manages native block authoring, units, recipes, and execution evidence. Modeling skills add source reconstruction and modular assembly contracts. Related references describe guide-driven lofting, two-rail sweeps, native rendering, and mesh export. Execution skills run prepared notebooks and parameter studies. Separate meshing and CFD skills prepare and solve flow cases. Project analysis scripts evaluate selected structural and propulsion models. Reporting skills collect the resulting evidence. Each stage retains its assumptions and links results to a specific model revision.

The proposed extension would organize additional engineering expertise into ten coordinated skills. A shared design contract would connect geometry, interfaces, loads, mass properties, and performance. Candidate changes would require explicit validation before they could update the accepted design state.
