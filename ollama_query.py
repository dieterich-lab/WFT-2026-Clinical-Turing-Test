import json
import os
import urllib.request

base = os.environ["OLLAMA_URL"]
model = os.environ["OLLAMA_MODEL"]

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