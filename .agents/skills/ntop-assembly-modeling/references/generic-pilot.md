# Generic custom part and two-instance assembly pilot

The [portable generator](../scripts/run_pilot.py) uses only the Python standard library. It imports no source CAD, mesh, full product assembly, private helper, or binary template.

The retained construction builders are unchanged from the recorded 80-check native pilot. The adapted runner adds an offline mode, requires a fresh output directory, and records bounded timeouts. It has not been newly executed natively as part of this skill packaging.

## Interface and geometry

| Item | Contract |
|---|---|
| Part input | `Width`, real length, default 0.010 m |
| Stock | Width by 8 mm by 2 mm |
| Corner cuts | Two continuous 0.5 mm front chamfer planes |
| Bore | Fixed 2 mm diameter, center X 3/Y 4 mm |
| Part output | One native implicit body |
| Assembly input | The same Width type, dimension, and default |
| Imported definitions | One complete saved part recipe |
| Custom calls | Two, to exercise the imported input contract |
| Placement B | Translation of 12 mm along Y |
| Assembly output | An implicit union containing both separate solids |

The pilot deliberately tests two calls to one definition. In a production assembly with identical input values, reuse one evaluated part variable for both placements. The separate `Part A` and `Part B` variables remain available; a union output is not the preferred sole GUI selection boundary.

## Run source checks

From the workspace root, use a new output directory:

```powershell
uv run python .agents/skills/ntop-assembly-modeling/scripts/run_pilot.py --offline --out .local/assembly-pilot-offline
```

This writes a complete part recipe, an authored assembly recipe, a validation recipe, width-input files, and an offline receipt. It checks reference closure, unique node IDs, input defaults, implicit outputs, imported-definition registration, and 40 planned probes per width.

Offline custom identities are provisional. Native save and readback can change the part identity. The offline receipt explicitly records that no native execution or saved custom-identity verification occurred.

## Run the native contract pilot

Use a matching licensed native CLI and another fresh output directory:

```powershell
uv run python .agents/skills/ntop-assembly-modeling/scripts/run_pilot.py --ntopcl "C:\path\to\licensed-build\ntopcl.exe" --out .local/assembly-pilot-native
```

The script performs `convert --ext` and `exportjson --ext`, reads the actual saved part identity, embeds that complete part into the assembly, and checks both saved implicit outputs. It then evaluates 40 field probes at Width 10 mm and 14 mm, for 80 native checks total. Finally it reopens and evaluates the actual assembly.

Each native command has a 45-second bound and records stdout, stderr, exit status, and elapsed time. A timeout stops the owned CLI process, retains an incomplete receipt, and is not automatically retried. Generated receipts can contain the user's local executable path; keep them in ignored output until audited for sharing.

The recorded debug build sometimes asserted during cleanup after a successful conversion save. The runner recognizes only the recorded `DummyListener` post-save signature, preserves the failed exit receipt, and requires independent readback and geometry checks. Other errors fail. This is a narrow historical workaround, not permission to ignore arbitrary nonzero exits.

## Native checks and recorded result

Both widths check the moving far wall, a station that changes from outside to inside, fixed bore walls at X 2 and X 4 mm, fixed plate faces at Z 0 and Z 2 mm, and both chamfers. Nearby points check material and void signs. Do not infer global signed-distance behavior from these local checks.

The [sanitized recorded receipt](recorded-pilot.json) retains all 80 measured values, the exact field tolerance, the native build identity, and the source-builder AST hash. All 80 checks passed on build 42594. The maximum error was 0.000000295451 mm with a 0.00001 mm check tolerance.

The original `part_convert` command reported the recognized post-save cleanup assertion. Its separate readback, assembly conversion/readback, validation conversion, two width evaluations, and final assembly reopen completed successfully. The public excerpt omits personal paths, raw process transcripts, and native binaries.

## Limits and GUI finish

This proves the recorded CLI extended-recipe contract, not live Notebook API marking, GUI rendering, colors, or a speedup. Recheck another build rather than assuming compatibility.

Generated native files are working contract fixtures. Before presenting a deliverable, show the separate native results, hide construction, apply a stable family color, and collapse the saved blocks and sections using the measured native UI or repository helper. Preserve the working source and verify the finished copy. No generated `.ntop` binary is distributed in this skill.
