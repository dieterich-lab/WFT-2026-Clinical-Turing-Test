# Using CPUs/GPUs on the Dieterichlab Cluster

## Contact & Login

Besides running scripts for visualization and testing on the JupyterLab playground, you will eventually be in need to run larger programs on our cluster. Be aware that you have to enable the WireGuard VPN Tunnel with the IP adress that you received from H. Wilhelmi to connect from outside the clinic network on our cluster.  You can access your home directory on our cluster `cluster.dieterichlab.org` via `ssh`:

# Using CPUs/GPUs on the Dieterichlab Cluster

## Quick overview

This guide helps you get started using the Dieterichlab cluster for CPU/GPU jobs. Key tasks:

- Connect via SSH (WireGuard VPN required when offsite).
- Use `srun` for interactive debugging and `sbatch` for batch jobs.
- Inspect resources with `sinfo`, `squeue`, and `gres.conf`.

## Access & prerequisites

- If you're offsite, enable the WireGuard VPN and use the IP assigned by the instructors.
- SSH into the cluster:

```bash
ssh <username>@cluster.dieterichlab.org
```

- Load environment modules as needed (ask instructors for required modules):

```bash
module load <module-name>
```

## Quickstart: run a batch job (sbatch)

Create a job script (see `../scripts/slurm.sh` for an example). Example header for a GPU job:

```bash
#SBATCH --gres=gpu:turing:1
#SBATCH --job-name=my_job
#SBATCH --output=logs/my_job.out
#SBATCH --partition=gpu
#SBATCH --mem=32G

# command to run, e.g.:
python train.py --config configs/exp.yaml
```

Submit the job:

```bash
sbatch slurm.sh
```

Check your jobs:

```bash
squeue -u $(whoami)
```

Cancel a job:

```bash
scancel <JOBID>
```

What the common SBATCH options mean:

- `--gres=gpu:turing:1`: request GPU resources (type `turing` here).
- `--job-name`: job label shown in queues.
- `--output`: file capturing stdout/stderr.
- `--partition`: partition to run on (use `sinfo` to inspect).
- `--mem`: memory reservation (e.g. `32G`).
- `--nodelist=gpu-g2-1`: optional pin to a specific node.

## Interactive sessions (srun)

For debugging or development you can request an interactive shell on a compute node:

```bash
srun --gres=gpu:turing:1 -p gpu --mem=50G --pty bash -i
```

This opens a shell on a `turing` node (e.g. `gpu-g2-1`) with one GPU and 50 GB memory. Use it to iterate quickly and test commands before submitting batch jobs.

## Inspecting cluster resources

- Show partitions and node availability:

```bash
sinfo -s
```

- Example partition layout (admin output may vary): the `gpu` and `interactive` partitions contain GPU nodes used for computations.

- Nodes and typical GPU types:

  * `gpu-g1-1`, `gpu-g1-2`: Pascal GPUs (8 GB VRAM each)
  * `gpu-g2-1`: Turing GPUs (24 GB VRAM each)
  * `gpu-g3-1`: Turing GPUs (24 GB VRAM each)
  * `gpu-g4-1`: Ampere GPUs (40 GB VRAM each)

- Inspect configured generic resources (gres):

```bash
cat /etc/slurm/gres.conf
```

Use matching `--gres=gpu:<type>:<count>` in your SBATCH header to request the appropriate GPU type.

## Useful commands and tips

- Tail job output as it runs:

```bash
tail -f logs/my_job.out
```

- Show recent jobs and status:

```bash
squeue -u $(whoami)
```

- When debugging, test inside an interactive `srun` session, then convert to `sbatch` for long runs.
- If you need specific modules loaded or access issues, contact the cluster admins or instructors.

## Checklist for students

1. Enable WireGuard VPN if connecting remotely.
2. SSH to `cluster.dieterichlab.org` and `cd` to your project folder.
3. Load required modules (ask instructors if unsure).
4. Use `srun` interactively for debugging and `sbatch` for production runs.

## References & support

- Cluster Wiki: https://redmine.dieterichlab.org/projects/infrastructure/wiki/Server
- Slurm documentation: https://slurm.schedmd.com/documentation.html

If anything is unclear or a resource is missing, raise an issue with the instructors or cluster admins.
