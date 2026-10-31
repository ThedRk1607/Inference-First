# ⚡ High-Throughput vLLM serving, Load-Testing, & Observability Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![vLLM](https://img.shields.io/badge/vLLM-0.32.0-orange.svg)](https://github.com/vllm-project/vllm)

A production-grade, metrics-driven LLM serving infrastructure pipeline. This project implements a high-throughput OpenAI-compatible API gateway serving quantized LLMs, conducts rigorous automated concurrency stress-testing, and establishes real-time system observability using a self-provisioning **Prometheus** and **Grafana** stack.

Designed to showcase enterprise-level skills in **LLM Inference Optimization**, **GPU Resource Amortization**, and **Infrastructure Observability**.

---

## 🛠️ Architecture & Tech Stack

```
   [ Async HTTP/2 Load Generator ] 
                 │  (httpx / asyncio client concurrency sweep)
                 ▼
   [ Ingress Secure Tunneling (Cloudflare) ]
                 │
                 ▼
   [ OpenAI-Compatible API Server (vLLM Engine) ] ◄───► [ GPU: NVIDIA Tesla T4 ]
                 │ (Exposes /v1/completions & /metrics) 
                 ▼
   [ Metrics Aggregation Engine (Prometheus) ]
                 │ (Scrapes system & serving metrics at 5s intervals)
                 ▼
   [ Observability & Alerting UI (Grafana Dashboard) ]
```

*   **LLM Serving Engine:** `vLLM` (v0.32.0) utilizing PagedAttention kernels and continuous batching.
*   **Models Benchmark-Tested:**
    *   `Qwen/Qwen2.5-7B-Instruct-AWQ` (4-bit activation-aware weight quantized baseline)
    *   `Qwen/Qwen2.5-7B-Instruct` (FP8 Per-Tensor Dynamic Quantization)
    *   `Qwen/Qwen2.5-1.5B-Instruct` (FP16 Dense Baseline)
*   **Infrastructure Hosting:** Google Colab Environment backed by an **NVIDIA Tesla T4 GPU (16GB VRAM)**.
*   **Observability Stack:** Prometheus Server (TSDB) scraping vLLM metrics natively at 5s intervals, visualizing via a dynamically provisioned Grafana dashboard.
*   **Secure Ingress:** `cloudflared` (Cloudflare Tunneling) allowing secure, zero-config WAN access to UI endpoints.

---

## 📈 Performance & Latency SLA Analysis

We executed a systematic load-testing sweep over the hosted API endpoints to analyze latency degradation, queue behaviors, and throughput limits under varying traffic rates:

### Load Sweep Summary

| Requests/sec (RPS) | Completed Requests | Latency p50 (s) | Latency p95 (s) | Engine Saturated? |
|:---:|:---:|:---:|:---:|:---:|
| **0.1** | 12 | 3.53s | 3.85s | 🟢 No |
| **0.2** | 24 | 3.48s | 3.80s | 🟢 No |
| **0.4** | 47 | 3.49s | 3.87s | 🟢 No |
| **0.6** | 70 | 3.49s | 4.06s | 🟡 Near Threshold |

### Model Format Quantization Comparison Table

| Model Configuration | Precision Type | Throughput (tok/s) | Peak VRAM Footprint (GB) | Serving Status |
| :--- | :---: | :---: | :---: | :---: |
| **Qwen2.5-1.5B-Instruct** | FP16 | 22.07 tok/s | 5.77 GB | `Success` (Hugging Face) |
| **Qwen2.5-7B-Instruct** | FP8 | 20.12 tok/s | 11.43 GB | `Success` (vLLM Dynamic) |
| **Qwen2.5-7B-Instruct-AWQ** | INT4 | **29.85 tok/s** | **8.21 GB** | `Success` (vLLM Active) |

### 💡 Key Inference Engineering Insights:
*   **Quantization Unlocks Budget Hardware:** A dense 7B parameter model in standard FP16/BF16 precision requires upwards of **14GB+ VRAM just for weights**, triggering immediate Out-Of-Memory (OOM) crashes on a 16GB T4 during batch generation. Quantization is a baseline production requirement to fit larger, highly-capable models into limited memory budgets.
*   **AWQ Quantization Superiority:** Serving `7B-AWQ (INT4)` yielded a **35.2% throughput improvement** over FP16 while maintaining a significantly smaller VRAM footprint (**8.21 GB** vs **11.43 GB** for dynamic FP8). This directly translates to lower hardware operational costs and higher request density tolerance.

---

## 📊 Live Observability: Dashboard & Metrics

The dashboard is fully configured to track production SLA metrics across four critical areas:
1.  **TTFT (Time-To-First-Token) Latency (p50 / p95):** Crucial metric for user-perceived performance bounds.
2.  **Inter-Token Latency (ITL):** Measures execution speed of subsequent decoding steps.
3.  **Engine Token Throughput:** Displays generated tokens per second in real-time.
4.  **Queue Depth:** Monitors active vs. waiting request pools to detect downstream server saturation early.

*(Insert your custom Grafana screenshot here to showcase visual execution details)*

---

## ⚙️ Declarative Provisioning Setup

To ensure infrastructure is fully reproducible and matches production guidelines, both the datasource and dashboard definitions are loaded declaratively at boot:

*   `prometheus.yml`: Scrapes local endpoints at highly active intervals (`5s`).
*   `provisioning/datasources/prom.yml`: Automates Grafana connections to the Prometheus TSDB system at startup.
*   `provisioning/dashboards/vllm.yml`: Directs Grafana to parse and build the preconfigured UI located in `dashboards/vllm.json` without manual click configuration.

---

## 🚀 How to Run and Reproduce

### Prerequisites
*   A Linux environment with CUDA capability (e.g. standard Google Colab T4 runtime)
*   Python 3.10+

### Execution Sequence
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/vllm-inference-benchmarking-grafana.git
    cd vllm-inference-benchmarking-grafana
    ```
2.  **Spin up the vLLM server instance:**
    ```bash
    python3 -m vllm.entrypoints.openai.api_server       --model Qwen/Qwen2.5-7B-Instruct-AWQ       --quantization awq       --port 8000       --max-model-len 2048       --gpu-memory-utilization 0.90
    ```
3.  **Boot the Observability Services:**
    ```bash
    # Start Prometheus
    ./prometheus --config.file=prometheus.yml &
    # Start Grafana
    GF_PATHS_PROVISIONING=./provisioning ./grafana-server
    ```
4.  **Launch the Load Testing Suite:**
    ```bash
    python3 bench.py
    ```
