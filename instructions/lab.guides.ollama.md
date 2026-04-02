# Using Ollama + Python with SLURM (Beginner Version)

This guide shows a beginner-friendly pattern for students to:

1) start an Ollama server inside a SLURM job  
2) run a Python request from a normal Python file  
3) stop Ollama gracefully on exit

---

## 0) Prerequisites

Ensure module loading is available in your shell setup (as in your first guide):

```bash
source /etc/profile.d/modules.sh
source /biosw/__modules__/modules.rc
module load ollama
```

If you are new to Linux: there is a file called `.bashrc` in your home directory.
If you place these commands in `.bashrc`, they will be loaded automatically in every new shell session.

Example:

```bash
nano ~/.bashrc
# paste the 3 lines above anywhere in the file
source ~/.bashrc
```

This avoids repeating the setup manually every time they log in to the cluster.

---

## 1) Create the Python file

### What is a SLURM script?

A SLURM script is just a normal shell script with extra `#SBATCH` lines at the top.
Those lines tell the scheduler what resources your job needs (GPU, memory, time, CPUs).

In this example, SLURM does three things for you:

1. allocates a compute node with a GPU  
2. runs your wrapper script on that node  
3. writes logs to the `--output` file

Create `ollama_query.py` first:

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

---

## 2) Create the wrapper script

### Why wrap Ollama + Python in one script?

For teaching and reproducibility, a single wrapper script is easier than running steps manually.
The flow is:

1. start Ollama server in the background  
2. wait until it is ready  
3. run `python ollama_query.py`  
4. stop Ollama cleanly via `trap`

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
export OLLAMA_PORT="11434"
export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_URL="http://127.0.0.1:11434"
export OLLAMA_KEEP_ALIVE="30m"
export OLLAMA_MODEL="llama3.1:8b"   # use a model available on your cluster

# ---------- Checks ----------
if ! command -v ollama >/dev/null 2>&1; then
  echo "ERROR: ollama command not found"
  exit 1
fi

# ---------- Start Ollama ----------
echo "Starting Ollama on ${OLLAMA_URL}"
ollama serve > "ollama_server_${SLURM_JOB_ID:-local}.log" 2>&1 &
OLLAMA_PID=$!

# Cleanup function:
# - runs at script end and on interrupts/signals
# - tries to stop Ollama if still running
cleanup() {
  echo "Stopping Ollama (pid=${OLLAMA_PID})"
  kill "${OLLAMA_PID}" 2>/dev/null || true
  wait "${OLLAMA_PID}" 2>/dev/null || true
}

# Register cleanup(): shell calls it automatically on EXIT, Ctrl+C (INT), and TERM
trap cleanup EXIT INT TERM

# ---------- Wait for readiness ----------
for i in {1..60}; do
  if curl --silent --fail "${OLLAMA_URL}/api/tags" >/dev/null; then
    echo "Ollama is ready"
    break
  fi
  sleep 1
done

# ---------- Run Python file ----------
python ollama_query.py

echo "Done."
```

---

## 3) Submit and monitor

Use this sequence for your first SLURM job.

### Step 1: Submit the job with `sbatch`

`sbatch` is the SLURM command that sends your script to the scheduler.
The scheduler then finds a matching node (based on your `#SBATCH` settings) and runs the script there.

```bash
sbatch slurm_ollama_python_demo.sh
```

You will get output like:

```text
Submitted batch job 123456
```

The number (`123456`) is your **job ID**.

### Step 2: Check your queued/running jobs with `squeue`

Use `squeue` to monitor whether your job is waiting (`PD`) or running (`R`):

```bash
squeue -u "$USER"
```

Helpful version with custom columns:

```bash
squeue -u "$USER" -o "%.18i %.9P %.20j %.8T %.10M %.6D %R"
```

Interpretation:
- `PD` = Pending (still waiting for resources)
- `R` = Running
- `%R` column often tells you why it is pending (for example, waiting for GPU resources)

### Step 3: Check available partitions/nodes with `sinfo`

Use `sinfo` to understand which partitions are available and their status:

```bash
sinfo
```

This helps when troubleshooting why a job is waiting, for example if a partition is busy or drained.

### Step 4: Read logs when the job starts or finishes

When finished, check the output log:

```bash
tail -n 100 ollama_python_demo_<JOBID>.log
```

If you know the job ID, replace `<JOBID>` with that number.

Example:

```bash
tail -n 100 ollama_python_demo_123456.log
```

---

## 4) Teaching notes

- `trap cleanup EXIT INT TERM` is the key line for graceful shutdown.
- `OLLAMA_KEEP_ALIVE=30m` keeps models warm briefly between requests without leaving them loaded for too long.
- `OLLAMA_HOST=127.0.0.1:PORT` keeps everything local to the allocated node.
- `export OLLAMA_PORT="11434"` is valid shell syntax and explicitly sets a fixed value.
- For larger models, increase `--mem`, `--time`, and potentially GPUs.

---

## 5) Execution timeline (mental model)

When students run `sbatch slurm_ollama_python_demo.sh`, this is what happens:

1. **SLURM queues and allocates** a node with requested resources.  
2. **Wrapper script starts** on that node.  
3. **Ollama server starts** in background (`ollama serve &`).  
4. **Readiness check loops** until `/api/tags` responds.  
5. **Python file runs** (`python ollama_query.py`) and sends one request to Ollama.  
6. **Script exits** and `trap` calls cleanup.  
7. **Ollama process is stopped gracefully** and logs remain in output files.

This timeline helps explain why one-file wrappers are robust: setup, execution, and cleanup are all in one reproducible job.
