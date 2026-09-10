# 20 lbf jet: agent instructions

Read the root AGENTS.md, the shared Notebook API skill, and this demo's README.md.
A native compressor, combustor, turbine, housing joints, fasteners, and service routes. The 20 lbf value is a conditional sizing target.

- scripts/ contains the standalone source. inputs/ contains the minimal rebuild data.
- models/ contains retained native snapshots. Use output/ and root .local/ for new work.
- reports/index.html contains the public report. LEARNINGS.md contains the edited project record.
- Build from the repository root with `uv run --locked python scripts/build.py jet20`.
- Use `uv run --locked python scripts/stage.py jet20` for a new empty nTop notebook.
- Validate units and graph dependencies before evaluating large geometry.
- Read measured scalar values and inspect the final geometry after native execution.
- Keep geometry fit, selected dimensions, numerical checks, and engineering qualification distinct.
- Finish with collapsed authored blocks and sections in a separate saved deliverable.

Keep screenshots/ with the real assembled and exploded nTop UI captures. Preserve their provenance.
