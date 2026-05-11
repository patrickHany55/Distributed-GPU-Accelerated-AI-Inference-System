import os

from redis import Redis
from rq import Queue


class Scheduler:

    def __init__(self):

        self.redis_conn = Redis(
            host=os.environ.get("REDIS_HOST", "redis"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
        )

        # 🔥 GPU Queues
        self.workers = [

            Queue(
                "gpu0",
                connection=self.redis_conn
            ),

            Queue(
                "gpu1",
                connection=self.redis_conn
            )
        ]

        # 🖥 CPU Fallback Queue
        self.cpu_queue = Queue(
            "cpu",
            connection=self.redis_conn
        )

        self.index = 0

    # 🔄 Round Robin GPU Scheduler
    def get_next_worker(self):

        worker = self.workers[self.index]

        self.index = (
            self.index + 1
        ) % len(self.workers)

        return worker

    # 📊 Queue Monitoring
    def get_queue_size(self):

        total = 0

        for queue in self.workers:
            total += len(queue)

        return total