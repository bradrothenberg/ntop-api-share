# KestrelSAT modeling skill audit

The repository bundles the reusable assembly skill and refreshes the CSG skill from the supplied KestrelSAT work. Both use the current build 42926 API reference. Recorded native results retain their original build labels.

## Source coverage

The source workspace was read only. The [source receipt](evidence/kestrelsat-skill-sources.json) records file hashes and comparison results without local absolute paths.

| Supplied source | Public destination |
|---|---|
| `skills/ntop-assembly-modeling` | [Assembly skill](../.agents/skills/ntop-assembly-modeling/SKILL.md), contracts, pilot, recorded receipt, and GUI guidance |
| `skills/ntop-csg-modeling` | [CSG skill](../.agents/skills/ntop-csg-modeling/SKILL.md) and [geometry robustness](../.agents/skills/ntop-csg-modeling/references/geometry-robustness.md) |
| KestrelSAT modular `ntop-custom-assembly` skill | Shared definitions, placements, input contracts, imported snapshots, and separate geometry/performance evidence |
| KestrelSAT CSG `ntop-custom-assembly` skill and references | Later CSG lessons, native interface details, pilot evidence, and [fixed-feature resizing](../.agents/skills/ntop-assembly-modeling/references/fixed-feature-resizing.md) |

The modular and CSG custom-assembly skills describe successive versions of the same workflow. Their portable lessons are consolidated into the assembly and CSG skills. The source inventory found no additional standalone skill under KestrelSAT.

The public copy replaces workspace links with bundled references and retains current unit and input-repair guidance. It includes the existing corner example and a generic source-only assembly pilot. The full satellite assembly, private helpers, generated native pilot files, and raw process transcripts remain outside this package.

## Evidence retained

The pilot uses one drilled, chamfered part and two custom calls. A dimensioned Width input changes the span while the bore and thickness remain fixed. It embeds the complete saved part definition and uses the identity returned by native readback.

The recorded build 42594 CLI run passed 80 field checks at widths of 10 and 14 mm. Its maximum field error was approximately 0.000000295451 mm. The source receipt records one post-save cleanup assertion. Subsequent independent readbacks and evaluations passed. See the [pilot reference](../.agents/skills/ntop-assembly-modeling/references/generic-pilot.md) for the measured scope.

The public pilot script matches the supplied reusable script. Its construction syntax trees also match the original native example. The retained numeric receipt matches the source, including all shared fields from the original native run.

These results establish the recorded CLI extended-recipe contract. They do not establish live API input/output promotion, native build 42926 compatibility, GUI behavior, or a production speedup.

The resizing reference separates the earlier map checks from replacement CSG geometry. Protected intervals, clamps, and transform order must be rechecked against the delivered parts. The generic Width pilot does not implement the satellite's XYZ coordinate map.

## Package checks

The offline pilot validates complete recipes, reference owners, input defaults, implicit output contracts, custom-call identities, and 40 planned probes per width. It performs no native execution. The GitHub workflow runs this check on each push and pull request.

Skill validation, repository tests, demo smoke checks, and a public-content/link audit apply to the isolated staged snapshot. No existing nTop session is used for this import.

All four bundled skills validate. All eleven demo smoke checks and all 104 tests pass without skips. The corner manifest and saved-graph checks pass. The public audit reports zero findings across 998 files, 1,104 local links, and 20 native containers. These are offline package checks, not new native execution.
