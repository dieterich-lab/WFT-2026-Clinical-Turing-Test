# Dieterichlab Cluster Guide

This guide explains how to access and understand the cluster resources used in this project.

## 1) Access

If you are outside the clinic network, connect WireGuard first.
Then log in:

```bash
ssh <username>@cluster.dieterichlab.org
```

If SSH does not work, fix VPN/access first before debugging Slurm jobs.

## 2) Quick cluster facts

These values are taken from current Slurm configuration (`/etc/slurm/slurm.conf` and `/etc/slurm/gres.conf`).

- GPU GRES enabled: `gpu`
- Default partition: `general`
- Main GPU partition: `gpu`

GPU nodes currently configured:

- `gpu-g1-1`: 2x `pascal` GPUs
- `gpu-g1-2`: 2x `pascal` GPUs
- `gpu-g2-1`: 4x `turing` GPUs
- `gpu-g3-1`: 4x `turing` GPUs
- `gpu-g4-1`: 4x `ampere` GPUs
- `gpu-g5-1`: 3x `hopper` GPUs

That means requests like these are valid:

```bash
#SBATCH --gres=gpu:ampere:1
#SBATCH --gres=gpu:turing:1
#SBATCH --gres=gpu:hopper:1
```

## 3) GPU VRAM and Ollama model fit (practical guide)

For this course, students usually choose models by VRAM first.

Approximate VRAM per GPU architecture in this cluster:

- `pascal`: about 8 GB VRAM
- `turing`: about 24 GB VRAM
- `ampere`: about 40 GB VRAM
- `hopper`: about 80 GB VRAM

Examples from Ollama model sizes (library pages):

- `gpt-oss:20b` is about 14 GB
- `gpt-oss:120b` is about 65 GB
- `qwen3:30b` is about 19 GB
- `qwen3.5:27b` is about 17 GB
- `qwen3.5:35b` is about 24 GB
- `qwen2.5:32b` is about 20 GB
- `qwen2.5:72b` is about 47 GB

What this means in practice:

- `turing` (24 GB): good default for `gpt-oss:20b`, `qwen3:30b`, `qwen3.5:27b`, `qwen2.5:32b`
- `ampere` (40 GB): same models with more headroom; often more robust for longer contexts and near-limit models like `qwen3.5:35b`
- `hopper` (80 GB): needed for very large models such as `gpt-oss:120b`; also fits `qwen2.5:72b`
- `pascal` (8 GB): use smaller models (for example around 7B/8B class)

Important: model file size is not the same as total runtime memory.
Real memory usage also depends on context length, batching, and serving overhead.
When in doubt, start one class smaller and verify with `nvidia-smi`.

## 4) Partitions you should know

- `general` (default): CPU jobs, short general compute
- `gpu`: main GPU workloads

Inspect live state any time:

```bash
sinfo
```

## 5) Basic Slurm commands

```bash
# show partitions/nodes
sinfo

# show your jobs
squeue -u "$USER"

# cancel a job
scancel <JOBID>
```

## 6) Interactive vs batch use

- Use `srun` for quick tests and debugging.
- Use `sbatch` for reproducible runs and long jobs.

Example interactive session:

```bash
srun --partition=interactive --time=00:10:00 --pty bash -i
```

Example batch script header for one Ampere GPU:

```bash
#SBATCH --partition=gpu
#SBATCH --gres=gpu:ampere:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=00:30:00
```

## 7) How to choose GPU type

Use the smallest GPU that fits your model.
A practical order for this course:

1. `turing` for most class exercises and medium models
2. `ampere` for larger models or more context headroom
3. `hopper` for very large models

If your job waits too long in queue, try a different compatible GPU type.

## 8) Common beginner issues

- Requesting unavailable resources (wrong `--gres` type/count).
- Forgetting to activate your Python venv inside job scripts.
- Running long experiments in interactive sessions.
- Not checking log files after job completion.

## 9) Recommended next guides

1. [instructions/venv.md](venv.md)
2. [instructions/slurm.md](slurm.md)
3. [instructions/ollama.md](ollama.md)
