import asyncio
import aiohttp
import time
import statistics

BASE_URL = "http://localhost:8001"

TOTAL_REQUESTS = 1000

latencies = []
success = 0
failed = 0
gpu_completed = 0
cpu_stub_completed = 0


async def submit_request(session, i):

    payload = {
        "id": i,
        "query": f"Explain distributed systems request {i}"
    }

    async with session.post(
        f"{BASE_URL}/request",
        json=payload
    ) as response:

        data = await response.json()

        return data["job_id"]


async def wait_for_result(session, job_id):

    while True:

        async with session.get(
            f"{BASE_URL}/result/{job_id}"
        ) as response:

            data = await response.json()

            status = data.get("status")

            if status == "finished":
                return True, data.get("source")

            if status == "failed":
                return False, None

            if status == "error":
                return False, None

        await asyncio.sleep(0.5)


async def process_request(session, i):

    global success, failed, gpu_completed, cpu_stub_completed

    start = time.time()

    try:

       
        job_id = await submit_request(session, i)

        
        ok, source = await wait_for_result(session, job_id)

        end = time.time()

        latency = end - start

        latencies.append(latency)

        if ok:
            success += 1
            if source == "gpu":
                gpu_completed += 1
            elif source == "cpu_stub":
                cpu_stub_completed += 1
            tag = "GPU" if source == "gpu" else ("CPU stub" if source == "cpu_stub" else source or "?")
            print(f"✅ Request {i} finished in {latency:.2f}s [{tag}]")

        else:
            failed += 1
            print(f"❌ Request {i} failed")

    except Exception as e:

        failed += 1

        print(f"💥 Request {i} crashed: {e}")


async def main():

    start_test = time.time()

    async with aiohttp.ClientSession() as session:

        tasks = []

        for i in range(TOTAL_REQUESTS):

            tasks.append(
                process_request(session, i)
            )

        await asyncio.gather(*tasks)

    end_test = time.time()

    total_time = end_test - start_test

    print("\n==============================")
    print("🔥 REAL DISTRIBUTED BENCHMARK")
    print("==============================")

    print(f"✅ Successful Requests: {success}")
    print(f"❌ Failed Requests: {failed}")

    unknown_ok = success - gpu_completed - cpu_stub_completed
    print(f"\n🖥 Completed by GPU workers: {gpu_completed}")
    print(f"💻 Completed by CPU stub workers: {cpu_stub_completed}")
    if unknown_ok > 0:
        print(f"❔ Completed (source unknown): {unknown_ok}")

    print(f"\n⚡ Total Time: {total_time:.2f} sec")

    if latencies:

        print(f"\n📈 Average Latency: {statistics.mean(latencies):.2f} sec")

        print(f"🚀 Max Latency: {max(latencies):.2f} sec")

        print(f"⚡ Min Latency: {min(latencies):.2f} sec")

        throughput = success / total_time

        print(f"\n🔥 Throughput: {throughput:.2f} req/sec")


if __name__ == "__main__":

    asyncio.run(main())