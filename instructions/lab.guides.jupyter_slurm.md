---
id: w8lmqsve7rl2rhd1q59agyc
title: Jupyter_notebook
desc: ''
updated: 1756808664888
created: 1746627717513
---

# Using Jupyter Notebooks with Slurm (VSCode workflows)

This guide shows two friendly workflows to run notebooks on GPU nodes allocated by Slurm:

- Workflow A — VSCode Remote-SSH to the compute node and connect VSCode to the remote Jupyter server (recommended for VSCode users).
- Workflow B — Start Jupyter on the compute node and access it locally via SSH port forwarding (useful if you prefer the browser).

Prerequisites
-------------

- SSH access to the cluster and compute nodes (ask instructors if you need direct node access).
- If working from outside the clinic network, enable WireGuard VPN first.
- VSCode with the Remote - SSH extension (for Workflow A).

Common preparation
------------------

1. Start an interactive Slurm allocation on a GPU node (example; adjust `--gres` to your GPU type):

```bash
srun --gres=gpu:turing:1 -p gpu --mem=50G --pty bash -i
```

2. Inside the allocated session, create or activate your environment and optionally start `tmux` to keep sessions alive.

```bash
module load anaconda  # if you use modules; adjust as needed
conda activate myenv  # or source ~/venvs/myenv/bin/activate
tmux new -s jupyter
```

Workflow A — VSCode Remote-SSH (recommended)
-------------------------------------------

1. Configure an SSH host (optional, for convenience) in `~/.ssh/config`:

```ssh
Host gpu-node
    HostName gpu-g5-1.cluster.dieterichlab.org  # or the node IP
    User <your-username>
```

2. In VSCode: `Remote-SSH: Connect to Host` → select the configured host (or connect via the cluster jump host and then `srun` to a node).

3. In the VSCode remote terminal request an interactive Slurm node (see above) or connect directly if you already have node access.

4. Start JupyterLab on the compute node (bind to localhost for security):

```bash
jupyter lab --no-browser --port=8888 --ip=127.0.0.1
```

5. Copy the displayed Jupyter URL with token (it will look like `http://127.0.0.1:8888/?token=...`).

6. In VSCode choose the kernel selector → `Existing Jupyter Server` → paste the URL. Because VSCode is connected to the remote host, `localhost` refers to the remote node and the connection will work directly.

Notes for Workflow A
--------------------

- This is the simplest for VSCode users — no manual port forwarding is required when VSCode is connected to the node.
- Use `tmux` to keep the server running if your VSCode session disconnects.

Workflow B — Local browser via SSH port-forward (alternate)
---------------------------------------------------------

Use this if you prefer opening the notebook in your local browser.

1. From your local machine, create an SSH tunnel to the compute node (replace `<node>` with the node hostname or IP):

```bash
ssh -L 8888:localhost:8888 <your-username>@<node>
```

If you cannot SSH directly to the compute node, forward through the login (jump) host:

```bash
ssh -L 8888:localhost:8888 -J <your-username>@cluster.dieterichlab.org <your-username>@<node>
```

2. On the compute node (either in the same SSH session or an `srun` interactive allocation), start JupyterLab bound to localhost:

```bash
jupyter lab --no-browser --port=8888 --ip=127.0.0.1
```

3. In your local browser open `http://localhost:8888/?token=...` using the token displayed by the Jupyter server.

Notes for Workflow B
--------------------

- Ensure the `ssh -L` session remains open while you use the notebook.
- If the compute node is not directly reachable, use the `-J` jump host option as shown.

Security and persistence
------------------------

- Bind Jupyter to `127.0.0.1` (localhost) to avoid exposing it publicly.
- Use the token or configure a password for the server if desired.
- Keep the server running inside `tmux` or `screen` to survive disconnects:

```bash
tmux new -s jupyter
jupyter lab --no-browser --port=8888 --ip=127.0.0.1
# detach with Ctrl-b d
```

Troubleshooting
---------------

- No token shown? Check the Jupyter log lines for `token=` or run `jupyter server list` on the node to show active servers.
- Port already in use? Choose another port like `--port=8889` and forward that instead.
- VSCode can't connect? Ensure you're connected with Remote-SSH to the same host where the server runs; paste the exact URL returned by JupyterLab.

Tips and best practices
-----------------------

- For heavy training, prefer submitting a batch job with `sbatch` and run notebooks for prototyping only.
- Save long-running outputs and models to your home directory or a mounted shared storage — not the node's local ephemeral storage.
- Keep a small example notebook that reproduces your run steps; this helps students and debugging.

Example minimal commands (quick copy)
-------------------------------------

```bash
# request interactive allocation
srun --gres=gpu:turing:1 -p gpu --mem=50G --pty bash -i

# start tmux and jupyter
tmux new -s jupyter
jupyter lab --no-browser --port=8888 --ip=127.0.0.1

# from local machine: ssh tunnel (if not using VSCode Remote-SSH)
ssh -L 8888:localhost:8888 -J <user>@cluster.dieterichlab.org <user>@gpu-g5-1
```

Support
-------

If you run into issues, provide the exact commands you used and the server log output (or `jupyter server list`). Instructors or admins can help with access, firewall, or module issues.
