from fastapi import FastAPI
import time

from workers.gpu_worker import process_query

app = FastAPI()


@app.post("/process")
def process(data: dict):

    start = time.time()

    result = process_query(
        data["query"]
    )

    latency = time.time() - start

    return {

        "id": data["id"],

        "result": result,

        "latency": latency
    }