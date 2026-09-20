---
name: ntop-orchestrate
description: "Submit prepared nTop notebooks to an Orchestrate service with ntopcl --remote, prepare NDJSON tasks, retrieve artifacts, and verify remote sweep results."
---

# nTop Orchestrate

This skill records a prototype remote workflow observed with build 42437 in August 2026.
Its schema and downloader findings are historical. Confirm the deployed API and CLI before use.
For local headless execution, use [run-ntop-automate](../run-ntop-automate/SKILL.md).

## Deployment contract

Obtain the endpoint, authenticated identity, runtime token, supported build, and output policy from the deployment owner.
Keep these settings in ignored local configuration or a secret store.
No endpoint, default token, monitoring host, or licensed application is bundled here.
Check that `ntopcl --help` exposes `--remote`; do not assume a released CLI includes it.

## Prepare the notebook

Generate its templates. Confirm input names, types, units, and exported artifacts with one local case.
The recorded workers collected files from the working directory and did not create export subdirectories.
For that deployment, use relative export names and set the declared output-directory input to `./`.
Do not rewrite imported `file_path` inputs to `./`; stage their files through the supported service mechanism.
Use the [DOE input generator](../ntop-doe-sweep/scripts/prepare_sweep.py) to create complete NDJSON documents.
Each line represents one task, including the `inputs` array and its containing object.

## Recorded action schema

| Action | Additional fields | Recorded behavior |
|---|---|---|
| `create_job` | `notebook` | Creates an open job |
| `add_task` | `job_id`, `params` or `params_file` | Adds one or more input sets |
| `submit` | `notebook`, `params` or `params_file` | Creates tasks and seals the job |
| `wait` | `job_id`, output options for that build | Historical downloader limitations below |
| `cancel` | `job_id` or `task_id` | Cancels the selected scope |

Common fields were `action`, `endpoint`, `token`, and `user_id`.
Construct the schema locally from the current service contract. Never commit the populated token.
Use `.json` for one input document and `.ndjson` for multiple documents where supported.

```text
ntopcl --remote .local/orchestrate/submit.json
```

Record the returned job and task IDs. The observed service used ULID job IDs and UUID task IDs.
These IDs were not interchangeable. Submission returned after queueing; it did not establish completion.
Do not resubmit after a lost response until the original outcome is reconciled.

## Retrieve and verify

The recorded `wait` downloader reported zero downloads even when server artifacts existed.
Its task-list route omitted artifact URLs. The per-task detail route supplied them:

```text
GET /api/v1/jobs/<job_id>
GET /api/v1/jobs/<job_id>/tasks
GET /api/v1/tasks/<task_id>
```

Use a downloader matched to the current service. Do not forward service Authorization headers to a different storage origin.
Resolve exported filenames inside the owned result directory and reject traversal paths.
Retain task inputs, output JSON, logs, export hashes, and status receipts.
Do not skip a previous download until size or hash verification establishes completeness.

Confirm task counts, terminal status, expected files, and meaningful output changes across the sweep.
Equal file sizes alone do not imply identical geometry. An output can also be legitimately insensitive to a varied input.
Use a physical relation appropriate to the model, with units and density stated when mass is involved.
Validate one task before scaling. This package contains guidance and input preparation, not a live service or cluster-specific downloader.
