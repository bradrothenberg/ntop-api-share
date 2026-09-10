# Background Notebook API commands

The prototype binds `notebook` inside nTop's Python Console. It does not provide a native stdin pipe,
RPC service, or socket. nTop Automate does not expose this Notebook API.

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
