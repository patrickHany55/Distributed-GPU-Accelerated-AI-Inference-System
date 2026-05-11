FROM nvidia/cuda:12.3.0-runtime-ubuntu22.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

# Shared HuggingFace cache
ENV HF_HOME=/root/.cache/huggingface

COPY . .

CMD ["python3"]