# Background Notebook API commands

The prototype binds `notebook` inside nTop's Python Console. For build 42926, use the [TCP route below](#build-42926-tcp-transport).
The [current method reference](API_REFERENCE.md) describes the commands carried by either transport.
TCP reaches the GUI process; nTop Automate does not expose this Notebook API.

## Launch a separate task-owned process

For new modeling work, launch the exact intended licensed custom build directly from the host shell and use the Notebook API in its task-owned scratch notebook.
Computer Use is not required for process launch or API authoring. Preserve the user's existing windows and notebooks.
Do not launch through a `.ntop` file association, an unverified shortcut, or whichever `ntop.exe` happens to be on PATH: those can select a different build or existing session.

After `scripts/bootstrap.ps1` has set `NTOP_EXE` and `NTOP_PYSCRIPTS` in the current PowerShell session:

```powershell
$ntopExistingProcesses = @(Get-Process -Name ntop -ErrorAction SilentlyContinue | Select-Object Id, Path, StartTime, MainWindowTitle)
$ntopExecutable = (Resolve-Path -LiteralPath $env:NTOP_EXE).Path
$ntopTaskProcess = Start-Process -FilePath $ntopExecutable -WorkingDirectory (Split-Path -Parent $ntopExecutable) -PassThru
$ntopProcessId = $ntopTaskProcess.Id
Get-Process -Id $ntopProcessId | Select-Object Id, Path, StartTime, MainWindowTitle
```

Verify that the returned process remains running, has the selected executable path and a new creation time, and is separate from the recorded existing processes.
If the shell runs under an isolated account or desktop, use the host's supported desktop execution route for this direct launch, with any required host approval. A process on an isolated desktop does not establish that the user's nTop window opened.
If startup hands off to another process or exits, do not assume the original PID identifies a new session. Inspect the actual process before proceeding.
Use a blank task-owned notebook. Never use `new_notebook` or `open_notebook` on a user's existing session to make room; both discard unsaved work without prompts.
Do not save a recovery copy and take over that session as the default setup workflow.

For TCP, inspect listener ownership before sending even the initial API probe:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 2323 | Select-Object LocalAddress, LocalPort, OwningProcess
```

Require exactly one loopback listener owned by the verified task process. A second window, a successful launch, or a responding port does not establish attachment to that process.
If port 2323 still belongs to an existing session, multiple owners appear, or the new process has no listener, do not send commands to that endpoint and do not terminate the user's process to free the port.
Use a separately addressable endpoint only when the installed build documents and verifies it, or the verified process-specific legacy bridge when its console is available. Otherwise report the attachment limitation and continue offline recipe work.
The client's `--port` option selects a destination; it does not configure nTop's listening port. Do not invent a server-port flag.

After host ownership checks pass, create the local identity record described below and make the first dispatch read-only.
Inspect `os.getpid()`, `notebook.list_blocks()`, `notebook.list_variables()`, and `notebook.current_open_custom_block()` in that interpreter; compare the PID and notebook contents with the intended scratch session.
An empty variable list alone is insufficient to identify a notebook. Confirm that no user document was restored or redirected into the selected process before authoring or saving to the task's output folder.
Retain process identity and probe receipts locally. Recheck ownership before each dispatch with the bundled helper.

Evidence scope: direct process launch is the preferred workflow. This procedure does not certify simultaneous TCP routing for multiple nTop windows. Validate routing on the installed build.

## Multiple agents and ports

Prefer one agent, one nTop process, one notebook, and one distinct loopback server listener port for each independently active modeling session, when the installed build supports configuring those ports.
Record the agent owner, executable, PID, creation time, endpoint, and notebook together. Different client source ports, output folders, or socket connections do not create separate nTop notebook sessions.

The supplied build 42926 README and `tools/send.py` document `127.0.0.1:2323`. A read-only check of the exact supplied `ntop.exe --help` on 14 September 2026 returned the Automate command options and no Python console server-port option.
No supported console server-port configuration was found in those sources. This is a limit of the inspected documentation and help, not proof that no internal configuration exists. Confirm any server setting with the build maintainer before relying on it.
The shared client's `--port` argument only changes where it connects; it does not start, rebind, or configure a listener. Do not present distinct client port arguments as verified independent nTop sessions.

When distinct server endpoints cannot be verified, serialize native authoring through one assigned session owner, or use a verified process-specific transport. Other agents can prepare recipes and review artifacts offline.
Do not allow multiple agents or clients to mutate the same live notebook concurrently, even through separate sockets or ports: the interpreter's `notebook` is shared within that process.
The helper's pending receipt lock covers this checkout only. It is not a cross-checkout or machine-wide agent coordination service.

The shared TCP helper retains its conservative requirement for exactly one loopback listener at the destination port. It also sends a nonce-tagged, read-only `os.getpid()` probe over the connected socket, requires exactly one matching response, and sends the notebook command only on that same socket after another host ownership check.
A mismatching or unconfirmed PID closes the connection without sending notebook code. This detects a wrong destination; it does not instruct the operating system to route a connection to an arbitrary PID or make ambiguous listener ownership acceptable.
This helper change is covered by offline socket tests. It does not certify simultaneous native TCP sessions on different ports.

## Legacy window-message bridge

Build 42594 used this route. It remains available when an installed build has no TCP listener.

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

## Build 42926 TCP transport

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

Use a fresh run directory each time. The helper verifies the listener's PID, executable, and creation time, then checks the interpreter PID on the actual connected socket before sending notebook code.
It retains `command.py`, `runner.py`, `transcript.txt`, `dispatch.json`, and an in-nTop `completion.json`.
A completed transport receipt is separate from block build state and geometric verification.

A timeout or connection loss after sending has an unknown outcome. Do not repeat the command.
Inspect its completion file later. The helper blocks another send in this checkout while the prior receipt is unresolved.
Do not send concurrently from other clients or checkouts. Do not forward this unauthenticated prototype port.
The existing background bridge prints its exact marker path, which can include `._done.txt`; use that returned path.
