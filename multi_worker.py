import multiprocessing
import os

def start_worker():
    os.system("rq worker default --worker-class rq.worker.SimpleWorker")

if __name__ == "__main__":

    workers = []

    for i in range(10):

        p = multiprocessing.Process(target=start_worker)

        p.start()

        workers.append(p)

    for p in workers:
        p.join()