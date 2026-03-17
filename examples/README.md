# Examples

This folder contains example Slurm scripts and helpers for running jobs and Jupyter on the cluster.

Files
- `jupyter/slurm_jupyter.sh`: Slurm script to launch JupyterLab on an allocated node. Submit with `sbatch examples/jupyter/slurm_jupyter.sh`. The script writes logs to `examples/jupyter/jupyter_<JOBID>.log` and prints SSH-tunnel instructions.
- `slurm/slurm_example.sh`: Minimal batch job example that runs a short Python snippet. Submit with `sbatch examples/slurm/slurm_example.sh`.

Quick usage

Start an interactive allocation and then use the jupyter script inside the allocation, or submit the `slurm_jupyter.sh` as a batch job (interactive partition recommended):

```bash
# make scripts executable (one-time)
chmod +x examples/jupyter/slurm_jupyter.sh examples/slurm/slurm_example.sh

# submit the example batch job
sbatch examples/slurm/slurm_example.sh

# submit the jupyter launcher (or run inside an interactive allocation)
sbatch examples/jupyter/slurm_jupyter.sh
```

Notes
- Adjust `--partition`, `--gres`, and module/environment activation inside the scripts to match your setup.
- These scripts are templates — please customize `conda`/`module` lines to your environment.
