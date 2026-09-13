# Background Notebook API commands

The prototype binds `notebook` inside nTop's Python Console. Build 42594 used the window-message bridge below.
Build 42926 also documents a loopback TCP console, described later on this page. nTop Automate does not expose this Notebook API.

The bundled scripts/ntop_console_post.ps1 stages a UTF-8 command and posts WM_CHAR and Return to one
verified nTop Python Console. It does not activate the window or send keys to the foreground app.
This behavior was measured in the source work on 9 September 2026. Recheck it on a different build.

Select a task-owned process, check its creation time and current notebook, and open its Python Console once.
Provide the exact process ID and a fresh, task-local script path. Never select the first available console.

```powershell
$apiCommand = Get-Content -LiteralPath $apiCommandFile -Raw -Encoding utf8
& .\scripts\ntop_console_post.ps1 -ProcessId $ntopProcessId -ScriptPath $dispatchFile -Command $apiCommand -NoWait
```

The variables above must be set from the current task. The printed completion marker contains OK or a traceback.
Check it before sending another command. An early py> prompt or a pre-existing export is not completion evidence.
Do not overwrite foreign input. If discovery cannot find the verified console, inspect the setup and permissions.
Keep any manual console-opening step separate from routine background dispatch.

## Optional build 42926 TCP transport

The supplied package documents a listener on 127.0.0.1:2323 from nTop process startup.
No console window is required according to that package. A port response does not identify the open notebook.
This repo's transport is tested against a mock socket; no live TCP call was made during the public update.

Select a process that belongs to your task and confirm it holds the intended scratch notebook.
Set `$ntopProcessId` explicitly from that selection. Create its identity record locally:

```powershell
$ntopSelectedProcess = Get-Process -Id $ntopProcessId
@{pid=$ntopSelectedProcess.Id;exe=$ntopSelectedProcess.Path;start_utc_ticks=$ntopSelectedProcess.StartTime.ToUniversalTime().Ticks.ToString()} | ConvertTo-Json | Set-Content -LiteralPath '.local/session.json' -Encoding utf8
uv run --locked python scripts/ntop_tcp.py --session .local/session.json --file .local/command.py --run-dir .local/tcp-run-001 --timeout 30
```

Use a fresh run directory each time. The helper verifies the listener's PID, executable, and creation time before sending.
It retains `command.py`, `runner.py`, `transcript.txt`, `dispatch.json`, and an in-nTop `completion.json`.
A completed transport receipt is separate from block build state and geometric verification.

A timeout or connection loss after sending has an unknown outcome. Do not repeat the command.
Inspect its completion file later. The helper blocks another send in this checkout while the prior receipt is unresolved.
Do not send concurrently from other clients or checkouts. Do not forward this unauthenticated prototype port.
The existing background bridge prints its exact marker path, which can include `._done.txt`; use that returned path.
