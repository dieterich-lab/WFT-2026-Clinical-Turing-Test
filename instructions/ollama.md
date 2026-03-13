# Using the ollama singularity image on our cluster

We downloaded the ollama docker container and converted it into a singularity image.

It is located under `/biosw/ollama/ollama.sif`. 

All our GPUs are ollama-ready, as we installed all the necessary nvidia packages. There will only be problems when multiple people start the ollama server on the port, where ollama serves, so we have to find out to how to give ollama a different port than the standard one (`11434`). Generally, this is the guide to make ollama run on a single GPU:

For this to work, you will need to open at least two shells, so you need to work with an IDE like VSCode or use screen/tmux.

* Login to our cluster
* Add the singularity to your `PATH` environment variable (for example, by adding it to the `~/.bashrc` file, so it gets loaded whenever you log in to our cluster): `PATH=.local/bin:/opt/singularity/bin:$PATH`. Here, `.local/bin:$PATH` was the existing `$PATH` entry and we added `:/opt/singularity/bin` in between.
* Reload your bash.rc via `source ~/.bashrc`.
* In the first shell, start an interactive session with a GPU on a designated node. Here we will use `gpu-g4-1` on the `ampere` configuration and the `gpu` partition to have enough runtime for longer projects (but you can decide for other gpu nodes following our [cluster instructions](cluster.md)): 
  * `srun --gres=gpu:ampere:1 -c 2 -p gpu --mem=50G --nodelist=gpu-g4-1 --pty bash -i`

* Now start the container that runs the ollama server by: 
  * `singularity run --nv /biosw/ollama/ollama.sif`

  This will expose ollama to the standard port `127.0.0.1:11434`. If this port is used and you want to change it, you can pass this as an environment variable to singularity:

  * `singularity run --nv --env "OLLAMA_HOST=127.0.0.1:11435" /biosw/ollama/ollama.sif`

* In another shell login to this very node (here by `ssh gpu-g4-1`). 
* There, you can then access the server by (as an example, this is dependent on what you're doing): `singularity exec /biosw/ollama/ollama.sif ollama run llama2`
