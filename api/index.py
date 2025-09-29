from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import json
import statistics
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/")
async def telemetry_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)
    # Load telemetry bundle (assume telemetry.json in api/)
    bundle_path = os.path.join(os.path.dirname(__file__), "telemetry.json")
    with open(bundle_path, "r") as f:
        data = json.load(f)
    result = {}
    for region in regions:
        region_records = [r for r in data if r.get("region") == region]
        latencies = [r["latency_ms"] for r in region_records]
        uptimes = [r["uptime"] for r in region_records]
        breaches = sum(1 for l in latencies if l > threshold_ms)
        avg_latency = statistics.mean(latencies) if latencies else None
        p95_latency = statistics.quantiles(latencies, n=100)[94] if latencies else None
        avg_uptime = statistics.mean(uptimes) if uptimes else None
        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }
    return result
