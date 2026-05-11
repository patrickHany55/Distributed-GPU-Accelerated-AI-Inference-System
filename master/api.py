import os
from datetime import datetime, timezone

from fastapi import FastAPI
from redis import Redis
from rq.job import Job
import time

from master.scheduler import Scheduler

app = FastAPI()

# Max GPU processing time before fallback
GPU_TASK_TIMEOUT_SECONDS = float(
    os.environ.get("GPU_TASK_TIMEOUT_SECONDS", "30")
)

# Hard timeout for RQ jobs
RQ_GPU_JOB_TIMEOUT_SECONDS = int(
    os.environ.get("RQ_GPU_JOB_TIMEOUT_SECONDS", "180")
)

# Redis connection
redis_conn = Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", "6379")),
)

# Scheduler
scheduler = Scheduler()

# Metrics
total_requests = 0
successful_requests = 0
failed_requests = 0


def _seconds_since_gpu_started(job: Job) -> float:

    if job.is_queued:
        return 0.0

    if job.started_at is None:
        return 0.0

    start = job.started_at

    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    return (
        datetime.now(timezone.utc) - start
    ).total_seconds()


def _stub_result(job_id: str):

    raw = redis_conn.get(f"stub_result:{job_id}")

    if raw is None:
        return None

    return raw.decode() if isinstance(raw, bytes) else raw


def _enqueue_cpu_fallback(gpu_job_id: str, query: str):

    if not query:
        return

    # Prevent duplicate fallback jobs
    if not redis_conn.set(
        f"cpu_fallback_lock:{gpu_job_id}",
        "1",
        nx=True,
        ex=86400
    ):
        return

    scheduler.cpu_queue.enqueue(
        "workers.cpu_stub_worker.stub_response",
        query,
        gpu_job_id,
    )


def _try_increment_success(job_id: str):

    global successful_requests

    if redis_conn.set(
        f"success_counted:{job_id}",
        "1",
        nx=True,
        ex=86400
    ):
        successful_requests += 1


# ============================================
# Submit Request
# ============================================

@app.post("/request")
def send_request(data: dict):

    global total_requests

    try:

        total_requests += 1

        query = data.get("query")

        print("\n==============================")
        print("📥 New Request Received")
        print(f"🆔 Request Number: {total_requests}")
        print(f"❓ Query: {query}")

        start_time = time.time()

        selected_queue = scheduler.get_next_worker()

        queue_size = scheduler.get_queue_size()

        print(f"📊 GPU Queue Size: {queue_size}")

        # 🔥 Queue overload fallback
        USE_CPU_FALLBACK = queue_size > 300

        if USE_CPU_FALLBACK:

            print("⚠ Queue overloaded -> CPU fallback")

            gpu_job_id = f"gpu-{total_requests}"

            job = scheduler.cpu_queue.enqueue(
                "workers.cpu_stub_worker.stub_response",
                query,
                gpu_job_id,
            )

        else:

            job = selected_queue.enqueue(
                "workers.gpu_worker.process_query",
                query,
                job_timeout=RQ_GPU_JOB_TIMEOUT_SECONDS,
            )

        print(f"🎯 Selected Queue: {selected_queue.name}")

        end_time = time.time()

        print("✅ Job Accepted")
        print(f"🆔 Job ID: {job.id}")
        print(f"⏱ Queue Time: {end_time - start_time:.2f} sec")
        print("==============================\n")

        return {
            "status": "submitted",
            "job_id": job.id,
            "gpu_timeout_seconds": GPU_TASK_TIMEOUT_SECONDS,
        }

    except Exception as e:

        print(f"❌ Request Failed: {str(e)}")

        return {
            "status": "error",
            "message": str(e),
        }


# ============================================
# Get Result
# ============================================

@app.get("/result/{job_id}")
def get_result(job_id: str):

    global successful_requests
    global failed_requests

    try:

        job = Job.fetch(
            job_id,
            connection=redis_conn,
        )

        # ====================================
        # GPU or CPU Job Finished
        # ====================================

        if job.is_finished:

            _try_increment_success(job_id)

            source = "gpu"

            # 🔥 Detect CPU queue jobs
            if job.origin == "cpu":
                source = "cpu_stub"

            print("\n==============================")
            print(f"✅ Job Finished ({source.upper()})")
            print(f"🆔 Job ID: {job.id}")
            print(f"📊 Successful Requests: {successful_requests}")
            print("==============================\n")

            return {
                "status": "finished",
                "result": job.result,
                "source": source,
            }

        # ====================================
        # CPU Stub Result Stored in Redis
        # ====================================

        stub = _stub_result(job_id)

        if job.is_failed:

            if stub:

                _try_increment_success(job_id)

                return {
                    "status": "finished",
                    "result": stub,
                    "source": "cpu_stub",
                }

            if not job.meta.get("counted_failed"):

                failed_requests += 1

                job.meta["counted_failed"] = True

                job.save_meta()

            print("\n==============================")
            print("❌ Job Failed")
            print(f"🆔 Job ID: {job.id}")
            print(f"📊 Failed Requests: {failed_requests}")
            print("==============================\n")

            return {
                "status": "failed",
            }

        # ====================================
        # GPU Runtime Monitoring
        # ====================================

        gpu_running_seconds = _seconds_since_gpu_started(job)

        query = job.args[0] if job.args else ""

        # 🔥 Runtime timeout fallback
        if gpu_running_seconds > GPU_TASK_TIMEOUT_SECONDS:

            _enqueue_cpu_fallback(
                job_id,
                query
            )

        stub = _stub_result(job_id)

        if stub:

            _try_increment_success(job_id)

            return {
                "status": "finished",
                "result": stub,
                "source": "cpu_stub",
            }

        if (
            gpu_running_seconds > GPU_TASK_TIMEOUT_SECONDS
            and redis_conn.exists(f"cpu_fallback_lock:{job_id}")
        ):

            return {
                "status": "fallback_pending"
            }

        # ====================================
        # Normal States
        # ====================================

        if job.is_queued:
            return {"status": "queued"}

        if job.is_started:
            return {"status": "started"}

        return {
            "status": "unknown",
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e),
        }


# ============================================
# Metrics
# ============================================

@app.get("/metrics")
def metrics():

    return {

        "total_requests": total_requests,

        "successful_requests": successful_requests,

        "failed_requests": failed_requests,

        "success_rate":
            f"{(successful_requests / total_requests * 100) if total_requests > 0 else 0:.2f}%",

        "queue_length":
            sum(len(queue) for queue in scheduler.workers),

        "cpu_queue_length":
            len(scheduler.cpu_queue),

        "gpu_task_timeout_seconds":
            GPU_TASK_TIMEOUT_SECONDS,

        "rq_gpu_job_timeout_seconds":
            RQ_GPU_JOB_TIMEOUT_SECONDS,
    }