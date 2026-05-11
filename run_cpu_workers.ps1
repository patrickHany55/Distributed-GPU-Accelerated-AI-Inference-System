# Start 8 local RQ workers on the "cpu" queue (stub responses).
# Prerequisites: Redis reachable at localhost:6379 (e.g. docker compose up redis).
# Usage: .\run_cpu_workers.ps1
# Optional: $env:REDIS_URL = "redis://localhost:6379"; $env:NUM_CPU_WORKERS = "8"

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not $env:REDIS_URL) {
    $env:REDIS_URL = "redis://localhost:6379"
}
if (-not $env:NUM_CPU_WORKERS) {
    $env:NUM_CPU_WORKERS = "8"
}

$venvPy = Join-Path $Root ".venv\Scripts\python.exe"
$script = Join-Path $Root "run_local_cpu_workers.py"

if (Test-Path $venvPy) {
    Write-Host "Using venv: $venvPy"
    & $venvPy $script
} else {
    Write-Host "Using system Python (create .venv and install redis rq if needed)"
    python $script
}
