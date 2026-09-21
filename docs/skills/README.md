# Engineering skill package

All **18 named skills** from the paper handoff are available in this repository.
The existing **sheet-metal** and **engineering-html** skills bring the repository total to **20 skill entries**.
The **ten future skills are proposals**, stored separately from executable agent instructions.

The package covers native authoring, modeling, nTop CL, studies, meshing, CFD, analysis methods, and reporting.
It does not imply that every experiment used every skill or that the skills form one executable pipeline.

## Skills and their contents

| Area | Skill | Public package content |
|---|---|---|
| Authoring | [ntop-notebook-api](../../.agents/skills/ntop-notebook-api/SKILL.md) | Current build 42926 API guidance, native graphs, units, recipes, dispatch, and verification |
| Modeling | [ntop-csg-modeling](../../.agents/skills/ntop-csg-modeling/SKILL.md) | Measured native reconstruction, stock, profiles, cuts, fillets, and source fidelity |
| Assembly | [ntop-assembly-modeling](../../.agents/skills/ntop-assembly-modeling/SKILL.md) | Native part contracts, shared definitions, placements, controlled imports, and an offline pilot |
| Custom assembly | [ntop-custom-assembly](../../.agents/skills/ntop-custom-assembly/SKILL.md) | Original skill name retained; reusable implementation consolidated into assembly and CSG guidance |
| nTop CL | [run-ntop-automate](../../.agents/skills/run-ntop-automate/SKILL.md) | Headless execution, version checks, InterOp diagnostics, output validation, and recovery |
| nTop CL | [ntop-automate](../../.agents/skills/ntop-automate/SKILL.md) | JSON schemas, iterative values, grids, and container/batch contracts |
| Studies | [ntop-doe-sweep](../../.agents/skills/ntop-doe-sweep/SKILL.md) | Reproducible sampling, typed input preparation, measurements, receipts, retries, and failure analysis |
| Remote execution | [ntop-orchestrate](../../.agents/skills/ntop-orchestrate/SKILL.md) | Versioned remote actions, NDJSON tasks, artifact retrieval, and result checks |
| Interactive review | [open-ntop-gui](../../.agents/skills/open-ntop-gui/SKILL.md) | Explicit GUI launch with selected inputs and task-owned process verification |
| Meshing | [AFLR3 Mesh Generator](../../.agents/skills/aflr3-mesh-generator/SKILL.md) | Body/farfield inputs, boundary-layer choices, mesh checks, and solver format handoff |
| CFD | [Fun3D CFD Runner](../../.agents/skills/fun3d-cfd-runner/SKILL.md) | Flow and reference contracts, solver settings, convergence, output, and refine notes |
| Cloud CFD | [fun3d-gcp](../../.agents/skills/fun3d-gcp/SKILL.md) | Configured GCP access, durable transfer, measured sizing, recovery, and owned-resource lifecycle |
| High-order CFD | [ntop-nektar-cfd](../../.agents/skills/ntop-nektar-cfd/SKILL.md) | Custom integration requirements, mesh curving, solver checks, example conditions, and field analysis |
| CFD | [run-lava](../../.agents/skills/run-lava/SKILL.md) | Solver-family selection, v1.0.0 compatibility findings, mesh/BC contracts, propulsion conditions, and evidence |
| Scientific reports | [engineering-report](../../.agents/skills/engineering-report/SKILL.md) | Scripted mesh/field figures, PDF production, rendering references, and verification helpers |
| Documents | [ntop-docs-v1](../../.agents/skills/ntop-docs-v1/SKILL.md) | Evidence structure, captions, source links, limitations, and rendered HTML delivery |
| Design | [ntop-design-v1](../../.agents/skills/ntop-design-v1/SKILL.md) | Typography, colors, layouts, accessible figures, and offline template references |
| Writing | [ntop-writing-style](../../.agents/skills/ntop-writing-style/SKILL.md) | Plain technical prose, units, source status, and calibrated claims |

Additional skills already present on main:

| Skill | Contents |
|---|---|
| [ntop-sheet-metal](../../.agents/skills/ntop-sheet-metal/SKILL.md) | Analytic bends, reliefs, drafted forms, assemblies, blank estimates, and scoped tooling illustrations |
| [engineering-html](../../.agents/skills/engineering-html/SKILL.md) | Implemented offline report template, design rules, accessible controls, and evidence delivery |

## Lofting and analysis methods

These methods are part of the workflow but were not separate installed skills in the original 18-skill inventory.

