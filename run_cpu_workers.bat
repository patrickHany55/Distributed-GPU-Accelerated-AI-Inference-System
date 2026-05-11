@echo off
setlocal
cd /d "%~dp0"

if not defined REDIS_URL set REDIS_URL=redis://localhost:6379
if not defined NUM_CPU_WORKERS set NUM_CPU_WORKERS=8

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run_local_cpu_workers.py
) else (
    python run_local_cpu_workers.py
)
