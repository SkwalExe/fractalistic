<p align="center">
  <img src="assets/logo.png">
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
  <img src="assets/banner.png">
</p>

# How to install 📥

Clone the repo

```bash
git clone https://github.com/SkwalExe/fractalistic
cd fractalistic
```

Install the dependencies

```bash
pip install -r requirements.txt
```

Run the program

```bash
python3 fractalistic/main.py
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
- [ ] Create a PyPI package
- [ ] Color smoothing
- [ ] Key to increase/decrease max iterations
- [ ] Key to increase/decrease zoom speed
- [ ] Key to increase/decrease move speed
- [x] Show how long it took to render the last frame
- [ ] Key to show current position, zoom, interations, etc
- [x] Prevent event queue from overflowing and freezing the program
- [ ] Key to clear log messages
- [ ] Use center as screen pos instead of top left corner
- [ ] Show zoom level in the title bar
- [ ] Allow use of builtin floats instead of gmpy2 for faster rendering 
- [ ] Press H for help
- [ ] Splash screen
- [x] Custom julia set c value (z² - c)

Command line options :
- [ ] Load fractal, position, and zoom from a file
- [ ] Custom zoom speed
- [ ] Custom move speed

# Development 

Please, open an issue if you have any suggestion or if you found a bug. I will try to fix it as soon as possible. If you want to contribute, open an empty pull request and explain what you want to do, wait for me to approve it and then you can start working on it.

# Screenshots

![Screenshot 1](assets/screenshot1.png)

![Screenshot 3](assets/screenshot3.png)

![Screenshot 2](assets/screenshot2.png)

![Screenshot 4](assets/screenshot4.png)

![Screenshot 5](assets/screenshot5.png)