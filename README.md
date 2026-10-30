# ⚡ High-Throughput vLLM Benchmarking & Observability Pipeline

An end-to-end LLM serving, load-testing, and production-grade monitoring pipeline. This project deploys an OpenAI-compatible API server using **vLLM** to serve models, stress-tests endpoints at scale, and monitors real-time engine health using **Prometheus** and **Grafana**.

## 📊 Real-Time Grafana Dashboard Link
[https://snapshots.raintank.io/dashboard/snapshot/3JuFTXxErLyzAvaVpO9IzL2GE2L03sLr?from=2026-10-30T10:45:02.383Z&to=2026-10-30T11:00:02.383Z&timezone=browser&refresh=auto
](https://snapshots.raintank.io/dashboard/snapshot/ImRtBGBeC8j84WYPpvuWMziegxyUZyjE)
## 🛠  Architecture & Tech Stack
- **LLM Engine:** vLLM (v0.32.0)
- **Models Tested:**
  - `Qwen/Qwen2.5-7B-Instruct-AWQ` (4-bit quantized baseline)
- **Hardware:** NVIDIA Tesla T4 GPU (16GB VRAM)
- **Metrics Scraping:** Prometheus (5s interval)
- **Visualization:** Grafana Dashboard (TTFT, Inter-Token Latency, Throughput, Queue Depth)
- **Ingress Tunneling:** Cloudflare Tunnels (`cloudflared`)
- **Load Generator:** Async HTTP/2 (`httpx` & `asyncio`)

## 📈 Real Performance & Sweep Results
Below are the actual benchmark results obtained during our stress testing load-sweep under concurrent requests:

| Requests/sec (RPS) | Completed Requests | Latency p50 (s) | Latency p95 (s) | Saturated? |
|:---:|:---:|:---:|:---:|:---:|
| **0.1** | 12 | 3.53 | 3.85 | No |
| **0.2** | 24 | 3.48 | 3.80 | No |
| **0.4** | 47 | 3.49 | 3.87 | No |
| **0.6** | 70 | 3.49 | 4.06 | No |

> **Inference Engineering Insight:** By evaluating a 7B AWQ 4-bit quantized model on a budget GPU (Tesla T4), we demonstrate how quantization allows larger, more capable models to fit within restricted GPU memory budgets while keeping p95 latencies strictly bounded.

## 🚀 How to Reproduce
1. Open `vllm_benchmark.ipynb` in Google Collabor.
2. Step through the setup to download, compile, and run the vLLM engine.
3. Run the Prometheus & Grafana stack inside the environment.
4. Access your metrics dashboard using the generated Cloudflare secure tunnel URL.
