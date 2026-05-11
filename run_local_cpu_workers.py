"""
Run 8 local RQ workers on the `cpu` queue (stub LLM path).
Requires Redis reachable from the host (e.g. docker compose exposing 6379).

  set REDIS_URL=redis://localhost:6379
  python run_local_cpu_workers.py

Override worker count: NUM_CPU_WORKERS=8
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
NUM_WORKERS = int(os.environ.get("NUM_CPU_WORKERS", "8"))


def main() -> None:
    env = {**os.environ, "PYTHONPATH": ROOT}
    procs: list[subprocess.Popen] = []
    for _ in range(NUM_WORKERS):
        procs.append(
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "rq.cli",
                    "worker",
                    "cpu",
                    "--url",
                    REDIS_URL,
                    "--worker-class",
                    "rq.worker.SimpleWorker",
                ],
                cwd=ROOT,
                env=env,
            )
        )
    print(f"Started {NUM_WORKERS} CPU workers on queue 'cpu' ({REDIS_URL})")
    try:
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        for p in procs:
            p.terminate()


if __name__ == "__main__":
    main()
