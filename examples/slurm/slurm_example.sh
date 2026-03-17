#!/usr/bin/env bash
# Simple example Slurm job script for running a Python task
# Usage: sbatch examples/slurm/slurm_example.sh

#SBATCH --job-name=example_job
#SBATCH --output=examples/slurm/example_%j.out
#SBATCH --partition=compute
#SBATCH --gres=gpu:turing:1
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

echo "Running example job on $(hostname) (SLURM_JOB_ID=${SLURM_JOB_ID})"

# Load modules or activate your environment
module load anaconda || true
if command -v conda >/dev/null 2>&1; then
  source "$(conda info --base 2>/dev/null)/etc/profile.d/conda.sh" || true
  conda activate myenv || true
fi

mkdir -p examples/slurm

echo "Environment: $(python -V 2>&1)"

# Replace the command below with your training or analysis command
python - <<'PY'
import time
print('Hello from example job')
for i in range(3):
    print('step', i+1)
    time.sleep(1)
PY

echo "Job finished"