| Method | Repository reference |
|---|---|
| Guide-driven conic and spline lofting | [Lofting guide](../LOFTING.md), [F-16](../../demos/f16/README.md), and [A-12](../../demos/a12/README.md) |
| Two-rail blade sweeps | [Propeller lessons](../PROPELLER_LEARNINGS.md) and [propeller studies](../../demos/propellers/README.md) |
| Native graph, geometry, and display verification | [Verification](../VERIFICATION.md), [API reference](../API_REFERENCE.md), and [recent lessons](../RECENT_MODELING_LEARNINGS.md) |
| Structural and buckling screens | [Civil research aircraft](../../demos/civil-research-aircraft/README.md), with its recorded failure modes and analysis limits |
| Engine cycle calculations | [Jet cycle model](../../demos/jet20/scripts/cycle.py) and [jet example](../../demos/jet20/README.md) |
| CFD field analysis | [Nektar++ postprocessing](../../.agents/skills/ntop-nektar-cfd/references/postprocessing.md) and [field figures](../../.agents/skills/engineering-report/references/flow_fields.md) |

The paper map also names the Ski-A170 beam/torsion work from the broader local inventory.
That source project is not bundled here. The figure is a workflow inventory, not a claim that every project script is redistributed.
The aircraft package preserves specific recorded revisions and reports, not a general structural-analysis solver.

## Paper handoff

- [Two-page vector PDF](paper/ntop-engineering-skills.pdf)
- [Current-skills SVG](paper/current-engineering-skills.svg) and [PNG](paper/current-engineering-skills.png)
- [Future-skills SVG](paper/proposed-engineering-skills.svg) and [PNG](paper/proposed-engineering-skills.png)
- [Captions and methods paragraph](captions.md)
- [Ten future skill briefs](future-engineering-skills.md)
- [Figure source](paper/make_diagrams.py)

The figures retain the **16 September 2026 inventory scope**: 18 named existing skills and ten future proposals.
The two additional repository skills appear in the catalog above. They do not change the figure's inventory count.
The proposed briefs include George Irving's configurator, expert airframing, propulsion, weights, S&C, loads, structural sizing, mission performance, manufacturing, and verification.
George's rules still require his contribution and review. The proposal does not claim that his expertise has already been encoded.

The figures use the nTop document design system: Aeonik headings/body, Aeonik Fono labels, blue highlights, light-grey surfaces, and thin rules.
The PDF contains selectable text and embedded font subsets. SVG lettering uses outlines with accessible labels for consistent viewing.
The PNGs are 450 dpi. Font source files are not distributed.
The [layout receipt](paper/layout-verification.json) records dimensions, fonts, label coverage, and file hashes.

The generator uses the bundled engineering-report style helper.
To reproduce the Aeonik typography, set `NTOP_REPORT_FONT_DIR` to an authorized local directory containing `aeonikvf.ttf` and `aeonikfonovf.ttf`.
The helper uses portable sans-serif and monospace fallbacks when those fonts are unavailable. It records the selected fonts in local output.
The source regenerates the vector figures and PNGs into ignored local output.

To regenerate:

```text
uv run --locked --group render python docs/skills/paper/make_diagrams.py --out .local/skill-figures
```

## Use and dependencies

Clone the repository and use its project-local `.agents/skills` directory with a compatible agent.
Read the selected `SKILL.md` and follow its linked resources. No global installation is required for repository use.
For another project, preserve the linked `docs`, `templates`, `harness`, and supporting skill resources; copying one file can break its references.

The skills package instructions and selected helpers. They do not include nTop, licenses, a compute cluster, or proprietary solver binaries.
AFLR3 requires its authorized driver and mesher. FUN3D, LAVA, and nTop Core integrations require compatible external installations.
Orchestrate requires a configured service and a matching CLI. The deployment owner supplies endpoints, identities, credentials, and resource policy.

## Adaptation and provenance

The [source receipt](source-provenance.json) records hashes and logical filenames without private source-workspace paths.
Four current public skills were preserved. Fourteen entries were added, including the custom-assembly routing entry.
The source deployment defaults, credentials, private URLs, host inventories, raw logs, binaries, and large solver outputs are excluded.
Old cloud lifecycle and download scripts are replaced by explicit deployment contracts.
The GUI launcher is replaced by the direct command with selective path handling.
The old sweep runners are replaced here by a bounded input-preparation helper and explicit run guidance.
The helper does not launch a solver, provision a fleet, or verify native results.

Public adaptations resolve source contradictions and qualify historical claims. They are not byte-for-byte private archives.
Current API documentation targets build 42926; each older recorded result keeps its own build label.
See [package verification](VERIFICATION.md) for the checks performed on this update.
