import argparse
import json
import time
import urllib.request


parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True)
parser.add_argument("--n", type=int, default=100)
args = parser.parse_args()

with open("data/fixtures/customer-example.json") as file:
    payload = json.load(file)

latencies = []
status_codes = []

for _ in range(args.n):
    request = urllib.request.Request(
        f"{args.url.rstrip('/')}/predict",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    try:
        with urllib.request.urlopen(request) as response:
            status_codes.append(response.status)
    except urllib.error.HTTPError as error:
        status_codes.append(error.code)

    latencies.append((time.perf_counter() - start) * 1000)

latencies.sort()

def percentile(values, p):
    index = int((len(values) - 1) * p)
    return values[index]

print(f"requests: {args.n}")
print(f"status 200: {status_codes.count(200)}")
print(f"errores: {args.n - status_codes.count(200)}")
print(f"p50_ms: {percentile(latencies, 0.50):.2f}")
print(f"p95_ms: {percentile(latencies, 0.95):.2f}")
print(f"p99_ms: {percentile(latencies, 0.99):.2f}")
