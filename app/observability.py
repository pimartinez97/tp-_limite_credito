import json


def log_prediction(latency_ms, decision, model_version):
    print(
        json.dumps(
            {
                "event": "prediction",
                "latency_ms": round(latency_ms, 2),
                "decision": decision,
                "model_version": model_version,
            }
        ),
        flush=True,
    )
