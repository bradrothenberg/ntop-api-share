---
name: fun3d-gcp
description: "Deploy and monitor authorized FUN3D and refine workloads on GCP, using configured instances, IAP access, durable results, measured resource sizing, and recovery receipts."
---

# FUN3D and refine on GCP

Use [FUN3D CFD runner](../fun3d-cfd-runner/SKILL.md) for physics, namelists, convergence, and adaptation.
This skill adapts earlier deployments without their accounts, hosts, snapshots, buckets, or pricing assumptions.

## Configuration

Record project, zone, instance identity, service account, image/snapshot identity, solver installation, result prefix, and approved resource scope.
Inspect current instance state and active jobs before changing lifecycle or metadata.
Use the user's authorized authentication method. Where the deployment uses IAP, pass `--tunnel-through-iap` for SSH and SCP.
An expired interactive session needs reauthentication. It does not justify creating a persistent service-account key.
For unattended execution, use the organization's approved workload identity or impersonation method.

Example PowerShell, with values supplied through the current environment:

```powershell
gcloud compute instances describe $env:CFD_INSTANCE --project=$env:GCP_PROJECT --zone=$env:GCP_ZONE
gcloud compute ssh $env:CFD_INSTANCE --project=$env:GCP_PROJECT --zone=$env:GCP_ZONE --tunnel-through-iap
```

## Execution and transfer

Stage inputs under a unique case path. Check source and destination hashes after transfer.
Use object storage for large transfers only when the instance identity has the required permissions.
Do not assume read access implies write access.
Verify the mesh format before conversion; an already little-endian mesh needs no endian swap.
Run the solver through a job driver that persists after SSH disconnects.
Record the job identity, PID, start time, model hash, mesh hash, command, and output validation state.

The source deployment encountered MPS failures on larger two-GPU cases.
It then used one rank per GPU without MPS. This is a recorded remedy, not a universal size threshold.
Check GPU assignment, MPI compatibility, peak memory, and progress on the actual machine.
Do not restart shared GPU services or kill unrelated solver processes.

## CPU adaptation and lifecycle

Run refine on resources selected from measured memory and throughput.
CPU adaptation may not need the GPU instance. Compare transfer cost and concurrent-case throughput before separating stages.
Use task-owned instances and a documented shutdown policy for new resources.
Preserve existing startup metadata and other users' jobs.
Before stopping or deleting a transient resource, verify durable results and confirm its task ownership and lifecycle scope.
Do not delete an existing instance or disk merely because a historical script did so.

## Recovery

For spot preemption or lost SSH, inspect the remote run receipt before relaunching.
Resume only from validated checkpoints or complete outputs. An existing VTK file can be truncated.
Check disk space, file growth, source/destination sizes, hashes, and log progress.
Clean only task-owned temporary files after the retained results are verified.
Measure current costs and quotas if resource selection requires them; historical prices and capacity are not forecasts.
