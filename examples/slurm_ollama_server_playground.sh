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
