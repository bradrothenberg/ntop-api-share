---
name: ntop-automate
description: "Prepare JSON inputs and outputs for nTop Automate, including single runs, iterative values arrays, parameter grids, and container or batch execution."
---

# nTop Automate JSON workflows

Use this skill to parameterize a prepared notebook. Use [run-ntop-automate](../run-ntop-automate/SKILL.md) for execution and diagnostics.
Promote each variable to a notebook Input and each returned value to an Output.
Export blocks write geometry files; output JSON alone does not contain those files.

## Single run

```text
ntopcl -t model.ntop
ntopcl -j input.json -o output.json model.ntop -v 2
```

Read the generated templates first. Names and types must match exactly.
Read [JSON I/O](references/json-io.md) when preparing inputs or interpreting returned values.
Retain units, descriptions, and enum encodings from the selected build's template.
Use JSON for points, vectors, booleans, enums, and paths. Inline `-i` support is narrower and order-dependent.

## Iterative values and grids

The recorded schema supports `values` arrays. Varying arrays have equal length; a singleton can supply a constant.
Confirm this behavior with a small run on the installed version before a larger study.
Generate a separate JSON per point when isolation, retries, or separate logs matter.
A factorial grid must first enumerate all combinations; paired arrays alone do not create a Cartesian product.

The [DOE skill](../ntop-doe-sweep/SKILL.md) includes a template-based input generator and a run-record contract.
The generator prepares inputs only. It does not launch paid compute or establish native success.

## Containers and batch systems

Use a version-pinned, licensed image or installation supplied by the deployment owner.
Record the image digest, notebook hash, command version, and input hash.
Mount or stage the notebook, imported inputs, and output directory explicitly.
Inject credentials at runtime. Do not include them in image layers or shared job specifications.
Verify one complete run, including returned geometry, before increasing the task count.

Flags such as `-p`, `--logfile`, `--license`, and `--trustnotebook` depend on the installed CLI.
Use its help and generated schema. Do not assume the prototype Notebook API and CLI expose identical operations.
