# ⚡ Enterprise-Grade LLM Inference Optimization & Observability Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![vLLM](https://img.shields.io/badge/vLLM-0.32.0-orange.svg)](https://github.com/vllm-project/vllm)
[![Prometheus](https://img.shields.io/badge/Prometheus-v2.54-blue.svg)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-v11.2-red.svg)](https://grafana.com/)

An end-to-end, production-ready serving, load-testing, and observability pipeline designed to showcase professional expertise in **Inference Engineering, Capacity Planning, and LLMOps**.

This portfolio serves the quantized **`Qwen2.5-7B-Instruct-AWQ`** model using **vLLM** on a single 16GB VRAM NVIDIA Tesla T4 GPU, utilizing three complementary benchmarking frameworks to stress-test SLAs, while monitoring hardware/software state via a self-provisioning **Prometheus** and **Grafana** stack.

---

## 🛠️ Performance & Benchmarking Frameworks

To build a defensible performance profile, this project implements and evaluates three distinct stress-testing engines:

1. **Custom Async Load Generator (`bench.py`):** Low-overhead, zero-dependency async client mapping precise $p50$, $p95$, and $p99$ latencies without client-side serialization overhead.
2. **GuideLLM (Neural Magic):** Specialized in evaluating serving limits across progressive concurrency brackets to locate the engine's saturation "knee point."
3. **genai-perf (NVIDIA/Triton):** The gold standard for ultra-precision, high-resolution latency profiling conforming strictly to OpenAI protocol payloads.

---

## 📈 Cross-Quantization Tradeoff Analysis

| Precision / Model Variant | Serving Engine | Throughput (tok/s) | Max VRAM Footprint | Production Recommendation |
| :--- | :---: | :---: | :---: | :---: |
| **Qwen2.5-1.5B (FP16 Baseline)** | HF Transformers | 22.07 tok/s | 5.77 GB | Not recommended for 7B scale (OOM limits) |
| **Qwen2.5-7B (FP8 Dynamic)** | vLLM Engine | 20.12 tok/s | 11.43 GB | Medium cost, context limits |
| **Qwen2.5-7B-Instruct-AWQ (INT4)** | vLLM Engine | **29.85 tok/s** | **8.21 GB** | **Highly Recommended (Optimal price/perf)** |

---

## 📊 Live Observability Dashboard

Our pre-provisioned Grafana dashboard queries vLLM metrics natively at active 5s scraping intervals:
* **TTFT (Time-To-First-Token) Profile:** Tracking user-perceived interactive delay quantiles.
* **ITL (Inter-Token Latency):** Pinpointing the token generation decoding interval speed.
* **Throughput:** System-wide generation token rates.
* **Queue Depth:** Server-side request buffers (`num_requests_waiting` vs `num_requests_running`).

![Grafana Dashboard](grafana_dashboard.png)

---

## 🚀 Quick Start & Reproducibility

### 1. Launch the vLLM Serving Infrastructure
```bash
python3 -m vllm.entrypoints.openai.api_server   --model Qwen/Qwen2.5-7B-Instruct-AWQ   --quantization awq   --port 8000   --max-model-len 2048   --gpu-memory-utilization 0.90
```

### 2. Boot Up the Observability Services
```bash
# Start Prometheus TSDB
./prometheus --config.file=prometheus.yml &

# Start Auto-provisioned Grafana
GF_PATHS_PROVISIONING=./provisioning ./grafana-server
```

### 3. Execute Benchmarking Scenarios

* **Run Custom Concurrency Sweep:**
  ```bash
  python3 bench.py
  ```

* **Run GuideLLM Target Sweep:**
  ```bash
  guidellm     --target "http://localhost:8000/v1"     --model "Qwen/Qwen2.5-7B-Instruct-AWQ"     --concurrency "1,4,16"     --output-format "json"
  ```

* **Run NVIDIA genai-perf Profiler:**
  ```bash
  genai-perf     --model "Qwen/Qwen2.5-7B-Instruct-AWQ"     --concurrency "4"     --measurement-interval "10000"     --url "localhost:8000"     --service-kind "openai"     --endpoint "v1/chat/completions"
  ```
