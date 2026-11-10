# Local runtime

## Existing installation

Use the configured Unlinked checkout. Read its `AGENTS.md` and
`LOCAL_SETUP.md`. Health checks do not require changing model data:

- Backend: `http://localhost:3000/api/health`
- Dashboard: `http://localhost:3001/dashboard/health`
- Current gear publication: `http://localhost:3001/gear/config`

If only the dashboard stopped:

```powershell
cd "<unlinked-checkout>"
.\scripts\start-dashboard.ps1
```

If the backend also stopped:

```powershell
cd "<unlinked-checkout>"
.\scripts\start-local.ps1
```

The existing launcher starts Docker Desktop if needed, uses Compose, waits for
health, and starts Node in a hidden window. It preserves PostgreSQL's volume.
`stop-local.ps1` stops services without removing data. Never use `down -v` as a
routine restart. Inspect container status and bounded logs if startup fails.

Open the relevant URL after health succeeds, using the app's `open_in_codex`
browser target when available. A queued open response is not proof of rendering.
The gear URL is `/gear.html`; the four-bar view is `/`. Read the current
publication instead of assuming that the latest geometry is still R08.

## New installation

Clone `https://github.com/CosmicFrontierLabs/unlinked.git` into the user's chosen
workspace. Inspect its current README, Compose files, and source revision first.
The startup helpers and mechanism dashboard in the reference checkout are local
additions; do not assume they exist upstream.

Use the current upstream build/image procedure. Bind published backend and
database ports to loopback for local development. Use a persistent database
volume, an ignored `.env`, a generated persistent session secret, and the supported
development login setting. Do not print secrets or copy a reference `.env`.
Keep OAuth and CSRF behavior intact. A production deployment is a separate task.

The reference checkout uses `Dockerfile.local` and `compose.local.yml`.
Source edits do not change the already-running image; rebuild when needed.
Check that the actual running image supports the desired blocks and options.
Do not increase quotas or solver limits merely to hide repeated failed runs.

## Runtime checks

Verify health, login, upload, a short simulation, and result retrieval. For a
new installation, confirm that a stop/start preserves the example model and run.
Do not restart a healthy shared service solely to test a new model.

The included helper uses Python's standard library. If uv's default cache is
unwritable in a restricted session, use `uv --cache-dir <writable-cache> run ...`.
This changes the cache location, not Python or application permissions.
