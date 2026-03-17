# Preparations for JupyterLab usage

## Quick overview

JupyterLab is available at https://jupyter.dieterichlab.org/ and uses your home directory as the workspace root. To use it remotely, enable the WireGuard VPN and ensure your cluster account is accessible.

## Access

SSH into the cluster first (this registers your home directory for JupyterLab):

```bash
ssh <username>@cluster.dieterichlab.org
```

If you need to expose files from other locations in your Jupyter home, create a symbolic link:

```bash
ln -s /path/to/shared/resource .
```

## Create a Python environment (recommended)

Using an isolated environment avoids dependency conflicts. Two common options:

- venv (standard library):

```bash
python3 -m venv ~/venvs/myenv
source ~/venvs/myenv/bin/activate
```

- conda (if you have it installed):

```bash
conda create --name myenv python=3.11
conda activate myenv
```

Update pip in the active environment:

```bash
python -m pip install --upgrade pip
```

Install common tools (example):

```bash
pip install ipykernel jupyterlab jupyterlab-server
```

## Register the kernel with Jupyter

Register your active environment so it appears as a kernel option in JupyterLab:

```bash
python -m ipykernel install --user --name=myenv --display-name="Python (myenv)"
```

Then start JupyterLab from your account (if provided as a service, just open the URL). In JupyterLab choose the kernel named "Python (myenv)" for notebooks that require your packages.

## Troubleshooting kernels and packages

- List registered kernels:

```bash
jupyter kernelspec list
```

- If a kernel is stale or incorrect, remove it and re-register:

```bash
jupyter kernelspec uninstall <kernel-name>
python -m ipykernel install --user --name=myenv --display-name="Python (myenv)"
```

- If a package is missing inside Jupyter but present locally, ensure you're using the notebook kernel associated with the environment where the package is installed.

## Tips for working in JupyterLab

- Start with an interactive terminal inside JupyterLab to verify `python --version` and `pip list`.
- Keep long-running training or heavy compute on batch jobs (use Slurm) rather than inside the web UI.
- Use `requirements.txt` or `environment.yml` to reproduce environments for students:

```bash
pip freeze > requirements.txt
# or for conda
conda env export > environment.yml
```

## Short checklist for students

1. Enable WireGuard if connecting remotely.
2. SSH to `cluster.dieterichlab.org` once to ensure your home directory is registered.
3. Create and activate an environment (`venv` or `conda`).
4. Install `ipykernel` and register the kernel with Jupyter.
5. Open https://jupyter.dieterichlab.org/, create a notebook, and switch to your environment kernel.

## Common commands

```bash
# create venv
python3 -m venv ~/venvs/myenv
source ~/venvs/myenv/bin/activate

# install kernel and tools
python -m pip install --upgrade pip
python -m pip install ipykernel jupyterlab
python -m ipykernel install --user --name=myenv --display-name="Python (myenv)"

# check kernels
jupyter kernelspec list
```

## Support

If you run into environment, access, or module issues, contact the instructors or the cluster admins. Provide the exact error message and the output of `python -V` and `jupyter kernelspec list` to help debugging.
