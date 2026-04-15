# JupyterHub Guide for Students

This guide explains how to start using JupyterHub on the Dieterichlab infrastructure for the first time.

## 1) What JupyterHub is used for

Use JupyterHub for:

- notebook prototyping
- data exploration
- quick tests

Use Slurm batch jobs (`sbatch`) for:

- long training runs
- heavy GPU/CPU jobs
- experiments that should continue when your browser closes

## 2) Prerequisites

Before opening JupyterHub, make sure all of the following are true:

1. You have a cluster account.
2. If you are offsite, your WireGuard VPN is connected.
3. You can log in via SSH.

```bash
ssh <username>@cluster.internal
```

Your first SSH login is important so your home directory and permissions are initialized correctly.

## 3) Open JupyterHub

Open:

- https://jupyter.dieterichlab.org/

Log in with your cluster credentials.

After login, your workspace root is your home directory.

If you need to expose a shared folder in your home, create a symbolic link once:

```bash
ln -s /path/to/shared/resource ~/shared_resource
```

## 4) Create a Python environment (once per project)

If you do not have an environment yet, create one with `venv` (or use `conda`).
For full details see [instructions/venv.md](venv.md).

Example with `venv`:

```bash
python3 -m venv ~/venvs/myenv
source ~/venvs/myenv/bin/activate
python -m pip install --upgrade pip
```

## 5) Register your environment as a Jupyter kernel

This is the step students most often miss.
Install and register `ipykernel` from the active environment:

```bash
source ~/venvs/myenv/bin/activate
python -m pip install ipykernel
python -m ipykernel install --user --name myenv --display-name "Python (myenv)"
```

Then in JupyterHub, create/open a notebook and choose kernel:

- `Python (myenv)`

## 6) Quick sanity check inside a notebook

In a new notebook cell, run:

```python
import sys
print(sys.executable)
```

The printed path should point to your environment (for example `.../venvs/myenv/...`).

## 7) Common commands

```bash
# list kernels visible to Jupyter
jupyter kernelspec list

# remove and recreate a broken kernel
jupyter kernelspec uninstall myenv
source ~/venvs/myenv/bin/activate
python -m ipykernel install --user --name myenv --display-name "Python (myenv)"

# freeze environment for reproducibility
pip freeze > requirements.txt
```

## 8) Troubleshooting (first experience)

### I can open VPN but not JupyterHub

- Verify VPN is active.
- Test SSH access first:

```bash
ssh <username>@cluster.internal
```

- If SSH fails, fix access first before troubleshooting JupyterHub.

### JupyterHub opens, but my kernel is missing

- Re-activate your environment.
- Re-run the `ipykernel install` command.
- Refresh the browser and re-open the notebook launcher.

### Package installed in terminal, but notebook says ModuleNotFoundError

- You are probably using the wrong kernel.
- In notebook: `Kernel -> Change Kernel` and select `Python (myenv)`.
- Re-run:

```python
import sys
print(sys.executable)
```

### Notebook is slow or disconnected during heavy runs

- This is expected for long jobs in web sessions.
- Move heavy workloads to Slurm (`sbatch`) and keep JupyterHub for interactive work.

## 9) Student checklist

1. Connect VPN (if offsite).
2. SSH once to cluster.
3. Open JupyterHub URL.
4. Create/activate project environment.
5. Install and register `ipykernel`.
6. Select the correct kernel in notebook.
7. Verify `sys.executable` points to your environment.

## 10) Support

If something does not work, send instructors/admins:

1. exact command(s) you ran
2. full error message
3. output of `jupyter kernelspec list`
4. output of `python -V`
