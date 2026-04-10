**Using Python virtual environments on the cluster**

- **Purpose:** Create an isolated Python environment for a project using `python -m venv`. This lets you install packages without sudo and avoids conflicts with system Python.

**Quick Start**

1. Pick a directory for your project and change into it:

```bash
mkdir -p ~/projects/myfirstproject
cd ~/projects/myfirstproject
```

2. Create a virtual environment named `myfirstproject`:

```bash
# Use python or python3 depending on what's available
python3 -m venv myfirstproject
```

3. Activate the environment:

```bash
source myfirstproject/bin/activate
```

After activation your shell prompt usually changes to show the venv name. While active, `pip install` will install into the venv only.

4. Install packages you need (example):

```bash
pip install numpy scipy jupyterlab
```

5. When done, deactivate:

```bash
deactivate
```

**Why this is helpful on the cluster**

- You do not need `sudo` to install packages inside the venv.
- Each project can have its own package versions, avoiding conflicts.
- Reproducibility: you can export a `requirements.txt` and recreate the environment later.

**Useful commands**

- Check Python path while venv is active:

```bash
which python
python --version
```

- Export installed packages:

```bash
pip freeze > requirements.txt
```

- Recreate environment from `requirements.txt`:

```bash
python3 -m venv myfirstproject
source myfirstproject/bin/activate
pip install -r requirements.txt
```

**Troubleshooting**

- If `python3` is not available, try `python`.
- If `venv` module is missing (rare), install `python3-venv` in a personal environment or ask the sysadmin. Typically on shared clusters `venv` is available.

**Tips for working with Jupyter on the cluster**

- To use this venv with Jupyter, install `ipykernel` and register a kernel:

```bash
source myfirstproject/bin/activate
pip install ipykernel
python -m ipykernel install --user --name=myfirstproject --display-name "Python (myfirstproject)"
```

- Then in Jupyter choose the kernel named "Python (myfirstproject)".

---

If you want, I can: add this guide to a README index, create a short slide for students, or write a companion guide that uses `virtualenv` or `conda`. What would you like next?