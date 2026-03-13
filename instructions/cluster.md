# Using CPUs/GPUs on the Dieterichlab Cluster

## Contact & Login

Besides running scripts for visualization and testing on the JupyterLab playground, you will eventually be in need to run larger programs on our cluster. Be aware that you have to enable the WireGuard VPN Tunnel with the IP adress that you received from H. Wilhelmi to connect from outside the clinic network on our cluster.  You can access your home directory on our cluster `cluster.dieterichlab.org` via `ssh`:

```bash
ssh <username>@cluster.dieterichlab.org
```

On the cluster, we use the [Slurm workload manager](https://slurm.schedmd.com/documentation.html) as our queing system to distribute resources. It provides commands and scripts to request resources (CPUs/GPUs) and queue your scripts into the pipeline of waiting jobs.

## Schedule jobs

You can start using slurm commands to distribute your jobs onto our CPU / GPU nodes. For these purposes, we provide you with a [sample script](../scripts/slurm.sh) that can be run with the `sbatch` command to tell slurm to queue the command given in the script as job on the specific node. The first part of the script are the slurm settings that - in this case- setup a job on GPU:

```bash
#SBATCH --gres=gpu:turing:1
#SBATCH --job-name=<your job name>
#SBATCH --output=<path to your output file>
#SBATCH --partition=gpu
#SBATCH --mem=32G
```

Explanation:

- `--gres=gpu:turing:1` is necessary when querying GPUs and tells slurm to 
  - requests a **gen**eric **r**esource, namly a gpu 
  - requests a gpu of the configuration **turing**, which includes the two nodes `gpu-g2-1` and `gpu-g3-1` with each 4x NVIDIA Quadro RTX 6000
  - to reserve `1` gpu for your job
- `--jobname=<...>` allocates a job name for your job, e.g. "my program"
- `output=<..>` writes all the outputs from the standard output to this file (e.g. `print` statements in python)
- `partition=gpu` determines the partition `GPU` which contains all nodes with GPUs.(see command `sinfo` explained below to get )
- `--mem=32G` reserves 32 GigaByte RAM for your job (32 Gigabyte should be usually suffiencent for your experiments)
- you could also specify a specific GPU node from the `turing` configuration with `--nodelist=gpu-g2-1` for example.

The final line begins with `srun` and states that the follwing command should be executed with the specifications set up with the `SBATCH` configuration.

You can start your script with by executing `sbatch slurm.sh`. Once your job started you will see it in the queue with the command `squeue`:

```bash
  JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
 130334 interacti     test pwiesenb  R       0:08      1 gpu-g4-1
```

And you can cancel it with the job-id and the command `scancel`:

```bash
scancel 130334
```

## Interactive jobs

It's also possible to request a node on which you can jump directly and play around interactively. To do so, you can also apply the following command directly from the terminal. This will be of optimal usage for you when you want to run your programs directly from command line on GPU (especially when debugging).

``` bash
srun --gres=gpu:turing:1 -p gpu --mem=50G --pty bash -i
```

This will send you on a bash on the turing configuartion (so either `gpu-g2-1` or `gpu-g3-1`) 1 CP and 50 GB of memory.

## Infrastructure 

For a general overview of our cluster configuration and the available nodes you may have a look at our [cluster Wiki](https://redmine.dieterichlab.org/projects/infrastructure/wiki/Server).

There are also 2 ways to inspect our slurm environment. 

1. The first is `sinfo` which will display all the **partitions** with their included *nodes* and their *time limit*. 

    ```bash
    PARTITION   AVAIL  TIMELIMIT  NODES  STATE NODELIST
    small          up 7-00:00:00      8    mix slurm-c-mk1-1b,slurm-c-mk1-1c,slurm-c-mk1-1d,slurm-c-mk1-4a,slurm-c-mk1-4c,slurm-c-mk1-6a,slurm-c-mk1-6b,slurm-c-mk1-6c
    medium         up 7-00:00:00     10   idle gpu-g1-[1-2],slurm-c-mk2-1a,slurm-c-mk2-1b,slurm-c-mk2-1c,slurm-c-mk2-1d,slurm-c-mk2-2a,slurm-c-mk2-2b,slurm-c-mk2-2c,slurm-c-mk2-2d
    large          up 7-00:00:00      2   idle gpu-g1-[1-2]
    gpu            up 90-00:00:0      1    mix gpu-g3-1
    gpu            up 90-00:00:0      4   idle gpu-g1-[1-2],gpu-g2-1,gpu-g4-1
    general*       up 1-00:00:00      8    mix slurm-c-mk1-1b,slurm-c-mk1-1c,slurm-c-mk1-1d,slurm-c-mk1-4a,slurm-c-mk1-4c,slurm-c-mk1-6a,slurm-c-mk1-6b,slurm-c-mk1-6c
    general*       up 1-00:00:00      8   idle slurm-c-mk2-1a,slurm-c-mk2-1b,slurm-c-mk2-1c,slurm-c-mk2-1d,slurm-c-mk2-2a,slurm-c-mk2-2b,slurm-c-mk2-2c,slurm-c-mk2-2d
    interactive    up   10:00:00      9    mix gpu-g3-1,slurm-c-mk1-1b,slurm-c-mk1-1c,slurm-c-mk1-1d,slurm-c-mk1-4a,slurm-c-mk1-4c,slurm-c-mk1-6a,slurm-c-mk1-6b,slurm-c-mk1-6c
    interactive    up   10:00:00     12   idle gpu-g1-[1-2],gpu-g2-1,gpu-g4-1,slurm-c-mk2-1a,slurm-c-mk2-1b,slurm-c-mk2-1c,slurm-c-mk2-1d,slurm-c-mk2-2a,slurm-c-mk2-2b,slurm-c-mk2-2c,slurm-c-mk2-2d
    long           up 90-00:00:0      8    mix slurm-c-mk1-1b,slurm-c-mk1-1c,slurm-c-mk1-1d,slurm-c-mk1-4a,slurm-c-mk1-4c,slurm-c-mk1-6a,slurm-c-mk1-6b,slurm-c-mk1-6c
    ```

    So, when you want to make gpu computations you will see that you have to choose the `gpu` (or `interactive` for shorter runtimes and debugging) partition, as it includes all our gpu nodes

    *  `gpu-g1-1` & `gpu-g1-2`: 2 x 2 Pascal GPUs with 8 GB VRAM each.
    *  `gpu-g2-1`: 1 x 4 Turing GPUs with 24 GB VRAM each.
    *  `gpu-g3-1`: 1 x 4 Turing GPUs with 24 GB VRAM each.
    *  `gpu-g4-1`: 1 x 4 Ampere GPUs with 40 GB VRAM each.

2. You also need to know the names for "generic resource configurations" (gres). Luckily, they are encoded as the archictecture names stated above and can be inspected in the following file:

    ```bash
    cat /etc/slurm/gres.conf
    # Configure support for four GPUs (with MPS), plus bandwidth
    #AutoDetect=nvml

    # NodeName=proteus AutoDetect=nvml

    NodeName=gpu-g4-1 Name=gpu Type=ampere  File=/dev/nvidia0
    NodeName=gpu-g4-1 Name=gpu Type=ampere  File=/dev/nvidia1
    NodeName=gpu-g4-1 Name=gpu Type=ampere  File=/dev/nvidia2
    NodeName=gpu-g4-1 Name=gpu Type=ampere  File=/dev/nvidia3

    NodeName=gpu-g2-1 Name=gpu Type=turing  File=/dev/nvidia0
    NodeName=gpu-g2-1 Name=gpu Type=turing  File=/dev/nvidia1
    NodeName=gpu-g2-1 Name=gpu Type=turing  File=/dev/nvidia2
    NodeName=gpu-g2-1 Name=gpu Type=turing  File=/dev/nvidia3

    NodeName=gpu-g3-1 Name=gpu Type=turing  File=/dev/nvidia0
    NodeName=gpu-g3-1 Name=gpu Type=turing  File=/dev/nvidia1
    NodeName=gpu-g3-1 Name=gpu Type=turing  File=/dev/nvidia2
    NodeName=gpu-g3-1 Name=gpu Type=turing  File=/dev/nvidia3

    NodeName=gpu-g1-1 Name=gpu Type=pascal  File=/dev/nvidia0
    NodeName=gpu-g1-1 Name=gpu Type=pascal  File=/dev/nvidia1

    NodeName=gpu-g1-2 Name=gpu Type=pascal  File=/dev/nvidia0
    NodeName=gpu-g1-2 Name=gpu Type=pascal  File=/dev/nvidia1

    #Name=mps Count=200  File=/dev/nvidia0
    #Name=mps Count=200  File=/dev/nvidia1
    #Name=mps Count=100  File=/dev/nvidia2
    ##Name=mps Count=100  File=/dev/nvidia3
    ```

    So the combinations for the gpus ind the bash script are like this:
    * #SBATCH --gres=gpu:pascal:1 for one GPU on nodes `gpu-g1-1` or `gpu-g1-2`
    * #SBATCH --gres=gpu:turing:1 for one GPU on node `gpu-g2-1` or `gpu-g3-2`
    * #SBATCH --gres=gpu:ampere:1 for one GPU on node `gpu-g4-1`
