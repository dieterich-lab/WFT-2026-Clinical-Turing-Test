# Preparations for JupyterLab usage

Our JupyterLab is accessible via `https://jupyter.dieterichlab.org/`. It will use your home directory as the root directory. In order to do so it, you have to visit your home directory *once* on our cluster. Be aware that you have to enable the WireGuard VPN Tunnel with the IP adress that you received from H. Wilhelmi to connect from outside the clinic network.  You can access your home directory on our cluster `cluster.dieterichlab.org` via `ssh`:

```bash
ssh <username>@cluster.dieterichlab.org
```

If you want to access files from the jupyter lab that are not located in your home directory (ressource that we will provide to you), you are always free to create symbolic links:

```bash
ln -s <some folder somewhere else> .
```

It will be convenient (but not necessary) to create a virtual Python environment to where you install all needed modules for the project. To create a virtual Python environment you can either use the Python standard library [venv](https://docs.python.org/3/library/venv.html) or the scientific Python distribution [anaconda](https://www.anaconda.com/products/distribution) (which has to be [installed](https://docs.anaconda.com/anaconda/install/linux/) in your home directory):

```bash
mkdir "<venv-directory>"
python3 -m venv "<venv-directory>/<venv-name>"
```

or

```bash
conda create --name "<env-name>"
```

Then activate your environment:

    ```bash
    source "<venv-directory>/<venv-name>/bin/ativate"
    ```

    or

    ```bash
    conda activate <env-name>
    ```

To deactivate your environment run:

    ```bash
    deactivate
    ```

    or

    ```bash
    conda deactivate
    ```

Please also upgrade your the python package manager `pip` in your environment.

    ```bash
    pip install --upgrade pip
    ```

To make jupyter recognize the virtual environment kernel, you have to install the IPython kernel and add your environment to jupyter. Do this by executing:

    ```bash
    python3 -m pip install --user ipykernel
    python3 -m ipykernel install --user --name="<venv-name>"
    ```

Now, you can choose your environment (where you will install all your packages, like PyTorch, transformers, datasets and so on) in the jupyter Lab:

![jupyter_lab_with_kernels](../assets/images/2022-03-29-09-31-18.png)

If modules are not found in jupyter despite that you seemingly activated the correct kernel, please check if your kernel appears in the list of jupyter's registered kernel:

 ```bash
 jupyter kernelspec list
 ```

If the kernel is there with a different name or just as a last resort, you can remove the kernel:

 ```bash
 jupyter kernelspec uninstall "<your-environment-name>"
 ```

 and then re-register it:

 ```bash
 python3 -m ipykernel install --user --name="<venv-name>"
 ```
