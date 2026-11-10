# New nTop and engineering skills

This update adds nine locally authored skills to the existing public collection.
Use the [catalog](README.md#skills-added-on-10-november-2026) to choose a skill.
Each entry includes its supporting references and any portable helper scripts.

## Scope and dependencies

The leading-edge skill includes root fairness, compact recovery, inlet and trailing
edges, cleanup, and an SI section checker. Its HM dependency includes scalar
reference formulas and recorded samples from a synthetic wing demonstration.

The windscreen and car-body skills retain documented failures and geometry checks.
Their source models, photographs, development scripts, and full study receipts
remain external. Case measurements are recorded findings, not default dimensions
or a claim that this publication reran those studies.

The adjoint skill includes a read-only directional-gate auditor. Native notebooks,
meshes, solver installations, and case data must be supplied separately.
The STYX skill includes combustion and engine verification guidance. Its private
implementation and active-run inventory are not part of this public package.

The Unlinked skill includes a loopback API client and an analytic decay pilot.
Install the external service separately. The referenced custom launchers and
mechanism dashboards are not included in the upstream service or this package.
The Omniverse skill includes storyboard guidance and an FFmpeg verification helper.
Omniverse Kit, FFmpeg, licensed fonts, source geometry, and simulation traces are
external requirements. The community skill includes templates and audit guidance;
consult the current contribution contract before submitting a model.

For native authoring, use the repository's existing Notebook API skill and match
the API to the installed build. Different recorded cases used different builds.
This update does not replace the existing API reference or its supported scope.

## Public adaptation

Machine paths and inaccessible source-project links were removed or replaced.
External artifact names remain only where they explain a recorded workflow.
The STYX active-run log and Omniverse workstation inventory were replaced with
portable lessons. Python caches, model files, images, binaries, credentials, and
large generated results were excluded from this upload.

The [provenance receipt](new-skills-2026-11-10-provenance.json) records each source
file's hash and its published hash. Logical names replace private source paths.
Existing repository files and historical paper figures retain their scope.

## Verification scope

Publication checks cover skill metadata, YAML and JSON parsing, Python syntax,
local reference targets, public-content patterns, and source receipt integrity.
The bundled leading-edge self-test and HM checker run without nTop.
The HM check compares its formulas with 270 previously recorded native samples.
All nine HM tests and all three Unlinked offline failure-handling tests pass.
The leading-edge self-test passes straight, displaced, mistwisted, and non-finite fixtures.
CLI checks exercise argument parsing for the adjoint, Unlinked, and movie helpers.

These checks do not run nTop, Unlinked services, STYX, CFD, cloud jobs, Omniverse,
or a community submission. They do not reproduce the full historical studies.
