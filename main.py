import asyncio
import aiohttp
import time
import matplotlib.pyplot as plt

URL = "http://localhost:8001/request"

latencies = []


async def send_request(session, i):
    start = time.time()

    payload = {
        "id": i,
        "query": f"Hello {i}"
    }

    try:
        async with session.post(URL, json=payload) as response:
            await response.text()
    except Exception as e:
        print(f"Error in request {i}: {e}")

    latency = time.time() - start
    latencies.append(latency)


async def main():
    start_total = time.time()

    async with aiohttp.ClientSession() as session:
        batch_size = 50
        total_requests = 1000

        for start in range(0, total_requests, batch_size):
            tasks = [send_request(session, i) for i in range(start, start + batch_size)]
            await asyncio.gather(*tasks)

    end_total = time.time()

    
    plt.figure()
    plt.plot(latencies)
    plt.title("Latency for 1000 Requests")
    plt.xlabel("Request Number")
    plt.ylabel("Latency (seconds)")

    
    plt.savefig("results/latency_graph.png")

    
    total_time = end_total - start_total
    throughput = len(latencies) / total_time

    print(f"Total time: {total_time:.2f} seconds")
    print(f"Throughput: {throughput:.2f} requests/sec")
    print("Graph saved!")


if __name__ == "__main__":
    asyncio.run(main())