# nTop Notebook API: public demo collection

Eleven editable demonstrations and 29 reports, with six source builders, five saved-graph replay collections, and measured Notebook API lessons.
Each demo contains a local agent, scripts, native models, and an HTML report. No private project checkout is required.

| Demo | Learn from it |
|---|---|
| [KestrelSAT corner](demos/kestrelsat-corner/README.md) | One native CSG part, its original STEP reference, matched geometry views, and measured volume and surface checks. |
| [Propellers](demos/propellers/README.md) | An eight-inch assembly, separate retained spinner, twenty native two-rail blade studies, and a CFD optimization plan. |
| [Original inline-six](demos/i6/README.md) | An API recorder, slider-crank mechanism, cam motion, and analytic helical springs. |
| [I6 Astra](demos/i6-astra/README.md) | A native assembly with involute gears, nominal fasteners, belts, spline routes, and mechanism checks. |
| [20 lbf jet](demos/jet20/README.md) | A native compressor, combustor, turbine, housing joints, fasteners, and service routes. The 20 lbf value is a conditional sizing target. |
| [Fury RC](demos/fury/README.md) | The finite-edge native snapshot and mesh evidence, plus the earlier conic-loft construction baseline. |
| [B52 fuselage](demos/b52/README.md) | The R7 fair nose blend and accepted cockpit loft. Geometry is derived from a GPL-2.0 artist model, not production aircraft data. |
| [DDGX concept](demos/ddgx/README.md) | A normalized public-concept exterior with a native hull loft, superstructure, and editable display features. Dimensions are inferred. |
| [F-16](demos/f16/README.md) | R6 fair airfoils, finite trailing edges, and earlier cross-CAD comparisons. |
| [A-12](demos/a12/README.md) | Independent section surfaces, fair guides, and the R33 cockpit study. |
| [F-Cat](demos/fcat/README.md) | A continuous bent tail, cargo-pod fairing, and recorded aerodynamic studies. |

[Open the report catalogue](reports/index.html). Download the complete repository, then open `reports/index.html` locally. The pages share offline assets. Reference photographs and videos remain in the separate downloadable collection.

## Get started

Requirements: Windows, Git, uv, and a licensed nTop custom build with the Notebook API.
The current API documentation targets **nTop 6.1.0-rc build 42926**, from the September 10 package.
The original demos retain their recorded **6.0.0-rc build 42594** provenance.
Start with the [current method reference](docs/API_REFERENCE.md) and [September changes](docs/API_42926.md). Obtain licensed builds from their maintainer.
The application and license are not included. Offline builders and tests run without nTop.

```powershell
git clone https://github.com/bradrothenberg/ntop-api-share.git
cd "ntop-api-share"
.\scripts\bootstrap.ps1 -NTopExe "C:\path\to\custom-build\ntop.exe"
uv run --locked python scripts/smoke.py
uv run --locked pytest -q
```

Launch a separate task-owned nTop process directly from that PowerShell session using the [launch and attachment procedure](docs/BACKGROUND_CONSOLE.md#launch-a-separate-task-owned-process).
Use the Notebook API after verifying the intended process and scratch notebook. For manual console use, open **View > Python Console** in that new empty notebook:

```python
import ntop_api
ntop_api.check_api(notebook, require_42926=True)
ntop_api.hello(notebook)
```

This checks the API surface, imports a small SI recipe, verifies 2 + 3 = 5, and saves a working notebook.
[Full setup](docs/SETUP.md) explains demo selection, background dispatch, and portable model paths.

## Structure

```text
ntop-api-share/
  harness/              Standalone in-nTop agent and API entry point
  scripts/              Build, stage, audit, native-file, and background-console tools
  demos/<demo>/
    AGENTS.md           Local agent instructions; CLAUDE.md routes here
    scripts/            Editable source and numerical helpers
    inputs/             Minimal source data or complete native recipe
    models/             Relevant .ntop snapshots
    reports/            Public HTML report and compact assets
    output/             Generated recipes and run evidence; ignored
  reports/              29-report offline catalogue and shared compact assets
  docs/                 Shared API, lofting, assembly, and verification lessons
  .agents/skills/       Bundled API, CSG, assembly, and HTML-report skills
  templates/            HTML report template and offline CSS
  tests/                Portability and graph-invariant checks
```

## Read next

- [Native CSG modeling skill](.agents/skills/ntop-csg-modeling/SKILL.md) and [corner comparison](demos/kestrelsat-corner/reports/index.html)
- [Native assembly modeling skill](.agents/skills/ntop-assembly-modeling/SKILL.md): reusable custom parts, explicit inputs, shared placements, and a generic contract pilot
- [KestrelSAT skill audit](docs/KESTRELSAT_SKILL_AUDIT.md): source coverage, resizing lessons, and recorded pilot scope
- [Recent modeling lessons](docs/RECENT_MODELING_LEARNINGS.md): bulkheads, marine propellers, skis, KestrelSAT, and DDG(X), with evidence and unfinished experiments separated
- [Build 42926 changes](docs/API_42926.md) and [propeller workflow lessons](docs/PROPELLER_LEARNINGS.md)
- [API lessons](docs/API.md), [current method reference](docs/API_REFERENCE.md), and [documentation audit](docs/API_DOC_AUDIT_42926.md)
- [Archived build 42594 reference](docs/API_REFERENCE_42594.md) and [historical API failures](docs/API_FINDINGS.md)
- [Lofting](docs/LOFTING.md), [assemblies](docs/ASSEMBLIES.md), and [later jet lessons](docs/JET_EVOLUTION.md)
- [Verification methods](docs/VERIFICATION.md) and [background console](docs/BACKGROUND_CONSOLE.md)
- [Public audit](docs/PUBLIC_AUDIT.md), [verification receipt](docs/RELEASE_VERIFICATION.md), and [asset notices](THIRD_PARTY_NOTICES.md)

Public sharing does not make these preliminary examples production-qualified.
Native results in reports refer to recorded revisions. Fresh offline checks verify recipes and packaging.
The B52 derivative has a GPL-2.0 license. Other bundled third-party notices retain their original scope.
