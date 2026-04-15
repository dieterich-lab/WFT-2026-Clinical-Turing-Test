# Ollama on Slurm: Main Student Workflow

This is the main guide to run Ollama and query it from Python in one reproducible Slurm job.

If you are new, read these first:

1. [instructions/start_here.md](start_here.md)
2. [instructions/cluster.md](cluster.md)
3. [instructions/venv.md](venv.md)
4. [instructions/slurm.md](slurm.md)

If you need quick interactive debugging instead of a full batch script, use:

- [instructions/ollama_playground.md](ollama_playground.md)

---

## 1) Prerequisites

Make sure module loading and Ollama are available in your shell:

```bash
source /etc/profile.d/modules.sh
source /biosw/__modules__/modules.rc
module load ollama
```

Tip for Linux beginners: put these lines in `~/.bashrc` so they are loaded automatically in new shells.

## 2) Create your Python query file

Create `ollama_query.py`:

```python
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
```

## 3) Create the Slurm wrapper script

Create `slurm_ollama_python_demo.sh`:

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

export OLLAMA_PORT="11434"
export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_URL="http://127.0.0.1:11434"
export OLLAMA_KEEP_ALIVE="30m"
export OLLAMA_MODEL="llama3.1:8b"

if ! command -v ollama >/dev/null 2>&1; then
  echo "ERROR: ollama command not found"
  exit 1
fi

echo "Starting Ollama on ${OLLAMA_URL}"
ollama serve > "ollama_server_${SLURM_JOB_ID:-local}.log" 2>&1 &
OLLAMA_PID=$!

cleanup() {
  echo "Stopping Ollama (pid=${OLLAMA_PID})"
  kill "${OLLAMA_PID}" 2>/dev/null || true
  wait "${OLLAMA_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

for i in {1..60}; do
  if curl --silent --fail "${OLLAMA_URL}/api/tags" >/dev/null; then
    echo "Ollama is ready"
    break
  fi
  sleep 1
done

python ollama_query.py

echo "Done."
```

## 4) Submit and monitor

Submit:

```bash
sbatch slurm_ollama_python_demo.sh
```

Monitor:

```bash
squeue -u "$USER"
```

Inspect logs:

```bash
tail -n 100 ollama_python_demo_<JOBID>.log
tail -n 100 ollama_server_<JOBID>.log
```

## 5) Why the cleanup function matters

`trap cleanup EXIT INT TERM` means the shell will call `cleanup()` when:

- the script exits normally
- you interrupt it (`Ctrl+C`)
- Slurm/job termination sends a termination signal

This prevents orphaned Ollama processes.

## 6) Common fixes

- `ollama: command not found`
  - Load modules first (`module load ollama`).
- Job runs but no model response
  - Check `ollama_server_<JOBID>.log` for startup errors.
- `ModuleNotFoundError` in Python
  - Activate the correct venv before installing packages.
- Queue waiting too long
  - Try another GPU type from [instructions/cluster.md](cluster.md).

## 7) Next steps

- For iterative debugging: [instructions/ollama_playground.md](ollama_playground.md)
- For notebook work with your venv: [instructions/jupyterhub.md](jupyterhub.md)
