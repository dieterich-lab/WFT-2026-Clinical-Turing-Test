import json
import os
import urllib.request

base = os.environ.get("OLLAMA_URL")
if not base:
    raise SystemExit(
        "OLLAMA_URL not set. Load the URL file or set OLLAMA_URL in your environment."
    )

model = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")

payload = {
    "model": model,
    "prompt": "Say one short sentence about medical AI.",
    "stream": False,
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    f"{base}/api/generate",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(req, timeout=120) as resp:
    body = json.loads(resp.read().decode("utf-8"))

print("Model:", model)
print("Response:", body.get("response", "").strip())
