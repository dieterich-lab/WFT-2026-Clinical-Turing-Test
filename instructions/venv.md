# Python Virtual Environment Guide for Students

Use this guide to create an isolated Python environment on the cluster.
This is required because students do not have sudo rights.

## 1) Why venv is required

A virtual environment lets you:

- install packages without sudo
- avoid conflicts between projects
- keep runs reproducible with `requirements.txt`

## 2) Create a project folder

```bash
mkdir -p ~/projects/myfirstproject
cd ~/projects/myfirstproject
```

## 3) Create and activate your venv

```bash
python3 -m venv my_env
source my_env/bin/activate
```

If `python3` is unavailable, try `python`.

After activation, your prompt usually shows `(my_env)`.

## 4) Install packages inside the venv

```bash
python -m pip install --upgrade pip
pip install numpy scipy
```

All package installs now go into `my_env`.

## 5) Verify the active interpreter

```bash
which python
python --version
```

`which python` should point to your project `my_env` path.

## 6) Save and restore dependencies

Export:

```bash
pip freeze > requirements.txt
```

Recreate later:

```bash
python3 -m venv my_env
source my_env/bin/activate
pip install -r requirements.txt
```

## 7) Use this venv in JupyterHub (optional)

Register your environment as a kernel:

```bash
source my_env/bin/activate
pip install ipykernel
python -m ipykernel install --user --name=myfirstproject --display-name "Python (myfirstproject)"
```

Then select `Python (myfirstproject)` in JupyterHub notebooks.

## 8) Deactivate when done

```bash
deactivate
```

## 9) Troubleshooting

### pip installs to wrong location

- You are likely outside the venv.
- Re-run `source my_env/bin/activate`.

### ModuleNotFoundError in notebook

- Notebook kernel is different from your venv.
- Switch kernel to `Python (myfirstproject)`.

### venv command fails

- Try `python -m venv my_env` instead of `python3`.
- If venv is missing on the system, ask instructors/admin.

## 10) Next step in onboarding

Continue with:

1. [instructions/slurm.md](slurm.md)
2. [instructions/ollama.md](ollama.md)
3. [instructions/jupyterhub.md](jupyterhub.md)
