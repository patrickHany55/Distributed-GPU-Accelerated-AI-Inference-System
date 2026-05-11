import os
import time

from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError
from rq.job import get_current_job

_TRANSIENT = (RedisConnectionError, RedisTimeoutError, ConnectionResetError, OSError)


def _redis_conn_fallback() -> Redis:
    """Separate client only when no job context (tests) or worker conn fails."""
    url = os.environ.get("REDIS_URL")
    kw = dict(
        socket_keepalive=True,
        socket_connect_timeout=10,
        retry_on_timeout=True,
        health_check_interval=30,
    )
    if url:
        return Redis.from_url(url, **kw)
    host = os.environ.get("REDIS_HOST", "localhost")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    return Redis(host=host, port=port, **kw)


def stub_response(query: str, original_job_id: str) -> str:
    """Fast stub for slow GPU paths; stores answer for GET /result/{original_job_id}."""
    text = f"[CPU stub] GPU exceeded time budget. Query: {query!r}"
    key = f"stub_result:{original_job_id}"

    job = get_current_job()
    conn = job.connection if job is not None else None

    last_err: Exception | None = None
    for attempt in range(4):
        try:
            if conn is not None:
                conn.set(key, text, ex=86400)
            else:
                _redis_conn_fallback().set(key, text, ex=86400)
            return text
        except _TRANSIENT as e:
            last_err = e
            conn = None
            time.sleep(0.15 * (2**attempt))

    assert last_err is not None
    raise last_err
