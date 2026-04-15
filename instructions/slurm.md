# Slurm Basics for Students

This guide explains the minimum Slurm workflow you need for this project.

## 1) Core idea

You do not run heavy work directly on login nodes.
Instead, you request resources from Slurm:

- `srun` for interactive sessions
- `sbatch` for reproducible batch jobs

## 2) Most important commands

```bash
# show partitions and node states
sinfo

# show your jobs
squeue -u "$USER"

# cancel a job
scancel <JOBID>
```

## 3) Interactive session (`srun`)

Use this when debugging commands quickly:

```bash
srun --partition=interactive --time=00:10:00 --pty bash -i
```

Interactive sessions are short by design. For real experiments, switch to `sbatch`.

## 4) Batch job (`sbatch`)

Create a script file, for example `slurm_test.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=slurm_test
#SBATCH --output=slurm_test_%j.log
#SBATCH --partition=gpu
#SBATCH --gres=gpu:ampere:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=00:10:00

set -euo pipefail
hostname
nvidia-smi || true
python -V
```

Submit:

```bash
sbatch slurm_test.sh
```

Monitor:

```bash
squeue -u "$USER"
```

Read logs:

```bash
tail -n 100 slurm_test_<JOBID>.log
```

## 5) How GPU requests work

GPU request format:

`--gres=gpu:<type>:<count>`

Examples:

- `--gres=gpu:ampere:1`
- `--gres=gpu:turing:1`
- `--gres=gpu:hopper:1`

Use [instructions/cluster.md](cluster.md) to check currently available GPU types and node composition.

## 6) Beginner mistakes to avoid

- Forgetting `--output` and then not knowing where logs are.
- Running heavy scripts in an interactive shell for hours.
- Requesting a GPU type that does not exist.
- Installing Python packages outside your active venv.

## 7) Next step

After this guide, continue with [instructions/ollama.md](ollama.md) to run an Ollama server and query it from Python inside a Slurm job.
