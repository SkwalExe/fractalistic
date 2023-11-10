<p align="center">
  <img src="https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/logo.png">
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/SkwalExe/fractalistic?style=for-the-badge">
  <img src="https://img.shields.io/github/stars/SkwalExe/fractalistic?style=for-the-badge">
  <img src="https://img.shields.io/github/issues/SkwalExe/fractalistic?color=blueviolet&style=for-the-badge">
  <img src="https://img.shields.io/github/forks/SkwalExe/fractalistic?color=teal&style=for-the-badge">
  <img src="https://img.shields.io/github/issues-pr/SkwalExe/fractalistic?color=tomato&style=for-the-badge">

</p>

<p align="center">💠 Terminal based fractal explorer, including Mandelbrot, Burning Ship, and Julia. 💠</p>

# Fractalistic

<p align="center">
  <img src="https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/banner.png">
</p>

# How to install 📥

You can install fractalistic easily with pip:
```bash
python3 -m pip install fractalistic
```

If you want to install the application securely, in an isolated environment, you can use [pipx](https://pypa.github.io/pipx/):
```bash
pipx install fractalistic
```


Now start the program with:
```bash
fractalistic
```


# Features 🌟

**Available fractals**:
- Mandelbrot set
- Burning Ship set
- Every Julia sets

---

- 🖥️ Terminal based
- ✨ Next-gen Terminal UI with texutal
- 🔍 Zoom in/out
- 🚶 Move around
- ⚙️ Change max iterations
- 🎨 Change color palette
- 🔢 Custom decimal precision
- 📸 High definition screenshots


# Roadmap

Possible features to add later:
- [ ] Click pos command, set position to next click position
- [ ] Show zoom level in the title bar
- [ ] Allow use of builtin floats instead of gmpy2 for faster rendering 
- [ ] Splash screen
- [ ] Custom mandelbrot/burning ship starting value or exponent
- [ ] app.log_error(), etc utility functions

Commands:
- [ ] Command to show current pos, zoom, etc
- [ ] Command to set decimal precision
- [ ] Command to save position to file
- [ ] Command to load position from a file

Command line options :
- [ ] Load fractal, position, and zoom from a file

# Development 

Please, open an issue if you have any suggestion or if you found a bug. I will try to fix it as soon as possible. If you want to contribute, open an empty pull request and explain what you want to do, wait for me to approve it and then you can start working on it.

### Running the app in textual dev mode

- First, open a textual console in a terminal with this command.

```
textual console
```

You will need to have `textual-dev` installed. You can install it with pip.

```
pip install textual-dev
```

- You can now open a new terminal, and start `fractalistic` in textual dev mode with :

```bash
# You must already be cd-ed into the repo directory
TEXTUAL=devtools,debug python3 -m fractalistic
```

# Screenshots

![Screenshot 1](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot1.png)

![Screenshot 3](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot3.png)

![Screenshot 2](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot2.png)

![Screenshot 4](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot4.png)

![Screenshot 5](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot5.png)