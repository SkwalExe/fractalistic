![Project's logo](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/logo.png)

<p align="center">💠 The Terminal-Based Fractal Explorer 💠</p>

## How to install 📥 {#installation}

You can install fractalistic easily with pip:


```bash
pip install fractalistic
```

If you want to install the application and its dependencies in an isolated environment, you can use [pipx](https://pypa.github.io/pipx/):

```bash
pipx install fractalistic
```

## Starting the app

::: info Caution
If the command is not found after installation, you may need to add  `~/.local/bin` to your path. You can do this by adding `export PATH=$PATH:~/.local/bin` to your `.bashrc` or `.zshrc` file. You will also need to **open a new shell session**.

```bash
# For bash
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc && bash
# For zsh
echo 'export PATH=$PATH:~/.local/bin' >> ~/.zshrc && zsh
```
:::

Now you can start the application with this command:

```bash
fractalistic
```

![Preview](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/banner.png)

## Troubleshooting install errors 

To perform high precision arithmetics, Fractalistic use GMPY2. This dependency can sometimes prevent the installation to succeed because of missing system libraries.
The [GMPY2 documentation](https://gmpy2.readthedocs.io/en/latest/install.html) provides a solution to this problem on debian systems.

> If pre-compiled binary wheels aren’t available for your platform, the pip will fallback to installation from sources. In this case you will need to have required libraries (GMP, MPFR and MPC) already installed on your system, along with the include files for those libraries. On Debian you can install them systed-wide with:
> 
> ```bash
> sudo apt install libgmp-dev libmpfr-dev libmpc-dev
> ```

For windows, I can suggest [this StackOverflow post](https://stackoverflow.com/questions/59471761/python-3-7-unable-to-install-gmpy2-in-a-venv-in-windows-10). 
I do not use Windows so I cannot check if this solution works, but you should give it a try.
