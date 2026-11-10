# Model authoring and API

## Source of truth

In the reference checkout, inspect these files for the running version:

- `shared/src/simulation.rs`: request/result types.
- `crates/unlinked-sim/src/lib.rs`: solver options and trace format.
- `crates/unlinked-sim/src/import.rs`, `matlab_function.rs`, and `crates/unlinked-matlab`: supported semantics.
- `backend/src/handlers/simulations.rs`: lifecycle, bounds, and retention.
- `examples/`: small native MDL models and initialization scripts.
- `models/four_bar/build_model.py`: scalar equation graph with virtual subsystems.
- `models/landing_gear_767/motion_v4/`: coupled dynamics, source hashes, checks, and load export.

The helper follows the API verified on 2026-10-19. If schemas differ, inspect
current types and adapt the helper. Do not silently reinterpret returned fields.

## HTTP contract

Use a cookie jar for local `GET /api/auth/dev-login`. Mutations must send an
`Origin` matching the server's public origin. Keep `localhost` and `127.0.0.1`
consistent. Do not disable same-origin checks to repair a dashboard proxy.

| Operation | Route |
| --- | --- |
| List organizations | `GET /api/orgs` |
| Create organization | `POST /api/orgs` with `name` |
| List all accessible projects | `GET /api/projects` |
| Create project | `POST /api/orgs/{org_id}/projects` with `name`, `description` |
| List files | `GET /api/projects/{project_id}/files` |
| Upload new file/version | `POST /api/projects/{project_id}/files?path=...&message=...`, raw bytes, `application/octet-stream` |
| Read file bytes | `GET /api/projects/{project_id}/files/{file_id}/content` |
| Run pinned model | `POST /api/files/{file_id}/simulations` |
| List runs | `GET /api/files/{file_id}/simulations` |
| Retrieve result | `GET /api/simulations/{run_id}` |

Example request, with actual IDs and versions substituted:

```json
{
  "version": 1,
  "init_script": {"file_id": "ACTUAL_SCRIPT_UUID", "version": 1},
  "options": {"start": 0, "stop": 0.1, "step": 0.01, "solver": "rk4"},
  "workspace": {"rate": "3"}
}
```

Workspace values are expression strings. Explicit overrides take precedence
over the init script. The `.m` file must be in the same project. `inputs` is a
separate map from root Inport block IDs to constant expression strings.
`output_signals` belongs inside `options` and contains stable signal IDs.

The HTTP run call returns a persisted `SimulationResult`, normally after completion.
Read `run.status` and `run.error`; HTTP 200 alone does not establish success.
`trace.time` is a sample array. `trace.signals` maps IDs to equally sized arrays.
The top-level `signals` array maps each ID to its recorded name. Do not select
signals by display order or guess IDs from their labels.

The inspected server caps output at 25,001 samples and retains about 20 runs
per user. Export important traces before sweeps. On an ambiguous POST timeout,
inspect runs for that file and match the pinned request before retrying. The
helper writes `pending.json` before submission and never retries POST automatically.

## Helper commands

Run these from the installed skill folder. Replace paths and IDs with actual values.
`project` reuses an exact name match and creates only if absent. Duplicate name
matches fail. `run` uploads a changed file as a new immutable version and reuses
identical bytes. Output directories must be new, so old runs are not overwritten.

```powershell
uv run scripts/unlinked.py health
uv run scripts/unlinked.py project --org "Unlinked skill examples" --name "Decay pilot"
uv run scripts/unlinked.py archive-history --out "D:\work\saved-unlinked-history"
uv run scripts/unlinked.py run --project-id "ACTUAL_PROJECT_UUID" --model assets/decay.mdl --init assets/decay_params.m --stop 0.1 --step 0.01 --out "D:\work\decay-pilot"
uv run scripts/unlinked.py check "D:\work\decay-pilot\result.json"
```

For a changed parameter, supply `--workspace path/to/overrides.json` containing
an object such as `{"rate":"3"}`. Use `--inputs` for root Inports and repeat
`--signal ACTUAL_ID` to select outputs. The default solver is RK4; choose
`--solver rk45` only with a suitable accuracy/work-budget review.

`archive-history` saves all currently accessible model run results. It is a
read-only export, not a database backup. Keep the PostgreSQL volume separately.
No helper command deletes server records, models, or local output directories.

## Mechanical validation

Separate kinematic closure from dynamic equations. State the constrained DOFs,
joint idealizations, input drive law, and mass/inertia basis. Use SI internally.
Expose forces, velocities, accelerations, energies, and constraint residuals as
needed to verify the claimed behavior.

- Four-bar closure must hold across the requested travel, not just the initial pose.
  Check square-root domains, fixed assembly branch, and toggle determinants.
  Reject invalid geometry with a useful explanation. Do not clamp a negative
  radicand to make impossible geometry appear to work.
- For retraction, include actuator force limits and appropriate deceleration and
  hold dynamics. Measure endpoint error and velocity. Camera animation or angle
  clipping does not fix dynamic overshoot or establish a mechanical lock.
- For touchdown, define sprung/unsprung masses, strut force law, and separate
  contact loads. Keep any rig-positioning transition distinct from solved motion.
- Compare force/moment or generalized residuals, energy/work balance, and a
  smaller time step. Choose tolerances from the model and numerical resolution.
- A finite trace is not proof of correct physics. Use an analytical case or an
  independent calculation for at least one relevant limiting case.

For the pilot, use the effective `rate` and `x0` in `x0*exp(-rate*(t-start))`.
Its fixed stable IDs are `1` (state), `2` (derivative), and `3` (state output).
Check it with `uv run scripts/verify_decay.py <result.json> --rate 2 --x0 1.5`.
Use the actual override value for `--rate` if changed. The dimensionless error
limit is an explicit test criterion, not a hardware accuracy claim.
