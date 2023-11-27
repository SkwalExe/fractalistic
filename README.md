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
- 📜 Save and load state
- 📊 Show average divergence
- 📌 Click to show coordinates and divergence
- 🏃 Multithreaded rendering

# Roadmap

Possible features to add later:
- [ ] Splash screen
- [ ] app.log_error(), etc utility functions
- [ ] New mandelbrot variants

Commands:
- [ ] Command to show current pos, zoom, etc

# How to migrate your state files to >= 2.0.0

First open your toml state file in a text editor. 
You can open the screen position in the app by using the `pos` command, and copy/pasting the real and imaginary values.
Then, select the correct fractal, color palette, precision and max_iter values in the app, 
and use the `save_state` command to save your updated state file.

# Development 

Please, open an issue if you have any suggestion or if you found a bug. I will try to fix it as soon as possible. If you want to contribute, open an empty pull request and explain what you want to do, wait for me to approve it and then you can start working on it.

### Development environment

**For this project, I recomment using vscode with Flake8 (linting/type-checking).**

You will need to fork this repo and clone it locally. 

```bash
# Replace SkwalExe with your github username
git clone https://github.com/SkwalExe/fractalistic
cd fractalistic
```

Then, install the project and the dependencies locally 

```bash
pip install .
```

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

You will be able to see the app logs, and print to the textual console with the `textual.log` function.

### Creating a pull request

- First, create a new branch with a name that describes your feature/fix.

```bash
git checkout -b my-new-feature
```

**You can now start working on your feature/fix.**

- Before commiting, you should run the linter and type-checker to make sure your code is clean.

```bash
# 'pip install flake8' if you don't have it
flake8 fractalistic
```

**If you get any error, you should fix it before commiting.**

- Now, commit your changes and push them to your fork.

```bash
git add .
git commit -m "My new feature"
git push origin my-new-feature
```

- Finally, open a pull request on github from your fork's page. I should receive a notification and I will review your changes.

# Screenshots

![Screenshot 0](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot0.png)

![Screenshot 1](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot1.png)

![Screenshot 3](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot3.png)

![Screenshot 2](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot2.png)

![Screenshot 4](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot4.png)

![Screenshot 5](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot5.png)

![Screenshot 6](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot6.png)

![Screenshot 7](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot7.png)

![Screenshot 8](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot8.png)

![Screenshot 9](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot9.png)

![Screenshot 10](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot10.png)

![Screenshot 11](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot11.png)

![Screenshot 12](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot12.png)

![Screenshot 13](https://raw.githubusercontent.com/SkwalExe/fractalistic/main/assets/screenshot13.png)