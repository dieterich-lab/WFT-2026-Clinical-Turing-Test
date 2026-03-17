#!/usr/bin/env bash
# Example Slurm script to start a JupyterLab server on an allocated node
# Usage: sbatch examples/jupyter/slurm_jupyter.sh

# SBATCH settings - adjust partition/gres/time as needed
#SBATCH --job-name=jupyter_lab
#SBATCH --output=examples/jupyter/jupyter_%j.out
#SBATCH --partition=interactive
#SBATCH --gres=gpu:turing:1
#SBATCH --mem=50G
#SBATCH --time=04:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

echo "Starting JupyterLab job on $(hostname) (SLURM_JOB_ID=${SLURM_JOB_ID})"

# Load modules or activate your environment here (adjust to your site)
module load anaconda || true
if command -v conda >/dev/null 2>&1; then
  # ensure conda is available in batch scripts
  source "$(conda info --base 2>/dev/null)/etc/profile.d/conda.sh" || true
  conda activate myenv || true
fi

# Port and bind address
PORT=${PORT:-8888}
BIND_IP=127.0.0.1

LOGFILE=examples/jupyter/jupyter_${SLURM_JOB_ID}.log
mkdir -p examples/jupyter

echo "Starting JupyterLab on ${BIND_IP}:${PORT}, logging to ${LOGFILE}"

# Start JupyterLab and redirect output to logfile
jupyter lab --no-browser --port=${PORT} --ip=${BIND_IP} &> "${LOGFILE}" &
JUPYTER_PID=$!

sleep 2
echo "JupyterLab PID: ${JUPYTER_PID}"

echo "--- Jupyter server log (tail) ---"
tail -n +1 "${LOGFILE}" | sed -n '1,200p'

echo "To find the token or URL, inspect the log file above or run on the node: jupyter server list"

echo "If you want to connect from your local machine, run (example):"
echo "  ssh -L ${PORT}:localhost:${PORT} -J <your-username>@cluster.dieterichlab.org <your-username>@$(hostname)"
echo "Then open http://localhost:${PORT}/ in your browser and paste the token from the log."

echo "Keep this job running while you work. To detach, consider starting Jupyter inside tmux: tmux new -s jupyter"

wait ${JUPYTER_PID}
