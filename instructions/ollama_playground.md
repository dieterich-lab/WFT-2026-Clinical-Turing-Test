**Ollama playground (debugging) — start server on a GPU node, query from an interactive shell or JupyterHub**

Purpose: provide a lightweight, easy-to-use pattern for students to start an Ollama server on a dedicated GPU node and then query it from a separate interactive compute session (`srun`) or from JupyterHub for quick debugging and experimentation.

Files created by this guide:

- `slurm_ollama_server_playground.sh` — starts Ollama on a GPU node and writes the server URL to a file in your home directory.
- `ollama_query.py` — minimal Python example to POST a prompt to the server.

---

1) Start the Ollama server on a dedicated GPU node

Create `slurm_ollama_server_playground.sh` and submit it with `sbatch`.

```bash
#!/bin/bash
#SBATCH --job-name=ollama_server_playground
#SBATCH --output=ollama_server_playground_%j.log
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=50G
#SBATCH --time=04:00:00

set -euo pipefail

module load ollama

# ---------- Config ----------
export OLLAMA_PORT=11434
NODE=$(hostname -s)
export OLLAMA_URL="http://${NODE}:${OLLAMA_PORT}"
export OLLAMA_MODEL="llama3.1:8b"

# Write a discoverable file so clients can find the server URL
echo "${OLLAMA_URL}" > "$HOME/ollama_server_${SLURM_JOB_ID:-local}.url"

# ---------- Start Ollama ----------
# Start in background so the script can wait and keep the job alive
ollama serve > "ollama_server_${SLURM_JOB_ID:-local}.log" 2>&1 &
OLLAMA_PID=$!

cleanup() {
  echo "Stopping Ollama (pid=${OLLAMA_PID})"
  kill "${OLLAMA_PID}" 2>/dev/null || true
  wait "${OLLAMA_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Wait until Ollama is ready (same node)
for i in {1..60}; do
  if curl --silent --fail "${OLLAMA_URL}/api/tags" >/dev/null; then
    echo "Ollama is ready at ${OLLAMA_URL}"
    break
  fi
  sleep 1
done

# Block here so the job (and server) stay alive until cancelled or time limit
wait "${OLLAMA_PID}"
```

Submit it:

```bash
sbatch slurm_ollama_server_playground.sh
```

Notes:

- The script writes the server address to `~/ollama_server_<JOBID>.url` so clients can discover it.
- The job will keep running until the time limit or until you cancel it (`scancel JOBID`).

---

1) Querying the server from an interactive compute session (recommended for quick tests)

Open a separate interactive session on the cluster (compute/general partition):

```bash
srun -c 5 --mem=50G -p general --pty bash -i
```

Inside that interactive shell, follow these simple playground steps:

- Source your project virtual environment (example):

```bash
source ~/projects/myfirstproject/myfirstproject/bin/activate
```

- Discover and export the server URL (the server job wrote this file):

```bash
export OLLAMA_URL=$(ls -1 ~/ollama_server_*.url | tail -n1 && cat $(ls -1 ~/ollama_server_*.url | tail -n1))
export OLLAMA_MODEL="llama3.1:8b"
# Alternatively, set OLLAMA_URL manually if you know the node: export OLLAMA_URL="http://node-name:11434"
```

- Start an interactive Python session and run the minimal request (paste into the REPL):

```python
import os, json, urllib.request

base = os.environ.get('OLLAMA_URL')
model = os.environ.get('OLLAMA_MODEL', 'llama3.1:8b')

payload = {'model': model, 'prompt': 'Say one short sentence about medical AI.', 'stream': False}
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(f"{base}/api/generate", data=data, headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=120) as resp:
    body = json.loads(resp.read().decode('utf-8'))
print('Model:', model)
print('Response:', body.get('response', '').strip())
```

This flow keeps the playground fast: you source a venv, start Python, import a few modules, and paste the request. It avoids creating separate files and is ideal for iterative debugging.

If you prefer a reusable script, you can still create `ollama_query.py` and run `python ollama_query.py` as an alternative.

---

1) Querying from JupyterHub

If you prefer Jupyter, open a notebook via the class JupyterHub (see the class Jupyter guide). In a Python cell paste the same request code (the `urllib.request` snippet) or call the script with `%run ollama_query.py`. Before running the cell, set the environment variables in the notebook (or set them in the terminal that launched the notebook server):

```python
import os
os.environ['OLLAMA_URL'] = 'http://server-node:11434'  # or load from the URL file
os.environ['OLLAMA_MODEL'] = 'llama3.1:8b'
```

Then run the request cell.

---

Troubleshooting & security notes

- If the client cannot reach the server across nodes, your cluster may block node-to-node ports. In that case:
  - Run the client on the same node (use `srun --nodelist=<server_node> --pty bash -i`) so `127.0.0.1` works.
  - Or use `ssh -L` port forwarding from a login node to the server node if allowed.
- Keep playground jobs short and use small time limits to avoid blocking GPUs.
- This playground pattern is intended for debugging and small experiments only — do not expose models to untrusted networks.
