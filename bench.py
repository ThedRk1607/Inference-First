import asyncio
import time
import csv
import httpx
import statistics

URL = "http://localhost:8000/v1/completions"
MODEL = "Qwen/Qwen2.5-7B-Instruct-AWQ"
PROMPT_WORDS = 200
OUTPUT_TOKENS = 128
REQS_PER_LEVEL = 100
CONCURRENCY_LEVELS = [1, 2, 4, 8, 16, 32, 64, 128]
PROMPT = " ".join(["benchmark"] * PROMPT_WORDS)

async def one_request(client, sem, results):
    async with sem:
        payload = {
            "model": MODEL,
            "prompt": PROMPT,
            "max_tokens": OUTPUT_TOKENS,
            "temperature": 0,
            "stream": True,
            "ignore_eos": True
        }
        start = time.perf_counter()
        ttft = None
        try:
            async with client.stream("POST", URL, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        if ttft is None:
                            ttft = time.perf_counter() - start
        except Exception:
            results.append({"ok": False})
            return
        latency = time.perf_counter() - start
        results.append({"ok": True, "ttft": ttft, "latency": latency})

async def run_level(concurrency):
    results = []
    sem = asyncio.Semaphore(concurrency)
    limits = httpx.Limits(max_connections=concurrency)
    async with httpx.AsyncClient(timeout=600, limits=limits) as client:
        await asyncio.gather(*[one_request(client, sem, results) for _ in range(REQS_PER_LEVEL)])
    return results

def percentile(values, p):
    s = sorted(values)
    index = round(p / 100 * (len(s) - 1))
    return s[index]

async def main():
    print(f"{'conc':>5} {'ok':>5} {'lat_p50':>8} {'lat_p95':>8} {'lat_p99':>8}")
    rows = []
    for c in CONCURRENCY_LEVELS:
        results = await run_level(c)
        ok = [r for r in results if r["ok"]]
        if not ok:
            print(f"{c:>5} Failed run")
            continue
        latencies = [r["latency"] for r in ok]
        ttfts = [r["ttft"] for r in ok if r["ttft"] is not None]
        p50 = percentile(latencies, 50)
        p95 = percentile(latencies, 95)
        p99 = percentile(latencies, 99)
        print(f"{c:>5} {len(ok):>5} {p50:>8.3f} {p95:>8.3f} {p99:>8.3f}")
        rows.append({
            "concurrency": c,
            "completed": len(ok),
            "p50": round(p50, 3),
            "p95": round(p95, 3),
            "p99": round(p99, 3)
        })
    
    with open("results_bench.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["concurrency", "completed", "p50", "p95", "p99"])
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    asyncio.run(main())