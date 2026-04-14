#!/bin/bash
#SBATCH --job-name=ollama_python_demo
#SBATCH --output=ollama_python_validation_%j.log
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
python3 llm_validation.py

echo "Done."