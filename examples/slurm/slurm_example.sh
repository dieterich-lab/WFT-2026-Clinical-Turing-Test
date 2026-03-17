#!/usr/bin/env bash
# Simple example Slurm job script for running a Python task
# Usage: sbatch examples/slurm/slurm_example.sh

#SBATCH --job-name=example_job
#SBATCH --output=slurm_example_%j.out
#SBATCH --partition=gpu
#SBATCH --gres=gpu:turing:1
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

echo "Running example job on $(hostname) (SLURM_JOB_ID=${SLURM_JOB_ID})"

echo "Environment: $(python3 -V 2>&1)"

# Replace the command below with your training or analysis command
python3 - <<'PY'
import time
print('Hello from example job')
for i in range(3):
    print('step', i+1)
    time.sleep(1)
PY

echo "Job finished"
