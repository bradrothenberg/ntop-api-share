---
name: ntop-doe-sweep
description: "Design reproducible nTop parameter studies, prepare typed input grids, size local or cloud execution from measurements, and diagnose failed design points."
---

# nTop design-of-experiments sweeps

Use [run-ntop-automate](../run-ntop-automate/SKILL.md) for execution mechanics and [Orchestrate](../ntop-orchestrate/SKILL.md) for its remote service.
This skill supplies the study contract. It does not include a cloud fleet provisioner.

## Freeze the study identity

Record the notebook hash and saved version, executable version, sampler and sampler version, seed, sample count, variable order, bounds, and units.
Store the actual input table. A seed alone does not reproduce points across different Latin-hypercube implementations.
For cross-platform comparisons, use identical stored points and compare a small sample before dispatch.

## Prepare a small typed grid

From the repository root:

```text
uv run python .agents/skills/ntop-doe-sweep/scripts/prepare_sweep.py --template input_template.json --out .local/study/inputs.ndjson --sweep Radius=200,350,500 --set Export_Path=./
```

The [generator](scripts/prepare_sweep.py) writes one full input document per line.
It preserves unswept values and imported-file inputs. Set the exact output-directory input explicitly.
Repeated `--sweep` or `--linspace` options form a full factorial; `--zip` pairs equal-length axes.
Use semicolons between point or vector values, for example `Position=0,0,0;1,0,0`.
The generator does not perform Latin-hypercube sampling or validate native block behavior.

## Run records

Use one directory per design point and one subdirectory per attempt:

```text
.local/study/run_001/attempt_001/
  input.json
  output.json
  run.log
  receipt.json
  exports/
```

Keep input files immutable. Store attempts, elapsed time, return code, expected and actual exports, file sizes, and output validation results.
For local runs, set output paths separately for each attempt. Do not send every point to the same export directory.
Check parseability and semantic completeness, not only file presence. Preserve failed cases.

## Scale from measurements

1. Validate the schema and a small preparation example.
2. Run one representative native case. Measure runtime, peak memory, output size, and license use.
3. Run a small fixed study and inspect successful and failed points.
4. Increase only the study scale or measured concurrency. Keep geometry, sampling, and acceptance rules fixed.

Account for slow valid points when setting timeouts. Check CPU oversubscription and memory under concurrent runs.
For queue workers, keep the retry budget within the lease or renew it. Use task identities to prevent duplicate result acceptance.
Resume from validated receipts, not an output file that could be partial.
Use a unique object-storage prefix. Preserve prior studies and all attempt logs.

## Analyze failures and comparisons

Rerun the same stored inputs to distinguish transient failure from geometry-dependent failure.
Inspect warnings and cluster failed points by design variable. Do not report a historical failure percentage as a forecast.
Compare platforms using the same input and notebook hashes, output contracts, geometry measurements, and solver settings.
Report exclusions and incomplete points alongside the successful results.
