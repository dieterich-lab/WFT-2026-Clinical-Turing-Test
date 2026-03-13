---
id: fnoh2zl6ug7608buepwz16u
title: Ollam
desc: ''
updated: 1746603713262
created: 1746603663217
---

# Using the ollama to serve models API-based on our cluster

[Ollama reference](https://ollama.com/):

> Ollama is an open-source project that serves as a powerful and user-friendly platform for running LLMs on your local machine

We installed Ollama as a module on our cluster. To have access to the module, you need the following lines in your `bash.rc`:

```bash
source /etc/profile.d/modules.sh  # specific for vscode users, check if you need that
source /biosw/__modules__/modules.rc # loads the module library                                                                                                                                                                                                                                          
module load ollama # loads the ollma binaries
```

To use an LLM via Ollama you have to

1) start the ollama server
2) let a model run

## 1) Start the Ollama server

To start the ollama server, you need an interactive session on a GPU node that has enough VRAM to fit your model. E.g., for an 8B model (like llama3.1:8B) one A100 card is sufficient, e.g.:

```bash
srun --gres=gpu:ampere:1 -c 2 -p gpu --mem=50G --nodelist=gpu-g4-1 --pty bash -i
```

For a 70B model (llama3.3:70B) you need 4 A100s:

```bash
srun --gres=gpu:ampere:4 -c 2 -p gpu --mem=250G --nodelist=gpu-g4-1 --pty bash -i
```

Then ou have to start the server in the shell of the interactive session:

```bash
OLLAMA_KEEP_ALIVE=240h OLLAMA_CONTEXT_LENGTH=128000 OLLAMA_HOST=10.250.135.153:11434 ollama serve
```

The preceding environment variables are for:

* OLLAMA_KEEP_ALIVE=240h: to let the model be loaded for a long time (240h = 10 days...)
* OLLAMA_CONTEXT_LENGTH=128000: to set the possible context size to the max of the concurrent models (llama, deepseek, gemma,... all have a possible context siz of 128k token, but *it must be set*, otherwise it will only consume 4096 tokens)
* OLLAMA_HOST=10.250.135.153:11434: this is the ip adress (`10.250.135.153`) of the GPU node and specifies the port (`11434`) at the same time. When you want to reach the API from another node (e.g. a python programm) then you have to specify this adress.

To get the ip adress of a node, just log in and run `ip a`, e.g.:

```bash
ssh gpu-g4-1
ip a
```

output:

``` bash
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute 
       valid_lft forever preferred_lft forever
2: enp193s0f0np0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:62:0b:b5:f8:fa brd ff:ff:ff:ff:ff:ff
    inet 10.250.135.153/24 brd 10.250.135.255 scope global enp193s0f0np0 # last line contains the IP adress
```

2) Run a model

Connect to the GPU node via ssh, e.g.:

```bash
ssh gpu-g4-1
```

There, run a model (here: llama3.1)

```bash
OLLAMA_HOST=10.250.135.153:11434 ollama run llama3.1 # you only need to specify the IP adress
```

To get a complete overview over the Ollama model zoo, visit: <https://ollama.com/library>
