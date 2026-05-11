# Distributed GPU-Accelerated AI Inference System

A production-style distributed AI inference platform built using **FastAPI**, **Redis Queue (RQ)**, **Docker**, and **GPU-accelerated PyTorch inference**.

The system demonstrates real distributed systems concepts including:

* Distributed task queues
* Multi-worker scheduling
* GPU inference acceleration
* Asynchronous processing
* Load balancing
* Fault tolerance
* Graceful degradation
* CPU fallback workers
* Dockerized distributed infrastructure

---

# 🚀 Features

* ✅ Distributed GPU workers
* ✅ Redis-based asynchronous queues
* ✅ FastAPI inference API
* ✅ Round Robin load balancing
* ✅ GPU acceleration using CUDA
* ✅ CPU fallback workers
* ✅ Queue overload protection
* ✅ Runtime timeout monitoring
* ✅ Dockerized worker containers
* ✅ Real benchmark testing
* ✅ Metrics and monitoring endpoints
* ✅ Shared HuggingFace cache volumes

---

# 🏗️ System Architecture

```text
Clients
   ↓
FastAPI API Server
   ↓
Scheduler / Load Balancer
   ↓
Redis Message Broker
 ↙              ↘
GPU Queue      CPU Queue
 ↙     ↘           ↓
GPU1   GPU2     CPU Workers
```

---

# 📂 Project Structure

```text
DPROJ/
│
├── client/
│   └── real_load_test.py
│
├── llm/
│   └── inference.py
│
├── master/
│   ├── api.py
│   └── scheduler.py
│
├── rag/
│   ├── retriever.py
│   └── vector_store.py
│
├── workers/
│   ├── api.py
│   ├── gpu_worker.py
│   ├── cpu_stub_worker.py
│   └── cpu_workers.py
│
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.api
├── requirements.txt
├── requirements-api.txt
├── nginx.conf
└── main.py
```

---

# ⚙️ Technologies Used

| Technology           | Purpose                   |
| -------------------- | ------------------------- |
| Python               | Core programming language |
| FastAPI              | API server                |
| Redis                | Message broker            |
| RQ                   | Distributed task queue    |
| Docker               | Containerization          |
| PyTorch              | Deep learning framework   |
| CUDA                 | GPU acceleration          |
| Transformers         | LLM inference             |
| SentenceTransformers | Embeddings                |
| HuggingFace          | Pretrained models         |

---

# 🔥 Distributed System Features

## 1. Distributed Queues

The system uses multiple distributed queues:

* `gpu0`
* `gpu1`
* `cpu`

Each queue is processed independently by dedicated workers.

---

## 2. Asynchronous Processing

Requests are submitted asynchronously using Redis Queue (RQ), allowing the API server to remain responsive under heavy load.

---

## 3. Load Balancing

The scheduler distributes requests across GPU workers using a **Round Robin** scheduling strategy.

---

## 4. Fault Tolerance

The architecture supports:

* CPU fallback workers
* Runtime timeout monitoring
* Queue overload detection
* Failure tracking

---

## 5. Graceful Degradation

During overload situations, requests are redirected to lightweight CPU workers instead of failing completely.

---

## 6. GPU Acceleration

The system uses:

* CUDA-enabled PyTorch inference
* NVIDIA RTX 3070 GPU acceleration
* Transformer-based LLM inference

---

# 🔄 Workflow

## Step 1 — Client Request

A client sends an inference request to the API server.

---

## Step 2 — Scheduling

The scheduler:

* selects a GPU worker
* monitors queue size
* checks overload conditions

---

## Step 3 — Queue Submission

The request is pushed into:

* GPU queues for real inference
  OR
* CPU fallback queue during overload

---

## Step 4 — Worker Processing

GPU workers:

* perform real transformer inference

CPU workers:

* generate lightweight fallback responses

---

## Step 5 — Result Retrieval

Clients poll the API using the generated job ID until the result becomes available.

---

# 📊 Benchmark Results

## Example Benchmark

| Metric              | Value         |
| ------------------- | ------------- |
| Total Requests      | 1000          |
| Successful Requests | 997           |
| Failed Requests     | 3             |
| Throughput          | 12.81 req/sec |
| Average Latency     | 17.27 sec     |
| Max Latency         | 77.80 sec     |

---

# 🖥️ GPU Setup

The project supports NVIDIA CUDA GPU acceleration.

Verified GPU:

* NVIDIA RTX 3070 Laptop GPU

---

# 🐳 Docker Deployment

## Build and Run

```bash
docker compose up --build
```

---

## Stop Containers

```bash
docker compose down
```

---

# 📡 API Endpoints

## Submit Request

```http
POST /request
```

### Example Body

```json
{
  "query": "Explain distributed systems"
}
```

---

## Get Result

```http
GET /result/{job_id}
```

---

## Metrics Endpoint

```http
GET /metrics
```

---

# 🔥 Example Benchmark Execution

```bash
python client/real_load_test.py
```

---

# 📈 Metrics Collected

The system tracks:

* total requests
* successful requests
* failed requests
* throughput
* queue length
* latency
* GPU timeout metrics

---

# 🛡️ Fault Tolerance

The system prevents total failure using:

* CPU fallback workers
* queue overload monitoring
* distributed worker isolation
* runtime timeout handling

---

# 🚀 Future Improvements

Potential future enhancements include:

* Kubernetes deployment
* Multi-node distributed clusters
* Autoscaling workers
* Prometheus monitoring
* Grafana dashboards
* Batch inference optimization
* Distributed GPU orchestration

---

# 📚 Concepts Demonstrated

This project demonstrates practical implementation of:

* Distributed Systems
* AI Infrastructure
* GPU Computing
* Queue-Based Communication
* Load Balancing
* Fault Tolerance
* Asynchronous Processing
* Scalable AI Serving
* Graceful Degradation


