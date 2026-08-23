"""Streaming sensor assimilation stub for real-time twin synchronisation.
Consumes IoT/strong-motion messages and updates asset state as they arrive.
Replace the generator with a Kafka consumer in production."""
import json
import time

def sensor_stream(n=5):
    """Placeholder stream; yields JSON sensor messages."""
    for i in range(n):
        yield json.dumps({"asset_id": f"shm_{i%3}", "pga": 0.1 + 0.05 * i,
                          "ts": time.time()})

def assimilate(msg, state):
    d = json.loads(msg)
    prev = state.get(d["asset_id"], 0.0)
    # exponential update of the running peak intensity
    state[d["asset_id"]] = max(prev, d["pga"])
    if d["pga"] > 0.2:                    # alert threshold
        print(f"ALERT {d['asset_id']}: PGA={d['pga']:.2f} g -> re-run damage model")
    return state

state = {}
for msg in sensor_stream():
    state = assimilate(msg, state)
print("Latest peak PGA per asset:", state)
