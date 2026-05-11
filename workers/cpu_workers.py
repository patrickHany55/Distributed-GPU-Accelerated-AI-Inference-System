"""
Legacy single-process CPU worker launcher.
Prefer run_local_cpu_workers.py for 8 workers.

  REDIS_URL=redis://localhost:6379  python workers/cpu_workers.py
"""
from redis import Redis
from rq import Queue, Worker

if __name__ == "__main__":
    import os

    url = os.environ.get("REDIS_URL")
    if url:
        redis_conn = Redis.from_url(url)
    else:
        host = os.environ.get("REDIS_HOST", "localhost")
        port = int(os.environ.get("REDIS_PORT", "6379"))
        redis_conn = Redis(host=host, port=port)

    queues = [Queue("cpu", connection=redis_conn)]
    worker = Worker(queues, connection=redis_conn)
    print("CPU Worker Started (queue cpu)")
    worker.work()
