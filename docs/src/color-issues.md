# Color Issues ❗ {#color-issues}

**In good conditions, the app should use 24-bit colors which looks like this:**

![Normal colors](./assets/normal-colors.png)

However, it is possible that when you open the app, the colors are not displaying correctly. In this case, it can look something like this if only 4-bits ANSI colors are used:

![Color issue 1](./assets/color-issue1.png)

It can also look like this if only 8-bits ANSI colors are used :

![Color issue 2](./assets/color-issue2.png)


If the colors are not displaying correctly, ensure that your terminal supports 24-bit colors (truecolor). You can verify this by copying and pasting the following command into your terminal:


```bash
curl -sLo- https://raw.githubusercontent.com/SkwalExe/fractalistic/main/test-truecolor.sh | bash
```

> Please note that running `curl ... | bash` commands can be dangerous and is generally considered a bad practice unless you are certain that the script originates from a trustworthy source.

You should see smooth output similar to the screenshot below. If not, consider updating your terminal or switching to a more modern terminal that supports 24-bit colors.

![Preview](./assets/truecolor.png)

If your terminal supports 24-bit colors but the colors are still not displaying correctly, you might need to set the following environment variable when running the app:

```bash
COLORTERM=truecolor fractalistic
```

Additionally, consider adding this to your `~/.bashrc` or `~/.zshrc` to make the change permanent:

```bash
export COLORTERM=truecolor
```

