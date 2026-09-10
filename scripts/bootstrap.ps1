[CmdletBinding()]
param([string]$NTopExe=$env:NTOP_EXE,[switch]$SkipSync)
$ErrorActionPreference='Stop'
$ntopShareRoot=Split-Path -Parent $PSScriptRoot
$env:NTOP_PYSCRIPTS=Join-Path $ntopShareRoot 'harness'
if($NTopExe){$env:NTOP_EXE=(Resolve-Path -LiteralPath $NTopExe).Path}
Push-Location -LiteralPath $ntopShareRoot
try {
    if(-not $SkipSync){uv sync --locked;if($LASTEXITCODE -ne 0){throw 'uv sync failed'}}
    uv run --locked python scripts/prepare.py --models
    if($LASTEXITCODE -ne 0){throw 'Preparation failed'}
} finally {Pop-Location}
Write-Output 'Prepared this session. Launch the matching nTop custom build from this PowerShell session.'
