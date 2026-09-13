# Build 42926 documentation audit

Audited on 13 September 2026 against the user-supplied September 10 demo package.
Its README identifies **Notebook API Build 0910, nTop 6.1.0-rc, build 42926**.
The five previously recorded package files still match their recorded SHA-256 values.
The additional `.claude/skills/SKILL.md` is byte-identical to `.claude/skills/ntop-modeling/SKILL.md`.
The supplied package was read-only throughout this audit.

The earlier public update already included this build, but its main reference remained a build 42594 manual.
New authoring now starts at [the current 31-method reference](API_REFERENCE.md).
The [older manual](API_REFERENCE_42594.md) and [findings](API_FINDINGS.md) remain explicitly historical.

## Coverage

| Area | Audit and change |
|---|---|
| Complete method surface | All 31 recorded signatures, exact keyword names, return types, and context rules are in the current reference |
| Six value types | Current support is separated from the four-type recorded probe and the supplied point/vector evidence |
| Unit handling | Explicit setter units, display readback, bare-number unit assignment, angle units, and field-input asymmetry are documented |
| Variables and properties | Rename versus wrapping, computed-value readback, property-read limits, fan-out, and method-specific wrapper traversal are documented |
| Repair and movement | Current clearing behavior and cross-section top-level movement replace blanket older restrictions |
| Lists | Native list processing, typed seeding, literal-list growth, overload conflicts, and integer count properties are documented |
| Evaluation | All documented build and pause states are listed; unknown state semantics remain unverified |
| Files and custom blocks | Recipe input merging, notebook identity changes, recipe_only, and active-custom-block export context are documented |
| Transport | Build 42926 TCP is the current route; the older window-message bridge remains available |
| Bundled skills | Notebook API, native CSG, and engineering HTML skills now route to the current contract and preserve evidence scope |
| Demo guidance | All eleven local agent files were reviewed; their shared-skill routing remains valid. Historical I6, Astra, and Jet notes now link to the current contract |
| Setup and verification | Setup lists all eleven demos. The optional probe's four-type limit is explicit. Meshing settings remain specific to recorded cases |
| Helpers and examples | The existing feature checker, state dump, identifier lookup, probe, and TCP receipts were reviewed. Full-catalog advice was corrected; no native helper execution is claimed |
| Recorded reports and receipts | Original geometry, timing, solver results, and build labels retain their source revisions |

The [machine-readable audit](evidence/api-42926-doc-audit.json) records source identities, reviewed guidance paths, and evidence classifications.
Unrelated marine revision work is outside this focused documentation commit.

## Source conflicts resolved

| Conflicting source statements | Resolution used here |
|---|---|
| Getter docstring says point/vector return two items; supplied skill says three | Document three-component values as supplied-package behavior and flag the docstring error. No new point/vector probe was run |
| A later skill paragraph says only three types are readable | Use the six-type contract stated by the package README, the skill's main type section, and getter docstring |
| `tools/send.py` says TCP requires an open console window; README says process startup | Use the README's process-start lifetime as a supplier claim. Do not infer window or notebook identity from the port |
| Skill says nested IDs stop resolving; several docstrings explicitly accept nested IDs | Document method-specific reachability. Moving still requires top-level IDs; do not infer universal nested access |
| README describes unit rewriting as preserving quantity | Distinguish dimensioned values from bare numbers, as the recorded setter docstring does |
| Supplier clearing tests report success; propeller mesh-wrapper clear failed | Preserve both scopes. Supported reference repair is useful; a wrapper's occupied computed Input remains a separate case |
| A successful default-input clear sounds like an empty input | The docstring says an untouched default can remain. Inspect before reconnecting |
| README's example wraps an existing typed variable; skill warns that this creates another wrapper | Use rename_variable for typed variables and add_variable for computed blocks |
| Old manual says no recipe workaround can make a model automatable | Dedicated live input/output methods remain absent, but input merging is documented. Full Automate contract behavior needs its own native test |

The supplied tool can return partial output after a timeout. This repository retains its receipt-based transport and never treats partial output as completion.
Supplier script paths and helper names were adapted to this checkout. The audit did not import supplier scripts, private configuration, or application binaries.

## Verification scope

Source comparisons and signature checks are offline checks.
The source manifest binds supplied files, while the surface and type records bind earlier native observations.
The optional probe covers real, integer, bool, and text. It is not a complete conformance test for the 31 methods.
No nTop process was launched or controlled during this audit.

Review all methods and dimensions on a different build before claiming compatibility.
Performance improvements need a controlled measurement; the newer documentation alone does not establish a speedup.
Historical report values and meshes were not regenerated by this documentation update.

## Offline validation results

- All 31 current signatures match the recorded method surface; all six current Python examples parse.
- All three bundled skills pass the skill validator.
- A subsequent [KestrelSAT skill import](KESTRELSAT_SKILL_AUDIT.md) adds the assembly skill and refreshes CSG guidance. The three-skill count above describes this earlier audit.
- All eleven demo smoke checks and all 104 tests pass in a separate staged checkout, without skips.
- The KestrelSAT manifest and saved-graph check passes.
- The public-payload audit reports zero findings across 989 files, 1,074 local links, and 20 native containers. Final documentation-only changes also receive a delta scan.
