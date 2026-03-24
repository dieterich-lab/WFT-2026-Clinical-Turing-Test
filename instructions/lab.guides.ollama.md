# Using Ollama + Python in one SLURM wrapper script

This guide shows the **simplest pattern** for teaching students how to:

1) start an Ollama server inside a SLURM job  
2) run a Python request (via heredoc) against that server  
3) stop Ollama gracefully on exit

---

## 0) Prerequisites

Ensure module loading is available in your shell setup (as in your first guide):

```bash
source /etc/profile.d/modules.sh
source /biosw/__modules__/modules.rc
module load ollama
```

---

## 1) Create the wrapper script

### What is a SLURM script?

A SLURM script is just a normal shell script with extra `#SBATCH` lines at the top.
Those lines tell the scheduler what resources your job needs (GPU, memory, time, CPUs).

In this example, SLURM does three things for you:

1. allocates a compute node with a GPU  
2. runs your wrapper script on that node  
3. writes logs to the `--output` file

### Why wrap Ollama + Python in one script?

For teaching and reproducibility, a single wrapper script is easier than running steps manually.
The flow is:

1. start Ollama server in the background  
2. wait until it is ready  
3. run Python request(s) against `http://127.0.0.1:<port>`  
4. stop Ollama cleanly via `trap`

### What is a heredoc?

A heredoc lets you embed Python directly in a bash script:

```bash
python - <<'PY'
print("hello from embedded python")
PY
```

This is useful for demos and short jobs because students only submit one file.

Save as `slurm_ollama_python_demo.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=ollama_python_demo
#SBATCH --output=ollama_python_demo_%j.log
#SBATCH --partition=gpu
#SBATCH --gres=gpu:ampere:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=00:10:00

set -euo pipefail

# ---------- Config ----------
export OLLAMA_PORT="${OLLAMA_PORT:-11434}"
export OLLAMA_HOST="127.0.0.1:${OLLAMA_PORT}"
export OLLAMA_URL="http://${OLLAMA_HOST}"
export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:-30m}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.1:8b}"   # use a model available on your cluster

# ---------- Checks ----------
if ! command -v ollama >/dev/null 2>&1; then
  echo "ERROR: ollama command not found"
  exit 1
fi

# ---------- Start Ollama ----------
echo "Starting Ollama on ${OLLAMA_URL}"
ollama serve > "ollama_server_${SLURM_JOB_ID:-local}.log" 2>&1 &
OLLAMA_PID=$!

# Always clean up, even on Ctrl+C or job cancel
cleanup() {
  if [[ -n "${OLLAMA_PID:-}" ]] && kill -0 "${OLLAMA_PID}" >/dev/null 2>&1; then
    echo "Stopping Ollama (pid=${OLLAMA_PID})"
    kill "${OLLAMA_PID}" || true
    wait "${OLLAMA_PID}" || true
  fi
}
trap cleanup EXIT INT TERM

# ---------- Wait for readiness ----------
for i in {1..60}; do
  if curl --silent --fail "${OLLAMA_URL}/api/tags" >/dev/null; then
    echo "Ollama is ready"
    break
  fi
  sleep 1
done

# ---------- Python heredoc request ----------
python - <<'PY'
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
PY

echo "Done."
```

---

## 2) Submit and monitor

```bash
sbatch slurm_ollama_python_demo.sh
squeue -u "$USER"
```

When finished, check the output log:

```bash
tail -n 100 ollama_python_demo_<JOBID>.log
```

---

## 3) Teaching notes

- `trap cleanup EXIT INT TERM` is the key line for graceful shutdown.
- `OLLAMA_KEEP_ALIVE=30m` keeps models warm briefly between requests without leaving them loaded for too long.
- `OLLAMA_HOST=127.0.0.1:PORT` keeps everything local to the allocated node.
- The Python heredoc is intentionally minimal and avoids extra dependencies.
- For larger models, increase `--mem`, `--time`, and potentially GPUs.

---

## 4) Execution timeline (mental model)

When students run `sbatch slurm_ollama_python_demo.sh`, this is what happens:

1. **SLURM queues and allocates** a node with requested resources.  
2. **Wrapper script starts** on that node.  
3. **Ollama server starts** in background (`ollama serve &`).  
4. **Readiness check loops** until `/api/tags` responds.  
5. **Python heredoc runs** and sends one request to Ollama.  
6. **Script exits** and `trap` calls cleanup.  
7. **Ollama process is stopped gracefully** and logs remain in output files.

This timeline helps explain why one-file wrappers are robust: setup, execution, and cleanup are all in one reproducible job.
