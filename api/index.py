import json
import numpy as np
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry once at startup
with open("telemetry.json", "r") as f:
    TELEMETRY = json.load(f)

@app.post("/")
async def telemetry_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    results = {}

    for region in regions:
        # Filter data by region
        region_data = [d for d in TELEMETRY if d["region"] == region]
        if not region_data:
            continue

        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime_pct"] for d in region_data]

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = sum(1 for l in latencies if l > threshold)

        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 3),
            "breaches": breaches
        }

    return results
