# Start Here: Student Pipeline Guide

If this is your first semester project on a cluster, use this exact order:

1. WireGuard VPN
2. Cluster basics (SSH + Slurm concepts)
3. Python virtual environment (`venv`)
4. Slurm job workflow (`srun`/`sbatch`)
5. Ollama on Slurm + Python query
6. Optional: register `ipykernel` + use JupyterHub

Use this file as your map through the other guides.

---

## Quick navigation

- VPN setup: [instructions/wireguard.md](wireguard.md)
- Cluster concepts and GPU types: [instructions/cluster.md](cluster.md)
- Python environment without sudo: [instructions/venv.md](venv.md)
- Slurm beginner commands: [instructions/slurm.md](slurm.md)
- Ollama + Python (main workflow): [instructions/ollama.md](ollama.md)
- Ollama playground (debugging workflow): [instructions/ollama_playground.md](ollama_playground.md)
- JupyterHub + kernels: [instructions/jupyterhub.md](jupyterhub.md)

---

## Minimal onboarding checklist

1. Enable WireGuard and confirm connection.
2. SSH login works:

```bash
ssh <username>@cluster.dieterichlab.org
```

3. Create and activate your venv:

```bash
python3 -m venv ~/venvs/ctt
source ~/venvs/ctt/bin/activate
python -m pip install --upgrade pip
```

4. Verify Slurm basics:

```bash
sinfo
squeue -u "$USER"
```

5. Run one interactive test session:

```bash
srun --partition=interactive --time=00:10:00 --pty bash -i
```

6. Run one batch job with Ollama using [instructions/ollama.md](ollama.md).

---

## Which guide should I use right now?

- "I cannot reach cluster resources": start with [instructions/wireguard.md](wireguard.md).
- "I can SSH, but I do not understand partitions/GPUs": read [instructions/cluster.md](cluster.md) and [instructions/slurm.md](slurm.md).
- "I cannot install Python packages": read [instructions/venv.md](venv.md).
- "I need the first working Ollama call": follow [instructions/ollama.md](ollama.md).
- "My Ollama script fails and I need fast debugging": use [instructions/ollama_playground.md](ollama_playground.md).
- "I want notebooks with my own environment": follow [instructions/jupyterhub.md](jupyterhub.md).